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
from configparser import NoOptionError

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
    'input_value, result', [
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
        ('0H', 0),
        (None, None),
    ]
)
def test_getseconds(input_value, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_SECONDS', input_value)

    try:
        seconds = conf.getseconds('config', 'TEST_SECONDS')
        assert(seconds == result)
    except NoOptionError:
        if result is None:
            assert(True)

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
        (None, None, None),
        (None, '1', '1'),
    ]
)
def test_getstr(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETSTR', input_value)

    # catch NoOptionError exception and pass test if default is None
    try:
        assert(result == conf.getstr('config', 'TEST_GETSTR', default))
    except NoOptionError:
        if default is None:
            assert(True)

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('/some/test/dir', None, '/some/test/dir'),
        ('/some//test/dir', None, '/some/test/dir'),
        ('/path/to', None, 'ValueError'),
        (None, None, 'NoOptionError'),
        (None, '/default/path', '/default/path'),

    ]
)
def test_getdir(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('dir', 'TEST_GETDIR', input_value)

    # catch NoOptionError exception and pass test if default is None
    try:
        assert(result == conf.getdir('TEST_GETSTR', default=default))
    except NoOptionError:
        if result is 'NoOptionError':
            assert(True)
    except ValueError:
        if result is 'ValueError':
            assert(True)

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('some_text', None, 'some_text'),
        ('{valid?fmt=%Y%m%d}', None, '{valid?fmt=%Y%m%d}'),
        ('%Y%m%d', None, '%Y%m%d'),
        ('{valid?fmt=%Y%m%d}_{TEST_EXTRA}', None, '{valid?fmt=%Y%m%d}_extra'),
        ('{valid?fmt=%Y%m%d}_{TEST_EXTRA2}', None, '{valid?fmt=%Y%m%d}_extra_extra'),
        ('{valid?fmt=%Y%m%d}_{NOT_REAL_VAR}', None, '{valid?fmt=%Y%m%d}_{NOT_REAL_VAR}'),
    ]
)
def test_getraw(input_value, default, result):
    conf = metplus_config()
    conf.set('config', 'TEST_EXTRA', 'extra')
    conf.set('config', 'TEST_EXTRA2', '{TEST_EXTRA}_extra')

    if input_value is not None:
        conf.set('config', 'TEST_GETRAW', input_value)

    assert(result == conf.getraw('config', 'TEST_GETRAW', default=default))


# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('True', None, True),
        ('True', 2, True),
        ('False', None, False),
        ('False', 1, False),
        ('true', None, True),
        ('true', 2, True),
        ('false', None, False),
        ('false', 1, False),
        ('yes', None, True),
        ('yes', 2, True),
        ('no', None, False),
        ('no', 1, False),
        ('pizza', None, None),
        ('pizza', False, None),
        (None, False, False),
        (None, True, True),
        (None, None, None),
    ]
)
def test_getbool(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETBOOL', input_value)

    # catch NoOptionError exception and pass test if default is None
    try:
        assert(result == conf.getbool('config', 'TEST_GETBOOL', default))
    except NoOptionError:
        if result is None:
            assert(True)

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, result', [
        (None, None),
        ('/some/fake/path', None),
        ('/bin/sh', '/bin/sh'),
        ('sh', '/bin/sh'),
    ]
)
def test_getexe(input_value, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('exe', 'TEST_GETEXE', input_value)

    assert(result == conf.getexe('TEST_GETEXE'))

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('1.1', None, 1.1),
        ('1.1', 2.2, 1.1),
        (None, None, util.MISSING_DATA_VALUE),
        (None, 1.1, 1.1),
        ('integer', None, None),
        ('integer', 1.1, None),
        ('0', None, 0.0),
        ('0', 2.2, 0.0),
        ('', None, util.MISSING_DATA_VALUE),
        ('', 2.2, util.MISSING_DATA_VALUE),
    ]
)
def test_getfloat(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETFLOAT', input_value)

    try:
        assert(result == conf.getfloat('config', 'TEST_GETFLOAT', default))
    except ValueError:
        if result is None:
            assert(True)

# value = None -- config variable not set
@pytest.mark.parametrize(
    'input_value, default, result', [
        ('1', None, 1),
        ('1', 2, 1),
        (None, None, util.MISSING_DATA_VALUE),
        (None, 1, 1),
        ('integer', None, None),
        ('integer', 1, None),
        ('0', None, 0),
        ('0', 2, 0),
        ('1.7', 2, None),
        ('1.0', None, None),
        ('1.0', 2, None),
        ('', None, util.MISSING_DATA_VALUE),
        ('', 2.2, util.MISSING_DATA_VALUE),
    ]
)
def test_getint(input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETINT', input_value)

    try:
        assert(result == conf.getint('config', 'TEST_GETINT', default))
    except ValueError:
        if result is None:
            assert(True)
