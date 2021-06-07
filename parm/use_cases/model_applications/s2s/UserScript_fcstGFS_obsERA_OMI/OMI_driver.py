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
import pandas as pd

from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
#from metcalcpy.util import read_file
import compute_mjo_indices as cmi
import plot_mjo_indices as pmi
from RMM_OMI_util import find_input_files, find_times, compute_plot_times


def run_omi_steps(inlabel, inconfig, spd, olr_eoffile, oplot_dir):

    # Get dates to read using METplus time variables
    fileconfig = config_metplus.replace_config_from_section(inconfig,'compute_omi')
    use_init =  is_loop_by_init(inconfig)
    alldata_time = find_times(fileconfig, use_init)

     # Get input File names and Directories
    olr_template = os.path.join(fileconfig.getraw('config',inlabel+'_OLR_INPUT_DIR'),
        fileconfig.getraw('config',inlabel+'_OLR_INPUT_TEMPLATE'))

    # Find Files
    olr_input_files = find_input_files(alldata_time, olr_template)

     # Create a time variable
    time = np.array([t_obj['valid'] for t_obj in alldata_time],dtype='datetime64')
    ntim = len(time)

    # read OLR data from file
    #### This will need to be converted to the dbload versions
    #### I've cut the domain using regrid_data_plane, so that can be omitted once switched to dbload
    ds = xr.open_dataset('UserScript_fcstGFS_obsERA_OMI/olr.1x.7920.anom7901.nc')
    olr = ds['olr'].sel(lat=slice(-20,20),time=slice(time[0],time[-1]))
    lat = ds['lat'].sel(lat=slice(-20,20))
    lon = ds['lon']
    print(olr.min(), olr.max())

    # project OLR onto EOFs
    #### The code called here goes into METcalcpy
    #### It is currently from the compute_mjo_indices.py
    PC1, PC2 = cmi.omi(olr[0:ntim,:,:], time, spd, 'UserScript_fcstGFS_obsERA_OMI/')

    print(PC1.min(), PC1.max())

    # Setup the PC phase diagram
    ####  This grabs the time window for the plot from the configuration file
    plot_time, months, days, ntim_plot = compute_plot_times(inconfig,use_init)
    PC1_plot = PC1.sel(time=slice(plot_time[0],plot_time[-1]))
    PC2_plot = PC2.sel(time=slice(plot_time[0],plot_time[-1]))
    PC1_plot = PC1_plot[0:ntim_plot]
    PC2_plot = PC2_plot[0:ntim_plot]
    phase_plot_name = oplot_dir+'/'+inconfig.getstr('compute_omi',inlabel+'_PHASE_PLOT_OUTPUT_NAME','obs_OMI_comp_phase')
    phase_plot_format = inconfig.getstr('compute_omi',inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')
    # plot the PC phase diagram
    ####  This will need to go into METplotpy
    ####  It is currently in plot_mjo_indices.py
    phase_diagram('OMI',PC1,PC2,plot_time,months,days,phase_plot_name,phase_plot_format)


def main():

    # Start configs
    config_list = sys.argv[1:]
    config = pre_run_setup(config_list)

    # Read in EOF filenames and number of obs per day
    olr_eoffile = config.getraw('compute_omi','OLR_EOF_FILENAME','')
    spd = config.getint('compute_rmm','OBS_PER_DAY',1)

    # Check for an output plot directory in the configs.  Create one if it does not exist
    oplot_dir = config.getstr('compute_omi','OMI_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = obase+'/'+'plots'
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    #  Determine if doing forecast or obs
    run_obs_omi = config.getbool('compute_omi','OBS_RUN', False)
    run_fcst_omi = config.getbool('compute_omi','FCST_RUN', False)

    # Run the steps to compute OMM
    # Observations
    if run_obs_omi:
        run_omi_steps('OBS', config, spd, olr_eoffile, oplot_dir)

    # Forecast
    if run_fcst_omi:
        run_omi_steps('FCST', config, spd, olr_eoffile, oplot_dir)


if __name__ == "__main__":
    main()
