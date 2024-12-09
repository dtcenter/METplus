import sys
import os
from netCDF4 import Dataset
import numpy as np
from datetime import datetime,timedelta

msg_type = ['ADPSFC']
var_name = ['low_cloud_area_fraction']
level = [-9999]
qc_string = ['NA']

if len(sys.argv) < 2:
  print(f"ERROR: {__file__} - Must provide at least 1 input file argument")
  sys.exit(1)

input_file = os.path.expandvars(sys.argv[1])

if not os.path.exists(input_file):
  print(f'ERROR: Input file does not exist: {input_file}')
  sys.exit(1)

nc = Dataset(input_file, 'r')

# Load variables (no qc vars present in file)
latitude = nc.variables['latitude'][:] # 5021
longitude = nc.variables['longitude'][:] # 5021
altitude = nc.variables['altitude'][:] # 5021
station_ids = nc.variables['station_id'][:] # stn:5021

parent_index = nc.variables['parent_index'][:] # recNum:130427
time_observation = nc.variables['time_observation'][:] # recNum:130427
low_cloud_area_fraction = nc.variables['low_cloud_area_fraction'][:] # recNum:130427
low_cloud_base_altitude = nc.variables['low_cloud_base_altitude'][:] # recNum:130427

stn_id = np.empty(len(parent_index),dtype="U10")
lat = np.zeros(len(parent_index))
lon = np.zeros(len(parent_index))
elev = np.zeros(len(parent_index))
for i in range(len(parent_index)):
  stn_id[i] = station_ids[parent_index[i]].tobytes().decode('utf-8').strip() # numpy.str
  lat[i] = latitude[parent_index[i]] # numpy.float64
  lon[i] = longitude[parent_index[i]] # numpy.float64
  elev[i] = altitude[parent_index[i]] # numpy.float64

epoch = datetime(1970, 1, 1)
formatted_times = [(epoch + timedelta(seconds=int(time))).strftime('%Y%m%d_%H%M%S') for time in time_observation]

msg_type = msg_type*len(parent_index) # str
msg_type = [np.str_(item) for item in msg_type]
vld_time = formatted_times # str 
var_name = var_name*len(parent_index) # str 
level = level*len(parent_index) # int
height = low_cloud_base_altitude # numpy.float32
qc_string = qc_string*len(parent_index) # str
obs_value = low_cloud_area_fraction # numpy.float32

print(type(msg_type))
print(type(msg_type[0]))
print(type(stn_id[0]))
obs_val = obs_value.filled(-9999)
hgt = height.filled(-9999)

point_data = []
point_data = [ msg_type, stn_id, vld_time, lat, lon, elev, var_name, level, hgt, qc_string, obs_val]

# 11-column observations for input
# string: message_type = ADPSFC
# string: station_id = station id
# string: vld_time = obs time (YYYYMMDD_HHMMSS)
# num:    lat = latitude
# num:    lon = longitude
# num:    elevation = stn altitude
# string: var_name = e.g. 'low_cloud_area_fraction'
# num:    level = e.g. cloud_base_height (Pa)
# num:    height = e.g. cloud_base_height (m)
# string: qc_string = qc flag
# num:    observation_value = obs value
