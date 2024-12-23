import multiprocessing
import numpy as np
import os
import sys
import xarray as xr
from itertools import repeat
from metcalcpy.diagnostics.land_surface import calc_ctp
from metpy.units import units

# Function for unpacking results in a single vector back to a 2D N-D array
def unpack_results(res,nx,ny):
  ret = np.empty([ny,nx])
  for r,xy in tuple(zip(res,get_iter())):
    ret[xy[0],xy[1]] = r
  return ret

# Function to return an iterator for looping over all possible i/j combinations in a 2D grid
def get_iter(nx,ny):
  return itertools.product(range(0,ny),range(0,nx))

# Functions to facilitate using starmap/multiprocessing with kwargs
# From here: https://stackoverflow.com/a/53173433
def starmap_with_kwargs(pool, fn, args_iter, kwargs_iter):
  args_for_starmap = zip(repeat(fn), args_iter, kwargs_iter)
  print("ARGS_FOR_STARMAP OK")
  return pool.starmap(apply_args_and_kwargs, args_for_starmap)

def apply_args_and_kwargs(fn, args, kwargs):
  print("APPLYING ARGS USING ARGS/KWARGS")
  return fn(*args, **kwargs)

# Obtain the command line arguments
input_file = sys.argv[1]
tmpvarname = sys.argv[2]
prsvarname = sys.argv[3]
mask_file  = sys.argv[4]

# Open the input_file as an Xarray Dataset
if os.path.splitext(input_file)[1]=='.nc':
  ds = xr.open_dataset(input_file)
  ds = ds[[tmpvarname,prsvarname,'pressfc']]
else:
  print("FATAL! pyembed_ctp_fcst_HR1.py.")
  print("Unable to open input file.")
  sys.exit(1)

# Determine the input dims
indims = ds.sizes
if not ('grid_xt' in ds.coords) or not ('grid_yt' in ds.coords):
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

# Next get the temperature data. It's stored upside-down so reverse it along the vertical dimension
tmp3d = ds[tmpvarname].squeeze().reindex(pfull=ds.pfull[::-1])

# Subset the temperature data so it only has data where the bk_interp variable is available
tmp3d = tmp3d.isel(pfull=slice(0,len(z0)))

# Change the vertical coordinate and dimension for the temperature data to be z0
tmp3d = tmp3d.rename({'pfull':'z0'}).assign_coords({'z0':z0})
tmp3d = tmp3d*units('degK')

# Create the 3D pressure variable
prs3d = xr.DataArray(bk_interp,dims=['z0'],coords={'z0':z0},attrs={'units':'Pa'}).broadcast_like(tmp3d)
prs3d = (prs3d*(ds['pressfc'].squeeze()))*units('Pa').to('hPa')

# Get a pool of workers
mp = multiprocessing.Pool(multiprocessing.cpu_count()-2)

# Stack the data in the x-y dimension into a single dimension named "sid".
# This treats each grid cell/column like a "site"
tmpstack = tmp3d.stack(sid=("grid_yt","grid_xt"))
prsstack = prs3d.stack(sid=("grid_yt","grid_xt"))
mskstack = ds['maskvar'].stack(sid=("grid_yt","grid_xt"))

# Create an Xarray DataArray like the stacked variables to hold the results
resstack = xr.full_like(mskstack,-9999.).rename('ctp')

# Subset the data to only the points where the mask is
prs_mask = prsstack[:,mskstack>0]
tmp_mask = tmpstack[:,mskstack>0]

print("COMPUTING CTP FOR %10d CELLS." % (int(tmpstack[:,mskstack>0].sizes['sid'])))
result = mp.starmap(calc_ctp,([prs_mask,tmp_mask,sidx] for sidx in list(range(0,tmp_mask.sizes['sid']))))
result = [x.m for x in result]

# Re-populate the stacked array with the values at the correct locations
resstack[mskstack>0] = result

# Unstack the data from the `sid` dimension back to just grid_xt and grid_yt (2D) and obtain the NumPy N-D array
met_data = resstack.unstack()
met_data = met_data.reindex(grid_yt=met_data.grid_yt[::-1])
met_data.to_netcdf('test.nc')
met_data = met_data.values

grid_attrs = {}
grid_attrs['type'] = 'Gaussian'
grid_attrs['name'] = 'HR1'
grid_attrs['lon_zero'] = 0.0
grid_attrs['nx'] = nx
grid_attrs['ny'] = ny

attrs = {}
attrs['valid'] = '20200805_120000'
attrs['init'] = '20200803_000000'
attrs['lead'] = '600000'
attrs['accum'] = '000000'
attrs['name'] = 'testing'
attrs['long_name'] = 'long_test'
attrs['level'] = 'surface'
attrs['units'] = 'test'
attrs['fill_value'] = -9999.
attrs['grid'] = grid_attrs
