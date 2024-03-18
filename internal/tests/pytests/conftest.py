import sys
import os
import shlex
import subprocess
import pytest
import getpass
import shutil
from unittest import mock
from pathlib import Path
from netCDF4 import Dataset

# add METplus directory to path so the wrappers and utilities can be found
metplus_dir = str(Path(__file__).parents[3])
sys.path.insert(0, os.path.abspath(metplus_dir))

from metplus.util import config_metplus

output_base = os.environ.get("METPLUS_TEST_OUTPUT_BASE")
if not output_base:
    print("ERROR: METPLUS_TEST_OUTPUT_BASE must be set to a path to write")
    sys.exit(1)

try:
    test_output_dir = os.path.join(output_base, "test_output")
    if os.path.exists(test_output_dir):
        print(f"Removing test output dir: {test_output_dir}")
        shutil.rmtree(test_output_dir)

    if not os.path.exists(test_output_dir):
        print(f"Creating test output dir: {test_output_dir}")
        os.makedirs(test_output_dir)
except PermissionError:
    print(f"ERROR: Cannot write to $METPLUS_TEST_OUTPUT_BASE: {output_base}")
    sys.exit(2)


@pytest.fixture(scope="session", autouse=True)
def custom_tmpdir():
    """! Set the default output location for temp files produced by pytest
    to METPLUS_TEST_OUTPUT_BASE env var. Causes default pytest fixtures,
    such as tmpdir_factory, to write temp files to this dir.

    A sub directory named 'pytest_tmp' is created to ensure there will never
    be name conflicts between files created by default pytest fixture and
    other methods for writing temp files.
    """
    original_var = os.environ.get("PYTEST_DEBUG_TEMPROOT", None)
    output_base = os.environ.get("METPLUS_TEST_OUTPUT_BASE")
    temp_base = os.path.join(output_base, "pytest_tmp")

    os.environ["PYTEST_DEBUG_TEMPROOT"] = temp_base
    if not os.path.exists(temp_base):
        os.mkdir(temp_base)
    yield
    # Restore original value, if existed
    if original_var:
        os.environ["PYTEST_DEBUG_TEMPROOT"] = original_var


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

    This fixture wraps config.logger with a MagicMock object, allowing tests to
    assert the logger was called with a specific message. Logged output is still
    written to ${METPLUS_TEST_OUTPUT_BASE}/test_output/{RUN_ID}/logs/metplus.log 

    e.g.
    def test_example(metplus_config):
        config = metplus_config
        some_function(config)
        config.logger.info.assert_called_once_with("Info message")
        config.logger.error.assert_not_called()

    See documentation for unittest.mock for full functionality.
    """
    script_dir = os.path.dirname(__file__)
    args = [os.path.join(script_dir, "minimum_pytest.conf")]
    config = config_metplus.setup(args)

    # Set mock logger
    old_logger = config.logger
    config.logger = mock.MagicMock(wraps=old_logger)

    yield config
    
    if config.logger.error.call_args_list:
        err_msgs = [
                str(msg.args[0]) 
                for msg 
                in config.logger.error.call_args_list
                if len(msg.args) != 0]
        print("Tests raised the following errors:")
        print("\n".join(err_msgs))
    if config.logger.warning.call_args_list:
        warn_msgs = [
                str(msg.args[0])
                for msg
                in config.logger.warning.call_args_list
                if len(msg.args) != 0]
        print("\nTests raised the following warnings:")
        print("\n".join(warn_msgs))
    config.logger = old_logger
    # don't remove output base if test fails
    if request.node.rep_call.failed:
        return
    config_output_base = config.getdir("OUTPUT_BASE")
    if config_output_base and os.path.exists(config_output_base):
        shutil.rmtree(config_output_base)


@pytest.fixture(scope="function")
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
        minimum_conf = os.path.join(script_dir, "minimum_pytest.conf")
        args = extra_configs.copy()
        args.insert(0, minimum_conf)
        config = config_metplus.setup(args)
        return config

    return read_configs


@pytest.fixture(scope="module")
def make_dummy_nc():
    return make_nc


def make_nc(tmp_path, lon, lat, z, data, variable='Temp', file_name='fake.nc'):
    """! Make a dummy netCDF file for use in tests. Populates a generic single
    variable netcdf is dimension, lat, lon, z.

    @param tmp_path directory to write this netCDF to.
    @param lon list of longitude values.
    @param lat list of latitude values.
    @param z list of pressure levels.
    @param data array of values with dimesions (lat, lon, z) 
    @param variable (optional) string name of variable, defualt 'Temp'
    @param file_name (optional) string name of file, defualt 'fake.nc'
    
    @returns path to netCDF file
    """
    file_name = tmp_path / file_name
    with Dataset(file_name, "w", format="NETCDF4") as rootgrp:
        # Some tools (i.e. diff_util) can't deal with groups,
        # so attach dimensions and variables to the root group.
        rootgrp.createDimension("lon", len(lon))
        rootgrp.createDimension("lat", len(lat))
        rootgrp.createDimension("z", len(z))
        rootgrp.createDimension("time", None)

        # create variables
        longitude = rootgrp.createVariable("Longitude", "f4", "lon")
        latitude = rootgrp.createVariable("Latitude", "f4", "lat")
        levels = rootgrp.createVariable("Levels", "i4", "z")
        temp = rootgrp.createVariable(variable, "f4", ("time", "lon", "lat", "z"))
        time = rootgrp.createVariable("Time", "i4", "time")

        longitude[:] = lon
        latitude[:] = lat
        levels[:] = z
        temp[0, :, :, :] = data

    return file_name


@pytest.fixture(scope="function")
def get_test_data_dir():
    """!Get path to directory containing test data.
    """
    def get_test_data_path(subdir):
        internal_tests_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir)
        )
        return os.path.join(internal_tests_dir, 'data', subdir)

    return get_test_data_path
