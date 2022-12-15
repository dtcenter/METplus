#! /usr/bin/env python3

# Script to obtain commands needed to run use case groups including
# scripts or pip commands to obtain external Python dependencies
# Run by GitHub Actions (in .github/jobs/run_use_cases.py) to run use case tests

import sys
import os

# add METplus directory to sys path so the test suite can be found
METPLUS_TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               os.pardir))
sys.path.insert(0, METPLUS_TOP_DIR)

from internal.tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite
from metplus.util.string_manip import expand_int_string_to_list
from docker_utils import VERSION_EXT
from metplus import get_metplus_version

# path to METplus install location in Docker
METPLUS_DOCKER_LOC = '/metplus/METplus'

# name of conda environment used for cases that don't need special env
METPLUS_BASE_ENV = 'metplus_base'

# keywords in requirements list that trigger obtaining METcalcpy and METplotpy
PLOTCALC_KEYWORDS = [
    'metplotpy',
    'metcalcpy',
    'spacetime',
    'weatherregime',
]

# Docker envs that do not use Python so they do not need print conda list
NOT_PYTHON_ENVS = [
    'gfdl-tracker',
    'gempak',
]


def handle_automation_env(host_name, reqs, work_dir):
    # if no env is specified, use metplus base environment
    conda_env = METPLUS_BASE_ENV

    # if requirement ending with _env is set, then
    # use that version of python3 to run
    use_env = [item for item in reqs if item.endswith('_env')]
    if use_env:
        conda_env = use_env[0].replace('_env', '')

    # if not using docker (automation),
    # return no setup commands and python embedding argument to command
    if host_name != 'docker':
        if 'py_embed' in reqs and conda_env != METPLUS_BASE_ENV:
            return '', 'user_env_vars.MET_PYTHON_EXE=python3'
        return '', ''

    # add version extension to conda environment name
    conda_env_w_ext = f'{conda_env}{VERSION_EXT}'

    # start building commands to run before run_metplus.py in Docker
    setup_env = 'source /etc/bashrc;'

    # add conda bin to beginning of PATH
    python_dir = os.path.join('/usr', 'local', 'envs',
                              conda_env_w_ext, 'bin')
    python_path = os.path.join(python_dir, 'python3')
    setup_env += f" echo 'export PATH={python_dir}:\$PATH;' >> /etc/bashrc;"

    # if py_embed listed in requirements and using a Python
    # environment that differs from the MET env, set MET_PYTHON_EXE
    if 'py_embed' in reqs and conda_env != METPLUS_BASE_ENV:
        py_embed_arg = f'user_env_vars.MET_PYTHON_EXE={python_path} '
    else:
        py_embed_arg = ''

    # get METplus version to determine Externals file to use
    # to get METplotpy/METcalcpy/METdataio
    # If stable release, get main branch, otherwise get develop
    is_stable_release = len(get_metplus_version().split('-')) == 1
    externals_ext = '_stable.cfg' if is_stable_release else '.cfg'

    # if any metplotpy/metcalcpy keywords are in requirements list,
    # add command to obtain and install METplotpy and METcalcpy
    if any([item for item in PLOTCALC_KEYWORDS if item in str(reqs).lower()]):
        ce_file = os.path.join(work_dir, '.github', 'parm',
                               f'Externals_metplotcalcpy{externals_ext}')
        setup_env += (
            f'cd {METPLUS_DOCKER_LOC};'
            f'{work_dir}/manage_externals/checkout_externals -e {ce_file};'
            f'{python_path} -m pip install {METPLUS_DOCKER_LOC}/../METplotpy;'
            f'{python_path} -m pip install {METPLUS_DOCKER_LOC}/../METcalcpy;'
            'cd -;'
        )

    # if metdataio is in requirements list, add command to obtain METdataio
    if 'metdataio' in str(reqs).lower():
        ce_file = os.path.join(work_dir, '.github', 'parm',
                               f'Externals_metdataio{externals_ext}')
        setup_env += (
            f'cd {METPLUS_DOCKER_LOC};'
            f'{work_dir}/manage_externals/checkout_externals -e {ce_file};'
            f'{python_path} -m pip install {METPLUS_DOCKER_LOC}/../METdataio;'
            'cd -;'
        )

    # if gempak is in requirements list, add JRE bin to path for java
    if 'gempak' in str(reqs).lower():
        setup_env += 'export PATH=$PATH:/usr/lib/jvm/jre/bin;'

    # if metplus is in requirements list,
    # add top of METplus repo to PYTHONPATH so metplus can be imported
    if 'metplus' in str(reqs).lower():
        setup_env += f'export PYTHONPATH={METPLUS_DOCKER_LOC}:$PYTHONPATH;'

    # list packages in python environment that will be used
    if conda_env not in NOT_PYTHON_ENVS:
        setup_env += (
            f'echo Using environment: dtcenter/metplus-envs:{conda_env_w_ext};'
            f'echo cat /usr/local/envs/{conda_env_w_ext}/environments.yml;'
            f'echo ----------------------------------------;'
            f'cat /usr/local/envs/{conda_env_w_ext}/environments.yml;'
            'echo ----------------------------------------;'
        )

    return setup_env, py_embed_arg


#def _add_to_bashrc(command):
#    return f"echo '{command.replace('$', '\\$')};' >> /etc/bashrc"

def main(categories, subset_list, work_dir=None,
         host_name=os.environ.get('HOST_NAME')):
    all_commands = []

    if work_dir is None:
        work_dir = METPLUS_TOP_DIR

    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories, subset_list)

    output_top_dir = os.environ.get('METPLUS_TEST_OUTPUT_BASE', '/data/output')

    # use METPLUS_TEST_SETTINGS_CONF if set
    test_settings_conf = os.environ.get('METPLUS_TEST_SETTINGS_CONF', '')
    if not test_settings_conf and host_name == 'docker':
        test_settings_conf = os.path.join(work_dir,
                                          '.github',
                                          'parm',
                                          'test_settings.conf')

    for group_name, use_cases_by_req in test_suite.category_groups.items():
        for use_case_by_requirement in use_cases_by_req:
            reqs = use_case_by_requirement.requirements

            setup_env, py_embed_arg = handle_automation_env(host_name, reqs,
                                                            work_dir)

            # use status variable to track if any use cases failed
            use_case_cmds = []
            if host_name != 'docker':
                use_case_cmds.append('status=0')
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
                use_case_cmd = (f"run_metplus.py"
                                f" {' '.join(config_args)}"
                                f" {py_embed_arg}{test_settings_conf}"
                                f" config.OUTPUT_BASE={output_base}")
                use_case_cmds.append(use_case_cmd)
                # check exit code from use case command and
                # set status to non-zero value on error
                if host_name != 'docker':
                    use_case_cmds.append("if [ $? != 0 ]; then status=1; fi")

            # if any use cases failed, force non-zero exit code with false
            if host_name != 'docker':
                use_case_cmds.append("if [ $status != 0 ]; then false; fi")
            # add commands to set up environment before use case commands
            all_commands.append((setup_env, use_case_cmds, reqs))

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
    categories, subset_list, _ = handle_command_line_args()
    all_commands = main(categories, subset_list)
    for setup_commands, use_case_commands, requirements in all_commands:
        print(f"REQUIREMENTS: {','.join(requirements)}")
        if setup_commands:
            command_format = ';\\\n'.join(setup_commands.split(';'))
            print(f"SETUP COMMANDS:\n{command_format}\n")
        command_format = ';\\\n'.join(use_case_commands)
        print(f"USE CASE COMMANDS:\n{command_format}\n")
