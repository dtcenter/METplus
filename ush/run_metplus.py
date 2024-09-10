#!/usr/bin/env python3

"""
Program Name: run_metplus.py
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

from os.path import abspath, join, dirname, realpath, basename
from os import pardir
import sys
import traceback

################################################################################
# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, abspath(join(dirname(realpath(__file__)), pardir)))

import produtil.setup

from metplus.util import pre_run_setup, run_metplus, post_run_cleanup
from metplus import __version__ as metplus_version

'''!@namespace run_metplus
Main script the processes all the tasks in the PROCESS_LIST
'''


def main():
    """!Main program.
    METplus script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    config_inputs = get_config_inputs_from_command_line()
    config = pre_run_setup(config_inputs)
    if not config:
        return False

    # warn if calling master_metplus.py
    if basename(__file__) == 'master_metplus.py':
        msg = ("master_metplus.py has been renamed to run_metplus.py. "
               "This script name will be removed in a future version.")
        config.logger.warning(msg)

    total_errors = run_metplus(config)

    return post_run_cleanup(config, 'METplus', total_errors)


def usage():
    """!How to call this script."""
    print(f"Running METplus v{metplus_version}\n"
          f"Usage: {basename(__file__)} arg1 arg2 arg3\n"
          "    -h|--help               Display this usage statement\n\n"
          "Arguments:\n"
          "/path/to/parmfile.conf -- Specify custom configuration file to use\n"
          "section.option=value -- override conf options on the command line")
    sys.exit(2)


def get_config_inputs_from_command_line():
    """! Read command line arguments. Pull out configuration
         files and configuration variable overrides. Display
         usage statement if invalid configuration or if help
         statement is requested, i.e. -h. Report error if
         invalid flag was provided, i.e. -a.
         @returns list of config inputs
    """
    # if not arguments were provided, print usage and exit
    if len(sys.argv) < 2:
        usage()

    # print usage statement and exit if help arg is found
    help_args = ('-h', '--help', '-help')
    if any(arg in sys.argv for arg in help_args):
        usage()

    # pull out command line arguments
    config_inputs = []
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            # ignore -c and --config since they are now optional
            if arg == '-c' or arg == '--config' or arg == '-config':
                continue

            # error/exit if an argument that is not supported was used
            print('ERROR: Invalid argument: %s.' % arg)
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
        produtil.setup.setup(send_dbn=False, jobname='run-METplus')
        if not main():
            sys.exit(1)
    except Exception as exc:
        print(traceback.format_exc())
        print('ERROR: run_metplus  failed: %s' % exc)
        sys.exit(2)
