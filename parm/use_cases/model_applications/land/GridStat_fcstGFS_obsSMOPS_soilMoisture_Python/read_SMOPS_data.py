import sys
from netCDF4 import Dataset
import numpy as np

filename, vari_name = sys.argv[1:]

f_in = Dataset(filename, 'r')

met_data = f_in[vari_name][:]
date_info = f_in.Date_Start


attrs = {

        'valid': str(date_info)+'_000000',
        'init': str(date_info)+'_000000',
        'name': vari_name,
        'long_name': f_in[vari_name].long_name,
        'lead': '00',
        'accum': '00',
        'level': 'UNKNOWN',
        'units': f_in[vari_name].units,

        'grid': {
            'name': 'Global 0.25 degree',
            'type': 'LatLon',
            'lat_ll': -90.0,
            'lon_ll': -180.0,
            'delta_lat': 0.25,
            'delta_lon': 0.25,

            'Nlon': f_in.dimensions['Longitude'].size,
            'Nlat': f_in.dimensions['Latitude'].size,
            }
        }

#print some output to show script ran successfully
print("Input file: " + repr(filename))
print("Variable name: " + repr(vari_name))
print("Attributes:\t" + repr(attrs))
f_in.close()
