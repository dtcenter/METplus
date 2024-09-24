import pytest
from unittest import mock
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.wrappers.series_analysis_wrapper import SeriesAnalysisWrapper
from metplus.wrappers import series_analysis_wrapper as saw

fcst_dir = '/some/fcst/dir'
obs_dir = '/some/obs/dir'
fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level_no_quotes = '(*,*)'
obs_level = f'"{obs_level_no_quotes}"'
fcst_fmt = f'field = [{{ name="{fcst_name}"; level="{fcst_level}"; }}];'
obs_fmt = (f'field = [{{ name="{obs_name}"; '
           f'level="{obs_level_no_quotes}"; }}];')
time_fmt = '%Y%m%d%H'
#run_times = ['2005080700', '2005080712']
run_times = ['2005080700',]
stat_list = 'TOTAL,RMSE,FBAR,OBAR'
stat_list_quotes = '", "'.join(stat_list.split(','))
stat_list_fmt = f'output_stats = {{cnt = ["{stat_list_quotes}"];}}'


def get_input_dirs(config):
    fake_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal', 'tests',
                                 'data')
    stat_input_dir = os.path.join(fake_data_dir,
                                  'stat_data')
    tile_input_dir = os.path.join(fake_data_dir,
                                  'tiles')
    return stat_input_dir, tile_input_dir


def series_analysis_wrapper(metplus_config, config_overrides=None):
    config = metplus_config
    config.set('config', 'SERIES_ANALYSIS_STAT_LIST', 'TOTAL, FBAR, OBAR, ME')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d')
    config.set('config', 'INIT_BEG', '20141214')
    config.set('config', 'INIT_END', '20141214')
    config.set('config', 'INIT_INCREMENT', '21600')
    config.set('config', 'SERIES_ANALYSIS_BACKGROUND_MAP', 'no')
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_TEMPLATE',
               ('{init?fmt=%Y%m%d_%H}/{storm_id}/FCST_TILE_F{lead?fmt=%3H}_'
                'gfs_4_{init?fmt=%Y%m%d}_{init?fmt=%H}00_{lead?fmt=%3H}.nc'))
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_TEMPLATE',
               ('{init?fmt=%Y%m%d_%H}/{storm_id}/OBS_TILE_F{lead?fmt=%3H}_gfs'
                '_4_{init?fmt=%Y%m%d}_{init?fmt=%H}00_{lead?fmt=%3H}.nc'))
    config.set('config', 'EXTRACT_TILES_OUTPUT_DIR',
               '{OUTPUT_BASE}/extract_tiles')
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_DIR',
               '{EXTRACT_TILES_OUTPUT_DIR}')
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_DIR',
               '{EXTRACT_TILES_OUTPUT_DIR}')
    config.set('config', 'SERIES_ANALYSIS_OUTPUT_DIR',
               '{OUTPUT_BASE}/series_analysis_init')
    if config_overrides:
        for key, value in config_overrides.items():
            config.set('config', key, value)

    return SeriesAnalysisWrapper(config)


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'SeriesAnalysis')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'SERIES_ANALYSIS_RUNTIME_FREQ',
               'RUN_ONCE_PER_INIT_OR_VALID')
    config.set('config', 'SERIES_ANALYSIS_CONFIG_FILE',
               '{PARM_BASE}/met_config/SeriesAnalysisConfig_wrapped')
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H},{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file,{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'SERIES_ANALYSIS_OUTPUT_DIR',
               '{OUTPUT_BASE}/SeriesAnalysis/output')
    config.set('config', 'SERIES_ANALYSIS_OUTPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)

    config.set('config', 'SERIES_ANALYSIS_STAT_LIST', stat_list)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing, runtime_freq', [
        (0, 1, 0.5, 0, True, 'RUN_ONCE'),
        (0, 1, 0.5, 0, False, 'RUN_ONCE'),
        (0, 2, 0.5, 0, True, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (0, 2, 0.5, 0, False, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (2, 7, 1.0, 1, True, 'RUN_ONCE_PER_LEAD'),
        (2, 7, 1.0, 2, False, 'RUN_ONCE_PER_LEAD'),
        (8, 14, 1.0, 1, True, 'RUN_ONCE_FOR_EACH'),
        (8, 14, 1.0, 8, False, 'RUN_ONCE_FOR_EACH'),
    ]
)
@pytest.mark.wrapper_a
def test_series_analysis_missing_inputs(metplus_config, get_test_data_dir,
                                        missing, run, thresh, errors, allow_missing,
                                        runtime_freq):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'SERIES_ANALYSIS_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'SERIES_ANALYSIS_INPUT_THRESH', thresh)
    config.set('config', 'SERIES_ANALYSIS_RUNTIME_FREQ', runtime_freq)
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12,15')
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_DIR', get_test_data_dir('obs'))
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')

    wrapper = SeriesAnalysisWrapper(config)
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
        ({'SERIES_ANALYSIS_REGRID_TO_GRID': 'FCST', },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'SERIES_ANALYSIS_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'SERIES_ANALYSIS_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'SERIES_ANALYSIS_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'SERIES_ANALYSIS_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'SERIES_ANALYSIS_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'SERIES_ANALYSIS_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'SERIES_ANALYSIS_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'SERIES_ANALYSIS_REGRID_TO_GRID': 'FCST',
          'SERIES_ANALYSIS_REGRID_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_REGRID_WIDTH': '1',
          'SERIES_ANALYSIS_REGRID_VLD_THRESH': '0.5',
          'SERIES_ANALYSIS_REGRID_SHAPE': 'SQUARE',
          'SERIES_ANALYSIS_REGRID_CONVERT': '2*x',
          'SERIES_ANALYSIS_REGRID_CENSOR_THRESH': '>12000,<5000',
          'SERIES_ANALYSIS_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )}),
        # climo_mean
        ({'SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}')}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),

        ({'SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),

        ({
             'SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'SERIES_ANALYSIS_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH': '1',
             'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH': 'True',
             'SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL': '30',
             'SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL': '12',
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
        ({'SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];}')}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),

        ({'SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),

        ({
             'SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'SERIES_ANALYSIS_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH': '1',
             'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH': 'True',
             'SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL': '30',
             'SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}')}),
        ({'SERIES_ANALYSIS_HSS_EC_VALUE': '0.5', },
         {'METPLUS_HSS_EC_VALUE': 'hss_ec_value = 0.5;'}),
        # output_stats
        ({'SERIES_ANALYSIS_OUTPUT_STATS_FHO': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {fho = ["RMSE", "FBAR", "OBAR"];cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_CTC': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {ctc = ["RMSE", "FBAR", "OBAR"];cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_CTS': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cts = ["RMSE", "FBAR", "OBAR"];cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_MCTC': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {mctc = ["RMSE", "FBAR", "OBAR"];cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_MCTS': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {mcts = ["RMSE", "FBAR", "OBAR"];cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_CNT': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_SL1L2': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];sl1l2 = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_SAL1L2': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];sal1l2 = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_PCT': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];pct = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_PSTD': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];pstd = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_PJC': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];pjc = ["RMSE", "FBAR", "OBAR"];}'}),

        ({'SERIES_ANALYSIS_OUTPUT_STATS_PRC': 'RMSE,FBAR,OBAR', },
         {'METPLUS_OUTPUT_STATS_DICT': 'output_stats = {cnt = ["TOTAL", "RMSE", "FBAR", "OBAR"];prc = ["RMSE", "FBAR", "OBAR"];}'}),

        ({
             'SERIES_ANALYSIS_OUTPUT_STATS_FHO': 'RMSE1,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_CTC': 'RMSE2,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_CTS': 'RMSE3,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_MCTC': 'RMSE4,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_MCTS': 'RMSE5,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_CNT': 'RMSE6,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_SL1L2': 'RMSE7,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_SAL1L2': 'RMSE8,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_PCT': 'RMSE9,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_PSTD': 'RMSE10,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_PJC': 'RMSE11,FBAR,OBAR',
             'SERIES_ANALYSIS_OUTPUT_STATS_PRC': 'RMSE12,FBAR,OBAR',
         },
         {'METPLUS_OUTPUT_STATS_DICT': ('output_stats = {'
                                        'fho = ["RMSE1", "FBAR", "OBAR"];'
                                        'ctc = ["RMSE2", "FBAR", "OBAR"];'
                                        'cts = ["RMSE3", "FBAR", "OBAR"];'
                                        'mctc = ["RMSE4", "FBAR", "OBAR"];'
                                        'mcts = ["RMSE5", "FBAR", "OBAR"];'
                                        'cnt = ["RMSE6", "FBAR", "OBAR"];'
                                        'sl1l2 = ["RMSE7", "FBAR", "OBAR"];'
                                        'sal1l2 = ["RMSE8", "FBAR", "OBAR"];'
                                        'pct = ["RMSE9", "FBAR", "OBAR"];'
                                        'pstd = ["RMSE10", "FBAR", "OBAR"];'
                                        'pjc = ["RMSE11", "FBAR", "OBAR"];'
                                        'prc = ["RMSE12", "FBAR", "OBAR"];}')}),
        ({'SERIES_ANALYSIS_FCST_CAT_THRESH': '>=0.0, >=0.3, >=1.0', },
         {'METPLUS_FCST_CAT_THRESH': 'cat_thresh = [>=0.0, >=0.3, >=1.0];'}),

        ({'SERIES_ANALYSIS_OBS_CAT_THRESH': '<=CDP33', },
         {'METPLUS_OBS_CAT_THRESH': 'cat_thresh = [<=CDP33];'}),

        ({'SERIES_ANALYSIS_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'SERIES_ANALYSIS_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'SERIES_ANALYSIS_CLIMO_CDF_DIRECT_PROB': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {direct_prob = FALSE;}'}),

        ({'SERIES_ANALYSIS_CLIMO_CDF_CDF_BINS': '1',
          'SERIES_ANALYSIS_CLIMO_CDF_CENTER_BINS': 'True',
          'SERIES_ANALYSIS_CLIMO_CDF_DIRECT_PROB': 'False',
         },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;direct_prob = FALSE;}'}),
        ({'SERIES_ANALYSIS_MASK_GRID': 'FULL', },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";}'}),

        ({'SERIES_ANALYSIS_MASK_POLY': 'MET_BASE/poly/EAST.poly', },
         {'METPLUS_MASK_DICT': 'mask = {poly = "MET_BASE/poly/EAST.poly";}'}),

        ({
             'SERIES_ANALYSIS_MASK_GRID': 'FULL',
             'SERIES_ANALYSIS_MASK_POLY': 'MET_BASE/poly/EAST.poly',
         },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";poly = "MET_BASE/poly/EAST.poly";}'}),
        # check animation config works
        ({
             'FCST_VAR1_LEVELS': 'A03',
             'SERIES_ANALYSIS_GENERATE_PLOTS': 'True',
             'SERIES_ANALYSIS_GENERATE_ANIMATIONS': 'True',
             'CONVERT_EXE': 'animation_exe'
         },
         {},),
        # check 'BOTH_*' and '*INPUT_FILE_LIST' config 
        ({'SERIES_ANALYSIS_REGRID_TO_GRID': 'FCST',
          'BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE': 'True,True',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),
        # TODO: Fix these tests to include file list paths
        # ({'SERIES_ANALYSIS_REGRID_TO_GRID': 'FCST',
        #   'BOTH_SERIES_ANALYSIS_INPUT_FILE_LIST': 'True',
        #   },
        #  {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),
        # ({'SERIES_ANALYSIS_REGRID_TO_GRID': 'FCST',
        #   'FCST_SERIES_ANALYSIS_INPUT_FILE_LIST': 'True',
        #   'OBS_SERIES_ANALYSIS_INPUT_FILE_LIST': 'True',
        #   },
        #  {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        # fcst climo_mean
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {file_name = ["/some/climo_mean/file.txt"];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR1_LEVELS': 'P850',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR2_NAME': 'VGRD', 'SERIES_ANALYSIS_FCST_CLIMO_MEAN_VAR2_LEVELS': 'P500',},
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_DAY_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = NA;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_HOUR_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = NA;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_WIDTH': '1',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_MATCH_MONTH': 'True',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_DAY_INTERVAL': '30',
          'SERIES_ANALYSIS_FCST_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                           '["/some/climo_mean/file.txt"];'
                                           'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                           'regrid = {method = NEAREST;width = 1;'
                                           'vld_thresh = 0.5;shape = SQUARE;}'
                                           'time_interp_method = NEAREST;'
                                           'match_month = TRUE;day_interval = 30;'
                                           'hour_interval = 12;}')}),
        # fcst climo_stdev
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {file_name = ["/some/climo_stdev/file.txt"];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR1_LEVELS': 'P850',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR2_NAME': 'VGRD', 'SERIES_ANALYSIS_FCST_CLIMO_STDEV_VAR2_LEVELS': 'P500',},
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_DAY_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = NA;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_HOUR_INTERVAL': 'NA', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = NA;}'}),
        ({'SERIES_ANALYSIS_FCST_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_WIDTH': '1',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_MATCH_MONTH': 'True',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_DAY_INTERVAL': '30',
          'SERIES_ANALYSIS_FCST_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_FCST_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                            '["/some/climo_stdev/file.txt"];'
                                            'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                            'regrid = {method = NEAREST;width = 1;'
                                            'vld_thresh = 0.5;shape = SQUARE;}'
                                            'time_interp_method = NEAREST;'
                                            'match_month = TRUE;day_interval = 30;'
                                            'hour_interval = 12;}')}),
        # obs climo_mean
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {file_name = ["/some/climo_mean/file.txt"];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR1_LEVELS': 'P850',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR2_NAME': 'VGRD', 'SERIES_ANALYSIS_OBS_CLIMO_MEAN_VAR2_LEVELS': 'P500',},
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_DAY_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = NA;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_HOUR_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = NA;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_WIDTH': '1',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_MATCH_MONTH': 'True',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_DAY_INTERVAL': '30',
          'SERIES_ANALYSIS_OBS_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                          '["/some/climo_mean/file.txt"];'
                                          'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                          'regrid = {method = NEAREST;width = 1;'
                                          'vld_thresh = 0.5;shape = SQUARE;}'
                                          'time_interp_method = NEAREST;'
                                          'match_month = TRUE;day_interval = 30;'
                                          'hour_interval = 12;}')}),
        # obs climo_stdev
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {file_name = ["/some/climo_stdev/file.txt"];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_FIELD': '{name="UGRD"; level=["P850","P500","P250"];}', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="UGRD"; level=["P850","P500","P250"];}];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR1_LEVELS':'P850,P500,P250', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="UGRD"; level="P500"; }, { name="UGRD"; level="P250"; }];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR1_NAME': 'UGRD', 'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR1_LEVELS': 'P850',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR2_NAME': 'VGRD', 'SERIES_ANALYSIS_OBS_CLIMO_STDEV_VAR2_LEVELS': 'P500',},
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{ name="UGRD"; level="P850"; }, { name="VGRD"; level="P500"; }];}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_DAY_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = NA;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_HOUR_INTERVAL': 'NA', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = NA;}'}),
        ({'SERIES_ANALYSIS_OBS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_WIDTH': '1',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_MATCH_MONTH': 'True',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_DAY_INTERVAL': '30',
          'SERIES_ANALYSIS_OBS_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_OBS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                           '["/some/climo_stdev/file.txt"];'
                                           'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                           'regrid = {method = NEAREST;width = 1;'
                                           'vld_thresh = 0.5;shape = SQUARE;}'
                                           'time_interp_method = NEAREST;'
                                           'match_month = TRUE;day_interval = 30;'
                                           'hour_interval = 12;}')}),
    ]
)
@pytest.mark.wrapper_a
def test_series_analysis_single_field(metplus_config, config_overrides,
                                      env_var_values, compare_command_and_env_vars):

    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.isOK

    is_both = wrapper.c_dict.get('USING_BOTH')
    
    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"

    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    prefix = 'series_analysis_files_'
    suffix = '_init_20050807000000_valid_ALL_lead_ALL.txt'
    fcst_file = f'{prefix}fcst{suffix}'
    obs_file = f'{prefix}obs{suffix}'
    
    if is_both:
        expected_cmds = [(f"{app_path} "
                      f"-both {out_dir}/{fcst_file} "
                      f"-out {out_dir}/2005080700 "
                      f"-config {config_file} {verbosity}"),
                     ]
    else:
        expected_cmds = [(f"{app_path} "
                      f"-fcst {out_dir}/{fcst_file} "
                      f"-obs {out_dir}/{obs_file} "
                      f"-out {out_dir}/2005080700 "
                      f"-config {config_file} {verbosity}"),
                     ]

    all_cmds = wrapper.run_all_times()

    expected_len = len(expected_cmds)
    if 'SERIES_ANALYSIS_GENERATE_PLOTS' in config_overrides:
        expected_len += 8
        if 'SERIES_ANALYSIS_GENERATE_ANIMATIONS' in config_overrides:
            expected_len += 4
    assert len(all_cmds) == expected_len

    special_values = {
        'METPLUS_FCST_FIELD': fcst_fmt,
        'METPLUS_OBS_FIELD': obs_fmt,
    }
    if 'METPLUS_OUTPUT_STATS_DICT' not in env_var_values:
        special_values['METPLUS_OUTPUT_STATS_DICT'] = stat_list_fmt
    # only compare first command since the rest are not series_analysis
    compare_command_and_env_vars(all_cmds[0:1], expected_cmds, env_var_values,
                                 wrapper, special_values)


@pytest.mark.wrapper_a
def test_get_fcst_file_info(metplus_config):
    """ Verify that the tuple created by get_fcst_file_info is
        not an empty tuple, and that the number, beginning
        fcst file and end fcst file are what we expected.
    """
    storm_id = 'ML1200942014'
    expected_num = str(9)
    expected_beg = '000'
    expected_end = '048'

    wrapper = series_analysis_wrapper(metplus_config)
    wrapper.c_dict['FCST_INPUT_DIR'] = '/fake/path/of/file'
    wrapper.c_dict['FCST_INPUT_TEMPLATE'] = (
        "FCST_TILE_F{lead?fmt=%3H}_gfs_4_{init?fmt=%Y%m%d}_"
        "{init?fmt=%H}00_000.nc"
    )

    output_dir = (
        os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                     'internal', 'tests',
                     'data',
                     'file_lists')
    )
    output_filename = f"FCST_FILES_{storm_id}"
    fcst_path = os.path.join(output_dir, output_filename)

    num, beg, end = wrapper.get_fcst_file_info(fcst_path)
    assert num == expected_num
    assert beg == expected_beg
    assert end == expected_end


@pytest.mark.wrapper_a
def test_get_storms_list(metplus_config):
    """Verify that the expected number of storms
       are found for the init time 20141214_00
    """
    expected_storm_list = ['ML1201072014',
                           'ML1221072014',
                           'ML1241072014',
                           'ML1251072014'
                           ]
    time_info = {'init': datetime(2014, 12, 14, 00)}
    stat_input_template = 'fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    wrapper = series_analysis_wrapper(metplus_config)
    stat_input_dir, _ = get_input_dirs(wrapper.config)

    wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = True
    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template

    storm_list = wrapper.get_storm_list(time_info)
    assert storm_list == expected_storm_list


@pytest.mark.parametrize(
        'time_info, expect_fcst_subset, expect_obs_subset', [
        # 0: filter by init all storms
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': '*'},
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',]),
        # 1: filter by init single storm
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': 'ML1201072014'},
         [
             'fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
             'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         [
             'obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
             'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
             'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # 2: filter by init another single storm
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': 'ML1221072014'},
         [
             'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         [
             'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
             'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
             'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # 3: filter by lead all storms
        ({'init': '*',
          'valid': '*',
          'lead': 21600,
          'storm_id': '*'},
         [
             'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         [
             'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
             'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
    ]
)
@pytest.mark.wrapper_a
def test_get_all_files_and_subset(metplus_config, time_info, expect_fcst_subset, expect_obs_subset):
    """! Test to ensure that get_all_files only gets the files that are
    relevant to the runtime settings and not every file in the directory
    """
    config_overrides = {
        'LOOP_BY': 'INIT',
        'SERIES_ANALYSIS_RUNTIME_FREQ': 'RUN_ONCE',
        'INIT_TIME_FMT': '%Y%m%d',
        'INIT_BEG': '20141214',
        'INIT_END': '20141214',
        'INIT_INCREMENT': '12H',
        'LEAD_SEQ': '0H, 6H, 12H',
    }
    wrapper = series_analysis_wrapper(metplus_config, config_overrides)

    stat_input_dir, tile_input_dir = get_input_dirs(wrapper.config)
    stat_input_template = 'another_fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template

    fcst_input_dir = os.path.join(tile_input_dir, 'fcst')
    obs_input_dir = os.path.join(tile_input_dir, 'obs')

    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = obs_input_dir

    if time_info['storm_id'] == '*':
        wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = False
    else:
        wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = True

    wrapper.c_dict['ALL_FILES'] = wrapper.get_all_files()
    print(f"ALL FILES: {wrapper.c_dict['ALL_FILES']}")
    expected_fcst = [
        'fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    if time_info['storm_id'] != '*':
        expected_fcst = [item for item in expected_fcst
                         if time_info['storm_id'] in item]
    expected_fcst_files = []
    for expected in expected_fcst:
        expected_fcst_files.append(os.path.join(tile_input_dir, expected))


    expected_obs = [
        'obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
        'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
        'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    if time_info['storm_id'] != '*':
        expected_obs = [item for item in expected_obs
                        if time_info['storm_id'] in item]
    expected_obs_files = []
    for expected in expected_obs:
        expected_obs_files.append(os.path.join(tile_input_dir, expected))

    fcst_key, obs_key = wrapper._get_fcst_obs_keys(time_info['storm_id'])
    fcst_files = [item[fcst_key] for item in wrapper.c_dict['ALL_FILES']
                  if fcst_key in item]
    obs_files = [item[obs_key] for item in wrapper.c_dict['ALL_FILES']
                 if obs_key in item]
    # convert list of lists into a single list to compare to expected results
    fcst_files = [item for sub in fcst_files for item in sub]
    obs_files = [item for sub in obs_files for item in sub]
    fcst_files.sort()
    obs_files.sort()
    assert fcst_files == expected_fcst_files
    assert obs_files == expected_obs_files

    list_file_dict = wrapper.subset_input_files(time_info)
    fcst_files_sub = []
    obs_files_sub = []
    for key, value in list_file_dict.items():
        if key.startswith('fcst'):
            with open(value, 'r') as file_handle:
                fcst_files_sub.extend(file_handle.read().splitlines()[1:])
        if key.startswith('obs'):
            with open(value, 'r') as file_handle:
                obs_files_sub.extend(file_handle.read().splitlines()[1:])
    fcst_files_sub.sort()
    obs_files_sub.sort()
    assert fcst_files_sub and obs_files_sub
    assert len(fcst_files_sub) == len(obs_files_sub)

    for actual_file, expected_file in zip(fcst_files_sub, expect_fcst_subset):
        assert actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file

    for actual_file, expected_file in zip(obs_files_sub, expect_obs_subset):
        assert actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file


@pytest.mark.parametrize(
        'config_overrides, time_info, storm_id, lead_group, expect_fcst_subset, expect_obs_subset', [
        # 0: filter by init all storms
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitallstorms'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         '*',
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',]),
        # 1: filter by init single storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitstormA'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         'ML1201072014',
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # 2: filter by init another single storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitstormB'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         'ML1221072014',
         None,
         ['fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # 3: filter by lead all storms
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadallstorms'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         '*',
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # 4: filter by lead 1 storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadstormA'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         'ML1201072014',
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # 5: filter by lead another storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadstormB'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         'ML1221072014',
         None,
         ['fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # 6: filter by lead groups A all storms
        ({'LEAD_SEQ_1': '0H, 6H',
          'LEAD_SEQ_1_LABEL': 'Group1',
          'LEAD_SEQ_2': '12H',
          'LEAD_SEQ_2_LABEL': 'Group2',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadgroupAallstorms'},
         {'init': '*',
          'valid': '*',
          },
         '*',
         ('Group1', [0, 21600]),
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
          'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # 7: filter by lead groups B all storms
        ({'LEAD_SEQ_1': '0H, 6H',
          'LEAD_SEQ_1_LABEL': 'Group1',
          'LEAD_SEQ_2': '12H',
          'LEAD_SEQ_2_LABEL': 'Group2',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadgroupBallstorms'},
         {'init': '*',
          'valid': '*',
          },
         '*',
         ('Group2', [43200]),
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
          'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
    ]
)
@pytest.mark.wrapper_a
def test_get_fcst_and_obs_path(metplus_config, config_overrides,
                               time_info, storm_id, lead_group,
                               expect_fcst_subset, expect_obs_subset):
    all_config_overrides = {
        'LOOP_BY': 'INIT',
        'SERIES_ANALYSIS_RUNTIME_FREQ': 'RUN_ONCE',
        'INIT_TIME_FMT': '%Y%m%d',
        'INIT_BEG': '20141214',
        'INIT_END': '20141214',
        'INIT_INCREMENT': '12H',
    }
    all_config_overrides.update(config_overrides)
    wrapper = series_analysis_wrapper(metplus_config, all_config_overrides)
    stat_input_dir, tile_input_dir = get_input_dirs(wrapper.config)
    fcst_input_dir = os.path.join(tile_input_dir, 'fcst')
    obs_input_dir = os.path.join(tile_input_dir, 'obs')

    stat_input_template = 'another_fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template
    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = obs_input_dir
    test_out_dirname = wrapper.config.getstr('config', 'TEST_OUTPUT_DIRNAME')
    output_dir = os.path.join(wrapper.config.getdir('OUTPUT_BASE'),
                              'series_by', 'output', test_out_dirname)
    wrapper.c_dict['OUTPUT_DIR'] = output_dir

    fcst_id, obs_id = wrapper._get_fcst_obs_keys(storm_id)

    # read output files and compare to expected list
    if storm_id == '*':
        storm_dir = 'all_storms'
        wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = False
    else:
        storm_dir = storm_id
        wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = True

    assert wrapper.get_all_files()

    templates = config_overrides['SERIES_ANALYSIS_OUTPUT_TEMPLATE'].split('/')
    if len(templates) == 1:
        output_prefix = ''
    else:
        output_prefix = os.path.join('20141214_00', storm_dir)

    fcst_list_file = wrapper.get_list_file_name(time_info, fcst_id)
    fcst_file_path = os.path.join(output_dir, output_prefix, fcst_list_file)
    if os.path.exists(fcst_file_path):
        os.remove(fcst_file_path)

    obs_list_file = wrapper.get_list_file_name(time_info, obs_id)
    obs_file_path = os.path.join(output_dir, output_prefix, obs_list_file)
    if os.path.exists(obs_file_path):
        os.remove(obs_file_path)

    fcst_path, obs_path = wrapper._get_fcst_and_obs_path(time_info,
                                                         storm_id,
                                                         lead_group)
    assert fcst_path == fcst_file_path and obs_path == obs_file_path

    with open(fcst_file_path, 'r') as file_handle:
        actual_fcsts = file_handle.readlines()
    actual_fcsts = [item.strip() for item in actual_fcsts[1:]]

    assert len(actual_fcsts) == len(expect_fcst_subset)
    for actual_file, expected_file in zip(actual_fcsts, expect_fcst_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert actual_file == expected_file

    with open(obs_file_path, 'r') as file_handle:
        actual_obs_files = file_handle.readlines()
    actual_obs_files = [item.strip() for item in actual_obs_files[1:]]

    assert len(actual_obs_files) == len(expect_obs_subset)
    for actual_file, expected_file in zip(actual_obs_files, expect_obs_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert actual_file == expected_file


@pytest.mark.parametrize(
        # no storm ID, label
        'template, storm_id, label, expected_result', [
        ('{init?fmt=%Y%m%d_%H}/{storm_id}_{label}/series_{fcst_name}_{fcst_level}.nc',
         '*', 'Label1', '20141031_12/all_storms_Label1'),
        # storm ID, label
        ('{init?fmt=%Y%m%d_%H}/{storm_id}_{label}/series_{fcst_name}_{fcst_level}.nc',
         'ML1221072014', 'Label1', '20141031_12/ML1221072014_Label1'),
        # no storm ID, no label
        ('{init?fmt=%Y%m%d_%H}/{storm_id}_{label}/series_{fcst_name}_{fcst_level}.nc',
         '*', '', '20141031_12/all_storms_'),
        # storm ID, no label
        ('{init?fmt=%Y%m%d_%H}/{storm_id}_{label}/series_{fcst_name}_{fcst_level}.nc',
         'ML1221072014', '', '20141031_12/ML1221072014_'),
    ]
)
@pytest.mark.wrapper_a
def test_get_output_dir(metplus_config, template, storm_id, label, expected_result):
    time_info = {'init': datetime(2014, 10, 31, 12, 15),
                 'valid': datetime(2014, 10, 31, 18, 15),
                 'lead': relativedelta(hours=6),}
    wrapper = series_analysis_wrapper(metplus_config)
    output_dir = '/some/fake/output/dir'
    wrapper.c_dict['OUTPUT_DIR'] = output_dir
    wrapper.c_dict['OUTPUT_TEMPLATE'] = template
    actual_result = wrapper.get_output_dir(time_info, storm_id, label)
    assert(actual_result == os.path.join(output_dir, expected_result))


@pytest.mark.parametrize(
    'data,expected_min,expected_max,variable_name', [
        (   [ 
            [[1, 2], [3, 4], [5, 6]],
            [[2, 3], [4, 5], [6, 7]],
            [[30, 31], [33, 32], [34, 39]],
            ],
            1,
            39,
            'Temp'
         ),
        (
            [ 
            [[1, 1], [1, 1], [1, 1]]
            ],
            1,
            1,
            'Temp'
         ),
            (
            [ 
            [[1, 1], [1, 1], [1, 1]]
            ],
            None,
            None,
            'Foo'
         ),            
    ]
    
)
@pytest.mark.wrapper_a
def test_get_netcdf_min_max(tmp_path_factory,
                            metplus_config,
                            make_dummy_nc,
                            data,
                            expected_min,
                            expected_max,
                            variable_name):

    filepath = make_dummy_nc(
        tmp_path_factory.mktemp("data1"),
        [359, 0, 1],
        [-1, 0, 1],
        [0, 1],
        data,
        "Temp"
    )
     
    wrapper = series_analysis_wrapper(metplus_config)

    min, max = wrapper._get_netcdf_min_max(filepath, variable_name)
    assert min == expected_min
    assert max == expected_max


@pytest.mark.wrapper_a
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'SeriesAnalysisConfig_wrapped')

    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'SERIES_ANALYSIS_CONFIG_FILE', fake_config_name)
    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name


@pytest.mark.wrapper_a
def test_run_once_per_lead(metplus_config):
    config = metplus_config
    set_minimum_config_settings(config)
    wrapper = SeriesAnalysisWrapper(config)

    # basic test
    actual = wrapper.run_once_per_lead(None)
    assert wrapper.isOK
    assert actual is True

    # lead_hours = None
    with mock.patch.object(saw, 'ti_get_hours_from_lead', return_value=None):
        actual = wrapper.run_once_per_lead(None)
    assert actual is True

    # run_at_time_once returns a failure
    with mock.patch.object(wrapper, 'run_at_time_once', return_value=None):
        actual = wrapper.run_once_per_lead(None)
    assert actual is False


@pytest.mark.wrapper_a
def test_get_fcst_obs_not_embedding(metplus_config):
    config = metplus_config
    set_minimum_config_settings(config)
    wrapper = SeriesAnalysisWrapper(config)
    with mock.patch.object(wrapper, "_check_python_embedding", return_value=False):
        actual = wrapper._get_fcst_and_obs_path({}, '*', None) 
    assert actual == (None, None)


@pytest.mark.parametrize(
    'lead_group, use_both, mock_exists, expected', [
        (('Group1', [0, 21600]), True, True, ('both_path', 'both_path')),
        (('F012', [relativedelta(hours=12)]), True, False, (None, None)),
        (('Group2', [0, 200]), False, True, ('fcst_path', 'obs_path')),
        ((None, [0, 200]), False, False, (None, None)),
    ]
)
@pytest.mark.wrapper_a
def test_get_fcst_and_obs_path(metplus_config,
                           lead_group,
                           use_both,
                           mock_exists,
                           expected):
    config = metplus_config
    set_minimum_config_settings(config)
    wrapper = SeriesAnalysisWrapper(config)
    wrapper.c_dict['EXPLICIT_FILE_LIST'] = True
    wrapper.c_dict['FCST_INPUT_FILE_LIST'] = 'fcst_path'
    wrapper.c_dict['OBS_INPUT_FILE_LIST'] = 'obs_path'
    wrapper.c_dict['BOTH_INPUT_FILE_LIST'] = 'both_path'
    wrapper.c_dict['USING_BOTH'] = use_both

    time_info = {'loop_by': 'init',
                 'init': datetime(2005, 8, 7, 0, 0),
                 'instance': '',
                 'valid': '*',
                 'lead': '*',
                 'lead_string':'ALL',
                 'date': datetime(2005, 8, 7, 0, 0),
                 'storm_id': '*'}

    if mock_exists:
        with mock.patch.object(os.path, "exists", return_value=True):
            actual = wrapper._get_fcst_and_obs_path(time_info, '*', lead_group) 
    else:
        actual = wrapper._get_fcst_and_obs_path(time_info, '*', lead_group) 
    assert actual == expected

