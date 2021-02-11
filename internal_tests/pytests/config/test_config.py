#!/usr/bin/env python

import sys
import pytest
import datetime
import os
from configparser import NoOptionError
from shutil import which

import produtil

from metplus.util import met_util as util

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
def test_getseconds(metplus_config, input_value, result):
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
def test_getstr(metplus_config, input_value, default, result):
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
def test_getdir(metplus_config, input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETDIR', input_value)

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
def test_getraw(metplus_config, input_value, default, result):
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
def test_getbool(metplus_config, input_value, default, result):
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
        ('sh', which('sh')),
    ]
)
def test_getexe(metplus_config, input_value, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETEXE', input_value)

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
def test_getfloat(metplus_config, input_value, default, result):
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
def test_getint(metplus_config, input_value, default, result):
    conf = metplus_config()
    if input_value is not None:
        conf.set('config', 'TEST_GETINT', input_value)

    try:
        assert(result == conf.getint('config', 'TEST_GETINT', default))
    except ValueError:
        if result is None:
            assert(True)

@pytest.mark.parametrize(
    'config_key, expected_result', [
        ('VAR_TO_TEST_1', '1'),
        ('VAR_TO_TEST_2', '2'),
        ('VAR_TO_TEST_3', '3'),
        # should use last instance in config_3.conf
        ('VAR_TO_TEST_A', 'A3'),
    ]
)
def test_move_all_to_config_section(metplus_config, config_key, expected_result):
    config_files = ['config_1.conf',
                    'config_2.conf',
                    'config_3.conf',
                   ]
    test_dir = os.path.dirname(__file__)
    config_files = [os.path.join(test_dir, item) for item in config_files]
    config = metplus_config(config_files)
    assert(config.getstr('config', config_key) == expected_result)

@pytest.mark.parametrize(
    'overrides, config_key, expected_result', [
        (['config.CMD_LINE_1=1',
          ],
        'CMD_LINE_1', '1'),
        (['dir.CMD_LINE_1=1',
          ],
        'CMD_LINE_1', '1'),
        (['filename_templates.CMD_LINE_1=1',
          ],
        'CMD_LINE_1', '1'),
        (['user_env_vars.CMD_LINE_1=1',
          ],
        'CMD_LINE_1', ''),
        (['made_up.CMD_LINE_1=1',
          ],
        'CMD_LINE_1', ''),
        (['config.CMD_LINE_1=1',
          'dir.CMD_LINE_1=2',
          ],
        'CMD_LINE_1', '2'),
        (['dir.CMD_LINE_1=1',
          'config.CMD_LINE_1=2',
          ],
        'CMD_LINE_1', '2'),
    ]
)
def test_move_all_to_config_section_cmd_line(metplus_config, overrides,
                                             config_key, expected_result):
    config = metplus_config(overrides)
    assert(config.getstr('config', config_key, '') == expected_result)

@pytest.mark.parametrize(
    'config_name, expected_result', [

        ('config.RAW_WITH_TAG',
         'some stuff {valid?fmt=%Y%m%d} other'
         ),
        ('config.RAW_WITH_TAG_AND_VAR',
         'some stuff {valid?fmt=%Y%m%d} A1 other'
         ),
        ('config.NESTED_BRACES',
         "value = { name='some_value_{init?fmt=%Y}';}"
         ),
        # variable that references a variable that references a variable
        ('config.SECOND_REF',
         "value"
         ),
        # variable that references a variable that references a variable x5
        ('config.FIFTH_REF',
         "some text value"
         ),
        # circular reference
        ('config.YOU_GOT_I',
         ''
         ),
        # improperly formatted value
        ('config.BAD_VAR',
         'FIRST_REF} {valid?fmt=%Y%m%d}'
         ),
        ('config.GRID_STAT_MET_CONFIG_OVERRIDES',
         ('climo_mean = {field = [{name= "/d1/projects/CPC_data/scripts/'
          'precip_climo_mean_embedded.py /d1/projects/CPC_data/input/'
          'MET_precip_climos/precip_clim_mean_unsmoothed_07d.nc:'
          '{valid?fmt=%d%m}"}]}; climo_stdev = {field = [{name= "/d1/projects/'
          'CPC_data/scripts/precip_climo_mean_embedded.py /d1/projects/'
          'CPC_data/input/MET_precip_climos/precip_clim_std_unsmoothed_07d.nc:'
          '{valid?fmt=%d%m}";}]};')
         ),
        # from another setion
        ('user_env_vars.USER_VALUE',
         'some stuff {valid?fmt=%Y%m%d} A1 other'
         ),
    ]
)
def test_getraw_nested_curly_braces(metplus_config,
                                    config_name,
                                    expected_result):
    config_files = ['config_1.conf',
                   ]
    test_dir = os.path.dirname(__file__)
    config_files = [os.path.join(test_dir, item) for item in config_files]
    config = metplus_config(config_files)
    sec, name = config_name.split('.', 1)
    assert(config.getraw(sec, name) == expected_result)
