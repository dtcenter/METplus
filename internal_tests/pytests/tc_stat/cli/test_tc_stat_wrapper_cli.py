#!/usr/bin/env python

from __future__ import print_function
import os
import sys
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
    """! For supporting config files from the command line"""
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    """! For supporting the additional config files used by METplus"""
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
    """! Generate the METplus config object"""
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


def test_run_via_command_line():
    """! Test that running via command line produces the expected results for
         a specific time window for the SBU GFS data.
    """
    tcsw = tc_stat_wrapper()
    tcsw.by_config = False
    tcsw.tc_stat_dict['INIT_BEG'] = '20170822'
    tcsw.tc_stat_dict['INIT_END'] = '20180508'
    output_base = tcsw.tc_stat_dict['OUTPUT_BASE']

    tcsw.tc_stat_dict['CMD_LINE_JOB'] = '-job filter -dump_row ' + \
                                        output_base + \
                                        '/tc_stat_filter.out' + \
                                        ' -basin AL -init_hour 00'
    # For the SBU data within this time window, there should be 13 rows of
    # data including one row for the header
    expected_num_rows = 13
    tcsw.run_all_times()
    output_file = output_base + '/tc_stat_filter.out'
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print('Number of lines: ', lines)
    assert lines == expected_num_rows
