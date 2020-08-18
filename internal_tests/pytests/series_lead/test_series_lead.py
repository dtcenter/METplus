#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

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


# ------------------------ TESTS GO HERE --------------------------
def test_retrieve_var_name_levels(metplus_config):
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
