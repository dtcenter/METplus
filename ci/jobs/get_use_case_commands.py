#! /usr/bin/env python3

import sys
import os

# add internal_tests/use_cases directory to path so the test suite can be found
USE_CASES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir,
                                             os.pardir))
sys.path.insert(0, USE_CASES_DIR)

from internal_tests.use_cases.metplus_use_case_suite import METplusUseCasesByRequirement as mp_by_req
from internal_tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite
from metplus.util.met_util import expand_int_string_to_list

def handle_requirements(requirements, work_dir):
    requirement_args = []
    for requirement in requirements:
        if requirement in mp_by_req.PYTHON_REQUIREMENTS:
            command = mp_by_req.PYTHON_REQUIREMENTS[requirement]

            if 'pip' in command:
                requirement_args.append(command)
            else:
                # if script, the path is relative to METplus directory
                command_path = os.path.join(work_dir,
                                            'METplus',
                                            command)
                requirement_args.append(command_path)
        else:
            requirement_args.append(f"pip3 install {requirement}")

    # add semi-colon to end of each command
    if requirement_args:
        return f"{';'.join(requirement_args)};"

    return ''

def main(categories, subset_list, work_dir=USE_CASES_DIR, host_name='docker'):
    all_commands = []

    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories, subset_list)

    for group_name, use_cases_by_requirement in test_suite.category_groups.items():
        for use_case_by_requirement in use_cases_by_requirement:
            requirement_args = handle_requirements(use_case_by_requirement.requirements,
                                                   work_dir)
            all_use_case_args = []
            for use_case in use_case_by_requirement.use_cases:
                use_case_args = f"--config {','.join(use_case.config_args)}"
                all_use_case_args.append(use_case_args)

            all_use_case_args.append('--skip_output_check')
            use_case_args = ' '.join(all_use_case_args)
            cmd = (f'{requirement_args} '
                   f'{work_dir}/METplus/internal_tests/use_cases/run_test_use_cases.sh {host_name} '
                   f'{use_case_args}')
            all_commands.append(cmd)

    return all_commands

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

if __name__ == '__main__':
    categories, subset_list =  handle_command_line_args()
    main(categories, subset_list)
