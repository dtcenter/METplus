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

# Open the input_file as an Xarray Dataset
if os.path.splitext(input_file)[1]=='.nc':
  ds = xr.open_dataset(input_file)
else:
  print("FATAL! pyembed_ctp_fcst_HR1.py.")
  print("Unable to open input file.")
  sys.exit(1)

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
tmp3d = tmp3d.expand_dims(dim={'z0':z0}).assign_coords({'z0':z0}).isel(pfull=0).squeeze()

# Create the 3D pressure variable
prs3d = xr.DataArray(bk_interp,dims=['z0'],coords={'z0':z0},attrs={'units':'Pa'}).broadcast_like(tmp3d)
prs3d = (prs3d*(ds['pressfc'].squeeze()))*units('Pa').to('hPa')

# Get a pool of workers
mp = multiprocessing.Pool(multiprocessing.cpu_count()-2)

# Stack the data in the x-y dimension into a single dimension named "sid".
# This treats each grid cell/column like a "site"
tmpstack = tmp3d.stack(sid=("grid_yt","grid_xt"))
prsstack = prs3d.stack(sid=("grid_yt","grid_xt"))

print("COMPUTING CTP FOR %10d CELLS." % (int(tmpstack.sizes['sid'])))

# Create a list of dictionaries equal to the number of times the function will be called.
# Each dictionary entry is another keyword argument for the function.
kwargs_iter = [{'station_index':idx} for idx in list(range(0,tmpstack.sizes['sid']))]
print("KWARGS OK")

# Create a iterable for each of the positional arguments for the function to be called.
# Using "zip" creates the iterable and "repeat" will repeat the item equivalent to the length
# of the kwargs iterator, which in this case is what's varying for each function call.
args_iter = zip(repeat(prsstack),repeat(tmpstack))
print("ITER OK")

# Pass the function name, the pool of workers, and the positional and keyword arg iterators
# to the multiprocessing helper function
print("CALLING STARMAP_WITH_KWARGS")
result = starmap_with_kwargs(mp,calc_ctp,args_iter,kwargs_iter)

# A pint.Quantity is returned from the function, so get the magnitude
result = [x.m for x in result]

# Put the results back into an Xarray DataArray and assign the multi-index variable from
# stacking earlier so we can unstack the data into a 2D grid
#met_data = xr.DataArray(result,dims=['sid'],coords={'sid':tmpstack.sid},attrs={'units':'J/kg'}).unstack().to_netcdf('test.nc')
met_data = xr.DataArray(result,dims=['sid'],coords={'sid':tmpstack.sid},attrs={'units':'J/kg'}).unstack()
print(met_data)
exit()

# 
print(result)
exit()

# Compute the CTP over all grid cells
result = mp.starmap(calc_ctp,[(prsvar,stack,idx) for idx in list(range(0,stack.sizes['sid']))])
result = [x.m for x in result]
#print(result)
result2 = xr.DataArray(result,dims=['sid'],coords={'sid':stack.sid},attrs={})
#print(result2)
print(result2.unstack())
exit()

# Unpack the result at each grid cell back to the 2D grid
met_data = unpack_results(result,nx,ny)
print(met_data)

exit()

met_data = ds['soilw'].isel(depthBelowLandLayer=0).values
print(met_data)

grid_attrs = {}
grid_attrs['type'] = 'LatLon'
grid_attrs['name'] = 'HR1'
grid_attrs['lat_ll'] = -89.910324
grid_attrs['lon_ll'] = 0.0
grid_attrs['delta_lat'] = 0.117188
grid_attrs['delta_lon'] = 0.117188
grid_attrs['Nlat'] = 1536
grid_attrs['Nlon'] = 3072

attrs = {}
attrs['valid'] = '20200805_120000'
attrs['init'] = '20200803_000000'
attrs['lead'] = '600000'
attrs['accum'] = '000000'
attrs['name'] = 'testing'
attrs['long_name'] = 'long_test'
attrs['level'] = 'surface'
attrs['units'] = 'test'
attrs['grid'] = grid_attrs
#attrs['grid'] = "G040"
