#!/usr/bin/env python

import os
import sys
import re
import csv
import pytest

import produtil

from metplus.wrappers.tc_pairs_wrapper import TCPairsWrapper
from metplus.util import met_util as util

bdeck_template = 'b{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'
adeck_template = 'a{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'
edeck_template = 'e{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'

output_template = '{basin?fmt=%s}q{date?fmt=%Y%m%d%H}.gfso.{cyclone?fmt=%s}'

time_fmt = '%Y%m%d%H'
run_times = ['2014121318']

def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCPairs')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'TC_PAIRS_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCPairsConfig_wrapped')
    config.set('config', 'TC_PAIRS_BDECK_TEMPLATE', bdeck_template)

    config.set('config', 'TC_PAIRS_OUTPUT_DIR',
               '{OUTPUT_BASE}/TCPairs/output')
    config.set('config', 'TC_PAIRS_OUTPUT_TEMPLATE', output_template)

    config.set('config', 'TC_PAIRS_READ_ALL_FILES', False)

    # can set adeck or edeck variables
    config.set('config', 'TC_PAIRS_ADECK_TEMPLATE', adeck_template)

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),
        ({'TC_PAIRS_BASIN': 'AL, ML'}, {'METPLUS_BASIN': 'basin = ["ML"];'}),

    ]
)
def test_tc_pairs_loop_order_processes(metplus_config, config_overrides,
                                       env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data',
                                 'tc_pairs')
    bdeck_dir = os.path.join(test_data_dir, 'bdeck')
    adeck_dir = os.path.join(test_data_dir, 'adeck')
    edeck_dir = os.path.join(test_data_dir, 'edeck')

    config.set('config', 'TC_PAIRS_BDECK_INPUT_DIR', bdeck_dir)
    config.set('config', 'TC_PAIRS_ADECK_INPUT_DIR', adeck_dir)

    # LOOP_ORDER processes runs once, times runs once per time
    config.set('config', 'LOOP_ORDER', 'processes')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    if 'METPLUS_INIT_BEG' not in env_var_values:
        env_var_values['METPLUS_INIT_BEG'] = f'init_beg = "{run_times[0]}";'

    if 'METPLUS_INIT_END' not in env_var_values:
        env_var_values['METPLUS_INIT_END'] = f'init_end = "{run_times[-1]}";'

    wrapper = TCPairsWrapper(config)
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"-bdeck {bdeck_dir}/bmlq2014123118.gfso.0104 "
                      f"-adeck {adeck_dir}/amlq2014123118.gfso.0104 "
                      f"-config {config_file} "
                      f"-out {out_dir}/mlq2014121318.gfso.0104"),
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
            print(f'Checking env var: {env_var_key}')
            actual_value = match.split('=', 1)[1]
            assert(env_var_values.get(env_var_key, '') == actual_value)
