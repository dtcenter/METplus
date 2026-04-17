#!/usr/bin/env python3

import os
import sys
from time import perf_counter
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
from metplotpy.plots.line import line

def main(plot_type):

    # Read the input data, input files, and output files
    plotting_stat_list_str = os.environ[f'PLOTTING_{plot_type}_FCST_STAT_LIST'].split(',')
    plotting_stat_list = [ps.lstrip() for ps in plotting_stat_list_str]
    plotting_vars_str = os.environ[f'PLOTTING_{plot_type}_FCST_VAR_LIST'].split(',')
    plotting_vars = [pv.lstrip() for pv in plotting_vars_str]
    var_longnames_str = os.environ[f'PLOTTING_{plot_type}_FCST_VAR_NAME_LIST'].split(',')
    var_longnames = [vl.lstrip() for vl in var_longnames_str]
    var_units_str = os.environ[f'PLOTTING_{plot_type}_FCST_VAR_UNITS_LIST'].split(',')
    var_units = [vu.lstrip() for vu in var_units_str]
    plotting_masks_str = os.environ[f'PLOTTING_{plot_type}_VX_MASK_LIST'].split(',')
    plotting_masks = [pm.lstrip() for pm in plotting_masks_str]
    yaml_files_str = os.environ[f'PLOTTING_{plot_type}_YAML_CONFIG_FILE_LIST'].split(',')
    yaml_files = [yf.lstrip() for yf in yaml_files_str]
    yaml_file_dir = os.environ[f'PLOTTING_{plot_type}_YAML_CONFIG_DIR']
    plot_output_dir = os.environ[f'PLOTTING_{plot_type}_OUTPUT_DIR']

    # Make output plot directory if if doesn't exist
    if not os.path.exists(plot_output_dir):
        os.makedirs(plot_output_dir)

    # Check to make sure that the lists are the same size
    if not len(plotting_vars) == len(var_longnames) == len(var_units):
        raise RuntimeError(f'The length of PLOTTING_{plot_type}_FCST_VAR_LIST must be equal to the lengths of PLOTTING_{plot_type}_FCST_VAR_NAME_LIST and PLOTTING_{plot_type}_FCST_VAR_UNITS_LIST')

    # Loop through the stats
    for s in plotting_stat_list:
        os.environ['PLOTTING_STAT'] = s

        set_plotting_stat_long_env_var(s)

        # Loop through the variables
        for v,n,u in zip(plotting_vars,var_longnames,var_units):

            os.environ['FCST_VAR_VAL1'] = v
            os.environ[f'PLOTTING_{plot_type}_LONG_VAR'] = n
            os.environ[f'PLOTTING_{plot_type}_VAR_UNITS'] = u

            # Loop through masks
            for m in plotting_masks:

                os.environ[f'PLOTTING_{plot_type}_OUTPUT_FILENAME'] = os.path.join(plot_output_dir,v+'_'+m)
                os.environ[f'PLOTTING_{plot_type}_MASK'] = m

                # Loop through data
                for i in yaml_files:

                    # Build yaml config file name
                    os.environ[f'PLOTTING_{plot_type}_YAML_CONFIG_NAME'] = os.path.join(yaml_file_dir,i)

                    create_plot(plot_type)


def set_plotting_stat_long_env_var(s):
    if s == 'MAE':
        os.environ['PLOTTING_STAT_LONG'] = 'Mean Absolute Error'
    elif s == 'ME':
        os.environ['PLOTTING_STAT_LONG'] = 'Mean Error'
    elif s == 'RMSE':
        os.environ['PLOTTING_STAT_LONG'] = 'Root Mean Squared Error'
    elif s == 'CSI':
        os.environ['PLOTTING_STAT_LONG'] = 'Critical Success Index'
    elif s == 'FBIAS':
        os.environ['PLOTTING_STAT_LONG'] = 'Frequency Bias'
    else:
        os.environ['PLOTTING_STAT_LONG'] = s


def create_plot(plot_type):
    try:
        input_config_file = os.getenv(f"PLOTTING_{plot_type}_YAML_CONFIG_NAME", "custom_line.yaml")
        config = readconfig.parse_config(input_config_file)
        logging.info(config)
    except yaml.YAMLError as exc:
        logging.error(exc)
        return None

    try:
        start = perf_counter()
        plot = line.Line(config)
        plot.save_to_file()
        plot.write_output_file()
        end = perf_counter()
        execution_time = end - start
        plot.logger.info(f"Finished creating line plot, execution time: {execution_time} seconds")
    except ValueError as val_er:
        print(val_er)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"ERROR: {__file__} - Must provide at least 1 input file argument")
        sys.exit(1)
    plot_type_id = sys.argv[1].upper()
    main(plot_type_id)
