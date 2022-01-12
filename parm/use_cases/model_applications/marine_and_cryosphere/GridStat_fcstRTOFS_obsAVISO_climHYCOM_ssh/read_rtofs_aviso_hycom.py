#!/bin/env python
"""
Code adapted from
Todd Spindler
NOAA/NWS/NCEP/EMC
Designed to read in RTOFS,AVISO,HYCOM and OSTIA data
and based on user input, read ssh data 
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

rtofsfile = os.path.expandvars(sys.argv[1]) 
sshfile = os.path.expandvars(sys.argv[2]) 
icefile = os.path.expandvars(sys.argv[3]) 
climoDir = os.path.expandvars(sys.argv[4]) 
vDate=datetime.strptime(sys.argv[5],'%Y%m%d')
file_flag = sys.argv[6] 

print('Starting Satellite AVISO V&V at',datetime.now(),'for',vDate, ' file_flag:',file_flag)

pd.date_range(vDate,vDate)
platform='AVISO'
param='ssh'


#####################################################################
# READ AVISO data ###################################################
#####################################################################

if not os.path.exists(sshfile):
        print('missing AVISO file for',vDate)

ssh_data=xr.open_dataset(sshfile,decode_times=True)
print('Retrieved SSH above sea level AVISO data from NESDIS for',ssh_data.time.values)
sla=ssh_data.sla.astype('single')
sla.attrs['platform']=platform
sla.attrs['time']=pd.Timestamp(ssh_data.time.values[0])
sla=sla.rename({'longitude':'lon','latitude':'lat'})


# all coords need to be single precision
sla['lon']=sla.lon.astype('single')
sla['lat']=sla.lat.astype('single')
sla.attrs['units']='meters'

adt=ssh_data.adt.astype('single')
adt.attrs['platform']='aviso'
adt.attrs['filename']=sshfile
adt.attrs['time']=pd.Timestamp(ssh_data.time.values[0])
adt=adt.rename({'longitude':'lon','latitude':'lat'})
# all coords need to be single precision
adt['lon']=adt.lon.astype('single')
adt['lat']=adt.lat.astype('single')
adt.attrs['units']='meters'

sla=sla.squeeze()
adt=adt.squeeze()

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

outdata=indata.copy()

outdata=outdata.rename({'Longitude':'lon','Latitude':'lat',})
# all coords need to be single precision
outdata['lon']=outdata.lon.astype('single')
outdata['lat']=outdata.lat.astype('single')
outdata.attrs['platform']='rtofs '+platform

#####################################################################
# READ CLIMO HYCOM data - May require 2 files depending on the date ###
#####################################################################

if not os.path.exists(climoDir):
        print('missing climo file file for',vDate)

vDate=pd.Timestamp(vDate)

climofile="hycom_GLBv0.08_53X_archMN.1994_{0:02n}_2015_{0:02n}_ssh.nc".format(vDate.month)
climo_data=xr.open_dataset(climoDir+'/'+climofile,decode_times=False)
#climo_data=climo_data['surf_el'].squeeze()[0,]

if vDate.day==15:  # even for Feb, just because
    climofile="hycom_GLBv0.08_53X_archMN.1994_{0:02n}_2015_{0:02n}_ssh.nc".format(vDate.month)
    climo_data=xr.open_dataset(climoDir+'/'+climofile,decode_times=False)
    climo_data=climo_data['surf_el'].copy().squeeze()
else:
    if vDate.day < 15:
        start=vDate - DateOffset(months=1,day=15)
        stop=pd.Timestamp(vDate.year,vDate.month,15)
    else:
        start=pd.Timestamp(vDate.year,vDate.month,15)
        stop=vDate + DateOffset(months=1,day=15)
    left=(vDate-start)/(stop-start)
        
    climofile1="hycom_GLBv0.08_53X_archMN.1994_{0:02n}_2015_{0:02n}_ssh.nc".format(start.month)
    climofile2="hycom_GLBv0.08_53X_archMN.1994_{0:02n}_2015_{0:02n}_ssh.nc".format(stop.month)
    climo_data1=xr.open_dataset(climoDir+'/'+climofile1,decode_times=False)
    climo_data2=xr.open_dataset(climoDir+'/'+climofile2,decode_times=False)
    climo_data1=climo_data1['surf_el'].copy().squeeze()
    climo_data2=climo_data2['surf_el'].copy().squeeze()
    climo_data=climo_data1+((climo_data2-climo_data1)*left)
    climofile='weighted average of '+climofile1+' and '+climofile2

    print('climofile1 :', climofile1)
    print('climofile2 :', climofile2)

climo_data.coords['time']=datetime(vDate.year,vDate.month,1)   # just a reference to the month
# all coords need to be single precision

climo_data['lon']=climo_data.lon.astype('single')
climo_data['lat']=climo_data.lat.astype('single')
climo_data.attrs['platform']='hycom'
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
    model2=model.copy()
    model2_lon=model2.lon.values
    model2_lat=model2.lat.values
    model2_data=model2.to_masked_array()
    if model2_lon.ndim==1:
        model2_lon,model2_lat=np.meshgrid(model2_lon,model2_lat)

    obs2=obs.copy()
    obs2_lon=obs2.lon.astype('single').values
    obs2_lat=obs2.lat.astype('single').values
    obs2_data=obs2.astype('single').to_masked_array()
    if obs2.lon.ndim==1:
        obs2_lon,obs2_lat=np.meshgrid(obs2.lon.values,obs2.lat.values)

    model2_lon1=pyr.utils.wrap_longitudes(model2_lon)
    model2_lat1=model2_lat.copy()
    obs2_lon1=pyr.utils.wrap_longitudes(obs2_lon)
    obs2_lat1=obs2_lat.copy()

    # pyresample gausshian-weighted kd-tree interp
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
    return data3

#ssh_data2=ssh_data.squeeze()

print('regridding climo to obs')
climo_data=climo_data.squeeze()
climo_data=regrid(climo_data,adt)

print('regridding ice to obs')
ice_data2=regrid(ice_data2,adt)

print('regridding model to obs')
model2=regrid(outdata,adt)

# combine obs ice mask with ncep
obs2=adt.to_masked_array()
obs_anom=sla.copy()
obs_anom2=obs_anom.to_masked_array()
ice2=ice_data2.to_masked_array()
climo2=climo_data.to_masked_array()
model2=model2.to_masked_array()

#reconcile with obs
obs2.mask=np.ma.mask_or(obs2.mask,ice2>0.0)
obs2.mask=np.ma.mask_or(obs2.mask,climo2.mask)
obs2.mask=np.ma.mask_or(obs2.mask,model2.mask)
climo2.mask=obs2.mask
model2.mask=obs2.mask
obs_anom2.mask=obs2.mask

obs2=xr.DataArray(obs2,coords=[adt.lat.values,adt.lon.values], dims=['lat','lon'])
obs_anom2=xr.DataArray(obs_anom2,coords=[adt.lat.values,adt.lon.values], dims=['lat','lon'])
model2=xr.DataArray(model2,coords=[adt.lat.values,adt.lon.values], dims=['lat','lon'])
climo2=xr.DataArray(climo2,coords=[adt.lat.values,adt.lon.values], dims=['lat','lon'])

model2=expand_grid(model2)
climo2=expand_grid(climo2)
obs2=expand_grid(obs2)
obs_anom2=expand_grid(obs_anom2)

#Create the MET grids based on the file_flag
if file_flag == 'fcst':
    met_data = model2[:,:]
    #trim the lat/lon grids so they match the data fields
    lat_met = model2.lat
    lon_met = model2.lon
    print(" RTOFS Data shape: "+repr(met_data.shape))
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
            'name': 'ssh',
            'standard_name': 'sea_surface_height',
            'long_name': 'sea_surface_height',
            'level': "SURFACE",
            'units': "psu",

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
            'name': 'ssh',
            'standard_name': 'analyzed sea surface height',
            'long_name': 'sea_surface_height',
            'level': "SURFACE",
            'units': "psu",

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
            'name': 'sea_surface_height',
            'standard_name': 'sea_surface_height',
            'long_name': 'sea_surface_height',
            'level': "SURFACE",
            'units': "psu",

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

