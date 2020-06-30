#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.util.config import config_metplus
from metplus.wrappers.pb2nc_wrapper import PB2NCWrapper
from metplus.util import met_util as util
from metplus.util import feature_util

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
#def pytest_addoption(parser):
#    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
#def cmdopt(request):
#    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='GridStatWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='GridStatWrapper')
        produtil.log.postmsg('grid_stat_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        logger = util.get_logger(config)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'grid_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------
def test_retrieve_var_name_levels():
    config = metplus_config()
    config.set('config', 'BOTH_VAR1_NAME', 'NAME1')
    config.set('config', 'BOTH_VAR1_LEVELS', 'LEVEL1')
    config.set('config', 'BOTH_VAR2_NAME', 'NAME2')
    config.set('config', 'BOTH_VAR2_LEVELS', 'LEVEL2')
    actual_vars = feature_util.retrieve_var_name_levels(config)
    expected_vars = [ ('NAME1', 'LEVEL1'), ('NAME2', 'LEVEL2')]
    print(f"ACTUAL: {actual_vars}")
    print(f"EXPECTED: {expected_vars}")
    assert(actual_vars == expected_vars)
