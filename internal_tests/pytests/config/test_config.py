#!/usr/bin/env python
from __future__ import print_function
import sys
import pytest
import datetime
from config_wrapper import ConfigWrapper
import met_util as util
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
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='test ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test ')
        produtil.log.postmsg('config test is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
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
    conf = ConfigWrapper(metplus_config(), None)
    conf.set('config', 'TEST_SECONDS', key)
    seconds = conf.getseconds('config', 'TEST_SECONDS')
    assert(seconds == value)
