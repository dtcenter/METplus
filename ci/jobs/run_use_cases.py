#!/usr/bin/env python3

import sys
import os
import re
import shlex
import subprocess
from os.path import dirname

import get_data_volumes
import download_gempaktocf
import print_log_errors

import get_use_case_commands
from metplus.util.met_util import expand_int_string_to_list

def main(categories, subset_list):

    categories_list = categories.split(',')

    OWNER_BUILD_DIR = os.path.dirname(os.environ['GITHUB_WORKSPACE'])

    # get data volumes
    print(f"calling get_data_volumes.main({categories_list})")
    volumes_from = get_data_volumes.main(categories_list)

    # obtain GempakToCF.jar for cases that read GEMPAK data
    input_data_directory = os.path.join(OWNER_BUILD_DIR,
                                        'input')
    download_gempaktocf.run(input_data_directory)

    # becomes False if any use case fails
    isOK = True

    # run use cases
    work_dir = os.path.join(os.environ.get('DOCKER_WORK_DIR'),
                            'METplus')
    all_commands = get_use_case_commands.main(categories_list,
                                              subset_list,
                                              work_dir=work_dir)
    for command, requirements in all_commands:
        travis_build_dir = os.environ['GITHUB_WORKSPACE']
        if requirements:
            reqs = f"{';'.join(requirements)};"
        else:
            reqs = ''
        cmd = (f'{travis_build_dir}/ci/jobs/docker_run_metplus.sh'
               f' "{reqs}{command}" "{volumes_from}"')
        print(cmd)
        try:
            subprocess.run(shlex.split(cmd), check=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed: {cmd} -- {err}")
            isOK = False
            output_dir = os.path.join(OWNER_BUILD_DIR,
                                      'output')
            replacement_dir = os.path.join(os.environ['DOCKER_DATA_DIR'],
                                           'output')
            print_log_errors.run(output_dir,
                                 replacement_dir)

    # if any tests failed, exit 1, otherwise exit 0
    if not isOK:
        sys.exit(1)

def handle_command_line_args():
    # read command line arguments to determine which use cases to run
    if len(sys.argv) < 2:
        print("No use cases specified")
        sys.exit(1)

    # split up categories by & or ,
    categories = sys.argv[1]

    # get subset values if specified
    if len(sys.argv) > 2:
        subset_list = expand_int_string_to_list(sys.argv[2])
    else:
        subset_list = None

    return categories, subset_list

if __name__ == "__main__":
    categories, subset_list =  handle_command_line_args()
    main(categories, subset_list)
