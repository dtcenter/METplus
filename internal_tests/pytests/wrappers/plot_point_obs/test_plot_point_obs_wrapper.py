#!/usr/bin/env python3

import pytest

import os

from datetime import datetime


from metplus.wrappers.plot_point_obs_wrapper import PlotPointObsWrapper

obs_dir = '/some/path/obs'
grid_dir = '/some/path/grid'


time_fmt = '%Y%m%d%H'
run_times = ['2012040912', '2012041000']


def set_minimum_config_settings(config, set_fields=True):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PlotPointObs')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', time_fmt)
    config.set('config', 'VALID_BEG', run_times[0])
    config.set('config', 'VALID_END', run_times[-1])
    config.set('config', 'VALID_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'PLOT_POINT_OBS_INPUT_DIR', obs_dir)
    config.set('config', 'PLOT_POINT_OBS_INPUT_TEMPLATE',
               ('pb2nc/ndas.{valid?fmt=%Y%m%d}.'
                't{valid?fmt=%H}z.prepbufr.tm00.nc'))
    #config.set('config', 'PLOT_POINT_OBS_GRID_INPUT_DIR', grid_dir)
    #config.set('config', 'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE',
    #           'nam_{init?fmt=%Y%m%d%H}_F{lead?fmt=%3H}.grib2')
    config.set('config', 'PLOT_POINT_OBS_OUTPUT_DIR',
               '{OUTPUT_BASE}/plot_point_obs')
    config.set('config', 'PLOT_POINT_OBS_OUTPUT_TEMPLATE',
               'nam_and_ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr_CONFIG.ps')


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'PLOT_POINT_OBS_INPUT_TEMPLATE': ('pb2nc/ndas.{valid?fmt=%Y%m%d}.'
                                            't{valid?fmt=%H}z.prepbufr.tm00.nc'
                                            ',ascii2nc/trmm_'
                                            '{valid?fmt=%Y%m%d%H}_3hr.nc'), },
         {}),

    ]
)
@pytest.mark.wrapper_c
def test_ensemble_stat_single_field(metplus_config, config_overrides,
                                    env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PlotPointObsWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    input_dir = wrapper.c_dict.get('INPUT_DIR')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [
        (f"{app_path} {verbosity} "
         f"{input_dir}/pb2nc/ndas.20120409.t12z.prepbufr.tm00.nc "
         f"{out_dir}/nam_and_ndas.20120409.t12z.prepbufr_CONFIG.ps"),
        (f"{app_path} {verbosity} "
         f"{input_dir}/pb2nc/ndas.20120410.t00z.prepbufr.tm00.nc "
         f"{out_dir}/nam_and_ndas.20120410.t00z.prepbufr_CONFIG.ps"),
    ]

    # add -point_obs argument if template has 2 items
    if ('PLOT_POINT_OBS_INPUT_TEMPLATE' in config_overrides and
            len(config_overrides['PLOT_POINT_OBS_INPUT_TEMPLATE'].split(',')) > 1):
        common_str = f' -point_obs {input_dir}/ascii2nc/trmm_'
        expected_cmds[0] += f'{common_str}2012040912_3hr.nc'
        expected_cmds[1] += f'{common_str}2012041000_3hr.nc'

    # add -config argument
    expected_cmds = [f'{item} -config {config_file}' for item in expected_cmds]

    # add -title if set

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

        # check that environment variables were set properly
        # including deprecated env vars (not in wrapper env var keys)
        env_var_keys = (wrapper.WRAPPER_ENV_VAR_KEYS +
                        [name for name in env_var_values
                         if name not in wrapper.WRAPPER_ENV_VAR_KEYS])
        for env_var_key in env_var_keys:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert(match is not None)
            actual_value = match.split('=', 1)[1]
            assert(env_var_values.get(env_var_key, '') == actual_value)


@pytest.mark.wrapper_c
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config()
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'PlotPointObsConfig_wrapped')

    wrapper = PlotPointObsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'PLOT_POINT_OBS_CONFIG_FILE', fake_config_name)
    wrapper = PlotPointObsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
