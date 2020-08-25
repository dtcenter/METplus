#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime

from metplus.wrappers.point2grid_wrapper import Point2GridWrapper
from metplus.util import met_util as util
from metplus.util import time_util

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
def p2g_wrapper(metplus_config):
    """! Returns a default Point2Grid with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return Point2GridWrapper(config)

# ------------------------ TESTS GO HERE --------------------------


def test_set_command_line_arguments(metplus_config):
    test_passed = True
    wrap = p2g_wrapper(metplus_config)

    input_dict = {'valid': datetime.datetime.strptime("202003050000", '%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)


    wrap.c_dict['REGRID_METHOD'] = 'UW_MEAN'

    expected_args = ['-method UW_MEAN',]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 0 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['GAUSSIAN_DX'] = 2

    expected_args = ['-method UW_MEAN',
                     '-gaussian_dx 2',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 1 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['PROB_CAT_THRESH'] = 1

    expected_args = ['-method UW_MEAN',
                     '-gaussian_dx 2',
                     '-prob_cat_thresh 1',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 2 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['GAUSSIAN_RADIUS'] = 3

    expected_args = ['-method UW_MEAN',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     '-prob_cat_thresh 1',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 3 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['VLD_THRESH'] = .5

    expected_args = ['-method UW_MEAN',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     '-prob_cat_thresh 1',
                     '-vld_thresh 0.5',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 4 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    assert(test_passed)
