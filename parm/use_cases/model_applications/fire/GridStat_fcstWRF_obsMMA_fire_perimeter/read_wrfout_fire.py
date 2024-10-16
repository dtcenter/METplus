import sys
import os
from glob import glob
from datetime import datetime

import xarray as xr
#import xwrf

VAR_NAME = 'FIRE_AREA'
LONG_NAME = 'Fire Area'
FILE_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
MET_DATE_FORMAT ='%Y%m%d_%H%M%S'
VALID_FORMAT = '%Y%m%d_%H%M%S'
WRF_FIRE_TEMPLATE = "wrfout_fire_d02_%Y-%m-%d_%H %M %S"
EARTH_RADIUS = 6371.229

if len(sys.argv) != 3:
    print("ERROR: Must supply input directory and valid time (YYYYMMDDHH) to script")
    sys.exit(1)

# read input directory
input_dir = sys.argv[1]

# parse valid time
try:
    valid_time = datetime.strptime(sys.argv[2], VALID_FORMAT)
except ValueError:
    print(f"ERROR: Invalid format for valid time: {sys.argv[2]} (Should match {VALID_FORMAT})")
    sys.exit(1)

# find input file
input_glob = os.path.join(input_dir, valid_time.strftime(WRF_FIRE_TEMPLATE))
found_files =  glob(input_glob)
if not found_files:
    print(f"ERROR: Could not find any files for {valid_time} in {input_dir}")
    sys.exit(1)

input_path = found_files[0]

#ds = xr.open_dataset(input_path, decode_times=False).xwrf.postprocess()
ds = xr.open_dataset(input_path, decode_times=False)

valid_dt = datetime.strptime(ds['Times'][0].values.tobytes().decode(),
                            FILE_DATE_FORMAT)
init_dt = datetime.strptime(ds.attrs['START_DATE'], FILE_DATE_FORMAT)
lead_td = valid_dt - init_dt
lead_hours = lead_td.days * 24 + (lead_td.seconds//3600)
lead_hms = (f"{str(lead_hours).zfill(2)}"
            f"{str((lead_td.seconds//60)%60).zfill(2)}00")

nx = ds.dims['west_east_subgrid']
ny = ds.dims['south_north_subgrid']

d_km = ds.attrs['DX'] * ds.dims['west_east'] / nx / 1000

lat_ll = float(ds['FXLAT'][0][0][0])
lon_ll = float(ds['FXLONG'][0][0][0])

met_data = ds[VAR_NAME][0]
met_data = met_data[::-1]
met_data.attrs['valid'] = valid_dt.strftime(MET_DATE_FORMAT)
met_data.attrs['init'] = init_dt.strftime(MET_DATE_FORMAT)
met_data.attrs['lead'] = lead_hms
met_data.attrs['accum'] = '000000'
met_data.attrs['name'] = VAR_NAME
met_data.attrs['long_name'] = LONG_NAME
met_data.attrs['level'] = 'Z0'
met_data.attrs['units'] = '%'
met_data.attrs['grid'] = {
    'type': ds.attrs['MAP_PROJ_CHAR'],
    'hemisphere': 'N' if float(ds.attrs['POLE_LAT']) > 0 else 'S',
    'name': VAR_NAME,
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

print(met_data)
for key,value in met_data.attrs.items():
    if key == 'grid':
        print(f"{key}:")
        for key2,value2 in value.items():
            print(f"  {key2}: {value2}")
    else:
        print(f"{key}: {value}")
