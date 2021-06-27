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
import atexit

import metcalcpy.contributed.rmm_omi.compute_mjo_indices as cmi
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi
#from metcalcpy.util import read_file


def read_omi_eofs(eof1_files, eof2_files):
    """
    Read the OMI EOFs from file and into a xarray DataArray.
    :param eofpath: filepath to the location of the eof files
    :return: EOF1 and EOF2 3D DataArrays
    """

    # observed EOFs from NOAA PSL are saved in individual text files for each doy
    # horizontal resolution of EOFs is 2.5 degree
    EOF1 = xr.DataArray(np.empty([366,17,144]),dims=['doy','lat','lon'],
    coords={'doy':np.arange(1,367,1), 'lat':np.arange(-20,22.5,2.5), 'lon':np.arange(0,360,2.5)})
    EOF2 = xr.DataArray(np.empty([366,17,144]),dims=['doy','lat','lon'],
    coords={'doy':np.arange(1,367,1), 'lat':np.arange(-20,22.5,2.5), 'lon':np.arange(0,360,2.5)})
    nlat = len(EOF1['lat'])
    nlon = len(EOF1['lon'])

    for doy in range(len(eof1_files)):
        doystr = str(doy).zfill(3)
        tmp1 = pd.read_csv(eof1_files[doy], header=None, delim_whitespace=True, names=['eof1'])
        tmp2 = pd.read_csv(eof2_files[doy], header=None, delim_whitespace=True, names=['eof2'])
        eof1 = xr.DataArray(np.reshape(tmp1.eof1.values,(nlat, nlon)),dims=['lat','lon'])
        eof2 = xr.DataArray(np.reshape(tmp2.eof2.values,(nlat, nlon)),dims=['lat','lon'])
        EOF1[doy,:,:] = eof1.values
        EOF2[doy,:,:] = eof2.values

    return EOF1, EOF2


def run_omi_steps(inlabel, olr_filetxt, spd, EOF1, EOF2, oplot_dir):

    # Read the listing of EOF files
    with open(olr_filetxt) as ol:
        olr_input_files = ol.read().splitlines()

    # read OLR data from file
    #### This will need to be converted to the dbload versions
    #### I've cut the domain using regrid_data_plane, so that can be omitted once switched to dbload
    datestrt = '1979-01-01'
    datelast = '2012-12-31'
    time = np.arange(datestrt,datelast, dtype='datetime64[D]')
    ntim = len(time)
    ds = xr.open_dataset('UserScript_fcstGFS_obsERA_OMI/olr.1x.7920.anom7901.nc')
    olr = ds['olr'].sel(lat=slice(-20,20),time=slice(time[0],time[-1]))
    lat = ds['lat'].sel(lat=slice(-20,20))
    lon = ds['lon']
    print(olr.min(), olr.max())

    # project OLR onto EOFs
    PC1, PC2 = cmi.omi(olr[0:ntim,:,:], time, spd, EOF1, EOF2)

    # Get times for the PC phase diagram
    plase_plot_time_format = os.environ['PHASE_PLOT_TIME_FMT']
    phase_plot_start_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_BEG'],plase_plot_time_format)
    phase_plot_end_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_END'],plase_plot_time_format)
    PC1_plot = PC1.sel(time=slice(phase_plot_start_time,phase_plot_end_time))
    PC2_plot = PC2.sel(time=slice(phase_plot_start_time,phase_plot_end_time))

    # Get the output name and format for the PC plase diagram
    phase_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_NAME',inlabel+'_OMI_comp_phase'))
    phase_plot_format = os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')

    # plot the PC phase diagram
    pmi.phase_diagram('OMI',PC1,PC2,np.array(PC1_plot['time'].dt.strftime("%Y-%m-%d").values),
        np.array(PC1_plot['time.month'].values),np.array(PC1_plot['time.day'].values),
        phase_plot_name,phase_plot_format)


def main():

    # Get Obs and Forecast OLR file listing
    obs_olr_filetxt = os.environ.get('OBS_OLR_OMI_INPUT_TEXTFILE','')
    fcst_olr_filetxt = os.environ.get('FCST_OLR_OMI_INPUT_TEXTFILE','')

    # Read in EOF filenames
    eof1_filetxt = os.environ['EOF1_INPUT_TEXTFILE']
    eof2_filetxt = os.environ['EOF2_INPUT_TEXTFILE']

    # Read the listing of EOF files
    with open(eof1_filetxt) as ef1:
        eof1_input_files = ef1.read().splitlines()
    with open(eof2_filetxt) as ef2:
        eof2_input_files = ef2.read().splitlines()

    # Read in the EOFs
    EOF1, EOF2 = read_omi_eofs(eof1_input_files, eof2_input_files)

    # Get Number of Obs per day
    spd = os.environ.get('OBS_PER_DAY',1)

    # Check for an output plot directory in the configs.  Create one if it does not exist
    oplot_dir = os.environ.get('OMI_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = os.environ['SCRIPT_OUTPUT_BASE']
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    #  Determine if doing forecast or obs
    run_obs_omi = os.environ.get('RUN_OBS',False)
    run_fcst_omi = os.environ.get('FCST_RUN_FCST', False)

    # Run the steps to compute OMM
    # Observations
    if run_obs_omi:
        run_omi_steps('OBS', obs_olr_filetxt, spd, EOF1, EOF2, oplot_dir)

    # Forecast
    if run_fcst_omi:
        run_omi_steps('FCST', fcst_olr_filetxt, spd, EOF1, EOF2, oplot_dir)

    # nothing selected
    if not run_obs_omi and not run_fcst_omi:
        warnings.warn('Forecast and Obs runs not selected, nothing will be calculated')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
