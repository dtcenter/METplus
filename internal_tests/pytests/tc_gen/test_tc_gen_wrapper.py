#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.grid_stat_wrapper import GridStatWrapper
from metplus.util import met_util as util
from metplus.util import time_util

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'TC_GEN_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'TC_GEN_INIT_FREQUENCY': '8'},
         {'METPLUS_INIT_FREQ': 'init_freq = 8;'}),

        ({'TC_GEN_VALID_FREQUENCY': '8'},
         {'METPLUS_VALID_FREQ': 'valid_freq = 8;'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),

        ({'TC_GEN_': ''},
         {'METPLUS_': ' = "";'}),
    ]
)
def test_grid_stat_single_field(metplus_config, config_overrides,
                                env_var_values):
    fcst_dir = '/some/path/fcst'
    obs_dir = '/some/path/obs'
    fcst_name = 'APCP'
    fcst_level = 'A03'
    obs_name = 'APCP_03'
    obs_level_no_quotes = '(*,*)'
    obs_level = f'"{obs_level_no_quotes}"'
    fcst_fmt = f'field = [{{ name="{fcst_name}"; level="{fcst_level}"; }}];'
    obs_fmt = (f'field = [{{ name="{obs_name}"; '
               f'level="{obs_level_no_quotes}"; }}];')
    config = metplus_config()

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'GridStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080712')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'GRID_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/GridStatConfig_wrapped')
    config.set('config', 'FCST_GRID_STAT_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_GRID_STAT_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_GRID_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_GRID_STAT_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'GRID_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/GridStat/output')
    config.set('config', 'GRID_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = GridStatWrapper(config)
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"{fcst_dir}/2005080700/fcst_file_F012 "
                      f"{obs_dir}/2005080712/obs_file "
                      f"{config_file} -outdir {out_dir}/2005080712"),
                     (f"{app_path} {verbosity} "
                      f"{fcst_dir}/2005080712/fcst_file_F012 "
                      f"{obs_dir}/2005080800/obs_file "
                      f"{config_file} -outdir {out_dir}/2005080800"),
                     ]


    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

        # check that environment variables were set properly
        for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert(match is not None)
            value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert(value == fcst_fmt)
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert (value == obs_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == value)
