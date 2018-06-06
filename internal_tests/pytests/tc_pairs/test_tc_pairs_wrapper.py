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

    # Default, empty TcPairsWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return TcPairsWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='TCPairsWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='TCPairsWrapper ')
        produtil.log.postmsg('tc_pairs_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'tc_pairs_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# def test_no_empty_mod_dir():
#     """ Verify that we are creating the ATCF_by_pairs files. """
#     rtcp = tc_pairs_wrapper()
#     tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
#     dirs_list = os.listdir(tc_pairs_dir)
#     assert len(dirs_list) == 1
#
# #
# def test_no_empty_tcp_dir():
#     """ Verify that we are creating tc pair output"""
#     rtcp = tc_pairs_wrapper()
#     rtcp.run_all_times()
#     tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
#     assert os.listdir(tc_pairs_dir)
#
#
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


# def test_col2_format_ok():
#     """Tests for proper behavior in the read_modify_write_file() method
#        Verify that the second column of one of the modified tc track files
#        does indeed have the month followed by the storm id:
#        Get the first row of the first file in the same subdirectory of the
#        modified and input directory (i.e. same month)
#     """
#     rtcp = tc_pairs_wrapper()
#     track_type = rtcp.tcp_dict['TRACK_TYPE']
#     if track_type != 'extra_tropical_cyclone':
#         pytest.exit("Skip this test, this is for non-ATCF_by_pairs data and based on TRACK_TYPE, this is ATCF_by_pairs data.")
#     rtcp.run_all_times()
#     track_data_dir = rtcp.config.getdir('TRACK_DATA_DIR')
#     track_data_subdir_mod = rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD')
#     mod_dir_list = os.listdir(track_data_subdir_mod)
#
#     # Get the first directory in the TRACK_DATA_SUBDIR_MOD directory and
#     # the matching year-month dir in the TRACK_DATA_DIR directory.
#     year_month_dir = mod_dir_list[0]
#     mod_first_file_list = os.listdir(
#         os.path.join(track_data_subdir_mod, year_month_dir))
#
#     # Get the track file that corresponds to the modified track file's
#     # first file.
#     first_track_file = mod_first_file_list[0]
#     mod_tc_file = os.path.join(track_data_subdir_mod, year_month_dir,
#                                first_track_file)
#     orig_tc_file = os.path.join(track_data_dir, year_month_dir,
#                                 first_track_file)
#
#     # Get the month from the year_month_dir
#     month_match = re.match(r'[0-9]{4}([0-9]{2})', year_month_dir)
#     if month_match:
#         month = month_match.group(1)
#
#         # Get the number of columns from the first row of the original and
#         # modified files, respectively.
#         with open(orig_tc_file) as f:
#             reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#             first_row = next(reader)
#             orig_storm_id = first_row[1]
#         with open(mod_tc_file) as f:
#             reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#             first_row = next(reader)
#             mod_storm_id = first_row[1]
#         # Create the expected storm id and compare it to what was produced
#         # in the modified file.
#         expected_storm_id = month + orig_storm_id
#         assert mod_storm_id == expected_storm_id
#     else:
#         # If no match, something is wrong, force test to fail.
#         assert 0
#


# def test_num_files_in_subdir_mod_for_201412():
#     """ Verify that for 201412 GFS data in /d1/SBU/GFS,
#         the track_data_atcf directory (containing the reformatted extra-tropical cyclone
#         data now in ATCF_by_pairs format) contains 450 files"""
#     rtcp = tc_pairs_wrapper()
#     track_type = rtcp.tcp_dict['TRACK_TYPE']
#     if track_type != 'extra_tropical_cyclone':
#         pytest.exit("Skip this test, this is for non-ATCF_by_pairs data and based on TRACK_TYPE, this is ATCF_by_pairs data.")
#
#     rtcp.run_all_times()
#     request_subdir = "201412"
#     atcf_dir = os.path.join(
#             rtcp.config.getdir('TRACK_DATA_SUBDIR_MOD'),
#             request_subdir)
#     subdir_mod_file_list = os.listdir(atcf_dir)
#     assert len(subdir_mod_file_list) == 450

# def test_create_filename_regex():
#     """ Verify that the expected filename regex is created, based on the filename described in the filename_templates
#         section of the config file. There is a similar test in the StringTemplateSubstitution pytest.
#     """
#     # create_filename_regex(self, tmpl)
#     rtcp = tc_pairs_wrapper()
#     track_type = rtcp.tcp_dict['TRACK_TYPE']
#     if track_type == 'extra_tropical_cyclone':
#         pytest.exit("Skip test_create_filename_regex, this is for ATCF_by_pairs data and based on TRACK_TYPE, this is non-ATCF_by_pairs data.")
#     tmpl = '/d1/METplus_TC/bdeck/{date?fmt=%s}/b{region?fmt=%s}{cyclone?fmt=%s}{misc?fmt=%s}.dat'
#     regex_fname, sorted_keywords = rtcp.create_filename_regex(tmpl)
#     expected_regex_fname = '/d1/METplus_TC/bdeck/([0-9]{4,10})/b([a-zA-Z]{2})([0-9]{2,3})([a-zA-Z0-9-_.]+).dat'
#     print('EXPECTED: ', expected_regex_fname)
#     print('ACTUAL:   ', regex_fname)
#     assert regex_fname == expected_regex_fname


def test_top_level_dir():
    # Verify that invoking tc_pairs with top-level directories for A-deck and B-deck
    # track files yields the expected results (for test data from Mallory, located on
    # 'eyewall' under /d1/METplus_TC/adeck and /d1/METplus_TC/bdeck directories), an expected number of
    # rows are in the .tcst file created.
    rtcp = tc_pairs_wrapper()
    track_type = rtcp.tcp_dict['TRACK_TYPE']
    if track_type == 'extra_tropical_cyclone':
        pytest.exit("Skip test_top_level_dir, this is for ATCF_by_pairs data and based on TRACK_TYPE, this is non-ATCF_by_pairs data.")
    rtcp.tcp_dict['INIT_BEG'] = ""
    rtcp.tcp_dict['INIT_END'] = ""
    rtcp.run_all_times()
    output_file = os.path.join(rtcp.tcp_dict['TC_PAIRS_DIR'], "tc_pairs.tcst")
    num_lines = len(open(output_file).readlines())

    expected_number_results = 27762
    print('EXPECTED: ', expected_number_results)
    print('ACTUAL:   ', num_lines)
    assert num_lines == expected_number_results
