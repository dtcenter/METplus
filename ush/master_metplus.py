#!/usr/bin/env python

"""
Program Name: master_metplus.py
Contact(s): George McCabe, Julie Prestopnik, Jim Frimel, Minna Win
Abstract: Runs METplus Wrappers scripts
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes:
Developer Note: Please do not use f-strings in this file so that the
  Python version check can notify the user of the incorrect version.
  Using Python 3.5 or earlier will output the SyntaxError from the
  f-string instead of the useful error message.
"""

import os
import sys

import metplus_check_python_version

import logging
import shutil
from datetime import datetime
import produtil.setup
import met_util as util
import config_metplus

# check if env var METPLUS_DISABLE_PLOT_WRAPPERS is not set or set to empty string
disable_plotting = False
if 'METPLUS_DISABLE_PLOT_WRAPPERS' in os.environ and os.environ['METPLUS_DISABLE_PLOT_WRAPPERS']:
    disable_plotting = True

# wrappers are referenced dynamically based on PROCESS_LIST values
# import of each wrapper is required
# pylint:disable=unused-import
from ensemble_stat_wrapper import EnsembleStatWrapper
from pcp_combine_wrapper import PCPCombineWrapper
from grid_stat_wrapper import GridStatWrapper
from regrid_data_plane_wrapper import RegridDataPlaneWrapper
from tc_pairs_wrapper import TCPairsWrapper
from extract_tiles_wrapper import ExtractTilesWrapper
from series_by_lead_wrapper import SeriesByLeadWrapper
from series_by_init_wrapper import SeriesByInitWrapper
from stat_analysis_wrapper import StatAnalysisWrapper
from mode_wrapper import MODEWrapper
from mtd_wrapper import MTDWrapper
from usage_wrapper import UsageWrapper
from command_builder import CommandBuilder
from pb2nc_wrapper import PB2NCWrapper
from point_stat_wrapper import PointStatWrapper
from tc_stat_wrapper import TCStatWrapper
from gempak_to_cf_wrapper import GempakToCFWrapper
from example_wrapper import ExampleWrapper
from custom_ingest_wrapper import CustomIngestWrapper
from ascii2nc_wrapper import ASCII2NCWrapper
from series_analysis_wrapper import SeriesAnalysisWrapper

# if using plotting wrappers, import them
if not disable_plotting:
    from tcmpr_plotter_wrapper import TCMPRPlotterWrapper
    from cyclone_plotter_wrapper import CyclonePlotterWrapper
    from make_plots_wrapper import MakePlotsWrapper

'''!@namespace master_metplus
Main script the processes all the tasks in the PROCESS_LIST
'''

def main():
    """!Main program.
    Master METplus script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    config = util.pre_run_setup(__file__, 'METplus')

    # Use config object to get the list of processes to call
    process_list = util.get_process_list(config)

    if disable_plotting and util.is_plotter_in_process_list(process_list):
        config.logger.error("Attempting to run a plotting wrapper while METPLUS_DISABLE_PLOT_WRAPPERS environment "
                            "variable is set. Unset the variable to run this use case")
        total_errors = 1
    else:
        total_errors = util.run_metplus(config, process_list)

    util.post_run_cleanup(config, 'METplus', total_errors)

if __name__ == "__main__":
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus')

        main()
    except Exception as exc:
        produtil.log.jlogger.critical(
            'master_metplus  failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)
