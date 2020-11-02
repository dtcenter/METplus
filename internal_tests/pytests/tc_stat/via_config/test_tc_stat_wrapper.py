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


def tc_stat_wrapper(metplus_config):
    """! Returns a default TCStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TcStatWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'tc_stat_conf.conf'))
    config = metplus_config(extra_configs)
    return TCStatWrapper(config)

def test_config_lists(metplus_config):
    """! Test that when the COLUMN_THRESH_NAME and COLUMN_THRESH_VAL lists
         are of different length, the appropriate value is returned
         from config_lists_ok()
    """
    tcsw = tc_stat_wrapper(metplus_config)

    # Uneven lengths, expect False to be returned
    column_thresh_name = "A, B, C"
    column_thresh_val = "1,2"
    tcsw.c_dict['COLUMN_THRESH_NAME'] = column_thresh_name
    tcsw.c_dict['COLUMN_THRESH_VAL'] = column_thresh_val
    tcsw.validate_config_values(tcsw.c_dict)
    assert tcsw.isOK is False

def test_filter_by_ml_basin(metplus_config):
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by basin=["ML"].
    """
    pytest.skip("This will be rewritten to verify the METplus sets the "
                "MET config value correctly in another test")
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.c_dict['INIT_BEG'] = 'init_beg = "20150301";'
    tcsw.c_dict['INIT_END'] = 'init_end = "20150304";'
    tcsw.c_dict['BASIN'] = 'basin = ["ML"];'
    # expect 352 lines of output (including the header) for SBU data
    expected_num_lines = 352
    tcsw.run_all_times()
    output_file = \
        tcsw.config.getdir('OUTPUT_BASE') + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_cyclone(metplus_config):
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by cyclone.
    """
    pytest.skip("This will be rewritten to verify the METplus sets the "
                "MET config value correctly in another test")
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.c_dict['INIT_BEG'] = 'init_beg = "20150301";'
    tcsw.c_dict['INIT_END'] = 'init_end = "20150304";'
    tcsw.c_dict['CYCLONE'] = 'cyclone = ["030020"];'

    # expect only 13 lines of output (including the header) for SBU data
    expected_num_lines = 9
    tcsw.run_all_times()
    output_file = \
        tcsw.config.getdir('OUTPUT_BASE') + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_storm_name(metplus_config):
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by storm_name.
    """
    pytest.skip("This will be rewritten to verify the METplus sets the "
                "MET config value correctly in another test")
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.c_dict['INIT_BEG'] = 'init_beg = "20150301";'
    tcsw.c_dict['INIT_END'] = 'init_end = "20150325";'
    tcsw.c_dict['STORM_NAME'] = 'storm_name = ["123"];'
    # expect only 13 lines of output (including the header) for SBU data
    expected_num_lines = 15
    tcsw.run_all_times()
    output_file = \
        tcsw.config.getdir('OUTPUT_BASE') + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_storm_id(metplus_config):
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by storm_id.  For
         this data and the indicated storm_id, tc_stat does not return any
         data
    """
    pytest.skip("This will be rewritten to verify the METplus sets the "
                "MET config value correctly in another test")
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.c_dict['INIT_BEG'] = 'init_beg = "20150301";'
    tcsw.c_dict['INIT_END'] = 'init_end = "20150304";'
    tcsw.c_dict['INIT_HOUR'] = ''
    tcsw.c_dict['STORM_ID'] = 'storm_id = ["ML032015"];'
    # expect 1148 lines of output (including the header) for SBU data
    expected_num_lines = 1148
    tcsw.run_all_times()
    output_file = \
        tcsw.config.getdir('OUTPUT_BASE') + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_basin_cyclone(metplus_config):
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by basin and cyclone
         to get the same results as if filtering by storm_id (which doesn't
         work, perhaps because the storm_id is greater than 2-digits?).
    """
    pytest.skip("This will be rewritten to verify the METplus sets the "
                "MET config value correctly in another test")
    tcsw = tc_stat_wrapper(metplus_config)
    tcsw.c_dict['INIT_BEG'] = 'init_beg = "20150301";'
    tcsw.c_dict['INIT_END'] = 'init_end = "20150304";'
    tcsw.c_dict['INIT_HOUR'] = ''
    tcsw.c_dict['CYCLONE'] = 'cyclone = ["030020"];'
    tcsw.c_dict['BASIN'] = 'basin = ["ML"];'

    # expect only 13 lines of output (including the header) for SBU data
    expected_num_lines = 31
    tcsw.run_all_times()
    output_file = \
        tcsw.config.getdir('OUTPUT_BASE') + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as out_file:
        lines = len(out_file.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines
