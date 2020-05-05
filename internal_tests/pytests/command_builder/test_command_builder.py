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
from command_builder import CommandBuilder
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
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    # Read in the configuration object CONFIG
    config = config_metplus.setup(util.baseinputconfs)
    util.get_logger(config)
    return config


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_find_data_no_dated
# ------------------------
@pytest.mark.parametrize(
    'data_type', [
        ("FCST_"),
        ("OBS_"),
        (""),
        ("MASK_"),
        ]
)
def test_find_data_no_dated(data_type):
    config = metplus_config()
    
    pcw = CommandBuilder(config, config.logger)
    v = {}
    v['fcst_level'] = "6"
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    
    pcw.c_dict[f'{data_type}FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict[f'{data_type}FILE_WINDOW_END'] = 3600
    pcw.c_dict[f'{data_type}INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict[f'{data_type}INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file = pcw.find_data(time_info, v, data_type)
    assert(obs_file == pcw.c_dict[f'{data_type}INPUT_DIR']+'/20180201_0045')


# if the input dir/template combination is not a path, then find_data should just return that string
# i.e. for a grid definition G003, input dir is empty and input template is G003
@pytest.mark.parametrize(
    'data_type', [
        ("FCST_"),
        ("OBS_"),
        (""),
        ("MASK_"),
        ]
)
def test_find_data_not_a_path(data_type):
    config = metplus_config()
    
    pcw = CommandBuilder(config, config.logger)
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    
    pcw.c_dict[f'{data_type}FILE_WINDOW_BEGIN'] = 0
    pcw.c_dict[f'{data_type}FILE_WINDOW_END'] = 0
    pcw.c_dict[f'{data_type}INPUT_DIR'] = ''
    pcw.c_dict[f'{data_type}INPUT_TEMPLATE'] = 'G003'
    obs_file = pcw.find_data(time_info, var_info=None, data_type=data_type)
    assert(obs_file == 'G003')

def test_find_obs_no_dated():
    config = metplus_config()

    pcw = CommandBuilder(config, config.logger)
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)

    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE') + "/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file = pcw.find_obs(time_info, v)
    assert (obs_file == pcw.c_dict['OBS_INPUT_DIR'] + '/20180201_0045')

def test_find_obs_dated():
    config = metplus_config()
    
    pcw = CommandBuilder(config, config.logger)
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

def test_find_obs_offset():
    config = metplus_config()

    pcw = CommandBuilder(config, config.logger)
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)

    pcw.c_dict['OFFSETS'] = [2]
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE') + "/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file, time_info = pcw.find_obs_offset(time_info, v)
    assert (obs_file == pcw.c_dict['OBS_INPUT_DIR'] + '/20180201_0045' and time_info['offset'] == 7200 )


def test_find_obs_dated_previous_day():
    config = metplus_config()
    
    pcw = CommandBuilder(config, config.logger)
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
    config = metplus_config()
    
    pcw = CommandBuilder(config, config.logger)
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
