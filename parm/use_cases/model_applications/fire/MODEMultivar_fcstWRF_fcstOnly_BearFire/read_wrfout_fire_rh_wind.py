import sys
import os
from glob import glob
from datetime import datetime
from metpy.calc import relative_humidity_from_specific_humidity,wind_speed
from metpy.units import units
import xarray as xr

# Some variables controling how the date is pulled from the file
FILE_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
MET_DATE_FORMAT ='%Y%m%d_%H%M%S'
VALID_FORMAT = '%Y%m%d_%H%M%S'
EARTH_RADIUS = 6371.229

# Check to make sure the correct number of inputs is supplied
if len(sys.argv) != 3:
    print("ERROR: Must supply input file and variable name")
    sys.exit(1)

# read input directory
input_file = sys.argv[1]
var_name = sys.argv[2]

# find input file
found_files =  glob(input_file)
if not found_files:
    print(f"ERROR: Could not find the file {input_file}")
    sys.exit(1)

input_path = found_files[0]

# Open File and read date
ds = xr.open_dataset(input_path, decode_times=False)
valid_dt = datetime.strptime(ds['Times'][0].values.tobytes().decode(),
                            FILE_DATE_FORMAT)
init_dt = datetime.strptime(ds.attrs['SIMULATION_START_DATE'], FILE_DATE_FORMAT)
#init_dt = datetime.strptime(ds.attrs['START_DATE'], FILE_DATE_FORMAT)
lead_td = valid_dt - init_dt
lead_hours = lead_td.days * 24 + (lead_td.seconds//3600)
lead_hms = (f"{str(lead_hours).zfill(2)}"
            f"{str((lead_td.seconds//60)%60).zfill(2)}00")

# Get Grid sizes
nx = ds.sizes['west_east']
ny = ds.sizes['south_north']
d_km = ds.attrs['DX'] * ds.sizes['west_east'] / nx / 1000

# Get lower left latitude and longitude points
lat_ll = float(ds['XLAT'][0][0][0])
lon_ll = float(ds['XLONG'][0][0][0])


# Read in variable of interest
if var_name == 'RH':
    # Read in specific humidity, pressure, and temperature
    q2 = ds['Q2'][0]
    q2_units = q2.attrs['units']
    pres = ds['PSFC'][0]
    pres_units = pres.attrs['units']
    temp = ds['T2'][0]
    temp_units  = temp.attrs['units']

    # Compute RH
    rh_data = relative_humidity_from_specific_humidity(pres*units(pres_units),temp*units(temp_units),q2*units(q2_units))*100.

    # Setup variables for MET output
    met_data = rh_data.to_numpy()
    met_data = met_data[::-1]
    LONG_NAME = 'Relative Humidity'
    var_level = 'Z2'
    var_units = '%'

elif var_name == 'WIND':
    # Read in the U and V components
    uwind = ds['U10'][0]
    uwind_units = uwind.attrs['units']
    vwind = ds['V10'][0]
    vwind_units = vwind.attrs['units']

    # Compute Wind Speed
    windspeed = wind_speed(uwind * units(uwind_units), vwind * units(vwind_units))

    # Setup variables for MET output
    met_data = windspeed.to_numpy()
    met_data = met_data[::-1]
    LONG_NAME = 'Wind Speed'
    var_level = 'Z2'
    var_units = str(windspeed.metpy.units)

else:
    print("ERROR: Input Variable name must either be set to RH or WIND")
    sys.exit(1)
 

# Set up output for MET
attrs = {
  'valid': valid_dt.strftime(MET_DATE_FORMAT),
   'init': init_dt.strftime(MET_DATE_FORMAT),
   'lead':  lead_hms,
   'accum': '00',

   'name':      var_name,
   'long_name': LONG_NAME,
   'level':     var_level,
   'units':     var_units,

   'grid': {
       'name': 'FireGrid',
       'type' :   ds.attrs['MAP_PROJ_CHAR'],
       'hemisphere': 'N' if float(ds.attrs['POLE_LAT']) > 0 else 'S',
       'nx': nx,
       'ny': ny,
       'lat_pin': lat_ll,
       'lon_pin': lon_ll,
       'x_pin': 0.0,
       'y_pin': 0.0,
       'lon_orient': float(ds.attrs['CEN_LON']),
       'd_km': d_km,
       'r_km': EARTH_RADIUS,
       'scale_lat_1': float(ds.attrs['TRUELAT1']),
       'scale_lat_2': float(ds.attrs['TRUELAT2']),
   }
}


print(met_data)
print(attrs)
