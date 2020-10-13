#!/usr/bin/env python3

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

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir)))

import produtil.setup

from metplus.util import metplus_check
from metplus.util import pre_run_setup, run_metplus, post_run_cleanup
from metplus.util import get_process_list
from metplus import __version__ as metplus_version

'''!@namespace master_metplus
Main script the processes all the tasks in the PROCESS_LIST
'''

def main():
    """!Main program.
    Master METplus script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    config_inputs = get_config_inputs_from_command_line()
    config = pre_run_setup(config_inputs)

    # Use config object to get the list of processes to call
    process_list = get_process_list(config)

    total_errors = run_metplus(config, process_list)

    post_run_cleanup(config, 'METplus', total_errors)

def usage():
    """! How to call this script.
    """

    filename = os.path.basename(__file__)

    print ('''
Usage: %s arg1 arg2 arg3
    -h|--help               Display this usage statement

Arguments:
/path/to/parmfile.conf -- Specify custom configuration file to use
section.option=value -- override conf options on the command line

'''%(filename))
    sys.exit(2)

def get_config_inputs_from_command_line():
    """! Read command line arguments. Pull out configuration
         files and configuration variable overrides. Display
         usage statement if invalid configuration or if help
         statement is requested, i.e. -h. Report error if
         invalid flag was provided, i.e. -a.
         @returns list of config inputs
    """

    # output version that is run to screen
    print('Running METplus %s' % metplus_version)

    # if not arguments were provided, print usage and exit
    if len(sys.argv) < 2:
        usage()

    # print usage statement and exit if help arg is found
    help_args = ('-h', '--help', '-help')
    for help_arg in help_args:
        if help_arg in sys.argv:
            usage()
            sys.exit(0)

    # pull out command line arguments
    config_inputs = []
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            # ignore -c and --config since they are now optional
            if arg == '-c' or arg == '--config' or arg == '-config':
                continue

            # error/exit if an argument that is not supported was used
            logger.critical('Invalid argument: %s.' % arg)
            usage()

        # split up comma separated lists into individual items
        # and add each to list of arguments
        # NOTE: to support lists in a config variable override,
        # this logic will have to be enhanced
        # i.e. config.PROCESS_LIST=PCPCombine,GridStat
        config_inputs.extend(arg.split(','))

    # if no valid config_inputs were found, print usage and exit
    if not config_inputs:
        usage()

    return config_inputs

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
