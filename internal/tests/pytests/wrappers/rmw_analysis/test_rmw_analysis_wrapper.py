#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.rmw_analysis_wrapper import RMWAnalysisWrapper

input_template = 'tc_rmw_aal14{date?fmt=%Y}.nc'
output_template = 'rmw_analysis_aal14{date?fmt=%Y}.nc'

time_fmt = '%Y'
run_times = ['2023']

data_fmt = 'field = [{ name="PRMSL"; },{ name="TMP"; }];'


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'RMWAnalysis')
    config.set('config', 'RMW_ANALYSIS_RUNTIME_FREQ', 'RUN_ONCE_PER_INIT_OR_VALID')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'RMW_ANALYSIS_INPUT_TEMPLATE', input_template)
    config.set('config', 'RMW_ANALYSIS_OUTPUT_DIR', '{OUTPUT_BASE}/rmw_analysis')
    config.set('config', 'RMW_ANALYSIS_OUTPUT_TEMPLATE', output_template)
    config.set('config', 'BOTH_VAR1_NAME', 'PRMSL')
    config.set('config', 'BOTH_VAR2_NAME', 'TMP')


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),
        ({'MODEL': 'GFSO, GFSA'}, {'METPLUS_MODEL': 'model = ["GFSO", "GFSA"];'}),
        ({'RMW_ANALYSIS_MODEL': 'GFSO, GFSA'}, {'METPLUS_MODEL': 'model = ["GFSO", "GFSA"];'}),
        ({'RMW_ANALYSIS_BASIN': 'AL,BO'}, {'METPLUS_BASIN': 'basin = ["AL", "BO"];'}),
        ({'RMW_ANALYSIS_STORM_NAME': 'STU,JOEY'}, {'METPLUS_STORM_NAME': 'storm_name = ["STU", "JOEY"];'}),
        ({'RMW_ANALYSIS_STORM_ID': 'AL092022,  ML082023'}, {'METPLUS_STORM_ID': 'storm_id = ["AL092022", "ML082023"];'}),
        ({'RMW_ANALYSIS_CYCLONE': '14,43'}, {'METPLUS_CYCLONE': 'cyclone = ["14", "43"];'}),
        ({'RMW_ANALYSIS_INIT_BEG': '20220924_00', }, {'METPLUS_INIT_BEG': 'init_beg = "20220924_00";'}),
        ({'RMW_ANALYSIS_INIT_END': '20220924_00', }, {'METPLUS_INIT_END': 'init_end = "20220924_00";'}),
        ({'RMW_ANALYSIS_VALID_BEG': '20220924_00', }, {'METPLUS_VALID_BEG': 'valid_beg = "20220924_00";'}),
        ({'RMW_ANALYSIS_VALID_END': '20220924_00', }, {'METPLUS_VALID_END': 'valid_end = "20220924_00";'}),
        ({'RMW_ANALYSIS_INIT_MASK': 'MET_BASE/poly/LMV.poly', }, {'METPLUS_INIT_MASK': 'init_mask = "MET_BASE/poly/LMV.poly";'}),
        ({'RMW_ANALYSIS_VALID_MASK': 'MET_BASE/poly/LMV.poly', }, {'METPLUS_VALID_MASK': 'valid_mask = "MET_BASE/poly/LMV.poly";'}),

    ]
)
@pytest.mark.wrapper
def test_rmw_analysis_run(metplus_config, tmp_path_factory, config_overrides,
                          env_var_values, compare_command_and_env_vars):
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    # create temporary directory and set input dir to it
    fake_input_dir = tmp_path_factory.mktemp("tc_rmw")
    config.set('config', 'RMW_ANALYSIS_INPUT_DIR', fake_input_dir)

    wrapper = RMWAnalysisWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    data_file = os.path.join(fake_input_dir, 'tc_rmw_aal142023.nc')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"

    expected_cmds = [
        (f"{app_path} -data {data_file} -config {config_file} "
         f"-out {out_dir}/rmw_analysis_aal142023.nc {verbosity}"),
    ]

    all_cmds = wrapper.run_all_times()
    special_values = {
        'METPLUS_DATA_FIELD': data_fmt,
    }
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values,
                                 wrapper, special_values)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    set_minimum_config_settings(config)

    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'RMWAnalysisConfig_wrapped')

    wrapper = RMWAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'RMW_ANALYSIS_CONFIG_FILE', fake_config_name)
    wrapper = RMWAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
