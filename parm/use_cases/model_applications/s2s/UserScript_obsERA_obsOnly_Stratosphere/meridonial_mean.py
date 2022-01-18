#!/usr/bin/env python3

"""
Create meridonial mean statistics

"""
import os
import sys
import logging
import yaml
import xarray as xr  # http://xarray.pydata.org/
import metcalcpy.util.read_env_vars_in_config as readconfig
import metcalcpy.pre_processing.directional_means as directional_means
import METreadnc.util.read_netcdf as read_netcdf


def main():
    """
    Use existing default meridonial mean config file found in METcalcpy to 
    grab the test file    
    """


    """
    Read Meridial Mean YAML configuration file
    user can use their own, if none specified at the command line,
    use the "default" example YAML config file, spectra_plot_coh2.py
    Using a custom YAML reader so we can use environment variables
    """

    try:
        input_config_file = os.getenv("YAML_CONFIG_NAME","meridonial_mean.yaml")
        config = readconfig.parse_config(input_config_file)
        logging.info(config)
    except yaml.YAMLError as exc:
        logging.error(exc)

    """
    Read METplus config file paramaters
    """
    #input_file_name = os.environ.get("INPUT_FILE_NAME","SSWC_v1.0_varFull_ERAi_d20130106_s20121107_e20130307_c20160701.nc")
    input_file = config["input_filename"]

    """
    Setup logging
    """
    logfile = "meridonial_mean.log"
    logging_level = os.environ.get("LOG_LEVEL","logging.INFO")
    logging.basicConfig(stream=logfile, level=logging_level)

    """
    Read dataset
    """
    try:
        logging.info('Opening ' + input_file[0])
        file_reader = read_netcdf.ReadNetCDF()

        #file_reader returns a list of xarrays even if there is only one file requested to be read
        #so we change it from a list to a single 
        ds = file_reader.read_into_xarray(input_file)[0]
    except IOError as exc:
        logging.error('Unable to open ' + input_file)
        logging.error(exc)
        sys.exit(1)
    logging.debug(ds)
    ds = ds[['uwndFull_TS','vwndFull_TS','tempFull_TS','geopFull_TS']]
    ds = ds.rename({'timeEv60':'time',
                    'lat':'latitude', # pyzome currently expects dimensions named latitude and longitude
                    'lon':'longitude',
                    'uwndFull_TS':'u',
                    'vwndFull_TS':'v',
                    'tempFull_TS':'T',
                    'geopFull_TS':'Z'})

    uzm = directional_means.zonal_mean(ds.u)
    Tzm = directional_means.zonal_mean(ds.T)
    T_6090 = directional_means.meridional_mean(Tzm, 60, 90)

    print(T_6090)

if __name__ == '__main__':
    main()
