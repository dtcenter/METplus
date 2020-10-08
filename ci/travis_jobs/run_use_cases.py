#!/usr/bin/env python3

import sys
import os
import re
import shlex
import subprocess

import get_data_volumes

# add internal_tests/use_cases directory to path so the test suite can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir,
                                                'internal_tests',
                                                'use_cases')))

from metplus_use_case_suite import METplusUseCasesByRequirement as mp_by_req
from metplus_use_case_suite import METplusUseCaseSuite

def handle_requirements(requirements):
    requirement_args = []
    metplus_home = os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir)
    for requirement in requirements:
        if requirement in mp_by_req.PYTHON_REQUIREMENTS:
            command = mp_by_req.PYTHON_REQUIREMENTS[requirement]

            # check if command is a path relative to METplus directory
            command_path = os.path.join(metplus_home, command)
            if os.path.exists(command_path):
                requirement_args.append(command_path)
            else:
                requirement_args.append(command)
        else:
            raise KeyError(f"Invalid Python Requirement: {requirement}")

    # add semi-colon to end of each command
    if requirement_args:
        return ';'.join(requirement_args) + '; '

    return ''

# read command line arguments to determine which use cases to run
if len(sys.argv) < 2:
    print("No use cases specified")
    sys.exit(1)

# split up categories by & or ,
categories = sys.argv[1]
categories_list = categories.split(',')

# get subset values if specified
#if len(sys.argv) > 2:
#    subset = sys.argv[2]
#    # if X-Y, get range of values
#    if re.match(r''
    
# get data volumes
print(f"calling get_data_volumes.main({categories_list})")
volumes_from = get_data_volumes.main(categories_list)

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

        all_use_case_args.append('--skip-output-check')
        use_case_args = ' '.join(all_use_case_args)
        travis_build_dir = os.environ['TRAVIS_BUILD_DIR']
        docker_work_dir = os.environ['DOCKER_WORK_DIR']
        cmd = (f'{travis_build_dir}/ci/travis_jobs/docker_run_metplus.sh'
               f'{requirement_args}'
               f' "{docker_work_dir}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker '
               f'{use_case_args}" "{volumes_from}"')
        print(cmd)
        ret = subprocess.run(shlex.split(cmd), check=True)
        if ret.returncode != 0:
            print(f"ERROR: Command failed: {cmd}")
            isOK = False
