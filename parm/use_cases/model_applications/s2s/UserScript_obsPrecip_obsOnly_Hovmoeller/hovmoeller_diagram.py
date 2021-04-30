#!/usr/bin/env python3

"""
Plot a Hovmoeller diagram using METplotpy functionality

"""
import os
import sys
import logging
import yaml
import xarray as xr  # http://xarray.pydata.org/
import metplotpy.plots.hovmoeller.hovmoeller as Hovmoeller
import metcalcpy.util.read_env_vars_in_config as readconfig


def main():
    """
    Use existing default Hovmoeller config file found int METplotpy to 
    create a default plot, using data in the METplus data store
    """

    """
    Read METplus config file paramaters
    """
    input_file_name = os.environ.get("INPUT_FILE_NAME","precip.erai.sfc.1p0.2x.2014-2016.nc")
    plot_config_file = os.getenv("YAML_CONFIG_NAME","hovmoeller.yaml")
    input_file = input_file_name

    """
    Read Hovmoeller YAML configuration file
    """
    try:
        config = readconfig.parse_config(plot_config_file)
        logging.info(config)
    except yaml.YAMLError as exc:
        logging.error(exc)


    """
    Setup logging
    """
    logfile = "Hovmoeller_diagram.log"
    logging_level = os.environ.get("LOG_LEVEL","logging.INFO")
    logging.basicConfig(stream=logfile, level=logging_level)

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

    plot_filename = config['plot_filename'][0]
    custom_param_dict = {"plot_filename": plot_filename}
    plot = Hovmoeller.Hovmoeller(custom_param_dict, time, lon, data)
    logging.info(plot_filename)
    plot.save_to_file()

if __name__ == '__main__':
    main()
