#!/usr/bin/env python3


import os
import time
import logging
import pandas as pd
import yaml
from metcalcpy.util import read_env_vars_in_config as readconfig
from metcalcpy.agg_stat import AggStat

logger = logging.getLogger(__name__)

def main():
    '''
       Read in the config file (with ENVIRONMENT variables defined in the
       UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot.conf).  Invoke METcalcpy agg_stat module to
       calculate the aggregation statistics, clean up the data so it is compatible for the METplotpy line plot
       and write a tab-separated ASCII file.

    '''

    start_agg_step = time.time()

    # Read in the YAML configuration file.  Environment variables in
    # the configuration file are supported.
    try:
        input_config_file = os.getenv("AGGREGATE_YAML_CONFIG_NAME", "aggregate_ecnt.yaml")
        settings = readconfig.parse_config(input_config_file)
        logger.info(settings)
    except yaml.YAMLError as exc:
        logger.error(exc)

    # Calculate the aggregation statistics using METcalcpy agg_stat
    agg_begin = time.time()
    try:
       os.mkdir(os.getenv("AGGREGATE_OUTPUT_BASE"))
    except OSError:
        # Directory already exists, ignore error.
        pass

    AGG_STAT = AggStat(settings)
    AGG_STAT.calculate_stats_and_ci()
    agg_finish = time.time()
    time_for_aggregation = agg_finish - agg_begin
    logger.info("Total time for calculating aggregation statistics (in seconds): {time_for_aggregation}")

    # Add a 'dummy' column (fcst_valid with the same values as fcst_lead)
    # to the output data.  The aggregation was based
    # on the fcst_lead BUT the line plot requires a *second* time-related
    # column (i.e. fcst_init_beg, fcst_valid, etc.) to identify unique
    # points.  In this case, the aggregated data already consists of
    # unique points. If any other time column was used, this
    # step would not be required.
    output_file = settings['agg_stat_output']
    df = pd.read_csv(output_file, sep='\t')
    df['fcst_valid'] = df['fcst_lead']
    df.to_csv(output_file, sep='\t')

    finish_agg = time.time()
    total_agg_step = finish_agg - start_agg_step
    logger.info("Total time for performing the aggregation step (in sec): {total_agg_step} ")


if __name__ == "__main__":
    main()