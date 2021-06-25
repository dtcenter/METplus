#!/usr/bin/env python3
"""
Driver Script to Compute RMM index from input U850, U200 and OLR data. Data is averaged from 20S-20N
"""

import numpy as np
import xarray as xr
import pandas as pd
import datetime
import glob
import os
import sys
import warnings

from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
#from metcalcpy.util import read_file
import metcalcpy.contributed.rmm_omi.compute_mjo_indices as cmi
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi


def read_rmm_eofs(olrfile, u850file, u200file):
    """
    Read the OMI EOFs from file and into a xarray DataArray.
    :param eofpath: filepath to the location of the eof files
    :return: EOF1 and EOF2 2D DataArrays
    """

    # observed EOFs from BOM Australia are saved in individual text files for each variable
    # horizontal resolution of EOFs is 2.5 degree and longitudes go from 0 - 375.5, column1 is eof1
    # column 2 is eof2 in each file

    EOF1 = xr.DataArray(np.empty([3,144]),dims=['var','lon'],
    coords={'var':['olr','u850','u200'], 'lon':np.arange(0,360,2.5)})
    EOF2 = xr.DataArray(np.empty([3,144]),dims=['var','lon'],
    coords={'var':['olr','u850','u200'], 'lon':np.arange(0,360,2.5)})
    nlon = len(EOF1['lon'])

    tmp = pd.read_csv(olrfile, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[0,:] = tmp.eof1.values
    EOF2[0,:] = tmp.eof2.values
    tmp = pd.read_csv(u850file, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[1,:] = tmp.eof1.values
    EOF2[1,:] = tmp.eof2.values
    tmp = pd.read_csv(u200file, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[2,:] = tmp.eof1.values
    EOF2[2,:] = tmp.eof2.values

    return EOF1, EOF2


def run_rmm_steps(inlabel, spd, EOF1, EOF2, oplot_dir):

    # Get OLR, U850, U200 file listings
    olr_filetxt = os.environ[inlabel+'_OLR_RMM_INPUT_TEXTFILE']
    u850_filetxt = os.environ[inlabel+'_U850_RMM_INPUT_TEXTFILE']
    u200_filetxt = os.environ[inlabel+'_U200_RMM_INPUT_TEXTFILE']

    # Read the listing of OLR, U850, U200 files
    with open(olr_filetxt) as ol:
        olr_input_files = ol.read().splitlines()
    with open(u850_filetxt) as u8:
        u850_input_files = u8.read().splitlines()
    with open(olr_filetxt) as u2:
        u200_input_files = u2.read().splitlines()   

    # read OLR, U850, U500 data from file
    #### This will need to be converted to the dbload versions
    #### I've cut the domain using regrid_data_plane, so that can be omitted once switched to dbload
    # set dates to read
    datestrt = '2000-01-01'
    datelast = '2002-12-31'
    time = np.arange(datestrt,datelast, dtype='datetime64[D]')
    ntim = len(time)
    ds = xr.open_dataset('UserScript_fcstGFS_obsERA_RMM/olr.1x.7920.anom7901.nc')
    olr = ds['olr'].sel(lat=slice(-15,15),time=slice(time[0],time[-1]))
    lon = ds['lon']
    olr = olr.mean('lat')
    print(olr.min(), olr.max())

    ds = xr.open_dataset('UserScript_fcstGFS_obsERA_RMM/uwnd.erai.an.2p5.850.daily.anom7901.nc')
    u850 = ds['uwnd'].sel(lat=slice(-15,15),time=slice(time[0],time[-1]))
    u850 = u850.mean('lat')
    print(u850.min(), u850.max())

    ds = xr.open_dataset('UserScript_fcstGFS_obsERA_RMM/uwnd.erai.an.2p5.200.daily.anom7901.nc')
    u200 = ds['uwnd'].sel(lat=slice(-15,15),time=slice(time[0],time[-1]))
    u200 = u200.mean('lat')
    print(u200.min(), u200.max())

    # project data onto EOFs
    PC1, PC2 = cmi.rmm(olr[0:ntim,:], u850[0:ntim,:], u200[0:ntim,:], time, spd, EOF1, EOF2)

    print(PC1.min(), PC1.max())

    # Setup the times for the PC phase diagram
    plase_plot_time_format = os.environ['PHASE_PLOT_TIME_FMT']
    phase_plot_start_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_BEG'],plase_plot_time_format)
    phase_plot_end_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_END'],plase_plot_time_format)
    PC1_plot = PC1.sel(time=slice(phase_plot_start_time,phase_plot_end_time))
    PC2_plot = PC2.sel(time=slice(phase_plot_start_time,phase_plot_end_time))

    # Get the output name and format for the PC plase diagram
    phase_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_NAME','obs_RMM_comp_phase'))
    phase_plot_format = os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')

    # Get times for plotting
    plot_time = PC1_plot['time'].dt.strftime("%Y-%m-%d").values
    months = PC1_plot['time.month'].values
    days = PC1_plot['time.day'].values

    # plot the PC phase diagram
    pmi.phase_diagram('RMM',PC1_plot,PC2_plot,plot_time,months,days,phase_plot_name,phase_plot_format)

    # Setup the times for the PC time series plot
    timeseries_plot_time_format = os.environ['PHASE_PLOT_TIME_FMT']
    timeseries_plot_start_time = datetime.datetime.strptime(os.environ['TIMESERIES_PLOT_TIME_BEG'],
        timeseries_plot_time_format)
    timeseries_plot_end_time = datetime.datetime.strptime(os.environ['TIMESERIES_PLOT_TIME_END'],timeseries_plot_time_format)
    PC1 = PC1.sel(time=slice(timeseries_plot_start_time,timeseries_plot_end_time))
    PC2 = PC2.sel(time=slice(timeseries_plot_start_time,timeseries_plot_end_time))
    #PC1_plot = PC1_plot[0:ntim_plot]
    #PC2_plot = PC2_plot[0:ntim_plot]

    # Get the output name and format for the Time Series Plot
    timeseries_plot_name=os.path.join(oplot_dir,os.environ.get(inlabel+'_TIMESERIES_PLOT_OUTPUT_NAME','obs_RMM_time_series'))
    timeseries_plot_format = os.environ.get(inlabel+'_TIMESERIES_PLOT_OUTPUT_FORMAT','png')

    # Get times for plotting
    plot_time = PC1_plot['time'].dt.strftime("%Y-%m-%d").values
    months = PC1_plot['time.month'].values
    days = PC1_plot['time.day'].values

    # plot PC time series
    pmi.pc_time_series('RMM',PC1_plot,PC2_plot,plot_time,months,days,timeseries_plot_name,timeseries_plot_format)


def main():

    # Start configs
    #config_list = sys.argv[1:]
    #config = pre_run_setup(config_list)

    # Get Number of Obs per day
    spd = os.environ.get('OBS_PER_DAY',1)

    # Check for an output plot directory
    oplot_dir = os.environ.get('RMM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Get the EOF Files
    olr_eoffile = os.path.join(os.environ['OLR_EOF_INPUT_DIR'],os.environ['OLR_EOF_FILENAME'])
    u850_eoffile = os.path.join(os.environ['U850_EOF_INPUT_DIR'],os.environ['U850_EOF_FILENAME'])
    u200_eoffile = os.path.join(os.environ['U200_EOF_INPUT_DIR'],os.environ['U200_EOF_FILENAME'])

    # Read in the EOFs and plot
    EOF1, EOF2 = read_rmm_eofs(olr_eoffile, u850_eoffile, u200_eoffile)

    # Get the EOF plot output name and format
    eof_plot_name =  os.path.join(oplot_dir,os.environ.get('EOF_PLOT_OUTPUT_NAME','RMM_EOFs'))
    eof_plot_format = os.environ.get('EOF_PLOT_OUTPUT_FORMAT','png')

    # Plot EOFs
    pmi.plot_rmm_eofs(EOF1, EOF2, eof_plot_name, eof_plot_format)

    #  Determine if doing forecast or obs
    run_obs_rmm = os.environ.get('RUN_OBS',False)
    run_fcst_rmm = os.environ.get('FCST_RUN_FCST', False)

    if run_obs_rmm:
        run_rmm_steps('OBS', spd, EOF1, EOF2, oplot_dir)

    if run_fcst_rmm:
        run_rmm_steps('FCST', spd, EOF1, EOF2, oplot_dir)

     # nothing selected
    if not run_obs_rmm and not run_fcst_rmm:
        warnings.warn('Forecast and Obs runs not selected, nothing will be calculated')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
