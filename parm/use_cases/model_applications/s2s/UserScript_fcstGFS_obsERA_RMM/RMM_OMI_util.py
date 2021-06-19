import os
import numpy as np
import xarray as xr
import pandas as pd
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub


def find_input_files(datetime_dictlist, intemplate):

    file_list = []
    for outtime in datetime_dictlist:
        filepath = do_string_sub(intemplate, **outtime)
        if os.path.exists(filepath):
            file_list.append(filepath)
        else:
            file_list.append('')

    if all('' == fn for fn in file_list):
        raise IOError('No input files found as given: '+template)

    return file_list


def find_times(inconfig, use_init):
    loop_time, end_time, time_interval = get_start_end_interval_times(inconfig)
    skip_times = get_skip_times(inconfig)

    datetime_list = []
    if use_init:
        timname = 'init'
    else:
        timname = 'valid'
    input_dict = {}
    input_dict['loop_by'] = timname
    while loop_time <= end_time:
        lead_seq = get_lead_sequence(inconfig)
        for ls in lead_seq:
            new_time = loop_time + ls
            input_dict[timname] = loop_time
            input_dict['lead'] = ls

            outtime = ti_calculate(input_dict)
            if skip_time(outtime, skip_times):
                continue
            datetime_list.append(outtime)

        loop_time += time_interval

    return datetime_list


def compute_plot_times(inconfig,use_init,config_sect,ptime_var):
    if use_init:
        inconfig.set(config_sect,'INIT_BEG',inconfig.getstr(config_sect,ptime_var+'_INIT_BEG'))
        inconfig.set(config_sect,'INIT_END',inconfig.getstr(config_sect,ptime_var+'_INIT_END'))
    else:
        inconfig.set(config_sect,'VALID_BEG',inconfig.getstr(config_sect,ptime_var+'_VALID_BEG'))
        inconfig.set(config_sect,'VALID_END',inconfig.getstr(config_sect,ptime_var+'_VALID_END'))

    pltconfig = config_metplus.replace_config_from_section(inconfig,config_sect)
    plot_alltimes = find_times(pltconfig, use_init)
    plot_time = np.array([t_obj2['valid'] for t_obj2 in plot_alltimes],dtype='datetime64')
    months = [t_obj2['valid'].month for t_obj2 in plot_alltimes]
    days = [t_obj2['valid'].day for t_obj2 in plot_alltimes]
    ntim_plot = len(plot_time)

    return plot_time, months, days, ntim_plot


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
