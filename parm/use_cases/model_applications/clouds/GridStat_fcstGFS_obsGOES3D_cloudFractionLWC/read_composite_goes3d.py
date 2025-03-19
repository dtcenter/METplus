import datetime
import os
import sys
import xarray as xr

satfile = sys.argv[1]
elem = os.path.basename(satfile).split('_')
tstring = elem[3]
valid = datetime.datetime.strptime(tstring,"%Y%m%dT%H%MZ").strftime('%Y%M%d_%H%M%S')

ds = xr.open_dataset(satfile)

met_data = ds['cloud_water_content'].sum(dim='altitude').values
met_data = met_data[::-1].copy()

attrs = {}
grid = {}

grid['type'] = 'LatLon'
grid['name'] = 'CSUSatellite'
grid['lat_ll'] = 20.0
grid['lon_ll'] = -130.0
grid['delta_lat'] = 0.0200005
grid['delta_lon'] = 0.0200043
grid['Nlat'] = 2001
grid['Nlon'] = 3501

attrs['valid'] = valid
attrs['init'] = valid
attrs['lead'] = '000000'
attrs['accum'] = '000000'
attrs['name'] = 'cloud_water_content_colsum'
attrs['long_name'] = 'column sum cloud liquid water content'
attrs['level'] = 'L0'
attrs['units'] = 'g/m3'
attrs['grid'] = grid
