#!/usr/bin/env python3

import os
from time import perf_counter
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
from metplotpy.plots.performance_diagram import performance_diagram


def main():

    # Read the input files
    yaml_files_str = os.environ['PERF_DIAGRAM_YAML_CONFIG_FILE_LIST'].split(',')
    yaml_files = [yf.lstrip() for yf in yaml_files_str]
    yaml_file_dir = os.environ['PERF_DIAGRAM_YAML_CONFIG_DIR']
    plot_input_dir = os.environ['PERF_DIAGRAM_STAT_INPUT_DIR']
    plot_input_files_list_str = os.environ['PERF_DIAGRAM_STAT_INPUT_FILES'].split(',')
    plot_input_files_list = [pi.lstrip() for pi in plot_input_files_list_str]
    plot_output_dir = os.environ['PERF_DIAGRAM_OUTPUT_DIR']

    # Check to see that the two lists have the same number of elements
    # If they dont', error out
    if len(plot_input_files_list) != len(yaml_files):
        raise RuntimeError('The number of files in PERF_DIAGRAM_STAT_INPUT_FILES must be equal to the number of files in PERF_DIAGRAM_YAML_CONFIG_FILE_LIST')

    # Check to see that the output directory exists
    # If not, make a directory
    if not os.path.exists(plot_output_dir):
        os.makedirs(plot_output_dir)

    # Loop through data
    for f,i in zip(yaml_files,plot_input_files_list):
        os.environ['PERF_DIAGRAM_STAT_INPUT'] = os.path.join(plot_input_dir,i)
        os.environ['PERF_DIAGRAM_YAML_CONFIG_NAME'] = os.path.join(yaml_file_dir,f)

        # Read in the YAML configuration file.  Environment variables in
        # the configuration file are supported.
        try:
            input_config_file = os.getenv("PERF_DIAGRAM_YAML_CONFIG_NAME", "custom_performance_diagram.yaml")
            print(input_config_file)
            settings = readconfig.parse_config(input_config_file)
            logging.info(settings)
        except yaml.YAMLError as exc:
            logging.error(exc)

        start = perf_counter()
        plot = performance_diagram.PerformanceDiagram(settings)
        plot.save_to_file()
        plot.write_output_file()
        end = perf_counter()
        execution_time = end - start
        plot.logger.info(f"Finished creating performance diagram, execution time: {execution_time} seconds")


if __name__ == "__main__":
  main()
