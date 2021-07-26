#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
from datetime import datetime

import produtil

from metplus.wrappers.ensemble_stat_wrapper import EnsembleStatWrapper
from metplus.util import met_util as util
from metplus.util import time_util

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'
fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level_no_quotes = '(*,*)'
obs_level = f'"{obs_level_no_quotes}"'
ens_name = 'REFC'
ens_level = 'L0'
fcst_fmt = f'field = [{{ name="{fcst_name}"; level="{fcst_level}"; }}];'
obs_fmt = (f'field = [{{ name="{obs_name}"; '
           f'level="{obs_level_no_quotes}"; }}];')
ens_fmt = f'field = [{{ name="{ens_name}"; level="{ens_level}"; }}];'

time_fmt = '%Y%m%d%H'
run_times = ['2005080700', '2005080712']

def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'EnsembleStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'ENSEMBLE_STAT_N_MEMBERS', 1)
    config.set('config', 'ENSEMBLE_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/EnsembleStatConfig_wrapped')
    config.set('config', 'FCST_ENSEMBLE_STAT_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_ENSEMBLE_STAT_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_ENSEMBLE_STAT_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'ENSEMBLE_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/EnsembleStat/output')
    config.set('config', 'ENSEMBLE_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)
    config.set('config', 'ENS_VAR1_NAME', ens_name)
    config.set('config', 'ENS_VAR1_LEVELS', ens_level)

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0 no climo settings
        ({}, {}),
        # 1 mean template only
        ({'ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE': 'gs_mean_{init?fmt=%Y%m%d%H}.tmpl'},
         {'CLIMO_MEAN_FILE': '"gs_mean_YMDH.tmpl"',
          'CLIMO_STDEV_FILE': '', }),
        # 2 mean template and dir
        ({'ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE': 'gs_mean_{init?fmt=%Y%m%d%H}.tmpl',
          'ENSEMBLE_STAT_CLIMO_MEAN_INPUT_DIR': '/climo/mean/dir'},
         {'CLIMO_MEAN_FILE': '"/climo/mean/dir/gs_mean_YMDH.tmpl"',
          'CLIMO_STDEV_FILE': '', }),
        # 3 stdev template only
        ({'ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE': 'gs_stdev_{init?fmt=%Y%m%d%H}.tmpl'},
         {'CLIMO_STDEV_FILE': '"gs_stdev_YMDH.tmpl"', }),
        # 4 stdev template and dir
        ({'ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE': 'gs_stdev_{init?fmt=%Y%m%d%H}.tmpl',
          'ENSEMBLE_STAT_CLIMO_STDEV_INPUT_DIR': '/climo/stdev/dir'},
         {'CLIMO_STDEV_FILE': '"/climo/stdev/dir/gs_stdev_YMDH.tmpl"', }),
    ]
)
def test_handle_climo_file_variables(metplus_config, config_overrides,
                                     env_var_values):
    """! Ensure that old and new variables for setting climo_mean and
     climo_stdev are set to the correct values
    """
    old_env_vars = ['CLIMO_MEAN_FILE',
                    'CLIMO_STDEV_FILE']
    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert(wrapper.isOK)

    all_cmds = wrapper.run_all_times()
    for (_, actual_env_vars), run_time in zip(all_cmds, run_times):
        run_dt = datetime.strptime(run_time, time_fmt)
        ymdh = run_dt.strftime('%Y%m%d%H')
        print(f"ACTUAL ENV VARS: {actual_env_vars}")
        for old_env in old_env_vars:
            match = next((item for item in actual_env_vars if
                          item.startswith(old_env)), None)
            assert(match is not None)
            actual_value = match.split('=', 1)[1]
            expected_value = env_var_values.get(old_env, '')
            expected_value = expected_value.replace('YMDH', ymdh)
            assert(expected_value == actual_value)

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'ENSEMBLE_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'ENSEMBLE_STAT_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'ENSEMBLE_STAT_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'ENSEMBLE_STAT_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'ENSEMBLE_STAT_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'ENSEMBLE_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'ENSEMBLE_STAT_REGRID_TO_GRID': 'FCST',
          'ENSEMBLE_STAT_REGRID_METHOD': 'NEAREST',
          'ENSEMBLE_STAT_REGRID_WIDTH': '1',
          'ENSEMBLE_STAT_REGRID_VLD_THRESH': '0.5',
          'ENSEMBLE_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;}'
                                  )}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE':
              '/some/path/climo/filename.nc',
          },
         {'METPLUS_CLIMO_MEAN_DICT':
              'climo_mean = {file_name = ["/some/path/climo/filename.nc"];}',
          'CLIMO_MEAN_FILE':
              '"/some/path/climo/filename.nc"',
          }),
        ({'ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE':
              '/some/path/climo/stdfile.nc',
          },
         {'METPLUS_CLIMO_STDEV_DICT':
              'climo_stdev = {file_name = ["/some/path/climo/stdfile.nc"];}',
          'CLIMO_STDEV_FILE':
              '"/some/path/climo/stdfile.nc"',
         }),
        # 12 mask grid and poly (old config var)
        ({'ENSEMBLE_STAT_MASK_GRID': 'FULL',
          'ENSEMBLE_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),
        # 13 mask grid and poly (new config var)
        ({'ENSEMBLE_STAT_MASK_GRID': 'FULL',
          'ENSEMBLE_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),
        # 14 mask grid value
        ({'ENSEMBLE_STAT_MASK_GRID': 'FULL',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          }),
        # 15 mask grid empty string (should create empty list)
        ({'ENSEMBLE_STAT_MASK_GRID': '',
          },
         {'METPLUS_MASK_GRID':
              'grid = [];',
          }),
        # 16 mask poly (old config var)
        ({'ENSEMBLE_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),
        # 27 mask poly (new config var)
        ({'ENSEMBLE_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),
        # output_prefix
        ({'ENSEMBLE_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),
        # output_flag individual and all at once
        ({'ENSEMBLE_STAT_OUTPUT_FLAG_ECNT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ecnt = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_RPS': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {rps = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_RHIST': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {rhist = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_PHIST': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {phist = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_ORANK': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {orank = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ssvar = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_RELP': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {relp = STAT;}'}),

        ({
             'ENSEMBLE_STAT_OUTPUT_FLAG_ECNT': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RPS': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RHIST': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PHIST': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_ORANK': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RELP': 'STAT',
         },
         {
             'METPLUS_OUTPUT_FLAG_DICT': ('output_flag = {ecnt = STAT;'
                                           'rps = STAT;rhist = STAT;'
                                           'phist = STAT;orank = STAT;'
                                           'ssvar = STAT;relp = STAT;}')}),
        # ensemble_flag
        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {latlon = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {mean = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {stdev = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {minus = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {plus = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {min = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {max = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {range = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT': 'FALSE', },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {vld_count = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY': 'FALSE', },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {frequency = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {nep = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {nmep = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_RANK': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {rank = FALSE;}'}),

        ({'ENSEMBLE_STAT_ENSEMBLE_FLAG_WEIGHT': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {weight = FALSE;}'}),

        ({
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_RANK': 'FALSE',
             'ENSEMBLE_STAT_ENSEMBLE_FLAG_WEIGHT': 'FALSE',
         },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': ('ensemble_flag = {latlon = FALSE;'
                                            'mean = FALSE;stdev = FALSE;'
                                            'minus = FALSE;plus = FALSE;'
                                            'min = FALSE;max = FALSE;'
                                            'range = FALSE;vld_count = FALSE;'
                                            'frequency = FALSE;nep = FALSE;'
                                            'nmep = FALSE;rank = FALSE;'
                                            'weight = FALSE;}')}),
        # climo_cdf dictionary
        ({'ENSEMBLE_STAT_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {write_bins = FALSE;}'}),

        ({
             'ENSEMBLE_STAT_CLIMO_CDF_CDF_BINS': '1',
             'ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS': 'True',
             'ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS': 'False',
         },
         {
             'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;write_bins = FALSE;}'}),

        ({'ENSEMBLE_STAT_INTERP_VLD_THRESH': '0.8', },
         {'METPLUS_INTERP_DICT': 'interp = {vld_thresh = 0.8;}'}),

        ({'ENSEMBLE_STAT_INTERP_SHAPE': 'CIRCLE', },
         {'METPLUS_INTERP_DICT': 'interp = {shape = CIRCLE;}'}),

        ({'ENSEMBLE_STAT_INTERP_TYPE_METHOD': 'BILIN', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {method = BILIN;}}'}),

        ({'ENSEMBLE_STAT_INTERP_TYPE_WIDTH': '2', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {width = 2;}}'}),

        ({
             'ENSEMBLE_STAT_INTERP_VLD_THRESH': '0.8',
             'ENSEMBLE_STAT_INTERP_SHAPE': 'CIRCLE',
             'ENSEMBLE_STAT_INTERP_TYPE_METHOD': 'BILIN',
             'ENSEMBLE_STAT_INTERP_TYPE_WIDTH': '2',
         },
         {'METPLUS_INTERP_DICT': ('interp = {vld_thresh = 0.8;'
                                  'shape = CIRCLE;'
                                  'type = {method = BILIN;width = 2;}}')}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),

        ({'ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),

        ({
             'ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'ENSEMBLE_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH': '1',
             'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH': 'True',
             'ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL': '30',
             'ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

        # climo stdev
        ({'ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),

        ({'ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),

        ({
             'ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'ENSEMBLE_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH': '1',
             'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH': 'True',
             'ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL': '30',
             'ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),
    ]
)
def test_ensemble_stat_single_field(metplus_config, config_overrides,
                                    env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    file_list_dir = os.path.join(wrapper.config.getdir('STAGING_DIR'),
                                 'file_lists')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807000000_12_ensemble.txt "
                      f"{config_file} -outdir {out_dir}/2005080712"),
                     (f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807120000_12_ensemble.txt "
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
            actual_value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert(actual_value == fcst_fmt)
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert (actual_value == obs_fmt)
            elif env_var_key == 'METPLUS_ENS_FIELD':
                assert (actual_value == ens_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == actual_value)
