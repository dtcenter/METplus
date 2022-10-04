#!/bin/env python
"""
Code adapted from
Todd Spindler
NOAA/NWS/NCEP/EMC

Designed to read in RTOFS and OSTIA data
and based on user input, process Arctic or Antarctic regions
for ice cover, and pass back in memory the forecast or observation
data field
"""

import numpy as np
from sklearn.metrics import mean_squared_error
import xarray as xr
import pandas as pd
from pyproj import Geod
import pyresample as pyr
from datetime import datetime, date
import os, sys

#-------------------------------------
def iceArea(lon1,lat1,ice1):
    """
    Compute the cell side dimensions (Vincenty) and the cell surface areas.
    This assumes the ice has already been masked and subsampled as needed    
    returns ice_extent, ice_area, surface_area = iceArea(lon,lat,ice)
    surface_area is the computed grid areas in km**2)
    """
    lon=lon1.copy()
    lat=lat1.copy()
    ice=ice1.copy()
    g=Geod(ellps='WGS84')
    _,_,xdist=g.inv(lon,lat,np.roll(lon,-1,axis=1),np.roll(lat,-1,axis=1))
    _,_,ydist=g.inv(lon,lat,np.roll(lon,-1,axis=0),np.roll(lat,-1,axis=0))
    xdist=np.ma.array(xdist,mask=ice.mask)/1000.
    ydist=np.ma.array(ydist,mask=ice.mask)/1000.
    xdist=xdist[:-1,:-1]
    ydist=ydist[:-1,:-1]
    ice=ice[:-1,:-1]     # just to match the roll
    extent=xdist*ydist   # extent is surface area only
    area=xdist*ydist*ice # ice area is actual ice cover (area * concentration)
    return extent.flatten().sum(), area.flatten().sum(), extent

#--------------------------------------------------------

try:
    rtofsfile, icefile, hemisphere, file_flag = sys.argv[1:]
except ValueError:
    print("Must specify the following elements: fcst_file obs_file hemisphere file_flag")
    sys.exit(1)

HEMISPHERES = ['north', 'south']
FILE_FLAGS = ['fcst', 'obs']

if hemisphere not in HEMISPHERES or file_flag not in FILE_FLAGS:
    print(f"ERROR: Invalid hemisphere value ({hemisphere}) or file_flag value ({file_flag}) "
            f"Valid options are {HEMISPHERES} {FILE_FLAGS}")
    sys.exit(1)

print('processing',hemisphere+'ern hemisphere')
if hemisphere == 'north':
    bounding_lat=30.98
else:
    bounding_lat=-39.23
        

# load rtofs data and subset to hemisphere of interest and ice cover min value
print('reading rtofs ice')
if not os.path.exists(rtofsfile):
    print('missing rtofs file',rtofsfile)
    sys.exit(1)
rtofs=xr.open_dataset(rtofsfile,decode_times=True)
rtofs=rtofs.ice_coverage[0,:-1,]
            
# load OSTIA data
print('reading OSTIA ice')
if not os.path.exists(icefile):
    print('missing OSTIA ice file',icefile)
    sys.exit(1)
ncep=xr.open_dataset(icefile,decode_times=True)
ncep=ncep.rename({'lon':'Longitude','lat':'Latitude'})
ncep=ncep.sea_ice_fraction.squeeze()
    
# trim to polar regions
if hemisphere == 'north':
    rtofs=rtofs.where((rtofs.Latitude>=bounding_lat),drop=True) 
    ncep=ncep.where((ncep.Latitude>=bounding_lat),drop=True) 
else:
    rtofs=rtofs.where((rtofs.Latitude<=bounding_lat),drop=True) 
    ncep=ncep.where((ncep.Latitude<=bounding_lat),drop=True) 
    
# now it's back to masked arrays for the RTOFS data
rlon=rtofs.Longitude.values
rlat=rtofs.Latitude.values
rice=rtofs.to_masked_array()

nlon=ncep.Longitude.values%360. # shift from -180 - 180 to 0-360
nlat=ncep.Latitude.values
nlon,nlat=np.meshgrid(nlon,nlat)  # shift from 1-d to 2-d arrays
nice=ncep.to_masked_array()
    
# mask out values below 15%
rice.mask=np.ma.mask_or(rice.mask,rice<0.15)
nice.mask=np.ma.mask_or(nice.mask,nice<0.15)

# compute ice area on original grids
print('computing ice area')
ncep_extent,ncep_area,ncep_surface_area=iceArea(nlon,nlat,nice)
rtofs_extent,rtofs_area,rtofs_surface_area=iceArea(rlon,rlat,rice)
    
# interpolate rtofs to ncep grid
print('interpolating rtofs to OSTIA grid')            
    
# pyresample gausssian-weighted kd-tree interp
rlon1=pyr.utils.wrap_longitudes(rlon)
rlat1=rlat.copy()
nlon1=pyr.utils.wrap_longitudes(nlon)
nlat1=nlat.copy()
# define the grids
orig_def = pyr.geometry.GridDefinition(lons=rlon1,lats=rlat1)
targ_def = pyr.geometry.GridDefinition(lons=nlon1,lats=nlat1)
radius=50000
sigmas=25000    
rice2=pyr.kd_tree.resample_gauss(orig_def,rice,targ_def,
                                     radius_of_influence=radius,
                                     sigmas=sigmas,
                                     nprocs=8,
                                     neighbours=8,
                                     fill_value=None)
            
print('creating combined mask')
combined_mask=np.logical_and(nice.mask,rice2.mask)
nice2=nice.filled(fill_value=0.0)
rice2=rice2.filled(fill_value=0.0)
nice2=np.ma.array(nice2,mask=combined_mask)
rice2=np.ma.array(rice2,mask=combined_mask)

#Create the MET grids based on the file_flag
if file_flag == 'fcst':
    met_data = rice2[:-1,:-1]
    met_data = met_data[::-1,]
    #trim the lat/lon grids so they match the data fields
    #note that nice1 lat/lon fields are valid, since rice2 is interpolated to nice2
    lat_met = nlat1[:-1,:-1]
    lon_met = nlon1[:-1,:-1]
    print("Data shape: "+repr(met_data.shape))
    v_str = rtofsfile.split('_')[-6].split('/')[-1]
    v_str = v_str + '_120000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[1]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'ice_coverage',
            'standard_name': rtofs.standard_name,
            'long_name': rtofs.long_name.strip(),
            'level': "SURFACE",
            'units': "UNKNOWN",

            'grid': {
                'type': "LatLon",
                'name': "RTOFS Grid",
                'lat_ll': lat_ll,
                'lon_ll': lon_ll,
                'delta_lat': delta_lat,
                'delta_lon': delta_lon,
                'Nlat': n_lat,
                'Nlon': n_lon,
                }
            }
    attrs = met_data.attrs
if file_flag == 'obs':
    met_data = nice2[:-1,:-1]
    met_data = met_data[::-1,]
    #modify the lat and lon grids since they need to match the data dimensions, and code cuts the last row/column of data
    lat_met = nlat1[:-1,:-1]
    lon_met = nlon1[:-1,:-1]
    print("Data shape: " +repr(met_data.shape))
    v_str = icefile.split('_')[-3].split('/')[-1]
    v_str = v_str[:-2]+'_120000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[1]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'ice_coverage',
            'standard_name': ncep.standard_name,
            'long_name': ncep.long_name.strip(),
            'level': "SURFACE",
            'units': "UNKNOWN",

            'grid': {
                'type': "LatLon",
                'name': "RTOFS Grid",
                'lat_ll': lat_ll,
                'lon_ll': lon_ll,
                'delta_lat': delta_lat,
                'delta_lon': delta_lon,
                'Nlat': n_lat,
                'Nlon': n_lon,
                }
            }
    attrs = met_data.attrs

