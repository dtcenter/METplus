import datetime
import multiprocessing
import sys
import xarray as xr
from gfs_025_interp_funcs import interp_column

model_file = sys.argv[1]
valid = sys.argv[2]
leadhours = sys.argv[3]

# Process time information
valid = datetime.datetime.strptime(valid,'%Y%m%d_%H%M%S')
init = valid-datetime.timedelta(hours=int(leadhours))

cbz_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'lowCloudBottom'},indexpath='')
gph_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'gh'},indexpath='')
top_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'surface','shortName':'orog'},indexpath='')

if len(cbz_var.data_vars) != 1:
    print("UNABLE TO DETERMINE CLOUD BASE HEIGHT VAR NAME IN read_interp_gfs_025.py")
    sys.exit(1)

if len(gph_var.data_vars) != 1:
    print("UNABLE TO DETERMINE GEOPOTENTIAL HEIGHT VAR NAME IN read_interp_gfs_025.py")
    sys.exit(1)

if len(top_var.data_vars) != 1:
    print("UNABLE TO DETERMINE OROGRAPHY VAR NAME IN read_interp_gfs_025.py")
    sys.exit(1)

cbz_var_name = list(cbz_var.data_vars)[0]
gph_var_name = list(gph_var.data_vars)[0]
top_var_name = list(top_var.data_vars)[0]


# The geopotential height field is in meters above mean sea level (MSL). To convert the geopotential height field 
# from meters MSL to meters AGL, we add the orography to the geopotential height field prior to interpolating so 
# that the result of the interpolation is meters AGL to match the observations.
gph_var[gph_var_name] = gph_var[gph_var_name]+top_var[top_var_name]

# Stack the cloud bottom pressure to 1D where each cell is treated like a site (site ID, sid)
cbzstack = cbz_var[cbz_var_name].stack(sid=("latitude","longitude"))

# Stack the GPH to 1D where each "column"/grid cell is like a site (site ID, sid)
gphstack = gph_var[gph_var_name].stack(sid=("latitude","longitude"))

# array to hold the results
resstack = xr.full_like(cbzstack,-9999.).rename('lcld_alt')
  
# Condition for masking
mask_cond = cbzstack<=(gphstack.isobaricInhPa.max(dim='isobaricInhPa').values * 100.0)

# Mask the data
cbzmask = cbzstack[mask_cond]
gphmask = gphstack[:,mask_cond]

# Get a pool of workers
mp = multiprocessing.Pool(multiprocessing.cpu_count()-2)

# Compute the interpolated height of the cloud base pressure at each site
cells_to_process = cbzmask.sizes['sid']
print("")
print(f'INTERPOLATING CLOUD BASE HEIGHT AT {cells_to_process} GRID CELLS')
print("")
result = mp.starmap(interp_column,([cbzmask,gphmask,sidx] for sidx in list(range(0,cells_to_process))))

# Re-populate the DataArray
resstack[mask_cond] = result

# Re-populate the results at the 2D cells they belong
met_data = resstack.unstack() 
met_data = met_data.values

attrs = {
    'valid': valid.strftime('%Y%m%d_%H%M%S'),
    'init': init.strftime('%Y%m%d_%H%M%S'),
    'lead': '%02d0000' % (int(leadhours)),
    'accum': '000000',
    'name': 'lcld_alt',
    'long_name': 'cloud_bottom_height',
    'level': "L0",
    'units': 'm',
    'grid': 'G193'
}
