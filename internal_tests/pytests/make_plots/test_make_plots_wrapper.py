#!/usr/bin/env python
from __future__ import print_function
import os
import config_metplus
import datetime
import sys
import logging
import pytest
import datetime
from make_plots_wrapper import MakePlotsWrapper
import met_util as util
import produtil.setup

#
# These are tests (not necessarily unit tests) for the
# wrapper to make plots, make_plots_wrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  test_make_plots.conf.  This contains
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
@pytest.fixture
def make_plots_wrapper():
    """! Returns a default MakePlotsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty MakePlotsWrapper with some configuration values set
    # to /path/to:
    config = metplus_config()
    return MakePlotsWrapper(config, config.logger)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='MakePlotsWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='MakePlotsWrapper ')
        produtil.log.postmsg('make_plots_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        logger = util.get_logger(config)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'make_plots_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


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
METPLUS_BASE = os.getcwd().split('METplus')[0]+'METplus'

def test_set_plotting_script():
    # Independently test that plotting script
    # of the make_plots python command is 
    # being set up correctly
    mp = make_plots_wrapper()
    # Test 1
    test_plotting_script = 'plot_fake_script_name.py'
    mp.set_plotting_script('plot_fake_script_name.py')
    assert(test_plotting_script == mp.plotting_script)

def test_get_command():
    # Independently test that the make_plots python
    # command is being put together correctly with
    # python command followed by the full path
    # to the plotting script
    mp = make_plots_wrapper()
    # Test 1
    expected_command = (
        'python plot_fake_script_name.py'
    )
    mp.set_plotting_script('plot_fake_script_name.py')
    test_command = mp.get_command()
    assert(expected_command == test_command)

def test_create_c_dict():
    # Independently test that c_dict is being created
    # and that the wrapper and config reader 
    # is setting the values as expected
    mp = make_plots_wrapper()
    # Test 1
    c_dict = mp.create_c_dict()
    assert(c_dict['LOOP_ORDER'] == 'processes')
    assert(c_dict['PROCESS_LIST'] == 'StatAnalysis, MakePlots')
    assert(c_dict['INPUT_BASE_DIR'] == mp.config.getdir('INPUT_BASE')
                                       +'/plotting/stat_analysis')
    assert(c_dict['OUTPUT_BASE_DIR'] == mp.config.getdir('OUTPUT_BASE')
                                       +'/plotting/make_plots') 
    assert(c_dict['SCRIPTS_BASE_DIR'] == METPLUS_BASE+'/ush/plotting_scripts')
    assert(c_dict['DATE_TYPE'] == 'VALID')
    assert(c_dict['VALID_BEG'] == '20190101')
    assert(c_dict['VALID_END'] == '20190101')
    assert(c_dict['INIT_BEG'] == '')
    assert(c_dict['INIT_END'] == '')
    assert(c_dict['GROUP_LIST_ITEMS'] == [ 'FCST_INIT_HOUR_LIST' ])
    assert(c_dict['LOOP_LIST_ITEMS'] == [ 'FCST_VALID_HOUR_LIST' ])
    assert(c_dict['VAR_LIST'] == [ {'fcst_name': 'HGT', 'obs_name': 'HGT',
                                    'fcst_extra': '', 'obs_extra': '',
                                    'fcst_thresh': [], 'obs_thresh': [], 
                                    'fcst_level': 'P1000', 
                                    'obs_level': 'P1000', 'index': '1'},
                                    {'fcst_name': 'HGT', 'obs_name': 'HGT',
                                    'fcst_extra': '', 'obs_extra': '',
                                    'fcst_thresh': [], 'obs_thresh': [],
                                    'fcst_level': 'P850',
                                    'obs_level': 'P850', 'index': '1'}])
    assert(c_dict['MODEL_LIST'] == [ 'MODEL_TEST1', 'MODEL_TEST2'])
    assert(c_dict['DESC_LIST'] == [])
    assert(c_dict['FCST_LEAD_LIST'] == [ '24', '48', '72', '96', '120', 
                                         '144', '168', '192', '216', '240' ])
    assert(c_dict['OBS_LEAD_LIST'] == [])
    assert(c_dict['FCST_VALID_HOUR_LIST'] == [ '00', '06', '12', '18' ])
    assert(c_dict['FCST_INIT_HOUR_LIST'] == [ '00' ])
    assert(c_dict['OBS_VALID_HOUR_LIST'] == [])
    assert(c_dict['OBS_INIT_HOUR_LIST'] == [])
    assert(c_dict['VX_MASK_LIST'] == [ 'G002', 'NHX', 'SHX',
                                       'TRO', 'PNA'])
    assert(c_dict['INTERP_MTHD_LIST'] == [])
    assert(c_dict['INTERP_PNTS_LIST'] == [])
    assert(c_dict['COV_THRESH_LIST'] == [])
    assert(c_dict['ALPHA_LIST'] == [])
    assert(c_dict['LINE_TYPE_LIST'] == [ 'SL1L2', 'VL1L2' ])
    assert(c_dict['USER_SCRIPT_LIST'] == [])
    assert(c_dict['VERIF_CASE'] == 'grid2grid')
    assert(c_dict['VERIF_TYPE'] == 'pres')
    assert(c_dict['STATS_LIST'] == [ 'bias', 'rmse', 'msess', 'rsd',
                                     'rmse_md', 'rmse_pv', 'pcor' ])
    assert(c_dict['AVERAGE_METHOD'] == 'MEAN')
    assert(c_dict['CI_METHOD'] == 'EMC')
    assert(c_dict['VERIF_GRID'] == 'G002')
    assert(c_dict['EVENT_EQUALIZATION'] == 'False')
    assert(c_dict['LOG_METPLUS'] == mp.config.getdir('OUTPUT_BASE')
                                    +'/logs/master_metplus.log.'
                                    +mp.config.getstr('config',
                                                      'LOG_TIMESTAMP'))
    assert(c_dict['LOG_LEVEL'] == 'DEBUG')
    assert(c_dict['MET_BASE'] == mp.config.getdir('MET_INSTALL_DIR')
                                 +'/share/met')
def test_list_to_str():
    # Independently test that a list of strings
    # are being converted to a one
    # string list correctly
    mp = make_plots_wrapper()
    # Test 1
    expected_list = 'a, b, c'
    test_list = mp.list_to_str([ 'a', 'b', 'c' ])
    assert(expected_list == test_list)
    # Test 2
    expected_list = '0, 1, 2'
    test_list = mp.list_to_str([ '0', '1', '2' ])
    assert(expected_list == test_list)

def test_set_lists_as_loop_or_group():
    # Independently test that the lists that are set
    # in the config file are being set 
    # accordingly based on their place 
    # in GROUP_LIST_ITEMS and LOOP_LIST_ITEMS 
    # and those not set are set to GROUP_LIST_ITEMS
    mp = make_plots_wrapper()
    # Test 1
    expected_lists_to_group_items = [ 'FCST_INIT_HOUR_LIST', 'DESC_LIST',
                                      'FCST_LEAD_LIST', 'OBS_LEAD_LIST',
                                      'OBS_VALID_HOUR_LIST', 'MODEL_LIST',
                                      'OBS_INIT_HOUR_LIST', 'FCST_UNITS_LIST',
                                      'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                                      'OBS_LEVEL_LIST', 'INTERP_MTHD_LIST',
                                      'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                                      'OBS_THRESH_LIST', 'COV_THRESH_LIST',
                                      'ALPHA_LIST', 'LINE_TYPE_LIST',
                                      'STATS_LIST' ]
    expected_lists_to_loop_items = [ 'FCST_VALID_HOUR_LIST', 'VX_MASK_LIST',
                                     'FCST_VAR_LIST', 'OBS_VAR_LIST' ]
    config_dict = {}
    config_dict['LOOP_ORDER'] = 'processes'
    config_dict['PROCESS_LIST'] = 'StatAnalysis, MakePlots'
    config_dict['OUTPUT_BASE_DIR'] = 'OUTPUT_BASE/stat_analysis'
    config_dict['GROUP_LIST_ITEMS'] = [ 'FCST_INIT_HOUR_LIST' ]
    config_dict['LOOP_LIST_ITEMS'] = [ 'FCST_VALID_HOUR_LIST' ]
    config_dict['FCST_VAR_LIST'] = [ 'HGT' ]
    config_dict['OBS_VAR_LIST'] = [ 'HGT' ]
    config_dict['FCST_LEVEL_LIST'] = [ 'P1000', 'P500' ]
    config_dict['OBS_LEVEL_LIST'] = [ 'P1000', 'P500' ]
    config_dict['FCST_UNITS_LIST'] = []
    config_dict['OBS_UNITS_LIST'] = []
    config_dict['FCST_THRESH_LIST'] = []
    config_dict['OBS_THRESH_LIST'] = []
    config_dict['MODEL_LIST'] = [ 'MODEL_TEST1', 'MODEL_TEST2' ]
    config_dict['DESC_LIST'] = []
    config_dict['FCST_LEAD_LIST'] = [ '24', '48', '72', '96', '120',
                                     '144', '168', '192', '216', '240' ]
    config_dict['OBS_LEAD_LIST'] = []
    config_dict['FCST_VALID_HOUR_LIST'] = [ '00', '06', '12', '18' ]
    config_dict['FCST_INIT_HOUR_LIST'] = [ '00' ]
    config_dict['OBS_VALID_HOUR_LIST'] = []
    config_dict['OBS_INIT_HOUR_LIST'] = []
    config_dict['VX_MASK_LIST'] = [ 'G002', 'NHX', 'SHX', 'TRO', 'PNA' ]
    config_dict['INTERP_MTHD_LIST'] = []
    config_dict['INTERP_PNTS_LIST'] = []
    config_dict['COV_THRESH_LIST'] = []
    config_dict['ALPHA_LIST'] = []
    config_dict['LINE_TYPE_LIST'] = [ 'SL1L2', 'VL1L2' ]
    config_dict['STATS_LIST'] = [ 'bias', 'rmse', 'msess', 'rsd',
                                   'rmse_md', 'rmse_pv', 'pcor' ]
    test_lists_to_group_items, test_lists_to_loop_items = (
        mp.set_lists_loop_or_group([ 'FCST_INIT_HOUR_LIST' ],
                                   [ 'FCST_VALID_HOUR_LIST' ],
                                   config_dict)
    )
    assert(all(elem in expected_lists_to_group_items
               for elem in test_lists_to_group_items))
    assert(all(elem in expected_lists_to_loop_items
               for elem in test_lists_to_loop_items))

def test_parse_model_info():
    # Independently test the creation of 
    # the model information dictionary
    # and the reading from the config file
    # are as expected
    mp = make_plots_wrapper()
    # Test 1
    expected_name1 = 'MODEL_TEST1'
    expected_reference_name1 = 'MODEL_TEST1'
    expected_obtype1 = 'MODEL_TEST1_ANL'
    expected_name2 = 'MODEL_TEST2'
    expected_reference_name2 = 'TEST2_MODEL'
    expected_obtype2 = 'ANLYS2'
    test_model_info_list, test_model_indices = mp.parse_model_info()
    assert(test_model_info_list[0]['name'] == expected_name1)
    assert(test_model_info_list[0]['reference_name'] ==
           expected_reference_name1)
    assert(test_model_info_list[0]['obtype'] == expected_obtype1)
    assert(test_model_info_list[1]['name'] == expected_name2)
    assert(test_model_info_list[1]['reference_name'] ==
           expected_reference_name2)
    assert(test_model_info_list[1]['obtype'] == expected_obtype2)

