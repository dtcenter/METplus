"""
Code adapted from Meg Fowler,CGD,NCAR
The code computes the Terrestrial Coupling Index (TCI)
from Sensible Heat Flux and 10 cm Soil Moisture  
Designed to read Sen Heat Flux (CAM) and Soil Temp (CLM)
from two  bove two CESM files 
User needs to provide the season (DJF, MAM, JJA, or SON)
"""


import numpy as np 
import xarray as xr 
import pandas as pd
import datetime
import time
import sys
import os
import netCDF4 as nc

dataDir = '/d1/personal/biswas/feature_2011_TCI_from_CESM_FLUXNET2015/'

#fileCLM = dataDir+'f.e21.FHIST.f09_f09_mg17.CESM2-CLM45physics.002.clm2.h1.1979-83_SoilWater10cm.nc'
#fileCAM = dataDir+'f.e21.FHIST.f09_f09_mg17.CESM2-CLM45physics.002.cam.h1.1979-83_CIvars.nc'

if len(sys.argv) < 3:
    print("Must specify the following elements: sfc_flux_file soil_file season (DJF, MAM, JJA, or SON)")
    sys.exit(1)

fileCLM = os.path.expandvars(sys.argv[1]) 
fileCAM = os.path.expandvars(sys.argv[2]) 
season = sys.argv[3] 

print('Starting Terrestrial Coupling Index Calculation for: ',season)

camDS_CLM45         = xr.open_dataset(fileCAM, decode_times=False)
print('Finished reading in CAM file')
clmDS_CLM45         = xr.open_dataset(fileCLM, decode_times=False)
print('Finished reading in CLM file')

if season=="DJF":
    ss = 0
elif season=="MAM":
    ss = 1
elif season=="JJA":
    ss = 2
elif season=="SON":
    ss = 3
else: 
    sys.exit('ERROR  : URECOGNIZED SEASON, PLEASE USE DJF, MAM, JJA, OR SON')

units, reference_date = camDS_CLM45.time.attrs['units'].split('since')
camDS_CLM45['time'] = pd.date_range(start=reference_date, periods=camDS_CLM45.sizes['time'], freq='D')
camDS_time=camDS_CLM45.time[0]
dt_object = datetime.datetime.utcfromtimestamp(camDS_time.values.tolist()/1e9)
vDate=dt_object.strftime("%Y%m%d")


units, reference_date = clmDS_CLM45.time.attrs['units'].split('since')
clmDS_CLM45['time'] = pd.date_range(start=reference_date, periods=clmDS_CLM45.sizes['time'], freq='D')

ds = camDS_CLM45
ds['SOILWATER_10CM'] = (('time','lat','lon'), clmDS_CLM45.SOILWATER_10CM.values)

xname = 'SOILWATER_10CM'    # Controlling variable
yname = 'SHFLX'             # Responding variable

xday = ds[xname].groupby('time.season')
yday = ds[yname].groupby('time.season')

# Get the covariance of the two (numerator in coupling index)
covarTerm = ((xday - xday.mean()) * (yday - yday.mean())).groupby('time.season').sum() / xday.count()

# Now compute the coupling index
couplingIndex = covarTerm/xday.std()
ci_season=couplingIndex[ss,:,:]

ci = np.where(np.isnan(ci_season), -9999, ci_season)

met_data = ci[:,:]
met_data = met_data[::-1].copy()

#trim the lat/lon grids so they match the data fields
lat_met = camDS_CLM45.lat
lon_met = camDS_CLM45.lon
print(" Model Data shape: "+repr(met_data.shape))
v_str = vDate
v_str = v_str + '_000000'
print(" Valid date: "+v_str)
lat_ll = float(lat_met.min())
lon_ll = float(lon_met.min())
n_lat = lat_met.shape[0]
n_lon = lon_met.shape[0]
delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)

print(f"variables:"
        f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")

attrs = {
        'valid': v_str,
        'init': v_str,
        'lead': "000000",
        'accum': "000000",
        'name': 'TCI',
        'standard_name': 'terrestrial_coupling_index',
        'long_name': 'terrestrial_coupling_index',
        'level': "10cm_soil_depth",
        'units': "psu",

        'grid': {
            'type': "LatLon",
            'name': "CESM Grid",
            'lat_ll': lat_ll,
            'lon_ll': lon_ll,
            'delta_lat': delta_lat,
            'delta_lon': delta_lon,
            'Nlat': n_lat,
            'Nlon': n_lon,
            }
        }
