#!/usr/bin/env python3

"""
Create QBO 

"""
import os
import sys
import datetime
#import cmcrameri
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib as mpl
import matplotlib.patheffects as PathEffects
from eofs.xarray import Eof
from matplotlib import pyplot as plt

import metcalcpy.pre_processing.directional_means as directional_means
import METreadnc.util.read_netcdf as read_netcdf
from metplotpy.contributed.stratosphere_diagnostics.stratosphere_plots import plot_qbo_phase_circuits,plot_qbo_phase_space
from metcalcpy.util.write_mpr import write_mpr_file


def process_single_file(infile,latvar,lonvar,lat_min,lat_max,pres_min,pres_max):

    file_reader = read_netcdf.ReadNetCDF()
    ds = file_reader.read_into_xarray(infile)[0]
    ds = ds.assign_coords(lat=('lat',ds.latitude.values))
    ds = ds.assign_coords(lon=('lon',ds.longitude.values))
    #****Need to fix these lines somehow to account for different lat/lon variable names

    # Compute zonal mean
    Uzm = directional_means.zonal_mean(ds,dimvar=lonvar)

    # Limit the data to 100 - 10 hPa
    Uzm = Uzm.sel(pres=slice(pres_min,pres_max))

    #Compute Meridional Mean
    U_1010 = directional_means.meridional_mean(Uzm, lat_min, lat_max, dimvar=latvar)

    return U_1010


def get_qbo_data(input_files,latvar,lonvar,timevar,lat_min,lat_max,pres_min,pres_max):

    # Read the first file
    ds = process_single_file(input_files[0],latvar,lonvar,lat_min,lat_max,pres_min,pres_max)
    # Read the rest of the files and concatenate
    for f in input_files[1:]:
        # Read in the data file
        ds2 = process_single_file(f,latvar,lonvar,lat_min,lat_max,pres_min,pres_max)
        # Save to array
        ds = xr.concat([ds,ds2],dim=timevar)

    return ds


def main():

    """
    Get the input variables
    """
    # Read the variable names for lat, lon, and time
    obs_latvar = os.environ.get('OBS_LAT_VAR','latitude')
    obs_lonvar = os.environ.get('OBS_LON_VAR','longitude')
    obs_timevar = os.environ.get('OBS_TIME_VAR','time')
    obs_uvar = os.environ.get('OBS_U_VAR','u')

    fcst_latvar = os.environ.get('FCST_LAT_VAR','latitude')
    fcst_lonvar = os.environ.get('FCST_LON_VAR','longitude')
    fcst_timevar = os.environ.get('FCST_TIME_VAR','time')
    fcst_uvar = os.environ.get('FCST_U_VAR','u')

    # Read the lat bounds, default -10 to 10
    lat_min = int(os.environ.get('LAT_MIN','-10'))
    lat_max = int(os.environ.get('LAT_MAX','10'))

    # Read the Pressure level bounds, default is 100 to 10
    pres_min = int(os.environ.get('PRES_LEV_MIN','10'))
    pres_max = int(os.environ.get('PRES_LEV_MAX','100'))

    # Read in plotting inits and period
    input_plot_inits = os.environ.get('PLOT_START_DATES','')
    plot_period = int(os.environ['PLOT_PERIODS'])

    # Read in plotting outfile names and titles
    plot_circuits_outname = os.environ.get('PLOT_PHASE_CIRCUTS_OUTPUT_NAME','QBO_circuits.png')
    plot_phasespace_title = os.environ.get('PLOT_PHASE_SPACE_TITLE','QBO Phase Space')
    plot_phasespace_outname = os.environ.get('PLOT_PHASE_SPACE_OUTPUT_NAME','QBO_PhaseSpace.png')


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
        dsE = get_qbo_data(obs_input_files_eofs,obs_latvar,obs_lonvar,obs_timevar,lat_min,lat_max,pres_min,pres_max)
    else:
        # Read in the name of the output data file
        eof_data_file_name = os.environ['EOF_DATA_FILE_NAME']
        # Load data
        dsE = xr.open_dataset(eof_data_file_name)
    # Rename time dimension if it's not called time
    if obs_timevar != 'time':
        dsE.rename({obs_timevar:'time'})
    

    """
    Save the Data to be loaded in the calculation of QBO  ****FIX ME
    """
    # Save xarray for now for later use
    #dsE.to_netcdf('/glade/derecho/scratch/kalb/Stratosphere_QBO/erai_zonal_mean_u.nc')


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
    dsO = get_qbo_data(obs_input_files,obs_latvar,obs_lonvar,obs_timevar,lat_min,lat_max,pres_min,pres_max)
    if obs_timevar != 'time':
        dsO.rename({obs_timevar:'time'})

    # Get model listing of files for plotting and stats
    fcst_filetxt = os.environ.get('METPLUS_FILELIST_FCST_INPUT','')
    with open(fcst_filetxt) as ff:
        fcst_input_files = ff.read().splitlines()
    if (fcst_input_files[0] == 'file_list'):
        fcst_input_files = fcst_input_files[1:]
    # Forecast
    dsF = get_qbo_data(fcst_input_files,fcst_latvar,fcst_lonvar,fcst_timevar,lat_min,lat_max,pres_min,pres_max)
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
    #solver,pcs,eofs = compute_eofs(trop_u_anom,2,1)
    solver = Eof(trop_u_anom)
    pcs = solver.pcs(npcs=2, pcscaling=1)
    eofs = solver.eofs(neofs=2)


    # Daily means from entire dataset
    mmdd = rean_trop_u.time.dt.strftime("%m-%d")
    mmdd.name = "mmdd"
    trop_u_daily_clim = rean_trop_u.groupby(mmdd).mean('time')

    # Daily means for plot time period
    dsO_daily = dsO.resample(time='1D').mean(dim='time')
    dsO_daily = dsO_daily[obs_uvar]
    mmdd1 = dsO_daily.time.dt.strftime("%m-%d")
    mmdd1.name = "mmdd"

    # Daily anomalies for observations time period
    rean_u_daily_anom = dsO_daily.groupby(mmdd1) - trop_u_daily_clim
    rean_u_daily_anom = rean_u_daily_anom.drop_vars("mmdd")


    # Daily anomalies for forecast plot time period
    dsF_daily = dsF.resample(time='1D').mean(dim='time')
    rfcst_daily = dsF_daily[fcst_uvar]

    utrop_fcst_anoms = rfcst_daily - trop_u_daily_clim.sel(mmdd=rfcst_daily.time.dt.strftime("%m-%d"))
    utrop_fcst_anoms.time.attrs['axis'] = 'T'
    utrop_fcst_anoms = utrop_fcst_anoms.drop_vars('mmdd') # get rid of trailing dimension from the anomaly calculation

    # project daily reanalysis zonal winds
    rean_qbo_pcs = solver.projectField(rean_u_daily_anom, eofscaling=1, neofs=2)

    # project daily rfcst zonal winds
    rfcst_qbo_pcs = solver.projectField(utrop_fcst_anoms, eofscaling=1, neofs=2)

    # Write out matched pair files for 30mb and 50mb wind



    # Create Circuits plot
    # If plot start dates not provided, use the minimum date and create one plot
    # if not plot_inits:
    #    plot_inits = 
    plot_inits = pd.DatetimeIndex([input_plot_inits])
    plot_qbo_phase_circuits(plot_inits,plot_period,rean_qbo_pcs,rfcst_qbo_pcs,plot_circuits_outname)

    # Create Phase Space plot
    plot_qbo_phase_space(rean_qbo_pcs,eofs,plot_phasespace_title,plot_phasespace_outname)



if __name__ == '__main__':
    main()
