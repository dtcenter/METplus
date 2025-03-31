# Script to read SFS-GSL model output. 
# Separate monthly files
# Data description
# 5 member ensemble, target: forecast target month
# Variable: fcst(ensmem, target, lat, lon)
 
import sys
import re
import numpy as np
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import *
from netCDF4 import Dataset, chartostring
import pandas as pd

print('Usage')
print('/location/of/model/data valid_month valid_year')

# Define inputs
#print('arguments: '+str(arguments))

path = sys.argv[0]
print('path: ' + path)
mod_path = sys.argv[1]
print('mod_path: ' + mod_path)
valid_month = sys.argv[2]
print('Valid Month: ' + valid_month)
year = sys.argv[3]
print('Year: ' + str(year))

valid_time = year+valid_month
valid_time = dt.datetime.strptime(valid_time,"%Y%m")

print('Reading input file')

# Setup data to be read into MET

f = Dataset(mod_path, 'r')

lat    = f.variables['lat'][::-1]
lon    = f.variables['lon'][:]
fcst   = f.variables['fcst'][:]      
target = f.variables['target'][:] 

mon_since = datetime(1960, 1, 1)
target_dates = [mon_since + pd.DateOffset(months=int(months)) for months in target]

#Get valid month from arguments above
val_month = int(valid_month)
desired_dates = [i for i, date in enumerate(target_dates) if date.month == val_month]

if not desired_dates:
   print(f"No data available for the specified month: {desired_month}")
else:
   # Extract the forecast data for the specified month
   fcst_for_month = fcst[:, desired_dates, :, :]
        
   # Calculate the mean over the ensemble dimension (ensmem)
   var = np.mean(fcst_for_month, axis=0)

val_time = valid_time
print('Valid Time: ' + str(val_time))
print('Shape of variable to read into MET: ' + str(var.shape))

#squeeze out all 1d arrays, add fill value, convert to float64
var = np.float64(var)
var[var < 0] = np.nan

met_data = np.squeeze(var).copy()

#create a metadata dictionary

attrs = {

        'valid': str(val_time.strftime("%Y%m%d"))+'_'+str(val_time.strftime("%H%M%S")),
        'init': str(val_time.strftime("%Y%m%d"))+'_'+str(val_time.strftime("%H%M%S")),
        'name': 'Soil_moisture',
        'long_name': 'SFS_GSL 0-1m soilm1m ensemble mean',
        'lead': str(int(valid_month)),
        'accum': '00',
        'level': '0-1m',
        'units': 'mm',
        'grid': {
            'name': 'Global 1 degree',
            'type': 'LatLon',
            'lat_ll': -90.0,
            'lon_ll': 0.0,
            'delta_lat': 1.0,
            'delta_lon': 1.0,

            'Nlon': f.dimensions['lon'].size,
            'Nlat': f.dimensions['lat'].size,
            }
        }


print("valid time: " + repr(val_time.strftime("%Y%m%d%H%M")))
print("Attributes:\t" + repr(attrs))
f.close()
