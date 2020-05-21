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
import importlib
import logging
import shutil
from datetime import datetime

import produtil.setup

from metplus.util import metplus_check_python_version
from metplus.util import pre_run_setup, run_metplus, post_run_cleanup
from metplus.util import get_process_list, is_plotter_in_process_list

# check if env var METPLUS_DISABLE_PLOT_WRAPPERS is not set or set to empty string
disable_plotting = False
if os.environ.get('METPLUS_DISABLE_PLOT_WRAPPERS', False):
    disable_plotting = True

'''!@namespace master_metplus
Main script the processes all the tasks in the PROCESS_LIST
'''

def main():
    """!Main program.
    Master METplus script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    config = pre_run_setup(__file__, 'METplus')

    # Use config object to get the list of processes to call
    process_list = get_process_list(config)

    if disable_plotting and is_plotter_in_process_list(process_list):
        config.logger.error("Attempting to run a plotting wrapper while METPLUS_DISABLE_PLOT_WRAPPERS environment "
                            "variable is set. Unset the variable to run this use case")
        total_errors = 1
    else:
        total_errors = run_metplus(config, process_list)

    post_run_cleanup(config, 'METplus', total_errors)

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
