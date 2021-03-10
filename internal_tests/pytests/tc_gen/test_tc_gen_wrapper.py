#!/usr/bin/env python3

import os
import sys
import pytest
import datetime

from metplus.wrappers.tc_gen_wrapper import TCGenWrapper

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'model1, model2'},
         {'METPLUS_MODEL': 'model = ["model1", "model2"];'}),

        ({'TC_GEN_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'TC_GEN_INIT_FREQUENCY': '8'},
         {'METPLUS_INIT_FREQ': 'init_freq = 8;'}),

        ({'TC_GEN_VALID_FREQUENCY': '8'},
         {'METPLUS_VALID_FREQ': 'valid_freq = 8;'}),

        ({'TC_GEN_FCST_HR_WINDOW_BEGIN': '7'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {beg = 7;}'}),

        ({'TC_GEN_FCST_HR_WINDOW_END': '119'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {end = 119;}'}),

        ({'TC_GEN_FCST_HR_WINDOW_BEGIN': '7',
          'TC_GEN_FCST_HR_WINDOW_END': '119'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {beg = 7;end = 119;}'}),

        ({'TC_GEN_MIN_DURATION': '13'},
         {'METPLUS_MIN_DURATION': 'min_duration = 13;'}),

        ({'TC_GEN_FCST_GENESIS_VMAX_THRESH': '>3'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {vmax_thresh = >3;}'}),

        ({'TC_GEN_FCST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {mslp_thresh = >4;}'}),

        ({'TC_GEN_FCST_GENESIS_VMAX_THRESH': '>3',
          'TC_GEN_FCST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {vmax_thresh = >3;mslp_thresh = >4;}'}),

        ({'TC_GEN_BEST_GENESIS_TECHNIQUE': 'WORST'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {technique = "WORST";}'}),

        ({'TC_GEN_BEST_GENESIS_CATEGORY': 'PH, SH'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {category = ["PH", "SH"];}'}),

        ({'TC_GEN_BEST_GENESIS_VMAX_THRESH': '>3'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {vmax_thresh = >3;}'}),

        ({'TC_GEN_BEST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {mslp_thresh = >4;}'}),

        ({'TC_GEN_BEST_GENESIS_TECHNIQUE': 'WORST',
          'TC_GEN_BEST_GENESIS_CATEGORY': 'PH, SH',
          'TC_GEN_BEST_GENESIS_VMAX_THRESH': '>3',
          'TC_GEN_BEST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_BEST_GENESIS_DICT': ('best_genesis = {technique = "WORST";'
                                        'category = ["PH", "SH"];'
                                        'vmax_thresh = >3;'
                                        'mslp_thresh = >4;}')}),

        ({'TC_GEN_OPER_TECHNIQUE': 'CARQ'},
         {'METPLUS_OPER_TECHNIQUE': 'oper_technique = "CARQ";'}),

        ({'TC_GEN_FILTER_1': 'desc = "uno";'},
         {'METPLUS_FILTER': 'filter = [{desc = "uno";}];'}),

        ({'TC_GEN_FILTER_2': 'desc = "dos";'},
         {'METPLUS_FILTER': 'filter = [{desc = "dos";}];'}),
        ({'TC_GEN_FILTER_1': 'desc = "uno";',
          'TC_GEN_FILTER_2': 'desc = "dos";'},
         {'METPLUS_FILTER': 'filter = [{desc = "uno";}, {desc = "dos";}];'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),
    ]
)
def test_tc_gen(metplus_config, config_overrides, env_var_values):
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data',
                                 'tc_gen')
    track_dir = os.path.join(test_data_dir, 'track')
    genesis_dir = os.path.join(test_data_dir, 'genesis')

    track_template = 'track_*{init?fmt=%Y}*'
    genesis_template = 'genesis_*{init?fmt=%Y}*'

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCGen')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y')
    config.set('config', 'INIT_BEG', '2016')
    config.set('config', 'LOOP_ORDER', 'processes')

    config.set('config', 'TC_GEN_TRACK_INPUT_DIR', track_dir)
    config.set('config', 'TC_GEN_TRACK_INPUT_TEMPLATE', track_template)
    config.set('config', 'TC_GEN_GENESIS_INPUT_DIR', genesis_dir)
    config.set('config', 'TC_GEN_GENESIS_INPUT_TEMPLATE', genesis_template)
    config.set('config', 'TC_GEN_OUTPUT_DIR', '{OUTPUT_BASE}/TCGen/output')
    config.set('config', 'TC_GEN_OUTPUT_TEMPLATE', 'tc_gen_{init?fmt=%Y}')

    config.set('config', 'TC_GEN_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCGenConfig_wrapped')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCGenWrapper(config)
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    file_list_dir = os.path.join(wrapper.config.getdir('STAGING_DIR'),
                                 'file_lists')
    genesis_ext = '0101000000_tc_gen_genesis.txt'
    track_ext = '0101000000_tc_gen_track.txt'
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [
        (f"{app_path} {verbosity} "
         f"-genesis {file_list_dir}/2016{genesis_ext} "
         f"-track {file_list_dir}/2016{track_ext} "
         f"-config {config_file} -out {out_dir}/tc_gen_2016"),
    ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

        # check that environment variables were set properly
        for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert(match is not None)
            value = match.split('=', 1)[1]
            assert(env_var_values.get(env_var_key, '') == value)
