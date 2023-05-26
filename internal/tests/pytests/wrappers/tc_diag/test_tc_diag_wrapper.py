#!/usr/bin/env python3

import pytest

import os
from datetime import datetime

from metplus.wrappers.tc_diag_wrapper import TCDiagWrapper

deck_template = 'aal14{date?fmt=%Y}_short.dat'
input_template = 'gfs.subset.t00z.pgrb2.0p25.f*'
output_template = 'tc_diag_aal14{date?fmt=%Y}.nc'

time_fmt = '%Y%m%d%H'
run_times = ['2016092900']

data_fmt = (
    'field = [{ name="PRMSL"; level="L0"; },'
    '{ name="TMP"; level="P1000"; },'
    '{ name="TMP"; level="P900"; },'
    '{ name="TMP"; level="P800"; },'
    '{ name="TMP"; level="P700"; },'
    '{ name="TMP"; level="P500"; },'
    '{ name="TMP"; level="P100"; }];'
)


def get_data_dir(config):
    return os.path.join(config.getdir('METPLUS_BASE'),
                        'internal', 'tests', 'data', 'tc_pairs')


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCDiag')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '6H')
    config.set('config', 'TC_DIAG_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCDiagConfig_wrapped')
    config.set('config', 'TC_DIAG_DECK_TEMPLATE', deck_template)
    config.set('config', 'TC_DIAG_INPUT_TEMPLATE', input_template)
    config.set('config', 'TC_DIAG_OUTPUT_DIR',
               '{OUTPUT_BASE}/TCDiag/output')
    config.set('config', 'TC_DIAG_OUTPUT_TEMPLATE', output_template)

    config.set('config', 'BOTH_VAR1_NAME', 'PRMSL')
    config.set('config', 'BOTH_VAR1_LEVELS', 'L0')
    config.set('config', 'BOTH_VAR2_NAME', 'TMP')
    config.set('config', 'BOTH_VAR2_LEVELS', 'P1000, P900, P800, P700, P500, P100')


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),

    ]
)
@pytest.mark.wrapper
def test_tc_diag_run(metplus_config, config_overrides,
                     env_var_values):
    config = metplus_config

    set_minimum_config_settings(config)

    test_data_dir = get_data_dir(config)
    deck_dir = os.path.join(test_data_dir, 'bdeck')

    config.set('config', 'TC_DIAG_DECK_INPUT_DIR', deck_dir)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCDiagWrapper(config)
    assert wrapper.isOK

    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    file_list_file = f"{file_list_dir}/aal142016_short.dat_data_files.txt"
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [(f"{app_path} "
                      f"-deck {deck_dir}/aal142016_short.dat "
                      f"-data {file_list_file} "
                      f"-config {config_file} "
                      f"-out {out_dir}/tc_diag_aal142016.nc "
                      f"{verbosity}"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        for env_var_key in env_var_keys:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            print(f'Checking env var: {env_var_key}')
            actual_value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_DATA_FIELD':
                assert actual_value == data_fmt
            else:
                assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCDiagConfig_wrapped')

    wrapper = TCDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_DIAG_CONFIG_FILE', fake_config_name)
    wrapper = TCDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
