from netCDF4 import Dataset
import numpy as np
import datetime as dt
import os
import sys
from time import gmtime, strftime

# Return valid time
def get_valid_time(input_file, mission_name):
    f = Dataset(input_file, 'r')
    mid = f.variables['mission_ID'][:].tolist().index(mission_name)
    valid_time = calculate_valid_time(f, mid)
    valid_time_mid = valid_time.strftime("%Y%m%d%H%M") 
    return valid_time_mid

def calculate_valid_time(f, mid):
  merge_year_np  = np.array(f.variables['merge_year'][mid])
  merge_month_np = np.array(f.variables['merge_month'][mid])
  merge_day_np   = np.array(f.variables['merge_day'][mid])
  merge_hour_np  = np.array(f.variables['merge_hour'][mid])
  merge_min_np   = np.array(f.variables['merge_min'][mid])
  valid_time     = dt.datetime(merge_year_np,merge_month_np,merge_day_np,merge_hour_np,merge_min_np,0)
  return valid_time

def read_inputs():
    # Read the input file as the first argument
    input_file   = os.path.expandvars(sys.argv[1])
    var_name     = sys.argv[2]
    mission_name = sys.argv[3]
    level_km     = float(sys.argv[4])
    return input_file, var_name, mission_name, level_km

def main(input_file, var_name, mission_name, level_km):
  ###########################################

  ##
  ##  input file specified on the command line
  ##  load the data into the numpy array
  ##


    try:
      # Print some output to verify that this script ran
      print("Input File:      " + repr(input_file))
      print("Variable Name:   " + repr(var_name))

      # Read input file
      f = Dataset(input_file, 'r')

      # Find the requested mission name 
      mid = f.variables['mission_ID'][:].tolist().index(mission_name)

      # Find the requested level value 
      lid = f.variables['level'][:].tolist().index(level_km)

      # Read the requested variable
      data = np.float64(f.variables[var_name][mid,:,:,lid])

      # Expect that dimensions are ordered (lat, lon)
      # If (lon, lat), transpose the data
      if(f.variables[var_name].dimensions[0] == 'lon'):
         data = data.transpose()

      print("Mission (index): " + repr(mission_name) + " (" + repr(mid) + ")")
      print("Level (index):   " + repr(level_km) + " (" + repr(lid) + ")")
      print("Data Range:      " + repr(np.nanmin(data)) + " to " + repr(np.nanmax(data)))

      # Reset any negative values to missing data (-9999 in MET)
      data[np.isnan(data)] = -9999

      # Flip data along the equator
      data = data[::-1]

      # Store a deep copy of the data for MET
      met_data = data.reshape(200,200).copy()

      print("Data Shape:      " + repr(met_data.shape))
      print("Data Type:       " + repr(met_data.dtype))

    except NameError:
      print("Trouble reading input file: " . input_file)


    ###############################################################################

    # Determine LatLon grid information

    # Read in coordinate data
    merged_lon  = np.array(f.variables['merged_longitudes'][mid,0,:])
    merged_lat  = np.array(f.variables['merged_latitudes'][mid,:,0])

    # Time data:
    valid_time = calculate_valid_time(f, mid)
    init_time = valid_time

    ###########################################

    ##
    ##  create the metadata dictionary
    ##

    ###########################################
    attrs = {
      'valid': valid_time.strftime("%Y%m%d_%H%M%S"),
      'init' : valid_time.strftime("%Y%m%d_%H%M%S"),
      'lead':  '00',
      'accum': '06',
      'mission_id': mission_name,

      'name':      var_name,
      'long_name': var_name,
      'level':     str(level_km) + "km",
      'units':     str(getattr(f.variables[var_name], "units")),

      'grid': {
          'name':       var_name,
          'type' :      'LatLon',
          'lat_ll' :    float(min(merged_lat)),
          'lon_ll' :    float(min(merged_lon)),
          'delta_lat' : float(merged_lat[1]-merged_lat[0]),
          'delta_lon' : float(merged_lon[1]-merged_lon[0]),
          'Nlat' :      len(merged_lat),
          'Nlon' :      len(merged_lon),
      }
    }

    print("Attributes:      " + repr(attrs))
    return met_data, attrs

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Must specify exactly one input file, variable name, mission ID (YYMMDDID), level (in km)")
        sys.exit(1)

    input_file, var_name, mission_name, level_km = read_inputs()

    met_data, attrs = main(input_file, var_name, mission_name, level_km)
