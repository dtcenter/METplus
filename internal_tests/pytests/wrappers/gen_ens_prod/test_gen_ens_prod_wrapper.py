#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.gen_ens_prod_wrapper import GenEnsProdWrapper

ens_name = 'REFC'
ens_level = 'L0'
ens_fmt = f'field = [{{ name="{ens_name}"; level="{ens_level}"; }}];'

time_fmt = '%Y%m%d%H'
run_times = ['2009123112', '2009123118']


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'GenEnsProd')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '6H')
    config.set('config', 'LEAD_SEQ', '24H, 48H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'GEN_ENS_PROD_CONFIG_FILE',
               '{PARM_BASE}/met_config/GenEnsProdConfig_wrapped')

    config.set('config', 'GEN_ENS_PROD_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/*gep*/d01_{init?fmt=%Y%m%d%H}_{lead?fmt=%3H}00.grib')
    config.set('config', 'GEN_ENS_PROD_CTRL_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/arw-tom-gep3/d01_{init?fmt=%Y%m%d%H}_{lead?fmt=%3H}00.grib')
    config.set('config', 'GEN_ENS_PROD_OUTPUT_DIR',
               '{OUTPUT_BASE}/GenEnsProd/output')
    config.set('config', 'GEN_ENS_PROD_OUTPUT_TEMPLATE',
               'gen_ens_prod_{valid?fmt=%Y%m%d_%H%M%S}V_ens.nc')

    config.set('config', 'ENS_VAR1_NAME', ens_name)
    config.set('config', 'ENS_VAR1_LEVELS', ens_level)


def handle_input_dir(config):
    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
    input_dir = os.path.join(test_data_dir, 'ens')
    config.set('config', 'GEN_ENS_PROD_INPUT_DIR', input_dir)
    config.set('config', 'GEN_ENS_PROD_CTRL_INPUT_DIR', input_dir)
    return input_dir


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),
        # 1
        ({'GEN_ENS_PROD_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),
        # 2
        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),
        # 3
        ({'GEN_ENS_PROD_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),
        # 4
        ({'GEN_ENS_PROD_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),
        # 5
        ({'GEN_ENS_PROD_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),
        # 6
        ({'GEN_ENS_PROD_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),
        # 7
        ({'GEN_ENS_PROD_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),
        # 8
        ({'GEN_ENS_PROD_REGRID_TO_GRID': 'FCST',
          'GEN_ENS_PROD_REGRID_METHOD': 'NEAREST',
          'GEN_ENS_PROD_REGRID_WIDTH': '1',
          'GEN_ENS_PROD_REGRID_VLD_THRESH': '0.5',
          'GEN_ENS_PROD_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;}'
                                  )}),
        # 9
        ({'GEN_ENS_PROD_CLIMO_MEAN_INPUT_TEMPLATE':
              '/some/path/climo/filename.nc',
          },
         {'METPLUS_CLIMO_MEAN_DICT':
              'climo_mean = {file_name = ["/some/path/climo/filename.nc"];}',
          }),
        # 10
        ({'GEN_ENS_PROD_CLIMO_STDEV_INPUT_TEMPLATE':
              '/some/path/climo/stdfile.nc',
          },
         {'METPLUS_CLIMO_STDEV_DICT':
              'climo_stdev = {file_name = ["/some/path/climo/stdfile.nc"];}',
         }),
        # 11 ensemble_flag
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_LATLON': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {latlon = FALSE;}'}),
        # 12
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_MEAN': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {mean = FALSE;}'}),
        # 13
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_STDEV': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {stdev = FALSE;}'}),
        # 14
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_MINUS': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {minus = FALSE;}'}),
        # 15
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_PLUS': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {plus = FALSE;}'}),
        # 16
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_MIN': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {min = FALSE;}'}),
        # 17
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_MAX': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {max = FALSE;}'}),
        # 18
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_RANGE': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {range = FALSE;}'}),
        # 19
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_VLD_COUNT': 'FALSE', },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {vld_count = FALSE;}'}),
        # 20
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_FREQUENCY': 'FALSE', },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {frequency = FALSE;}'}),
        # 21
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_NEP': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {nep = FALSE;}'}),
        # 22
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_NMEP': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {nmep = FALSE;}'}),
        # 23
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {climo = FALSE;}'}),
        # 24
        ({'GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO_CDP': 'FALSE', },
         {'METPLUS_ENSEMBLE_FLAG_DICT': 'ensemble_flag = {climo_cdp = FALSE;}'}),
        # 25
        ({
             'GEN_ENS_PROD_ENSEMBLE_FLAG_LATLON': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_MEAN': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_STDEV': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_MINUS': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_PLUS': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_MIN': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_MAX': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_RANGE': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_VLD_COUNT': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_FREQUENCY': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_NEP': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_NMEP': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO': 'FALSE',
             'GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO_CDP': 'FALSE',
         },
         {
             'METPLUS_ENSEMBLE_FLAG_DICT': ('ensemble_flag = {latlon = FALSE;'
                                            'mean = FALSE;stdev = FALSE;'
                                            'minus = FALSE;plus = FALSE;'
                                            'min = FALSE;max = FALSE;'
                                            'range = FALSE;vld_count = FALSE;'
                                            'frequency = FALSE;nep = FALSE;'
                                            'nmep = FALSE;climo = FALSE;'
                                            'climo_cdp = FALSE;}')}),
        # 26
        ({'GEN_ENS_PROD_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt', },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];}'),}),
        # 27
        ({'GEN_ENS_PROD_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # 28
        ({'GEN_ENS_PROD_CLIMO_MEAN_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {method = NEAREST;}}'}),
        # 29
        ({'GEN_ENS_PROD_CLIMO_MEAN_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {width = 1;}}'}),
        # 30
        ({'GEN_ENS_PROD_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {vld_thresh = 0.5;}}'}),
        # 31
        ({'GEN_ENS_PROD_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {regrid = {shape = SQUARE;}}'}),
        # 32
        ({'GEN_ENS_PROD_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {time_interp_method = NEAREST;}'}),
        # 33
        ({'GEN_ENS_PROD_CLIMO_MEAN_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {match_month = TRUE;}'}),
        # 34
        ({'GEN_ENS_PROD_CLIMO_MEAN_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {day_interval = 30;}'}),
        # 35
        ({'GEN_ENS_PROD_CLIMO_MEAN_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_MEAN_DICT': 'climo_mean = {hour_interval = 12;}'}),
        # 36
        ({
             'GEN_ENS_PROD_CLIMO_MEAN_FILE_NAME': '/some/climo_mean/file.txt',
             'GEN_ENS_PROD_CLIMO_MEAN_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'GEN_ENS_PROD_CLIMO_MEAN_REGRID_METHOD': 'NEAREST',
             'GEN_ENS_PROD_CLIMO_MEAN_REGRID_WIDTH': '1',
             'GEN_ENS_PROD_CLIMO_MEAN_REGRID_VLD_THRESH': '0.5',
             'GEN_ENS_PROD_CLIMO_MEAN_REGRID_SHAPE': 'SQUARE',
             'GEN_ENS_PROD_CLIMO_MEAN_TIME_INTERP_METHOD': 'NEAREST',
             'GEN_ENS_PROD_CLIMO_MEAN_MATCH_MONTH': 'True',
             'GEN_ENS_PROD_CLIMO_MEAN_DAY_INTERVAL': '30',
             'GEN_ENS_PROD_CLIMO_MEAN_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_MEAN_DICT': ('climo_mean = {file_name = '
                                      '["/some/climo_mean/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}')}),
        # 37 climo stdev
        ({'GEN_ENS_PROD_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt', },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];}')}),
        # 38
        ({'GEN_ENS_PROD_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {field = [{name="CLM_NAME"; level="(0,0,*,*)";}];}'}),
        # 39
        ({'GEN_ENS_PROD_CLIMO_STDEV_REGRID_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {method = NEAREST;}}'}),
        # 40
        ({'GEN_ENS_PROD_CLIMO_STDEV_REGRID_WIDTH': '1', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {width = 1;}}'}),
        # 41
        ({'GEN_ENS_PROD_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {vld_thresh = 0.5;}}'}),
        # 42
        ({'GEN_ENS_PROD_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {regrid = {shape = SQUARE;}}'}),
        # 43
        ({'GEN_ENS_PROD_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST', },
         {
             'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {time_interp_method = NEAREST;}'}),
        # 44
        ({'GEN_ENS_PROD_CLIMO_STDEV_MATCH_MONTH': 'True', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {match_month = TRUE;}'}),
        # 45
        ({'GEN_ENS_PROD_CLIMO_STDEV_DAY_INTERVAL': '30', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {day_interval = 30;}'}),
        # 46
        ({'GEN_ENS_PROD_CLIMO_STDEV_HOUR_INTERVAL': '12', },
         {'METPLUS_CLIMO_STDEV_DICT': 'climo_stdev = {hour_interval = 12;}'}),
        # 47
        ({
             'GEN_ENS_PROD_CLIMO_STDEV_FILE_NAME': '/some/climo_stdev/file.txt',
             'GEN_ENS_PROD_CLIMO_STDEV_FIELD': '{name="CLM_NAME"; level="(0,0,*,*)";}',
             'GEN_ENS_PROD_CLIMO_STDEV_REGRID_METHOD': 'NEAREST',
             'GEN_ENS_PROD_CLIMO_STDEV_REGRID_WIDTH': '1',
             'GEN_ENS_PROD_CLIMO_STDEV_REGRID_VLD_THRESH': '0.5',
             'GEN_ENS_PROD_CLIMO_STDEV_REGRID_SHAPE': 'SQUARE',
             'GEN_ENS_PROD_CLIMO_STDEV_TIME_INTERP_METHOD': 'NEAREST',
             'GEN_ENS_PROD_CLIMO_STDEV_MATCH_MONTH': 'True',
             'GEN_ENS_PROD_CLIMO_STDEV_DAY_INTERVAL': '30',
             'GEN_ENS_PROD_CLIMO_STDEV_HOUR_INTERVAL': '12',
         },
         {'METPLUS_CLIMO_STDEV_DICT': ('climo_stdev = {file_name = '
                                      '["/some/climo_stdev/file.txt"];'
                                      'field = [{name="CLM_NAME"; level="(0,0,*,*)";}];'
                                      'regrid = {method = NEAREST;width = 1;'
                                      'vld_thresh = 0.5;shape = SQUARE;}'
                                      'time_interp_method = NEAREST;'
                                      'match_month = TRUE;day_interval = 30;'
                                      'hour_interval = 12;}')}),
        # 48
        ({'GEN_ENS_PROD_NBRHD_PROB_WIDTH': '5', },
         {'METPLUS_NBRHD_PROB_DICT': 'nbrhd_prob = {width = [5];}'}),
        # 49
        ({'GEN_ENS_PROD_NBRHD_PROB_SHAPE': 'circle', },
         {'METPLUS_NBRHD_PROB_DICT': 'nbrhd_prob = {shape = CIRCLE;}'}),
        # 50
        ({'GEN_ENS_PROD_NBRHD_PROB_VLD_THRESH': '0.0', },
         {'METPLUS_NBRHD_PROB_DICT': 'nbrhd_prob = {vld_thresh = 0.0;}'}),
        # 51
        ({
             'GEN_ENS_PROD_NBRHD_PROB_WIDTH': '5',
             'GEN_ENS_PROD_NBRHD_PROB_SHAPE': 'CIRCLE',
             'GEN_ENS_PROD_NBRHD_PROB_VLD_THRESH': '0.0',
         },
         {
             'METPLUS_NBRHD_PROB_DICT': (
                     'nbrhd_prob = {width = [5];shape = CIRCLE;'
                     'vld_thresh = 0.0;}'
             )
         }),
        # 52
        ({'GEN_ENS_PROD_NMEP_SMOOTH_VLD_THRESH': '0.0', },
         {'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {vld_thresh = 0.0;}'}),
        # 53
        ({'GEN_ENS_PROD_NMEP_SMOOTH_SHAPE': 'circle', },
         {'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {shape = CIRCLE;}'}),
        # 54
        ({'GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_DX': '81.27', },
         {'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {gaussian_dx = 81.27;}'}),
        # 55
        ({'GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_RADIUS': '120', },
         {
             'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {gaussian_radius = 120;}'}),
        # 56
        ({'GEN_ENS_PROD_NMEP_SMOOTH_TYPE_METHOD': 'GAUSSIAN', },
         {'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {type = [{method = GAUSSIAN;}];}'}),
        # 57
        ({'GEN_ENS_PROD_NMEP_SMOOTH_TYPE_WIDTH': '1', },
         {'METPLUS_NMEP_SMOOTH_DICT': 'nmep_smooth = {type = [{width = 1;}];}'}),
        # 58
        ({
             'GEN_ENS_PROD_NMEP_SMOOTH_VLD_THRESH': '0.0',
             'GEN_ENS_PROD_NMEP_SMOOTH_SHAPE': 'circle',
             'GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_DX': '81.27',
             'GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_RADIUS': '120',
             'GEN_ENS_PROD_NMEP_SMOOTH_TYPE_METHOD': 'GAUSSIAN',
             'GEN_ENS_PROD_NMEP_SMOOTH_TYPE_WIDTH': '1',
         },
         {
             'METPLUS_NMEP_SMOOTH_DICT': (
                     'nmep_smooth = {vld_thresh = 0.0;shape = CIRCLE;'
                     'gaussian_dx = 81.27;gaussian_radius = 120;'
                     'type = [{method = GAUSSIAN;width = 1;}];}'
             )
         }),
        # 59
        ({'GEN_ENS_PROD_ENS_MEMBER_IDS': '1,2,3,4', },
         {'METPLUS_ENS_MEMBER_IDS': 'ens_member_ids = ["1", "2", "3", "4"];'}),
        # 60
        ({'GEN_ENS_PROD_CONTROL_ID': '0', },
         {'METPLUS_CONTROL_ID': 'control_id = "0";'}),
        # 61
        ({'GEN_ENS_PROD_NORMALIZE': 'CLIMO_STD_ANOM', },
         {'METPLUS_NORMALIZE': 'normalize = CLIMO_STD_ANOM;'}),

    ]
)
@pytest.mark.wrapper
def test_gen_ens_prod_single_field(metplus_config, config_overrides,
                                   env_var_values):

    config = metplus_config()

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    input_dir = handle_input_dir(config)

    wrapper = GenEnsProdWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    file_list_dir = os.path.join(wrapper.config.getdir('STAGING_DIR'),
                                 'file_lists')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [
        (f"{app_path} {verbosity} -ens "
         f"{file_list_dir}/20091231120000_24_gen_ens_prod.txt "
         "-out "
         f"{out_dir}/gen_ens_prod_20100101_120000V_ens.nc "
         f"-config {config_file} -ctrl "
         f"{input_dir}/2009123112/arw-tom-gep3/d01_2009123112_02400.grib"),
        (f"{app_path} {verbosity} -ens "
         f"{file_list_dir}/20091231120000_48_gen_ens_prod.txt "
         "-out "
         f"{out_dir}/gen_ens_prod_20100102_120000V_ens.nc "
         f"-config {config_file} -ctrl "
         f"{input_dir}/2009123112/arw-tom-gep3/d01_2009123112_04800.grib"),
        (f"{app_path} {verbosity} -ens "
         f"{file_list_dir}/20091231180000_24_gen_ens_prod.txt "
         "-out "
         f"{out_dir}/gen_ens_prod_20100101_180000V_ens.nc "
         f"-config {config_file} -ctrl "
         f"{input_dir}/2009123118/arw-tom-gep3/d01_2009123118_02400.grib"),
        (f"{app_path} {verbosity} -ens "
         f"{file_list_dir}/20091231180000_48_gen_ens_prod.txt "
         "-out "
         f"{out_dir}/gen_ens_prod_20100102_180000V_ens.nc "
         f"-config {config_file} -ctrl "
         f"{input_dir}/2009123118/arw-tom-gep3/d01_2009123118_04800.grib"),
    ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

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
            if env_var_key == 'METPLUS_ENS_FIELD':
                assert (actual_value == ens_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == actual_value)


@pytest.mark.parametrize(
    'use_default_config_file', [
        True,
        False,
    ]
)
@pytest.mark.wrapper
def test_get_config_file(metplus_config, use_default_config_file):
    config = metplus_config()

    if use_default_config_file:
        config_file = os.path.join(config.getdir('PARM_BASE'),
                                   'met_config',
                                   'GenEnsProdConfig_wrapped')
    else:
        config_file = '/my/config/file'
        config.set('config', 'GEN_ENS_PROD_CONFIG_FILE', config_file)

    wrapper = GenEnsProdWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == config_file


@pytest.mark.parametrize(
    'config_overrides, expected_num_files', [
        ({}, 10),
        ({'GEN_ENS_PROD_ENS_MEMBER_IDS': '1'}, 5),
    ]
)
@pytest.mark.wrapper
def test_gen_ens_prod_fill_missing(metplus_config, config_overrides,
                                   expected_num_files):
    config = metplus_config()

    set_minimum_config_settings(config)
    handle_input_dir(config)

    # change some config values for this test
    config.set('config', 'INIT_END', run_times[0])
    config.set('config', 'GEN_ENS_PROD_N_MEMBERS', 10)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = GenEnsProdWrapper(config)

    file_list_file = os.path.join(wrapper.config.getdir('STAGING_DIR'),
                                  'file_lists',
                                  '20091231120000_24_gen_ens_prod.txt')
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    all_cmds = wrapper.run_all_times()
    assert len(all_cmds) == 2

    with open(file_list_file, 'r') as file_handle:
        actual_num_files = len(file_handle.read().splitlines()) - 1

    assert actual_num_files == expected_num_files
