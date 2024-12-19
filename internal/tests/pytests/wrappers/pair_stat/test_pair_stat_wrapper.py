#!/usr/bin/env python3

import pytest

import os
from datetime import datetime, timedelta

from metplus.wrappers.pair_stat_wrapper import PairStatWrapper

pairs_dir = '/some/path/pairs'

fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level = '"(*,*)"'

inits = ['2005080700', '2005080712']
time_fmt = '%Y%m%d%H'
lead_hour = 12
lead_hour_str = str(lead_hour).zfill(3)
valids = []
for init in inits:
    valid = datetime.strptime(init, time_fmt) + timedelta(hours=lead_hour)
    valid = valid.strftime(time_fmt)
    valids.append(valid)


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PairStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', inits[0])
    config.set('config', 'INIT_END', inits[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', f'{lead_hour}H')

    config.set('config', 'PAIR_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/PairStatConfig_wrapped')
    config.set('config', 'PAIR_STAT_PAIRS_INPUT_DIR', pairs_dir)
    config.set('config', 'PAIR_STAT_PAIRS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'PAIR_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/PairStat/output')
    config.set('config', 'PAIR_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')


@pytest.mark.parametrize(
    'once_per_field, missing, run, thresh, errors, allow_missing', [
        (False, 6, 12, 0.5, 0, True),
        (False, 6, 12, 0.6, 1, True),
        (True, 12, 24, 0.5, 0, True),
        (True, 12, 24, 0.6, 1, True),
        (False, 6, 12, 0.5, 6, False),
        (True, 12, 24, 0.5, 12, False),
    ]
)
@pytest.mark.wrapper_a
def test_point_stat_missing_inputs(metplus_config, get_test_data_dir,
                                   once_per_field, missing, run, thresh, errors,
                                   allow_missing):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'PAIR_STAT_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'PAIR_STAT_INPUT_THRESH', thresh)
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'PAIR_STAT_PAIRS_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'PAIR_STAT_PAIRS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    # add 2 sets of fields to test ONCE_PER_FIELD
    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)
    config.set('config', 'FCST_VAR2_NAME', fcst_name)
    config.set('config', 'FCST_VAR2_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR2_NAME', obs_name)
    config.set('config', 'OBS_VAR2_LEVELS', obs_level)
    config.set('config', 'PAIR_STAT_ONCE_PER_FIELD', once_per_field)

    wrapper = PairStatWrapper(config)
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
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),
        ({'PAIR_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),
        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        # mask grid and poly (old config var)
        ({'PAIR_STAT_MASK_GRID': 'FULL',
          'PAIR_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_DICT': 'mask = {grid = ["FULL"];poly = ["one", "two"];}',
          }),
        # mask grid and poly (new config var)
        ({'PAIR_STAT_MASK_GRID': 'FULL',
          'PAIR_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_DICT': 'mask = {grid = ["FULL"];poly = ["one", "two"];}',
          }),
        # mask grid value
        ({'PAIR_STAT_MASK_GRID': 'FULL', },
         {'METPLUS_MASK_DICT': 'mask = {grid = ["FULL"];}',
          }),
        # mask.poly complex example
        ({'PAIR_STAT_MASK_POLY': ('["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly" ];'),
          },
         {'METPLUS_MASK_DICT':
              'mask = {poly = ["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
              '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly"];}',
          }),
        # mask grid empty string (should create empty list)
        ({'PAIR_STAT_MASK_GRID': '', },
         {'METPLUS_MASK_DICT': 'mask = {grid = [];}'}),
        # mask poly (new config var)
        ({'PAIR_STAT_MASK_POLY': 'one, two', },
         {'METPLUS_MASK_DICT': 'mask = {poly = ["one", "two"];}'}),
        ({'PAIR_STAT_MASK_SID': 'one, two', },
         {'METPLUS_MASK_DICT': 'mask = {sid = ["one", "two"];}'}),

        ({'PAIR_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'PAIR_STAT_OBS_WINDOW_BEGIN': '-2700',
          'PAIR_STAT_OBS_WINDOW_END': '2700',
          },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -2700;end = 2700;}'}),

        ({'PAIR_STAT_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'PAIR_STAT_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'PAIR_STAT_CLIMO_CDF_WRITE_BINS': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {write_bins = FALSE;}'}),

        ({'PAIR_STAT_CLIMO_CDF_DIRECT_PROB': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {direct_prob = FALSE;}'}),

        ({'PAIR_STAT_CLIMO_CDF_CDF_BINS': '1',
          'PAIR_STAT_CLIMO_CDF_CENTER_BINS': 'True',
          'PAIR_STAT_CLIMO_CDF_WRITE_BINS': 'False',
          'PAIR_STAT_CLIMO_CDF_DIRECT_PROB': 'False',},
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;write_bins = FALSE;direct_prob = FALSE;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_FHO': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {fho = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_CTC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ctc = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_CTS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cts = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_MCTC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mctc = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_MCTS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mcts = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_CNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cnt = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_SL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sl1l2 = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_SAL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {sal1l2 = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_VL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vl1l2 = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_VAL1L2': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {val1l2 = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_VCNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {vcnt = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_PCT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pct = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_PSTD': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pstd = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_PJC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pjc = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_PRC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {prc = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_ECNT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ecnt = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_ORANK': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {orank = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_RPS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {rps = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_ECLV': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {eclv = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_MPR': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {mpr = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_SEEPS': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {seeps = BOTH;}'}),

        ({'PAIR_STAT_OUTPUT_FLAG_SEEPS_MPR': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {seeps_mpr = BOTH;}'}),

        ({
             'PAIR_STAT_OUTPUT_FLAG_FHO': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_CTC': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_CTS': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_MCTC': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_MCTS': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_CNT': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_SL1L2': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_SAL1L2': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_VL1L2': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_VAL1L2': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_VCNT': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_PCT': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_PSTD': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_PJC': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_PRC': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_ECNT': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_ORANK': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_RPS': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_ECLV': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_MPR': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_SEEPS': 'BOTH',
             'PAIR_STAT_OUTPUT_FLAG_SEEPS_MPR': 'BOTH',
         },
         {'METPLUS_OUTPUT_FLAG_DICT': (
              'output_flag = {fho = BOTH;ctc = BOTH;cts = BOTH;mctc = BOTH;'
              'mcts = BOTH;cnt = BOTH;sl1l2 = BOTH;sal1l2 = BOTH;'
              'vl1l2 = BOTH;val1l2 = BOTH;vcnt = BOTH;pct = BOTH;pstd = BOTH;'
              'pjc = BOTH;prc = BOTH;ecnt = BOTH;orank = BOTH;rps = BOTH;'
              'eclv = BOTH;mpr = BOTH;seeps = BOTH;seeps_mpr = BOTH;'
              '}'
         )}),

        ({'PAIR_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}')}),

        ({'PAIR_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'PAIR_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),

        ({'PAIR_STAT_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),

        ({'PAIR_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),

        ({'PAIR_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),

        ({'PAIR_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),

        ({'PAIR_STAT_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),

        ({'PAIR_STAT_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),

        ({'PAIR_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),

        ({
             'PAIR_STAT_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'PAIR_STAT_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'PAIR_STAT_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'PAIR_STAT_CLIMO_MEAN_REGRID_WIDTH': '1',
             'PAIR_STAT_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'PAIR_STAT_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'PAIR_STAT_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'PAIR_STAT_CLIMO_MEAN_MATCH_MONTH': 'True',
             'PAIR_STAT_CLIMO_MEAN_DAY_INTERVAL': '30',
             'PAIR_STAT_CLIMO_MEAN_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}')}),

        # climo stdev
        ({'PAIR_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                       '["/some/climo_stdev/file.txt"];}')}),

        ({'PAIR_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'PAIR_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),

        ({'PAIR_STAT_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),

        ({'PAIR_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),

        ({'PAIR_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),

        ({'PAIR_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),

        ({'PAIR_STAT_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),

        ({'PAIR_STAT_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),

        ({'PAIR_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),

        ({
             'PAIR_STAT_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'PAIR_STAT_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'PAIR_STAT_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'PAIR_STAT_CLIMO_STDEV_REGRID_WIDTH': '1',
             'PAIR_STAT_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'PAIR_STAT_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'PAIR_STAT_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'PAIR_STAT_CLIMO_STDEV_MATCH_MONTH': 'True',
             'PAIR_STAT_CLIMO_STDEV_DAY_INTERVAL': '30',
             'PAIR_STAT_CLIMO_STDEV_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                       '["/some/climo_stdev/file.txt"];'
                                       'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                       'regrid = {method = NEAREST;width = 1;'
                                       'vld_thresh = 0.5;shape = SQUARE;}'
                                       'time_interp_method = NEAREST;'
                                       'match_month = TRUE;day_interval = 30;'
                                       'hour_interval = 12;}')}),
        ({'PAIR_STAT_HSS_EC_VALUE': '0.5', },
         {'METPLUS_HSS_EC_VALUE': 'hss_ec_value = 0.5;'}),
        ({'PAIR_STAT_MASK_LLPNT': ('{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; },'
                                    '{ name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }')},
         {'METPLUS_MASK_DICT': 'mask = {llpnt = [{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; }, { name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }];}'}),

        ({'PAIR_STAT_FCST_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'PAIR_STAT_FCST_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'PAIR_STAT_SEEPS_P1_THRESH': 'ge0.1&&le0.85', },
         {'METPLUS_SEEPS_P1_THRESH': 'seeps_p1_thresh = ge0.1&&le0.85;'}),
        ({'PAIR_STAT_OBS_VALID_BEG': '{valid?fmt=%Y%m%d_%H?shift=-6H}', }, {}),
        ({'PAIR_STAT_OBS_VALID_END': '{valid?fmt=%Y%m%d_%H?shift=6H}', }, {}),
        ({'PAIR_STAT_OBS_VALID_BEG': '{valid?fmt=%Y%m%d_%H?shift=-6H}',
          'PAIR_STAT_OBS_VALID_END': '{valid?fmt=%Y%m%d_%H?shift=6H}'}, {}),
        # complex mask example
        ({'PAIR_STAT_MASK_GRID': 'FULL',
          'PAIR_STAT_MASK_POLY': ('["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
                                   '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly" ];'),
          'PAIR_STAT_MASK_SID': 'one, two',
          'PAIR_STAT_MASK_LLPNT': (
         '{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; },'
         '{ name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }')},
         {'METPLUS_MASK_DICT': (
             'mask = {grid = ["FULL"];'
             'poly = ["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
             '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
             '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
             '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly"];'
             'sid = ["one", "two"];'
             'llpnt = [{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; }, { name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }];}'
          )}),
        # complex mask example, empty grid value
        ({'PAIR_STAT_MASK_GRID': '',
          'PAIR_STAT_MASK_POLY': (
          '["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
          '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
          '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
          '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly" ];'),
          'PAIR_STAT_MASK_SID': 'one, two',
          'PAIR_STAT_MASK_LLPNT': (
                  '{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; },'
                  '{ name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }')},
         {'METPLUS_MASK_DICT': (
                 'mask = {grid = [];'
                 'poly = ["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", '
                 '"{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly", '
                 '"{ENV[MET_BUILD_BASE]}/share/met/poly/NAO.poly", '
                 '"{ENV[MET_BUILD_BASE]}/share/met/poly/SAO.poly"];'
                 'sid = ["one", "two"];'
                 'llpnt = [{ name = "LAT30TO40"; lat_thresh = >=30&&<=40; lon_thresh = NA; }, { name = "BOX"; lat_thresh = >=20&&<=40; lon_thresh = >=-110&&<=-90; }];}'
         )}),

        # land_mask dictionary
        ({'PAIR_STAT_LAND_MASK_FLAG': 'false', },
         {'METPLUS_LAND_MASK_DICT': 'land_mask = {flag = FALSE;}'}),
        ({'PAIR_STAT_LAND_MASK_FILE_NAME': '/some/file/path.nc', },
         {'METPLUS_LAND_MASK_DICT': 'land_mask = {file_name = ["/some/file/path.nc"];}'}),
        ({'PAIR_STAT_LAND_MASK_FIELD_NAME': 'LAND',
          'PAIR_STAT_LAND_MASK_FIELD_LEVEL': 'L0'},
         {'METPLUS_LAND_MASK_DICT': 'land_mask = {field = {name = "LAND";level = "L0";}}'}),
        ({'PAIR_STAT_LAND_MASK_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_LAND_MASK_REGRID_WIDTH': '1'},
         {'METPLUS_LAND_MASK_DICT': 'land_mask = {regrid = {method = NEAREST;width = 1;}}'}),
        ({'PAIR_STAT_LAND_MASK_THRESH': 'eq1', },
         {'METPLUS_LAND_MASK_DICT': 'land_mask = {thresh = eq1;}'}),
        ({'PAIR_STAT_LAND_MASK_FLAG': 'false',
          'PAIR_STAT_LAND_MASK_FILE_NAME': '/some/file/path.nc',
          'PAIR_STAT_LAND_MASK_FIELD_NAME': 'LAND',
          'PAIR_STAT_LAND_MASK_FIELD_LEVEL': 'L0',
          'PAIR_STAT_LAND_MASK_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_LAND_MASK_REGRID_WIDTH': '1',
          'PAIR_STAT_LAND_MASK_THRESH': 'eq1',
         },
         {'METPLUS_LAND_MASK_DICT': ('land_mask = {flag = FALSE;file_name = ["/some/file/path.nc"];'
                                     'field = {name = "LAND";level = "L0";}'
                                     'regrid = {method = NEAREST;width = 1;}thresh = eq1;}')}),
        # topo_mask dictionary
        ({'PAIR_STAT_TOPO_MASK_FLAG': 'false', },
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {flag = FALSE;}'}),
        ({'PAIR_STAT_TOPO_MASK_FILE_NAME': '/some/file/path.nc', },
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {file_name = ["/some/file/path.nc"];}'}),
        ({'PAIR_STAT_TOPO_MASK_FIELD_NAME': 'TOPO',
          'PAIR_STAT_TOPO_MASK_FIELD_LEVEL': 'L0'},
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {field = {name = "TOPO";level = "L0";}}'}),
        ({'PAIR_STAT_TOPO_MASK_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_TOPO_MASK_REGRID_WIDTH': '1'},
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {regrid = {method = NEAREST;width = 1;}}'}),
        ({'PAIR_STAT_TOPO_MASK_USE_OBS_THRESH': 'ge-100&&le100', },
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {use_obs_thresh = ge-100&&le100;}'}),
        ({'PAIR_STAT_TOPO_MASK_INTERP_FCST_THRESH': 'ge-50&&le50', },
         {'METPLUS_TOPO_MASK_DICT': 'topo_mask = {interp_fcst_thresh = ge-50&&le50;}'}),
        ({'PAIR_STAT_TOPO_MASK_FLAG': 'false',
          'PAIR_STAT_TOPO_MASK_FILE_NAME': '/some/file/path.nc',
          'PAIR_STAT_TOPO_MASK_FIELD_NAME': 'TOPO',
          'PAIR_STAT_TOPO_MASK_FIELD_LEVEL': 'L0',
          'PAIR_STAT_TOPO_MASK_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_TOPO_MASK_REGRID_WIDTH': '1',
          'PAIR_STAT_TOPO_MASK_USE_OBS_THRESH': 'ge-100&&le100',
          'PAIR_STAT_TOPO_MASK_INTERP_FCST_THRESH': 'ge-50&&le50'
         },
         {'METPLUS_TOPO_MASK_DICT': ('topo_mask = {flag = FALSE;file_name = ["/some/file/path.nc"];'
                                     'field = {name = "TOPO";level = "L0";}regrid = {method = NEAREST;width = 1;}'
                                     'use_obs_thresh = ge-100&&le100;interp_fcst_thresh = ge-50&&le50;}')}),

        # fcst climo_mean
        ({'PAIR_STAT_FCST_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {file_name = ["/some/climo_mean/file.txt"];}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'PAIR_STAT_FCST_CLIMO_MEAN_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'PAIR_STAT_FCST_CLIMO_MEAN_VAR1_LEVELS': 'P850',
          'PAIR_STAT_FCST_CLIMO_MEAN_VAR2_NAME': 'VGRD', 'PAIR_STAT_FCST_CLIMO_MEAN_VAR2_LEVELS': 'P500',},
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_DAY_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = NA;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_HOUR_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = NA;}'}),
        ({'PAIR_STAT_FCST_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
          'PAIR_STAT_FCST_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_WIDTH': '1',
          'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
          'PAIR_STAT_FCST_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
          'PAIR_STAT_FCST_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
          'PAIR_STAT_FCST_CLIMO_MEAN_MATCH_MONTH': 'True',
          'PAIR_STAT_FCST_CLIMO_MEAN_DAY_INTERVAL': '30',
          'PAIR_STAT_FCST_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                           '["/some/climo_mean/file.txt"];'
                                           'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                           'regrid = {method = NEAREST;width = 1;'
                                           'vld_thresh = 0.5;shape = SQUARE;}'
                                           'time_interp_method = NEAREST;'
                                           'match_month = TRUE;day_interval = 30;'
                                           'hour_interval = 12;}')}),
        # fcst climo_stdev
        ({'PAIR_STAT_FCST_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {file_name = ["/some/climo_stdev/file.txt"];}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'PAIR_STAT_FCST_CLIMO_STDEV_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'PAIR_STAT_FCST_CLIMO_STDEV_VAR1_LEVELS': 'P850',
          'PAIR_STAT_FCST_CLIMO_STDEV_VAR2_NAME': 'VGRD', 'PAIR_STAT_FCST_CLIMO_STDEV_VAR2_LEVELS': 'P500',},
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_DAY_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = NA;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_HOUR_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = NA;}'}),
        ({'PAIR_STAT_FCST_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
          'PAIR_STAT_FCST_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_WIDTH': '1',
          'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
          'PAIR_STAT_FCST_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
          'PAIR_STAT_FCST_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
          'PAIR_STAT_FCST_CLIMO_STDEV_MATCH_MONTH': 'True',
          'PAIR_STAT_FCST_CLIMO_STDEV_DAY_INTERVAL': '30',
          'PAIR_STAT_FCST_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                            '["/some/climo_stdev/file.txt"];'
                                            'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                            'regrid = {method = NEAREST;width = 1;'
                                            'vld_thresh = 0.5;shape = SQUARE;}'
                                            'time_interp_method = NEAREST;'
                                            'match_month = TRUE;day_interval = 30;'
                                            'hour_interval = 12;}')}),
        # obs climo_mean
        ({'PAIR_STAT_OBS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {file_name = ["/some/climo_mean/file.txt"];}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'PAIR_STAT_OBS_CLIMO_MEAN_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'PAIR_STAT_OBS_CLIMO_MEAN_VAR1_LEVELS': 'P850',
          'PAIR_STAT_OBS_CLIMO_MEAN_VAR2_NAME': 'VGRD', 'PAIR_STAT_OBS_CLIMO_MEAN_VAR2_LEVELS': 'P500',},
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_DAY_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = NA;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_HOUR_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = NA;}'}),
        ({'PAIR_STAT_OBS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
          'PAIR_STAT_OBS_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_WIDTH': '1',
          'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
          'PAIR_STAT_OBS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
          'PAIR_STAT_OBS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
          'PAIR_STAT_OBS_CLIMO_MEAN_MATCH_MONTH': 'True',
          'PAIR_STAT_OBS_CLIMO_MEAN_DAY_INTERVAL': '30',
          'PAIR_STAT_OBS_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                          '["/some/climo_mean/file.txt"];'
                                          'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                          'regrid = {method = NEAREST;width = 1;'
                                          'vld_thresh = 0.5;shape = SQUARE;}'
                                          'time_interp_method = NEAREST;'
                                          'match_month = TRUE;day_interval = 30;'
                                          'hour_interval = 12;}')}),
        # obs climo_stdev
        ({'PAIR_STAT_OBS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {file_name = ["/some/climo_stdev/file.txt"];}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'PAIR_STAT_OBS_CLIMO_STDEV_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'PAIR_STAT_OBS_CLIMO_STDEV_VAR1_LEVELS': 'P850',
          'PAIR_STAT_OBS_CLIMO_STDEV_VAR2_NAME': 'VGRD', 'PAIR_STAT_OBS_CLIMO_STDEV_VAR2_LEVELS': 'P500',},
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_DAY_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = NA;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_HOUR_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = NA;}'}),
        ({'PAIR_STAT_OBS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
          'PAIR_STAT_OBS_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_WIDTH': '1',
          'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
          'PAIR_STAT_OBS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
          'PAIR_STAT_OBS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
          'PAIR_STAT_OBS_CLIMO_STDEV_MATCH_MONTH': 'True',
          'PAIR_STAT_OBS_CLIMO_STDEV_DAY_INTERVAL': '30',
          'PAIR_STAT_OBS_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                           '["/some/climo_stdev/file.txt"];'
                                           'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                           'regrid = {method = NEAREST;width = 1;'
                                           'vld_thresh = 0.5;shape = SQUARE;}'
                                           'time_interp_method = NEAREST;'
                                           'match_month = TRUE;day_interval = 30;'
                                           'hour_interval = 12;}')}),
        ({'PAIR_STAT_POINT_WEIGHT_FLAG': 'SID', },
         {'METPLUS_POINT_WEIGHT_FLAG': 'point_weight_flag = SID;'}),

    ]
)
@pytest.mark.wrapper_a
def test_pair_stat_all_fields(metplus_config, config_overrides,
                              env_var_values, compare_command_and_env_vars):
    level_no_quotes = '(*,*)'
    level_with_quotes = f'"{level_no_quotes}"'

    fcsts = [{'name': 'TMP',
              'level': 'P750-900',
              'thresh': '<=273,>273'},
              {'name': 'UGRD',
               'level': 'Z10',
               'thresh': '>=5'},
             ]
    obss = [{'name': 'TMP',
            'level': level_no_quotes,
            'thresh': '<=273,>273'},
            {'name': 'UGRD',
             'level': 'Z10',
             'thresh': '>=5'},
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

    config.set('config', 'PAIR_STAT_ONCE_PER_FIELD', False)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PairStatWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    # add extra command line arguments
    extra_args = [' '] * len(inits)

    for beg_end in ('BEG', 'END'):
        if f'PAIR_STAT_OBS_VALID_{beg_end}' in config_overrides:
            for index in range(0, len(inits)):
                valid_dt = datetime.strptime(valids[index], time_fmt)
                if beg_end == 'BEG':
                    value = valid_dt - timedelta(hours=6)
                else:
                    value = valid_dt + timedelta(hours=6)
                value = value.strftime('%Y%m%d_%H')
                extra_args[index] += f'-obs_valid_{beg_end.lower()} {value} '

    expected_cmds = []
    for index in range(0, len(inits)):
        expected_cmds.append(
            f"{app_path} {verbosity} "
            f"{pairs_dir}/{inits[index]}/fcst_file_F{lead_hour_str} "
            f"{config_file}{extra_args[index]}-outdir {out_dir}/{valids[index]}"
        )

    fcst_fmt = f"pairs = [{','.join(fcst_fmts)}];"
    obs_fmt = f"pairs = [{','.join(obs_fmts)}];"

    all_cmds = wrapper.run_all_times()
    special_values = {
        'METPLUS_FCST_FIELD': fcst_fmt,
        'METPLUS_OBS_FIELD': obs_fmt,
    }
    special_values = {}
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values,
                                 wrapper, special_values)


@pytest.mark.wrapper_a
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'PairStatConfig_wrapped')

    wrapper = PairStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'PAIR_STAT_CONFIG_FILE', fake_config_name)
    wrapper = PairStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
