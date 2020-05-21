#!/usr/bin/env python

import sys
import pytest
import datetime
import os

import produtil

from metplus.util.config.config_launcher import METplusConfig
from metplus.util import met_util as util
from metplus.wrappers.command_builder import CommandBuilder
from metplus.util.config import config_metplus

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='test ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test ')
        produtil.log.postmsg('config test is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'config test failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)

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
