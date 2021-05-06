#!/usr/bin/env /usr/local/anaconda3/bin/python3
"""
Driver Script to Compute RMM index from input U850, U200 and OLR data. Data is averaged from 20S-20N
"""

import numpy as np
import xarray as xr
import datetime
import pandas as pd
import glob
import sys

from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
from metcalcpy.util import read_file
import compute_mjo_indices as cmi
import plot_mjo_indices as pmi
from RMM_OMI_util import find_input_files, find_times


def run_rmm_steps(inlabel,inconfig):

    # set dates to read
    fileconfig = config_metplus.replace_config_from_section(inconfig,'compute_rmm')
    use_init =  is_loop_by_init(inconfig)
    alldata_time = find_times(fileconfig, use_init)
    olr_input_files = find_input_files(alldata_time, fileconfig, inlabel+'_OLR_INPUT_TEMPLATE')
    u850_input_files = find_input_files(alldata_time, fileconfig, inlabel+'_U850_INPUT_TEMPLATE')
    u200_input_files = find_input_files(alldata_time, fileconfig, inlabel+'_U200_INPUT_TEMPLATE')

    # Create a time variable
    time = [t_obj['valid'].strftime("%Y-%m-%d") for t_obj in alldata_time]
    ntim = len(time)

    # read data from file
    ds = xr.open_dataset('olr.1x.7920.anom7901.nc')
    olr = ds['olr'].sel(lat=slice(-15,15),time=slice(datestrt,datelast))
    lon = ds['lon']
    olr = olr.mean('lat')
    print(olr.min(), olr.max())

    ds = xr.open_dataset('uwnd.erai.an.2p5.850.daily.anom7901.nc')
    u850 = ds['uwnd'].sel(lat=slice(-15,15),time=slice(datestrt,datelast))
    u850 = u850.mean('lat')
    print(u850.min(), u850.max())

    ds = xr.open_dataset('uwnd.erai.an.2p5.200.daily.anom7901.nc')
    u200 = ds['uwnd'].sel(lat=slice(-15,15),time=slice(datestrt,datelast))
    u200 = u200.mean('lat')
    print(u200.min(), u200.max())

    ########################################
    # project data onto EOFs
    PC1, PC2 = cmi.rmm(olr[0:ntim,:], u850[0:ntim,:], u200[0:ntim,:], time, spd, './')

    print(PC1.min(), PC1.max())

    ########################################
    # plot phase diagram
    datestrt = '2002-01-01'
    datelast = '2002-12-31'
    exit()
    # NEED TO FIX THIS SO IT CREATES A NEW LIST OF TIMES USING FIND_TIMES
    

    time = np.arange(datestrt,datelast, dtype='datetime64[D]')
    ntim = len(time)
    PC1 = PC1.sel(time=slice(datestrt,datelast))
    PC2 = PC2.sel(time=slice(datestrt,datelast))
    PC1 = PC1[0:ntim]
    PC2 = PC2[0:ntim]

    months = []
    days = []
    for idx, val in enumerate(time):
        date = pd.to_datetime(val).timetuple()
        month = date.tm_mon
        day = date.tm_mday
        months.append(month)
        days.append(day)

    # plot the PC phase diagram
    pmi.phase_diagram('RMM',PC1,PC2,time,months,days,'RMM_comp_phase','png')

    # plot PC time series
    pmi.pc_time_series('RMM',PC1,PC2,time,months,days,'RMM_time_series','png')


def main():

    # Start configs
    config_list = sys.argv[1:]
    config = pre_run_setup(config_list)

    # Read in EOF files and EOF plot variables
    olr_eof = config.getstr('compute_rmm','OLR_EOF_FILE','')
    u850_eof = config.getstr('compute_rmm','U850_EOF_FILE','')
    u200_eof = config.getstr('compute_rmm','U200_EOF_FILE','')
    spd = config.getint('compute_rmm','OBS_PER_DAY',1)

    # Read in the EOFs and plot
    ####!! NEED TO FIX THIS BECASUE THE READ NEEDS TO BE EDITED TO ACCEPT INPUT FILES
    #################################################################################
    EOF1, EOF2 = cmi.read_rmm_eofs()
    pmi.plot_rmm_eofs(EOF1, EOF2, 'RMM_EOFs','png')

    #  Determine if doing forecast or obs
    run_obs_rmm = config.getbool('compute_rmm','OBS_RUN',False)
    run_fcst_rmm = config.getbool('compute_rmm','FCST_RUN',False)

    if run_obs_rmm:
        run_rmm_steps('OBS',config)

    if run_fcst_rmm:
        run_rmm_steps('FCST',config)


if __name__ == "__main__":
    main()
