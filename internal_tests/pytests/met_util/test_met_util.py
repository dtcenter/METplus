#!/usr/bin/env python
from __future__ import print_function
import sys
import pytest
import met_util as util
import produtil
import os
import config_metplus

@pytest.fixture
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
        produtil.log.postmsg('met_util test is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'met_util test failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_add_common_items_to_dictionary():
    conf = metplus_config()
    dictionary = dict()
    util.add_common_items_to_dictionary(conf, dictionary)
    assert(dictionary['WGRIB2'] == conf.getexe('WGRIB2'))
