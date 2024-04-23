#!/usr/bin/env python3

import os
from time import perf_counter
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
import metplotpy.plots.tcmpr_plots.tcmpr as tcmpr
# from metplotpy.plots.tcmpr_plots.tcmpr import Tcmpr
from metplotpy.plots.tcmpr_plots.tcmpr_config import TcmprConfig

def main():

    # Determine location of the default YAML config files and then
    # read defaults stored in YAML formatted file into the dictionary
    if 'METPLOTPY_BASE' in os.environ:
        location = os.path.join(os.environ['METPLOTPY_BASE'], 'metplotpy/plots/config')
    else:
        location = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

    with open(os.path.join(location, "tcmpr_defaults.yaml"), 'r') as stream:
        try:
            defaults = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    # Read in the YAML configuration file.  Environment variables in
    # the configuration file are supported.
    try:
        input_config_file = os.getenv("TIME_SERIES_PLOT_YAML_CONFIG_NAME", "plot_time_series.yaml")
        settings = readconfig.parse_config(input_config_file)
        logging.info(settings)
    except yaml.YAMLError as exc:
        logging.error(exc)


    # merge user defined parameters into defaults if they exist
    docs = {**defaults, **settings}


    config_obj = TcmprConfig(docs)

    try:
        start = perf_counter()

        tcmpr.create_plot(config_obj)
        end = perf_counter()
        execution_time = end - start
        logging.info(f"Finished creating time series plot, execution time: {execution_time} seconds")
    except ValueError as val_er:
        print(val_er)


if __name__ == "__main__":
   main()