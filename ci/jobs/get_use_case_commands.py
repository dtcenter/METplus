#! /usr/bin/env python3

# Script to obtain commands needed to run use case groups including
# scripts or pip commands to obtain external Python dependencies
# Run by GitHub Actions (in ci/jobs/run_use_cases.py) to run use case tests

import sys
import os

# add METplus directory to sys path so the test suite can be found
USE_CASES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir,
                                             os.pardir))
sys.path.insert(0, USE_CASES_DIR)

from internal_tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite
from metplus.util.met_util import expand_int_string_to_list

METPLUS_BASE_ENV = 'metplus_base'

def main(categories, subset_list, work_dir=None, host_name='docker'):
    all_commands = []

    if work_dir is None:
        work_dir = USE_CASES_DIR

    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories, subset_list)

    output_top_dir = os.environ.get('METPLUS_TEST_OUTPUT_BASE', '/data/output')
    system_conf = os.path.join(work_dir, 'ci', 'parm', 'system.conf')

    for group_name, use_cases_by_req in test_suite.category_groups.items():
        for use_case_by_requirement in use_cases_by_req:
            reqs = use_case_by_requirement.requirements

            setup_env = 'source /etc/bashrc;'
            conda_env = None
            python_path = 'python3'

            # if requirement ending with _env is set, then
            # use that version of python3 to run
            use_env = [item for item in reqs if item.endswith('_env')]
            if use_env:
                conda_env = use_env[0].replace('_env', '')
            else:
                # if no env is specified, use metplus base environment
                conda_env = METPLUS_BASE_ENV

            # if using docker, add conda bin to beginning of PATH
            if host_name == 'docker':
                python_dir = os.path.join('/usr', 'local', 'envs',
                                          conda_env, 'bin')
                python_path = os.path.join(python_dir, 'python3')
                setup_env += f' export PATH={python_dir}:$PATH;'

            # if py_embed listed in requirements and using a Python
            # environment that differs from the MET env, set MET_PYTHON_EXE
            if 'py_embed' in reqs and conda_env != METPLUS_BASE_ENV:
                py_embed_arg = f'user_env_vars.MET_PYTHON_EXE={python_path} '
            else:
                py_embed_arg = ''

            # if metplotpy, metcalcpy, or spacetime are in requirements list,
            # add command to obtain and install METplotpy and METcalcpy
            plotcalc_keywords = ['metplotpy', 'metcalcpy', 'spacetime']
            if any([item for item in plotcalc_keywords
                    if item in str(reqs).lower()]):
                setup_env += (
                    f'{work_dir}/manage_externals/checkout_externals'
                    f' -e {work_dir}/ci/parm/Externals_metplotcalcpy.cfg;'
                    f'{python_path} -m pip install {work_dir}/METplotpy;'
                    f'{python_path} -m pip install {work_dir}/METcalcpy;'
                )

            # if metdatadb is in requirements list,
            # add command to obtain METdatadb
            plotcalc_keywords = ['metplotpy', 'metcalcpy', 'spacetime']
            if 'metdatadb' in str(reqs).lower():
                setup_env += (
                    f'{work_dir}/manage_externals/checkout_externals'
                    f' -e {work_dir}/ci/parm/Externals_metdatadb.cfg;'
                )

            use_case_cmds = []
            for use_case in use_case_by_requirement.use_cases:
                # add parm/use_cases path to config args if they are conf files
                config_args = []
                for config_arg in use_case.config_args:
                    if config_arg.endswith('.conf'):
                        config_arg = os.path.join(work_dir, 'parm',
                                                  'use_cases',
                                                  config_arg)

                    config_args.append(config_arg)

                output_base = os.path.join(output_top_dir, use_case.name)
                use_case_cmd = (f"{setup_env} run_metplus.py"
                                f" {' '.join(config_args)}"
                                f" {py_embed_arg}{system_conf}"
                                f" config.OUTPUT_BASE={output_base}")
                use_case_cmds.append(use_case_cmd)
            group_commands = ';'.join(use_case_cmds)
            all_commands.append((group_commands, reqs))

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
