#!/usr/bin/env python3

import pytest

from metplus.util.met_config import *

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
