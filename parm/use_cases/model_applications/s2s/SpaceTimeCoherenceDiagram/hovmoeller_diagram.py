#!/usr/bin/env python3

"""
Plot a Hovmoeller diagram using METplotpy functionality

"""
import os
import sys
import logging
import yaml
import xarray as xr  # http://xarray.pydata.org/
from netCDF4 import num2date
import METplotpy.metplotpy.plots.hovmoeller.hovmoeller as Hovmoeller


def main():
    """
    Use existing default Hovmoeller config file found int METplotpy to 
    create a default plot, using data in the METplus data store
    """

    #input_file_name = os.path.join(os.getenv('METplus_Data'),'TropicalDiagnostics','precip.erai.sfc.1p0.2x.2014-2016.nc')
    input_file_name = '/d2/METcalcpy_Data/TropicalDiagnostics/precip.erai.sfc.1p0.2x.2014-2016.nc'
    plot_config_file = os.path.join(os.getenv('METPLOTPY_BASE'), 'plots', 'config', 'hovmoeller_defaults.yaml')
    #data_dir = os.getenv('METplus_Data')
    data_dir = ('/d2/METplus_Data')
    input_file = os.path.join(data_dir,input_file_name)

    """
    Read Hovmoeller YAML configuration file
    """
    try:
        config = yaml.load(
            open(plot_config_file), Loader=yaml.FullLoader)
        logging.info(config)
    except yaml.YAMLError as exc:
        logging.error(exc)


    """
    Setup logging
    """
    logfile = "Hovmoeller_diagram.log"
    logging_level = logging.INFO
    logging.basicConfig(stream=logfile, level=logging_level)

    if os.path.isdir(data_dir):
        logging.info(data_dir)
    else:
        logging.error(data_dir + ' not found')
        sys.exit(1)

    # Plot and save difficulty index figures
    """
    Read dataset
    """
    try:
        logging.info('Opening ' + input_file)
        ds = xr.open_dataset(input_file)
    except IOError as exc:
        logging.error('Unable to open ' + input_file)
        logging.error(exc)
        sys.exit(1)
    logging.debug(ds)

    data = ds[config['var_name']]
    logging.debug(data)

    data = data.sel(time=slice(config['date_start'], config['date_end']))
    time = ds.time.sel(time=slice(config['date_start'], config['date_end']))
    lon = ds.lon

    data = data * config['unit_conversion']
    data.attrs['units'] = config['var_units']

    plot = Hovmoeller.Hovmoeller(None, time, lon, data)
    plot.save_to_file()

if __name__ == '__main__':
    main()
