#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import config_metplus
from pb2nc_wrapper import PB2NCWrapper
from config_wrapper import ConfigWrapper
import met_util as util


# --------------------TEST CONFIGURATION and FIXTURE SUPPORT -------------
#
# The test configuration and fixture support the additional configuration
# files used in METplus
#              !!!!!!!!!!!!!!!
#              !!!IMPORTANT!!!
#              !!!!!!!!!!!!!!!
# The following two methods should be included in ALL pytest tests for METplus.
#
#
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


def cmdopt(request):
    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
def pb2nc_wrapper():
    """! Returns a default PB2NCWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    config = metplus_config()
    return PB2NCWrapper(config, config.logger)

def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='PB2NCWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='PB2NCWrapper ')
        produtil.log.postmsg('pb2nc_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        logger = util.get_logger(config)
        config = ConfigWrapper(config, logger)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'pb2nc_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------

# ---------------------
# test_reformat_grid_id
# ---------------------
@pytest.mark.parametrize(
    # key = grid_id, value = expected reformatted grid id
        'key, value', [
            ('G1', 'G001'),
            ('G100', 'G100'),
            ('G10', 'G010'),
        ]
)
def test_reformat_grid_id(key, value):
    # Verify that reformatting of the grid id is correct
    pb = pb2nc_wrapper()
    reformatted = pb.reformat_grid_id(key)
    assert value == reformatted


# test files can be found with find_input_files with varying offset lists


# test that find_and_check_output_file returns correctly based on
# if file exists and if 'skip if exists' is turned on

# test that environment variables are formatted and set correctly

# test that command is generated correctly
def test_get_command():
    pb = pb2nc_wrapper()
    assert True
