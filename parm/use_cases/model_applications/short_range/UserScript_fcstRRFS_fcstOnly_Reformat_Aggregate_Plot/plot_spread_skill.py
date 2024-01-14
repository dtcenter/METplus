#!/usr/bin/env python3


import os
import time
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
# from metplotpy.plots import line as Line
from metplotpy.plots.line import line

def main():

    # Read in the YAML configuration file.  Environment variables in
    # the configuration file are supported.
    try:
        input_config_file = os.getenv("PLOTTING_YAML_CONFIG_NAME", "spread_skill_ecnt.yaml")
        settings = readconfig.parse_config(input_config_file)
        logging.info(settings)
    except yaml.YAMLError as exc:
        logging.error(exc)

    try:
        plot = line.Line(settings)
        plot.save_to_file()
        # plot.show_in_browser()
        plot.write_html()
        plot.write_output_file()
        # plot.line_logger.info(f"Finished creating line plot: {datetime.now()}")
    except ValueError as val_er:
        print(val_er)

if __name__ == "__main__":
  main()