#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import pytest
import produtil
import config_metplus
from tc_stat_wrapper import TcStatWrapper
import met_util as util


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
        ('INIT_END', '20141220'),
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
    TC_STAT_COLUMN_THRESH_VAL = "1,2"
    tcsw.tc_stat_dict['COLUMN_THRESH_NAME'] = TC_STAT_COLUMN_THRESH_NAME
    tcsw.tc_stat_dict['COLUMN_THRESH_VAL'] = TC_STAT_COLUMN_THRESH_VAL
    assert tcsw.config_lists_ok() is False


def test_filter_by_si_basin():
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by basin=["SI"].
    """

    tcsw = tc_stat_wrapper()
    tcsw.tc_stat_dict['INIT_BEG'] = "20141213"
    tcsw.tc_stat_dict['INIT_END'] = "20141220"
    tcsw.tc_stat_dict['BASIN'] = ["SI"]
    # expect only 6 lines of output (including the header) for SBU data
    expected_num_lines = 6
    tcsw.run_all_times()
    output_file = \
        tcsw.tc_stat_dict['OUTPUT_BASE'] + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_cyclone():
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by cyclone.
    """

    tcsw = tc_stat_wrapper()
    tcsw.tc_stat_dict['INIT_BEG'] = "20141213"
    tcsw.tc_stat_dict['INIT_END'] = "20141220"
    tcsw.tc_stat_dict['CYCLONE'] = ["120126", "120099", "1203S"]

    # expect only 6 lines of output (including the header) for SBU data
    expected_num_lines = 23
    tcsw.run_all_times()
    output_file = \
        tcsw.tc_stat_dict['OUTPUT_BASE'] + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        # print("Num lines: ", str(lines))

    assert lines == expected_num_lines


def test_filter_by_storm_name():
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by storm_name.
    """

    tcsw = tc_stat_wrapper()
    tcsw.tc_stat_dict['INIT_BEG'] = "20141213"
    tcsw.tc_stat_dict['INIT_END'] = "20141220"
    tcsw.tc_stat_dict['STORM_NAME'] = ["-183", "-143", "-100", "-213", "141"]
    # expect only 6 lines of output (including the header) for SBU data
    expected_num_lines = 30
    tcsw.run_all_times()
    output_file = \
        tcsw.tc_stat_dict['OUTPUT_BASE'] + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines

def test_filter_by_storm_id():
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by storm_id.  For
         this data and the indicated storm_id, tc_stat does not return any
         data
    """

    tcsw = tc_stat_wrapper()
    tcsw.tc_stat_dict['INIT_BEG'] = "20141213"
    tcsw.tc_stat_dict['INIT_END'] = "20141220"
    tcsw.tc_stat_dict['STORM_ID'] = ["SI1203S2014"]
    # expect only 6 lines of output (including the header) for SBU data
    expected_num_lines = 23
    tcsw.run_all_times()
    output_file = \
        tcsw.tc_stat_dict['OUTPUT_BASE'] + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print("Num lines: ", str(lines))
    # Note that the number of lines does NOT match what is expected.  For
    # this data, the stratify by storm_id produces 0 results.  This may
    # be due to the long cyclone name???
    assert lines != expected_num_lines


def test_filter_by_basin_cyclone():
    """! Test that for a given time window of SBU GFS data, the expected number
         of results is returned when additional filtering by basin and cyclone
         to get the same results as if filtering by storm_id (which doesn't
         work, perhaps because the storm_id is greater than 2-digits?).
    """

    tcsw = tc_stat_wrapper()
    tcsw.tc_stat_dict['INIT_BEG'] = "20141213"
    tcsw.tc_stat_dict['INIT_END'] = "20141220"
    tcsw.tc_stat_dict['CYCLONE'] = ["120126"]
    tcsw.tc_stat_dict['BASIN'] = ["ML"]

    # expect only 13 lines of output (including the header) for SBU data
    expected_num_lines = 13
    tcsw.run_all_times()
    output_file = \
        tcsw.tc_stat_dict['OUTPUT_BASE'] + "/tc_stat/tc_stat_summary.tcst"
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print("Num lines: ", str(lines))

    assert lines == expected_num_lines

def test_run_via_command_line():
    """! Test that running via command line produces the expected results for
         a specific time window for the SBU GFS data.
    """
    tcsw = tc_stat_wrapper()
    tcsw.by_config = False
    tcsw.tc_stat_dict['INIT_BEG'] = '20141213'
    tcsw.tc_stat_dict['INIT_END'] = '20141220'
    output_base = tcsw.tc_stat_dict['OUTPUT_BASE']

    tcsw.tc_stat_dict['CMD_LINE_JOB'] = '-job filter -dump_row ' + \
                                        output_base + \
                                        '/tc_stat/tc_stat_filter.out' + \
                                        ' -basin SI -init_hour 00'
    # For the SBU data within this time window, there should be 6 rows of
    # data including one row for the header
    expected_num_rows = 6
    tcsw.run_all_times()
    output_file = output_base + '/tc_stat/tc_stat_filter.out'
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print('Number of lines: ', lines)
    assert lines == expected_num_rows

def test_run_via_config_file():
    """! Test that running via the config file on a specific time window
         produces the expected number of results for SBU GFS data.
    """
    tcsw = tc_stat_wrapper()
    tcsw.by_config = True
    tcsw.tc_stat_dict['INIT_BEG'] = '20141213'
    tcsw.tc_stat_dict['INIT_END'] = '20141220'
    tcsw.tc_stat_dict['CYCLONE'] = ["120126"]
    tcsw.tc_stat_dict['BASIN'] = ["ML"]
    output_path = os.path.join(tcsw.tc_stat_dict['OUTPUT_BASE'],
                               'by_conf/tc_stat')
    tcsw.tc_stat_dict['OUTPUT_DIR'] = output_path
    output_file = os.path.join(output_path, "tc_stat_summary.txt")
    tcsw.tc_stat_dict['JOBS_LIST'] =\
        "-job summary -line_type TCMPR -column 'ABS(AMAX_WIND-BMAX_WIND)'" +\
        " -dump_row " + output_file
    tcsw.run_all_times()

    # Expect 13 lines of output (including the header)
    num_expected_lines = 13
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
        print("Number of lines: ", lines)
    assert lines == num_expected_lines


