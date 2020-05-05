#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime
import config_metplus
from regrid_data_plane_wrapper import Point2GridWrapper
import met_util as util
import time_util

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
def p2g_wrapper():
    """! Returns a default Point2Grid with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return Point2GridWrapper(config, config.logger)

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    config = config_metplus.setup(util.baseinputconfs)
    util.get_logger(config)
    return config


# ------------------------ TESTS GO HERE --------------------------


def test_set_command_line_arguments():
    test_passed = True
    wrap = p2g()

    wrap.c_dict['METHOD'] = 'UW_MEAN'
    expected_args = ['-method UW_MEAN',]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 0 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.c_dict['GAUSSIAN_DX'] = 2

    expected_args = ['-method UW_MEAN',
                     '-gaussian_dx 2',
                     ]

    wrap.args.clear()

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 1 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['PROB_CAT_THRESH'] = 1

    expected_args = ['-method UW_MEAN',
                     '-prob_cat_thresh 1',
                     '-gaussian_dx 2',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 2 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['GAUSSIAN_RADIUS'] = 3

    expected_args = ['-method UW_MEAN',
                     '-prob_cat_thresh 1',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 3 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['VLD_THRESH'] = .5

    expected_args = ['-method UW_MEAN',
                     '-prob_cat_thresh 1',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     '-vld_thresh .5',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 4 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    assert(test_passed)
