#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.make_plots_wrapper import MakePlotsWrapper

METPLUS_BASE = os.getcwd().split('/internal')[0]


def make_plots_wrapper(metplus_config):
    """! Returns a default MakePlotsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty MakePlotsWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'test_make_plots.conf'))
    config = metplus_config(extra_configs)
    return MakePlotsWrapper(config)


@pytest.mark.plotting
def test_get_command(metplus_config):
    # Independently test that the make_plots python
    # command is being put together correctly with
    # python command followed by the full path
    # to the plotting script
    mp = make_plots_wrapper(metplus_config)
    # Test 1
    expected_command = (
        'python plot_fake_script_name.py'
    )
    mp.plotting_script = 'plot_fake_script_name.py'
    test_command = mp.get_command()
    assert(expected_command == test_command)


@pytest.mark.plotting
def test_create_c_dict(metplus_config):
    # Independently test that c_dict is being created
    # and that the wrapper and config reader 
    # is setting the values as expected
    mp = make_plots_wrapper(metplus_config)
    # Test 1
    c_dict = mp.create_c_dict()
    # NOTE: MakePlots relies on output from StatAnalysis
    #       so its input resides in the output of StatAnalysis
    assert(c_dict['INPUT_BASE_DIR'] == mp.config.getdir('OUTPUT_BASE')
                                       +'/plotting/stat_analysis')
    assert(c_dict['OUTPUT_BASE_DIR'] == mp.config.getdir('OUTPUT_BASE')
                                       +'/plotting/make_plots') 
    assert(os.path.realpath(c_dict['SCRIPTS_BASE_DIR']) == METPLUS_BASE+'/ush/plotting_scripts')
    assert(c_dict['DATE_TYPE'] == 'VALID')
    assert(c_dict['VALID_BEG'] == '20190101')
    assert(c_dict['VALID_END'] == '20190101')
    assert(c_dict['INIT_BEG'] == '')
    assert(c_dict['INIT_END'] == '')
    assert(c_dict['GROUP_LIST_ITEMS'] == [ 'FCST_INIT_HOUR_LIST' ])
    assert(c_dict['LOOP_LIST_ITEMS'] == [ 'FCST_VALID_HOUR_LIST' ])
    assert(c_dict['VAR_LIST'] == [{'fcst_name': 'HGT',
                                   'fcst_output_name': 'HGT',
                                   'obs_name': 'HGT',
                                   'obs_output_name': 'HGT',
                                   'fcst_extra': '', 'obs_extra': '',
                                   'fcst_thresh': [], 'obs_thresh': [],
                                   'fcst_level': 'P1000',
                                   'obs_level': 'P1000', 'index': '1'},
                                  {'fcst_name': 'HGT',
                                   'fcst_output_name': 'HGT',
                                    'obs_name': 'HGT',
                                   'obs_output_name': 'HGT',
                                   'fcst_extra': '', 'obs_extra': '',
                                   'fcst_thresh': [], 'obs_thresh': [],
                                   'fcst_level': 'P850',
                                   'obs_level': 'P850', 'index': '1'}])
    assert(c_dict['MODEL_LIST'] == [ 'MODEL_TEST1', 'MODEL_TEST2'])
    assert(c_dict['DESC_LIST'] == [])
    assert(c_dict['FCST_LEAD_LIST'] == [ '24', '48' ]) 
    assert(c_dict['OBS_LEAD_LIST'] == [])
    assert(c_dict['FCST_VALID_HOUR_LIST'] == [ '00', '06', '12', '18' ])
    assert(c_dict['FCST_INIT_HOUR_LIST'] == [ '00', '06', '12', '18' ])
    assert(c_dict['OBS_VALID_HOUR_LIST'] == [])
    assert(c_dict['OBS_INIT_HOUR_LIST'] == [])
    assert(c_dict['VX_MASK_LIST'] == [ 'NHX' ])
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
                                    +'/logs/metplus.log')
