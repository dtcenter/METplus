
import xarray as xr
import datetime as dt
import sys

# Check and get input arguments
if len(sys.argv) != 6:
    print("ERROR: Must supply input file, init time, lead time, variable, and level to script")
    sys.exit(1)

input_file = sys.argv[1]
init_time_in = sys.argv[2]
lead_time_in = sys.argv[3]
var = sys.argv[4]
varlevel = sys.argv[5]

# Read the zarr file
ds = xr.open_zarr(input_file)

# Get/Calculate init, valid, and lead time
init_time = dt.datetime.strptime(init_time_in,'%Y%m%d_%H%M%S')
lead_time = dt.timedelta(hours=float(lead_time_in))
valid_time_dt = init_time + lead_time

# Select the time and variable from the data
try:
    ds_time = ds.sel(time=init_time)
    ds_time_lt = ds_time.sel(lead_time=lead_time)
    met_data_var = ds_time_lt[var]
except:
    print('Error: Init Time '+init_time_in+', lead time '+lead_time_in+', or variable '+var+' not present in zarr file.')
    print('Please select a variable or time that is in the file.')
    sys.exit('Exiting')

# Get level if needed
if varlevel[0] == 'P':
    levnum = varlevel[1:]
    # Check to make sure level is a dimension in our variable array
    if 'level' in met_data_var.dims:
        level_in_array = (met_data_var.level == float(levnum)).any().item()
        if level_in_array:
            met_data_var_lvl = met_data_var.sel(level=levnum)
        else:
            print('Error: Level '+str(levnum)+' not found in array')
            sys.exit('Exiting')
else:
    met_data_var_lvl = met_data_var

# Set up MET data
latsize = int(met_data_var.sizes['latitude'])
lonsize = int(met_data_var.sizes['longitude'])
met_data = met_data_var_lvl.values
met_data = met_data[::-1]

# Get up some units and variable names
if var == 'T2M' or var == 'TMP':
    varunits = 'K'
    var_lonname = 'Temperature'
elif var == 'REFC':
    varunits = 'dBZ'
    var_lonname = 'Reflectivity'
elif var == 'HGT':
    varunits = 'gpm'
    var_lonname = 'Height'
elif var == 'UGRD' or var == 'VGRD':
    varunits = 'm/s'
    var_lonname = var[0]+' Wind'
elif var == 'SPFH':
    varunits = 'kg/kg'
    var_lonname = 'Specific Humidity'
elif var == 'VVEL':
    varunits = 'Pa/s'
    var_lonname = 'Vertical Velocity'

# Set up MET attributes
attrs = {
   'valid': valid_time_dt.strftime('%Y%m%d_%H%M%S'),
   'init':  init_time_in,
   'lead':  lead_time_in+'0000',
   'accum': '00',

   'name':      var,
   'long_name': var_lonname,
   'level':     varlevel,
   'units':     varunits,

   'grid': {
       'type': 'Lambert Conformal',
       'hemisphere': 'N',
       'name': var,
       'nx':lonsize,
       'ny':latsize,
       'lat_pin': 38.5,
       'lon_pin': 262.5,
       'x_pin': float(lonsize)/2.0,
       'y_pin': float(latsize)/2.0,
       'lon_orient': 262.5,
       'd_km': 6.0,
       'r_km': 6371.229,
       'scale_lat_1': 38.5,
       'scale_lat_2': 38.5
    }
}

print(attrs)
