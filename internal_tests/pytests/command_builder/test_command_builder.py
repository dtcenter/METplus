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

    pcw = CommandBuilder(config, config_overrides=overrides)
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

    pcw = CommandBuilder(config, config_overrides=overrides)
    for key, expected_value in overrides.items():
        assert(pcw.config.getraw('config', key) == expected_value)

# dictionary items with values will be set in [test_section]
# items with value None will not be set, so it should use
# the value in [config], which is always 'default'
@pytest.mark.parametrize(
    'section_items', [
        # all values set in test_section
        ({'LOG_MET_VERBOSITY': '5',
          'CUSTOM_LOOP_LIST': 'a,b,c',
          'SKIP_TIMES': '"%H:12,18", "%Y%m%d:20200201"',
          'FAKE_TEMPLATE': '{valid?fmt=%Y%m%d%H}' }),
        # some values set in test_section, some not
        ({'LOG_MET_VERBOSITY': '5',
          'CUSTOM_LOOP_LIST': None,
          'SKIP_TIMES': '"%H:12,18", "%Y%m%d:20200201"',
          'FAKE_TEMPLATE': None }),
        # no values are set in test_section
        ({'FAKE_TEMPLATE': None}),
        ]
)
def test_override_by_instance(metplus_config, section_items):
    config = metplus_config()

    # set config variables to default
    for key in section_items:
        config.set('config', key, 'default')

    # set test_section variables to values
    config.add_section('test_section')
    for key, value in section_items.items():
        if value is not None:
            config.set('test_section', key, value)

    pcw = CommandBuilder(config, instance='test_section')
    for key, value in section_items.items():
        expected_value = 'default' if value is None else value
        assert(pcw.config.getraw('config', key) == expected_value)

@pytest.mark.parametrize(
    'filename, file_list, output_dir', [
        # write lists to staging dir
        ('my_ascii_file1', ['file1', 'file2', 'file3'], None),
        ('my_ascii_file2', ['file4', 'file5', 'file6'], None),
        ('my_ascii_file3', [], None),
        ('my_ascii_file1', ['file1', 'file2', 'file3'], 'write_list_test'),
        ('my_ascii_file2', ['file4', 'file5', 'file6'], 'write_list_test'),
        ('my_ascii_file3', [], 'write_list_test'),
    ]
)
def test_write_list_file(metplus_config, filename, file_list, output_dir):
    config = metplus_config()
    cbw = CommandBuilder(config)

    # use output_dir relative to OUTPUT_BASE if it is specified
    # otherwise use {STAGING_DIR}/file_lists
    if output_dir:
        output_dir = os.path.join(config.getdir('OUTPUT_BASE'),
                                  output_dir)
        check_dir = output_dir
    else:
        check_dir = os.path.join(config.getdir('STAGING_DIR'),
                                 'file_lists')

    check_file = os.path.join(check_dir, filename)
    # remove expected output file is it already exists
    if os.path.exists(check_file):
        os.remove(check_file)

    cbw.write_list_file(filename, file_list, output_dir=output_dir)

    # ensure file was written
    assert(os.path.exists(check_file))
    with open(check_file, 'r') as file_handle:
        lines = file_handle.readlines()

    # ensure number of lines written is 1 greater than provided list
    # to account for first line that contains 'file_list' text
    assert(len(lines) == len(file_list) + 1)

    # ensure content of file is as expected
    for actual_line, expected_line in zip(lines[1:], file_list):
        assert(actual_line.strip() == expected_line)

@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        ({}, ''),
        ({'DESCRIPTION': 'generic_desc'}, 'desc = "generic_desc";'),
        ({'GRID_STAT_DESCRIPTION': 'gs_desc'}, 'desc = "gs_desc";'),
        ({'DESCRIPTION': 'generic_desc',
          'GRID_STAT_DESCRIPTION': 'gs_desc'}, 'desc = "gs_desc";'),
        # same but with quotes around value
        ({'DESCRIPTION': '"generic_desc"'}, 'desc = "generic_desc";'),
        ({'GRID_STAT_DESCRIPTION': '"gs_desc"'}, 'desc = "gs_desc";'),
        ({'DESCRIPTION': '"generic_desc"',
          'GRID_STAT_DESCRIPTION': '"gs_desc"'}, 'desc = "gs_desc";'),
    ]
)
def test_handle_description(metplus_config, config_overrides, expected_value):
    config = metplus_config()

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    cbw = CommandBuilder(config)

    # set app_name to grid_stat for testing
    cbw.app_name = 'grid_stat'

    # create empty dictionary for testing
    c_dict = {}

    cbw.handle_description(c_dict)
    assert(c_dict.get('DESC', '') == expected_value)

@pytest.mark.parametrize(
    'input, output', [
        ('', 'NONE'),
        ('NONE', 'NONE'),
        ('FCST', 'FCST'),
        ('OBS', 'OBS'),
        ('G002', '"G002"'),
    ]
)
def test_format_regrid_to_grid(metplus_config, input, output):
    cbw = CommandBuilder(metplus_config())
    assert(cbw.format_regrid_to_grid(input) == output)

@pytest.mark.parametrize(
    'config_overrides, set_to_grid, expected_dict', [
        ({}, True, {}),
        ({}, False, {}),
        ({'APP_REGRID_TO_GRID': 'G002'},
         True,
         {'REGRID_TO_GRID': 'to_grid = "G002";'}),
        ({'APP_REGRID_TO_GRID': 'G002'},
         False,
         {}),
        ({'APP_REGRID_METHOD': 'BILIN'},
         True,
         {'REGRID_METHOD': 'method = BILIN;'}),
        ({'APP_REGRID_WIDTH': '2'},
         True,
         {'REGRID_WIDTH': 'width = 2;'}),
        ({'APP_REGRID_VLD_THRESH': '0.8'},
         True,
         {'REGRID_VLD_THRESH': 'vld_thresh = 0.8;'}),
        ({'APP_REGRID_SHAPE': 'CIRCLE'},
         True,
         {'REGRID_SHAPE': 'shape = CIRCLE;'}),
    ]
)
def test_handle_c_dict_regrid(metplus_config, config_overrides, set_to_grid,
                              expected_dict):
    config = metplus_config()

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    cbw = CommandBuilder(config)

    # set app_name to grid_stat for testing
    cbw.app_name = 'app'

    # create empty dictionary for testing
    c_dict = {}

    cbw.handle_c_dict_regrid(c_dict, set_to_grid=set_to_grid)
    assert(len(c_dict) == len(expected_dict))
    for key, value in expected_dict.items():
        assert(c_dict.get(key, '') == value)

@pytest.mark.parametrize(
    'c_dict_values, expected_output', [
        ({}, ''),
        ({'REGRID_TO_GRID': 'to_grid = FCST;',},
         'regrid = {to_grid = FCST;}'),
        ({'REGRID_METHOD': 'method = BILIN;',},
         'regrid = {method = BILIN;}'),
        ({'REGRID_WIDTH': 'width = 2;',},
         'regrid = {width = 2;}'),
        ({'REGRID_VLD_THRESH': 'vld_thresh = 0.8;',},
         'regrid = {vld_thresh = 0.8;}'),
        ({'REGRID_SHAPE': 'shape = CIRCLE;',},
         'regrid = {shape = CIRCLE;}'),
        ({'REGRID_TO_GRID': 'to_grid = FCST;',
          'REGRID_WIDTH': 'width = 2;',
          'REGRID_SHAPE': 'shape = CIRCLE;',},
         'regrid = {to_grid = FCST;width = 2;shape = CIRCLE;}'),
        ({'REGRID_TO_GRID': 'to_grid = FCST;',
          'REGRID_METHOD': 'method = BILIN;',
          'REGRID_WIDTH': 'width = 2;',
          'REGRID_VLD_THRESH': 'vld_thresh = 0.8;',
          'REGRID_SHAPE': 'shape = CIRCLE;',},
         'regrid = {to_grid = FCST;method = BILIN;width = 2;vld_thresh = 0.8;shape = CIRCLE;}'),
    ]
)
def test_get_regrid_dict(metplus_config, c_dict_values, expected_output):
    cbw = CommandBuilder(metplus_config())

    for key, value in c_dict_values.items():
        cbw.c_dict[key] = value

    assert(cbw.get_regrid_dict() == expected_output)
