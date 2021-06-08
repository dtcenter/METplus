#! /usr/bin/env python3

# Script to obtain commands needed to run use case groups including
# scripts or pip commands to obtain external Python dependencies
# Run by GitHub Actions (in ci/jobs/run_use_cases.py) to run use case tests

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
        # don't obtain METviewer here because it has to be set up outside of
        # docker container that runs the use cases
        if requirement.lower() == 'metviewer':
            continue

        # check if get_{requirement} script exists and use it if it does
        script_path = os.path.join(work_dir,
                                   'ci',
                                   'jobs',
                                   'python_requirements',
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

    output_top_dir = os.environ.get('METPLUS_TEST_OUTPUT_BASE', '/data/output')

    for group_name, use_cases_by_requirement in test_suite.category_groups.items():
        for use_case_by_requirement in use_cases_by_requirement:
            requirements = use_case_by_requirement.requirements

            # if requirement ending with _env is set, use that version of python3 to run
            use_env = [item for item in requirements if item.endswith('_env')]
            if use_env:
                python_path = f"/usr/local/envs/{use_env[0].replace('_env', '')}/bin/python3"
            else:
                python_path = 'python3'

            # if py_embed listed in requirements, set MET_PYTHON_EXE
            if 'py_embed' in requirements:
                py_embed_arg = f' user_env_vars.MET_PYTHON_EXE={python_path}'
            else:
                py_embed_arg = ''

            for use_case in use_case_by_requirement.use_cases:
                output_base = os.path.join(output_top_dir, use_case.name)
                use_case_cmd = (f"{python_path} run_metplus.py "
                                f"{' '.join(use_case.config_args)} "
                                f"config.OUTPUT_BASE={output_base}"
                                f"{py_embed_arg}")
                all_commands.append(use_case_cmd)

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
