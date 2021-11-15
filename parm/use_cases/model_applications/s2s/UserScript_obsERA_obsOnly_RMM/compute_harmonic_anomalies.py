#!/usr/bin/env python3
import numpy as np
import xarray as xr
import glob
import os
import sys
import datetime
import METreadnc.util.read_netcdf as read_netcdf

input_mean_daily_annual_infiles_list = os.environ[sys.argv[1]]
dm_var = sys.argv[2]
mda_var = sys.argv[3]
anom_output_dir = sys.argv[4]
anom_output_base = sys.argv[5]
input_daily_mean_infiles_list = os.environ['METPLUS_FILELIST_INPUT_DAILY_MEAN_INFILES']

# Environment variables for script
nobs = int(os.environ.get('OBS_PER_DAY',1))
out_var = dm_var+'_anom'

# Read the listing of files
with open(input_daily_mean_infiles_list) as idm:
    input_daily_mean_infiles = idm.read().splitlines()
if (input_daily_mean_infiles[0] == 'file_list'):
    input_daily_mean_infiles = input_daily_mean_infiles[1:]

with open(input_mean_daily_annual_infiles_list) as imda:
    input_mean_daily_annual_infiles = imda.read().splitlines()
if (input_mean_daily_annual_infiles[0] == 'file_list'):
    input_mean_daily_annual_infiles = input_mean_daily_annual_infiles[1:]


# Read in the data
netcdf_reader = read_netcdf.ReadNetCDF()
dm_orig = netcdf_reader.read_into_xarray(input_daily_mean_infiles)
# Add some needed attributes
dm_list = []
time_dm = []
yr_dm = []
doy_dm = []
for din in dm_orig:
    ctime =  datetime.datetime.strptime(din[dm_var].valid_time,'%Y%m%d_%H%M%S')
    time_dm.append(ctime.strftime('%Y-%m-%d'))
    yr_dm.append(int(ctime.strftime('%Y')))
    doy_dm.append(int(ctime.strftime('%j')))
    din = din.assign_coords(time=ctime)
    din = din.expand_dims("time")
    dm_list.append(din)
time_dm = np.array(time_dm,dtype='datetime64[D]')
yr_dm = np.array(yr_dm)
doy_dm = np.array(doy_dm)
everything = xr.concat(dm_list,"time")
dm_data = np.array(everything[dm_var])

netcdf_reader2 = read_netcdf.ReadNetCDF()
mda_orig = netcdf_reader2.read_into_xarray(input_mean_daily_annual_infiles)
# Add some needed attributes
mda_list = []
time_mda = []
for din in mda_orig:
    ctime =  datetime.datetime.strptime(din[mda_var].valid_time,'%Y%m%d_%H%M%S')
    time_mda.append(ctime.strftime('%Y-%m-%d'))
    din = din.assign_coords(time=ctime)
    din = din.expand_dims("time")
    mda_list.append(din)
time_mda = np.array(time_mda,dtype='datetime64[D]')
everything2 = xr.concat(mda_list,"time")
mda_data = np.array(everything2[mda_var])

# Harmonic Analysis, first step is Forward Fast Fourier Transform
clmfft =  np.fft.rfft(mda_data,axis=0)

smthfft = np.zeros(clmfft.shape,dtype=complex)
for f in np.arange(0,3):
    smthfft[f,:,:] = clmfft[f,:,:]

clmout = np.fft.irfft(smthfft,axis=0)

# Subtract the clmout from the data to create anomalies, each year at a time
yrstrt = yr_dm[0]
yrend = yr_dm[-1]
anom = np.zeros(dm_data.shape)

for y in np.arange(yrstrt,yrend+1,1):
    curyr = np.where(yr_dm == y)
    dd = doy_dm[curyr] - 1
    ndd = len(curyr[0])
    clmshp = [np.arange(dd[0]*nobs,dd[0]*nobs+ndd,1)]
    anom[curyr,:,:] = dm_data[curyr,:,:] - clmout[clmshp,:,:]

# Assign to an xarray and write output
if not os.path.exists(anom_output_dir):
    os.makedirs(anom_output_dir)
for o in np.arange(0,len(dm_orig)):
    dm_orig_cur = dm_orig[o]
    dout = xr.Dataset({out_var: (("lat", "lon"),anom[o,:,:])},
    coords={"lat": dm_orig_cur.coords['lat'], "lon": dm_orig_cur.coords['lon']},
    attrs=dm_orig_cur.attrs)
    dout[out_var].attrs = dm_orig_cur[dm_var].attrs
    dout[out_var].attrs['long_name'] = dm_orig_cur[dm_var].attrs['long_name']+' Anomalies'
    dout[out_var].attrs['name'] = out_var

    # write to a file
    cvtime = datetime.datetime.strptime(dm_orig_cur[dm_var].valid_time,'%Y%m%d_%H%M%S')
    citime = datetime.datetime.strptime(dm_orig_cur[dm_var].init_time,'%Y%m%d_%H%M%S')
    cltime = (cvtime - citime)
    leadmin,leadsec = divmod(cltime.total_seconds(), 60)
    leadhr,leadmin = divmod(leadmin,60)
    lead_str = str(int(leadhr)).zfill(2)+str(int(leadmin)).zfill(2)+str(int(leadsec)).zfill(2)
    dout.to_netcdf(os.path.join(anom_output_dir,anom_output_base+'_'+lead_str+'L_'+cvtime.strftime('%Y%m%d')+'_'+cvtime.strftime('%H%M%S')+'V.nc'))
