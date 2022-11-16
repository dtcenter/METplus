#!/usr/bin/env python3

import pytest

import pprint
import os
from datetime import datetime

from metplus.util.config_validate import *


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
    assert is_var_item_valid(item_list, '1', extension, conf)[0] == is_valid


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

    assert is_var_item_valid(item_list, '1', 'LEVELS', conf)[0] == is_valid
