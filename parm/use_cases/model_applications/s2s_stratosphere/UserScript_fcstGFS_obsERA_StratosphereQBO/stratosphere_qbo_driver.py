#!/usr/bin/env python3

"""
Create QBO 

"""
import os
#import sys
import datetime
import numpy as np
import xarray as xr
import pandas as pd
#import matplotlib as mpl
#import matplotlib.patheffects as PathEffects
from eofs.xarray import Eof
#from matplotlib import pyplot as plt

import metcalcpy.pre_processing.directional_means as directional_means
import METreadnc.util.read_netcdf as read_netcdf
from metplotpy.contributed.stratosphere_diagnostics.stratosphere_plots import plot_qbo_phase_circuits,plot_qbo_phase_space,plot_u_timeseries
from metcalcpy.util.write_mpr import write_mpr_file


def process_single_file(infile,latvar,latdim,londim,lat_min,lat_max,pres_min,pres_max):

    file_reader = read_netcdf.ReadNetCDF()
    ds = file_reader.read_into_xarray(infile)[0]
    ds = ds.assign_coords({latdim:ds[latvar].values})
    #ds = ds.assign_coords({londim:ds[lonvar].values})

    # Compute zonal mean
    Uzm = directional_means.zonal_mean(ds,dimvar=londim)

    # Limit the data to 100 - 10 hPa
    Uzm = Uzm.sel(pres=slice(pres_min,pres_max))

    #Compute Meridional Mean
    U_1010 = directional_means.meridional_mean(Uzm, lat_min, lat_max, dimvar=latdim)

    return U_1010


def get_qbo_data(input_files,latvar,latdim,londim,timevar,lat_min,lat_max,pres_min,pres_max):

    # Read the first file
    ds = process_single_file(input_files[0],latvar,latdim,londim,lat_min,lat_max,pres_min,pres_max)
    # Read the rest of the files and concatenate
    for f in input_files[1:]:
        # Read in the data file
        ds2 = process_single_file(f,latvar,latdim,londim,lat_min,lat_max,pres_min,pres_max)
        # Save to array
        ds = xr.concat([ds,ds2],dim=timevar)

    return ds


def main():

    """
    Get the input variables
    """
    # Read the variable names for lat, lon, and time
    obs_latvar = os.environ.get('OBS_LAT_VAR','latitude')
    #obs_lonvar = os.environ.get('OBS_LON_VAR','longitude')
    obs_latdim = os.environ.get('OBS_LAT_DIM','lat')
    obs_londim = os.environ.get('OBS_LON_DIM','lon')
    obs_timevar = os.environ.get('OBS_TIME_VAR','time')
    obs_uvar = os.environ.get('OBS_U_VAR','u')

    fcst_latvar = os.environ.get('FCST_LAT_VAR','latitude')
    #fcst_lonvar = os.environ.get('FCST_LON_VAR','longitude')
    fcst_latdim = os.environ.get('FCST_LAT_DIM','lat')
    fcst_londim = os.environ.get('FCST_LON_DIM','lon')
    fcst_timevar = os.environ.get('FCST_TIME_VAR','time')
    fcst_uvar = os.environ.get('FCST_U_VAR','u')

    # Read the lat bounds, default -10 to 10
    lat_min = int(os.environ.get('LAT_MIN','-10'))
    lat_max = int(os.environ.get('LAT_MAX','10'))

    # Read the Pressure level bounds, default is 100 to 10
    pres_min = int(os.environ.get('PRES_LEV_MIN','10'))
    pres_max = int(os.environ.get('PRES_LEV_MAX','100'))

    # Read output directory
    output_dir = os.environ['OUTPUT_DIR']

    # Read in plotting inits and period
    input_plot_inits = os.environ['PLOT_START_DATES']
    plot_period = int(os.environ['PLOT_PERIODS'])

    # Read in plotting outfile names and titles
    plot_circuits_outname = os.environ.get('PLOT_PHASE_CIRCUTS_OUTPUT_NAME','QBO_circuits.png')
    plot_phasespace_title = os.environ.get('PLOT_PHASE_SPACE_TITLE','QBO Phase Space')
    plot_phasespace_outname = os.environ.get('PLOT_PHASE_SPACE_OUTPUT_NAME','QBO_PhaseSpace.png')
    plot_timeseries_30_title = os.environ.get('PLOT_TIME_SERIES_TITLE_30','U 30mb')
    plot_timeseries_30_outname = os.environ.get('PLOT_TIME_SERIES_OUTPUT_NAME_30','QBO_U_time_series_30.png')
    plot_timeseries_50_title = os.environ.get('PLOT_TIME_SERIES_TITLE_50','U 50mb')
    plot_timeseries_50_outname = os.environ.get('PLOT_TIME_SERIES_OUTPUT_NAME_50','QBO_U_time_series_50.png')


    """
    Make output directories if they don't exist
    """
    mpr_output_dir = os.path.join(output_dir,'mpr')
    if not os.path.exists(mpr_output_dir):
        os.makedirs(mpr_output_dir)
    plot_output_dir = os.path.join(output_dir,'plots')
    if not os.path.exists(plot_output_dir):
        os.makedirs(plot_output_dir)

    """
    Read in the data for EOFs
    Compute zonal and meridional means if not already computed
    """
    compute_zmm = os.environ.get('COMPUTE_EOF_ZONAL_MERIDIONAL_MEAN','True')
    if compute_zmm.lower() == 'true':
        # Get input files
        obs_eof_filetxt = os.environ.get('METPLUS_FILELIST_OBS_EOF_INPUT','')
        with open(obs_eof_filetxt) as oef:
            obs_input_files_eofs = oef.read().splitlines()
        if (obs_input_files_eofs[0] == 'file_list'):
            obs_input_files_eofs = obs_input_files_eofs[1:]
        # Get the data
        dsE = get_qbo_data(obs_input_files_eofs,obs_latvar,obs_latdim,obs_londim,obs_timevar,lat_min,lat_max,pres_min,pres_max)
    else:
        # Read in the name of the output data file
        eof_data_file_name = os.environ['EOF_DATA_FILE_NAME']
        # Load data
        dsE = xr.open_dataset(eof_data_file_name)
    # Rename time dimension if it's not called time
    if obs_timevar != 'time':
        dsE.rename({obs_timevar:'time'})
    

    """
    Save the Data to be loaded in the calculation of QBO
    """
    save_zmm = os.environ.get('SAVE_EOF_ZONAL_MERIDIONAL_MEAN','False')
    if save_zmm.lower() == 'true':
        savefile = os.environ['ZONAL_MERIDIONAL_MEAN_EOF_FILE_NAME']
        dsE.to_netcdf(savefile)


    """
    Read the other datasets
    """
    # Get Obs listing of files for plotting and stats
    obs_filetxt = os.environ.get('METPLUS_FILELIST_OBS_INPUT','')
    with open(obs_filetxt) as of:
        obs_input_files = of.read().splitlines()
    if (obs_input_files[0] == 'file_list'):
        obs_input_files = obs_input_files[1:]
    # Get obs
    dsO = get_qbo_data(obs_input_files,obs_latvar,obs_latdim,obs_londim,obs_timevar,lat_min,lat_max,pres_min,pres_max)
    if obs_timevar != 'time':
        dsO.rename({obs_timevar:'time'})

    # Get model listing of files for plotting and stats
    fcst_filetxt = os.environ.get('METPLUS_FILELIST_FCST_INPUT','')
    with open(fcst_filetxt) as ff:
        fcst_input_files = ff.read().splitlines()
    if (fcst_input_files[0] == 'file_list'):
        fcst_input_files = fcst_input_files[1:]
    # Forecast
    dsF = get_qbo_data(fcst_input_files,fcst_latvar,fcst_latdim,fcst_londim,fcst_timevar,lat_min,lat_max,pres_min,pres_max)
    if fcst_timevar != 'time':
        dsF.rename({fcst_timevar:'time'})


    """
    Compute Anomalies
    """
    # Take Daily averages
    dsE_daily = dsE.resample(time='1D').mean()
    rean_trop_u = dsE_daily[obs_uvar]

    # Take monthly averages
    trop_u_monthly = rean_trop_u.resample(time='1MS').mean()

    # Get monthly zonal wind anomalies
    trop_u_anom = trop_u_monthly.groupby('time.month') - trop_u_monthly.groupby('time.month').mean('time')

    # get rid of the month coordinate which gets added
    # (it can cause an error in the EOF analysis package)
    trop_u_anom = trop_u_anom.drop_vars('month')


    """
    Compute EOFs
    """
    # Compute EOFs
    solver = Eof(trop_u_anom)
    pcs = solver.pcs(npcs=2, pcscaling=1)
    eofs = solver.eofs(neofs=2)


    # Daily means from entire dataset
    mmdd = rean_trop_u.time.dt.strftime("%m-%d")
    mmdd.name = "mmdd"
    trop_u_daily_clim = rean_trop_u.groupby(mmdd).mean('time')

    # Daily means for plot time period
    dsO = dsO.drop_duplicates(dim='time')
    dsO_daily = dsO.resample(time='1D').mean(dim='time')
    dsO_daily = dsO_daily[obs_uvar]
    mmdd1 = dsO_daily.time.dt.strftime("%m-%d")
    mmdd1.name = "mmdd"

    # Daily anomalies for observations time period
    rean_u_daily_anom = dsO_daily.groupby(mmdd1) - trop_u_daily_clim
    rean_u_daily_anom = rean_u_daily_anom.drop_vars("mmdd")

    # Daily anomalies for forecast plot time period
    dsF = dsF.sortby('time')
    dsF_daily = dsF.resample(time='1D').mean(dim='time')
    max_leads = dsF.resample(time='1D').max(dim='time').lead_time
    #min_leads = dsF.resample(time='1D').min(dim='time').lead_time
    #mean_leads = dsF_daily.lead_time
    dsF_daily = dsF_daily[fcst_uvar]

    utrop_fcst_anoms = dsF_daily - trop_u_daily_clim.sel(mmdd=dsF_daily.time.dt.strftime("%m-%d"))
    utrop_fcst_anoms.time.attrs['axis'] = 'T'
    utrop_fcst_anoms = utrop_fcst_anoms.drop_vars('mmdd') # get rid of trailing dimension from the anomaly calculation

    # project daily reanalysis zonal winds
    rean_qbo_pcs = solver.projectField(rean_u_daily_anom, eofscaling=1, neofs=2)

    # project daily rfcst zonal winds
    rfcst_qbo_pcs = solver.projectField(utrop_fcst_anoms, eofscaling=1, neofs=2)


    """
    EOF Phase Diagram Plots
    """
    # Create Circuits plot
    plot_inits = pd.DatetimeIndex([input_plot_inits])
    plot_qbo_phase_circuits(plot_inits,plot_period,rean_qbo_pcs,rfcst_qbo_pcs,
                            os.path.join(plot_output_dir,plot_circuits_outname))

    # Create Phase Space plot
    plot_qbo_phase_space(rean_qbo_pcs,eofs,plot_phasespace_title,
                         os.path.join(plot_output_dir,plot_phasespace_outname))


    """
    Time Series of U at 30 and 50mb Plot
    """
    dsO_3050 = dsO_daily.sel(pres=[30,50])
    dsF_3050 = dsF_daily.sel(pres=[30,50])
    plot_u_timeseries(dsO_3050.sel(pres=30)['time'].values,dsO_3050.sel(pres=30).values,
                      dsF_3050.sel(pres=30)['time'].values,dsF_3050.sel(pres=30).values,
                      plot_timeseries_30_title,os.path.join(plot_output_dir,plot_timeseries_30_outname))
    plot_u_timeseries(dsO_3050.sel(pres=50)['time'].values,dsO_3050.sel(pres=50).values,
                      dsF_3050.sel(pres=50)['time'].values,dsF_3050.sel(pres=50).values,
                      plot_timeseries_50_title,os.path.join(plot_output_dir,plot_timeseries_50_outname))


    """
    Write out matched pair files
    """
    # 30mb and 50mb wind
    dlength = 2
    modname = os.environ.get('MODEL_NAME','GFS')
    maskname = 'FULL'
    lead_hr = np.floor(max_leads)
    lead_min = np.round(np.remainder(max_leads,1) * 60)
    lead_sec = np.round(np.remainder(lead_min,1) * 60)
    datetimeindex = dsO_3050.indexes[obs_timevar]
    for i in range(len(datetimeindex)):
        valid_str = datetimeindex[i].strftime('%Y%m%d_%H%M%S')
        dsO_cur = dsO_3050.sel(time=datetimeindex[i])
        dsF_cur = dsF_3050.sel(time=datetimeindex[i])
        qbo_phase = np.where(dsO_cur < 0, 'East','West')
        obs_lvls = ['P'+str(int(op)) for op in dsO_cur.pres]
        obs_lvls2 = [str(int(op)) for op in dsO_cur.pres]
        fcst_lvls = ['P'+str(int(fp)) for fp in dsF_cur.pres]
        leadstr = str(int(lead_hr[i])).zfill(2)+str(int(lead_min[i])).zfill(2)+str(int(lead_sec[i])).zfill(2)
        write_mpr_file(dsF_cur.values,dsO_cur.values,[0.0]*dlength,[0.0]*dlength,
            [leadstr]*dlength,[valid_str]*dlength,['000000']*dlength,[valid_str]*dlength,modname,qbo_phase,
            ['QBO_U']*dlength,['m/s']*dlength,fcst_lvls,['QBO_U']*dlength,['m/s']*dlength,obs_lvls,
            maskname,obs_lvls2,mpr_output_dir,'qbo_u_'+modname)



if __name__ == '__main__':
    main()
