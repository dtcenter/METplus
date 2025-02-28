import sys
import os
from netCDF4 import Dataset
import numpy as np
from datetime import datetime,timedelta

msg_type = ['ADPSFC']
level = [-9999.]
qc_string = ['NA']

if len(sys.argv) < 2:
  print(f"ERROR: {__file__} - Must provide at least 1 input file argument")
  sys.exit(1)

input_file, var_name = sys.argv[1].split(":")

if not os.path.exists(input_file):
  print(f'ERROR: Input file does not exist: {input_file}')
  sys.exit(1)

nc = Dataset(input_file, 'r')

# Load variables (no qc vars present in file)
latitude = nc.variables['latitude'][:]
longitude = nc.variables['longitude'][:]
altitude = nc.variables['altitude'][:] # Station altitude [m]
station_ids = nc.variables['station_id'][:]

parent_index = nc.variables['parent_index'][:]
time_observation = nc.variables['time_observation'][:] # seconds since 1970-01-01 00 UTC 
low_cloud_area_fraction = nc.variables[var_name][:] # 0-1 [unitless]
low_cloud_base_altitude = nc.variables['low_cloud_base_altitude'][:] # measurement altitude [m]

nc.close()

stn_id = np.empty(len(parent_index),dtype="U10")
stn_lat = np.zeros(len(parent_index))
stn_lon = np.zeros(len(parent_index))
stn_elev = np.zeros(len(parent_index))
for i in range(len(parent_index)):
  stn_id[i] = station_ids[parent_index[i]].tobytes().decode('utf-8').strip()
  stn_lat[i] = latitude[parent_index[i]]
  stn_lon[i] = longitude[parent_index[i]]
  stn_elev[i] = altitude[parent_index[i]]

epoch = datetime(1970, 1, 1)
formatted_times = [(epoch + timedelta(seconds=int(time))).strftime('%Y%m%d_%H%M%S') for time in time_observation]
msg_type = msg_type*len(parent_index)
vld_time = formatted_times
var_name = [var_name]*len(parent_index)
level = level*len(parent_index)
height = low_cloud_base_altitude.astype(float)
qc_string = qc_string*len(parent_index)
obs_value = low_cloud_area_fraction.astype(float)*100.0

obs_val = obs_value.filled(-9999.)
height = height.filled(-9999.)

point_data = []
point_data = [[typ,sid,vid,lat,lon,elv,var,lvl,hgt,qc,obs] for typ,sid,vid,lat,lon,elv,var,lvl,hgt,qc,obs in tuple(zip(msg_type,stn_id,vld_time,stn_lat,stn_lon,stn_elev,var_name,level,height,qc_string,obs_val))]
