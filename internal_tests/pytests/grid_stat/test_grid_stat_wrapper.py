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
from grid_stat_wrapper import GridStatWrapper
from config_wrapper import ConfigWrapper
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
def grid_stat_wrapper():
    """! Returns a default GridStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    return GridStatWrapper(config, config.logger)

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
        config = config_metplus.setup()
        logger = util.get_logger(config)
        config = ConfigWrapper(config, logger)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'grid_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_find_obs_no_dated
# ------------------------
def test_find_obs_no_dated():
    pcw = grid_stat_wrapper()
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file = pcw.find_obs(time_info, v)
    assert(obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180201_0045')


def test_find_obs_dated():
    pcw = grid_stat_wrapper()
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)

    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    obs_file = pcw.find_obs(time_info, v)
    assert(obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180201/20180201_0013')

def test_find_obs_dated_previous_day():
    pcw = grid_stat_wrapper()
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)

    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 0
    obs_file = pcw.find_obs(time_info, v)
    assert(obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180131/20180131_2345')

def test_find_obs_dated_next_day():
    pcw = grid_stat_wrapper()
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802012345", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = 0
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    obs_file = pcw.find_obs(time_info, v)
    assert(obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180202/20180202_0013')

# conf_dict is produtil config items set before creating grid_stat wrapper instance
# out_dict is grid_stat wrapper c_dict values set by initialization
@pytest.mark.parametrize(
    'conf_dict, out_dict', [
        # file window is get from obs window if not set
        ({ 'OBS_WINDOW_BEGIN' : -10,
            'OBS_WINDOW_END': 10},  {'OBS_FILE_WINDOW_BEGIN' : -10,
                                     'OBS_FILE_WINDOW_END' : 10}),
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
                                       'OBS_FILE_WINDOW_END' : 30}),

    ]
)

def test_window_variables_(conf_dict, out_dict):
    conf = metplus_config()
    logger = logging.getLogger("dummy")

    for key, value in conf_dict.items():
        conf.set('config', key, value)
    
    gsw = GridStatWrapper(conf, logger)

    good = True
    for key, value in out_dict.items():
        if gsw.c_dict[key] != value:
            good = False

    assert(good == True)

