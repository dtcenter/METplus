#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import re
import csv
import pytest
import produtil
import config_metplus
from tc_pairs_wrapper import TcPairsWrapper

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
# def pytest_addoption(parser):
#     parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
# def cmdopt(request):
#     return request.config.getoption("-c")


#
# ------------Pytest fixtures that can be used for all tests ---------------
#
@pytest.fixture
def tc_pairs_wrapper():
    """! Returns a default TCPairsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty PointStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return TcPairsWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='PointStatWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='PointStatWrapper ')
        produtil.log.postmsg('point_stat_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'point_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# def test_no_empty_mod_dir():
#     """ Verify that we are creating the ATCF files. """
#     rtcp = tc_pairs_wrapper()
#     tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
#     dirs_list = os.listdir(tc_pairs_dir)
#     assert len(dirs_list) == 1
#
#
# def test_no_empty_tcp_dir():
#     """ Verify that we are creating tc pair output"""
#     rtcp = tc_pairs_wrapper()
#     rtcp.run_all_times()
#     tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
#     assert os.listdir(tc_pairs_dir)


# def test_one_less_column():
#     """ Tests the read_modify_write_file() method.
#         Verify that the output: in the track_data_atcf directory
#         has one fewer column than the input track data.
#     """
#     rtcp = tc_pairs_wrapper()
#     rtcp.run_all_times()
#     track_data_dir = rtcp.config.getdir('TRACK_DATA_DIR')
#     track_data_subdir_mod = rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD')
#
#     # So that we have independence of the start and end times indicated
#     # in the metplus.conf or any other conf file, perform the test as
#     # follows:
#     # 1) get a list of directories in the track_data_dir and
#     #    track_data_subdir_mod
#     # 2) use the first directory of each in #1
#     # 3) then look at the first file in each of those directories in #2
#     # We don't need to have matching dates and filename in the original and
#     # modified files, since we are only interested in the *number* of
#     # columns in the files.
#     orig_dir_list = os.listdir(track_data_dir)
#     mod_dir_list = os.listdir(track_data_subdir_mod)
#     orig_first_file_list = os.listdir(
#             os.path.join(track_data_dir, orig_dir_list[0]))
#     mod_first_file_list = os.listdir(
#             os.path.join(track_data_subdir_mod, mod_dir_list[0]))
#     orig_first_file = orig_first_file_list[0]
#     mod_first_file = mod_first_file_list[0]
#     orig_tc_file = os.path.join(track_data_dir, orig_dir_list[0],
#                                 orig_first_file)
#     mod_tc_file = os.path.join(track_data_subdir_mod, mod_dir_list[0],
#                                mod_first_file)
#     # Get the number of columns from the first row of the original and
#     # modified files, respectively.
#     with open(orig_tc_file) as f:
#         reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#         first_row = next(reader)
#         orig_num_cols = len(first_row)
#     with open(mod_tc_file) as f:
#         reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#         first_row = next(reader)
#         mod_num_cols = len(first_row)
#
#     assert mod_num_cols == (orig_num_cols - 1)
#
#
def test_col2_format_ok():
    """Tests for proper behavior in the read_modify_write_file() method
       Verify that the second column of one of the modified tc track files
       does indeed have the month followed by the storm id:
       Get the first row of the first file in the same subdirectory of the
       modified and input directory (i.e. same month)
    """
    rtcp = tc_pairs_wrapper()
    rtcp.run_all_times()
    track_data_dir = rtcp.config.getdir('TRACK_DATA_DIR')
    track_data_subdir_mod = rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD')
    mod_dir_list = os.listdir(track_data_subdir_mod)

    # Get the first directory in the TRACK_DATA_SUBDIR_MOD directory and
    # the matching year-month dir in the TRACK_DATA_DIR directory.
    year_month_dir = mod_dir_list[0]
    mod_first_file_list = os.listdir(
        os.path.join(track_data_subdir_mod, year_month_dir))

    # Get the track file that corresponds to the modified track file's
    # first file.
    first_track_file = mod_first_file_list[0]
    mod_tc_file = os.path.join(track_data_subdir_mod, year_month_dir,
                               first_track_file)
    orig_tc_file = os.path.join(track_data_dir, year_month_dir,
                                first_track_file)

    # Get the month from the year_month_dir
    month_match = re.match(r'[0-9]{4}([0-9]{2})', year_month_dir)
    if month_match:
        month = month_match.group(1)

        # Get the number of columns from the first row of the original and
        # modified files, respectively.
        with open(orig_tc_file) as f:
            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
            first_row = next(reader)
            orig_storm_id = first_row[1]
        with open(mod_tc_file) as f:
            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
            first_row = next(reader)
            mod_storm_id = first_row[1]
        # Create the expected storm id and compare it to what was produced
        # in the modified file.
        expected_storm_id = month + orig_storm_id
        assert mod_storm_id == expected_storm_id
    else:
        # If no match, something is wrong, force test to fail.
        assert 0


#
def test_same_dates_in_mod_and_final_dir():
        """ Test that the dirs (i.e. dates) that were found in the modified dir
            are also found in the final track data output dir.  Verify that the
            list of dates in the TRACK_DATA_SUBDIR_MOD directory are equal to
            the list of dates in the TRACK_DATA_DIR directory.
        """
        rtcp = tc_pairs_wrapper()
        tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
        track_data_subdir_mod = rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD')
        rtcp.run_all_times()

        # First check that there are the same number of subdirectories in the
        # TC_PAIRS_DIR (the final output dir) and TRACK_DATA_SUBDIR_MOD
        # directories (i.e. the same number of year-month data).
        mod_year_month_list = os.listdir(track_data_subdir_mod)
        final_year_month_list = os.listdir(tc_pairs_dir)
        if len(final_year_month_list) == len(mod_year_month_list):
            # Make sure the dates in the TRACK_DATA_SUBDIR_MOD are found in the
            # TC_PAIRS_DIR.
            for year_month_dir in final_year_month_list:
                if year_month_dir not in mod_year_month_list:
                    # If the year_month directory in the final output directory
                    # doesn't exist in the mod directory, fail the test.
                    assert 0
        else:
            # If the directories don't have the same number of subdirectories,
            # something is wrong, force the test to fail.
            assert 0
        # If we get here, then the test passes
        assert True


def test_num_files_in_subdir_mod_for_201412():
    """ Verify that for 201412 GFS data in /d1/SBU/GFS,
        the track_data_atcf directory (containing the reformatted extra-tropical cyclone
        data now in ATCF format) contains 450 files"""
    rtcp = tc_pairs_wrapper()
    rtcp.run_all_times()
    request_subdir = "201412"
    atcf_dir = os.path.join(
            rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD'),
            request_subdir)
    subdir_mod_file_list = os.listdir(atcf_dir)
    assert len(subdir_mod_file_list) == 450
