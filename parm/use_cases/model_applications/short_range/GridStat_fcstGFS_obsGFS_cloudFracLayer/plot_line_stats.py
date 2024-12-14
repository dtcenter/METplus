#!/usr/bin/env python3

import os
from time import perf_counter
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
from metplotpy.plots.line import line

def main():

    # Read the input files
    yaml_files_str = os.environ['PLOTTING_YAML_CONFIG_FILE_LIST'].split(',')
    yaml_files = [yf.lstrip() for yf in yaml_files_str]
    yaml_file_dir = os.environ['PLOTTING_YAML_CONFIG_DIR']
    plot_output_file_list_str = os.environ['PLOTTING_OUTPUT_FILENAME_LIST'].split(',')
    plot_output_files = [po.lstrip() for po in plot_output_file_list_str]
    plot_output_dir = os.environ['PLOTTING_OUTPUT_DIR']

    # Check to see that the two lists have the same number of elements
    # If they dont', error out
    if len(yaml_files) != len(plot_output_files):
        raise Exception('The number of files in PLOTTING_YAML_CONFIG_FILE_LIST must be equal to the number of files in PLOTTING_OUTPUT_FILENAME_LIST')


    # Loop through data
    for i,j in zip (yaml_files,plot_output_files):

        os.environ['PLOTTING_YAML_CONFIG_NAME'] = os.path.join(yaml_file_dir,i)
        os.environ['PLOTTING_OUTPUT_FILENAME'] = os.path.join(plot_output_dir,j)

        # Read in the YAML configuration file.  Environment variables in
        # the configuration file are supported.
        try:
            input_config_file = os.getenv("PLOTTING_YAML_CONFIG_NAME", "custom_line.yaml")
            settings = readconfig.parse_config(input_config_file)
            logging.info(settings)
        except yaml.YAMLError as exc:
            logging.error(exc)

        try:
            start = perf_counter()
            plot = line.Line(settings)
            plot.save_to_file()
            plot.write_html()
            plot.write_output_file()
            end = perf_counter()
            execution_time = end - start
            plot.logger.info(f"Finished creating line plot, execution time: {execution_time} seconds")
        except ValueError as val_er:
            print(val_er)

if __name__ == "__main__":
  main()
