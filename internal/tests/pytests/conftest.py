import sys
import os
import shlex
import subprocess
import pytest
import getpass
import shutil
from pathlib import Path

# add METplus directory to path so the wrappers and utilities can be found
metplus_dir = str(Path(__file__).parents[3])
sys.path.insert(0, os.path.abspath(metplus_dir))

from metplus.util import config_metplus

# get host from either METPLUS_PYTEST_HOST or from actual host name
# Look for minimum_pytest.<pytest_host>.sh script to source
# error and exit if not found
pytest_host = os.environ.get('METPLUS_PYTEST_HOST')
if pytest_host is None:
    import socket
    pytest_host = socket.gethostname()
    print("No hostname provided with METPLUS_PYTEST_HOST, "
          f"using {pytest_host}")
else:
    print(f"METPLUS_PYTEST_HOST = {pytest_host}")

minimum_pytest_file = os.path.join(os.path.dirname(__file__),
                                   f'minimum_pytest.{pytest_host}.sh')
if not os.path.exists(minimum_pytest_file):
    print(f"ERROR: minimum_pytest.{pytest_host}.sh file must exist in "
          "pytests directory. Set METPLUS_PYTEST_HOST correctly or "
          "create file to run pytests on this host.")
    sys.exit(4)

# source minimum_pytest.<pytest_host>.sh script
current_user = getpass.getuser()
command = shlex.split(f"env -i bash -c 'export USER={current_user} && "
                      f"source {minimum_pytest_file} && env'")
proc = subprocess.Popen(command, stdout=subprocess.PIPE)

for line in proc.stdout:
    line = line.decode(encoding='utf-8', errors='strict').strip()
    key, value = line.split('=')
    os.environ[key] = value

proc.communicate()

output_base = os.environ['METPLUS_TEST_OUTPUT_BASE']
if not output_base:
    print('ERROR: METPLUS_TEST_OUTPUT_BASE must be set to a path to write')
    sys.exit(1)

test_output_dir = os.path.join(output_base, 'test_output')
if os.path.exists(test_output_dir):
    print(f'Removing test output dir: {test_output_dir}')
    shutil.rmtree(test_output_dir)


@pytest.fixture(scope='function')
def metplus_config_files():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    def read_configs(extra_configs):
        # Read in minimum pytest config file and any other extra configs
        script_dir = os.path.dirname(__file__)
        minimum_conf = os.path.join(script_dir, 'minimum_pytest.conf')
        args = [minimum_conf]
        for extra_config in extra_configs:
            if extra_config.startswith('use_cases'):
                args.append(os.path.join(metplus_dir, 'parm', extra_config))
            elif extra_config:
                args.append(extra_config)

        config = config_metplus.setup(args)
        return config

    return read_configs

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)

#@pytest.fixture(scope='function')
@pytest.fixture()
def metplus_config(request):
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    script_dir = os.path.dirname(__file__)
    args = [os.path.join(script_dir, 'minimum_pytest.conf')]
    config = config_metplus.setup(args)
    yield config

    # don't remove output base if test fails
    if request.node.rep_call.failed:
        return
    config_output_base = config.getdir('OUTPUT_BASE')
    if config_output_base and os.path.exists(config_output_base):
        shutil.rmtree(config_output_base)
