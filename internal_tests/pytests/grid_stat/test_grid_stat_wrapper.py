#!/usr/bin/env python3

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
from datetime import datetime

import produtil

from metplus.wrappers.grid_stat_wrapper import GridStatWrapper
from metplus.util import met_util as util
from metplus.util import time_util

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
time_fmt = '%Y%m%d%H'
run_times = ['2005080700', '2005080712']

def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'GridStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
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

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0 no climo settings
        ({}, {}),
        # 1 mean template only
        ({'GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE': 'gs_mean_{init?fmt=%Y%m%d%H}.tmpl'},
         {'CLIMO_MEAN_FILE': '"gs_mean_YMDH.tmpl"',
          'CLIMO_STDEV_FILE': '', }),
        # 2 mean template and dir
        ({'GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE': 'gs_mean_{init?fmt=%Y%m%d%H}.tmpl',
          'GRID_STAT_CLIMO_MEAN_INPUT_DIR': '/climo/mean/dir'},
         {'CLIMO_MEAN_FILE': '"/climo/mean/dir/gs_mean_YMDH.tmpl"',
          'CLIMO_STDEV_FILE': '', }),
        # 3 stdev template only
        ({'GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE': 'gs_stdev_{init?fmt=%Y%m%d%H}.tmpl'},
         {'CLIMO_STDEV_FILE': '"gs_stdev_YMDH.tmpl"', }),
        # 4 stdev template and dir
        ({'GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE': 'gs_stdev_{init?fmt=%Y%m%d%H}.tmpl',
          'GRID_STAT_CLIMO_STDEV_INPUT_DIR': '/climo/stdev/dir'},
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

    wrapper = GridStatWrapper(config)
    assert wrapper.isOK

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

        ({'GRID_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'GRID_STAT_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}',
          'REGRID_TO_GRID': 'FCST'}),

        ({'GRID_STAT_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'GRID_STAT_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'GRID_STAT_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'GRID_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'GRID_STAT_REGRID_TO_GRID': 'FCST',
          'GRID_STAT_REGRID_METHOD': 'NEAREST',
          'GRID_STAT_REGRID_WIDTH': '1',
          'GRID_STAT_REGRID_VLD_THRESH': '0.5',
          'GRID_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;}'
                                  ),
          'REGRID_TO_GRID': 'FCST'}),

        ({'GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE':
              '/some/path/climo/filename.nc',
          },
         {'METPLUS_CLIMO_MEAN_DICT':
              'climo_mean = {file_name = ["/some/path/climo/filename.nc"];}',
          'CLIMO_MEAN_FILE':
              '"/some/path/climo/filename.nc"',
          }),
        ({'GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE':
              '/some/path/climo/stdfile.nc',
          },
         {'METPLUS_CLIMO_STDEV_DICT':
              'climo_stdev = {file_name = ["/some/path/climo/stdfile.nc"];}',
          'CLIMO_STDEV_FILE':
              '"/some/path/climo/stdfile.nc"',
         }),
        # mask grid and poly (old config var)
        ({'GRID_STAT_MASK_GRID': 'FULL',
          'GRID_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_DICT':
              'mask = {grid = ["FULL"];poly = ["one", "two"];}',
          }),
        # mask grid and poly (new config var)
        ({'GRID_STAT_MASK_GRID': 'FULL',
          'GRID_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_DICT':
              'mask = {grid = ["FULL"];poly = ["one", "two"];}',
          }),
        # mask grid value
        ({'GRID_STAT_MASK_GRID': 'FULL',
          },
         {'METPLUS_MASK_DICT':
              'mask = {grid = ["FULL"];}',
          }),
        # mask grid empty string (should create empty list)
        ({'GRID_STAT_MASK_GRID': '',
          },
         {'METPLUS_MASK_DICT':
              'mask = {grid = [];}',
          }),
        # mask poly (old config var)
        ({'GRID_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_DICT':
              'mask = {poly = ["one", "two"];}',
          }),
        # mask poly (new config var)
        ({'GRID_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_DICT':
              'mask = {poly = ["one", "two"];}',
          }),

        ({'GRID_STAT_NEIGHBORHOOD_COV_THRESH': '>=0.5'},
         {'METPLUS_NBRHD_COV_THRESH': 'cov_thresh = [>=0.5];'}),

        ({'GRID_STAT_NEIGHBORHOOD_WIDTH': '1,2'},
         {'METPLUS_NBRHD_WIDTH': 'width = [1, 2];'}),

        ({'GRID_STAT_NEIGHBORHOOD_SHAPE': 'CIRCLE'},
         {'METPLUS_NBRHD_SHAPE': 'shape = CIRCLE;'}),

        ({'GRID_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'GRID_STAT_OUTPUT_FLAG_FHO': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {fho = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_CTC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ctc = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_CTS': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cts = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_MCTC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mctc = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_MCTS': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mcts = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_CNT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cnt = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_SL1L2': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sl1l2 = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_SAL1L2': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sal1l2 = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_VL1L2': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vl1l2 = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_VAL1L2': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {val1l2 = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_VCNT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vcnt = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_PCT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pct = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_PSTD': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pstd = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_PJC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pjc = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_PRC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {prc = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_ECLV': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {eclv = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_NBRCTC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {nbrctc = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_NBRCTS': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {nbrcts = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_NBRCNT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {nbrcnt = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_GRAD': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {grad = STAT;}'}),

        ({'GRID_STAT_OUTPUT_FLAG_DMAP': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {dmap = STAT;}'}),

        ({
             'GRID_STAT_OUTPUT_FLAG_FHO': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_CTC': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_CTS': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_MCTC': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_MCTS': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_CNT': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_SL1L2': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_SAL1L2': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_VL1L2': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_VAL1L2': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_VCNT': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_PCT': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_PSTD': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_PJC': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_PRC': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_ECLV': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_NBRCTC': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_NBRCTS': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_NBRCNT': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_GRAD': 'STAT',
             'GRID_STAT_OUTPUT_FLAG_DMAP': 'STAT',
         },
         {
             'METPLUS_OUTPUT_FLAG_DICT': (
                     'output_flag = {fho = STAT;ctc = STAT;cts = STAT;'
                     'mctc = STAT;mcts = STAT;cnt = STAT;sl1l2 = STAT;'
                     'sal1l2 = STAT;vl1l2 = STAT;val1l2 = STAT;'
                     'vcnt = STAT;pct = STAT;pstd = STAT;pjc = STAT;'
                     'prc = STAT;eclv = STAT;nbrctc = STAT;nbrcts = STAT;'
                     'nbrcnt = STAT;grad = STAT;dmap = STAT;}')}),

        ({'GRID_STAT_NC_PAIRS_FLAG_LATLON': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {latlon = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_RAW': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {raw = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_DIFF': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {diff = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_CLIMO': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {climo = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_CLIMO_CDP': 'TRUE', },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {climo_cdp = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_WEIGHT': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {weight = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_NBRHD': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {nbrhd = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_FOURIER': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {fourier = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_GRADIENT': 'TRUE', },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {gradient = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_DISTANCE_MAP': 'TRUE', },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {distance_map = TRUE;}'}),

        ({'GRID_STAT_NC_PAIRS_FLAG_APPLY_MASK': 'TRUE', },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {apply_mask = TRUE;}'}),

        ({
             'GRID_STAT_NC_PAIRS_FLAG_LATLON': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_RAW': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_DIFF': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_CLIMO': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_CLIMO_CDP': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_WEIGHT': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_NBRHD': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_FOURIER': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_GRADIENT': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_DISTANCE_MAP': 'TRUE',
             'GRID_STAT_NC_PAIRS_FLAG_APPLY_MASK': 'TRUE',
         },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {latlon = TRUE;raw = TRUE;diff = TRUE;climo = TRUE;climo_cdp = TRUE;weight = TRUE;nbrhd = TRUE;fourier = TRUE;gradient = TRUE;distance_map = TRUE;apply_mask = TRUE;}'}),

        ({'GRID_STAT_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'GRID_STAT_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'GRID_STAT_CLIMO_CDF_WRITE_BINS': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {write_bins = FALSE;}'}),

        ({
             'GRID_STAT_CLIMO_CDF_CDF_BINS': '1',
             'GRID_STAT_CLIMO_CDF_CENTER_BINS': 'True',
             'GRID_STAT_CLIMO_CDF_WRITE_BINS': 'False',
         },
         {
             'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;write_bins = FALSE;}'}),

        ({'GRID_STAT_INTERP_FIELD': 'NONE', },
         {'METPLUS_INTERP_DICT': 'interp = {field = NONE;}'}),

        ({'GRID_STAT_INTERP_VLD_THRESH': '0.8', },
         {'METPLUS_INTERP_DICT': 'interp = {vld_thresh = 0.8;}'}),

        ({'GRID_STAT_INTERP_SHAPE': 'CIRCLE', },
         {'METPLUS_INTERP_DICT': 'interp = {shape = CIRCLE;}'}),

        ({'GRID_STAT_INTERP_TYPE_METHOD': 'BILIN', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {method = BILIN;}}'}),

        ({'GRID_STAT_INTERP_TYPE_WIDTH': '2', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {width = 2;}}'}),

        ({
             'GRID_STAT_INTERP_FIELD': 'NONE',
             'GRID_STAT_INTERP_VLD_THRESH': '0.8',
             'GRID_STAT_INTERP_SHAPE': 'CIRCLE',
             'GRID_STAT_INTERP_TYPE_METHOD': 'BILIN',
             'GRID_STAT_INTERP_TYPE_WIDTH': '2',
         },
         {'METPLUS_INTERP_DICT': ('interp = {vld_thresh = 0.8;'
                                  'shape = CIRCLE;'
                                  'type = {method = BILIN;width = 2;}'
                                  'field = NONE;}')}),

        ({'GRID_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

        ({'GRID_STAT_CLIMO_MEAN_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),

        ({'GRID_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # ignore USE_FCST because FIELD is set
        ({'GRID_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'GRID_STAT_CLIMO_MEAN_USE_FCST': 'TRUE'},
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # ignore USE_OBS because FIELD is set
        ({'GRID_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'GRID_STAT_CLIMO_MEAN_USE_OBS': 'TRUE'},
        {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # use fcst no other climo_mean
        ({'GRID_STAT_CLIMO_MEAN_USE_FCST': 'TRUE'},
        {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = fcst;'}),
        # use obs no other climo_mean
        ({'GRID_STAT_CLIMO_MEAN_USE_OBS': 'TRUE'},
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = obs;'}),
        # use fcst with other climo_mean
        ({'GRID_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'GRID_STAT_CLIMO_MEAN_USE_FCST': 'TRUE'},
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}climo_mean = fcst;'}),
        # use obs with other climo_mean
        ({'GRID_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'GRID_STAT_CLIMO_MEAN_USE_OBS': 'TRUE'},
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}climo_mean = obs;'}),

        ({'GRID_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),

        ({'GRID_STAT_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),

        ({'GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),

        ({'GRID_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),

        ({'GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),

        ({'GRID_STAT_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),

        ({'GRID_STAT_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),

        ({'GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),

        ({
             'GRID_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'GRID_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'GRID_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'GRID_STAT_CLIMO_MEAN_REGRID_WIDTH': '1',
             'GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'GRID_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'GRID_STAT_CLIMO_MEAN_MATCH_MONTH': 'True',
             'GRID_STAT_CLIMO_MEAN_DAY_INTERVAL': '30',
             'GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12',
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
        ({'GRID_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),

        ({'GRID_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'GRID_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),

        ({'GRID_STAT_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),

        ({'GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),

        ({'GRID_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),

        ({'GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),

        ({'GRID_STAT_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),

        ({'GRID_STAT_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),

        ({'GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),

        ({
             'GRID_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'GRID_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'GRID_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'GRID_STAT_CLIMO_STDEV_REGRID_WIDTH': '1',
             'GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'GRID_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'GRID_STAT_CLIMO_STDEV_MATCH_MONTH': 'True',
             'GRID_STAT_CLIMO_STDEV_DAY_INTERVAL': '30',
             'GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12',
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
        # ignore USE_FCST because FIELD is set
        (
        {'GRID_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
         'GRID_STAT_CLIMO_STDEV_USE_FCST': 'TRUE'},
        {
            'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # ignore USE_OBS because FIELD is set
        (
        {'GRID_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
         'GRID_STAT_CLIMO_STDEV_USE_OBS': 'TRUE'},
        {
            'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # use fcst no other climo_stdev
        ({'GRID_STAT_CLIMO_STDEV_USE_FCST': 'TRUE'},
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = fcst;'}),
        # use obs no other climo_stdev
        ({'GRID_STAT_CLIMO_STDEV_USE_OBS': 'TRUE'},
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = obs;'}),
        # use fcst with other climo_stdev
        ({'GRID_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'GRID_STAT_CLIMO_STDEV_USE_FCST': 'TRUE'},
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}climo_stdev = fcst;'}),
        # use obs with other climo_stdev
        ({'GRID_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'GRID_STAT_CLIMO_STDEV_USE_OBS': 'TRUE'},
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}climo_stdev = obs;'}),

        ({'GRID_STAT_GRID_WEIGHT_FLAG': 'COS_LAT', },
         {'METPLUS_GRID_WEIGHT_FLAG': 'grid_weight_flag = COS_LAT;'}),

        ({'FCST_GRID_STAT_FILE_TYPE': 'NETCDF_NCCF', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_NCCF;'}),
        ({'OBS_GRID_STAT_FILE_TYPE': 'NETCDF_NCCF', },
         {'METPLUS_OBS_FILE_TYPE': 'file_type = NETCDF_NCCF;'}),
        ({'GRID_STAT_HSS_EC_VALUE': '0.5', },
         {'METPLUS_HSS_EC_VALUE': 'hss_ec_value = 0.5;'}),
        ({'GRID_STAT_DISTANCE_MAP_BADDELEY_P': '1', },
         {'METPLUS_DISTANCE_MAP_DICT': 'distance_map = {baddeley_p = 1;}'}),

        ({'GRID_STAT_DISTANCE_MAP_BADDELEY_MAX_DIST': '2.3', },
         {'METPLUS_DISTANCE_MAP_DICT': 'distance_map = {baddeley_max_dist = 2.3;}'}),

        ({'GRID_STAT_DISTANCE_MAP_FOM_ALPHA': '4.5', },
         {'METPLUS_DISTANCE_MAP_DICT': 'distance_map = {fom_alpha = 4.5;}'}),

        ({'GRID_STAT_DISTANCE_MAP_ZHU_WEIGHT': '0.5', },
         {'METPLUS_DISTANCE_MAP_DICT': 'distance_map = {zhu_weight = 0.5;}'}),

        ({'GRID_STAT_DISTANCE_MAP_BETA_VALUE_N': 'n * n / 3.0', },
         {'METPLUS_DISTANCE_MAP_DICT': 'distance_map = {beta_value(n) = n * n / 3.0;}'}),
        ({
             'GRID_STAT_DISTANCE_MAP_BADDELEY_P': '1',
             'GRID_STAT_DISTANCE_MAP_BADDELEY_MAX_DIST': '2.3',
             'GRID_STAT_DISTANCE_MAP_FOM_ALPHA': '4.5',
             'GRID_STAT_DISTANCE_MAP_ZHU_WEIGHT': '0.5',
             'GRID_STAT_DISTANCE_MAP_BETA_VALUE_N': 'n * n / 3.0',
         },
         {'METPLUS_DISTANCE_MAP_DICT': ('distance_map = {baddeley_p = 1;'
                                        'baddeley_max_dist = 2.3;'
                                        'fom_alpha = 4.5;zhu_weight = 0.5;'
                                        'beta_value(n) = n * n / 3.0;}')}),
        ({'GRID_STAT_FOURIER_WAVE_1D_BEG': '0,4,10', },
         {'METPLUS_FOURIER_DICT': 'fourier = {wave_1d_beg = [0, 4, 10];}'}),

        ({'GRID_STAT_FOURIER_WAVE_1D_END': '3,9,20', },
         {'METPLUS_FOURIER_DICT': 'fourier = {wave_1d_end = [3, 9, 20];}'}),

        ({'GRID_STAT_FOURIER_WAVE_1D_BEG': '0,4,10',
          'GRID_STAT_FOURIER_WAVE_1D_END': '3,9,20',},
         {'METPLUS_FOURIER_DICT': ('fourier = {wave_1d_beg = [0, 4, 10];'
                                   'wave_1d_end = [3, 9, 20];}')}),
        ({'GRID_STAT_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_CENSOR_THRESH': 'censor_thresh = [>12000, <5000];'}),

        ({'GRID_STAT_CENSOR_VAL': '12000, 5000', },
         {'METPLUS_CENSOR_VAL': 'censor_val = [12000, 5000];'}),

    ]
)
def test_grid_stat_single_field(metplus_config, config_overrides,
                                env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = GridStatWrapper(config)
    assert wrapper.isOK

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
        # including deprecated env vars (not in wrapper env var keys)
        env_var_keys = (wrapper.WRAPPER_ENV_VAR_KEYS +
                        [name for name in env_var_values
                         if name not in wrapper.WRAPPER_ENV_VAR_KEYS])
        for env_var_key in env_var_keys:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert(match is not None)
            actual_value = match.split('=', 1)[1]
            print(f"ENV VAR: {env_var_key}")
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert(actual_value == fcst_fmt)
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert (actual_value == obs_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == actual_value)

def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config()
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'GridStatConfig_wrapped')

    wrapper = GridStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'GRID_STAT_CONFIG_FILE', fake_config_name)
    wrapper = GridStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
