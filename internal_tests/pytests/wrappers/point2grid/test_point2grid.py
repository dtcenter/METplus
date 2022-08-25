#!/usr/bin/env python3

import pytest
import datetime

from metplus.wrappers.point2grid_wrapper import Point2GridWrapper
from metplus.util import time_util


def p2g_wrapper(metplus_config):
    """! Returns a default Point2Grid with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return Point2GridWrapper(config)


@pytest.mark.wrapper
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

    wrap.c_dict['QC_FLAGS'] = 1

    expected_args = ['-qc 1',
                     '-method UW_MEAN',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     '-prob_cat_thresh 1',
                     '-vld_thresh 0.5',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 5 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['ADP'] = 'test.nc'

    expected_args = ['-qc 1',
                     '-adp test.nc',
                     '-method UW_MEAN',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     '-prob_cat_thresh 1',
                     '-vld_thresh 0.5',
                     ]

    wrap.set_command_line_arguments(time_info)
    if wrap.args != expected_args:
        test_passed = False
        print("Test 6 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

<<<<<<< HEAD:internal_tests/pytests/wrappers/point2grid/test_point2grid.py
    assert test_passed
=======

    assert(test_passed)
>>>>>>> origin:internal_tests/pytests/point2grid/test_point2grid.py
