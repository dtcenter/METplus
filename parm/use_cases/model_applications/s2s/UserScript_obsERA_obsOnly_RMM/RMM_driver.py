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

import metcalcpy.contributed.rmm_omi.compute_mjo_indices as cmi
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi
import METreadnc.util.read_netcdf as read_netcdf


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

    # Get OLR, U850, U200 file listings and variable names
    olr_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_OLR_INPUT']
    u850_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_U850_INPUT']
    u200_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_U200_INPUT']

    olr_var = os.environ[inlabel+'_OLR_VAR_NAME']
    u850_var = os.environ[inlabel+'_U850_VAR_NAME']
    u200_var = os.environ[inlabel+'_U200_VAR_NAME']

    # Read the listing of OLR, U850, U200 files
    with open(olr_filetxt) as ol:
        olr_input_files = ol.read().splitlines()
    if (olr_input_files[0] == 'file_list'):
            olr_input_files = olr_input_files[1:]
    with open(u850_filetxt) as u8:
        u850_input_files = u8.read().splitlines()
    if (u850_input_files[0] == 'file_list'):
            u850_input_files = u850_input_files[1:]
    with open(u200_filetxt) as u2:
        u200_input_files = u2.read().splitlines()
    if (u200_input_files[0] == 'file_list'):
            u200_input_files = u200_input_files[1:]

    # Check the input data to make sure it's not all missing
    olr_allmissing = all(elem == 'missing' for elem in olr_input_files)
    if olr_allmissing:
        raise IOError ('No input OLR files were found, check file paths')
    u850_allmissing = all(elem == 'missing' for elem in u850_input_files)
    if u850_allmissing:
        raise IOError('No input U850 files were found, check file paths')
    u200_allmissing = all(elem == 'missing' for elem in u200_input_files)
    if u200_allmissing:
        raise IOError('No input U200 files were found, check file paths')
    

    # Read OLR, U850, U200 data from file
    netcdf_reader_olr = read_netcdf.ReadNetCDF()
    ds_olr = netcdf_reader_olr.read_into_xarray(olr_input_files)

    netcdf_reader_u850 = read_netcdf.ReadNetCDF()
    ds_u850 = netcdf_reader_u850.read_into_xarray(u850_input_files)

    netcdf_reader_u200 = read_netcdf.ReadNetCDF()
    ds_u200 = netcdf_reader_u200.read_into_xarray(u200_input_files)


    time = []
    for din in range(len(ds_olr)):
        colr = ds_olr[din]
        ctime =  datetime.datetime.strptime(colr[olr_var].valid_time,'%Y%m%d_%H%M%S')
        time.append(ctime.strftime('%Y-%m-%d'))
        colr = colr.assign_coords(time=ctime)
        ds_olr[din] = colr.expand_dims("time")

        cu850 = ds_u850[din]
        cu850 = cu850.assign_coords(time=ctime)
        ds_u850[din] = cu850.expand_dims("time")

        cu200 = ds_u200[din]
        cu200 = cu200.assign_coords(time=ctime)
        ds_u200[din] = cu200.expand_dims("time")

    time = np.array(time,dtype='datetime64[D]')

    everything_olr = xr.concat(ds_olr,"time")
    olr = everything_olr[olr_var]
    olr = olr.mean('lat')
    print(olr.min(), olr.max())

    everything_u850 = xr.concat(ds_u850,"time")
    u850 = everything_u850[u850_var]
    u850 = u850.mean('lat')
    print(u850.min(), u850.max())

    everything_u200 = xr.concat(ds_u200,"time")
    u200 = everything_u200[u200_var]
    u200 = u200.mean('lat')
    print(u200.min(), u200.max())
    

    # Get normalization factors for use 
    rmm_norm = [float(os.environ['RMM_OLR_NORM']),float(os.environ['RMM_U850_NORM']),float(os.environ['RMM_U200_NORM'])]
    pc_norm = [float(os.environ['PC1_NORM']),float(os.environ['PC2_NORM'])]

    # project data onto EOFs
    PC1, PC2 = cmi.rmm(olr, u850, u200, time, spd, EOF1, EOF2, rmm_norm, pc_norm)
    print(PC1.min(), PC1.max())

    # Get times for the PC phase diagram
    plase_plot_time_format = os.environ['PHASE_PLOT_TIME_FMT']
    phase_plot_start_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_BEG'],plase_plot_time_format)
    phase_plot_end_time = datetime.datetime.strptime(os.environ['PHASE_PLOT_TIME_END'],plase_plot_time_format)
    PC1_pcplot = PC1.sel(time=slice(phase_plot_start_time,phase_plot_end_time))
    PC2_pcplot = PC2.sel(time=slice(phase_plot_start_time,phase_plot_end_time))
    pc_ntim_plot = len(PC1_pcplot)
    PC1_pcplot = PC1_pcplot[0:pc_ntim_plot]
    PC2_pcplot = PC2_pcplot[0:pc_ntim_plot]
    
    # Get the output name and format for the PC plase diagram
    phase_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_NAME',inlabel+'_RMM_comp_phase'))
    phase_plot_format = os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')

    # plot the PC phase diagram
    pmi.phase_diagram('RMM',PC1_pcplot,PC2_pcplot,np.array(PC1_pcplot['time'].dt.strftime("%Y-%m-%d").values),
        np.ndarray.tolist(PC1_pcplot['time.month'].values),np.ndarray.tolist(PC1_pcplot['time.day'].values),
        phase_plot_name, phase_plot_format)

    # Get times for the PC time series plot
    timeseries_plot_time_format = os.environ['TIMESERIES_PLOT_TIME_FMT']
    timeseries_plot_start_time = datetime.datetime.strptime(os.environ['TIMESERIES_PLOT_TIME_BEG'],plase_plot_time_format)
    timeseries_plot_end_time = datetime.datetime.strptime(os.environ['TIMESERIES_PLOT_TIME_END'],plase_plot_time_format)
    PC1_tsplot = PC1.sel(time=slice(timeseries_plot_start_time,timeseries_plot_end_time))
    PC2_tsplot = PC2.sel(time=slice(timeseries_plot_start_time,timeseries_plot_end_time))
    ts_ntim_plot = len(PC1_tsplot)
    PC1_tsplot = PC1_tsplot[0:ts_ntim_plot]
    PC2_tsplot = PC2_tsplot[0:ts_ntim_plot]

    # Get the ouitput name and format for the PC Timeseries plot
    timeseries_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_TIMESERIES_PLOT_OUTPUT_NAME',
        inlabel+'_RMM_timeseries'))
    timeseries_plot_format = os.environ.get(inlabel+'_TIMESERIES_PLOT_OUTPUT_FORMAT','png')

    # plot PC time series
    pmi.pc_time_series('RMM',PC1_tsplot,PC2_tsplot,np.array(PC1_tsplot['time'].values),
        np.ndarray.tolist(PC1_tsplot['time.month'].values),np.ndarray.tolist(PC1_tsplot['time.day'].values),
        timeseries_plot_name,timeseries_plot_format)


def main():

    # Get the EOF files and EOF plot variables
    olr_eoffile = os.environ['OLR_EOF_INPUT_TEXTFILE']
    u850_eoffile = os.environ['U850_EOF_INPUT_TEXTFILE']
    u200_eoffile = os.environ['U200_EOF_INPUT_TEXTFILE']

    # Get Number of Obs per day
    spd = os.environ.get('OBS_PER_DAY',1)

    # Check for an output plot directory
    oplot_dir = os.environ.get('RMM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = os.environ['SCRIPT_OUTPUT_BASE']
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Read in the EOFs and plot and get plot name and format
    EOF1, EOF2 = read_rmm_eofs(olr_eoffile, u850_eoffile, u200_eoffile)
    eof_plot_name = os.path.join(oplot_dir,os.environ.get('EOF_PLOT_OUTPUT_NAME','RMM_EOFs'))
    eof_plot_format = os.environ.get('EOF_PLOT_OUTPUT_FORMAT','png')
    pmi.plot_rmm_eofs(EOF1, EOF2, eof_plot_name, eof_plot_format)

    #  Determine if doing forecast or obs
    run_obs_rmm = os.environ.get('RUN_OBS', 'False').lower()
    run_fcst_rmm = os.environ.get('RUN_FCST', 'False').lower()

    if (run_obs_rmm == 'true'):
        run_rmm_steps('OBS', spd, EOF1, EOF2, oplot_dir)

    if (run_fcst_rmm == 'true'):
        run_rmm_steps('FCST', spd, EOF1, EOF2, oplot_dir)

    # nothing selected
    if (run_obs_rmm == 'false') and (run_fcst_rmm == 'false'):
        warnings.warn('Forecast and Obs runs not selected, nothing will be calculated')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
