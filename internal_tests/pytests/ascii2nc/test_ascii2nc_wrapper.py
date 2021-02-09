#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.ascii2nc_wrapper import ASCII2NCWrapper
from metplus.util import met_util as util
from metplus.util import time_util

def ascii2nc_wrapper(metplus_config, config_path=None, config_overrides=None):
    config = metplus_config()

    if config_path:
        parm_base = config.getdir('PARM_BASE')
        config_full_path = os.path.join(parm_base, config_path)
        config = metplus_config([config_full_path])

    overrides = {'DO_NOT_RUN_EXE': True,
                 'INPUT_MUST_EXIST': False}
    if config_overrides:
        for key, value in config_overrides.items():
            overrides[key] = value

    return ASCII2NCWrapper(config,
                           config_overrides=overrides)

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

    ]
)
def test_ascii2nc_wrapper(metplus_config, config_overrides,
                          env_var_values):
    wrapper = (
        ascii2nc_wrapper(metplus_config,
                         'use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC.conf',
                         config_overrides)
    )
    assert(wrapper.isOK)

    input_path = wrapper.config.getraw('config', 'ASCII2NC_INPUT_TEMPLATE')
    input_dir = os.path.dirname(input_path)
    input_file = 'precip24_2010010112.ascii'

    output_path = wrapper.config.getraw('config', 'ASCII2NC_OUTPUT_TEMPLATE')
    output_dir = os.path.dirname(output_path)
    output_file = 'precip24_2010010112.nc'

    all_commands = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_commands}")

    app_path = os.path.join(wrapper.config.getdir('MET_BIN_DIR'),
                            wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')

    expected_cmd = (f"{app_path} "
                  f"{input_dir}/{input_file} "
                  f"{output_dir}/{output_file} "
                  f"-config {config_file} "
                  f"{verbosity}")

    assert(all_commands[0][0] == expected_cmd)

    env_vars = all_commands[0][1]
    for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
        match = next((item for item in env_vars if
                      item.startswith(env_var_key)), None)
        assert (match is not None)
        value = match.split('=', 1)[1]

        assert (env_var_values.get(env_var_key, '') == value)
