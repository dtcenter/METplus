#!/usr/bin/env python3

import pytest

import os

from datetime import datetime


from metplus.wrappers.ensemble_stat_wrapper import EnsembleStatWrapper

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'
ens_mean_dir = '/some/path/ens_mean'
ens_mean_template = 'the_ens_mean_file.nc'
obs_point_template = 'point_obs.nc'
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


def set_minimum_config_settings(config, set_fields=True):
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
    config.set('config', 'OBS_ENSEMBLE_STAT_GRID_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'ENSEMBLE_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/EnsembleStat/output')
    config.set('config', 'ENSEMBLE_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    if set_fields:
        config.set('config', 'FCST_VAR1_NAME', fcst_name)
        config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
        config.set('config', 'OBS_VAR1_NAME', obs_name)
        config.set('config', 'OBS_VAR1_LEVELS', obs_level)


@pytest.mark.parametrize(
    'config_overrides, expected_filename', [
        # 0 - set forecast level
        ({'FCST_VAR1_NAME': 'fcst_file',
          'FCST_VAR1_LEVELS': 'A06',
          'OBS_VAR1_NAME': 'obs_file',
          'OBS_VAR1_LEVELS': 'A06',
          'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE': '{fcst_name}_A{level?fmt=%3H}',
          },
         f'{fcst_dir}/fcst_file_A006'),
        # 1 - don't set forecast level
        ({'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE': 'fcst_file_A{level?fmt=%3H}'},
         f'{fcst_dir}/fcst_file_A000'),
    ]
)
@pytest.mark.wrapper_c
def test_ensemble_stat_level_in_template(metplus_config, config_overrides,
                                         expected_filename):

    config = metplus_config

    set_minimum_config_settings(config, set_fields=False)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert wrapper.isOK

    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    file_list_file = f"{file_list_dir}/20050807000000_12_ensemble_stat.txt"
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    wrapper.run_all_times()
    assert os.path.exists(file_list_file)
    with open(file_list_file, 'r') as file_handle:
        filenames = file_handle.read().splitlines()[1:]
    assert len(filenames) == 1
    assert filenames[0] == expected_filename


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0 : no ens, 1 fcst, 1 obs
        ({'FCST_VAR1_NAME': 'fcst_name_1',
          'FCST_VAR1_LEVELS': 'FCST_LEVEL_1',
          'OBS_VAR1_NAME': 'obs_name_1',
          'OBS_VAR1_LEVELS': 'OBS_LEVEL_1',
          },
         {'METPLUS_FCST_FIELD': ('field = ['
                                 '{ name="fcst_name_1"; level="FCST_LEVEL_1"; }'
                                 '];'),
          'METPLUS_OBS_FIELD': ('field = ['
                                '{ name="obs_name_1"; level="OBS_LEVEL_1"; }'
                                '];'),
          }),
    ]
)
@pytest.mark.wrapper_c
def test_ensemble_stat_field_info(metplus_config, config_overrides,
                                  env_var_values):

    config = metplus_config

    set_minimum_config_settings(config, set_fields=False)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()

    assert len(all_cmds) == 2

    actual_env_vars = all_cmds[0][1]
    for key, expected_value in env_var_values.items():
        match = next((item for item in actual_env_vars if
                      item.startswith(key)), None)
        assert match is not None
        actual_value = match.split('=', 1)[1]
        assert actual_value == expected_value
        print(f"ACTUAL  : {actual_value}")
        print(f"EXPECTED: {expected_value}")


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
@pytest.mark.wrapper_c
def test_handle_climo_file_variables(metplus_config, config_overrides,
                                     env_var_values):
    """! Ensure that old and new variables for setting climo_mean and
     climo_stdev are set to the correct values
    """
    old_env_vars = ['CLIMO_MEAN_FILE',
                    'CLIMO_STDEV_FILE']
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    assert len(all_cmds) == len(run_times)
    for (_, actual_env_vars), run_time in zip(all_cmds, run_times):
        run_dt = datetime.strptime(run_time, time_fmt)
        ymdh = run_dt.strftime('%Y%m%d%H')
        print(f"ACTUAL ENV VARS: {actual_env_vars}")
        for old_env in old_env_vars:
            match = next((item for item in actual_env_vars if
                          item.startswith(old_env)), None)
            assert match is not None
            actual_value = match.split('=', 1)[1]
            expected_value = env_var_values.get(old_env, '')
            expected_value = expected_value.replace('YMDH', ymdh)
            assert expected_value == actual_value


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
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}',
          'REGRID_TO_GRID': 'FCST'}),

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
                                  ),
          'REGRID_TO_GRID': 'FCST'}),

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
              'poly = ["one", "two"];',
          }),
        # 13 mask grid and poly (new config var)
        ({'ENSEMBLE_STAT_MASK_GRID': 'FULL',
          'ENSEMBLE_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          'METPLUS_MASK_POLY':
              'poly = ["one", "two"];',
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
              'poly = ["one", "two"];',
          }),
        # 27 mask poly (new config var)
        ({'ENSEMBLE_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one", "two"];',
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

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_PCT': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pct = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_PSTD': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pstd = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_PJC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pjc = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_PRC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {prc = STAT;}'}),

        ({'ENSEMBLE_STAT_OUTPUT_FLAG_ECLV': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {eclv = STAT;}'}),

        ({
             'ENSEMBLE_STAT_OUTPUT_FLAG_ECNT': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RPS': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RHIST': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PHIST': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_ORANK': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_RELP': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PCT': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PSTD': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PJC': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_PRC': 'STAT',
             'ENSEMBLE_STAT_OUTPUT_FLAG_ECLV': 'STAT',
         },
         {
             'METPLUS_OUTPUT_FLAG_DICT': ('output_flag = {ecnt = STAT;'
                                          'rps = STAT;rhist = STAT;'
                                          'phist = STAT;orank = STAT;'
                                          'ssvar = STAT;relp = STAT;'
                                          'pct = STAT;pstd = STAT;'
                                          'pjc = STAT;prc = STAT;eclv = STAT;'
                                          '}')}),
        # nc_orank_flag
        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_LATLON': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {latlon = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_MEAN': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {mean = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_RAW': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {raw = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_RANK': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {rank = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_PIT': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {pit = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_VLD_COUNT': 'True', },
         {
             'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {vld_count = TRUE;}'}),

        ({'ENSEMBLE_STAT_NC_ORANK_FLAG_WEIGHT': 'True', },
         {'METPLUS_NC_ORANK_FLAG_DICT': 'nc_orank_flag = {weight = TRUE;}'}),

        ({
             'ENSEMBLE_STAT_NC_ORANK_FLAG_LATLON': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_MEAN': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_RAW': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_RANK': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_PIT': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_VLD_COUNT': 'True',
             'ENSEMBLE_STAT_NC_ORANK_FLAG_WEIGHT': 'True',
         },
         {
             'METPLUS_NC_ORANK_FLAG_DICT': ('nc_orank_flag = {latlon = TRUE;'
                                            'mean = TRUE;raw = TRUE;'
                                            'rank = TRUE;pit = TRUE;'
                                            'vld_count = TRUE;'
                                            'weight = TRUE;}')
         }),

        # climo_cdf dictionary
        ({'ENSEMBLE_STAT_CLIMO_CDF_CDF_BINS': '1', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;}'}),

        ({'ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS': 'True', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {center_bins = TRUE;}'}),

        ({'ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {write_bins = FALSE;}'}),

        ({'ENSEMBLE_STAT_CLIMO_CDF_DIRECT_PROB': 'False', },
         {'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {direct_prob = FALSE;}'}),

        ({
             'ENSEMBLE_STAT_CLIMO_CDF_CDF_BINS': '1',
             'ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS': 'True',
             'ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS': 'False',
             'ENSEMBLE_STAT_CLIMO_CDF_DIRECT_PROB': 'False',
         },
         {
             'METPLUS_CLIMO_CDF_DICT': 'climo_cdf = {cdf_bins = 1.0;center_bins = TRUE;write_bins = FALSE;direct_prob = FALSE;}'}),

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
        ({'ENSEMBLE_STAT_OBS_QUALITY_INC': '2,3,4', },
         {'METPLUS_OBS_QUALITY_INC': 'obs_quality_inc = ["2", "3", "4"];'}),
        ({'ENSEMBLE_STAT_OBS_QUALITY_EXC': '5,6,7', },
         {'METPLUS_OBS_QUALITY_EXC': 'obs_quality_exc = ["5", "6", "7"];'}),

        ({'ENSEMBLE_STAT_ENS_MEMBER_IDS': '1,2,3,4', },
         {'METPLUS_ENS_MEMBER_IDS': 'ens_member_ids = ["1", "2", "3", "4"];'}),

        ({'ENSEMBLE_STAT_CONTROL_ID': '0', },
         {'METPLUS_CONTROL_ID': 'control_id = "0";'}),

        ({'ENSEMBLE_STAT_GRID_WEIGHT_FLAG': 'COS_LAT', },
         {'METPLUS_GRID_WEIGHT_FLAG': 'grid_weight_flag = COS_LAT;'}),

        ({'ENSEMBLE_STAT_PROB_CAT_THRESH': '<=0.25', },
         {'METPLUS_PROB_CAT_THRESH': 'prob_cat_thresh = [<=0.25];'}),

        ({'ENSEMBLE_STAT_PROB_PCT_THRESH': '==0.25', },
         {'METPLUS_PROB_PCT_THRESH': 'prob_pct_thresh = [==0.25];'}),

        ({'ENSEMBLE_STAT_ECLV_POINTS': '0.05', },
         {'METPLUS_ECLV_POINTS': 'eclv_points = 0.05;'}),

        ({'ENSEMBLE_STAT_ENS_THRESH': '0.1', },
         {'METPLUS_ENS_THRESH': 'ens_thresh = 0.1;'}),

        ({'ENSEMBLE_STAT_VLD_THRESH': '0.5', },
         {'METPLUS_VLD_THRESH': 'vld_thresh = 0.5;'}),

        ({'ENSEMBLE_STAT_OBS_THRESH': 'NA, 0.5', },
         {'METPLUS_OBS_THRESH': 'obs_thresh = [NA, 0.5];'}),

        ({'ENSEMBLE_STAT_ENS_MEAN_INPUT_DIR': ens_mean_dir,
          'ENSEMBLE_STAT_ENS_MEAN_INPUT_TEMPLATE': ens_mean_template},
         {}),

        ({'OBS_ENSEMBLE_STAT_POINT_INPUT_DIR': obs_dir,
          'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE': obs_point_template},
         {}),

        ({'ENSEMBLE_STAT_ENS_MEAN_INPUT_DIR': ens_mean_dir,
          'ENSEMBLE_STAT_ENS_MEAN_INPUT_TEMPLATE': ens_mean_template,
          'OBS_ENSEMBLE_STAT_POINT_INPUT_DIR': obs_dir,
          'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE': obs_point_template},
         {}),

    ]
)
@pytest.mark.wrapper_c
def test_ensemble_stat_single_field(metplus_config, config_overrides,
                                    env_var_values):

    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    point_obs = ' '
    ens_mean = ' '
    if 'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE' in config_overrides:
        point_obs = f' -point_obs "{obs_dir}/{obs_point_template}" '
    if 'ENSEMBLE_STAT_ENS_MEAN_INPUT_TEMPLATE' in config_overrides:
        ens_mean = f' -ens_mean {ens_mean_dir}/{ens_mean_template} '

    expected_cmds = [(f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807000000_12_ensemble_stat.txt "
                      f"{config_file}{point_obs}"
                      f'-grid_obs "{obs_dir}/2005080712/obs_file"{ens_mean}'
                      f"-outdir {out_dir}/2005080712"),
                     (f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807120000_12_ensemble_stat.txt "
                      f"{config_file}{point_obs}"
                      f'-grid_obs "{obs_dir}/2005080800/obs_file"{ens_mean}'
                      f"-outdir {out_dir}/2005080800"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

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
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert actual_value == fcst_fmt
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert actual_value == obs_fmt
            else:
                assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.wrapper_c
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'EnsembleStatConfig_wrapped')

    wrapper = EnsembleStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'ENSEMBLE_STAT_CONFIG_FILE', fake_config_name)
    wrapper = EnsembleStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name


@pytest.mark.parametrize(
    'config_overrides, expected_num_files', [
        ({}, 4),
        ({'ENSEMBLE_STAT_ENS_MEMBER_IDS': '1'}, 1),
    ]
)
@pytest.mark.wrapper_c
def test_ensemble_stat_fill_missing(metplus_config, config_overrides,
                                    expected_num_files):
    config = metplus_config

    set_minimum_config_settings(config)

    # change some config values for this test
    config.set('config', 'INIT_END', run_times[0])
    config.set('config', 'ENSEMBLE_STAT_N_MEMBERS', 4)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = EnsembleStatWrapper(config)

    file_list_file = os.path.join(wrapper.config.getdir('FILE_LISTS_DIR'),
                                  '20050807000000_12_ensemble_stat.txt')
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    all_cmds = wrapper.run_all_times()
    assert len(all_cmds) == 1

    with open(file_list_file, 'r') as file_handle:
        actual_num_files = len(file_handle.read().splitlines()) - 1

    assert actual_num_files == expected_num_files
