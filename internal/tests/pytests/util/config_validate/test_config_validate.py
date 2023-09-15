#!/usr/bin/env python3

import pytest
from unittest import mock
import pprint
import os
from datetime import datetime

from metplus.util import config_validate as cv


@pytest.mark.parametrize(
    'item_list, extension, is_valid', [
        (['FCST'], 'NAME', False),
        (['OBS'], 'NAME', False),
        (['FCST', 'OBS'], 'NAME', True),
        (['BOTH'], 'NAME', True),
        (['FCST', 'OBS', 'BOTH'], 'NAME', False),
        (['FCST', 'ENS'], 'NAME', False),
        (['OBS', 'ENS'], 'NAME', False),
        (['FCST', 'OBS', 'ENS'], 'NAME', True),
        (['BOTH', 'ENS'], 'NAME', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'NAME', False),

        (['FCST', 'OBS'], 'THRESH', True),
        (['BOTH'], 'THRESH', True),
        (['FCST', 'OBS', 'BOTH'], 'THRESH', False),
        (['FCST', 'OBS', 'ENS'], 'THRESH', True),
        (['BOTH', 'ENS'], 'THRESH', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'THRESH', False),

        (['FCST'], 'OPTIONS', True),
        (['OBS'], 'OPTIONS', True),
        (['FCST', 'OBS'], 'OPTIONS', True),
        (['BOTH'], 'OPTIONS', True),
        (['FCST', 'OBS', 'BOTH'], 'OPTIONS', False),
        (['FCST', 'ENS'], 'OPTIONS', True),
        (['OBS', 'ENS'], 'OPTIONS', True),
        (['FCST', 'OBS', 'ENS'], 'OPTIONS', True),
        (['BOTH', 'ENS'], 'OPTIONS', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'OPTIONS', False),

        (['FCST', 'OBS', 'BOTH'], 'LEVELS', False),
        (['FCST', 'OBS'], 'LEVELS', True),
        (['BOTH'], 'LEVELS', True),
        (['FCST', 'OBS', 'ENS'], 'LEVELS', True),
        (['BOTH', 'ENS'], 'LEVELS', True),

    ]
)
@pytest.mark.util
def test_is_var_item_valid(metplus_config, item_list, extension, is_valid):
    conf = metplus_config
    assert cv.is_var_item_valid(item_list, '1', extension, conf)[0] == is_valid


@pytest.mark.parametrize(
    'item_list, configs_to_set, is_valid', [

        (['FCST'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, True),
        (['FCST'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                    'FCST_VAR1_NAME': 'script_name.py something else'}, True),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                    'FCST_VAR1_NAME': 'APCP'}, False),

        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, True),
        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, True),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                   'FCST_VAR1_NAME': 'APCP'}, False),

        (['FCST'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, False),
        (['FCST'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(0,*,*)", "(1,*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, False),

        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, False),
        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(0,*,*)", "(1,*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, False),

    ]
)
@pytest.mark.util
def test_is_var_item_valid_levels(metplus_config, item_list, configs_to_set, is_valid):
    conf = metplus_config
    for key, value in configs_to_set.items():
        conf.set('config', key, value)

    assert cv.is_var_item_valid(item_list, '1', 'LEVELS', conf)[0] == is_valid



@pytest.mark.parametrize(
    'met_config_file, expected',
    [
        ('GridStatConfig_good', (True, [])),
        ('GridStatConfig_bad', (False, [])),
        ('GridStatConfig_fake', (False, [])),
    ]
)
@pytest.mark.util
def test_check_for_deprecated_met_config(metplus_config, met_config_file, expected):
    script_dir = os.path.dirname(__file__)
    met_config = os.path.join(script_dir, met_config_file)

    metplus_config.set('config', 'GRID_STAT_CONFIG_FILE', met_config)

    actual = cv.check_for_deprecated_met_config(metplus_config)
    assert actual == expected


@pytest.mark.util
def test_check_for_deprecated_config_simple(metplus_config):
    actual = cv.check_for_deprecated_config(metplus_config)
    assert actual == (True, [])
    metplus_config.logger.error.assert_not_called


@pytest.mark.parametrize(
    'dep_item,deprecated_dict, expected, err_msgs',
    [
        (
            "TEST_DEPRECATED",
            {
                'upgrade': 'ensemble',
                'alt': 'ice cream',
                'copy': True
            },
            (False, ["sed -i 's|^TEST_DEPRECATED|ice cream|g' dir/config1.conf", "sed -i 's|{TEST_DEPRECATED}|{ice cream}|g' dir/config1.conf"]),
            ['DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE FOLLOW THE INSTRUCTIONS TO UPDATE THE CONFIG FILES',
            'TEST_DEPRECATED should be replaced with ice cream'],
        ),
        (
            "TEST_DEPRECATED_<n>",
            {
                'upgrade': 'ensemble',
                'alt': 'nth degree',
                'copy': False
            },
            (False, []),
            ['DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE FOLLOW THE INSTRUCTIONS TO UPDATE THE CONFIG FILES'],
        ),
        (
            "TEST_DEPRECATED_NO_ALT",
            {},
            (False, []),
            ['DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE FOLLOW THE INSTRUCTIONS TO UPDATE THE CONFIG FILES',
             'TEST_DEPRECATED_NO_ALT should be removed'],
        ),
        (
            "TEST_DEPRECATED_NO_dict",
            [],
            (True, []),
            [],
        ),  
    ]
)
@pytest.mark.util
def test_check_for_deprecated_config(metplus_config,
                                     dep_item,
                                     deprecated_dict,
                                     expected,
                                     err_msgs):

    depr_dict = {dep_item: deprecated_dict}
    config = metplus_config
    config.set('config', dep_item.replace('<n>','2'), 'old value')
    config.set('config', 'CONFIG_INPUT', 'dir/config1.conf')

    with mock.patch.object(cv, 'DEPRECATED_DICT', depr_dict):
        actual = cv.check_for_deprecated_config(metplus_config)
    assert actual == expected

    if err_msgs:
        for msg in err_msgs:
            config.logger.error.assert_any_call(msg)
    else:
        config.logger.error.assert_not_called
