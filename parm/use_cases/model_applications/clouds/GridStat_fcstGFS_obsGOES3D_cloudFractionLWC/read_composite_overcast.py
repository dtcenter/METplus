import datetime
import os
import sys
import xarray as xr

# Split the input filename and extract the time from the filename.
# The expected fielname format is:
# GEO-stitch-cloud3d_L3_2.3.1_YYYYMMDDTHHMMZ_CONUS.nc
satfile = sys.argv[1]
elem = os.path.basename(satfile).split('_')
tstring = elem[3]
valid = datetime.datetime.strptime(tstring,"%Y%m%dT%H%MZ").strftime('%Y%M%d_%H%M%S')

# Open the file with Xarray
ds = xr.open_dataset(satfile)

# Use Xarray to sum the cloud_water_content variable across the vertical dimension named altitude
# to create a total atmospheric cloud water content variable
met_data = ds['cloud_water_content'].sum(dim='altitude').values

# Flip the data along the horizontal axis due to the way MET reads the data
met_data = met_data[::-1].copy()

# Dictionaries for data and grid attributes
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
