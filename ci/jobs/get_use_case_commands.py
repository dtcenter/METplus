#! /usr/bin/env python3

import sys
import os

# add internal_tests/use_cases directory to path so the test suite can be found
USE_CASES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir,
                                             os.pardir))
sys.path.insert(0, USE_CASES_DIR)

from internal_tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite
from metplus.util.met_util import expand_int_string_to_list

def handle_requirements(requirements, work_dir):
    requirement_args = []
    for requirement in requirements:
        # check if get_{requirement} script exists and use it if it does
        script_path = os.path.join(work_dir,
                                   'ci',
                                   'jobs',
                                    f'get_{requirement.lower()}.sh')
        print(f"Looking for script: {script_path}")
        if os.path.exists(script_path):
            print("Script found, using script to obtain dependencies")
            requirement_args.append(script_path)
        else:
            # if script doesn't exist, use pip3 install to obtain package
            print("Script does not exist. Using pip3 install to obtain depdencies")
            requirement_args.append(f"pip3 install {requirement}")

    return requirement_args

def main(categories, subset_list, work_dir=None, host_name='docker'):
    all_commands = []

    if work_dir is None:
        work_dir = USE_CASES_DIR

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
            cmd = (f'{work_dir}/internal_tests/use_cases/run_test_use_cases.sh '
                   f'{host_name} {use_case_args}')
            all_commands.append((cmd, requirement_args))

    return sorted(all_commands, key = lambda x: x[1])

def handle_command_line_args():
    # read command line arguments to determine which use cases to run
    if len(sys.argv) < 2:
        print("No use cases specified")
        sys.exit(1)

    # split up categories by & or ,
    categories = sys.argv[1]

    # get subset values if specified
    if len(sys.argv) > 2:
        if sys.argv[2] == 'all':
            subset_list = None
        else:
            subset_list = expand_int_string_to_list(sys.argv[2])
    else:
        subset_list = None


    # check if comparison flag should be set
    if len(sys.argv) > 3:
        do_comparison = True
    else:
        do_comparison = False

    return categories, subset_list, do_comparison

if __name__ == '__main__':
    categories, subset_list, _ =  handle_command_line_args()
    all_commands = main(categories, subset_list)
    for command, requirements in all_commands:
        print(f"COMMAND:")
        for req in requirements:
            print(f'{req}')
        print(f'{command}\n')
