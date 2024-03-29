#!/usr/bin/env python3

import pytest

import logging
import re
import os


@pytest.mark.util
def test_log_level(metplus_config):
    # Verify that the log level is set to what we indicated in the config file.
    config = metplus_config
    fixture_logger = config.logger
    # Expecting log level = INFO as set in the test config file.
    level = logging.getLevelName('INFO')
    assert fixture_logger.isEnabledFor(level)


@pytest.mark.util
def test_log_level_key(metplus_config):
    # Verify that the LOG_LEVEL key is in the config file
    config_instance = metplus_config
    section = 'config'
    option = 'LOG_LEVEL'
    assert config_instance.has_option(section, option)


@pytest.mark.util
def test_logdir_exists(metplus_config):
    # Verify that the expected log dir exists.
    config = metplus_config
    log_dir = config.get('config', 'LOG_DIR')
    # Verify that a logfile exists in the log dir, with a filename
    # like {LOG_DIR}/metplus.YYYYMMDD.log
    assert os.path.exists(log_dir)


@pytest.mark.util
def test_logfile_exists(metplus_config):
    # Verify that a logfile with format metplus.log exists
    # We are assuming that there can be numerous files in the log directory.
    config = metplus_config
    log_dir = config.get('config', 'LOG_DIR')
    # Only check for the log file if the log directory is present
    if os.path.exists(log_dir):
        found = False
        for f in os.listdir(log_dir):
            match = re.match(r'metplus.log', f)
            if match:
                # Check all files, first file may not be master log
                assert match.group(0)
                found = True
                break
        assert found

    else:
        # There is no log directory
        assert False
