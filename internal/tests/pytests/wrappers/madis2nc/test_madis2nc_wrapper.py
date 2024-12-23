#!/usr/bin/env python3

import pytest

import os
import shutil

from metplus.wrappers.madis2nc_wrapper import MADIS2NCWrapper


def madis2nc_wrapper(metplus_config, config_overrides=None):
    config = metplus_config
    overrides = {
        'DO_NOT_RUN_EXE': True,
        'INPUT_MUST_EXIST': False,
        'PROCESS_LIST': 'MADIS2NC',
        'LOOP_BY': 'VALID',
        'VALID_TIME_FMT': '%Y%m%d%H',
        'VALID_BEG': '2019040912',
        'VALID_END': '2019040918',
        'VALID_INCREMENT': '6H',
        'MADIS2NC_INPUT_TEMPLATE': '{INPUT_BASE}/met_test/data/sample_obs/madis/metar_{valid?fmt=%Y%m%d%H}_F000.nc',
        'MADIS2NC_OUTPUT_TEMPLATE': '{OUTPUT_BASE}/madis2nc/metar_{valid?fmt=%Y%m%d%H}.nc',
        'MADIS2NC_CONFIG_FILE': '{PARM_BASE}/met_config/Madis2NcConfig_wrapped',
        'MADIS2NC_TYPE': 'metar',
    }
    if config_overrides:
        for key, value in config_overrides.items():
            overrides[key] = value

    instance = 'overrides'
    if not config.has_section(instance):
        config.add_section(instance)
    for key, value in overrides.items():
        config.set(instance, key, value)

    return MADIS2NCWrapper(config, instance=instance)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (1, 3, 0.5, 0, True),
        (1, 3, 0.8, 1, True),
        (1, 3, 0.5, 1, False),
    ]
)
@pytest.mark.wrapper
def test_madis2nc_missing_inputs(metplus_config, get_test_data_dir,
                                 missing, run, thresh, errors, allow_missing):
    config_overrides = {
        'INPUT_MUST_EXIST': True,
        'MADIS2NC_ALLOW_MISSING_INPUTS': allow_missing,
        'MADIS2NC_INPUT_THRESH': thresh,
        'MADIS2NC_INPUT_TEMPLATE': os.path.join(get_test_data_dir('madis'), 'metar_{valid?fmt=%Y%m%d%H}_F000.nc'),
        'VALID_END': '2019041000',
    }
    wrapper = madis2nc_wrapper(metplus_config, config_overrides)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),

        ({'MADIS2NC_TIME_SUMMARY_FLAG': 'True'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {flag = TRUE;}'}),

        ({'MADIS2NC_TIME_SUMMARY_RAW_DATA': 'true'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {raw_data = TRUE;}'}),

        ({'MADIS2NC_TIME_SUMMARY_BEG': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {beg = "123456";}'}),

        ({'MADIS2NC_TIME_SUMMARY_END': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {end = "123456";}'}),

        ({'MADIS2NC_TIME_SUMMARY_STEP': '500'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {step = 500;}'}),

        ({'MADIS2NC_TIME_SUMMARY_WIDTH': '900'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {width = 900;}'}),
        # width as dictionary
        ({'MADIS2NC_TIME_SUMMARY_WIDTH': '{ beg = -21600; end = 0; }'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {width = { beg = -21600; end = 0; };}'}),

        ({'MADIS2NC_TIME_SUMMARY_GRIB_CODE': '12, 203, 212'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {grib_code = [12, 203, 212];}'}),

        ({'MADIS2NC_TIME_SUMMARY_OBS_VAR': 'TMP, HGT, PRES'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {obs_var = ["TMP", "HGT", "PRES"];}'}),

        ({'MADIS2NC_TIME_SUMMARY_TYPE': 'min, range, max'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {type = ["min", "range", "max"];}'}),

        ({'MADIS2NC_TIME_SUMMARY_VLD_FREQ': '2'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {vld_freq = 2;}'}),

        ({'MADIS2NC_TIME_SUMMARY_VLD_THRESH': '0.5'},
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {vld_thresh = 0.5;}'}),

        ({'MADIS2NC_TIME_SUMMARY_FLAG': 'false',
          'MADIS2NC_TIME_SUMMARY_RAW_DATA': 'false',
          'MADIS2NC_TIME_SUMMARY_BEG': '123456',
          'MADIS2NC_TIME_SUMMARY_END': '125634',
          'MADIS2NC_TIME_SUMMARY_STEP': '500',
          'MADIS2NC_TIME_SUMMARY_WIDTH': '900',
          'MADIS2NC_TIME_SUMMARY_GRIB_CODE': '12, 203, 212',
          'MADIS2NC_TIME_SUMMARY_OBS_VAR': 'TMP, HGT, PRES',
          'MADIS2NC_TIME_SUMMARY_TYPE': 'min, range, max',
          'MADIS2NC_TIME_SUMMARY_VLD_FREQ': '2',
          'MADIS2NC_TIME_SUMMARY_VLD_THRESH': '0.5',
          },
         {'METPLUS_TIME_SUMMARY_DICT':
              ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "123456";'
               'end = "125634";step = 500;width = 900;'
               'grib_code = [12, 203, 212];obs_var = ["TMP", "HGT", "PRES"];'
               'type = ["min", "range", "max"];'
               'vld_freq = 2;vld_thresh = 0.5;}')}),
        ({'MADIS2NC_QC_DD': '4,5,6'}, {}),
        ({'MADIS2NC_LVL_DIM': 'P500,P750'}, {}),
        ({'MADIS2NC_REC_BEG': '2'}, {}),
        ({'MADIS2NC_REC_END': '3'}, {}),
        ({'MADIS2NC_MASK_GRID': 'mask_grid'}, {}),
        ({'MADIS2NC_MASK_POLY': '/some/path/to/mask/poly'}, {}),
        ({'MADIS2NC_MASK_SID': 'mask_sid,/some/path/to/mask/sid'}, {}),
        ({'MADIS2NC_QC_DD': '4,5,6',
          'MADIS2NC_LVL_DIM': 'P500,P750',
          'MADIS2NC_REC_BEG': '2',
          'MADIS2NC_REC_END': '3',
          'MADIS2NC_MASK_GRID': 'mask_grid',
          'MADIS2NC_MASK_POLY': '/some/path/to/mask/poly',
          'MADIS2NC_MASK_SID': 'mask_sid,/some/path/to/mask/sid'}, {}),

    ]
)
@pytest.mark.wrapper
def test_madis2nc_wrapper(metplus_config, config_overrides,
                          env_var_values, compare_command_and_env_vars):
    wrapper = madis2nc_wrapper(metplus_config, config_overrides)
    assert wrapper.isOK

    input_dir = os.path.dirname(wrapper.config.getraw('config', 'MADIS2NC_INPUT_TEMPLATE'))
    input_file1 = 'metar_2019040912_F000.nc'
    input_file2 = 'metar_2019040918_F000.nc'

    output_dir = os.path.dirname(wrapper.config.getraw('config', 'MADIS2NC_OUTPUT_TEMPLATE'))
    output_file1 = 'metar_2019040912.nc'
    output_file2 = 'metar_2019040918.nc'

    all_commands = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_commands}")

    app_path = os.path.join(wrapper.config.getdir('MET_BIN_DIR'),
                            wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')

    in_type = config_overrides['MADIS2NC_TYPE'] if 'MADIS2NC_TYPE' in config_overrides else 'metar'
    extra_args = ''
    for optional_arg in ('qc_dd', 'lvl_dim', 'rec_beg', 'rec_end', 'mask_grid', 'mask_poly', 'mask_sid'):
        if f'MADIS2NC_{optional_arg.upper()}' in config_overrides:
            extra_args += f" -{optional_arg} {config_overrides[f'MADIS2NC_{optional_arg.upper()}']}"

    expected_cmds = [
        (f"{app_path} {input_dir}/{input_file1} {output_dir}/{output_file1} "
         f"-type {in_type} -config {config_file}{extra_args} {verbosity}"),
        (f"{app_path} {input_dir}/{input_file2} {output_dir}/{output_file2} "
         f"-type {in_type} -config {config_file}{extra_args} {verbosity}"),
    ]

    compare_command_and_env_vars(all_commands, expected_cmds, env_var_values, wrapper)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'
    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'Madis2NcConfig_wrapped')

    wrapper = MADIS2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'MADIS2NC_CONFIG_FILE', fake_config_name)
    wrapper = MADIS2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
