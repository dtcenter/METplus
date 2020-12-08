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

# add internal_tests/use_cases directory to path so the test suite can be found
sys.path.insert(0, os.path.abspath(os.path.join(dirname(__file__),
                                                os.pardir,
                                                os.pardir,)))

from internal_tests.use_cases.metplus_use_case_suite import METplusUseCasesByRequirement as mp_by_req
from internal_tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite
from metplus.util.met_util import expand_int_string_to_list

def handle_requirements(requirements):
    requirement_args = []
    for requirement in requirements:
        if requirement in mp_by_req.PYTHON_REQUIREMENTS:
            command = mp_by_req.PYTHON_REQUIREMENTS[requirement]

            if 'pip' in command:
                requirement_args.append(command)
            else:
                # if script, the path is relative to METplus directory
                command_path = os.path.join(os.environ['DOCKER_WORK_DIR'],
                                            'METplus',
                                            command)
                requirement_args.append(command_path)
        else:
            raise KeyError(f"Invalid Python Requirement: {requirement}")

    # add semi-colon to end of each command
    if requirement_args:
        return f"{';'.join(requirement_args)};"

    return ''

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
    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories, subset_list)
    for group_name, use_cases_by_requirement in test_suite.category_groups.items():
        print(group_name)
        for use_case_by_requirement in use_cases_by_requirement:
            # handle requirements
            requirement_args = handle_requirements(use_case_by_requirement.requirements)
            all_use_case_args = []
            for use_case in use_case_by_requirement.use_cases:
                use_case_args = f"--config {','.join(use_case.config_args)}"
                all_use_case_args.append(use_case_args)

            all_use_case_args.append('--skip_output_check')
            use_case_args = ' '.join(all_use_case_args)
            travis_build_dir = os.environ['GITHUB_WORKSPACE']
            docker_work_dir = os.environ['DOCKER_WORK_DIR']
            cmd = (f'{travis_build_dir}/ci/jobs/docker_run_metplus.sh'
                   f' "{requirement_args}'
                   f' {docker_work_dir}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker '
                   f'{use_case_args}" "{volumes_from}"')
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
