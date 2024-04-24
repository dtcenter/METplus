#!/usr/bin/env python3

import os
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
import metplotpy.plots.skew_t.skew_t as skewt
import metplotpy.plots.util as util


def main():

    # Read in the YAML configuration file.  Environment variables in
    # the configuration file are supported.
    try:
        input_config_file = os.getenv("SKEW_T_PLOT_YAML_CONFIG_NAME", "plot_skew_t.yaml")
        config = readconfig.parse_config(input_config_file)

        # Set up the logging.
        log_dir = config['log_directory']
        log_file = config['log_filename']
        log_full_path = os.path.join(log_dir, log_file)

        try:
            os.makedirs(log_dir, exist_ok=True)
        except FileExistsError:
            # If directory already exists, this is OK.  Continue.
            pass

        log_level = config['log_level']
        format_str = "'%(asctime)s||%(levelname)s||%(funcName)s||%(message)s'"
        if log_level == 'DEBUG':
            logging.basicConfig(filename=log_full_path, level=logging.DEBUG,
                                format=format_str,
                                filemode='w')
        elif log_level == 'INFO':
            logging.basicConfig(filename=log_full_path, level=logging.INFO,
                                format=format_str,
                                filemode='w')
        elif log_level == 'WARNING':
            logging.basicConfig(filename=log_full_path, level=logging.WARNING,
                                format=format_str,
                                filemode='w')
        else:
            # log_level == 'ERROR'
            logging.basicConfig(filename=log_full_path, level=logging.ERROR,
                                format=format_str,
                                filemode='w')

        # Get the list of input files to visualize.
        input_dir = config['input_directory']
        file_ext = config['input_file_extension']
        files_of_interest = []

        logging.info("Reading in ASCII files")
        for root, dir, files in os.walk(input_dir):
           for item in files:
               if item.endswith(file_ext):
                   files_of_interest.append(os.path.join(root, item))

        # Create skew T diagrams for each input file.
        for file_of_interest in files_of_interest:
            logging.info(f"Creating skew-T plot for {file_of_interest} ")
            skewt.create_skew_t(file_of_interest, config)
    except yaml.YAMLError:
        logging.error('Error reading yaml config file')

if __name__ == "__main__":
    main()
