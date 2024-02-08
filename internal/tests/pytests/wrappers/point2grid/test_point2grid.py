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
    'config_overrides, optional_args', [
        ({}, {}),
        ({'POINT2GRID_REGRID_METHOD': 'UW_MEAN'}, ['-method UW_MEAN']),
        ({'POINT2GRID_REGRID_METHOD': 'UW_MEAN',
          'POINT2GRID_GAUSSIAN_DX': '2',},
         ['-method UW_MEAN', '-gaussian_dx 2']),
        ({'POINT2GRID_GAUSSIAN_RADIUS': '81.231'},
         ['-gaussian_radius 81.231']),
        ({'POINT2GRID_PROB_CAT_THRESH': '1'}, ['-prob_cat_thresh 1']),
        ({'POINT2GRID_VLD_THRESH': '0.5'}, ['-vld_thresh 0.5']),
        ({'POINT2GRID_QC_FLAGS': '0,1'}, ['-qc 0,1']),
        ({'POINT2GRID_ADP': '{valid?fmt=%Y%m}.nc'}, ['-adp 201706.nc']),
        ({'POINT2GRID_REGRID_TO_GRID': 'G212'}, []),
        ({'POINT2GRID_INPUT_LEVEL': '(*,*)'}, []),
    ]
)
@pytest.mark.wrapper
def test_point2grid_run(metplus_config, config_overrides, optional_args):
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

    extra_args = " ".join(optional_args) + " " if optional_args else ""
    expected_cmds = []
    for idx in range(0, 3):
        expected_cmds.append(
            f'{app_path} {input_files[idx]} "{grids[idx]}" {output_files[idx]}'
            f' -field \'name="{input_name}"; level="{level}";\''
            f' {extra_args}{verbosity}'
        )

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd
