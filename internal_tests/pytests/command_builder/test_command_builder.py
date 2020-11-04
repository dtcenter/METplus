#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime
from metplus.wrappers.command_builder import CommandBuilder
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
def test_find_data_no_dated(metplus_config, data_type):
    config = metplus_config()

    pcw = CommandBuilder(config)
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
def test_find_data_not_a_path(metplus_config, data_type):
    config = metplus_config()
    
    pcw = CommandBuilder(config)
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

def test_find_obs_no_dated(metplus_config):
    config = metplus_config()

    pcw = CommandBuilder(config)
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

def test_find_obs_dated(metplus_config):
    config = metplus_config()
    
    pcw = CommandBuilder(config)
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

@pytest.mark.parametrize(
    'offsets, expected_file, offset_seconds', [
        ([2], '14z.prepbufr.tm02.20200201', 7200),
        ([6, 2], '18z.prepbufr.tm06.20200201', 21600),
        ([2, 6], '14z.prepbufr.tm02.20200201', 7200),
        ([3, 7, 2, 6], '14z.prepbufr.tm02.20200201', 7200),
        ([3, 7], None, None),
        ([], None, None),
        ]
)
def test_find_obs_offset(metplus_config, offsets, expected_file, offset_seconds):
    config = metplus_config()

    pcw = CommandBuilder(config)
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2020020112", '%Y%m%d%H')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)

    pcw.c_dict['OFFSETS'] = offsets
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE') + "/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{da_init?fmt=%2H}z.prepbufr.tm{offset?fmt=%2H}.{da_init?fmt=%Y%m%d}"
    obs_file, time_info = pcw.find_obs_offset(time_info, v)

    print(f"OBSFILE: {obs_file}")
    print(f"EXPECTED FILE: {expected_file}")

    if expected_file is None:
        assert(not obs_file)
    else:
        assert (os.path.basename(obs_file) == expected_file and time_info['offset'] == offset_seconds)

def test_find_obs_dated_previous_day(metplus_config):
    config = metplus_config()
    
    pcw = CommandBuilder(config)
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

def test_find_obs_dated_next_day(metplus_config):
    config = metplus_config()
    
    pcw = CommandBuilder(config)
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

@pytest.mark.parametrize(
    'overrides, c_dict', [
        ({'LOG_MET_VERBOSITY': '5', }, # string
         {'VERBOSITY': '5', }),
        ({'CUSTOM_LOOP_LIST': 'a,b,c', }, # list
         {'CUSTOM_LOOP_LIST': ['a', 'b', 'c'], }),
        ({'SKIP_TIMES': '"%H:12,18", "%Y%m%d:20200201"', },  # dict
         {'SKIP_TIMES': {'%H': ['12', '18'],
                         '%Y%m%d': ['20200201'], }}),
        ]
)
def test_override_config_in_c_dict(metplus_config, overrides, c_dict):
    config = metplus_config()

    pcw = CommandBuilder(config, overrides)
    for key, expected_value in c_dict.items():
        assert(pcw.c_dict.get(key) == expected_value)

@pytest.mark.parametrize(
    'overrides', [
        ({'LOG_MET_VERBOSITY': '5', }),
        ({'CUSTOM_LOOP_LIST': 'a,b,c', }),
        ({'SKIP_TIMES': '"%H:12,18", "%Y%m%d:20200201"', }),
        ({'FAKE_TEMPLATE': '{valid?fmt=%Y%m%d%H}', }),
        ]
)
def test_override_config(metplus_config, overrides):
    config = metplus_config()

    pcw = CommandBuilder(config, overrides)
    for key, expected_value in overrides.items():
        assert(pcw.config.getraw('config', key) == expected_value)