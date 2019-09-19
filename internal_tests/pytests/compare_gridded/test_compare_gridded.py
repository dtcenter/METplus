#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime
import config_metplus
from compare_gridded_wrapper import CompareGriddedWrapper
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
def compare_gridded_wrapper():
    """! Returns a default GridStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    return CompareGriddedWrapper(config, config.logger)

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

def test_get_field_info_no_prob(key, value):
    w = compare_gridded_wrapper()
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
#  test_get_field_info_fcst_prob_grib
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

#        (['NAME', 'L0', ['gt3&&lt5'], '', 'FCST'],
#         ['{ name=\"PROB\"; level=\"L0\"; prob={ name=\"NAME\"; thresh_lo=3.0; thresh_hi=5.0 } }']),

        # fcst grib name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; prob=TRUE; cat_thresh=[==0.1]; }']),

        # obs name py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name=\"/some/script/name.py args /path/of/infile.txt\"; }']),

         ]
)

def test_get_field_info_fcst_prob_grib(key, value):
    w = compare_gridded_wrapper()
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['OBS_IS_PROB'] = False
    w.c_dict['FCST_INPUT_DATATYPE'] = 'GRIB'
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
def test_get_field_info_fcst_prob_netcdf(key, value):
    w = compare_gridded_wrapper()
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

