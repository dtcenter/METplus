#!/usr/bin/env python3

import pytest
from unittest import mock

import os
import datetime
import metplus.wrappers.command_builder as cb_wrapper
from metplus.wrappers.command_builder import CommandBuilder
import metplus.util.run_util
from metplus.util import ti_calculate, add_field_info_to_time_info


def get_data_dir(config):
    return os.path.join(config.getdir('METPLUS_BASE'),
                        'internal', 'tests', 'data', 'obs')


@pytest.mark.parametrize(
    'data_type,allow_multiple', [
        ("FCST_", False),
        ("OBS_", False),
        ("", False),
        ("MASK_", False),
        ("FCST_", True),
        ("OBS_", True),
        ("", True),
        ("MASK_", True),
    ]
)
@pytest.mark.wrapper
def test_find_data_no_dated(metplus_config, data_type, allow_multiple):
    config = metplus_config

    pcw = CommandBuilder(config)
    var_info = {}
    var_info['fcst_level'] = "6"
    var_info['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)
    
    pcw.c_dict[f'{data_type}FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict[f'{data_type}FILE_WINDOW_END'] = 3600
    pcw.c_dict[f'{data_type}INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict[f'{data_type}INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    pcw.c_dict[f'ALLOW_MULTIPLE_FILES'] = allow_multiple
    add_field_info_to_time_info(time_info, var_info)
    obs_file = pcw.find_data(time_info, data_type)
    assert not isinstance(obs_file, list)
    assert obs_file == pcw.c_dict[f'{data_type}INPUT_DIR']+'/20180201_0045'


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
@pytest.mark.wrapper
def test_find_data_not_a_path(metplus_config, data_type):
    config = metplus_config
    
    pcw = CommandBuilder(config)
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)
    
    pcw.c_dict[f'{data_type}FILE_WINDOW_BEGIN'] = 0
    pcw.c_dict[f'{data_type}FILE_WINDOW_END'] = 0
    pcw.c_dict[f'{data_type}INPUT_DIR'] = ''
    pcw.c_dict[f'{data_type}INPUT_TEMPLATE'] = 'G003'
    obs_file = pcw.find_data(time_info, data_type=data_type)
    assert obs_file == 'G003'


@pytest.mark.wrapper
def test_find_obs_no_dated(metplus_config):
    config = metplus_config

    pcw = CommandBuilder(config)
    var_info = {}
    var_info['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)

    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    add_field_info_to_time_info(time_info, var_info)
    obs_file = pcw.find_obs(time_info)
    assert obs_file == pcw.c_dict['OBS_INPUT_DIR'] + '/20180201_0045'


@pytest.mark.wrapper
def test_find_obs_dated(metplus_config):
    config = metplus_config
    
    pcw = CommandBuilder(config)
    var_info = {}
    var_info['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)

    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    add_field_info_to_time_info(time_info, var_info)
    obs_file = pcw.find_obs(time_info)
    assert obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180201/20180201_0013'


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
@pytest.mark.wrapper
def test_find_obs_offset(metplus_config, offsets, expected_file, offset_seconds):
    config = metplus_config

    pcw = CommandBuilder(config)
    var_info = {}
    var_info['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2020020112", '%Y%m%d%H')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)

    pcw.c_dict['OFFSETS'] = offsets
    pcw.c_dict['OBS_INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{da_init?fmt=%H}z.prepbufr.tm{offset?fmt=%2H}.{da_init?fmt=%Y%m%d}"
    add_field_info_to_time_info(time_info, var_info)
    obs_file, time_info = pcw.find_obs_offset(time_info)

    print(f"OBSFILE: {obs_file}")
    print(f"EXPECTED FILE: {expected_file}")

    if expected_file is None:
        assert not obs_file
    else:
        assert (os.path.basename(obs_file) == expected_file and
                time_info['offset'] == offset_seconds)


@pytest.mark.wrapper
def test_find_obs_dated_previous_day(metplus_config):
    config = metplus_config
    
    pcw = CommandBuilder(config)
    var_info = {}
    var_info['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)

    pcw.c_dict['OBS_INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 0
    add_field_info_to_time_info(time_info, var_info)
    obs_file = pcw.find_obs(time_info)
    assert obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180131/20180131_2345'


@pytest.mark.wrapper
def test_find_obs_dated_next_day(metplus_config):
    config = metplus_config
    
    pcw = CommandBuilder(config)
    var_info = {
        'obs_level': "6"
    }
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802012345", '%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)

    pcw.c_dict['OBS_INPUT_DIR'] = get_data_dir(pcw.config)
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = 0
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    add_field_info_to_time_info(time_info, var_info)
    obs_file = pcw.find_obs(time_info)
    assert obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180202/20180202_0013'


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
@pytest.mark.wrapper
def test_override_by_instance(metplus_config, section_items):
    config = metplus_config

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
        assert pcw.config.getraw('config', key) == expected_value


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
@pytest.mark.wrapper
def test_write_list_file(metplus_config, filename, file_list, output_dir):
    config = metplus_config
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
    assert os.path.exists(check_file)
    with open(check_file, 'r') as file_handle:
        lines = file_handle.readlines()

    # ensure number of lines written is 1 greater than provided list
    # to account for first line that contains 'file_list' text
    assert len(lines) == len(file_list) + 1

    # ensure content of file is as expected
    for actual_line, expected_line in zip(lines[1:], file_list):
        assert actual_line.strip() == expected_line


@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        ({}, ''),
        ({'DESC': 'generic_desc'}, 'desc = "generic_desc";'),
        ({'GRID_STAT_DESC': 'gs_desc'}, 'desc = "gs_desc";'),
        ({'DESC': 'generic_desc',
          'GRID_STAT_DESC': 'gs_desc'}, 'desc = "gs_desc";'),
        # same but with quotes around value
        ({'DESC': '"generic_desc"'}, 'desc = "generic_desc";'),
        ({'GRID_STAT_DESC': '"gs_desc"'}, 'desc = "gs_desc";'),
        ({'DESC': '"generic_desc"',
          'GRID_STAT_DESC': '"gs_desc"'}, 'desc = "gs_desc";'),
    ]
)
@pytest.mark.wrapper
def test_handle_description(metplus_config, config_overrides, expected_value):
    config = metplus_config

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    cbw = CommandBuilder(config)

    # set app_name to grid_stat for testing
    cbw.app_name = 'grid_stat'

    cbw.handle_description()
    assert cbw.env_var_dict.get('METPLUS_DESC', '') == expected_value


@pytest.mark.parametrize(
    'config_overrides, set_to_grid, expected_dict', [
        ({}, True, {'REGRID_TO_GRID': 'NONE'}),
        ({}, False, {}),
        ({'APP_REGRID_TO_GRID': 'G002'},
         True,
         {'REGRID_TO_GRID': '"G002"'}),
        ({'APP_REGRID_TO_GRID': 'G002'},
         False,
         {}),
        ({'APP_REGRID_METHOD': 'BILIN'},
         True,
         {'REGRID_TO_GRID': 'NONE'}),
        ({'APP_REGRID_WIDTH': '2'},
         True,
         {'REGRID_TO_GRID': 'NONE'}),
        ({'APP_REGRID_VLD_THRESH': '0.8'},
         True,
         {'REGRID_TO_GRID': 'NONE'}),
        ({'APP_REGRID_SHAPE': 'CIRCLE'},
         True,
         {'REGRID_TO_GRID': 'NONE'}),
    ]
)
@pytest.mark.wrapper
def test_handle_regrid_old(metplus_config, config_overrides, set_to_grid,
                           expected_dict):
    config = metplus_config

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    cbw = CommandBuilder(config)

    # set app_name to grid_stat for testing
    cbw.app_name = 'app'

    # create empty dictionary for testing
    c_dict = {}

    cbw.handle_regrid(c_dict, set_to_grid=set_to_grid)

    assert len(c_dict) == len(expected_dict)
    for key, value in expected_dict.items():
        assert c_dict.get(key, '') == value


@pytest.mark.parametrize(
    'config_overrides, expected_output', [
        ({}, ''),
        ({'APP_REGRID_TO_GRID': 'FCST',},
         'regrid = {to_grid = FCST;}'),
        ({'APP_REGRID_METHOD': 'BILIN',},
         'regrid = {method = BILIN;}'),
        ({'APP_REGRID_WIDTH': '2',},
         'regrid = {width = 2;}'),
        ({'APP_REGRID_VLD_THRESH': '0.8',},
         'regrid = {vld_thresh = 0.8;}'),
        ({'APP_REGRID_SHAPE': 'CIRCLE',},
         'regrid = {shape = CIRCLE;}'),
        ({'APP_REGRID_TO_GRID': 'FCST',
          'APP_REGRID_WIDTH': '2',
          'APP_REGRID_SHAPE': 'CIRCLE',},
         'regrid = {to_grid = FCST;width = 2;shape = CIRCLE;}'),
        ({'APP_REGRID_TO_GRID': 'FCST',
          'APP_REGRID_METHOD': 'BILIN',
          'APP_REGRID_WIDTH': '2',
          'APP_REGRID_VLD_THRESH': '0.8',
          'APP_REGRID_SHAPE': 'CIRCLE',},
         ('regrid = {to_grid = FCST;method = BILIN;width = 2;'
          'vld_thresh = 0.8;shape = CIRCLE;}')),
    ]
)
@pytest.mark.wrapper
def test_handle_regrid_new(metplus_config, config_overrides, expected_output):
    config = metplus_config

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    cbw = CommandBuilder(config)

    # set app_name to grid_stat for testing
    cbw.app_name = 'app'

    cbw.handle_regrid(cbw.c_dict)
    assert cbw.env_var_dict['METPLUS_REGRID_DICT'] == expected_output


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,remove_quotes,expected_output', [
        # var is set, use quotes
        ('TEST_STRING_1', 'test_string_1', None,
         False, 'test_string_1 = "value_1";'),
        # var is set, remove quotes
        ('TEST_STRING_1', 'test_string_1', None,
         True, 'test_string_1 = value_1;'),
        # var is not set
        ('TEST_STRING_2', 'test_string_2', None,
         False, ''),
        # var is set, use quotes, set c_dict key
        ('TEST_STRING_1', 'test_string_1', 'the_key',
         False, 'test_string_1 = "value_1";'),
        # var is set, remove quotes, set c_dict key
        ('TEST_STRING_1', 'test_string_1', 'the_key',
         True, 'test_string_1 = value_1;'),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_string(metplus_config, mp_config_name, met_config_name,
                               c_dict_key, remove_quotes, expected_output):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_STRING_1', 'value_1')

    extra_args = {}
    if remove_quotes:
        extra_args['remove_quotes'] = True

    key = c_dict_key
    if key is None:
        key = met_config_name
    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       data_type='string',
                       env_var_name=key,
                       metplus_configs=[mp_config_name],
                       extra_args=extra_args)

    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,uppercase,expected_output, is_ok', [
        # var is set to True, not uppercase
        ('TEST_BOOL_1', 'test_bool_1', None,
         False, 'test_bool_1 = True;', True),
        # var is set to True, uppercase
        ('TEST_BOOL_1', 'test_bool_1', None,
         True, 'test_bool_1 = TRUE;', True),
        # var is not set
        ('TEST_BOOL_2', 'test_bool_2', None,
         False, '', True),
        # var is set to False, not uppercase
        ('TEST_BOOL_3', 'test_bool_3', None,
         False, 'test_bool_3 = False;', True),
        # var is set to False, uppercase
        ('TEST_BOOL_3', 'test_bool_3', None,
         True, 'test_bool_3 = FALSE;', True),
        # var is set, not uppercase, set c_dict key
        ('TEST_BOOL_1', 'test_bool_1', 'the_key',
         False, 'test_bool_1 = True;', True),
        # var is set, uppercase, set c_dict key
        ('TEST_BOOL_1', 'test_bool_1', 'the_key',
         True, 'test_bool_1 = TRUE;', True),
        # var is set but not a valid boolean
        ('TEST_BOOL_4', 'test_bool_4', None,
         True, '', False),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_bool(metplus_config, mp_config_name, met_config_name,
                             c_dict_key, uppercase, expected_output, is_ok):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_BOOL_1', True)
    cbw.config.set('config', 'TEST_BOOL_3', False)
    cbw.config.set('config', 'TEST_BOOL_4', 'chicken')

    extra_args = {}
    if not uppercase:
        extra_args['uppercase'] = False

    key = c_dict_key
    if key is None:
        key = met_config_name
    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       data_type='bool',
                       env_var_name=key,
                       metplus_configs=[mp_config_name],
                       extra_args=extra_args)

    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output
    assert cbw.isOK == is_ok


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,expected_output,is_ok', [
        # var is set to positive int
        ('TEST_INT_1', 'test_int_1', None,
         'test_int_1 = 7;', True),
        # var is not set
        ('TEST_INT_2', 'test_int_2', None,
         '', True),
        # var is set to negative int
        ('TEST_INT_3', 'test_int_3', None,
         'test_int_3 = -4;', True),
        # var is set, set c_dict key
        ('TEST_INT_1', 'test_int_1', 'the_key',
         'test_int_1 = 7;', True),
        # var is set but not a valid int
        ('TEST_INT_4', 'test_int_4', None,
         '', False),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_int(metplus_config, mp_config_name, met_config_name,
                             c_dict_key, expected_output, is_ok):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_INT_1', 7)
    cbw.config.set('config', 'TEST_INT_3', -4)
    cbw.config.set('config', 'TEST_INT_4', 'chicken')

    key = c_dict_key
    if key is None:
        key = met_config_name
    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       data_type='int',
                       env_var_name=key,
                       metplus_configs=[mp_config_name])

    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output
    assert cbw.isOK == is_ok


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,expected_output,is_ok', [
        # var is set to float
        ('TEST_FLOAT_1', 'test_float_1', None,
         'test_float_1 = 7.0;', True),
        # var is not set
        ('TEST_FLOAT_2', 'test_float_2', None,
         '', True),
        # var is set to int
        ('TEST_FLOAT_3', 'test_float_3', None,
         'test_float_3 = 4.0;', True),
        # var is set, set c_dict key
        ('TEST_FLOAT_1', 'test_float_1', 'the_key',
         'test_float_1 = 7.0;', True),
        # var is set but not a valid int
        ('TEST_FLOAT_4', 'test_float_4', None,
         '', False),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_float(metplus_config, mp_config_name, met_config_name,
                             c_dict_key, expected_output, is_ok):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_FLOAT_1', 7.0)
    cbw.config.set('config', 'TEST_FLOAT_3', 4)
    cbw.config.set('config', 'TEST_FLOAT_4', 'chicken')

    key = c_dict_key
    if key is None:
        key = met_config_name
    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       data_type='float',
                       env_var_name=key,
                       metplus_configs=[mp_config_name])

    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output
    assert cbw.isOK == is_ok


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,expected_output,is_ok', [
        # var is set to alphabet threshold
        ('TEST_THRESH_1', 'test_thresh_1', None,
         'test_thresh_1 = gt74;', True),
        # var is not set
        ('TEST_THRESH_2', 'test_thresh_2', None,
         '', True),
        # var is set to symbol threshold
        ('TEST_THRESH_3', 'test_thresh_3', None,
         'test_thresh_3 = >=74.4;', True),
        # var is set, set c_dict key
        ('TEST_THRESH_1', 'test_thresh_1', 'the_key',
         'test_thresh_1 = gt74;', True),
        # var is set but not a valid threshold
        ('TEST_THRESH_4', 'test_thresh_4', None,
         '', False),
        # var is set to complex threshold
        ('TEST_THRESH_5', 'test_thresh_5', None,
         'test_thresh_5 = >CDP40&&<=CDP50;', True),
        # var is set to NA
        ('TEST_THRESH_6', 'test_thresh_6', None,
         'test_thresh_6 = NA;', True),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_thresh(metplus_config, mp_config_name, met_config_name,
                               c_dict_key, expected_output, is_ok):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_THRESH_1', 'gt74')
    cbw.config.set('config', 'TEST_THRESH_3', '>=74.4')
    cbw.config.set('config', 'TEST_THRESH_4', 'chicken')
    cbw.config.set('config', 'TEST_THRESH_5', '>CDP40&&<=CDP50')
    cbw.config.set('config', 'TEST_THRESH_6', 'NA')

    key = c_dict_key
    if key is None:
        key = met_config_name
    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       env_var_name=key,
                       data_type='thresh',
                       metplus_configs=[mp_config_name])

    print(f"KEY: {key}, ENV VARS: {cbw.env_var_dict}")
    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output
    assert cbw.isOK == is_ok


@pytest.mark.parametrize(
    'mp_config_name,met_config_name,c_dict_key,remove_quotes,expected_output', [
        # var is set, use quotes
        ('TEST_LIST_1', 'test_list_1', None,
         False, 'test_list_1 = ["value_1", "value2"];'),
        # var is set, remove quotes
        ('TEST_LIST_1', 'test_list_1', None,
         True, 'test_list_1 = [value_1, value2];'),
        # var is not set
        ('TEST_LIST_2', 'test_list_2', None,
         False, ''),
        # var is set, use quotes, set c_dict key
        ('TEST_LIST_1', 'test_list_1', 'the_key',
         False, 'test_list_1 = ["value_1", "value2"];'),
        # var is set, remove quotes, set c_dict key
        ('TEST_LIST_1', 'test_list_1', 'the_key',
         True, 'test_list_1 = [value_1, value2];'),
        # var is set with single quotes, remove quotes
        ('TEST_LIST_3', 'test_list_3', None,
         True, 'test_list_3 = [value_1, value2];'),
        # var is set with double quotes, remove quotes
        ('TEST_LIST_4', 'test_list_4', None,
         True, 'test_list_4 = [value_1, value2];'),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_list(metplus_config, mp_config_name, met_config_name,
                             c_dict_key, remove_quotes, expected_output):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_LIST_1', 'value_1,   value2')
    cbw.config.set('config', 'TEST_LIST_3', "'value_1',   'value2'")
    cbw.config.set('config', 'TEST_LIST_4', '"value_1",   "value2"')

    extra_args = {}
    if remove_quotes:
        extra_args['remove_quotes'] = True

    key = c_dict_key
    if key is None:
        key = met_config_name

    key = key.upper()

    cbw.add_met_config(name=met_config_name,
                       data_type='list',
                       env_var_name=key,
                       metplus_configs=[mp_config_name],
                       extra_args=extra_args)
    print(f"KEY: {key}, ENV VARS: {cbw.env_var_dict}")
    assert cbw.env_var_dict.get(f'METPLUS_{key}', '') == expected_output


@pytest.mark.parametrize(
    'mp_config_name,allow_empty,expected_output', [
        # var is set to empty, don't set
        ('TEST_LIST_1', False, ''),
        # var is set to empty, set to empty list
        ('TEST_LIST_1', True, 'test_list_1 = [];'),
        # var is not set
        ('TEST_LIST_2', False, ''),
        # var is not set
        ('TEST_LIST_2', True, ''),
    ]
)
@pytest.mark.wrapper
def test_add_met_config_list_allow_empty(metplus_config, mp_config_name,
                                         allow_empty, expected_output):
    cbw = CommandBuilder(metplus_config)

    # set some config variables to test
    cbw.config.set('config', 'TEST_LIST_1', '')

    extra_args = {}
    if allow_empty:
        extra_args['allow_empty'] = True

    met_config_name = mp_config_name.lower()

    cbw.add_met_config(name=met_config_name,
                       data_type='list',
                       metplus_configs=[mp_config_name],
                       extra_args=extra_args)

    assert cbw.env_var_dict.get(f'METPLUS_{mp_config_name}', '') == expected_output


@pytest.mark.wrapper
def test_add_met_config_dict(metplus_config):
    dict_name = 'fcst_hr_window'
    beg = -3
    end = 5
    expected_value = f'{dict_name} = {{beg = -3;end = 5;}}'

    config = metplus_config
    config.set('config', 'TC_GEN_FCST_HR_WINDOW_BEG', beg)
    config.set('config', 'TC_GEN_FCST_HR_WINDOW_END', end)
    cbw = CommandBuilder(config)
    cbw.app_name = 'tc_gen'

    items = {
        'beg': 'int',
        'end': 'int',
    }

    cbw.add_met_config_dict(dict_name, items)
    print(f"env_var_dict: {cbw.env_var_dict}")
    actual_value = cbw.env_var_dict.get('METPLUS_FCST_HR_WINDOW_DICT')
    assert actual_value == expected_value


@pytest.mark.wrapper
def test_add_met_config_window(metplus_config):
    dict_name = 'fcst_hr_window'
    beg = -3
    end = 5
    expected_value = f'{dict_name} = {{beg = -3;end = 5;}}'

    config = metplus_config
    config.set('config', 'TC_GEN_FCST_HR_WINDOW_BEG', beg)
    config.set('config', 'TC_GEN_FCST_HR_WINDOW_END', end)
    cbw = CommandBuilder(config)
    cbw.app_name = 'tc_gen'

    cbw.add_met_config_window(dict_name)
    print(f"env_var_dict: {cbw.env_var_dict}")
    actual_value = cbw.env_var_dict.get('METPLUS_FCST_HR_WINDOW_DICT')
    assert actual_value == expected_value


@pytest.mark.wrapper
def test_add_met_config(metplus_config):
    config = metplus_config
    value = 5
    config.set('config', 'TC_GEN_VALID_FREQUENCY', value)
    cbw = CommandBuilder(config)
    cbw.add_met_config(name='valid_freq',
                       data_type='int',
                       metplus_configs=['TC_GEN_VALID_FREQUENCY',
                                       'TC_GEN_VALID_FREQ',])
    print(f"env_var_dict: {cbw.env_var_dict}")
    expected_value = f'valid_freq = {value};'
    assert cbw.env_var_dict['METPLUS_VALID_FREQ'] == expected_value


@pytest.mark.wrapper
def test_add_met_config_dict_nested(metplus_config):
    dict_name = 'outer'
    beg = -3
    end = 5
    sub_dict_name = 'inner'
    sub_dict_value1 = 'value1'
    sub_dict_value2 = 'value2'
    expected_value = (
        f'{dict_name} = {{beg = {beg};end = {end};{sub_dict_name} = '
        f'{{var1 = {sub_dict_value1};var2 = {sub_dict_value2};}}}}'
    )

    config = metplus_config
    config.set('config', 'APP_OUTER_BEG', beg)
    config.set('config', 'APP_OUTER_END', end)
    config.set('config', 'APP_OUTER_INNER_VAR1', sub_dict_value1)
    config.set('config', 'APP_OUTER_INNER_VAR2', sub_dict_value2)
    cbw = CommandBuilder(config)
    cbw.app_name = 'app'

    items = {
        'beg': 'int',
        'end': 'int',
        'inner': ('dict', None, {'var1': ('string', 'remove_quotes', None),
                                 'var2': ('string', 'remove_quotes', None),
                                 }),
    }

    cbw.add_met_config_dict(dict_name, items)
    print(f"env_var_dict: {cbw.env_var_dict}")
    assert cbw.env_var_dict.get('METPLUS_OUTER_DICT') == expected_value


@pytest.mark.parametrize(
    'extra, expected_value', [
        # trailing semi-colon should be added at end automatically
        ('file_type = NETCDF_NCCF',
         "'name=\"name\"; level=\"(*,*)\"; file_type = NETCDF_NCCF;'"),
        ('file_type = NETCDF_NCCF;',
         "'name=\"name\"; level=\"(*,*)\"; file_type = NETCDF_NCCF;'"),
        ('file_type = NETCDF_NCCF; other_opt = "opt"',
         "'name=\"name\"; level=\"(*,*)\"; file_type = NETCDF_NCCF; other_opt = \"opt\";'"),
    ]
)
@pytest.mark.wrapper
def test_get_field_info_extra(metplus_config, extra, expected_value):
    d_type = 'FCST'
    name = 'name'
    level = '"(*,*)"'
    config = metplus_config
    wrapper = CommandBuilder(config)
    actual_value = wrapper.get_field_info(
        d_type=d_type,
        v_name=name,
        v_level=level,
        v_extra=extra,
        add_curly_braces=False
    )[0]
    assert actual_value == expected_value


@pytest.mark.parametrize(
    'exists, skip, is_dir, use_prefix, run', [
            (True, True, False, True, False),
            (True, False, False, True, True),
            (False, True, False, True, True),
            (False, False, False, True, True),
            (True, True, True, True, False),
            (True, False, True, True, True),
            (False, True, True, True, True),
            (False, False, True, True, True),
            (True, True, False, False, False),
            (True, False, False, False, True),
            (False, True, False, False, True),
            (False, False, False, False, True),
            (True, True, True, False, False),
            (True, False, True, False, True),
            (False, True, True, False, True),
            (False, False, True, False, True),
        ]
)
@pytest.mark.wrapper
def test_find_and_check_output_file_skip(metplus_config, exists, skip, is_dir,
                                         use_prefix, run):
    app_name = 'command_builder'
    config = metplus_config
    if use_prefix:
        config.set('config', f'{app_name.upper()}_OUTPUT_PREFIX', 'prefix')
    wrapper = CommandBuilder(config)
    wrapper.app_name = app_name
    prefix = f'{app_name}_prefix' if use_prefix else app_name
    exist_file = f'{prefix}_120000L_20190201_000000V.stat'
    non_exist_file = f'{prefix}_240000L_20190201_000000V.stat'

    # create fake file to test
    create_fullpath = os.path.join(config.getdir('OUTPUT_BASE'), exist_file)
    open(create_fullpath, 'a').close()

    # set time_info, output template/dir, skip if output exists flag
    task_info = {'valid': datetime.datetime(2019, 2, 1, 0)}
    if is_dir:
        task_info['lead_hours'] = 12 if exists else 24

    time_info = ti_calculate(task_info)
    wrapper.c_dict['OUTPUT_DIR'] = wrapper.config.getdir('OUTPUT_BASE')

    wrapper.c_dict['SKIP_IF_OUTPUT_EXISTS'] = skip
    if is_dir:
        wrapper.c_dict['OUTPUT_TEMPLATE'] = ''
    else:
        wrapper.c_dict['OUTPUT_TEMPLATE'] = exist_file if exists else non_exist_file

    result = wrapper.find_and_check_output_file(time_info, is_directory=is_dir)

    # cast result to bool because None isn't equal to False
    assert bool(result) == run


@pytest.mark.wrapper
def test_set_met_config_obs_window(metplus_config):
    config = metplus_config
    cb = CommandBuilder(config)
    cb.c_dict['OBS_WINDOW_BEGIN'] = '20230808'
    cb.c_dict['OBS_WINDOW_END'] = None
    cb.set_met_config_obs_window(cb.c_dict)

    assert cb.env_var_dict['METPLUS_OBS_WINDOW_BEGIN'] == 'begin = 20230808;'
    assert cb.env_var_dict['METPLUS_OBS_WINDOW_END'] == ''
    

@pytest.mark.parametrize(
    'time_info, user_envs, expected_env, expected_user_env', [
        (
            {'init':'20230810104356', 'now': '2023081011'},
            True,
            'Foo = 20230810104356',
            'My now = 2023081011',
         ),
        (
            {'init':'20230810104356', 'now': '2023081011'},
            False,
            'Foo = 20230810104356',
            None,
         ),
        (
            None,
            True,
            'Foo = {init?fmt=%Y%m%d%H%M%S}',
            None,
        ),

    ]
)
@pytest.mark.wrapper
def test_set_environment_variables(metplus_config,
                                   time_info,
                                   user_envs,
                                   expected_env,
                                   expected_user_env):
    
    config = metplus_config
    
    if user_envs:
        config.set('user_env_vars',
                   'CMD_BUILD_USER_TEST',
                   'My now = {now?fmt=%Y%m%d%H}'
                   )
    
    cb = CommandBuilder(config)
    cb.env_var_dict['CMD_BUILD_TEST'] = 'Foo = {init?fmt=%Y%m%d%H%M%S}'
    cb.env_var_keys.append('CMD_BUILD_TEST')
    cb.set_environment_variables(time_info=time_info)
    
    assert cb.env['CMD_BUILD_TEST'] == expected_env
    if user_envs and not time_info:
        ct = cb.config.getstr('config', 'CLOCK_TIME')
        ct = datetime.datetime.strptime(ct, "%Y%m%d%H%M%S").strftime("%Y%m%d%H")
        assert cb.env['CMD_BUILD_USER_TEST'] == f'My now = {ct}'
    elif user_envs:
        assert cb.env['CMD_BUILD_USER_TEST'] == expected_user_env
    else:
        assert cb.config['user_env_vars'] == {}


@pytest.mark.parametrize(
    'shell, expected', [
        ('bash', 'export CMD_BUILD_USER_TEST="User \\"var\\"!";'),
        ('csh', 'setenv CMD_BUILD_USER_TEST "User "\\""var"\\""!";'),
    ]
)    
@pytest.mark.wrapper
def test_get_env_copy(metplus_config, shell, expected):
    config = metplus_config
    config.set('user_env_vars',
            'CMD_BUILD_USER_TEST',
            "User \"var\"!"
            )

    cb = CommandBuilder(config)
    cb.c_dict['USER_SHELL']= shell
    
    cb.set_environment_variables()
    actual = cb.get_env_copy({'MET_TMP_DIR', 'OMP_NUM_THREADS'})
 
    assert expected in actual


def _in_last_err(msg, mock_logger):
    last_msg = mock_logger.error.call_args_list[-1][0][0]
    return msg in last_msg


@pytest.mark.wrapper
def test_get_command(metplus_config):
    config = metplus_config

    cb = CommandBuilder(config)
    cb.app_path = '/jabberwocky/'
    cb.infiles = ['O','frabjous','day']
    cb.outfile = 'callooh'
    cb.param = 'callay'

    with mock.patch.object(os.path, 'dirname', return_value='callooh'): 
        with mock.patch.object(cb_wrapper, 'mkdir_p'):
            actual = cb.get_command()
    assert actual == '/jabberwocky/ -v 2 O frabjous day callooh callay'

    with mock.patch.object(os.path, 'dirname', return_value=None): 
        actual = cb.get_command()
    assert actual is None
    assert _in_last_err('Must specify path to output file', cb.logger)

    cb.outfile = None
    actual = cb.get_command()
    assert actual is None
    assert _in_last_err('No output filename specified', cb.logger)

    cb.infiles = None
    actual = cb.get_command()
    assert actual is None
    assert _in_last_err('No input filenames specified', cb.logger)

    cb.app_path = None
    actual = cb.get_command()
    assert actual is None
    assert _in_last_err('No app path specified.', cb.logger)


@pytest.mark.parametrize(
    'd_type, curly, values, expected', [
        ('fcst',
         True,
         [['0.2','1.0'],'A24','Z0','extra'],
         ['{ name="A24"; level="Z0"; cat_thresh=[ 0.2,1.0 ]; extra; }']
        ),
        ('fcst',
         False,
         [['20'],'apcp','3000',None],
         ['\'name="apcp"; level="3000"; cat_thresh=[ 20 ];\'']
        ),
        ('obs',
         True,
         [['0.2','1.0'],'A24','Z0',None],
         ['{ name="A24"; level="Z0"; cat_thresh=[ 0.2,1.0 ]; }']
        ),
    ]
)    
@pytest.mark.wrapper
def test_format_field_info(metplus_config,
                           d_type,
                           curly,
                           values,
                           expected):
    var_keys = [
                f'{d_type}_thresh',
                f'{d_type}_name',
                f'{d_type}_level',
                f'{d_type}_extra',
               ]
    var_info = dict(zip(var_keys, values))

    cb = CommandBuilder(metplus_config)
    actual = cb.format_field_info(var_info, d_type, curly)
    assert actual == expected

 
@pytest.mark.parametrize(
    'log_metplus', [
        (True),(False)
    ]
)
@pytest.mark.wrapper
def test_run_command_error(metplus_config, log_metplus):
    config = metplus_config
    if log_metplus:
        config.set('config', 'LOG_METPLUS', '/fake/file.log')
    else:
        config.set('config', 'LOG_METPLUS', '') 

    cb = CommandBuilder(metplus_config)
    with mock.patch.object(cb, 'run_cmd', return_value=-1):
        actual = cb.run_command('foo')
    assert not actual 
    assert _in_last_err('Command returned a non-zero return code: foo', cb.logger)

 
@pytest.mark.wrapper
def test_find_input_files_ensemble(metplus_config):
    config = metplus_config
    cb = CommandBuilder(metplus_config)

    time_info =  ti_calculate({
        'valid': datetime.datetime.strptime("201802010000", '%Y%m%d%H%M'),
        'lead':  0,
        })

    # can't write file list
    with mock.patch.object(cb, 'write_list_file', return_value=None):
        with mock.patch.object(cb, 'find_model', return_value=['file']):
            actual = cb.find_input_files_ensemble(time_info, False)
    assert actual is False
    assert _in_last_err('Could not write filelist file', cb.logger)

    # not _check_expected_ensembles
    with mock.patch.object(cb, '_check_expected_ensembles', return_value=None):
        with mock.patch.object(cb, 'find_model', return_value=['file']):
            actual = cb.find_input_files_ensemble(time_info)
    assert actual is False

    # no input files
    with mock.patch.object(cb, 'find_model', return_value=[]):
        actual = cb.find_input_files_ensemble(time_info)
    assert actual is False
    assert _in_last_err('Could not find any input files', cb.logger)
    
    # file list does/doesn't exist
    cb.c_dict['FCST_INPUT_FILE_LIST'] = 'fcst_file_list'
    actual = cb.find_input_files_ensemble(time_info)
    assert actual is False
    assert _in_last_err('Could not find file list file', cb.logger)
    
    with mock.patch.object(cb_wrapper.os.path, 'exists', return_value=True):
        actual = cb.find_input_files_ensemble(time_info)
    assert actual is True
    assert cb.infiles[-1] == 'fcst_file_list'

    # ctrl file not found
    cb.c_dict['CTRL_INPUT_TEMPLATE'] = 'ctrl_file'
    with mock.patch.object(cb, 'find_data', return_value=None):
        actual = cb.find_input_files_ensemble(time_info)
    assert actual is False


@pytest.mark.wrapper
def test_errors_and_defaults(metplus_config):
    """
    A test to check various functions produce expected log messages
    and return values on error or unexpected input.
    """
    config = metplus_config
    app_name = 'command_builder'
    config.set('config', f'{app_name.upper()}_OUTPUT_PREFIX', 'prefix')
    cb = CommandBuilder(metplus_config)
    cb.app_name = app_name

    # smoke test run_all_times
    cb.run_all_times()
    assert cb.isOK

    # test get_output_prefix without time_info
    actual = cb.get_output_prefix(time_info=None)
    assert actual == 'prefix'

    # test handle_climo_dict errors counted correctly
    starting_errs = cb.errors
    with mock.patch.object(cb_wrapper, 'handle_climo_dict', return_value=False):
        for x in range(2):
            cb.handle_climo_dict()
    assert starting_errs + 2 == cb.errors

    # test missing FLAGS returns none
    actual = cb.handle_flags('foo')
    assert actual is None

    # test get_env_var_value empty and list
    actual = cb.get_env_var_value('foo',{'foo':''},'list')
    assert actual == '[]'

    # test add_met_config_dict not OK
    assert cb.isOK
    with mock.patch.object(cb_wrapper, 'add_met_config_dict', return_value=False):
        actual = cb.add_met_config_dict('foo', 'bar')
    assert actual is False
    assert not cb.isOK

    # test build when no cmd
    with mock.patch.object(cb, 'get_command', return_value=None):
        actual = cb.build()
    assert actual == False
    assert _in_last_err('Could not generate command', cb.logger)

    # test python embedding check
    with mock.patch.object(cb_wrapper, 'is_python_script', return_value=True):
        actual = cb.check_for_python_embedding('FCST',{'fcst_name':'pyEmbed'})
    assert actual == 'python_embedding'

    cb.env_var_dict['METPLUS_FCST_FILE_TYPE'] = "PYTHON_NUMPY"
    with mock.patch.object(cb_wrapper, 'is_python_script', return_value=True):
        actual = cb.check_for_python_embedding('FCST',{'fcst_name':'pyEmbed'})
    assert actual == 'python_embedding'

    with mock.patch.object(cb_wrapper, 'is_python_script', return_value=False):
        actual = cb.check_for_python_embedding('FCST',{'fcst_name':'pyEmbed'})
    assert actual == 'pyEmbed'

    # test field_info not set
    cb.c_dict['CURRENT_VAR_INFO'] = None
    actual = cb.set_current_field_config()
    assert actual is None

    # test check_gempaktocf
    cb.isOK = True
    cb.check_gempaktocf(False)
    assert cb.isOK == False
    assert _in_last_err('[exe] GEMPAKTOCF_JAR was not set in configuration file.', cb.logger)

    # test expected ensemble mismatch
    cb.c_dict['N_MEMBERS'] = 1
    actual = cb._check_expected_ensembles(['file1', 'file2'])
    assert actual is False
    assert _in_last_err('Found more files than expected!', cb.logger)

    # format field info
    with mock.patch.object(cb_wrapper, 'format_field_info', return_value='bar'): 
        actual = cb.format_field_info({},'foo')
    assert actual is None
    assert _in_last_err('bar', cb.logger)

    # check get_field_info 
    with mock.patch.object(cb_wrapper, 'get_field_info', return_value='bar'): 
        actual = cb.get_field_info({},'foo')
    assert actual is None
    assert _in_last_err('bar', cb.logger)

