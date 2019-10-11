from __future__ import print_function

import os
import sys
import re
import numpy as np
import datetime as dt

###########################################

   ##
   ##  input file specified on the command line
   ##  load the data into the numpy array
   ##

if len(sys.argv) == 2:

    # Store the input file and record number
    input_file = os.path.expandvars(sys.argv[1])
    try:
        # Print some output to verify that this script ran
        print("Input File: " + repr(input_file))

        # Read input file
        data = np.float64(np.fromfile(input_file, '>f'))

        # Read and re-orient the data
        met_data = data[::-1].reshape(181, 360)[:,::-1].copy()

        print("Data Shape: " + repr(met_data.shape))
        print("Data Type:  " + repr(met_data.dtype))
        print("Data Range: " + repr(min(data)) + " to " + repr(max(data)))
    except NameError:
        print("Trouble reading input file: " + input_file)
else:
    print("Must specify exactly one input file.")
    sys.exit(1)

###########################################

   ##
   ##  create the metadata dictionary
   ##

tokens = os.path.basename(input_file).replace('-', '_').split('_');

for token in tokens:
   if(re.search("[0-9]{10,10}", token)):
       ymdh = dt.datetime.strptime(token[0:10],"%Y%m%d%H")
   elif(re.search("[0-9]{8,8}", token)):
       fhr = int(token) / 10000

init  = ymdh
valid = init + dt.timedelta(hours=fhr)
lead, rem = divmod((valid-init).total_seconds(), 3600)

attrs = {
   'valid': valid.strftime("%Y%m%d_%H%M%S"),
   'init':  init.strftime("%Y%m%d_%H%M%S"),
   'lead':  str(int(lead)),
   'accum': '00',

   'name':      tokens[0],
   'long_name': 'UNKNOWN',
   'level':     tokens[1]+'_'+tokens[2],
   'units':     'UNKNOWN',

   'grid': {
       'name': 'Global 1 Degree',
       'type' : 'LatLon',
       'lat_ll' :    -90.0,
       'lon_ll' :      0.0,
       'delta_lat' :   1.0,
       'delta_lon' :   1.0,
       'Nlat' :      181,
       'Nlon' :      360,
   }
}

print("Attributes: " + repr(attrs))
