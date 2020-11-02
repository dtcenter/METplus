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
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'tc_pairs_wrapper_test.conf'))
    config = metplus_config(extra_configs)
    return TCPairsWrapper(config)

def test_top_level_dir(metplus_config):
    # Verify that invoking tc_pairs with top-level directories for A-deck and B-deck
    # track files yields the expected results (for test data from Mallory, located on
    # 'eyewall' under /d1/METplus_TC/adeck and /d1/METplus_TC/bdeck directories), an expected number of
    # rows are in the .tcst file created.

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
#    pytest.skip("This test needs to be rewritten to check new filtering method")
    # Verify that the init list is OK
    rtcp = tc_pairs_wrapper(metplus_config)
    # Skip if by top level dir
    by_top_level = rtcp.c_dict['READ_ALL_FILES']
    if by_top_level:
        pytest.skip("This test is for data that is to be filtered")
    # Skip if not ATCF
    if rtcp.c_dict['REFORMAT_DECK'] and rtcp.c_dict['REFORMAT_DECK_TYPE'] == 'SBU':
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
#    pytest.skip("This test needs to be rewritten to check new filtering method")
    # Verify that filtering bdeck data from Mallory is correct. The bdeck data has cyclone, region/basin, and
    # date in the filename.

    rtcp = tc_pairs_wrapper(metplus_config)
    # Skip if by top level dir
    by_top_level = rtcp.c_dict['READ_ALL_FILES']
    if by_top_level:
        pytest.skip("This test is for data that is to be filtered")
    # Skip if not ATCF
    if rtcp.c_dict['REFORMAT_DECK'] and rtcp.c_dict['REFORMAT_DECK_TYPE'] == 'SBU':
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

