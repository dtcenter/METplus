#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.point_stat_wrapper import PointStatWrapper

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PointStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080712')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')

    config.set('config', 'POINT_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/PointStatConfig_wrapped')
    config.set('config', 'FCST_POINT_STAT_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_POINT_STAT_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_POINT_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_POINT_STAT_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'POINT_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/GridStat/output')
    config.set('config', 'POINT_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')


@pytest.mark.wrapper_a
def test_met_dictionary_in_var_options(metplus_config):
    config = metplus_config
    set_minimum_config_settings(config)

    config.set('config', 'BOTH_VAR1_NAME', 'name')
    config.set('config', 'BOTH_VAR1_LEVELS', 'level')
    config.set('config', 'BOTH_VAR1_OPTIONS',
               'interp = { type = [ { method = NEAREST; width = 1; } ] };')

    wrapper = PointStatWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'POINT_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'POINT_STAT_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}',
          'REGRID_TO_GRID': 'FCST'}),

        ({'POINT_STAT_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'POINT_STAT_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'POINT_STAT_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'POINT_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'POINT_STAT_REGRID_TO_GRID': 'FCST',
          'POINT_STAT_REGRID_METHOD': 'NEAREST',
          'POINT_STAT_REGRID_WIDTH': '1',
          'POINT_STAT_REGRID_VLD_THRESH': '0.5',
          'POINT_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;}'
                                  ),
          'REGRID_TO_GRID': 'FCST'}),

        # mask grid and poly (old config var)
        ({'POINT_STAT_MASK_GRID': 'FULL',
          'POINT_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_GRID': 'grid = ["FULL"];',
          'METPLUS_MASK_POLY': 'poly = ["one", "two"];',
          }),
        # mask grid and poly (new config var)
        ({'POINT_STAT_MASK_GRID': 'FULL',
          'POINT_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_GRID': 'grid = ["FULL"];',
          'METPLUS_MASK_POLY': 'poly = ["one", "two"];',
          }),
        # mask grid value
        ({'POINT_STAT_MASK_GRID': 'FULL',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          }),
        # mask.poly complex example
        ({'POINT_STAT_MASK_POLY': ('["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly" ];'),
          },
         {'METPLUS_MASK_POLY':
              'poly = ["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly"];',
          }),
        # mask grid empty string (should create empty list)
        ({'POINT_STAT_MASK_GRID': '',
          },
         {'METPLUS_MASK_GRID':
              'grid = [];',
          }),
        # mask poly (old config var)
        ({'POINT_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one", "two"];',
          }),
        # mask poly (new config var)
        ({'POINT_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one", "two"];',
          }),

        ({'POINT_STAT_MASK_SID': 'one, two',
          },
         {'METPLUS_MASK_SID':
              'sid = ["one", "two"];',
          }),

        ({'POINT_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'POINT_STAT_MESSAGE_TYPE': 'ADPUPA, ADPSFC'},
         {'METPLUS_MESSAGE_TYPE': 'message_type = ["ADPUPA", "ADPSFC"];'}),

        ({'OBS_POINT_STAT_WINDOW_BEGIN': '-2700',
          'OBS_POINT_STAT_WINDOW_END': '2700',
          },
         {'METPLUS_OBS_WINDOW_DICT':
              'obs_window = {beg = -2700;end = 2700;}',
          'OBS_WINDOW_BEGIN': '-2700',
          'OBS_WINDOW_END': '2700'
          }),

        ({'POINT_STAT_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'POINT_STAT_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'POINT_STAT_CLIMO_CDF_WRITE_BINS': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {write_bins = FALSE;}'}),

        ({'POINT_STAT_CLIMO_CDF_DIRECT_PROB': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {direct_prob = FALSE;}'}),

        ({
             'POINT_STAT_CLIMO_CDF_CDF_BINS': '1',
             'POINT_STAT_CLIMO_CDF_CENTER_BINS': 'True',
             'POINT_STAT_CLIMO_CDF_WRITE_BINS': 'False',
             'POINT_STAT_CLIMO_CDF_DIRECT_PROB': 'False',
         },
         {
             'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;write_bins = FALSE;direct_prob = FALSE;}'}),

        ({'POINT_STAT_OBS_QUALITY_INC': '2,3,4', },
         {'METPLUS_OBS_QUALITY_INC': 'obs_quality_inc = ["2", "3", "4"];'}),
        ({'POINT_STAT_OBS_QUALITY_EXC': '5,6,7', },
         {'METPLUS_OBS_QUALITY_EXC': 'obs_quality_exc = ["5", "6", "7"];'}),
        ({'POINT_STAT_OBS_QUALITY': '1, 2, 3', },
         {'METPLUS_OBS_QUALITY_INC': 'obs_quality_inc = ["1", "2", "3"];'}),

        ({'POINT_STAT_OUTPUT_FLAG_FHO': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {fho = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_CTC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ctc = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_CTS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cts = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_MCTC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mctc = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_MCTS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mcts = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_CNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cnt = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_SL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sl1l2 = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_SAL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sal1l2 = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_VL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vl1l2 = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_VAL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {val1l2 = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_VCNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vcnt = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_PCT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pct = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_PSTD': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pstd = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_PJC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pjc = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_PRC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {prc = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_ECNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ecnt = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_RPS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {rps = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_ECLV': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {eclv = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_MPR': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mpr = BOTH;}'}),

        ({'POINT_STAT_OUTPUT_FLAG_ORANK': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {orank = BOTH;}'}),

        ({
             'POINT_STAT_OUTPUT_FLAG_FHO': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_CTC': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_CTS': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_MCTC': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_MCTS': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_CNT': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_SL1L2': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_SAL1L2': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_VL1L2': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_VAL1L2': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_VCNT': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_PCT': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_PSTD': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_PJC': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_PRC': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_ECNT': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_RPS': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_ECLV': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_MPR': 'BOTH',
             'POINT_STAT_OUTPUT_FLAG_ORANK': 'BOTH',
         },
         {
             'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {fho = BOTH;ctc = BOTH;cts = BOTH;mctc = BOTH;mcts = BOTH;cnt = BOTH;sl1l2 = BOTH;sal1l2 = BOTH;vl1l2 = BOTH;val1l2 = BOTH;vcnt = BOTH;pct = BOTH;pstd = BOTH;pjc = BOTH;prc = BOTH;ecnt = BOTH;rps = BOTH;eclv = BOTH;mpr = BOTH;orank = BOTH;}'}),

        ({'POINT_STAT_INTERP_VLD_THRESH': '0.5', },
         {'METPLUS_INTERP_DICT': 'interp = {vld_thresh = 0.5;}'}),

        ({'POINT_STAT_INTERP_SHAPE': 'SQUARE', },
         {'METPLUS_INTERP_DICT': 'interp = {shape = SQUARE;}'}),

        ({'POINT_STAT_INTERP_TYPE_METHOD': 'BILIN', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {method = BILIN;}}'}),

        ({'POINT_STAT_INTERP_TYPE_WIDTH': '2', },
         {'METPLUS_INTERP_DICT': 'interp = {type = {width = 2;}}'}),

        ({
             'POINT_STAT_INTERP_VLD_THRESH': '0.5',
             'POINT_STAT_INTERP_SHAPE': 'SQUARE',
             'POINT_STAT_INTERP_TYPE_METHOD': 'BILIN',
             'POINT_STAT_INTERP_TYPE_WIDTH': '2',
         },
         {
             'METPLUS_INTERP_DICT': ('interp = {'
                                     'vld_thresh = 0.5;shape = SQUARE;'
                                     'type = {method = BILIN;width = 2;}}')}),

        ({'POINT_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

        ({'POINT_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'POINT_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),

        ({'POINT_STAT_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),

        ({'POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),

        ({'POINT_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),

        ({'POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),

        ({'POINT_STAT_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),

        ({'POINT_STAT_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),

        ({'POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),

        ({
             'POINT_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'POINT_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'POINT_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'POINT_STAT_CLIMO_MEAN_REGRID_WIDTH': '1',
             'POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'POINT_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'POINT_STAT_CLIMO_MEAN_MATCH_MONTH': 'True',
             'POINT_STAT_CLIMO_MEAN_DAY_INTERVAL': '30',
             'POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12',
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
        ({'POINT_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                       '["/some/climo_stdev/file.txt"];}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),

        ({'POINT_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'POINT_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),

        ({'POINT_STAT_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),

        ({'POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),

        ({'POINT_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),

        ({'POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),

        ({'POINT_STAT_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),

        ({'POINT_STAT_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),

        ({'POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),

        ({
             'POINT_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'POINT_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'POINT_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'POINT_STAT_CLIMO_STDEV_REGRID_WIDTH': '1',
             'POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'POINT_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'POINT_STAT_CLIMO_STDEV_MATCH_MONTH': 'True',
             'POINT_STAT_CLIMO_STDEV_DAY_INTERVAL': '30',
             'POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12',
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
        ({'POINT_STAT_HSS_EC_VALUE': '0.5', },
         {'METPLUS_HSS_EC_VALUE': 'hss_ec_value = 0.5;'}),
        ({'POINT_STAT_MASK_LLPNT': ('{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; },'
                                    '{ name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }')},
         {'METPLUS_MASK_LLPNT': 'llpnt = [{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; }, { name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }];'}),

        ({'POINT_STAT_HIRA_FLAG': 'False', },
         {'METPLUS_HIRA_DICT': 'hira = {flag = FALSE;}'}),

        ({'POINT_STAT_HIRA_WIDTH': '2,3,4,5', },
         {'METPLUS_HIRA_DICT': 'hira = {width = [2, 3, 4, 5];}'}),

        ({'POINT_STAT_HIRA_VLD_THRESH': '1.0', },
         {'METPLUS_HIRA_DICT': 'hira = {vld_thresh = 1.0;}'}),

        ({'POINT_STAT_HIRA_COV_THRESH': '==0.25, ==0.5', },
         {'METPLUS_HIRA_DICT': 'hira = {cov_thresh = [==0.25, ==0.5];}'}),

        ({'POINT_STAT_HIRA_SHAPE': 'square', },
         {'METPLUS_HIRA_DICT': 'hira = {shape = SQUARE;}'}),

        ({'POINT_STAT_HIRA_PROB_CAT_THRESH': '>1,<=2', },
         {'METPLUS_HIRA_DICT': 'hira = {prob_cat_thresh = [>1, <=2];}'}),

        ({
             'POINT_STAT_HIRA_FLAG': 'False',
             'POINT_STAT_HIRA_WIDTH': '2,3,4,5',
             'POINT_STAT_HIRA_VLD_THRESH': '1.0',
             'POINT_STAT_HIRA_COV_THRESH': '==0.25, ==0.5',
             'POINT_STAT_HIRA_SHAPE': 'square',
             'POINT_STAT_HIRA_PROB_CAT_THRESH': '>1,<=2',
         },
         {
             'METPLUS_HIRA_DICT': ('hira = {flag = FALSE;width = [2, 3, 4, 5];'
                                   'vld_thresh = 1.0;'
                                   'cov_thresh = [==0.25, ==0.5];'
                                   'shape = SQUARE;'
                                   'prob_cat_thresh = [>1, <=2];}')}),
        ({'POINT_STAT_MESSAGE_TYPE_GROUP_MAP': '{ key = "SURFACE"; val = "ADPSFC,SFCSHP,MSONET";},{ key = "ANYAIR";  val = "AIRCAR,AIRCFT";}', },
         {'METPLUS_MESSAGE_TYPE_GROUP_MAP': 'message_type_group_map = [{ key = "SURFACE"; val = "ADPSFC,SFCSHP,MSONET";}, { key = "ANYAIR";  val = "AIRCAR,AIRCFT";}];'}),
        ({'POINT_STAT_FCST_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'POINT_STAT_FCST_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'POINT_STAT_SEEPS_P1_THRESH': 'ge0.1&&le0.85', },
         {'METPLUS_SEEPS_P1_THRESH': 'seeps_p1_thresh = ge0.1&&le0.85;'}),
    ]
)
@pytest.mark.wrapper_a
def test_point_stat_all_fields(metplus_config, config_overrides,
                               env_var_values):
    level_no_quotes = '(*,*)'
    level_with_quotes = f'"{level_no_quotes}"'

    fcsts = [{'name': 'TMP',
              'level': 'P750-900',
              'thresh': '<=273,>273'},
              {'name': 'UGRD',
               'level': 'Z10',
               'thresh': '>=5'},
              # {'name': 'VGRD',
              #  'level': 'Z10',
              #  'thresh': '>=5'},
             ]
    obss = [{'name': 'TMP',
            'level': level_no_quotes,
            'thresh': '<=273,>273'},
            {'name': 'UGRD',
             'level': 'Z10',
             'thresh': '>=5'},
            # {'name': 'VGRD',
            #  'level': 'Z10',
            #  'thresh': '>=5'},
           ]

    fcst_fmts = []
    obs_fmts = []
    for fcst, obs in zip(fcsts, obss):
        fcst_name = fcst['name']
        fcst_level = fcst['level']
        fcst_thresh = fcst['thresh']
        obs_name = obs['name']
        obs_level = obs['level']
        obs_thresh = obs['thresh']

        fcst_fmt = (f'{{ name="{fcst_name}"; level="{fcst_level}"; '
                    f'cat_thresh=[ {fcst_thresh} ]; }}')
        obs_fmt = (f'{{ name="{obs_name}"; level="{obs_level}"; '
                    f'cat_thresh=[ {obs_thresh} ]; }}')
        fcst_fmts.append(fcst_fmt)
        obs_fmts.append(obs_fmt)

    config = metplus_config
    set_minimum_config_settings(config)

    for index, (fcst, obs) in enumerate(zip(fcsts, obss)):
        idx = index + 1
        if obs['level'] == level_no_quotes:
            obs['level'] = level_with_quotes
        config.set('config', f'FCST_VAR{idx}_NAME', fcst['name'])
        config.set('config', f'FCST_VAR{idx}_LEVELS', fcst['level'])
        config.set('config', f'FCST_VAR{idx}_THRESH', fcst['thresh'])
        config.set('config', f'OBS_VAR{idx}_NAME', obs['name'])
        config.set('config', f'OBS_VAR{idx}_LEVELS', obs['level'])
        config.set('config', f'OBS_VAR{idx}_THRESH', obs['thresh'])

    config.set('config', 'POINT_STAT_ONCE_PER_FIELD', False)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PointStatWrapper(config)
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

    fcst_fmt = f"field = [{','.join(fcst_fmts)}];"
    obs_fmt = f"field = [{','.join(obs_fmts)}];"

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        # including deprecated env vars (not in wrapper env var keys)
        for env_var_key in env_var_keys:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert value == fcst_fmt
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert value == obs_fmt
            else:
                assert env_var_values.get(env_var_key, '') == value


@pytest.mark.wrapper_a
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'PointStatConfig_wrapped')

    wrapper = PointStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'POINT_STAT_CONFIG_FILE', fake_config_name)
    wrapper = PointStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
