#!/usr/bin/env python3

import sys
import os
import re
import shlex
import subprocess
from os.path import dirname

import get_data_volumes
import download_gempaktocf

# add internal_tests/use_cases directory to path so the test suite can be found
sys.path.insert(0, os.path.abspath(os.path.join(dirname(__file__),
                                                os.pardir,
                                                os.pardir,
                                                'internal_tests',
                                                'use_cases')))

from metplus_use_case_suite import METplusUseCasesByRequirement as mp_by_req
from metplus_use_case_suite import METplusUseCaseSuite

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

def handle_subset(subset):
    subset_list = []
    # separate into list by comma
    comma_list = subset.split(',')
    for comma_item in comma_list:
        dash_list = comma_item.split('-')
        # if item contains X-Y, expand it
        if len(dash_list) == 2:
            for i in range(int(dash_list[0].strip()),
                           int(dash_list[1].strip())+1,
                           1):
                subset_list.append(i)
        else:
            subset_list.append(comma_item.strip())

    return subset_list

def main(categories_list, subset_list):


    # get data volumes
    print(f"calling get_data_volumes.main({categories_list})")
    volumes_from = get_data_volumes.main(categories_list)

    # obtain GempakToCF.jar for cases that read GEMPAK data
    input_data_directory = os.path.join(os.environ['OWNER_BUILD_DIR'],
                                        'input')
    download_gempaktocf.run(input_data_directory)

    # becomes False if any use case fails
    isOK = True

    # run use cases
    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories)
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
            travis_build_dir = os.environ['TRAVIS_BUILD_DIR']
            docker_work_dir = os.environ['DOCKER_WORK_DIR']
            cmd = (f'{travis_build_dir}/ci/travis_jobs/docker_run_metplus.sh'
                   f' "{requirement_args}'
                   f' {docker_work_dir}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker '
                   f'{use_case_args}" "{volumes_from}"')
            print(cmd)
            try:
                ret = subprocess.run(shlex.split(cmd), check=True)
            except subprocess.CalledProcessError as err:
                print(f"ERROR: Command failed: {cmd}")
                isOK = False

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
    categories_list = categories.split(',')

    # get subset values if specified
    if len(sys.argv) > 2:
        subset_list = handle_subset(sys.argv[2])
    else:
        subset_list = None

    return categories_list, subset_list

if __name__ == "__main__":
    categories_list, subset_list =  handle_command_line_args()
    main(categories_list, subset_list)