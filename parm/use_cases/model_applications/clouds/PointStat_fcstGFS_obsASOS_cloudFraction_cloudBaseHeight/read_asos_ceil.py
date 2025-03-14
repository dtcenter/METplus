import sys
import os
from netCDF4 import Dataset
import numpy as np
from datetime import datetime,timedelta

# Set the MET 11-column "typ", "lvl", and "qc" variables
msg_type = ['ADPSFC']
level = [-9999.]
qc_string = ['NA']

# Require an input file and variable name in the format:
# path_to_file:variable_name
if len(sys.argv) < 2:
  print(f"ERROR: {__file__} - Must provide at least 1 input file argument")
  sys.exit(1)

# Separate out the input file and the variable name
input_file, var_name = sys.argv[1].split(":")

# Ensure the input file exists, and exit if it does not
if not os.path.exists(input_file):
  print(f'ERROR: Input file does not exist: {input_file}')
  sys.exit(1)

# Open the NetCDF input file
nc = Dataset(input_file, 'r')

# Load variables (no qc vars present in file)
latitude = nc.variables['latitude'][:]
longitude = nc.variables['longitude'][:]
altitude = nc.variables['altitude'][:] # Station altitude [m]
station_ids = nc.variables['station_id'][:]
parent_index = nc.variables['parent_index'][:]
time_observation = nc.variables['time_observation'][:] # seconds since 1970-01-01 00 UTC 
observation = nc.variables[var_name][:]

# Close the NetCDF input file after all data have been acquired
nc.close()

# Set up variables to hold the "sid", "lat", "lon", and "elv" variables in the MET 11-column data format
stn_id = np.empty(len(parent_index),dtype="U10")
stn_lat = np.zeros(len(parent_index))
stn_lon = np.zeros(len(parent_index))
stn_elev = np.zeros(len(parent_index))

# Fill those variables with data from the input file
for i in range(len(parent_index)):
  stn_id[i] = station_ids[parent_index[i]].tobytes().decode('utf-8').strip()
  stn_lat[i] = latitude[parent_index[i]]
  stn_lon[i] = longitude[parent_index[i]]
  stn_elev[i] = altitude[parent_index[i]]

# Fill the "vld" column with time information formatted the way MET expects
epoch = datetime(1970, 1, 1)
formatted_times = [(epoch + timedelta(seconds=int(time))).strftime('%Y%m%d_%H%M%S') for time in time_observation]
vld_time = formatted_times

# Fill the "typ" variable
msg_type = msg_type*len(parent_index)

# Fill the "var" variable
var = [var_name]*len(parent_index)

# Fill the "lvl" variable
level = level*len(parent_index)

# Set the "hgt" column in the MET 11-column data to the same as "lvl"
height = level

# Set the "qc" variable
qc_string = qc_string*len(parent_index)

# Convert the "obs" value to float, and if it is cloud fraction then
# multiply the obs variable by 100 to match the forecast
obs_value = observation.astype(float)
if 'fraction' in var_name:
  obs_value = obs_value*100.0

# Fill any missing data with the MET missing data value of -9999.
obs_val = obs_value.filled(-9999.)

# Create the point_data object MET expects
point_data = []
point_data = [[typ,sid,vid,lat,lon,elv,var,lvl,hgt,qc,obs] for typ,sid,vid,lat,lon,elv,var,lvl,hgt,qc,obs in tuple(zip(msg_type,stn_id,vld_time,stn_lat,stn_lon,stn_elev,var,level,height,qc_string,obs_val))]
