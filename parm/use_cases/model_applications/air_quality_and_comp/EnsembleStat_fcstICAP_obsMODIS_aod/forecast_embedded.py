import sys
import re
import numpy as np
import datetime as dt
from netCDF4 import Dataset, chartostring

#grab input from user
#should be (1)input file using full path (2) variable name (3) valid time for the forecast in %Y%m%d%H%M format and (4) ensemble member number, all separated by ':' characters
#program can only accept that 1 input, while still maintaining user flexability to change multiple
#variables, including valid time, ens member, etc.
input_file, var_name, val_time, ens_mem = sys.argv[1].split(':')
ens_mem = int(ens_mem)
val_time = dt.datetime.strptime(val_time,"%Y%m%d%H%M")
try:
    #set pointers to file and group name in file
    f = Dataset(input_file, 'r')
    v = f[var_name]
    #grab intialization time from file name and hold
    #also compute the lead time
    i_time_ind = input_file.split("_").index("aod.nc")-1
    i_time = input_file.split("_")[i_time_ind]
    i_time_obj = dt.datetime.strptime(i_time,"%Y%m%d%H")
    lead, rem = divmod((val_time - i_time_obj).total_seconds(), 3600) 

    print("Ensemble Member evaluation for: "+f.members.split(',')[ens_mem])

    #checks if the the valid time for the forecast from user is present in file.
    #Exits if the time is not present with a message
    if not val_time.timestamp() in f['time'][:]:
            print("valid time of "+str(val_time)+" is not present. Check file initialization time, passed valid time.")
            f.close()
            sys.exit(1)

    #grab index in the time array for the valid time provided by user (val_time)
    val_time_ind = np.where(f['time'][:] == val_time.timestamp())[0][0]
    
    #grab data from file
    lat = np.float64(f.variables['lat'][:])
    lon = np.float64(f.variables['lon'][:])
    var = np.float64(v[val_time_ind:val_time_ind+1,ens_mem:ens_mem+1,::-1,:])
    var[var < -800] = -9999
    #squeeze out all 1d arrays, add fill value
    met_data = np.squeeze(var).copy()
except NameError:
    print("Can't find input file")
    sys.exit(1)

##########
#create a metadata dictionary

attrs = {

        'valid': str(val_time.strftime("%Y%m%d"))+'_'+str(val_time.strftime("%H%M%S")),
        'init': i_time[:-2]+'_'+i_time[-2:]+'0000',
        'name': var_name,
        'long_name': 'UNKNOWN',
        'lead': str(int(lead)),
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

            'Nlon': f.dimensions['lon'].size,
            'Nlat': f.dimensions['lat'].size,
            }
        }

#print some output to show script ran successfully
print("Input file: " + repr(input_file))
print("Variable name: " + repr(var_name))
print("valid time: " + repr(val_time.strftime("%Y%m%d%H%M")))
print("Attributes:\t" + repr(attrs))
f.close()
