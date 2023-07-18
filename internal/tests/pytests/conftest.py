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

output_base = os.environ.get('METPLUS_TEST_OUTPUT_BASE')
if not output_base:
    print('ERROR: METPLUS_TEST_OUTPUT_BASE must be set to a path to write')
    sys.exit(1)

test_output_dir = os.path.join(output_base, 'test_output')
if os.path.exists(test_output_dir):
    print(f'Removing test output dir: {test_output_dir}')
    shutil.rmtree(test_output_dir)

if not os.path.exists(test_output_dir):
    print(f'Creating test output dir: {test_output_dir}')
    try:
        os.makedirs(test_output_dir)
    except PermissionError:
        print(f'ERROR: You cannot write to METPLUS_TEST_OUTPUT_BASE')
        sys.exit(2)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """! This is used to capture the status of a test so the metplus_config
    fixture can remove output data from tests that pass.
    """
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture()
def metplus_config(request):
    """! Create a METplus configuration object using only the minimum required
    settings found in minimum_pytest.conf. This fixture checks the result of
    the test it is used in and automatically removes the output that is
    generated by it unless the test fails. This makes it much easier to review
    the failed tests. To use this fixture, add metplus_config to the test
    function arguments and set a variable called config to metplus_config, e.g.
    config = metplus_config.
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


@pytest.fixture(scope='function')
def metplus_config_files():
    """! Create a METplus configuration object using minimum_pytest.conf
    settings and any list of config files.The metplus_config fixture is
    preferred because it automatically cleans up the output files generated
    by the use case unless the test fails. To use this in a test, add
    metplus_config_files as an argument to the test function and pass in a list
    of config files to it. Example: config = metplus_config_files([my_file])
    """
    def read_configs(extra_configs):
        # Read in minimum pytest config file and any other extra configs
        script_dir = os.path.dirname(__file__)
        minimum_conf = os.path.join(script_dir, 'minimum_pytest.conf')
        args = extra_configs.copy()
        args.append(minimum_conf)
        config = config_metplus.setup(args)
        return config

    return read_configs
