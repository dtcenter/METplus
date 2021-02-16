#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.grid_stat_wrapper import GridStatWrapper
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

# ------------------------ TESTS GO HERE --------------------------

# conf_dict is produtil config items set before creating grid_stat wrapper instance
# out_dict is grid_stat wrapper c_dict values set by initialization
@pytest.mark.parametrize(
    'conf_dict, out_dict', [
        # file window is get from obs window if not set
        ({ 'OBS_WINDOW_BEGIN' : -10,
            'OBS_WINDOW_END': 10},  {'OBS_FILE_WINDOW_BEGIN' : 0,
                                     'OBS_FILE_WINDOW_END' : 0}),
        # obs grid_stat window overrides obs window
        ({ 'OBS_GRID_STAT_WINDOW_BEGIN' : -10,
            'OBS_GRID_STAT_WINDOW_END': 10},  {'OBS_WINDOW_BEGIN' : -10,
                                       'OBS_WINDOW_END' : 10}),
        # obs grid_stat window overrides 1 item but not the other
        ({ 'OBS_GRID_STAT_WINDOW_BEGIN' : -10},  {'OBS_WINDOW_BEGIN' : -10,
                                                  'OBS_WINDOW_END' : 0}),
        # file window overrides file window
        ({ 'OBS_GRID_STAT_FILE_WINDOW_BEGIN' : -10,
            'OBS_GRID_STAT_FILE_WINDOW_END': 20,
            'OBS_GRID_STAT_WINDOW_END': 30},  {'OBS_FILE_WINDOW_BEGIN' : -10,
                                       'OBS_FILE_WINDOW_END' : 20}),
        # file window overrides file window begin but end uses obs window
        ({ 'OBS_GRID_STAT_FILE_WINDOW_BEGIN' : -10,
           'OBS_GRID_STAT_WINDOW_BEGIN' : -20,
            'OBS_GRID_STAT_WINDOW_END': 30},  {'OBS_FILE_WINDOW_BEGIN' : -10,
                                       'OBS_FILE_WINDOW_END' : 0}),

    ]
)

def test_window_variables_(metplus_config, conf_dict, out_dict):
    config = metplus_config()

    for key, value in conf_dict.items():
        config.set('config', key, value)
    
    gsw = GridStatWrapper(config)

    good = True
    for key, value in out_dict.items():
        if gsw.c_dict[key] != value:
            good = False

    assert(good == True)

