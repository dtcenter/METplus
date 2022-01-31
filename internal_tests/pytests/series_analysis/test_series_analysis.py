import pytest
import os
import sys
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

import produtil

from metplus.util import ti_get_seconds_from_lead, sub_var_list
from metplus.wrappers.series_analysis_wrapper import SeriesAnalysisWrapper

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
                                 'internal_tests',
                                 'data')
    stat_input_dir = os.path.join(fake_data_dir,
                                  'stat_data')
    tile_input_dir = os.path.join(fake_data_dir,
                                  'tiles')
    return stat_input_dir, tile_input_dir

def series_analysis_wrapper(metplus_config, config_overrides=None):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'series_test.conf'))
    config = metplus_config(extra_configs)
    config.set('config', 'LOOP_ORDER', 'processes')
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
    config.set('config', 'LOOP_ORDER', 'processes')
    config.set('config', 'SERIES_ANALYSIS_RUNTIME_FREQ',
               'RUN_ONCE_PER_INIT_OR_VALID')
    config.set('config', 'SERIES_ANALYSIS_CONFIG_FILE',
               '{PARM_BASE}/met_config/SeriesAnalysisConfig_wrapped')
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_SERIES_ANALYSIS_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'SERIES_ANALYSIS_OUTPUT_DIR',
               '{OUTPUT_BASE}/GridStat/output')
    config.set('config', 'SERIES_ANALYSIS_OUTPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)

    config.set('config', 'SERIES_ANALYSIS_STAT_LIST', stat_list)


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # climo_mean
        ({'SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

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
                                      'hour_interval = 12;}'),
          'CLIMO_MEAN_FILE': '"/some/climo_mean/file.txt"'}),

        # climo stdev
        ({'SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),

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
                                      'hour_interval = 12;}'),
          'CLIMO_STDEV_FILE': '"/some/climo_stdev/file.txt"'}),
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

    ]
)
def test_series_analysis_single_field(metplus_config, config_overrides,
                                      env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"

    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} "
                      f"-fcst {out_dir}/FCST_FILES "
                      f"-obs {out_dir}/OBS_FILES "
                      f"-out {out_dir}/2005080700 "
                      f"-config {config_file} {verbosity}"),
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
            print(f"ENV VAR: {env_var_key}")
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert(actual_value == fcst_fmt)
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert (actual_value == obs_fmt)
            elif env_var_key == 'METPLUS_OUTPUT_STATS_DICT' and 'METPLUS_OUTPUT_STATS_DICT' not in env_var_values:
                assert (actual_value == stat_list_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == actual_value)

def test_get_fcst_file_info(metplus_config):
    """ Verify that the tuple created by get_fcst_file_info is
        not an empty tuple, and that the number, beginning
        fcst file and end fcst file are what we expected.
    """
    storm_id = 'ML1200942014'
    expected_num = str(9)
    expected_beg = '000'
    expected_end = '048'

    time_info = {'storm_id': storm_id, 'lead': 0, 'valid': '', 'init': ''}

    wrapper = series_analysis_wrapper(metplus_config)
    wrapper.c_dict['FCST_INPUT_DIR'] = '/fake/path/of/file'
    wrapper.c_dict['FCST_INPUT_TEMPLATE'] = (
        "FCST_TILE_F{lead?fmt=%3H}_gfs_4_{init?fmt=%Y%m%d}_"
        "{init?fmt=%H}00_000.nc"
    )

    output_dir = (
        os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                     'internal_tests',
                     'data',
                     'file_lists')
    )
    output_filename = f"FCST_FILES_{storm_id}"
    fcst_path = os.path.join(output_dir, output_filename)

    num, beg, end = wrapper.get_fcst_file_info(fcst_path)
    assert num == expected_num
    assert beg == expected_beg
    assert end == expected_end

def test_get_storms_list(metplus_config):
    """Verify that the expected number of storms
       are found for the init time 20141214_00
    """
    config = metplus_config()

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

# added list of all files for reference for creating subsets
all_fake_fcst = ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F000_gfs_4_20141215_0000_000.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F006_gfs_4_20141215_0000_006.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F012_gfs_4_20141215_0000_012.nc',
                  ]
all_fake_obs = ['obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'obs/20141215_00/ML1291072014/OBS_TILE_F000_gfs_4_20141215_0000_000.nc',
                 'obs/20141215_00/ML1291072014/OBS_TILE_F006_gfs_4_20141215_0000_006.nc',
                 'obs/20141215_00/ML1291072014/OBS_TILE_F012_gfs_4_20141215_0000_012.nc',
                  ]
@pytest.mark.parametrize(
        'time_info, expect_fcst_subset, expect_obs_subset', [
        # filter by init all storms
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': '*'},
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
        # filter by init single storm
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
        # filter by init another single storm
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
        # filter by lead all storms
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

    wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = True
    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template

    fcst_input_dir = os.path.join(tile_input_dir,
                                  'fcst')
    obs_input_dir = os.path.join(tile_input_dir,
                                 'obs')

    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = obs_input_dir

    assert(wrapper.get_all_files())

    expected_fcst = [
        'fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    expected_fcst_files = []
    for expected in expected_fcst:
        expected_fcst_files.append(os.path.join(tile_input_dir, expected))


    expected_obs = [
        'obs/20141214_00/ML1201072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F000_gfs_4_20141214_0000_000.nc',
        'obs/20141214_00/ML1201072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F006_gfs_4_20141214_0000_006.nc',
        'obs/20141214_00/ML1201072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
        'obs/20141214_00/ML1221072014/OBS_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    expected_obs_files = []
    for expected in expected_obs:
        expected_obs_files.append(os.path.join(tile_input_dir, expected))

    # convert list of lists into a single list to compare to expected results
    fcst_files = [item['fcst'] for item in wrapper.c_dict['ALL_FILES']]
    fcst_files = [item for sub in fcst_files for item in sub]
    obs_files = [item['obs'] for item in wrapper.c_dict['ALL_FILES']]
    obs_files = [item for sub in obs_files for item in sub]

    assert(fcst_files == expected_fcst_files)
    assert(obs_files == expected_obs_files)

    fcst_files_sub, obs_files_sub = wrapper.subset_input_files(time_info)
    assert(fcst_files_sub and obs_files_sub)
    assert(len(fcst_files_sub) == len(obs_files_sub))

    for actual_file, expected_file in zip(fcst_files_sub, expect_fcst_subset):
        assert(actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file)

    for actual_file, expected_file in zip(obs_files_sub, expect_obs_subset):
        assert(actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file)

@pytest.mark.parametrize(
        'config_overrides, time_info, storm_id, lead_group, expect_fcst_subset, expect_obs_subset', [
        # filter by init all storms
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
        # filter by init single storm
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
        # filter by init another single storm
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
        # filter by lead all storms
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
        # filter by lead 1 storm
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
        # filter by lead another storm
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
        # filter by lead groups A all storms
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
        # filter by lead groups B all storms
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
    fcst_input_dir = os.path.join(tile_input_dir,
                                  'fcst')
    obs_input_dir = os.path.join(tile_input_dir,
                                 'obs')

    stat_input_template = 'another_fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template
    wrapper.c_dict['RUN_ONCE_PER_STORM_ID'] = True
    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = obs_input_dir
    test_out_dirname = wrapper.config.getstr('config', 'TEST_OUTPUT_DIRNAME')
    output_dir = os.path.join(wrapper.config.getdir('OUTPUT_BASE'),
                              'series_by',
                              'output',
                              test_out_dirname)
    wrapper.c_dict['OUTPUT_DIR'] = output_dir

    assert(wrapper.get_all_files())

    # read output files and compare to expected list
    if storm_id == '*':
        storm_dir = 'all_storms'
    else:
        storm_dir = storm_id

    templates = config_overrides['SERIES_ANALYSIS_OUTPUT_TEMPLATE'].split('/')
    if len(templates) == 1:
        output_prefix = ''
    else:
        output_prefix = os.path.join('20141214_00', storm_dir)

    if lead_group:
        leads = lead_group[1]
    else:
        leads = None
    fcst_list_file = wrapper._get_ascii_filename('FCST', storm_id, leads)
    fcst_file_path = os.path.join(output_dir,
                                  output_prefix,
                                  fcst_list_file)
    if os.path.exists(fcst_file_path):
        os.remove(fcst_file_path)

    obs_list_file = wrapper._get_ascii_filename('OBS', storm_id, leads)
    obs_file_path = os.path.join(output_dir,
                                  output_prefix,
                                  obs_list_file)
    if os.path.exists(obs_file_path):
        os.remove(obs_file_path)

    fcst_path, obs_path = wrapper._get_fcst_and_obs_path(time_info,
                                                         storm_id,
                                                         lead_group)
    assert(fcst_path == fcst_file_path and obs_path == obs_file_path)

    with open(fcst_file_path, 'r') as file_handle:
        actual_fcsts = file_handle.readlines()
    actual_fcsts = [item.strip() for item in actual_fcsts[1:]]

    for actual_file, expected_file in zip(actual_fcsts, expect_fcst_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert(actual_file == expected_file)

    with open(obs_file_path, 'r') as file_handle:
        actual_obs_files = file_handle.readlines()
    actual_obs_files = [item.strip() for item in actual_obs_files[1:]]

    for actual_file, expected_file in zip(actual_obs_files, expect_obs_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert(actual_file == expected_file)

@pytest.mark.parametrize(
        'storm_id, leads, expected_result', [
        # storm ID, no leads
        ('ML1221072014', None, '_FILES_ML1221072014'),
        # no storm ID no leads
        ('*', None, '_FILES'),
        # storm ID, 1 lead
        ('ML1221072014', [relativedelta(hours=12)], '_FILES_ML1221072014_F012'),
        # no storm ID, 1 lead
        ('*', [relativedelta(hours=12)], '_FILES_F012'),
        # storm ID, 2 leads
        ('ML1221072014', [relativedelta(hours=18),
                                  relativedelta(hours=12)],
         '_FILES_ML1221072014_F012_to_F018'),
        # no storm ID, 2 leads
        ('*', [relativedelta(hours=18),
                       relativedelta(hours=12)],
         '_FILES_F012_to_F018'),
        # storm ID, 3 leads
        ('ML1221072014', [relativedelta(hours=15),
                                  relativedelta(hours=18),
                                  relativedelta(hours=12)],
         '_FILES_ML1221072014_F012_to_F018'),
        # no storm ID, 3 leads
        ('*', [relativedelta(hours=15),
                       relativedelta(hours=18),
                       relativedelta(hours=12)],
         '_FILES_F012_to_F018'),
    ]
)
def test_get_ascii_filename(metplus_config, storm_id, leads,
                            expected_result):
    wrapper = series_analysis_wrapper(metplus_config)
    for data_type in ['FCST', 'OBS']:
        actual_result = wrapper._get_ascii_filename(data_type,
                                                   storm_id,
                                                   leads)
        assert(actual_result == f"{data_type}{expected_result}")

        if leads is None:
            return

        lead_seconds = [ti_get_seconds_from_lead(item) for item in leads]
        actual_result = wrapper._get_ascii_filename(data_type,
                                                   storm_id,
                                                   lead_seconds)
        assert(actual_result == f"{data_type}{expected_result}")
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

def test_get_netcdf_min_max(metplus_config):
    expected_min = 0.0
    expected_max = 8.0

    wrapper = series_analysis_wrapper(metplus_config)
    met_install_dir = wrapper.config.getdir('MET_INSTALL_DIR')
    filepath = os.path.join(met_install_dir,
                            'share',
                            'met',
                            'tc_data',
                            'basin_global_tenth_degree.nc')
    variable_name = 'basin'
    min, max = wrapper._get_netcdf_min_max(filepath, variable_name)
    assert(min == expected_min)
    assert(max == expected_max)

def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config()
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'SeriesAnalysisConfig_wrapped')

    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'SERIES_ANALYSIS_CONFIG_FILE', fake_config_name)
    wrapper = SeriesAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
