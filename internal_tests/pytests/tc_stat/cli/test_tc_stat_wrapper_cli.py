#!/usr/bin/env python

import os
import sys
import pytest
import produtil
from metplus.wrappers.tc_stat_wrapper import TCStatWrapper


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
#@pytest.fixture
def tc_stat_wrapper(metplus_config):
    """! Returns a default TCStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TcStatWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'tc_stat_cli.conf'))
    config = metplus_config(extra_configs)
    return TCStatWrapper(config)

def test_run_via_command_line(metplus_config):
    """! Test that running via command line produces the expected results for
         a specific time window for the SBU GFS data.
    """
    pytest.skip()
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.by_config = False
    tcsw.c_dict['INIT_BEG'] = '20170822'
    tcsw.c_dict['INIT_END'] = '20180508'
    output_base = tcsw.c_dict['OUTPUT_BASE']

    tcsw.c_dict['CMD_LINE_JOB'] = '-job filter -dump_row ' + \
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
