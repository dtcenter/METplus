#!/usr/bin/env python

import os
import datetime
import sys
import logging
import pytest
import datetime

import produtil.setup

from metplus.wrappers.stat_analysis_wrapper import StatAnalysisWrapper
from metplus.util import met_util as util


#
# These are tests (not necessarily unit tests) for the
# MET stat_analysis wrapper, stat_analysis_wrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  test_stat_analysis.conf.  This contains
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
def stat_analysis_wrapper(metplus_config):
    """! Returns a default StatAnalysisWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty StatAnalysisWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'test.conf'))
    config = metplus_config(extra_configs)
    util.handle_tmp_dir(config)
    return StatAnalysisWrapper(config)

# ------------------TESTS GO BELOW ---------------------------
#

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# To test numerous files for filesize, use parametrization:
# @pytest.mark.parametrize(
#     'key, value', [
#         ('/usr/local/met-6.1/bin/point_stat', 382180),
#         ('/usr/local/met-6.1/bin/stat_analysis', 3438944),
#         ('/usr/local/met-6.1/bin/pb2nc', 3009056)
#
#     ]
# )
# def test_file_sizes(key, value):
#     st = stat_analysis_wrapper()
#     # Retrieve the value of the class attribute that corresponds
#     # to the key in the parametrization
#     files_in_dir = []
#     for dirpath, dirnames, files in os.walk("/usr/local/met-6.1/bin"):
#         for name in files:
#             files_in_dir.append(os.path.join(dirpath, name))
#         if actual_key in files_in_dir:
#         # The actual_key is one of the files of interest we retrieved from
#         # the output directory.  Verify that it's file size is what we
#         # expected.
#             assert actual_key == key
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
METPLUS_BASE = os.getcwd().split('/internal_tests')[0]

def test_get_command(metplus_config):
    # Independently test that the stat_analysis command
    # is being put together correctly with
    # the full path to stat_analysis, the 
    # lookin dir, and config file
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_command = (
        st.config.getdir('MET_BIN_DIR', '')
        +'/stat_analysis '
        +'-lookin /path/to/lookin_dir '
        +'-config /path/to/STATAnalysisConfig'
    )
    st.lookindir = '/path/to/lookin_dir'
    st.c_dict['CONFIG_FILE'] = '/path/to/STATAnalysisConfig'
    test_command = st.get_command()
    assert(expected_command == test_command)

def test_create_c_dict(metplus_config):
    # Independently test that c_dict is being created
    # and that the wrapper and config reader 
    # is setting the values as expected
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    c_dict = st.create_c_dict()
    assert(c_dict['LOOP_ORDER'] == 'times')
    assert(os.path.realpath(c_dict['CONFIG_FILE']) == (METPLUS_BASE+'/internal_tests/'
                                                       +'config/STATAnalysisConfig'))
    assert(c_dict['OUTPUT_DIR'] == (st.config.getdir('OUTPUT_BASE')
                                         +'/stat_analysis'))
    assert('FCST_INIT_HOUR_LIST' in c_dict['GROUP_LIST_ITEMS'])
    assert('FCST_VALID_HOUR_LIST' in c_dict['LOOP_LIST_ITEMS'] and
           'MODEL_LIST' in c_dict['LOOP_LIST_ITEMS'])
    assert(c_dict['VAR_LIST'] == [])
    assert(c_dict['MODEL_LIST'] == ['MODEL_TEST'])
    assert(c_dict['DESC_LIST'] == [])
    assert(c_dict['FCST_LEAD_LIST'] == [])
    assert(c_dict['OBS_LEAD_LIST'] == [])
    assert(c_dict['FCST_VALID_HOUR_LIST'] == ['000000'])
    assert(c_dict['FCST_INIT_HOUR_LIST'] == ['000000', '060000', '120000', '180000'])
    assert(c_dict['OBS_VALID_HOUR_LIST'] == [])
    assert(c_dict['OBS_INIT_HOUR_LIST'] == [])
    assert(c_dict['VX_MASK_LIST'] == [])
    assert(c_dict['INTERP_MTHD_LIST'] == [])
    assert(c_dict['INTERP_PNTS_LIST'] == [])
    assert(c_dict['COV_THRESH_LIST'] == [])
    assert(c_dict['ALPHA_LIST'] == [])
    assert(c_dict['LINE_TYPE_LIST'] == [])

def test_list_to_str(metplus_config):
    # Independently test that a list of strings
    # are being converted to a one
    # string list correctly
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_list = '"a", "b", "c"'
    test_list = st.list_to_str([ 'a', 'b', 'c' ])
    assert(expected_list == test_list)
    # Test 2
    expected_list = '"0", "1", "2"'
    test_list = st.list_to_str([ '0', '1', '2' ])
    assert(expected_list == test_list)

def test_set_lists_as_loop_or_group(metplus_config):
    # Independently test that the lists that are set
    # in the config file are being set 
    # accordingly based on their place 
    # in GROUP_LIST_ITEMS and LOOP_LIST_ITEMS 
    # and those not set are set to GROUP_LIST_ITEMS
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_lists_to_group_items = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST',
                                      'FCST_LEAD_LIST', 'OBS_LEAD_LIST',
                                      'OBS_VALID_HOUR_LIST',
                                      'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST',
                                      'OBS_VAR_LIST', 'FCST_UNITS_LIST', 
                                      'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                                      'OBS_LEVEL_LIST', 'VX_MASK_LIST',
                                      'INTERP_MTHD_LIST', 'INTERP_PNTS_LIST', 
                                      'FCST_THRESH_LIST', 'OBS_THRESH_LIST',
                                      'COV_THRESH_LIST', 'ALPHA_LIST', 
                                      'LINE_TYPE_LIST' ]
    expected_lists_to_loop_items = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST' ]
    config_dict = {}
    config_dict['LOOP_ORDER'] = 'times'
    config_dict['PROCESS_LIST'] = 'StatAnalysis'
    config_dict['CONFIG_FILE'] = (
        'PARM_BASE/grid_to_grid/met_config/STATAnalysisConfig'
    )
    config_dict['OUTPUT_DIR'] = 'OUTPUT_BASE/stat_analysis'
    config_dict['GROUP_LIST_ITEMS'] = [ 'FCST_INIT_HOUR_LIST' ]
    config_dict['LOOP_LIST_ITEMS'] = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST']
    config_dict['FCST_VAR_LIST'] = []
    config_dict['OBS_VAR_LIST'] = []
    config_dict['FCST_LEVEL_LIST'] = []
    config_dict['OBS_LEVEL_LIST'] = []
    config_dict['FCST_UNITS_LIST'] = []
    config_dict['OBS_UNITS_LIST'] = []
    config_dict['FCST_THRESH_LIST'] = []
    config_dict['OBS_THRESH_LIST'] = []
    config_dict['MODEL_LIST'] = [ 'MODEL_TEST' ]
    config_dict['DESC_LIST'] = []
    config_dict['FCST_LEAD_LIST'] = []
    config_dict['OBS_LEAD_LIST'] = []
    config_dict['FCST_VALID_HOUR_LIST'] = [ '00', '06', '12', '18']
    config_dict['FCST_INIT_HOUR_LIST'] = [ '00', '06', '12', '18']
    config_dict['OBS_VALID_HOUR_LIST'] = []
    config_dict['OBS_INIT_HOUR_LIST'] = []
    config_dict['VX_MASK_LIST'] = []
    config_dict['INTERP_MTHD_LIST'] = []
    config_dict['INTERP_PNTS_LIST'] = []
    config_dict['COV_THRESH_LIST'] = []
    config_dict['ALPHA_LIST'] = []
    config_dict['LINE_TYPE_LIST'] = []
    config_dict = st.set_lists_loop_or_group(config_dict)
    test_lists_to_loop_items = config_dict['LOOP_LIST_ITEMS']
    test_lists_to_group_items = config_dict['GROUP_LIST_ITEMS']

    assert(all(elem in expected_lists_to_group_items
               for elem in test_lists_to_group_items))
    assert(all(elem in expected_lists_to_loop_items 
               for elem in test_lists_to_loop_items))

@pytest.mark.parametrize(
    'expression, expected_result', [
        ('>1', 'gt1'),
        ('>=0.2', 'ge0.2'),
        ('<30', 'lt30'),
        ('<=0.04', 'le0.04'),
        ('==5', 'eq5'),
        ('!=0.06', 'ne0.06'),
        ('>0.05, gt0.05, >=1, ge1, <5, lt5, <=10, le10, ==15, eq15, !=20, ne20',
           'gt0.05,gt0.05,ge1,ge1,lt5,lt5,le10,le10,eq15,eq15,ne20,ne20'),
        ('<805, <1609, <4828, <8045, >=8045, <16090',
         'lt805,lt1609,lt4828,lt8045,ge8045,lt16090'),
    ]
)
def test_format_thresh(metplus_config, expression, expected_result):
    # Idependently test the creation of 
    # string values for defining thresholds
    st = stat_analysis_wrapper(metplus_config)

    assert(st.format_thresh(expression) == expected_result)

def test_build_stringsub_dict(metplus_config):
    # Independently test the building of 
    # the dictionary used in the stringtemplate
    # substitution and the values are being set
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '000000'
    config_dict['FCST_VAR'] = ''
    config_dict['FCST_LEVEL'] = ''
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = ''
    config_dict['FCST_INIT_HOUR'] = '"000000", "060000", "120000", "180000"'
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = ''
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] =  '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = ''
    # Test 1
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190105'
    st.c_dict['DATE_TYPE'] = 'VALID'
    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST', 'FCST_LEAD_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST' ] 
    test_stringsub_dict = st.build_stringsub_dict(lists_to_loop,
                                                  lists_to_group, config_dict)
    assert(test_stringsub_dict['valid_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['valid_end'] == 
           datetime.datetime(2019, 1, 5, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid_hour'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid_hour_end'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid_end'] == 
           datetime.datetime(2019, 1, 5, 0, 0, 0))
    assert(test_stringsub_dict['valid_hour'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['valid_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['valid_hour_end'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['model'] == 'MODEL_TEST')
    assert(test_stringsub_dict['obtype'] == 'MODEL_TEST_ANL')
    assert(test_stringsub_dict['fcst_init_hour'] == 
           '000000_060000_120000_180000')
    assert(test_stringsub_dict['fcst_init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 18, 0, 0))
    assert(test_stringsub_dict['init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 18, 0, 0)) 
    assert(test_stringsub_dict['fcst_var'] == '')
    assert(test_stringsub_dict['fcst_level'] == '')
    assert(test_stringsub_dict['fcst_units'] == '')
    assert(test_stringsub_dict['fcst_thresh'] == '')
    assert(test_stringsub_dict['desc'] == '')
    # Test 2
    config_dict['FCST_LEAD'] = '240000'
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'
    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST', 
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST', 'FCST_LEAD_LIST' ]
    test_stringsub_dict = st.build_stringsub_dict(lists_to_loop,
                                                  lists_to_group, config_dict)
    assert(test_stringsub_dict['valid'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_lead_totalsec'] == '86400')
    assert(test_stringsub_dict['fcst_lead_hour'] == '24')
    assert(test_stringsub_dict['fcst_lead_min'] == '00')
    assert(test_stringsub_dict['fcst_lead_sec'] == '00')
    assert(test_stringsub_dict['fcst_lead'] == '240000')
    assert(test_stringsub_dict['lead_totalsec'] == '86400')
    assert(test_stringsub_dict['lead_hour'] == '24')
    assert(test_stringsub_dict['lead_min'] == '00')
    assert(test_stringsub_dict['lead_sec'] == '00')
    assert(test_stringsub_dict['lead'] == '240000')
    # Test 3
    config_dict['FCST_LEAD'] = '1200000'
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'
    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST', 'FCST_LEAD_LIST' ]
    test_stringsub_dict = st.build_stringsub_dict(lists_to_loop,
                                                  lists_to_group, config_dict)
    assert(test_stringsub_dict['valid'] ==
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_valid'] ==
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_lead_totalsec'] == '432000')
    assert(test_stringsub_dict['fcst_lead_hour'] == '120')
    assert(test_stringsub_dict['fcst_lead_min'] == '00')
    assert(test_stringsub_dict['fcst_lead_sec'] == '00')
    assert(test_stringsub_dict['fcst_lead'] == '1200000')
    assert(test_stringsub_dict['lead_totalsec'] == '432000')
    assert(test_stringsub_dict['lead_hour'] == '120')
    assert(test_stringsub_dict['lead_min'] == '00')
    assert(test_stringsub_dict['lead_sec'] == '00')
    assert(test_stringsub_dict['lead'] == '1200000')
    # Test 4
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190105'
    st.c_dict['DATE_TYPE'] = 'INIT'
    test_stringsub_dict = st.build_stringsub_dict(lists_to_loop,
                                                  lists_to_group, config_dict)
    assert(test_stringsub_dict['fcst_init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 18, 0, 0))
    assert(test_stringsub_dict['fcst_init_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['fcst_init_end'] == 
           datetime.datetime(2019, 1, 5, 18, 0, 0))
    assert(test_stringsub_dict['init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 18, 0, 0))
    assert(test_stringsub_dict['init_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0, 0))
    assert(test_stringsub_dict['init_end'] == 
           datetime.datetime(2019, 1, 5, 18, 0, 0))
    # Test 5
    config_dict['FCST_INIT_HOUR'] = ''
    config_dict['FCST_LEAD'] = ''
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'INIT'
    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST', 'FCST_LEAD_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST' ]
    test_stringsub_dict = st.build_stringsub_dict(lists_to_loop,
                                                  lists_to_group, config_dict)
    assert(test_stringsub_dict['init_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0 ,0))
    assert(test_stringsub_dict['init_end'] == 
           datetime.datetime(2019, 1, 1, 23, 59 ,59))
    assert(test_stringsub_dict['fcst_init_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0 ,0))
    assert(test_stringsub_dict['fcst_init_end'] == 
           datetime.datetime(2019, 1, 1, 23, 59 ,59))
    assert(test_stringsub_dict['obs_init_beg'] == 
           datetime.datetime(2019, 1, 1, 0, 0 ,0))
    assert(test_stringsub_dict['obs_init_end'] == 
           datetime.datetime(2019, 1, 1, 23, 59 ,59))
    assert(test_stringsub_dict['fcst_init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0)) 
    assert(test_stringsub_dict['fcst_init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 23, 59 ,59))
    assert(test_stringsub_dict['obs_init_hour_beg'] == 
           datetime.datetime(1900, 1, 1, 0, 0, 0))                               
    assert(test_stringsub_dict['obs_init_hour_end'] == 
           datetime.datetime(1900, 1, 1, 23, 59 ,59))
 
def test_get_output_filename(metplus_config):
    # Independently test the building of
    # the output file name 
    # using string template substitution
    # and test the values is
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '000000'
    config_dict['FCST_VAR'] = ''
    config_dict['FCST_LEVEL'] = ''
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = ''
    config_dict['FCST_INIT_HOUR'] = '"000000", "060000", "120000", "180000"'
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = ''
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] =  '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = ''
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'
    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST', 'FCST_LEAD_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST' ]
    # Test 1
    expected_output_filename = '00Z/MODEL_TEST/MODEL_TEST_20190101.stat'
    output_type = 'dump_row'
    filename_template = (
        '{fcst_valid_hour?fmt=%H}Z/{model?fmt=%s}/{model?fmt=%s}_{valid?fmt=%Y%m%d}.stat'
    )
    filename_type = 'user'
    test_output_filename = st.get_output_filename(output_type,
                                                  filename_template,
                                                  filename_type,
                                                  lists_to_loop,
                                                  lists_to_group,
                                                  config_dict)
    assert(expected_output_filename == test_output_filename)
    # Test 2
    expected_output_filename = (
        'MODEL_TEST_MODEL_TEST_ANL_'
        +'valid20190101_fcstvalidhour000000Z'
        +'_dump_row.stat'
    )
    output_type = 'dump_row'
    filename_template = (
        '{model?fmt=%s}_{obtype?fmt=%s}'
        +'_valid{valid?fmt=%Y%m%d}_'
        +'fcstvalidhour000000Z_dump_row.stat'
    )
    filename_type = 'user'
    test_output_filename = st.get_output_filename(output_type,
                                                  filename_template,
                                                  filename_type,
                                                  lists_to_loop,
                                                  lists_to_group,
                                                  config_dict)
    assert(expected_output_filename == test_output_filename)   
    # Test 3
    expected_output_filename = (
        'MODEL_TEST_MODEL_TEST_ANL'
        +'_valid2019010100'
        +'_init000000_060000_120000_180000.stat'
    )
    output_type = 'out_stat'
    filename_template = (
        '{model?fmt=%s}_{obtype?fmt=%s}'
        +'_valid{valid?fmt=%Y%m%d}{valid_hour?fmt=%H}'
        +'_init{fcst_init_hour?fmt=%s}.stat'
    )
    filename_type = 'user'
    test_output_filename = st.get_output_filename(output_type,
                                                  filename_template,
                                                  filename_type,
                                                  lists_to_loop,
                                                  lists_to_group,
                                                  config_dict)
    assert(expected_output_filename == test_output_filename)
    # Test 4
    expected_output_filename = (
        'MODEL_TEST_MODEL_TEST_ANL'
        +'valid20190101_fcstvalidhour000000Z'
        +'_out_stat.stat'
    )
    output_type = 'out_stat'
    filename_template = (
        '{model?fmt=%s}_{obtype?fmt=%s}'
    )
    filename_type = 'default'
    test_output_filename = st.get_output_filename(output_type,
                                                  filename_template,
                                                  filename_type,
                                                  lists_to_loop,
                                                  lists_to_group,
                                                  config_dict)
    assert(expected_output_filename == test_output_filename)

def test_get_lookin_dir(metplus_config):
    # Independently test the building of
    # the lookin directory
    # using string template substitution
    # and wildcard filling
    # and test the value is
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '000000'
    config_dict['FCST_VAR'] = ''
    config_dict['FCST_LEVEL'] = ''
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = ''
    config_dict['FCST_INIT_HOUR'] = '"000000", "060000", "120000", "180000"'
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = ''
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] =  '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = ''
    st.c_dict['DATE_BEG'] = '20180201'
    st.c_dict['DATE_END'] = '20180201'
    st.c_dict['DATE_TYPE'] = 'VALID'

    lists_to_group = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST', 'FCST_LEAD_LIST',
                       'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                       'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                       'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                       'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                       'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                       'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                       'LINE_TYPE_LIST' ]
    lists_to_loop = [ 'FCST_VALID_HOUR_LIST', 'MODEL_LIST' ]
    stat_analysis_pytest_dir = os.path.dirname(__file__)
    # Test 1
    expected_lookin_dir = os.path.join(stat_analysis_pytest_dir,
                                       '../../data/fake/20180201')
    dir_path = os.path.join(stat_analysis_pytest_dir,
                            '../../data/fake/*')

    test_lookin_dir = st.get_lookin_dir(dir_path, lists_to_loop,
                                        lists_to_group, config_dict)
    assert(expected_lookin_dir == test_lookin_dir)

    # Test 2
    expected_lookin_dir = os.path.join(stat_analysis_pytest_dir,
                                       '../../data/fake/20180201')
    dir_path = os.path.join(stat_analysis_pytest_dir,
                            '../../data/fake/{valid?fmt=%Y%m%d}')

    test_lookin_dir = st.get_lookin_dir(dir_path, lists_to_loop,
                                        lists_to_group, config_dict)
    assert(expected_lookin_dir == test_lookin_dir)

    # Test 3 - no matches for lookin dir wildcard
    expected_lookin_dir = ''
    dir_path = os.path.join(stat_analysis_pytest_dir,
                            '../../data/fake/*nothingmatches*')

    test_lookin_dir = st.get_lookin_dir(dir_path, lists_to_loop,
                                        lists_to_group, config_dict)
    assert(expected_lookin_dir == test_lookin_dir)

def test_format_valid_init(metplus_config):
    # Independently test the formatting 
    # of the valid and initialization date and hours
    # from the METplus config file for the MET
    # config file and that they are formatted
    # correctly
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190105'
    st.c_dict['DATE_TYPE'] = 'VALID'

    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '000000'
    config_dict['FCST_INIT_HOUR'] = '"000000", "120000"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict = st.format_valid_init(config_dict)
    assert(config_dict['FCST_VALID_BEG'] == '20190101_000000')
    assert(config_dict['FCST_VALID_END'] == '20190105_000000')
    assert(config_dict['FCST_VALID_HOUR'] == '"000000"')
    assert(config_dict['FCST_INIT_BEG'] == '')
    assert(config_dict['FCST_INIT_END'] == '')
    assert(config_dict['FCST_INIT_HOUR'] == '"000000", "120000"')
    assert(config_dict['OBS_VALID_BEG'] == '')
    assert(config_dict['OBS_VALID_END'] == '')
    assert(config_dict['OBS_VALID_HOUR'] == '')
    assert(config_dict['OBS_INIT_BEG'] == '')
    assert(config_dict['OBS_INIT_END'] == '')
    assert(config_dict['OBS_INIT_HOUR'] == '')
    # Test 2
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190105'
    st.c_dict['DATE_TYPE'] = 'VALID'

    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '"000000", "120000"'
    config_dict['FCST_INIT_HOUR'] = '"000000", "120000"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict = st.format_valid_init(config_dict)
    assert(config_dict['FCST_VALID_BEG'] == '20190101_000000')
    assert(config_dict['FCST_VALID_END'] == '20190105_120000')
    assert(config_dict['FCST_VALID_HOUR'] == '"000000", "120000"')
    assert(config_dict['FCST_INIT_BEG'] == '')
    assert(config_dict['FCST_INIT_END'] == '')
    assert(config_dict['FCST_INIT_HOUR'] == '"000000", "120000"')
    assert(config_dict['OBS_VALID_BEG'] == '')
    assert(config_dict['OBS_VALID_END'] == '')
    assert(config_dict['OBS_VALID_HOUR'] == '')
    assert(config_dict['OBS_INIT_BEG'] == '')
    assert(config_dict['OBS_INIT_END'] == '')
    assert(config_dict['OBS_INIT_HOUR'] == '')
    # Test 3
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'

    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = ''
    config_dict['FCST_INIT_HOUR'] = ''
    config_dict['OBS_VALID_HOUR'] = '000000'
    config_dict['OBS_INIT_HOUR'] = '"000000", "120000"'
    config_dict = st.format_valid_init(config_dict)
    assert(config_dict['FCST_VALID_BEG'] == '')
    assert(config_dict['FCST_VALID_END'] == '')
    assert(config_dict['FCST_VALID_HOUR'] == '')
    assert(config_dict['FCST_INIT_BEG'] == '')
    assert(config_dict['FCST_INIT_END'] == '')
    assert(config_dict['FCST_INIT_HOUR'] == '')
    assert(config_dict['OBS_VALID_BEG'] == '20190101_000000')
    assert(config_dict['OBS_VALID_END'] == '20190101_000000')
    assert(config_dict['OBS_VALID_HOUR'] == '"000000"')
    assert(config_dict['OBS_INIT_BEG'] == '')
    assert(config_dict['OBS_INIT_END'] == '')
    assert(config_dict['OBS_INIT_HOUR'] == '"000000", "120000"')
    # Test 3
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'INIT'

    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = ''
    config_dict['FCST_INIT_HOUR'] = ''
    config_dict['OBS_VALID_HOUR'] = '000000'
    config_dict['OBS_INIT_HOUR'] = '"000000", "120000"'
    config_dict = st.format_valid_init(config_dict)
    assert(config_dict['FCST_VALID_BEG'] == '')
    assert(config_dict['FCST_VALID_END'] == '')
    assert(config_dict['FCST_VALID_HOUR'] == '')
    assert(config_dict['FCST_INIT_BEG'] == '')
    assert(config_dict['FCST_INIT_END'] == '')
    assert(config_dict['FCST_INIT_HOUR'] == '')
    assert(config_dict['OBS_VALID_BEG'] == '')
    assert(config_dict['OBS_VALID_END'] == '')
    assert(config_dict['OBS_VALID_HOUR'] == '"000000"')
    assert(config_dict['OBS_INIT_BEG'] == '20190101_000000')
    assert(config_dict['OBS_INIT_END'] == '20190101_120000')
    assert(config_dict['OBS_INIT_HOUR'] == '"000000", "120000"')

def test_parse_model_info(metplus_config):
    # Independently test the creation of 
    # the model information dictionary
    # and the reading from the config file
    # are as expected
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_name = 'MODEL_TEST'
    expected_reference_name = 'MODELTEST'
    expected_obtype = 'MODEL_TEST_ANL'
    expected_dump_row_filename_template = (
        '{fcst_valid_hour?fmt=%H}Z/MODEL_TEST/'
        +'MODEL_TEST_{valid?fmt=%Y%m%d}.stat'
    )
    expected_dump_row_filename_type = 'user'
    expected_out_stat_filename_template = (
        '{model?fmt=%s}_'
        '{obtype?fmt=%s}_valid'
        '{valid?fmt=%Y%m%d}{valid_hour?fmt=%H}_init'
        '{fcst_init_hour?fmt=%s}.stat'
    )

    expected_out_stat_filename_type = 'user'
    test_model_info_list = st.parse_model_info()
    assert(test_model_info_list[0]['name'] == expected_name)
    assert(test_model_info_list[0]['reference_name'] == 
           expected_reference_name)
    assert(test_model_info_list[0]['obtype'] == expected_obtype)
    assert(test_model_info_list[0]['dump_row_filename_template'] == 
           expected_dump_row_filename_template)
    assert(test_model_info_list[0]['dump_row_filename_type'] == 
           expected_dump_row_filename_type)
    assert(test_model_info_list[0]['out_stat_filename_template'] == 
           expected_out_stat_filename_template)
    assert(test_model_info_list[0]['out_stat_filename_type'] == 
           expected_out_stat_filename_type)

def test_run_stat_analysis(metplus_config):
    # Test running of stat_analysis
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_filename = (st.config.getdir('OUTPUT_BASE')+'/stat_analysis'
                         +'/00Z/MODEL_TEST/MODEL_TEST_20190101.stat')
    comparison_filename = (METPLUS_BASE+'/internal_tests/data/stat_data/'
                           +'test_20190101.stat') 
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'
    st.run_stat_analysis()
    assert(os.path.exists(expected_filename))
    assert(os.path.getsize(expected_filename)
           == os.path.getsize(comparison_filename))

@pytest.mark.parametrize(
    'data_type, config_list, expected_list', [
      ('FCST', '\"0,*,*\"', ["0,*,*"]),
      ('FCST', '\"(0,*,*)\"', ["0,*,*"]),
      ('FCST', '\"0,*,*\", \"1,*,*\"', ["0,*,*", "1,*,*"]),
      ('FCST', '\"(0,*,*)\", \"(1,*,*)\"', ["0,*,*", "1,*,*"]),
      ('OBS', '\"0,*,*\"', ["0,*,*"]),
      ('OBS', '\"(0,*,*)\"', ["0,*,*"]),
      ('OBS', '\"0,*,*\", \"1,*,*\"', ["0,*,*", "1,*,*"]),
      ('OBS', '\"(0,*,*)\", \"(1,*,*)\"', ["0,*,*", "1,*,*"]),
    ]
)
def test_get_level_list(metplus_config, data_type, config_list, expected_list):
    config = metplus_config()
    config.set('config', f'{data_type}_LEVEL_LIST', config_list)

    saw = StatAnalysisWrapper(config)

    assert(saw.get_level_list(data_type) == expected_list)
