import sys
import datetime as dt
import numpy as np
from netCDF4 import Dataset


try:
    #user will input name of the file, as well as a percentile they're interested in
    #in future iteration, this may need to change to multiple percentiles (a la list style)
    print("1")
    input_file,ptile = sys.argv[1].split(':')
    f = Dataset(input_file, 'r')
    print("2")
    v = f['poe']
    val_time = f.valid_date_range[1]
    val_time = dt.datetime.strptime(val_time,"%Y%m%d")
    ini_time = str(input_file.split('_')[-2])
    ini_time = dt.datetime.strptime(ini_time,"%Y%m%d")
    print("3")
    lead, rem = divmod((val_time - ini_time).total_seconds(), 3600)
    ptile_ind = np.nonzero(f['ptile'][:] == int(ptile))[0][0]
    print("4")
    lat = np.float64(f.variables['latitude'][:])
    lon = np.float64(f.variables['longitude'][:])
    var = np.float64(v[0,ptile_ind,:,:])
    print(np.amax(var),np.amin(var))
    met_data = var.copy()
except NameError:
    print("Can't find input file")
    sys.exit(1)

attrs = {

        'valid': str(val_time.strftime("%Y%m%d"))+'_000000',
        'init': str(ini_time.strftime("%Y%m%d"))+'_000000',
        'name': 'poe_P'+str(ptile),
        'long_name': v.long_name,
        'lead': str(int(lead)),
        'accum': '00',
        'level': 'SURFACE',
        'units': 'PERCENTILES',

        'grid': {
            'name': 'Global 1 degree',
            'type': 'LatLon',
            'lat_ll': -90.0,
            'lon_ll': 0.0,
            'delta_lat': 1.0,
            'delta_lon': 1.0,

            'Nlon': f.dimensions['longitude'].size,
            'Nlat': f.dimensions['latitude'].size,
            }
        }

#print output for user to show successful run
print("Input file: " + repr(input_file.split('/')[-1]))
print("Attributes:\t"+ repr(attrs))
f.close()

