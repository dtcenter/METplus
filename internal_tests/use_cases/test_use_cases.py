#!/usr/bin/env python3

"""
Program Name: test_use_cases.py
Contact(s): George McCabe
Abstract: Runs METplus use cases
History Log:  Initial version
Usage: test_use_cases.py <host> --config <config1>,<config2>,...<configN>
<host> is the name of the host running the test or ID for running on machines
 that don't have constant $HOSTNAME , i.e. docker
<config1>,<config2>,...<configN> are the set of use cases to read
Multiple instances of --config can be passed in to run multiple use cases
Condition codes: 0 on success, 1 on failure
"""

import os
import sys
from os.path import dirname, realpath
import glob
import shutil
import subprocess
import filecmp
import logging
import time
import calendar
import argparse

from metplus.util import config_metplus

# keep track of use cases that failed to report at the end of execution
failed_runs = []

metplus_home = dirname(dirname(dirname(realpath(__file__))))
use_case_dir = os.path.join(metplus_home, "parm/use_cases")

def get_param_list(param):
    conf = metplus_home+"/internal_tests/use_cases/system.conf"
    params = param.split(",")
    params = params + [conf]
    return params

def run_test_use_case(param, test_metplus_base):
    global failed_runs

    params = get_param_list(param)
    output_base = os.environ.get('METPLUS_TEST_OUTPUT_BASE')
    if not output_base:
        print("ERROR: Must set METPLUS_TEST_OUTPUT_BASE to run")
        sys.exit(1)

    # get list of actual param files (ignoring config value overrides)
    # to the 2nd last file to use as the output directory
    # last param file is always the system.conf file
    param_files = [param for param in params if os.path.exists(param)]

    out_dir = os.path.join(output_base, os.path.basename(param_files[-2]))

    cmd = os.path.join(test_metplus_base, "ush", "run_metplus.py")
    use_case_name = None
    for parm in params:
        if parm.startswith('config.USE_CASE_NAME'):
            use_case_name = parm.split('=', 1)[1]
        cmd += " -c "+parm

    if use_case_name is None:
        use_case_name = os.path.basename(params[-2])
        if use_case_name.endswith('.conf'):
            use_case_name = use_case_name[0: -5]

    output_dir = os.path.join(output_base, use_case_name)
    cmd += f" -c dir.OUTPUT_BASE={output_dir}"
    print("CMD:"+cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.communicate()[0]
    returncode = process.returncode
    if returncode:
        failed_runs.append((cmd, out_dir))

def handle_output_directories(output_base, output_base_prev):
    """!if there are files in output base, prompt user to copy them to prev output base
        Args:
            @param output_base directory to write output from the current test run
            @param output_base_prev directory containing files written from previous run
            to compare to the current run
    """
    if os.path.exists(output_base) and os.listdir(output_base):

        # if prev exists, ask user to wipe it out
        if os.path.exists(output_base_prev):

            print("OUTPUT_BASE for previous run exists:" + output_base_prev)
            user_answer = input("Would you like to remove all files? (y/n)[n]")

            if user_answer and user_answer[0] == 'y':
                print("Removing " + output_base_prev + " and all files in it.")
                shutil.rmtree(output_base_prev)
            else:
                print("Directory must be empty to proceed with tests")
                sys.exit(1)

        print("Moving " + output_base + " to " + output_base_prev)
        os.rename(output_base, output_base_prev)

def main():
    global failed_runs

    if not os.environ.get('METPLUS_TEST_METPLUS_BASE'):
        test_metplus_base = metplus_home
    else:
        test_metplus_base = os.environ['METPLUS_TEST_METPLUS_BASE']

    print("Starting test script")
    print("Running " + test_metplus_base + " to test")

    output_base_prev = os.environ['METPLUS_TEST_PREV_OUTPUT_BASE']
    output_base = os.environ['METPLUS_TEST_OUTPUT_BASE']

    # read command line arguments to determine which use cases to run
    parser = argparse.ArgumentParser()
    parser.add_argument('host_id', action='store')
    parser.add_argument('--met_tool_wrapper', action='store_true', required=False)
    parser.add_argument('--climate', action='store_true', required=False)
    parser.add_argument('--convection_allowing_models', action='store_true', required=False)
    parser.add_argument('--cryosphere', action='store_true', required=False)
    parser.add_argument('--medium_range1', action='store_true', required=False)
    parser.add_argument('--medium_range2', action='store_true', required=False)
    parser.add_argument('--precipitation', action='store_true', required=False)
    parser.add_argument('--s2s', action='store_true', required=False)
    parser.add_argument('--space_weather', action='store_true', required=False)
    parser.add_argument('--tc_and_extra_tc', action='store_true', required=False)
    parser.add_argument('--all', action='store_true', required=False)
    parser.add_argument('--config', action='append', required=False)
    parser.add_argument('--skip_output_check',
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    print(args.config)

    if args.skip_output_check:
        print("Skipping output directory check. Output from previous tests "
              "may be found in output directory")
    else:
        handle_output_directories(output_base, output_base_prev)

    # compile list of use cases to run
    use_cases_to_run = []

    if args.config:
        for use_case in args.config:
            config_args = use_case.split(',')
            config_list = []
            for config_arg in config_args:
                # if relative path, must be relative to parm/use_cases
                if not os.path.isabs(config_arg):
                    # check that the full path exists before adding
                    # use_case_dir in case item is a config value override
                    check_config_exists = os.path.join(use_case_dir, config_arg)
                    if os.path.exists(check_config_exists):
                        config_arg = check_config_exists

                config_list.append(config_arg)

            use_cases_to_run.append(','.join(config_list))

    # exit if use case list is empty
    if not use_cases_to_run:
        print("ERROR: No use cases specified")
        sys.exit(1)

    # run use cases
    for param_file in use_cases_to_run:
        param = param_file.replace(metplus_home, test_metplus_base)
        run_test_use_case(param, test_metplus_base)

    # compare results with commands if prev output base has files
    if not os.path.exists(output_base_prev) or not os.listdir(output_base_prev):
        print("No files were found in previous OUTPUT_BASE: " + output_base_prev +\
              "\nRun this script again to compare results to previous run")
    else:
        print("\nIf files or directories were only found in one run, they will appear when you run the following:\n")
        diff_cmd = f'diff -r {output_base_prev} {output_base} | grep "Only in" | less'
        print(diff_cmd)

        print("\nCompare the output from previous run (" + output_base_prev + ") to this run"+\
              " (" + output_base + ").\nRun the following to compare results:")
        print(f"diff -r {output_base_prev} {output_base} | grep -v Binary | grep -v SSH | grep -v CONDA | grep -v OLDPWD | grep -v tmp | grep -v CLOCK_TIME | grep -v XDG | grep -v GSL | grep -v METPLUS | grep -v \"METplus took\" | grep -v \"Finished\" | grep -v \"\-\-\-\" | egrep -v \"^[[:digit:]]*c[[:digit:]]*$\" | less")

    # list any commands that failed
    for failed_run, out_dir in failed_runs:
        print(f"ERROR: Use case failed: {failed_run}")
#        print_error_logs(out_dir)

    if len(failed_runs) > 0:
        print(f"\nERROR: {len(failed_runs)} use cases failed")
        sys.exit(1)

    print("\nINFO: All use cases returned 0. Success!")
    sys.exit(0)

if __name__ == "__main__":
    main()
