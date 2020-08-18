#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.compare_gridded_wrapper import CompareGriddedWrapper
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
def compare_gridded_wrapper(metplus_config):
    """! Returns a default GridStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    return CompareGriddedWrapper(config)

# ------------------------ TESTS GO HERE --------------------------

# ------------------------
#  test_get_field_info_no_prob
# ------------------------
# key is a list of inputs to get_field_info: name, level, thresh_list, extras, and data type (FCST/OBS)
# value is a list of field info lists that are generated from the keys
@pytest.mark.parametrize(
    'key, value', [
        # forecast name and level
        (['NAME', 'L0', [], '', 'FCST'],
         ['{ name=\"NAME\"; level=\"L0\"; }']),

        # forecast name only
        (['NAME', '', [], '', 'FCST'],
         ['{ name=\"NAME\"; }']),

        # forecast name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3,<=5 ]; }']),

        # forecast name level thresh extra
        (['NAME', 'L0', ['gt3', '<=5'], 'extra=val;', 'FCST'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3,<=5 ]; extra=val; }']),

        # forecast name only py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; }']),

        # obs name and level
        (['NAME', 'L0', [], '', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; }']),

        # obs name only
        (['NAME', '', [], '', 'OBS'],
         ['{ name=\"NAME\"; }']),

        # obs name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3,<=5 ]; }']),

        # obs name level thresh extra
        (['NAME', 'L0', ['gt3', '<=5'], 'extra=val;', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3,<=5 ]; extra=val; }']),

        # obs name only py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; }']),

    ]
)

def test_get_field_info_no_prob(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = False
    w.c_dict['OBS_IS_PROB'] = False

    field_dict = {'v_name' : key[0],
                  'v_level' : key[1],
                  'v_thresh' : key[2],
                  'v_extra' : key[3],
                  'd_type' : key[4],
                  }

    fields = w.get_field_info(**field_dict)
    assert(fields == value)

# ------------------------
#  test_get_field_info_fcst_prob_grib_pds
#   - forecast is grib probabalistic but observation is not
# ------------------------
# key is a list of inputs to get_field_info: name, level, thresh_list, extras, and data type (FCST/OBS)
# value is a list of field info lists that are generated from the keys
@pytest.mark.parametrize(
    'key, value', [
        # forecast grib name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name=\"PROB\"; level=\"L0\"; prob={ name=\"NAME\"; thresh_lo=3.0; } cat_thresh=[==0.1]; }',
          '{ name=\"PROB\"; level=\"L0\"; prob={ name=\"NAME\"; thresh_hi=5.0; } cat_thresh=[==0.1]; }']),

        # obs grib name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3 ]; }',
          '{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ <=5 ]; }']),

        (['NAME', 'L0', ['gt3&&lt5'], '', 'FCST'],
         ['{ name=\"PROB\"; level=\"L0\"; prob={ name=\"NAME\"; thresh_lo=3.0; thresh_hi=5.0; } cat_thresh=[==0.1]; }']),

        # fcst grib name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; prob=TRUE; cat_thresh=[==0.1]; }']),

        # obs name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; }']),

         ]
)
def test_get_field_info_fcst_prob_grib_pds(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['OBS_IS_PROB'] = False
    w.c_dict['FCST_INPUT_DATATYPE'] = 'GRIB'
    w.c_dict['FCST_PROB_IN_GRIB_PDS'] = True
    w.c_dict['FCST_PROB_THRESH'] = '==0.1'

    field_dict = {'v_name' : key[0],
                  'v_level' : key[1],
                  'v_thresh' : key[2],
                  'v_extra' : key[3],
                  'd_type' : key[4],
                  }

    fields = w.get_field_info(**field_dict)
    assert(fields == value)

# ------------------------
#  test_get_field_info_fcst_prob_grib_non_pds
#   - forecast is grib probabalistic but observation is not
# ------------------------
# key is a list of inputs to get_field_info: name, level, thresh_list, extras, and data type (FCST/OBS)
# value is a list of field info lists that are generated from the keys
@pytest.mark.parametrize(
    'key, value', [
        # forecast grib name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name=\"NAME\"; level=\"L0\"; prob=TRUE; cat_thresh=[==0.1]; }',
          '{ name=\"NAME\"; level=\"L0\"; prob=TRUE; cat_thresh=[==0.1]; }']),

        # obs grib name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3 ]; }',
          '{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ <=5 ]; }']),

        (['NAME', 'L0', ['gt3&&lt5'], '', 'FCST'],
         ['{ name=\"NAME\"; level=\"L0\"; prob=TRUE; cat_thresh=[==0.1]; }']),

        # fcst grib name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; prob=TRUE; cat_thresh=[==0.1]; }']),

        # obs name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; }']),

         ]
)
def test_get_field_info_fcst_prob_grib_non_pds(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['OBS_IS_PROB'] = False
    w.c_dict['FCST_INPUT_DATATYPE'] = 'GRIB'
    w.c_dict['FCST_PROB_IN_GRIB_PDS'] = False
    w.c_dict['FCST_PROB_THRESH'] = '==0.1'

    field_dict = {'v_name' : key[0],
                  'v_level' : key[1],
                  'v_thresh' : key[2],
                  'v_extra' : key[3],
                  'd_type' : key[4],
                  }
    
    fields = w.get_field_info(**field_dict)
    assert(fields == value)

    # ------------------------
#  test_get_field_info_fcst_prob
#   - forecast is probabalistic but observation is not
# ------------------------
# key is a list of inputs to get_field_info: name, level, thresh_list, extras, and data type (FCST/OBS)
# value is a list of field info lists that are generated from the keys
@pytest.mark.parametrize(
    'key, value', [

        # forecast netcdf name level
        (['NAME_gt3', 'L0', [], '', 'FCST'],
         ['{ name=\"NAME_gt3\"; level=\"L0\"; prob=TRUE; }']),

        # obs netcdf name level thresh
        (['NAME', 'L0', ['gt3'], '', 'OBS'],
         ['{ name=\"NAME\"; level=\"L0\"; cat_thresh=[ gt3 ]; }']),
         ]
)
def test_get_field_info_fcst_prob_netcdf(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['OBS_IS_PROB'] = False
    w.c_dict['FCST_INPUT_DATATYPE'] = 'NETCDF'

    field_dict = {'v_name' : key[0],
                  'v_level' : key[1],
                  'v_thresh' : key[2],
                  'v_extra' : key[3],
                  'd_type' : key[4],
                  }
    
    fields = w.get_field_info(**field_dict)
    assert(fields == value)

@pytest.mark.parametrize(
    'win, app_win, file_win, app_file_win, win_value, file_win_value', [
        ([1, 2, 3, 4, 2, 4 ]),
        ([1, 2, 3, None, 2, 3]),
        ([1, 2, None, None, 2, 0]),
        ([1, None, None, None, 1, 0]),
        ([None, None, None, None, 0, 0]),
        ([1, None, 3, 4, 1, 4 ]),
        ([1, None, 3, 4, 1, 4 ]),
         ]
)
def test_handle_window_once(metplus_config, win, app_win, file_win, app_file_win, win_value, file_win_value):
    cgw = compare_gridded_wrapper(metplus_config)
    config = cgw.config

    if win is not None:
        config.set('config', 'FCST_WINDOW_BEGIN', win)

    if app_win is not None:
        config.set('config', 'FCST_APP_NAME_WINDOW_BEGIN', app_win)

    if file_win is not None:
        config.set('config', 'FCST_FILE_WINDOW_BEGIN', file_win)

    if app_file_win is not None:
        config.set('config', 'FCST_APP_NAME_FILE_WINDOW_BEGIN', app_file_win)

    c_dict = {}
    cgw.handle_window_once(c_dict, 'FCST', 'BEGIN', 'APP_NAME')
    assert(c_dict['FCST_WINDOW_BEGIN'] == win_value and \
           c_dict['FCST_FILE_WINDOW_BEGIN'] == file_win_value)
