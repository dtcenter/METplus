#!/usr/bin/env python

import sys
import pytest
import datetime
from config_launcher import METplusConfig
import met_util as util
from command_builder import CommandBuilder
import produtil
import os
import config_metplus

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    # Read in the configuration object CONFIG
    config = config_metplus.setup(util.baseinputconfs)
    return config

@pytest.mark.parametrize(
    'key, value', [
        (3600, 3600),
        ('3600S', 3600),
        ('60M', 3600),
        ('1H', 3600),
        (-3600, -3600),
        ('-3600S', -3600),
        ('-60M', -3600),
        ('-1H', -3600),
        (0, 0),
        ('0S', 0),
        ('0M', 0),
        ('0H', 0)
    ]
)
def test_getseconds(key, value):
    conf = metplus_config()
    conf.set('config', 'TEST_SECONDS', key)
    seconds = conf.getseconds('config', 'TEST_SECONDS')
    assert(seconds == value)

@pytest.mark.parametrize(
    'input_value, typeobj, default, result', [
        ('1', int, None, 1),
        ('1', float, None, 1.0),
        ('1.0', float, None, 1.0),
        ('1.0', int, None, None),
        ('', int, None, util.MISSING_DATA_VALUE_INT),
        ('', float, None, util.MISSING_DATA_VALUE_FLOAT),
        ('x', int, None, None),
        ('x', float, None, None),
        ('1', int, 2, 1),
        ('1', float, 2.0, 1.0),
        ('1.0', float, 2.0, 1.0),
        ('1.0', int, 2, None),
        ('', int, 2, 2),
        ('', float, 2.0, 2.0),
        ('x', int, 2, None),
        ('x', float, 2.0, None),

    ]
)
def test_get_optional_number_from_config(input_value, typeobj, default, result):
    conf = metplus_config()
    conf.set('config', 'TEST_OPT_NUMBER', input_value)
    cb = CommandBuilder(conf, conf.logger)
    output_value = cb.get_optional_number_from_config('config', 'TEST_OPT_NUMBER', typeobj, default)
    assert(output_value == result)

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('1', None, '1'),
        ('1', 2, '1'),
        ('integer', None, 'integer'),
        ('integer', 1, 'integer'),
        ('1.7', '2', '1.7'),
        ('1.0', None, '1.0'),
        ('', None, ''),
        ('', '2', ''),
#        (None, None, None),
        (None, '1', '1'),
    ]
)
def test_getstr(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETSTR', input_value)

    assert(result == conf.getstr('config', 'TEST_GETSTR', default))


# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('1', None, 1),
        ('1', 2, 1),
        (None, None, util.MISSING_DATA_VALUE_INT),
        (None, 1, 1),
        ('integer', None, None),
        ('integer', 1, None),
        ('0', None, 0),
        ('0', 2, 0),
        ('', None, None),
        ('', 2, None),
        ('1.7', 2, None),
        ('1.0', None, None),
        ('1.0', 2, None),
    ]
)
def test_getint(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETINT', input_value)

    assert(result == conf.getint('config', 'TEST_GETINT', default))