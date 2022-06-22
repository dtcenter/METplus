#!/usr/bin/env python3

import pytest

from metplus.util.met_config import *
from metplus.util.met_config import _read_climo_file_name, _read_climo_field
from metplus.util import CLIMO_TYPES

@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        # 0 no relevant config set
        ({}, ''),
        # 1 _FIELD set
        ({'APP_CLIMO_MEAN_FIELD': '{name="TMP"; level="(*,*)";}'},
         '{name="TMP"; level="(*,*)";}'),
        # 2 VAR1 name/level set
        ({'APP_CLIMO_MEAN_VAR1_NAME': 'TMP',
          'APP_CLIMO_MEAN_VAR1_LEVELS': '"(*,*)"'},
         '{ name="TMP"; level="(*,*)"; }'),
        # 3 VAR1/2 name/level set
        ({'APP_CLIMO_MEAN_VAR1_NAME': 'TMP',
          'APP_CLIMO_MEAN_VAR1_LEVELS': '"(*,*)"',
          'APP_CLIMO_MEAN_VAR2_NAME': 'PRES',
          'APP_CLIMO_MEAN_VAR2_LEVELS': '"(0,*,*)"'},
         '{ name="TMP"; level="(*,*)"; },{ name="PRES"; level="(0,*,*)"; }'),
        # 4 VAR1 name/level and FIELD set - prefer VAR<n>
        ({'APP_CLIMO_MEAN_FIELD': '{name="TEMP"; level="(0,*,*)";}',
          'APP_CLIMO_MEAN_VAR1_NAME': 'TMP',
          'APP_CLIMO_MEAN_VAR1_LEVELS': '"(*,*)"'},
         '{ name="TMP"; level="(*,*)"; }'),
    ]
)
def test_read_climo_field(metplus_config, config_overrides, expected_value):
    app_name = 'app'
    climo_type = 'MEAN'
    expected_var = f'{app_name}_CLIMO_{climo_type}_FIELD'.upper()
    config = metplus_config()

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    _read_climo_field(climo_type, config, app_name)
    assert config.getraw('config', expected_var) == expected_value

@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        # 0 no relevant config set
        ({}, ''),
        # 1 file name single
        ({'APP_CLIMO_MEAN_FILE_NAME': 'some/file/path'},
         'climo_mean = {file_name = ["some/file/path"];}'),
        # 2 file name multiple
        ({'APP_CLIMO_MEAN_FILE_NAME': 'some/file/path, other/path'},
         'climo_mean = {file_name = ["some/file/path", "other/path"];}'),
        # 3 field single
        ({'APP_CLIMO_MEAN_FIELD': '{name="TMP"; level="(*,*)";}'},
         'climo_mean = {field = [{name="TMP"; level="(*,*)";}];}'),
        # 4 field multiple
        ({'APP_CLIMO_MEAN_FIELD': ('{name="TMP"; level="(*,*)";},'
                                         '{name="TEMP"; level="P500";}')},
         ('climo_mean = {field = [{name="TMP"; level="(*,*)";}, '
          '{name="TEMP"; level="P500";}];}')),
        # day interval only - int
        ({'APP_CLIMO_MEAN_DAY_INTERVAL': '3'},
         'climo_mean = {day_interval = 3;}'),
        # day interval only - NA
        ({'APP_CLIMO_MEAN_DAY_INTERVAL': 'NA'},
         'climo_mean = {day_interval = NA;}'),
    ]
)
def test_handle_climo_dict(metplus_config, config_overrides, expected_value):
    app_name = 'app'
    climo_type = 'MEAN'
    expected_var = f'METPLUS_CLIMO_{climo_type}_DICT'
    config = metplus_config()
    output_dict = {}

    # set config values
    for key, value in config_overrides.items():
        config.set('config', key, value)

    handle_climo_dict(config, app_name, output_dict)
    print(output_dict)
    assert output_dict[expected_var] == expected_value


@pytest.mark.parametrize(
    'name, data_type, mp_configs, extra_args', [
        ('beg', 'int', 'BEG', None),
        ('end', 'int', ['END'], None),
    ]
)
def test_met_config_info(name, data_type, mp_configs, extra_args):
    item = METConfig(name=name, data_type=data_type)

    item.metplus_configs = mp_configs
    item.extra_args = extra_args

    assert(item.name == name)
    assert(item.data_type == data_type)
    if isinstance(mp_configs, list):
        assert(item.metplus_configs == mp_configs)
    else:
        assert(item.metplus_configs == [mp_configs])

    if not extra_args:
        assert(item.extra_args == {})

@pytest.mark.parametrize(
    'data_type, expected_function', [
        ('int', 'set_met_config_int'),
        ('float', 'set_met_config_float'),
        ('list', 'set_met_config_list'),
        ('string', 'set_met_config_string'),
        ('thresh', 'set_met_config_thresh'),
        ('bool', 'set_met_config_bool'),
        ('bad_name', None),
    ]
)
def test_set_met_config_function(data_type, expected_function):
    try:
        function_found = set_met_config_function(data_type)
        function_name = function_found.__name__ if function_found else None
        assert(function_name == expected_function)
    except ValueError:
        assert expected_function is None


@pytest.mark.parametrize(
    'input, output', [
        ('', 'NONE'),
        ('NONE', 'NONE'),
        ('FCST', 'FCST'),
        ('OBS', 'OBS'),
        ('G002', '"G002"'),
    ]
)
def test_format_regrid_to_grid(input, output):
    assert format_regrid_to_grid(input) == output

@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        # 0 no climo variables set
        ({}, ''),
        # 1 file name set only
        ({'FILE_NAME': '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'},
         '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'),
        # 2 input template set
        ({'INPUT_TEMPLATE': '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'},
         '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'),
        # 3 input template and dir set
        ({'INPUT_DIR': '/mean/dir',
          'INPUT_TEMPLATE': 'gs_climo_{init?fmt=%Y%m%d%H}.tmpl'},
         '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'),
        # 4 input template and dir set multiple templates
        ({'INPUT_DIR': '/mean/dir',
          'INPUT_TEMPLATE': 'gs_climo_1.tmpl, gs_climo_2.tmpl'},
         '/mean/dir/gs_climo_1.tmpl,/mean/dir/gs_climo_2.tmpl'),
        # 5file name, input template and dir all set
        ({'FILE_NAME': '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl',
          'INPUT_DIR': '/mean/dir',
          'INPUT_TEMPLATE': 'gs_climo_1.tmpl, gs_climo_2.tmpl'},
         '/mean/dir/gs_climo_{init?fmt=%Y%m%d%H}.tmpl'),
        # 6 input template is python embedding keyword and dir is set
        ({'INPUT_DIR': '/mean/dir',
          'INPUT_TEMPLATE': 'PYTHON_NUMPY'},
         'PYTHON_NUMPY'),
        # 7 input template is python embedding keyword and dir is set
        ({'INPUT_DIR': '/mean/dir',
          'INPUT_TEMPLATE': 'PYTHON_XARRAY'},
         'PYTHON_XARRAY'),
    ]
)
def test_read_climo_file_name(metplus_config, config_overrides,
                              expected_value):
    # name of app used for testing to read/set config variables
    app_name = 'grid_stat'

    # check mean and stdev climo variables
    for climo_type in CLIMO_TYPES:
        prefix = f'{app_name.upper()}_CLIMO_{climo_type.upper()}_'

        config = metplus_config()

        # set config values
        for key, value in config_overrides.items():
            config.set('config', f'{prefix}{key}', value)

        _read_climo_file_name(climo_type=climo_type,
                              config=config,
                              app_name=app_name)
        actual_value = config.getraw('config', f'{prefix}FILE_NAME', '')
        assert actual_value == expected_value
