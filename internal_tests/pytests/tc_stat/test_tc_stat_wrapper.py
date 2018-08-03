#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import re
import csv
import pytest
import produtil
import config_metplus
from tc_stat_wrapper import TcStatWrapper

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")


#
# ------------Pytest fixtures that can be used for all tests ---------------
#
@pytest.fixture
def tc_stat_wrapper():
    """! Returns a default TCStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TcStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return TcStatWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='TcStatWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='TcStatWrapper ')
        produtil.log.postmsg('tc_stat_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'tc_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


@pytest.mark.parametrize(
    'key, value', [
        ('APP_PATH', '/usr/local/met-6.1/bin/tc_stat'),
        ('APP_NAME', 'tc_stat'),
        ('INIT_BEG', '20141213'),
        ('INIT_END', '20141213'),
        ('INIT_HOUR', ['00'])
    ]
)
def test_tc_stat_dict(key, value):
    """! Test that the expected values set in the tc_stat_filter.conf
         file are correctly read/captured in the tc_stat_dict dictionary
    """
    tcsw = tc_stat_wrapper()
    actual_value = tcsw.tc_stat_dict[key]
    assert actual_value == value


def test_config_lists():
    """! Test that when the COLUMN_THRESH_NAME and COLUMN_THRESH_VAL lists
         are of different length, the appropriate value is returned
         from config_lists_ok()
    """
    tcsw = tc_stat_wrapper()

    # Uneven lengths, expect False to be returned
    TC_STAT_COLUMN_THRESH_NAME = "A, B, C"
    TC_STAT_COLUMN_THRESH_VAL =  "1,2"
    tcsw.tc_stat_dict['COLUMN_THRESH_NAME'] = TC_STAT_COLUMN_THRESH_NAME
    tcsw.tc_stat_dict['COLUMN_THRESH_VAL'] = TC_STAT_COLUMN_THRESH_VAL
    assert tcsw.config_lists_ok() is False














