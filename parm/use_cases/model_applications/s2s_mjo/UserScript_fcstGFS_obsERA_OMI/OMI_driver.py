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
import warnings

import metcalcpy.contributed.rmm_omi.compute_mjo_indices as cmi
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi
import METreadnc.util.read_netcdf as read_netcdf


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
    if (olr_input_files[0] == 'file_list'):
        olr_input_files = olr_input_files[1:]

    # Read in the netCDF data from a list of files

    netcdf_reader = read_netcdf.ReadNetCDF()
    ds_orig = netcdf_reader.read_into_xarray(olr_input_files)

    # Add some needed attributes
    ds_list = []
    time = []
    for din in ds_orig:
        ctime =  datetime.datetime.strptime(din['olr'].valid_time,'%Y%m%d_%H%M%S')
        time.append(ctime.strftime('%Y-%m-%d'))
        din = din.assign_coords(time=ctime)
        din = din.expand_dims("time")
        ds_list.append(din)
    time = np.array(time,dtype='datetime64[D]')

    everything = xr.concat(ds_list,"time")
    olr = everything['olr']
    print(olr.min(), olr.max())

    # project OLR onto EOFs
    PC1, PC2 = cmi.omi(olr, time, spd, EOF1, EOF2)

    # Get times for the PC phase diagram
    plase_plot_time_format = os.environ['PHASE_PLOT_TIME_FMT']
    phase_plot_start_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_BEG'],plase_plot_time_format)
    phase_plot_end_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_END'],plase_plot_time_format)
    PC1_plot = PC1.sel(time=slice(phase_plot_start_time,phase_plot_end_time))
    PC2_plot = PC2.sel(time=slice(phase_plot_start_time,phase_plot_end_time))

    # Get the output name and format for the PC plase diagram
    phase_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_NAME',inlabel+'_OMI_comp_phase'))
    print(phase_plot_name)
    phase_plot_format = os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')

    # plot the PC phase diagram
    pmi.phase_diagram('OMI',PC1,PC2,np.array(PC1_plot['time'].dt.strftime("%Y-%m-%d").values),
        np.array(PC1_plot['time.month'].values),np.array(PC1_plot['time.day'].values),
        phase_plot_name,phase_plot_format)


def main():

    # Get Obs and Forecast OLR file listing
    obs_olr_filetxt = os.environ.get('METPLUS_FILELIST_OBS_OLR_INPUT','')
    fcst_olr_filetxt = os.environ.get('METPLUS_FILELIST_FCST_OLR_INPUT','')

    # Read in EOF filenames
    eof1_filetxt = os.environ['METPLUS_FILELIST_EOF1_INPUT']
    eof2_filetxt = os.environ['METPLUS_FILELIST_EOF2_INPUT']

    # Read the listing of EOF files
    with open(eof1_filetxt) as ef1:
        eof1_input_files = ef1.read().splitlines()
    if (eof1_input_files[0] == 'file_list'):
        eof1_input_files = eof1_input_files[1:]
    with open(eof2_filetxt) as ef2:
        eof2_input_files = ef2.read().splitlines()
    if (eof2_input_files[0] == 'file_list'):
        eof2_input_files = eof2_input_files[1:]

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
    run_obs_omi = os.environ.get('RUN_OBS','False').lower()
    run_fcst_omi = os.environ.get('RUN_FCST', 'False').lower()

    # Run the steps to compute OMM
    # Observations
    if run_obs_omi == 'true':
        run_omi_steps('OBS', obs_olr_filetxt, spd, EOF1, EOF2, oplot_dir)

    # Forecast
    if run_fcst_omi == 'true':
        run_omi_steps('FCST', fcst_olr_filetxt, spd, EOF1, EOF2, oplot_dir)

    # nothing selected
    if (run_obs_omi == 'false') and (run_fcst_omi == 'false'):
        warnings.warn('Forecast and Obs runs not selected, nothing will be calculated')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
