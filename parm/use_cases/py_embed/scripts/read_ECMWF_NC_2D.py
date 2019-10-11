from __future__ import print_function

import sys
sys.path.insert(0, '/contrib/anaconda/anaconda2/4.4.0/lib/python2.7/site-packages')
sys.path.insert(0, '/contrib/anaconda/anaconda2/4.4.0/lib/site-python')

from netCDF4 import Dataset
import numpy as np
import datetime as dt
import os

print(sys.version)

###########################################

   ##
   ##  input file specified on the command line
   ##  load the data into the numpy array
   ##

if len(sys.argv) == 3:
  # Read the input file as the first argument
  input_file = os.path.expandvars(sys.argv[1])
  var_name   = sys.argv[2]
  try:
    # Print some output to verify that this script ran
    print("Input File: " + repr(input_file))
    print("Variable Name : " + repr(var_name))

    # Read input file
    f = Dataset(input_file, 'r')

    met_data = np.float64(f.variables[var_name][:])
    print("Data Shape: " + repr(met_data.shape))
    print("Data Type:  " + repr(met_data.dtype))
  except NameError:
    print("Trouble reading input file: " . input_file)
else:
    print("Must specify exactly one input file and the variable name.")
    sys.exit(1)

# Determine timing information
init_time_str = f.variables[var_name].getncattr('initial_time')
init_time     = dt.datetime.strptime(init_time_str, "%m/%d/%Y (%H:%M)")
fcst_unit_str = f.variables[var_name].getncattr('forecast_time_units')
fcst_time     = f.variables[var_name].getncattr('forecast_time')
# Should use fcst_unit_str instead of hard-coding 'hours'
valid_time    = init_time + dt.timedelta(hours=np.asscalar(fcst_time)) 

###########################################

   ##
   ##  create the metadata dictionary
   ##

attrs = {

   'valid': valid_time.strftime("%Y%m%d_%H%M%S"),
   'init':  valid_time.strftime("%Y%m%d_%H%M%S"),
   'lead':  '00',
   'accum': '06',

   'name':      var_name,
   'long_name': var_name,
   'level':     'Surface',
   'units':     'mm',

   'grid': {
       'name': 'ECMWF-Global',
       'type' :   'LatLon',
       'lat_ll' :    -90.0,
       'lon_ll' :      0.0,
       'delta_lat' :   1.0,
       'delta_lon' :   1.0,
       'Nlat' :      181,
       'Nlon' :      360,
   }

}

print("Attributes: " + repr(attrs))
