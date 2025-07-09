import sys
import os
from glob import glob
from datetime import datetime
from metpy.calc import relative_humidity_from_specific_humidity,wind_speed
from metpy.units import units
import xarray as xr

FILE_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
MET_DATE_FORMAT ='%Y%m%d_%H%M%S'
VALID_FORMAT = '%Y%m%d_%H%M%S'
EARTH_RADIUS = 6371.229

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

ds = xr.open_dataset(input_path, decode_times=False)

valid_dt = datetime.strptime(ds['Times'][0].values.tobytes().decode(),
                            FILE_DATE_FORMAT)
#init_dt = datetime.strptime(ds.attrs['SIMULATION_START_DATE'], FILE_DATE_FORMAT)
init_dt = datetime.strptime(ds.attrs['START_DATE'], FILE_DATE_FORMAT)
lead_td = valid_dt - init_dt
lead_hours = lead_td.days * 24 + (lead_td.seconds//3600)
lead_hms = (f"{str(lead_hours).zfill(2)}"
            f"{str((lead_td.seconds//60)%60).zfill(2)}00")

nx = ds.sizes['west_east']
ny = ds.sizes['south_north']

d_km = ds.attrs['DX'] * ds.sizes['west_east'] / nx / 1000

lat_ll = float(ds['XLAT'][0][0][0])
lon_ll = float(ds['XLONG'][0][0][0])


# Read in variable of interest
if var_name == 'RH':
    spec_hum = ds['Q2'][0]
    pres = ds['PSFC'][0]
    temp = ds['T2'][0]
    rh_data = relative_humidity_from_specific_humidity(pres*units.Pa,temp*units.kelvin,spec_hum)*100.
    met_data = rh_data.to_numpy()
    met_data = met_data[::-1]

    LONG_NAME = 'Relative Humidity'
    var_level = 'Z2'
    var_units = '%'

elif var_name == 'WIND':
    uwind = ds['U10'][0]
    vwind = ds['V10'][0]
    windspeed = wind_speed(uwind * units('m/s'), vwind * units('m/s'))
    met_data = windspeed.to_numpy()
    met_data = met_data[::-1]

    LONG_NAME = 'Wind Speed'
    var_level = 'Z2'
    var_units = 'ms-1'

else:
    print("ERROR: Input Variable name must either be set to RH or WIND")
    sys.exit(1)
 

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
