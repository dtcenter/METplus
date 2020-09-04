#!/usr/bin/env python

import os
import sys
import re
import csv
import pytest

import produtil

from metplus.wrappers.tc_pairs_wrapper import TCPairsWrapper
from metplus.util import met_util as util


#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


#@pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")


#
# ------------Pytest fixtures that can be used for all tests ---------------
#
#@pytest.fixture
def tc_pairs_wrapper(metplus_config):
    """! Returns a default TCPairsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TCPairsWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'tc_pairs_wrapper_test.conf'))
    config = metplus_config(extra_configs)
    return TCPairsWrapper(config)

def test_no_empty_mod_dir(metplus_config):
    """ Verify that we are creating the modified extra tropical cyclone
        files. """
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    # This test is for extra tropical cyclone data (non-ATCF data)
    if not rtcp.c_dict['REFORMAT_DECK']:
        pytest.skip('This test is for extra tropical cyclone data.')
    rtcp.run_all_times()
    tc_mods_dir = rtcp.config.getdir('TC_PAIRS_REFORMAT_DIR')
    dirs_list = os.listdir(tc_mods_dir)
    assert len(dirs_list) == 1


def test_no_empty_tcp_dir(metplus_config):
    """ Verify that we are creating tc pair output"""
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    rtcp.run_all_times()
    tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_OUTPUT_DIR')
    assert os.listdir(tc_pairs_dir)


def test_one_less_column(metplus_config):
    """ Tests the read_modify_write_file() method.
        Verify that the output: in the track_data_atcf directory
        has one fewer column than the input track data.
    """
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    track_data_dir = rtcp.config.getdir('TC_PAIRS_ADECK_INPUT_DIR')
    track_data_subdir_mod = rtcp.config.getdir('TC_PAIRS_REFORMAT_DIR')
    if not rtcp.config.getbool('config', 'TC_PAIRS_REFORMAT_DECK'):
        pytest.skip("This test is for extra tropical cyclone (non-ATCF) data.")

    rtcp.run_all_times()
    # So that we have independence of the start and end times indicated
    # in the metplus.conf or any other conf file, perform the test as
    # follows:
    # 1) get a list of directories in the track_data_dir and
    #    track_data_subdir_mod
    # 2) use the first directory of each in #1
    # 3) then look at the first file in each of those directories in #2
    # We don't need to have matching dates and filename in the original and
    # modified files, since we are only interested in the *number* of
    # columns in the files.
    orig_dir_list = os.listdir(track_data_dir)
    mod_dir_list = os.listdir(track_data_subdir_mod)
    orig_first_file_list = os.listdir(
            os.path.join(track_data_dir, orig_dir_list[0]))
    mod_first_file_list = os.listdir(
            os.path.join(track_data_subdir_mod, mod_dir_list[0]))
    orig_first_file = orig_first_file_list[0]
    mod_first_file = mod_first_file_list[0]
    orig_tc_file = os.path.join(track_data_dir, orig_dir_list[0],
                                orig_first_file)
    mod_tc_file = os.path.join(track_data_subdir_mod, mod_dir_list[0],
                               mod_first_file)
    # Get the number of columns from the first row of the original and
    # modified files, respectively.
    with open(orig_tc_file, newline='') as f:
        reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
        first_row = next(reader)
        orig_num_cols = len(first_row)
    with open(mod_tc_file, newline='') as f:
        reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
        first_row = next(reader)
        mod_num_cols = len(first_row)

    assert mod_num_cols == (orig_num_cols - 1)


def test_col2_format_ok(metplus_config):
    """Tests for proper behavior in the read_modify_write_file() method
       Verify that the second column of one of the modified tc track files
       does indeed have the month followed by the storm id:
       Get the first row of the first file in the same subdirectory of the
       modified and input directory (i.e. same month)
    """
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    if not rtcp.config.getbool('config', 'TC_PAIRS_REFORMAT_DECK'):
        pytest.skip("Skip this test, this is for non-ATCF_by_pairs data.")
    rtcp.run_all_times()
    track_data_dir = rtcp.config.getdir('TC_PAIRS_ADECK_INPUT_DIR')
    track_data_subdir_mod = rtcp.config.getdir('TC_PAIRS_REFORMAT_DIR')
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
        with open(orig_tc_file, newline='') as f:
            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
            first_row = next(reader)
            orig_storm_id = first_row[1]
        with open(mod_tc_file, newline='') as f:
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


def test_num_files_in_subdir_mod_for_201412(metplus_config):
    """ Verify that for 201412 GFS data in /d1/SBU/GFS,
        the track_data_atcf directory (containing the reformatted extra-tropical cyclone
        data now in ATCF_by_pairs format) contains 450 files"""
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    if not rtcp.config.getbool('config', 'TC_PAIRS_REFORMAT_DECK'):
        pytest.skip("Skip this test, this is for non-ATCF_by_pairs data.")

    rtcp.run_all_times()
    request_subdir = "201412"
    atcf_dir = os.path.join(
            rtcp.config.getdir('TC_PAIRS_REFORMAT_DIR'),
            request_subdir)
    subdir_mod_file_list = os.listdir(atcf_dir)
    assert len(subdir_mod_file_list) == 450

def test_top_level_dir(metplus_config):
    # Verify that invoking tc_pairs with top-level directories for A-deck and B-deck
    # track files yields the expected results (for test data from Mallory, located on
    # 'eyewall' under /d1/METplus_TC/adeck and /d1/METplus_TC/bdeck directories), an expected number of
    # rows are in the .tcst file created.
    pytest.skip('Tests need to be written to match refactor')

    rtcp = tc_pairs_wrapper(metplus_config)
    if rtcp.config.getbool('config', 'TC_PAIRS_REFORMAT_DECK'):
        pytest.skip("Skip test_top_level_dir, this is for ATCF_by_pairs data and based on TRACK_TYPE, " +
                    "this is non-ATCF_by_pairs data.")
    if rtcp.c_dict['READ_ALL_FILES'] is False:
        pytest.skip("Skip, this is a test for tc-pairs via top-level input dirs.")

    # Capture all the available data
    rtcp.c_dict['INIT_BEG'] = "20170101"
    rtcp.c_dict['INIT_END'] = "20171231"

    rtcp.run_all_times()
    output_file = os.path.join(rtcp.c_dict['OUTPUT_DIR'], "tc_pairs.tcst")
    num_lines = len(open(output_file).readlines())

    # This number was obtained by running MET tc-pairs at the command line with empty values in the MET
    # config file, match_points = False,  and then obtaining the line count of the resulting .tcst file.
    expected_number_results = 27762

    # This is the expected value when match_points = True in the MET config file
    # expected_number_results = 7299

    assert num_lines == expected_number_results

def test_filter_by_region_nhc_data(metplus_config):
    pytest.skip("This test needs to be rewritten to check new filtering method")
    # Verify that the init list is OK
    rtcp = tc_pairs_wrapper(metplus_config)
    # Skip if by top level dir
    by_top_level = rtcp.c_dict['TOP_LEVEL_DIRS'].lower()
    if by_top_level == 'yes':
        pytest.skip("This test is for data that is to be filtered")
    # Skip if not ATCF
    if rtcp.c_dict['TRACK_TYPE'] == 'extra_tropical_cyclone':
        pytest.skip("This test is for ATCF data.")
    adeck_dir = rtcp.c_dict['ADECK_TRACK_DATA_DIR'] = '/d1/METplus_TC/NHC_from_Mallory/atcf-navy/aid'
    bdeck_dir = rtcp.c_dict['BDECK_TRACK_DATA_DIR'] = '/d1/METplus_TC/NHC_from_Mallory/atcf-navy/btk'
    forecast_tmpl = rtcp.c_dict['FORECAST_TMPL'] = \
        '/d1/METplus_TC/NHC_from_Mallory/atcf-navy/aid/a{region?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat'
    reference_tmpl = rtcp.c_dict['REFERENCE_TMPL'] =\
        '/d1/METplus_TC/NHC_from_Mallory/atcf-navy/btk/b{region?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat'
    region = rtcp.c_dict['BASIN'] = ['wp', 'al']

    # Number of expected files filtered by date for this data set: 124 atcf files for 201708* and 4 for 20170901*
    # num_expected = 43
    num_expected_wp_al = 45

    file_regex, sorted_keywords = rtcp.create_filename_regex(forecast_tmpl)

    all_files = []
    for dirpath, _, filenames in os.walk(adeck_dir):
        for f in filenames:
            all_files.append(os.path.join(dirpath, f))

    filtered_by_region = rtcp.filter_by_region(all_files, file_regex, sorted_keywords)
    actual_num = len(filtered_by_region)
    assert actual_num == num_expected_wp_al


def test_filter_by_region_data(metplus_config):
    pytest.skip("This test needs to be rewritten to check new filtering method")
    # Verify that filtering bdeck data from Mallory is correct. The bdeck data has cyclone, region/basin, and
    # date in the filename.

    rtcp = tc_pairs_wrapper(metplus_config)
    # Skip if by top level dir
    by_top_level = rtcp.c_dict['TOP_LEVEL_DIRS'].lower()
    if by_top_level == 'yes':
        pytest.skip("This test is for data that is to be filtered")
    # Skip if not ATCF
    if rtcp.c_dict['TRACK_TYPE'] == 'extra_tropical_cyclone':
        pytest.skip("This test is for ATCF data.")

    bdeck_dir = rtcp.c_dict['BDECK_TRACK_DATA_DIR'] = '/d1/METplus_TC/bdeck'
    reference_tmpl = rtcp.c_dict['REFERENCE_TMPL'] =\
        '/d1/METplus_TC/NHC_from_Mallory/atcf-navy/btk/b{region?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat'
    region = rtcp.c_dict['BASIN'] = ['wp', 'al']

    # 19 Files of format bal##YYYY.dat in /d1/METplus_TC/bdeck on eyewall
    num_expected_wp_al = 19

    file_regex, sorted_keywords = rtcp.create_filename_regex(reference_tmpl)

    all_files = []
    for dirpath, _, filenames in os.walk(bdeck_dir):
        for f in filenames:
            all_files.append(os.path.join(dirpath, f))

    filtered_by_region = rtcp.filter_by_region(all_files, file_regex, sorted_keywords)
    actual_num = len(filtered_by_region)
    assert actual_num == num_expected_wp_al

