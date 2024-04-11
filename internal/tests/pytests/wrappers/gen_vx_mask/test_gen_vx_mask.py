#!/usr/bin/env python3

import pytest

import os
import datetime


from metplus.wrappers.gen_vx_mask_wrapper import GenVxMaskWrapper
from metplus.util import time_util


def gen_vx_mask_wrapper(metplus_config):
    """! Returns a default GenVxMaskWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return GenVxMaskWrapper(config)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (6, 12, 0.5, 0, True),
        (6, 12, 0.6, 1, True),
        (6, 12, 0.5, 6, False),
    ]
)
@pytest.mark.wrapper
def test_gen_vx_mask_missing_inputs(metplus_config, get_test_data_dir, missing,
                                    run, thresh, errors, allow_missing):
    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'GEN_VX_MASK_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'GEN_VX_MASK_INPUT_THRESH', thresh)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'GEN_VX_MASK_OPTIONS', "-type lat -thresh 'ge30&&le50', -type lon -thresh 'le-70&&ge-130' -intersection -name lat_lon_mask")
    config.set('config', 'GEN_VX_MASK_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'GEN_VX_MASK_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')

    config.set('config', 'GEN_VX_MASK_INPUT_MASK_DIR', get_test_data_dir('obs'))
    config.set('config', 'GEN_VX_MASK_INPUT_MASK_TEMPLATE',
               '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc,{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
    config.set('config', 'GEN_VX_MASK_OUTPUT_TEMPLATE', '{OUTPUT_BASE}/GenVxMask/test.nc')

    wrapper = GenVxMaskWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


@pytest.mark.wrapper
def test_run_gen_vx_mask_once(metplus_config):
    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    wrap = gen_vx_mask_wrapper(metplus_config)
    wrap.c_dict['INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT']
    wrap.c_dict['OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                             'GenVxMask_test')
    wrap.c_dict['OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH_LAT_MASK.nc'
    wrap.c_dict['COMMAND_OPTIONS'] = ["-type lat -thresh 'ge30&&le50'"]
#    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT', 'LON']
#    wrap.c_dict['COMMAND_OPTIONS'] = ["-type lat -thresh 'ge30&&le50'", "-type lon -thresh 'le-70&&ge-130' -intersection"]

    wrap.run_at_time_once(time_info)

    expected_cmd = f"{wrap.app_path} \"2018020100_ZENITH\" LAT {wrap.config.getdir('OUTPUT_BASE')}/GenVxMask_test/2018020100_ZENITH_LAT_MASK.nc -type lat -thresh 'ge30&&le50' -v 2"

    for cmd, _ in wrap.all_commands:
        print(f"COMMAND:{cmd}")
        print("EXPECTED:{expected_cmd}")
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_run_gen_vx_mask_twice(metplus_config):
    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    wrap = gen_vx_mask_wrapper(metplus_config)
    wrap.c_dict['INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT', 'LON']
    wrap.c_dict['OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                             'GenVxMask_test')
    wrap.c_dict['OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH_LAT_LON_MASK.nc'
    cmd_args = ["-type lat -thresh 'ge30&&le50'", "-type lon -thresh 'le-70&&ge-130' -intersection -name lat_lon_mask"]
    wrap.c_dict['COMMAND_OPTIONS'] = cmd_args

    wrap.run_at_time_once(time_info)

    expected_cmds = [f"{wrap.app_path} \"2018020100_ZENITH\" LAT {wrap.config.getdir('OUTPUT_BASE')}/stage/gen_vx_mask/temp_0.nc {cmd_args[0]} -v 2",
                     f"{wrap.app_path} \"{wrap.config.getdir('OUTPUT_BASE')}/stage/gen_vx_mask/temp_0.nc\" LON {wrap.config.getdir('OUTPUT_BASE')}/GenVxMask_test/2018020100_ZENITH_LAT_LON_MASK.nc {cmd_args[1]} -v 2"]

    test_passed = True

    if len(wrap.all_commands) != len(expected_cmds):
        print("Number of commands run is not the same as expected")
        assert False

    for (cmd, _), expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert test_passed

