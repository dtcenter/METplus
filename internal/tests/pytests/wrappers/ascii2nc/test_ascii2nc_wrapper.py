#!/usr/bin/env python3

import pytest

import os
import shutil

from metplus.wrappers.ascii2nc_wrapper import ASCII2NCWrapper


def ascii2nc_wrapper(metplus_config, config_overrides=None):
    config = metplus_config
    overrides = {
        'DO_NOT_RUN_EXE': True,
        'INPUT_MUST_EXIST': False,
        'PROCESS_LIST': 'ASCII2NC',
        'LOOP_BY': 'VALID',
        'VALID_TIME_FMT': '%Y%m%d%H',
        'VALID_BEG': '2010010112',
        'VALID_END': '2010010118',
        'VALID_INCREMENT': '6H',
        'ASCII2NC_INPUT_TEMPLATE': '{INPUT_BASE}/met_test/data/sample_obs/ascii/precip24_{valid?fmt=%Y%m%d%H}.ascii',
        'ASCII2NC_OUTPUT_TEMPLATE': '{OUTPUT_BASE}/ascii2nc/precip24_{valid?fmt=%Y%m%d%H}.nc',
        'ASCII2NC_CONFIG_FILE': '{PARM_BASE}/met_config/Ascii2NcConfig_wrapped',
        'ASCII2NC_TIME_SUMMARY_FLAG': 'False',
        'ASCII2NC_TIME_SUMMARY_RAW_DATA': 'False',
        'ASCII2NC_TIME_SUMMARY_BEG': '000000',
        'ASCII2NC_TIME_SUMMARY_END': '235959',
        'ASCII2NC_TIME_SUMMARY_STEP': '300',
        'ASCII2NC_TIME_SUMMARY_WIDTH': '600',
        'ASCII2NC_TIME_SUMMARY_GRIB_CODES': '11, 204, 211',
        'ASCII2NC_TIME_SUMMARY_VAR_NAMES': '',
        'ASCII2NC_TIME_SUMMARY_TYPES': 'min, max, range, mean, stdev, median, p80',
        'ASCII2NC_TIME_SUMMARY_VALID_FREQ': '0',
        'ASCII2NC_TIME_SUMMARY_VALID_THRESH': '0.0',
    }
    if config_overrides:
        for key, value in config_overrides.items():
            overrides[key] = value

    instance = 'overrides'
    if not config.has_section(instance):
        config.add_section(instance)
    for key, value in overrides.items():
        config.set(instance, key, value)

    return ASCII2NCWrapper(config, instance=instance)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (1, 3, 0.5, 0, True),
        (1, 3, 0.8, 1, True),
        (1, 3, 0.5, 1, False),
    ]
)
@pytest.mark.wrapper
def test_ascii2nc_missing_inputs(metplus_config, get_test_data_dir,
                                 missing, run, thresh, errors, allow_missing):
    config_overrides = {
        'INPUT_MUST_EXIST': True,
        'ASCII2NC_ALLOW_MISSING_INPUTS': allow_missing,
        'ASCII2NC_INPUT_THRESH': thresh,
        'ASCII2NC_INPUT_TEMPLATE': os.path.join(get_test_data_dir('ascii'), 'precip24_{valid?fmt=%Y%m%d%H}.ascii'),
        'VALID_END': '2010010200',
    }
    wrapper = ascii2nc_wrapper(metplus_config, config_overrides)
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
        ({},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_FLAG': 'True'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = TRUE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_RAW_DATA': 'true'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = TRUE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_BEG': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "123456";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_END': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "123456";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_STEP': '500'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 500;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_WIDTH': '900'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 900;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),
        # width as dictionary
        ({'ASCII2NC_TIME_SUMMARY_WIDTH': '{ beg = -21600; end = 0; }'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = { beg = -21600; end = 0; };'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_GRIB_CODES': '12, 203, 212'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [12, 203, 212];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_VAR_NAMES': 'TMP, HGT, PRES'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = ["TMP", "HGT", "PRES"];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_TYPES': 'min, range, max'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "range", "max"];'
           'vld_freq = 0;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_VALID_FREQ': '2'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 2;vld_thresh = 0.0;}')}),

        ({'ASCII2NC_TIME_SUMMARY_VALID_THRESH': '0.5'},
         {'METPLUS_TIME_SUMMARY_DICT':
          ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
           'end = "235959";step = 300;width = 600;'
           'grib_code = [11, 204, 211];obs_var = [];'
           'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
           'vld_freq = 0;vld_thresh = 0.5;}')}),

        ({'TIME_OFFSET_WARNING': '3'},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 3;',
          'METPLUS_TIME_SUMMARY_DICT':
              ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
               'end = "235959";step = 300;width = 600;'
               'grib_code = [11, 204, 211];obs_var = [];'
               'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
               'vld_freq = 0;vld_thresh = 0.0;}')
          }),

        ({'TIME_OFFSET_WARNING': '3', 'ASCII2NC_TIME_OFFSET_WARNING': '4'},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 4;',
          'METPLUS_TIME_SUMMARY_DICT':
              ('time_summary = {flag = FALSE;raw_data = FALSE;beg = "000000";'
               'end = "235959";step = 300;width = 600;'
               'grib_code = [11, 204, 211];obs_var = [];'
               'type = ["min", "max", "range", "mean", "stdev", "median", "p80"];'
               'vld_freq = 0;vld_thresh = 0.0;}')
          }),
    ]
)
@pytest.mark.wrapper
def test_ascii2nc_wrapper(metplus_config, config_overrides, env_var_values,
                          compare_command_and_env_vars):
    wrapper = ascii2nc_wrapper(metplus_config, config_overrides)
    assert wrapper.isOK

    input_path = wrapper.config.getraw('config', 'ASCII2NC_INPUT_TEMPLATE')
    input_dir = os.path.dirname(input_path)
    input_file1 = 'precip24_2010010112.ascii'
    input_file2 = 'precip24_2010010118.ascii'

    output_path = wrapper.config.getraw('config', 'ASCII2NC_OUTPUT_TEMPLATE')
    output_dir = os.path.dirname(output_path)
    output_file1 = 'precip24_2010010112.nc'
    output_file2 = 'precip24_2010010118.nc'

    all_commands = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_commands}")

    app_path = os.path.join(wrapper.config.getdir('MET_BIN_DIR'),
                            wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')

    expected_cmds = [
        (f"{app_path} {input_dir}/{input_file1} {output_dir}/{output_file1} "
         f"-config {config_file} {verbosity}"),
        (f"{app_path} {input_dir}/{input_file2} {output_dir}/{output_file2} "
         f"-config {config_file} {verbosity}"),
    ]

    compare_command_and_env_vars(all_commands, expected_cmds, env_var_values, wrapper)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'
    config = metplus_config
    config.set('config', 'INPUT_MUST_EXIST', False)

    wrapper = ASCII2NCWrapper(config)
    assert not wrapper.c_dict['CONFIG_FILE']

    config.set('config', 'ASCII2NC_CONFIG_FILE', fake_config_name)
    wrapper = ASCII2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
