#!/usr/bin/env python3
"""
Driver Script to Compute RMM index from input U850, U200 and OLR data. Data is averaged from 20S-20N
"""

import numpy as np
import xarray as xr
import datetime
import glob
import os
import sys

from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
#from metcalcpy.util import read_file
import metcalcpy.contributed.rmm_omi.compute_mjo_indices as cmi
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi
from RMM_OMI_util import find_input_files, find_times, compute_plot_times


def run_rmm_steps(inlabel, inconfig, spd, olr_eoffile, u850_eoffile, u200_eoffile, oplot_dir):

    # Get dates to read
    fileconfig = config_metplus.replace_config_from_section(inconfig,'compute_rmm')
    use_init =  is_loop_by_init(inconfig)
    alldata_time = find_times(fileconfig, use_init)

    # Get input File names and Directories
    olr_template = os.path.join(fileconfig.getraw('config',inlabel+'_OLR_INPUT_DIR'),
        fileconfig.getraw('config',inlabel+'_OLR_INPUT_TEMPLATE'))
    u850_template = os.path.join(fileconfig.getraw('config',inlabel+'_U850_INPUT_DIR'),
        fileconfig.getraw('config',inlabel+'_U850_INPUT_TEMPLATE'))
    u200_template = os.path.join(fileconfig.getraw('config',inlabel+'_U200_INPUT_DIR'),
        fileconfig.getraw('config',inlabel+'_U200_INPUT_TEMPLATE'))

    # Find Files
    olr_input_files = find_input_files(alldata_time, olr_template)
    u850_input_files = find_input_files(alldata_time, u850_template)
    u200_input_files = find_input_files(alldata_time, u200_template)

    # Create a time variable
    time = np.array([t_obj['valid'] for t_obj in alldata_time],dtype='datetime64')
    ntim = len(time)

    # read OLR, U850, U500 data from file
    #### This will need to be converted to the dbload versions
    #### I've cut the domain using regrid_data_plane, so that can be omitted once switched to dbload
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
    #### The code called here goes into METcalcpy
    #### It is currently from the compute_mjo_indices.py
    PC1, PC2 = cmi.rmm(olr[0:ntim,:], u850[0:ntim,:], u200[0:ntim,:], time, spd, olr_eoffile, u850_eoffile, u200_eoffile)

    print(PC1.min(), PC1.max())

    # Setup the PC phase diagram
    ####  This grabs the time window for the plot from the configuration file
    plot_time, months, days, ntim_plot = compute_plot_times(inconfig,use_init,'compute_rmm','TIMESERIES_PLOT')
    PC1_plot = PC1.sel(time=slice(plot_time[0],plot_time[-1]))
    PC2_plot = PC2.sel(time=slice(plot_time[0],plot_time[-1]))
    PC1_plot = PC1_plot[0:ntim_plot]
    PC2_plot = PC2_plot[0:ntim_plot]
    phase_plot_name = oplot_dir+'/'+inconfig.getstr('compute_rmm',inlabel+'_PHASE_PLOT_OUTPUT_NAME','obs_RMM_comp_phase')
    phase_plot_format = inconfig.getstr('compute_rmm',inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')
    # plot the PC phase diagram
    ####  This will need to go into METplotpy
    ####  It is currently in plot_mjo_indices.py
    pmi.phase_diagram('RMM',PC1_plot,PC2_plot,plot_time,months,days,phase_plot_name,phase_plot_format)

    # Setup PC time series plot
    ####  This grabs the time window for the plot from the configuration file
    plot_time, months, days, ntim_plot = compute_plot_times(inconfig,use_init,'compute_rmm','TIMESERIES_PLOT')
    PC1 = PC1.sel(time=slice(plot_time[0],plot_time[-1]))
    PC2 = PC2.sel(time=slice(plot_time[0],plot_time[-1]))
    PC1_plot = PC1_plot[0:ntim_plot]
    PC2_plot = PC2_plot[0:ntim_plot]
    timeseries_plot_name = oplot_dir+'/'+inconfig.getstr('compute_rmm',inlabel+'_TIMESERIES_PLOT_OUTPUT_NAME','obs_RMM_time_series')
    timeseries_plot_format = inconfig.getstr('compute_rmm',inlabel+'_TIMESERIES_PLOT_OUTPUT_FORMAT','png')
    # plot PC time series
    ####  This will need to go into METplotpy
    ####  It is currently in plot_mjo_indices.py
    pmi.pc_time_series('RMM',PC1_plot,PC2_plot,plot_time,months,days,timeseries_plot_name,timeseries_plot_format)


def main():

    # Start configs
    config_list = sys.argv[1:]
    config = pre_run_setup(config_list)

    # Read in EOF files and EOF plot variables
    olr_eoffile = config.getraw('compute_rmm','OLR_EOF_FILENAME','')
    u850_eoffile = config.getraw('compute_rmm','U850_EOF_FILENAME','')
    u200_eoffile = config.getraw('compute_rmm','U200_EOF_FILENAME','')
    spd = config.getint('compute_rmm','OBS_PER_DAY',1)

    # Check for an output plot directory
    oplot_dir = config.getstr('compute_rmm','RMM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Read in the EOFs and plot
    ####!! NEED TO FIX THIS BECASUE THE READ NEEDS TO BE EDITED TO ACCEPT INPUT FILES
    #################################################################################
    EOF1, EOF2 = cmi.read_rmm_eofs(olr_eoffile, u850_eoffile, u200_eoffile)
    eof_plot_name =  oplot_dir+'/'+config.getstr('compute_rmm','EOF_PLOT_OUTPUT_NAME','RMM_EOFs')
    eof_plot_format = config.getstr('compute_rmm','EOF_PLOT_OUTPUT_FORMAT','png')
    pmi.plot_rmm_eofs(EOF1, EOF2, eof_plot_name, eof_plot_format)

    #  Determine if doing forecast or obs
    run_obs_rmm = config.getbool('compute_rmm','OBS_RUN', False)
    run_fcst_rmm = config.getbool('compute_rmm','FCST_RUN', False)

    if run_obs_rmm:
        run_rmm_steps('OBS', config, spd, olr_eoffile, u850_eoffile, u200_eoffile, oplot_dir)

    if run_fcst_rmm:
        run_rmm_steps('FCST', config, spd, olr_eoffile, u850_eoffile, u200_eoffile, oplot_dir)


if __name__ == "__main__":
    main()
