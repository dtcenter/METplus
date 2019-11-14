#!/usr/bin/env python

import logging
import re
import os
import pytest
import met_util as util
import config_metplus

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")

#@pytest.fixture
def get_test_config():
    config_instance = config_metplus.setup(util.baseinputconfs)
    return config_instance


#@pytest.fixture
def get_test_logger():
    # Create a logger object based on the logging_test.conf
    config_instance = get_test_config()
    fixture_logger = util.get_logger(config_instance)
    return fixture_logger

# --------------Tests go here ------------


def test_log_level():
    # Verify that the log level is set to what we indicated in the config file.
    fixture_logger = get_test_logger()
    # Expecting log level = DEBUG as set in the test config file.
    level = logging.getLevelName('DEBUG')
    assert fixture_logger.isEnabledFor(level)


def test_log_level_key():
    # Verify that the LOG_LEVEL key is in the config file
    config_instance = get_test_config()
    section = 'config'
    option = 'LOG_LEVEL'
    assert config_instance.has_option(section, option)


def test_logdir_exists():
    # Verify that the expected log dir exists.
    config = get_test_config()
    log_dir = config.get('config', 'LOG_DIR')
    # Verify that a logfile exists in the log dir, with a filename
    # like {LOG_DIR}/master_metplus.YYYYMMDD.log
    assert os.path.exists(log_dir)


def test_logfile_exists():
    # Verify that a logfile with format master_metplus.log.YYYYMMDD exists
    # We are assuming that there can be numerous files in the log directory.
    config = get_test_config()
    log_dir = config.get('config', 'LOG_DIR')
    # Only check for the log file if the log directory is present
    if os.path.exists(log_dir):
        found = False
        for f in os.listdir(log_dir):
            match = re.match(r'master_metplus.log.[0-9]{8}', f)
            if match:
                # Check all files, first file may not be master log
                assert match.group(0)
                found = True
                break
        assert found

    else:
        # There is no log directory
        assert False






