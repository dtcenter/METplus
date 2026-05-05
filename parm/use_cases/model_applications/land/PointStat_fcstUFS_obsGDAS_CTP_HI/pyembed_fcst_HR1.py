import multiprocessing
import numpy as np
import os
import sys
import xarray as xr

from metpy.units import units

print(f"\nSTARTING {__file__}\n")

# Obtain the command line arguments
derivation_type = sys.argv[1]
input_file = sys.argv[2]
tmpvarname = sys.argv[3]
prsvarname = sys.argv[4]
mask_file  = sys.argv[5]

if derivation_type == 'hi':
    if len(sys.argv) > 7:
        print("ERROR: SPFH not provided on command line.")
        sys.exit(1)

    sphvarname = sys.argv[6]
    from metcalcpy.diagnostics.land_surface import calc_humidity_index
    from metpy.calc import dewpoint_from_specific_humidity

elif derivation_type == 'ctp':
    from metcalcpy.diagnostics.land_surface import calc_ctp
else:
    print(f"ERROR: Unknown derivation type: {derivation_type}")
    sys.exit(1)


# Open the input_file as an Xarray Dataset
if os.path.splitext(input_file)[1]=='.nc':
  ds = xr.open_dataset(input_file)
  if derivation_type == 'hi':
      ds = ds[[tmpvarname,prsvarname,sphvarname,'pressfc']]
  else:
      ds = ds[[tmpvarname,prsvarname,'pressfc']]
else:
  print(f"FATAL! {__file__}.")
  print("Unable to open input file.")
  sys.exit(1)

# Determine the input dims
indims = ds.sizes
if ('grid_xt' not in ds.coords) or ('grid_yt' not in ds.coords):
  print("FATAL! unexpected dimension names in FCST file.")
  sys.exit(1)
else:
  ny = indims['grid_yt']
  nx = indims['grid_xt']

# Open the mask file
maskdata = xr.open_dataset(mask_file)

# Add the mask variable to the data
ds['maskvar'] = xr.DataArray(maskdata['RAOB_SITES'].values,dims=['grid_yt','grid_xt'],coords={'grid_yt':ds.grid_yt,'grid_xt':ds.grid_xt})

# The files that were used to develop this use case need special treatment of the pressure field.
# Find the "bk_interp" attribute
try:
  bk = ds.attrs['bk']
except KeyError:
  print("ERROR! Required attribute \"bk\" not found in:")
  print(input_file)
  print("UNABLE TO CONTINUE.")
  exit(1)

# Reverse bk, sfc pressure is -1 so make it item 0
bk = bk[::-1]

# The adjustment is at the half levels, but pressures are at the full levels.
# Average each pair of data to create n-1 number of bk values to use.
bk_interp = np.array([np.mean([bk[n],bk[n+1]]) for n in range(0,len(bk)-1)])

# Filter out values where bk=0
bk_interp = bk_interp[bk_interp>0.0]

# The model data are on terrain-following levels so it can't have a constant z-coordinate.
# Thus, we define a new z-coordinate "z0" of integers representing the levels
z0 = xr.DataArray(range(0,len(bk_interp)),dims=['z0'],coords={'z0':range(0,len(bk_interp))},attrs={'units':'levelnumber'})

# Next get the temperature. It's stored upside-down so reverse it along the vertical dimension
tmp3d = ds[tmpvarname].squeeze().reindex(pfull=ds.pfull[::-1])

# Subset the temperature and specific humidity data so it only has data where the bk_interp variable is available
tmp3d = tmp3d.isel(pfull=slice(0,len(z0)))

# Change the vertical coordinate and dimension for the temperature data to be z0
tmp3d = tmp3d.rename({'pfull':'z0'}).assign_coords({'z0':z0})
tmp3d = tmp3d*units('degK')

# do the same for specific humidity data if computing humidity index
if derivation_type == 'hi':
    sph3d = ds[sphvarname].squeeze().reindex(pfull=ds.pfull[::-1])
    sph3d = sph3d.isel(pfull=slice(0, len(z0)))

    sph3d = sph3d.rename({'pfull':'z0'}).assign_coords({'z0':z0})
    sph3d = sph3d*units('kg/kg')

# Create the 3D pressure variable
prs3d = xr.DataArray(bk_interp,dims=['z0'],coords={'z0':z0},attrs={'units':'Pa'}).broadcast_like(tmp3d)
prs3d = (prs3d*(ds['pressfc'].squeeze()))*units('Pa').to('hPa')

# Stack the data in the x-y dimension into a single dimension named "sid".
# This treats each grid cell/column like a "site"
tmpstack = tmp3d.stack(sid=("grid_yt","grid_xt"))
prsstack = prs3d.stack(sid=("grid_yt","grid_xt"))
mskstack = ds['maskvar'].stack(sid=("grid_yt","grid_xt"))

# Compute dewpoint temperature from specific humidity
if derivation_type == 'hi':
    dew3d = dewpoint_from_specific_humidity(prs3d,sph3d)
    dew3d = dew3d*units('degK')

    dewstack = dew3d.stack(sid=("grid_yt","grid_xt"))
    dew_mask = dewstack[:, mskstack > 0]
    # Create an Xarray DataArray like the stacked variables to hold the results
    resstack = xr.full_like(mskstack,-9999.).rename('humidity_index')
else:
    resstack = xr.full_like(mskstack, -9999.).rename('ctp')


# Subset the data to only the points where the mask is
prs_mask = prsstack[:,mskstack>0]
tmp_mask = tmpstack[:,mskstack>0]

# Get a pool of workers
mp = multiprocessing.Pool(int(os.environ.get('PYEMBED_MPROC_NUM_WORKERS', multiprocessing.cpu_count()-2)))

print("")
print(f"COMPUTING {derivation_type.upper() if derivation_type == 'ctp' else 'HUM'}. INDEX FOR {int(tmpstack[:,mskstack>0].sizes['sid'])} CELLS.")
print("")

if derivation_type == 'hi':
    result = mp.starmap(calc_humidity_index,([prs_mask,tmp_mask,dew_mask,sidx] for sidx in list(range(0,tmp_mask.sizes['sid']))))
else:
    result = mp.starmap(calc_ctp, ([prs_mask, tmp_mask, sidx] for sidx in list(range(0, tmp_mask.sizes['sid']))))

result = [x.m for x in result]

# Re-populate the stacked array with the values at the correct locations
resstack[mskstack>0] = result

# Unstack the data from the `sid` dimension back to just grid_xt and grid_yt (2D) and obtain the NumPy N-D array
met_data = resstack.unstack()
met_data = met_data.reindex(grid_yt=met_data.grid_yt[::-1])
met_data = met_data.values

grid_attrs = {
    'type': 'Gaussian',
    'name': 'HR1',
    'lon_zero': 0.0,
    'nx': nx,
    'ny': ny,
}

attrs = {
    'valid': '20200805_120000',
    'init': '20200803_000000',
    'lead': '600000',
    'accum': '000000',
    'name': 'testing',
    'long_name': 'long_test',
    'level': 'surface',
    'units': 'test',
    'fill_value': -9999.,
    'grid': grid_attrs,
}
