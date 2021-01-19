import sys
import re
import numpy as np
import datetime as dt
from netCDF4 import Dataset, chartostring

#grab input from user
#should be (1)input file using full path (2) group name for the variable and (3) variable name
input_file, group_name, var_name = sys.argv[1].split(':')
try:
    #set pointers to file and group name in file
    f = Dataset(input_file, 'r')
    g = f.groups[group_name]
    #grab time from file name and hold
    v_time_ind = input_file.split("_").index("HOURLY")+1
    v_time = input_file.split("_")[v_time_ind]

    #grab data from file
    lat = np.float64(f.variables['latitude'][:])
    lon = np.float64(f.variables['longitude'][:])
    #the data is defined by (lon, lat), so it needs to be transposed
    #in addition to being filled by fill value if data is missing
    var_invert = np.float64(g.variables[var_name][:,::-1])
    var_invert[var_invert < -800] = -9999
    met_data = var_invert.T.copy()
except NameError:
    print("Can't find input file")
    sys.exit(1)

##########

#create a metadata dictionary

attrs = {

        'valid': str(v_time.split('T')[0])+'_'+str(v_time.split('T')[1])+'00',
        'init': str(v_time.split('T')[0])+'_'+str(v_time.split('T')[1])+'00',
        'name': group_name+'_'+var_name,
        'long_name': 'UNKNOWN',
        'lead': '00',
        'accum': '00',
        'level': 'UNKNOWN',
        'units': 'UNKNOWN',

        'grid': {
            'name': 'Global 1 degree',
            'type': 'LatLon',
            'lat_ll': -89.5,
            'lon_ll': -179.5,
            'delta_lat': 1.0,
            'delta_lon': 1.0,

            'Nlon': f.dimensions['longitude'].size,
            'Nlat': f.dimensions['latitude'].size,
            }
        }

#print some output to show script ran successfully
print("Input file: " + repr(input_file))
print("Group name: " + repr(group_name))
print("Variable name: " + repr(var_name))
print("Attributes:\t" + repr(attrs))
f.close()
