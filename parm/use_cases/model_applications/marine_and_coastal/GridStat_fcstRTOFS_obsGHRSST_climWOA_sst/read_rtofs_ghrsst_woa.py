#!/usr/bin/env python3
"""
Code adapted from
Todd Spindler
NOAA/NWS/NCEP/EMC
Designed to read in RTOFS,GHRSST,WOA and OSTIA data
and based on user input, read sst data 
and pass back in memory the forecast, observation, or climatology
data field
"""

import numpy as np
import xarray as xr
import pandas as pd
import pyresample as pyr
from pandas.tseries.offsets import DateOffset
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
import io
from glob import glob
import warnings
import os, sys


if len(sys.argv) < 6:
    print("Must specify the following elements: fcst_file obs_file ice_file, climo_file, valid_date, file_flag")
    sys.exit(1)
#grab input files from command line input
rtofsfile = os.path.expandvars(sys.argv[1]) 
sstfile = os.path.expandvars(sys.argv[2]) 
icefile = os.path.expandvars(sys.argv[3]) 
climoDir = os.path.expandvars(sys.argv[4]) 
vDate=datetime.strptime(sys.argv[5],'%Y%m%d')
file_flag = sys.argv[6] 

print('Starting Satellite GHRSST V&V at',datetime.now(),'for',vDate, ' file_flag:',file_flag)

pd.date_range(vDate,vDate)
platform='GHRSST'
param='sst'


#####################################################################
# READ GHRSST data ##################################################
#####################################################################

if not os.path.exists(sstfile):
        print('missing GHRSST file for',vDate)

sst_data=xr.open_dataset(sstfile,decode_times=True)
sst_data['time']=sst_data.time-pd.Timedelta('12H')  # shift 12Z offset time to 00Z
sst_data2=sst_data.analysed_sst.astype('single')-273.15 # convert from Kelvin
print('Retrieved GHRSST data from NESDIS for',sst_data2.time.values)

sst_data2['lon']=sst_data2.lon.astype('single')
sst_data2['lat']=sst_data2.lat.astype('single')
#sst_data2.attrs['platform']='ghrsst'
sst_data2.attrs['platform']=platform
sst_data2.attrs['units']='degC'

#####################################################################
# READ RTOFS data (model output in Tri-polar coordinates) ###########
#####################################################################

print('reading rtofs ice')
if not os.path.exists(rtofsfile):
    print('missing rtofs file',rtofsfile)
    sys.exit(1)

indata=xr.open_dataset(rtofsfile,decode_times=True)


indata=indata.mean(dim='MT')
indata = indata[param][:-1,]
indata.coords['time']=vDate
#indata.coords['fcst']=fcst

#outdata=indata.copy()
#indata.close()

outdata=indata

outdata=outdata.rename({'Longitude':'lon','Latitude':'lat',})
# all coords need to be single precision
outdata['lon']=outdata.lon.astype('single')
outdata['lat']=outdata.lat.astype('single')
outdata.attrs['platform']='rtofs '+platform

#####################################################################
# READ CLIMO WOA data - May require 2 files depending on the date ###
#####################################################################

if not os.path.exists(climoDir):
        print('missing climo file file for',vDate)

vDate=pd.Timestamp(vDate)

#climofile="woa13_decav_t{:02n}_04v2.nc".format(vDate.month)
#climo_data=xr.open_dataset(climoDir+'/'+climofile,decode_times=False)
#climo_data=climo_data['t_an'].squeeze()[0,]

if vDate.day==15:  # even for Feb, just because
    climofile="woa13_decav_t{:02n}_04v2.nc".format(vDate.month)
    climo_data=xr.open_dataset(climoDir+'/'+climofile,decode_times=False)
    climo_data=climo_data['t_an'].squeeze()[0,]  # surface only
else:
    if vDate.day < 15:
        start=vDate - DateOffset(months=1,day=15)
        stop=pd.Timestamp(vDate.year,vDate.month,15)
    else:
        start=pd.Timestamp(vDate.year,vDate.month,15)
        stop=vDate + DateOffset(months=1,day=15)
    left=(vDate-start)/(stop-start)
        
    climofile1="woa13_decav_t{:02n}_04v2.nc".format(start.month)
    climofile2="woa13_decav_t{:02n}_04v2.nc".format(stop.month)
    climo_xr1=xr.open_dataset(climoDir+'/'+climofile1,decode_times=False)
    climo_xr2=xr.open_dataset(climoDir+'/'+climofile2,decode_times=False)
    climo_data1=climo_xr1['t_an'].squeeze()[0,]  # surface only
    climo_data2=climo_xr2['t_an'].squeeze()[0,]  # surface only

    climo_xr1.close()
    climo_xr2.close()

    print('climofile1 :', climofile1)
    print('climofile2 :', climofile2)
    climo_data=climo_data1+((climo_data2-climo_data1)*left)
    climofile='weighted average of '+climofile1+' and '+climofile2

# all coords need to be single precision
climo_data['lon']=climo_data.lon.astype('single')
climo_data['lat']=climo_data.lat.astype('single')
climo_data.attrs['platform']='woa'
climo_data.attrs['filename']=climofile

#####################################################################
# READ ICE data for masking #########################################
#####################################################################

if not os.path.exists(icefile):
        print('missing OSTIA ice file for',vDate)

ice_data=xr.open_dataset(icefile,decode_times=True)
ice_data=ice_data.rename({'sea_ice_fraction':'ice'})

# all coords need to be single precision
ice_data2=ice_data.ice.astype('single')
ice_data2['lon']=ice_data2.lon.astype('single')
ice_data2['lat']=ice_data2.lat.astype('single')


def regrid(model,obs):
    """
    regrid data to obs -- this assumes DataArrays
    """
    #model2=model.copy()
    model2=model
    model2_lon=model2.lon.values
    model2_lat=model2.lat.values
    model2_data=model2.to_masked_array()
    if model2_lon.ndim==1:
        model2_lon,model2_lat=np.meshgrid(model2_lon,model2_lat)

    #obs2=obs.copy()
    obs2=obs
    obs2_lon=obs2.lon.astype('single').values
    obs2_lat=obs2.lat.astype('single').values
    obs2_data=obs2.astype('single').to_masked_array()
    if obs2.lon.ndim==1:
        obs2_lon,obs2_lat=np.meshgrid(obs2.lon.values,obs2.lat.values)

    model2_lon1=pyr.utils.wrap_longitudes(model2_lon)
    #model2_lat1=model2_lat.copy()
    model2_lat1=model2_lat
    obs2_lon1=pyr.utils.wrap_longitudes(obs2_lon)
    #obs2_lat1=obs2_lat.copy()
    obs2_lat1=obs2_lat

    # pyresample gausssian-weighted kd-tree interp
    # define the grids
    orig_def = pyr.geometry.GridDefinition(lons=model2_lon1,lats=model2_lat1)
    targ_def = pyr.geometry.GridDefinition(lons=obs2_lon1,lats=obs2_lat1)
    radius=50000
    sigmas=25000
    model2_data2=pyr.kd_tree.resample_gauss(orig_def,model2_data,targ_def,
                                            radius_of_influence=radius,
                                            sigmas=sigmas,
                                            fill_value=None)
    model=xr.DataArray(model2_data2,coords=[obs.lat.values,obs.lon.values],dims=['lat','lon'])

    return model

def expand_grid(data):
    """
    concatenate global data for edge wraps
    """

    data2=data.copy()
    data2['lon']=data2.lon+360
    data3=xr.concat((data,data2),dim='lon')
    data2.close()
    data.close()
    return data3

sst_data2=sst_data2.squeeze()

#print('regridding climo to obs')
climo_data=climo_data.squeeze()
climo_data=regrid(climo_data,sst_data2)

#print('regridding ice to obs')
ice_data2=regrid(ice_data2,sst_data2)

#print('regridding model to obs')
model2=regrid(outdata,sst_data2)

# combine obs ice mask with ncep
obs2=sst_data2.to_masked_array()
ice2=ice_data2.to_masked_array()
climo2=climo_data.to_masked_array()
model2=model2.to_masked_array()

#reconcile with obs
obs2.mask=np.ma.mask_or(obs2.mask,ice2>0.0)
obs2.mask=np.ma.mask_or(obs2.mask,climo2.mask)
obs2.mask=np.ma.mask_or(obs2.mask,model2.mask)
climo2.mask=obs2.mask
model2.mask=obs2.mask

coord_lat = sst_data2.lat.values
coord_lon = sst_data2.lon.values

sst_data2.close()

#Create the MET grids based on the file_flag
if file_flag == 'fcst':
    #model2=xr.DataArray(model2,coords=[sst_data2.lat.values,sst_data2.lon.values], dims=['lat','lon'])
    model2=xr.DataArray(model2,coords=[coord_lat,coord_lon], dims=['lat','lon'])
    model2=expand_grid(model2)
    met_data = model2[:,:]
    #trim the lat/lon grids so they match the data fields
    lat_met = model2.lat
    lon_met = model2.lon
    #print(" RTOFS Data shape: "+repr(met_data.shape))
    v_str = vDate.strftime("%Y%m%d")
    v_str = v_str + '_000000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[0]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'sst',
            'standard_name': 'sst',
            'long_name': 'sst',
            'level': "SURFACE",
            'units': "degC",

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
    #obs2=xr.DataArray(obs2,coords=[sst_data2.lat.values,sst_data2.lon.values], dims=['lat','lon'])
    obs2=xr.DataArray(obs2,coords=[coord_lat, coord_lon], dims=['lat','lon'])
    obs2=expand_grid(obs2)
    met_data = obs2[:,:]
    #trim the lat/lon grids so they match the data fields
    lat_met = obs2.lat
    lon_met = obs2.lon
    v_str = vDate.strftime("%Y%m%d")
    v_str = v_str + '_000000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[0]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'sst',
            'standard_name': 'analyzed sst',
            'long_name': 'analyzed sst',
            'level': "SURFACE",
            'units': "degC",

            'grid': {
                'type': "LatLon",
                'name': "Lat Lon",
                'lat_ll': lat_ll,
                'lon_ll': lon_ll,
                'delta_lat': delta_lat,
                'delta_lon': delta_lon,
                'Nlat': n_lat,
                'Nlon': n_lon,
                }
            }
    attrs = met_data.attrs

if file_flag == 'climo':
    #climo2=xr.DataArray(climo2,coords=[sst_data2.lat.values,sst_data2.lon.values], dims=['lat','lon'])
    climo2=xr.DataArray(climo2,coords=[coord_lat, coord_lon], dims=['lat','lon'])
    climo2=expand_grid(climo2)
    met_data = climo2[:,:]
    #modify the lat and lon grids since they need to match the data dimensions, and code cuts the last row/column of data
    lat_met = climo2.lat
    lon_met = climo2.lon
    v_str = vDate.strftime("%Y%m%d")
    v_str = v_str + '_000000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[0]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'sea_water_temperature',
            'standard_name': 'sea_water_temperature',
            'long_name': 'sea_water_temperature',
            'level': "SURFACE",
            'units': "degC",

            'grid': {
                'type': "LatLon",
                'name': "crs Grid",
                'lat_ll': lat_ll,
                'lon_ll': lon_ll,
                'delta_lat': delta_lat,
                'delta_lon': delta_lon,
                'Nlat': n_lat,
                'Nlon': n_lon,
                }
            }
    attrs = met_data.attrs

