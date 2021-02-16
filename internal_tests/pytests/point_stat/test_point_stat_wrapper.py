#!/usr/bin/env python

import os
import datetime
import sys
import logging
import re
import pytest

from metplus.wrappers.point_stat_wrapper import PointStatWrapper
from metplus.util import met_util as util

#
# These are tests (not necessarily unit tests) for the
# MET Point-Stat Wrapper, PointStatWrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  point_stat_test.conf.  This contains
# the information necessary for running all the tests.  Each test can be
# customized to replace various settings if needed.
#

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
#@pytest.fixture
def point_stat_wrapper(metplus_config):
    """! Returns a default PointStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty PointStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return PointStatWrapper(conf)

# ------------------TESTS GO BELOW ---------------------------

@pytest.mark.parametrize(
    'key, value', [
        ('app_name', 'point_stat')

    ]
)
def test_config(metplus_config, key, value):
    pytest.skip('Needs to read config file - which?')
    psw = point_stat_wrapper(metplus_config)
    # assert isinstance(conf, METplusLauncher)
    # Retrieve the value of the class attribute that corresponds
    # to the key in the parametrization

    psw_key = psw.__getattribute__(key)
    assert(psw_key == value)


def test_correct_time_info_by_valid(metplus_config):
    pytest.skip('Hard-coded output directories do not match current setup')

    # Test that the time info derived from a particular file is
    # correct when selecting by valid time
    output_dir = '/tmp'
    fcst_filename = 'pgbf00.gfs.2017060112'
    obs_filename = 'prepbufr.gdas.2017060112.nc'
    expected_fcst_valid_str = '2017060112'
    expected_obs_valid_str = '2017060112'
    fcst_filepath = os.path.join(output_dir, fcst_filename)
    obs_filepath = os.path.join(output_dir, obs_filename)
    ps = point_stat_wrapper(metplus_config)
    # First, get the fcst and obs file regular expressions
    fcst_file_tmpl = 'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H}'
    fcst_file_regex_tuple = ps.create_filename_regex(fcst_file_tmpl)
    obs_file_tmpl = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}'
    fcst_file_regex = '.*' + fcst_file_regex_tuple[0]
    obs_file_regex_tuple = ps.create_filename_regex(obs_file_tmpl)
    obs_file_regex = '.*' + obs_file_regex_tuple[0]
    fcst_compile = re.compile(fcst_file_regex)
    obs_compile = re.compile(obs_file_regex)
    fcst_match = re.match(fcst_compile, fcst_filepath)
    obs_match = re.match(obs_compile, obs_filepath)
    full_fcst_input_regex = ".*/" + fcst_file_regex_tuple[0]
    full_fcst_keywords = fcst_file_regex_tuple[1]
    fcst_time_info = ps.get_time_info_from_file(fcst_match,
                                                full_fcst_input_regex,
                                                full_fcst_keywords)
    full_obs_input_regex = ".*/" + obs_file_regex_tuple[0]
    full_obs_keywords = obs_file_regex_tuple[1]
    obs_time_info = ps.get_time_info_from_file(obs_match, full_obs_input_regex,
                                               full_obs_keywords)

    fcst_valid = datetime.datetime.fromtimestamp(
        fcst_time_info.valid).strftime('%Y%m%d%H')
    obs_valid = datetime.datetime.fromtimestamp(
        obs_time_info.valid).strftime(
        '%Y%m%d%H')
    assert (expected_fcst_valid_str == fcst_valid)
    assert (expected_obs_valid_str == obs_valid)


def test_file_info_by_valid_correct_for_gdas(metplus_config):
    pytest.skip('Hard-coded output directories do not match current setup')

    # Test that the resulting tuple from create_input_file_info() is correct
    # when selecting by valid time for obs files
    ps = point_stat_wrapper(metplus_config)
    ps.ps_dict['OBS_INPUT_FILE_TMPL'] = "prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc"
    ps.ps_dict['OBS_INPUT_DIR_REGEX'] = ""
    ps.ps_dict[
        'OBS_INPUT_DIR'] = '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr'
    ps.ps_dict['VALID_START_DATE'] = '2017060100'
    ps.ps_dict['VALID_END_DATE'] = '2017060323'
    ps.ps_dict['FCST_HR_START'] = '00'
    ps.ps_dict['FCST_HR_END'] = '96'
    ps.ps_dict['FCST_HR_INTERVAL'] = '24'
    # Based on the files in the input directory above, these are the fcst
    # files
    # that are used for the test:
    # prepbufr.20170601.t12z.tm00.nc
    # prepbufr.20170601.t18z.tm00.nc
    # prepbufr.20170602.t00z.tm03.nc
    # prepbufr.20170602.t18z.tm00.nc
    # prepbufr.20170603.t00z.tm00.nc
    # prepbufr.20170603.t00z.tm03.nc
    expected_obs_filepaths = [
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.gdas.2017060100.nc',
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.gdas.2017060200.nc',
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.gdas.2017060300.nc'


    ]
    expected_obs_valid_times = ['2017060100', '2017060200', '2017060300']

    file_type = "obs"
    consolidated_obs_list = ps.create_input_file_info(file_type)
    if len(expected_obs_filepaths) == len(consolidated_obs_list):
        for obs in consolidated_obs_list:
            print('obs:', obs)
            if obs.full_filepath in expected_obs_filepaths:
                expected_obs_filepaths.remove(obs.full_filepath)
            valid_time_str = datetime.datetime.fromtimestamp(
                obs.valid_time).strftime('%Y%m%d%H')
            if valid_time_str in expected_obs_valid_times:
                expected_obs_valid_times.remove(valid_time_str)

        if len(expected_obs_filepaths) > 0:
            # Exact match to expected obs filepaths was not met, fail
            assert True is False

        if len(expected_obs_valid_times) > 0:
            # Exact match expected for init times not met, fail
            assert True is False

    else:
        # Number of results not expected, fail
        assert True is False


def test_file_info_by_valid_correct_for_nam(metplus_config):
    pytest.skip('Hard-coded output directories do not match current setup')

    # Test that the resulting tuple from create_input_file_info() is correct
    # when selecting by valid time for obs files
    ps = point_stat_wrapper(metplus_config)
    ps.ps_dict['OBS_INPUT_DIR'] = '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr'
    ps.ps_dict['VALID_START_DATE'] = '2017060100'
    ps.ps_dict['VALID_END_DATE'] = '2017060323'
    ps.ps_dict['FCST_HR_START'] = '0'
    ps.ps_dict['FCST_HR_END'] = '24'
    ps.ps_dict['FCST_HR_INTERVAL'] = 12
    ps.ps_dict['OBS_INPUT_DIR_REGEX'] = ''
    ps.ps_dict['OBS_INPUT_FILE_TMPL'] = 'prepbufr.nam.{init?fmt=%Y%m%d}.t{cycle?fmt=%H}z.tm{offset?fmt=%H}.nc'
    ps.ps_dict['FCST_INPUT_DIR_REGEX'] = ''
    ps.ps_dict['FCST_INPUT_FILE_TMPL']= 'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H} '

    # Based on the files in the input directory above, these are the
    expected_obs_filepaths = [
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.nam.20170601.t00z'
        '.tm00.nc',
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.nam.20170602.t00z'
        '.tm00.nc',
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr/prepbufr.nam.20170603.t00z'
        '.tm00.nc'
    ]
    expected_obs_valid_times = ['2017060100', '2017060200', '2017060300']

    file_type = "obs"
    consolidated_obs_list = ps.create_input_file_info(file_type)
    assert(len(expected_obs_filepaths) == len(consolidated_obs_list))

    # Make sure we got exact matches with respect to the valid times
    # and filepaths
    for obs in consolidated_obs_list:
        if obs.full_filepath in expected_obs_filepaths:
            expected_obs_filepaths.remove(obs.full_filepath)
        valid_time_str = datetime.datetime.fromtimestamp(
            obs.valid_time).strftime('%Y%m%d%H')
        if valid_time_str in expected_obs_valid_times:
            expected_obs_valid_times.remove(valid_time_str)

    # If we had the exact matches, these arrays will be empty
    assert(len(expected_obs_filepaths) == 0)
    assert(len(expected_obs_valid_times) == 0)


def test_correct_pairings_nam_vs_gfs(metplus_config):
    pytest.skip('Hard-coded output directories do not match current setup')

    # THIS TEST IS FOR CONUS_SFC (NAM vs GFS)
    # Test that the pairings produce correct results for NAM (conus_sfc) vs
    # GFS(fcst/model)
    ps = point_stat_wrapper(metplus_config)

    # For conus_sfc first
    # fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
    fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
    obs_input_dir = \
        '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr'
    ps.ps_dict['FCST_INPUT_DIR'] = fcst_input_dir
    ps.ps_dict['OBS_INPUT_DIR'] = obs_input_dir
    ps.ps_dict['OBS_INPUT_DIR_REGEX'] = ''
    ps.ps_dict['OBS_INPUT_FILE_TMPL'] = 'prepbufr.nam.{init?fmt=%Y%m%d}.t{cycle?fmt=%HH}z.tm{offset?fmt=%HH}.nc'
    ps.ps_dict['FCST_INPUT_DIR_REGEX'] = ''
    ps.ps_dict['FCST_INPUT_FILE_TMPL'] = 'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H}'

    # Check conus sfc (NAM)
    pairs_by_valid = ps.select_fcst_obs_pairs()
    # Using data in /d1/METplus_Mallory/data/prepbufr/nam for NAM data
    # For fcst file in pair, expecting the fcst filename (NAM) in format
    # ymd.tCC.tmhh where date = ymd, cycle = CC and offset = hh
    # First, get the fcst and obs file regular expressions
    fcst_file_tmpl = ps.ps_dict['FCST_INPUT_FILE_TMPL']
    fcst_file_regex_tuple = ps.create_filename_regex(fcst_file_tmpl)
    obs_file_tmpl = ps.ps_dict['OBS_INPUT_FILE_TMPL']
    fcst_file_regex = fcst_file_regex_tuple[0]
    obs_file_regex_tuple = ps.create_filename_regex(obs_file_tmpl)
    obs_file_regex = obs_file_regex_tuple[0]
    fcst_regex_compile = re.compile(fcst_file_regex)
    obs_regex_compile = re.compile(obs_file_regex)
    # anticipate matched pairs like the following (filepaths omitted for
    # clarity)
    #
    # conus_sfc
    # ----------
    # prepbufr.nam.20170601.t03z.tm03.nc, pgbf00.gfs.2017060100
    # prepbufr.nam.20170601.t03z.tm03.nc, pgbf12.gfs.2017053112
    # prepbufr.nam.20170601.t03z.tm03.nc, pgbf24.gfs.2017050100
    # ...
    #
    # prepbufr.nam.20170601.t12z.tm00.nc, pgbf00.gfs.2017060112
    # prepbufr.nam.20170601.t12z.tm00.nc, pgbf12.gfs.2017060100

    # pick a matched pair from the middle of the list and verify that they
    # have the same valid time
    num_pairs = len(pairs_by_valid)

    if num_pairs > 0:
        mid_index = (num_pairs - 1)/2
        fcst = pairs_by_valid[mid_index][0]
        obs = pairs_by_valid[mid_index][1]
        fcst_match = re.match(fcst_regex_compile, fcst)
        obs_match = re.match(obs_regex_compile, obs)
        if fcst_match and obs_match:
            fcst_ymdh_str = fcst_match.group(2)
            fcst_ymd = ps.convert_date_strings_to_unix_times(fcst_ymdh_str)
            fcst_hr_in_secs = int(fcst_match.group(1)) * ps.HOURS_TO_SECONDS
            fcst_valid = fcst_ymd + fcst_hr_in_secs

            # Now get the valid time for this
            obs_ymd =\
                ps.convert_date_strings_to_unix_times(obs_match.group(1))
            obs_cycle = int(obs_match.group(2))
            obs_offset = int(obs_match.group(3))
            delta_secs = (obs_cycle - obs_offset) * ps.HOURS_TO_SECONDS
            obs_valid = obs_ymd + delta_secs

            assert(fcst_valid == obs_valid)

    else:
        # No matches were produced but some matches were expected. Fail
        assert True is False


def test_correct_pairings_gdas_vs_gfs(metplus_config):
    pytest.skip('Hard-coded output directories do not match current setup')

    # Test that the pairings produce correct results for
    # GDAS (upper_air) point obs vs GFS(fcst/model)
    ps = point_stat_wrapper(metplus_config)

    # For conus_sfc first
    # fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
    fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
    obs_input_dir = '/d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr'
    ps.ps_dict['FCST_INPUT_DIR'] = fcst_input_dir
    ps.ps_dict['OBS_INPUT_DIR'] = obs_input_dir
    ps.ps_dict['OBS_INPUT_FILE_REGEX'] = ''
    ps.ps_dict['OBS_INPUT_FILE_TMPL'] = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc'
    ps.ps_dict['FCST_INPUT_FILE_REGEX'] = ''
    ps.ps_dict['FCST_INPUT_FILE_TMPL'] = \
        'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H}'
    # Check upper_air (GDAS)
    pairs_by_valid = ps.select_fcst_obs_pairs()
    # Using data in /d1/METplus_Mallory/output_for_testing/grid2obs_metplustest.2/prepbufr for GDAS data.
    # For fcst file in pair, expecting the fcst filename (GDAS) to be in
    # format ymdh where ymdh = valid time = init time

    # First, get the fcst and obs file regular expressions
    fcst_file_tmpl = ps.ps_dict['FCST_INPUT_FILE_TMPL']
    fcst_file_regex_tuple = ps.create_filename_regex(fcst_file_tmpl)
    obs_file_tmpl = ps.ps_dict['OBS_INPUT_FILE_TMPL']
    fcst_file_regex = fcst_file_regex_tuple[0]
    obs_file_regex_tuple = ps.create_filename_regex(obs_file_tmpl)
    obs_file_regex = obs_file_regex_tuple[0]
    fcst_regex_compile = re.compile(fcst_file_regex)
    obs_regex_compile = re.compile(obs_file_regex)
    # anticipate matched pairs like the following (filepaths omitted for
    # clarity)
    #
    # upper air
    # ----------
    # prepbufr.gdas.2017060100, pbgf00.gfs.2017060100
    # prepbufr.gdas.2017060100, pbgf12.gfs.2017053112
    # prepbufr.gdas.2017060100, pbgf24.gfs.2017053100
    # ...
    # prepbufr.gdas.2017060112, pgbf00.gfs.2017060112
    # prepbufr.gdas.2017060112, pgbf12.gfs.2017060100
    #

    # pick a matched pair from the middle of the list and verify that they
    # have the same valid time
    num_pairs = len(pairs_by_valid)

    if num_pairs > 0:
        mid_index = (num_pairs - 1) / 2
        fcst = pairs_by_valid[mid_index][0]
        obs = pairs_by_valid[mid_index][1]
        fcst_match = re.match(fcst_regex_compile, fcst)
        obs_match = re.match(obs_regex_compile, obs)
        if fcst_match and obs_match:
            fcst_ymdh_str = fcst_match.group(2)
            fcst_ymd = ps.convert_date_strings_to_unix_times(fcst_ymdh_str)
            fcst_hr_in_secs = int(fcst_match.group(1)) * ps.HOURS_TO_SECONDS
            fcst_valid = fcst_ymd + fcst_hr_in_secs

            # Now get the valid time for this
            obs_valid =\
                ps.convert_date_strings_to_unix_times(obs_match.group(1))

            assert(fcst_valid == obs_valid)

    else:
        # No matches were produced but some matches were expected. Fail
        assert True is False


def test_reformat_fields_for_met_conus_sfc(metplus_config):
    """! THIS RUNS ONLY FOR CONUS SFC skips if config file is set up
         for upper air
         Verify that the fcst_field and obs_field text in the MET config
         field dictionary are well-formed. Test is based on the
         point_stat_test_conus_sfc.conf file.
    """
    pytest.skip('Hard-coded output directories do not match current setup')

    ps = point_stat_wrapper(metplus_config)

    # Set up the appropriate input directories
    fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
    obs_input_dir = '/d1/minnawin/pb2nc_output/nam/conus_sfc'
    ps.ps_dict['FCST_INPUT_DIR'] = fcst_input_dir
    ps.ps_dict['OBS_INPUT_DIR'] = obs_input_dir
    ps.ps_dict['OBS_INPUT_FILE_REGEX'] = \
        '.*prepbufr.nam.(2[0-9]{7}).t([0-9]{2})z.tm([0-9]{2}).nc'
    ps.ps_dict['FCST_INPUT_FILE_REGEX'] = '.*pgbf([0-9]{1,3}).gfs.(2[0-9]{9})'
    met_config_file = ps.ps_dict['POINT_STAT_CONFIG_FILE']
    match = re.match(r'.*conus.*', met_config_file)
    if not match:
        pytest.skip("The current test config file is not set up for conus_sfc")
    all_vars_list = util.parse_var_list(ps.p)
    logger = logging.getLogger("temp_log")
    fields = util.reformat_fields_for_met(all_vars_list, logger)
    # The following fields were defined in the MET+ config file:
    # TMP, RH, DPT, UGRD, VGRD, TCDC, PRMSL

    fcst_str = fields.fcst_field
    expected_fcst_str = '{ name = "TMP"; level = [ "Z2" ]; }, ' \
                        '{ name = "RH"; level = [ "Z2" ]; }, ' \
                        '{ name = "DPT"; level = [ "Z2" ]; }, ' \
                        '{ name = "UGRD"; level = [ "Z10" ]; }, ' \
                        '{ name = "VGRD"; level = [ "Z10" ]; }, ' \
                        '{ name = "TCDC"; level = [ "L0" ]; GRIB_lvl_typ = ' \
                        '200; }, ' \
                        '{ name = "PRMSL"; level = [ "Z0" ]; }'

    print("expected: ", expected_fcst_str)
    print("fcst str: ", fcst_str)
    obs_str = fields.obs_field
    expected_obs_str = '{ name = "TMP"; level = [ "Z2" ]; }, ' \
                       '{ name = "RH"; level = [ "Z2" ]; }, ' \
                       '{ name = "DPT"; level = [ "Z2" ]; }, ' \
                       '{ name = "UGRD"; level = [ "Z10" ]; }, ' \
                       '{ name = "VGRD"; level = [ "Z10" ]; }, ' \
                       '{ name = "TCDC"; level = [ "L0" ]; }, ' \
                       '{ name = "PRMSL"; level = [ "Z0" ]; }'
    print("expected: ", expected_obs_str)
    print("obs  str: ", obs_str)

    if fcst_str == expected_fcst_str:
        assert True is True
    assert obs_str == expected_obs_str


# def test_reformat_fields_for_met_upper_air():
#     """! THIS RUNS ONLY FOR GDAS upper air configuration file (g20_upper.conf)
#          This test gets skipped if test config file is set
#          up for conus_sfc
#          Verify that the fcst_field and obs_field text in the MET config
#          field dictionary are well-formed. Test is based on the
#          point_stat_test_upper_air.conf file.
#     """
#     ps = point_stat_wrapper()
#     # Check if we are currently using the upper air config files for testing
#     # Do this by checking which MET point_stat config file is being used by
#     # searching for the term 'upper' in the MET point_stat config file name.
#     # If is is absent, skip this test.
#
#     met_config_file =  ps.ps_dict['POINT_STAT_CONFIG_FILE']
#     match = re.match(r'.*upper.*', met_config_file)
#     if not match:
#        pytest.skip("The current test config file is not set up for upper air")
#
#     # Set up the appropriate input directories
#     fcst_input_dir = '/d1/METplus_Mallory/data/gfs'
#     obs_input_dir = '/d1/minnawin/pb2nc_crow_test/gdas/upper_air/Mallory_config'
#     ps.ps_dict['FCST_INPUT_DIR'] = fcst_input_dir
#     ps.ps_dict['OBS_INPUT_DIR'] = obs_input_dir
#     ps.ps_dict['OBS_INPUT_DIR_REGEX'] = ''
#     ps.ps_dict['OBS_INPUT_FILE_TMPL'] = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc'
#     ps.ps_dict['FCST_INPUT_DIR_REGEX'] = ''
#     ps.ps_dict['FCST_INPUT_FILE_TMPL'] = \
#         'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H}'
#
#     all_vars_list = util.parse_var_list(ps.p)
#     logger = logging.getLogger("temp_log")
#     fields = util.reformat_fields_for_met(all_vars_list, logger)
#     # The following fields were defined in the MET+ config file:
#     # TMP, RH, HGT, UGRD, VGRD
#
#     fcst_str = fields.fcst_field
#     expected_fcst_str = '{ name = "TMP"; level = [ "P1000" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P925" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P850" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P700" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P500" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P400" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P300" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P250" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P200" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P150" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P100" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P50" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P20" ]; }, ' \
#                         '{ name = "TMP"; level = [ "P10" ]; }, ' \
#                         '{ name = "RH"; level = [ "P1000" ]; }, ' \
#                         '{ name = "RH"; level = [ "P925" ]; }, ' \
#                         '{ name = "RH"; level = [ "P850" ]; }, ' \
#                         '{ name = "RH"; level = [ "P700" ]; }, ' \
#                         '{ name = "RH"; level = [ "P500" ]; }, ' \
#                         '{ name = "RH"; level = [ "P400" ]; }, ' \
#                         '{ name = "RH"; level = [ "P300" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P1000" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P925" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P850" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P700" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P500" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P400" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P300" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P250" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P200" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P150" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P100" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P50" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P20" ]; }, ' \
#                         '{ name = "UGRD"; level = [ "P10" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P1000" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P925" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P850" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P700" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P500" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P400" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P300" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P250" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P200" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P150" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P100" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P50" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P20" ]; }, ' \
#                         '{ name = "VGRD"; level = [ "P10" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P1000" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P950" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P925" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P850" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P700" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P500" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P400" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P300" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P250" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P200" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P150" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P100" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P50" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P20" ]; }, ' \
#                         '{ name = "HGT"; level = [ "P10" ]; }'
#
#     # print("expected: ", expected_fcst_str)
#     # print("fcst str: ", fcst_str)
#     obs_str = fields.obs_field
#     expected_obs_str = expected_fcst_str
#     # print("expected: ", expected_obs_str)
#     # print("obs  str: ", obs_str)
#
#     assert fcst_str == expected_fcst_str and obs_str == expected_obs_str
