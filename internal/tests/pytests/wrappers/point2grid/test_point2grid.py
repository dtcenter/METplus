#!/usr/bin/env python3

import pytest
import datetime
import os

from metplus.wrappers.point2grid_wrapper import Point2GridWrapper
from metplus.util import time_util

input_dir = '/some/path/input'
input_name = 'TMP'

# grid to use if grid is not set with command line argument
grid_dir = '/some/path/grid'
grid_template = os.path.join(grid_dir, '{valid?fmt=%Y%m%d}.nc')


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'Point2Grid')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2017060100')
    config.set('config', 'INIT_END', '2017060300')
    config.set('config', 'INIT_INCREMENT', '24H')
    config.set('config', 'LEAD_SEQ', '12H')

    # required variables for input/output, to grid, and input field
    config.set('config', 'POINT2GRID_INPUT_DIR', input_dir)
    config.set('config', 'POINT2GRID_INPUT_TEMPLATE',
               'input.{init?fmt=%Y%m%d%H}_f{lead?fmt=%2H}.nc')
    config.set('config', 'POINT2GRID_OUTPUT_DIR', '{OUTPUT_BASE}/out')
    config.set('config', 'POINT2GRID_OUTPUT_TEMPLATE',
               'output.{valid?fmt=%Y%m%d%H}.nc')
    config.set('config', 'POINT2GRID_REGRID_TO_GRID', grid_template)
    config.set('config', 'POINT2GRID_INPUT_FIELD', input_name)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (6, 12, 0.5, 0, True),
        (6, 12, 0.6, 1, True),
        (6, 12, 0.5, 6, False),
    ]
)
@pytest.mark.wrapper
def test_point2grid_missing_inputs(metplus_config, get_test_data_dir,
                                   missing, run, thresh, errors,
                                   allow_missing):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'POINT2GRID_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'POINT2GRID_INPUT_THRESH', thresh)
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'POINT2GRID_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'POINT2GRID_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')

    wrapper = Point2GridWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


@pytest.mark.parametrize(
    'config_overrides, env_var_values, optional_args', [
        ({}, {}, []),
        ({'POINT2GRID_REGRID_METHOD': 'UW_MEAN'}, {}, ['-method UW_MEAN']),
        ({'POINT2GRID_REGRID_METHOD': 'UW_MEAN',
          'POINT2GRID_GAUSSIAN_DX': '2',}, {},
         ['-method UW_MEAN', '-gaussian_dx 2']),
        ({'POINT2GRID_GAUSSIAN_RADIUS': '81.231'}, {},
         ['-gaussian_radius 81.231']),
        ({'POINT2GRID_PROB_CAT_THRESH': '1'}, {}, ['-prob_cat_thresh 1']),
        ({'POINT2GRID_VLD_THRESH': '0.5'}, {}, ['-vld_thresh 0.5']),
        ({'POINT2GRID_ADP': '{valid?fmt=%Y%m}.nc'}, {}, ['-adp 201706.nc']),
        ({'POINT2GRID_REGRID_TO_GRID': 'G212'}, {}, []),
        ({'POINT2GRID_REGRID_TO_GRID': 'lambert 614 428 12.190 -133.459 -95.0 12.19058 6367.47 25.0 N'}, {}, []),
        ({'POINT2GRID_INPUT_LEVEL': '(*,*)'}, {}, []),
        ({'POINT2GRID_VALID_TIME': '20240509_120800', },
         {'METPLUS_VALID_TIME': 'valid_time = "20240509_120800";'}, []),

        ({'POINT2GRID_OBS_WINDOW_BEG': '-5400', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -5400;}'}, []),

        ({'POINT2GRID_OBS_WINDOW_END': '3600', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {end = 3600;}'}, []),

        ({'POINT2GRID_OBS_WINDOW_BEG': '-3600', 'POINT2GRID_OBS_WINDOW_END': '5400'},
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -3600;end = 5400;}'}, []),
        ({'POINT2GRID_MESSAGE_TYPE': 'ADPSFC, ADPUPA'},
         {'METPLUS_MESSAGE_TYPE': 'message_type = ["ADPSFC", "ADPUPA"];'}, []),

        ({'POINT2GRID_VAR_NAME_MAP1_KEY': '3', 'POINT2GRID_VAR_NAME_MAP1_VAL': 'MAGIC'},
         {'METPLUS_VAR_NAME_MAP_LIST': 'var_name_map = [{key = "3";val = "MAGIC";}];'}, []),

        ({'POINT2GRID_VAR_NAME_MAP1_KEY': '13', 'POINT2GRID_VAR_NAME_MAP1_VAL': 'LUCKY',
          'POINT2GRID_VAR_NAME_MAP2_KEY': '3', 'POINT2GRID_VAR_NAME_MAP2_VAL': 'MAGIC'
          },
         {'METPLUS_VAR_NAME_MAP_LIST': 'var_name_map = [{key = "13";val = "LUCKY";},{key = "3";val = "MAGIC";}];'}, []),

        ({'POINT2GRID_OBS_QUALITY_INC': '0, 1, 2', },
         {'METPLUS_OBS_QUALITY_INC': 'obs_quality_inc = ["0", "1", "2"];'}, []),

        ({'POINT2GRID_OBS_QUALITY_EXC': '3,4, 5', },
         {'METPLUS_OBS_QUALITY_EXC': 'obs_quality_exc = ["3", "4", "5"];'}, []),
        ({'POINT2GRID_GOES_QC_FLAGS': '0,1'}, {}, ['-goes_qc 0,1']),
        ({'POINT2GRID_QC_FLAGS': '0,1'}, {}, ['-goes_qc 0,1']),
        ({'POINT2GRID_GOES_QC_FLAGS': '0,1', 'POINT2GRID_QC_FLAGS': '2,3'}, {}, ['-goes_qc 0,1']),

    ]
)
@pytest.mark.wrapper
def test_point2grid_run(metplus_config, config_overrides, optional_args,
                        env_var_values):
    config = metplus_config
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = Point2GridWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    input_files = (
        f'{input_dir}/input.2017060100_f12.nc',
        f'{input_dir}/input.2017060200_f12.nc',
        f'{input_dir}/input.2017060300_f12.nc',
    )
    output_files = (
        f'{out_dir}/output.2017060112.nc',
        f'{out_dir}/output.2017060212.nc',
        f'{out_dir}/output.2017060312.nc',
    )

    if 'POINT2GRID_REGRID_TO_GRID' in config_overrides:
        grids = (
            config_overrides['POINT2GRID_REGRID_TO_GRID'],
            config_overrides['POINT2GRID_REGRID_TO_GRID'],
            config_overrides['POINT2GRID_REGRID_TO_GRID']
        )
        # add quotation marks around grid if it is include spaces
        if len(config_overrides['POINT2GRID_REGRID_TO_GRID'].split()) > 1:
            grids = [f'"{grid}"' for grid in grids]
    else:
        grids = (
            os.path.join(grid_dir, '20170601.nc'),
            os.path.join(grid_dir, '20170602.nc'),
            os.path.join(grid_dir, '20170603.nc')
        )

    if 'POINT2GRID_INPUT_LEVEL' in config_overrides:
        level = config_overrides['POINT2GRID_INPUT_LEVEL']
    else:
        level = ''

    config_file = wrapper.c_dict.get('CONFIG_FILE')
    extra_args = " ".join(optional_args) + " " if optional_args else ""

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    expected_cmds = []
    for idx in range(0, len(input_files)):
        expected_cmds.append(
            f'{app_path} {input_files[idx]} {grids[idx]} {output_files[idx]}'
            f' -field \'name="{input_name}"; level="{level}";\''
            f' -config {config_file} {extra_args}{verbosity}'
        )

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        # including deprecated env vars (not in wrapper env var keys)
        for env_var_key in env_var_keys:
            print(f"ENV VAR: {env_var_key}")
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            value = match.split('=', 1)[1]
            assert env_var_values.get(env_var_key, '') == value


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'Point2GridConfig_wrapped')

    wrapper = Point2GridWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'POINT2GRID_CONFIG_FILE', fake_config_name)
    wrapper = Point2GridWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
