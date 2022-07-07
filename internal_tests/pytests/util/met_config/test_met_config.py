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
        ({'APP_CLIMO_<TYPE>_FIELD': '{name="TMP"; level="(*,*)";}'},
         '{name="TMP"; level="(*,*)";}'),
        # 2 VAR1 name/level set
        ({'APP_CLIMO_<TYPE>_VAR1_NAME': 'TMP',
          'APP_CLIMO_<TYPE>_VAR1_LEVELS': '"(*,*)"'},
         '{ name="TMP"; level="(*,*)"; }'),
        # 3 VAR1/2 name/level set
        ({'APP_CLIMO_<TYPE>_VAR1_NAME': 'TMP',
          'APP_CLIMO_<TYPE>_VAR1_LEVELS': '"(*,*)"',
          'APP_CLIMO_<TYPE>_VAR2_NAME': 'PRES',
          'APP_CLIMO_<TYPE>_VAR2_LEVELS': '"(0,*,*)"'},
         '{ name="TMP"; level="(*,*)"; },{ name="PRES"; level="(0,*,*)"; }'),
        # 4 VAR1 name/level and FIELD set - prefer VAR<n>
        ({'APP_CLIMO_<TYPE>_FIELD': '{name="TEMP"; level="(0,*,*)";}',
          'APP_CLIMO_<TYPE>_VAR1_NAME': 'TMP',
          'APP_CLIMO_<TYPE>_VAR1_LEVELS': '"(*,*)"'},
         '{ name="TMP"; level="(*,*)"; }'),
    ]
)
@pytest.mark.util
def test_read_climo_field(metplus_config, config_overrides, expected_value):
    app_name = 'app'
    for climo_type in ('MEAN', 'STDEV'):
        expected_var = f'{app_name}_CLIMO_{climo_type}_FIELD'.upper()
        config = metplus_config()

        # set config values
        for key, value in config_overrides.items():
            key_sub = key.replace('<TYPE>', climo_type)
            value_sub = value.replace('<type>', climo_type.lower())
            config.set('config', key_sub, value_sub)

        _read_climo_field(climo_type, config, app_name)
        assert config.getraw('config', expected_var) == expected_value


@pytest.mark.parametrize(
    'config_overrides, expected_value', [
        # 0 no relevant config set
        ({}, ''),
        # 1 file name single
        ({'APP_CLIMO_<TYPE>_FILE_NAME': 'some/file/path'},
         'climo_<type> = {file_name = ["some/file/path"];}'),
        # 2 file name multiple
        ({'APP_CLIMO_<TYPE>_FILE_NAME': 'some/file/path, other/path'},
         'climo_<type> = {file_name = ["some/file/path", "other/path"];}'),
        # 3 field single
        ({'APP_CLIMO_<TYPE>_FIELD': '{name="TMP"; level="(*,*)";}'},
         'climo_<type> = {field = [{name="TMP"; level="(*,*)";}];}'),
        # 4 field multiple
        ({'APP_CLIMO_<TYPE>_FIELD': ('{name="TMP"; level="(*,*)";},'
                                         '{name="TEMP"; level="P500";}')},
         ('climo_<type> = {field = [{name="TMP"; level="(*,*)";}, '
          '{name="TEMP"; level="P500";}];}')),
        # 5 use fcst no other climo_<type>
        ({'APP_CLIMO_<TYPE>_USE_FCST': 'TRUE'},
         'climo_<type> = fcst;'),
        # 6 use obs no other climo_<type>
        ({'APP_CLIMO_<TYPE>_USE_OBS': 'TRUE'},
         'climo_<type> = obs;'),
        # 7 use fcst with other climo_<type>
        ({'APP_CLIMO_<TYPE>_REGRID_METHOD': 'NEAREST',
          'APP_CLIMO_<TYPE>_USE_FCST': 'TRUE'},
         'climo_<type> = {regrid = {method = NEAREST;}}climo_<type> = fcst;'),
        # 8 use obs with other climo_<type>
        ({'APP_CLIMO_<TYPE>_REGRID_METHOD': 'NEAREST',
          'APP_CLIMO_<TYPE>_USE_OBS': 'TRUE'},
         'climo_<type> = {regrid = {method = NEAREST;}}climo_<type> = obs;'),
        # 9 regrid method
        ({'APP_CLIMO_<TYPE>_REGRID_METHOD': 'NEAREST', },
         'climo_<type> = {regrid = {method = NEAREST;}}'),
        # 10 regrid width
        ({'APP_CLIMO_<TYPE>_REGRID_WIDTH': '1', },
         'climo_<type> = {regrid = {width = 1;}}'),
        # 11 regrid vld_thresh
        ({'APP_CLIMO_<TYPE>_REGRID_VLD_THRESH': '0.5', },
         'climo_<type> = {regrid = {vld_thresh = 0.5;}}'),
        # 12 regrid shape
        ({'APP_CLIMO_<TYPE>_REGRID_SHAPE': 'SQUARE', },
         'climo_<type> = {regrid = {shape = SQUARE;}}'),
        # 13 time_interp_method
        ({'APP_CLIMO_<TYPE>_TIME_INTERP_METHOD': 'NEAREST', },
         'climo_<type> = {time_interp_method = NEAREST;}'),
        # 14 match_month
        ({'APP_CLIMO_<TYPE>_MATCH_MONTH': 'True', },
         'climo_<type> = {match_month = TRUE;}'),
        # 15 day_interval - int
        ({'APP_CLIMO_<TYPE>_DAY_INTERVAL': '30', },
         'climo_<type> = {day_interval = 30;}'),
        # 16 day_interval - NA
        ({'APP_CLIMO_<TYPE>_DAY_INTERVAL': 'NA', },
         'climo_<type> = {day_interval = NA;}'),
        # 17 hour_interval
        ({'APP_CLIMO_<TYPE>_HOUR_INTERVAL': '12', },
         'climo_<type> = {hour_interval = 12;}'),
        # 18 all
        ({
             'APP_CLIMO_<TYPE>_FILE_NAME': '/some/climo_<type>/file.txt',
             'APP_CLIMO_<TYPE>_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'APP_CLIMO_<TYPE>_REGRID_METHOD': 'NEAREST',
             'APP_CLIMO_<TYPE>_REGRID_WIDTH': '1',
             'APP_CLIMO_<TYPE>_REGRID_VLD_THRESH': '0.5',
             'APP_CLIMO_<TYPE>_REGRID_SHAPE': 'SQUARE',
             'APP_CLIMO_<TYPE>_TIME_INTERP_METHOD': 'NEAREST',
             'APP_CLIMO_<TYPE>_MATCH_MONTH': 'True',
             'APP_CLIMO_<TYPE>_DAY_INTERVAL': '30',
             'APP_CLIMO_<TYPE>_HOUR_INTERVAL': '12',
         },
         ('climo_<type> = {file_name = '
          '["/some/climo_<type>/file.txt"];'
          'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
          'regrid = {method = NEAREST;width = 1;'
          'vld_thresh = 0.5;shape = SQUARE;}'
          'time_interp_method = NEAREST;'
          'match_month = TRUE;day_interval = 30;'
          'hour_interval = 12;}')),
    ]
)
@pytest.mark.util
def test_handle_climo_dict(metplus_config, config_overrides, expected_value):
    app_name = 'app'
    for climo_type in ('MEAN', 'STDEV'):
        expected_var = f'METPLUS_CLIMO_{climo_type}_DICT'
        config = metplus_config()
        output_dict = {}

        # set config values
        for key, value in config_overrides.items():
            key_sub = key.replace('<TYPE>', climo_type)
            value_sub = value.replace('<type>', climo_type.lower())
            config.set('config', key_sub, value_sub)

        handle_climo_dict(config, app_name, output_dict)
        print(output_dict)
        expected_sub = expected_value.replace('<type>', climo_type.lower())
        assert output_dict[expected_var] == expected_sub


@pytest.mark.parametrize(
    'name, data_type, mp_configs, extra_args', [
        ('beg', 'int', 'BEG', None),
        ('end', 'int', ['END'], None),
    ]
)
@pytest.mark.util
def test_met_config_info(name, data_type, mp_configs, extra_args):
    item = METConfig(name=name, data_type=data_type)

    item.metplus_configs = mp_configs
    item.extra_args = extra_args

    assert item.name == name
    assert item.data_type == data_type
    if isinstance(mp_configs, list):
        assert item.metplus_configs == mp_configs
    else:
        assert item.metplus_configs == [mp_configs]

    if not extra_args:
        assert item.extra_args == {}


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
@pytest.mark.util
def test_set_met_config_function(data_type, expected_function):
    try:
        function_found = set_met_config_function(data_type)
        function_name = function_found.__name__ if function_found else None
        assert function_name == expected_function
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
@pytest.mark.util
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
@pytest.mark.util
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
