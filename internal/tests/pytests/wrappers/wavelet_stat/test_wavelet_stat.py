#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.wavelet_stat_wrapper import WaveletStatWrapper

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'
fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level_no_quotes = '(*,*)'
obs_level = f'"{obs_level_no_quotes}"'
both_thresh = ' lt-0.5,gt-0.5 && lt0.5,gt0.5 '
fcst_fmt = f'field = [{{ name="{fcst_name}"; level="{fcst_level}"; cat_thresh=[{both_thresh}]; }}];'
obs_fmt = (f'field = [{{ name="{obs_name}"; '
           f'level="{obs_level_no_quotes}"; cat_thresh=[{both_thresh}]; }}];')
time_fmt = '%Y%m%d%H'
run_times = ['2005080700', '2005080712']


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'WaveletStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'WAVELET_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/WaveletStatConfig_wrapped')
    config.set('config', 'FCST_WAVELET_STAT_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_WAVELET_STAT_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_WAVELET_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_WAVELET_STAT_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'WAVELET_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/WaveletStat/output')
    config.set('config', 'WAVELET_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)
    config.set('config', 'BOTH_VAR1_THRESH', both_thresh)


@pytest.mark.parametrize(
    'config_overrides, expected_values', [
        # 0 generic FCST is prob
        ({'FCST_IS_PROB': True},
         {'FCST_IS_PROB': True, 'OBS_IS_PROB': False}),
        # 1 generic OBS is prob
        ({'OBS_IS_PROB': True},
         {'FCST_IS_PROB': False, 'OBS_IS_PROB': True}),
        # 2 generic FCST and OBS is prob
        ({'FCST_IS_PROB': True, 'OBS_IS_PROB': True},
         {'FCST_IS_PROB': True, 'OBS_IS_PROB': True}),
        # 3 generic FCST true, wrapper FCST false
        ({'FCST_IS_PROB': True, 'FCST_WAVELET_STAT_IS_PROB': False},
         {'FCST_IS_PROB': False, 'OBS_IS_PROB': False}),
        # 4 generic OBS true, wrapper OBS false
        ({'OBS_IS_PROB': True, 'OBS_WAVELET_STAT_IS_PROB': False},
         {'FCST_IS_PROB': False, 'OBS_IS_PROB': False}),
        # 5 generic FCST unset, wrapper FCST true
        ({'FCST_WAVELET_STAT_IS_PROB': True},
         {'FCST_IS_PROB': True, 'OBS_IS_PROB': False}),
        # 6 generic OBS unset, wrapper OBS true
        ({'OBS_WAVELET_STAT_IS_PROB': True},
         {'FCST_IS_PROB': False, 'OBS_IS_PROB': True}),
        # 7 generic FCST false, wrapper FCST true
        ({'FCST_IS_PROB': False, 'FCST_WAVELET_STAT_IS_PROB': True},
         {'FCST_IS_PROB': True, 'OBS_IS_PROB': False}),
        # 8 generic FCST true, wrapper FCST false
        ({'FCST_IS_PROB': True, 'FCST_WAVELET_STAT_IS_PROB': False},
         {'FCST_IS_PROB': False, 'OBS_IS_PROB': False}),
    ]
)
@pytest.mark.wrapper_b
def test_wavelet_stat_is_prob(metplus_config, config_overrides, expected_values):
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = WaveletStatWrapper(config)
    assert wrapper.isOK
    for key, expected_value in expected_values.items():
        assert expected_value == wrapper.c_dict[key]


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'WAVELET_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'WAVELET_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'WAVELET_STAT_REGRID_TO_GRID': 'FCST',},
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'WAVELET_STAT_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'WAVELET_STAT_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'WAVELET_STAT_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'WAVELET_STAT_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'WAVELET_STAT_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'WAVELET_STAT_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'WAVELET_STAT_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'WAVELET_STAT_REGRID_TO_GRID': 'FCST',
          'WAVELET_STAT_REGRID_METHOD': 'NEAREST',
          'WAVELET_STAT_REGRID_WIDTH': '1',
          'WAVELET_STAT_REGRID_VLD_THRESH': '0.5',
          'WAVELET_STAT_REGRID_SHAPE': 'SQUARE',
          'WAVELET_STAT_REGRID_CONVERT': '2*x',
          'WAVELET_STAT_REGRID_CENSOR_THRESH': '>12000,<5000',
          'WAVELET_STAT_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )}),

        ({'WAVELET_STAT_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_CENSOR_THRESH': 'censor_thresh = [>12000, <5000];'}),
        ({'WAVELET_STAT_CENSOR_VAL': '12000, 5000', },
         {'METPLUS_CENSOR_VAL': 'censor_val = [12000, 5000];'}),

        ({'WAVELET_STAT_MASK_MISSING_FLAG': 'NONE', },
         {'METPLUS_MASK_MISSING_FLAG': 'mask_missing_flag = NONE;'}),

        ({'WAVELET_STAT_GRID_DECOMP_FLAG': 'AUTO', },
         {'METPLUS_GRID_DECOMP_FLAG': 'grid_decomp_flag = AUTO;'}),

        ({'WAVELET_STAT_TITLE_WIDTH': '0', },
         {'METPLUS_TITLE_DICT': 'title = {width = 0;}'}),

        ({'WAVELET_STAT_TITLE_LOCATION_X_LL': '1', },
         {'METPLUS_TITLE_DICT': 'title = {location = [{x_ll = 1;}];}'}),

        ({'WAVELET_STAT_TITLE_LOCATION_Y_LL': '1', },
         {'METPLUS_TITLE_DICT': 'title = {location = [{y_ll = 1;}];}'}),

        ({
             'WAVELET_STAT_TITLE_WIDTH': '1',
             'WAVELET_STAT_TITLE_LOCATION1_X_LL': '1',
             'WAVELET_STAT_TITLE_LOCATION1_Y_LL': '2',
             'WAVELET_STAT_TITLE_LOCATION2_X_LL': '3',
             'WAVELET_STAT_TITLE_LOCATION2_Y_LL': '4',
         },
         {'METPLUS_TITLE_DICT': 'title = {width = 1;location = [{x_ll = 1;y_ll = 2;},{x_ll = 3;y_ll = 4;}];}'}),

        ({'WAVELET_STAT_WAVELET_TYPE': 'HAAR', },
         {'METPLUS_WAVELET_DICT': 'wavelet = {type = HAAR;}'}),

        ({'WAVELET_STAT_WAVELET_MEMBER': '2', },
         {'METPLUS_WAVELET_DICT': 'wavelet = {member = 2;}'}),

        ({
             'WAVELET_STAT_WAVELET_TYPE': 'HAAR',
             'WAVELET_STAT_WAVELET_MEMBER': '2',
         },
         {'METPLUS_WAVELET_DICT': 'wavelet = {type = HAAR;member = 2;}'}),

        ({'WAVELET_STAT_OUTPUT_FLAG_ISC': 'STAT', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {isc = STAT;}'}),

        ({'WAVELET_STAT_NC_PAIRS_FLAG_RAW': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {raw = TRUE;}'}),

        ({'WAVELET_STAT_NC_PAIRS_FLAG_DIFF': 'TRUE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {diff = TRUE;}'}),

        ({'WAVELET_STAT_NC_PAIRS_FLAG_RAW': 'TRUE',
          'WAVELET_STAT_NC_PAIRS_FLAG_DIFF': 'TRUE',
          },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {raw = TRUE;diff = TRUE;}'
          }),

         ({'WAVELET_STAT_FCST_RAW_PLOT_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable', },
          {'METPLUS_FCST_RAW_PLOT_DICT': 'fcst_raw_plot = {color_table = \"MET_BASE/colortables/met_default.ctable\";}'}),

         ({'WAVELET_STAT_FCST_RAW_PLOT_PLOT_MIN': '0.0', },
          {'METPLUS_FCST_RAW_PLOT_DICT': 'fcst_raw_plot = {plot_min = 0.0;}'}),

         ({'WAVELET_STAT_FCST_RAW_PLOT_PLOT_MAX': '1.0', },
          {'METPLUS_FCST_RAW_PLOT_DICT': 'fcst_raw_plot = {plot_max = 1.0;}'}),

        ({'WAVELET_STAT_FCST_RAW_PLOT_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable',
          'WAVELET_STAT_FCST_RAW_PLOT_PLOT_MIN': '0.0',
          'WAVELET_STAT_FCST_RAW_PLOT_PLOT_MAX': '1.0',
          },
         {'METPLUS_FCST_RAW_PLOT_DICT': 'fcst_raw_plot = {color_table = \"MET_BASE/colortables/met_default.ctable\";plot_min = 0.0;plot_max = 1.0;}'}),

        ({'WAVELET_STAT_OBS_RAW_PLOT_PLOT_MIN': '0.0', },
         {'METPLUS_OBS_RAW_PLOT_DICT': 'obs_raw_plot = {plot_min = 0.0;}'}),

        ({'WAVELET_STAT_OBS_RAW_PLOT_PLOT_MAX': '1.0', },
         {'METPLUS_OBS_RAW_PLOT_DICT': 'obs_raw_plot = {plot_max = 1.0;}'}),

        ({'WAVELET_STAT_OBS_RAW_PLOT_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable',
          'WAVELET_STAT_OBS_RAW_PLOT_PLOT_MIN': '0.0',
          'WAVELET_STAT_OBS_RAW_PLOT_PLOT_MAX': '1.0',
          },
         {'METPLUS_OBS_RAW_PLOT_DICT': 'obs_raw_plot = {color_table = \"MET_BASE/colortables/met_default.ctable\";plot_min = 0.0;plot_max = 1.0;}'}),

        ({'WAVELET_STAT_WVLT_PLOT_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable', },
         {
             'METPLUS_WVLT_PLOT_DICT': 'wvlt_plot = {color_table = \"MET_BASE/colortables/met_default.ctable\";}'}),

        ({'WAVELET_STAT_WVLT_PLOT_PLOT_MIN': '0.0', },
         {'METPLUS_WVLT_PLOT_DICT': 'wvlt_plot = {plot_min = 0.0;}'}),

        ({'WAVELET_STAT_WVLT_PLOT_PLOT_MAX': '1.0', },
         {'METPLUS_WVLT_PLOT_DICT': 'wvlt_plot = {plot_max = 1.0;}'}),

        ({'WAVELET_STAT_WVLT_PLOT_COLOR_TABLE': 'MET_BASE/colortables/NCL_colortables/BlWhRe.ctable',
          'WAVELET_STAT_WVLT_PLOT_PLOT_MIN': '0.0',
          'WAVELET_STAT_WVLT_PLOT_PLOT_MAX': '1.0',
          },
         {'METPLUS_WVLT_PLOT_DICT': 'wvlt_plot = {color_table = \"MET_BASE/colortables/NCL_colortables/BlWhRe.ctable\";plot_min = 0.0;plot_max = 1.0;}'}),

        ({'WAVELET_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'FCST_WAVELET_STAT_FILE_TYPE': 'NETCDF_NCCF', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_NCCF;'}),
        ({'OBS_WAVELET_STAT_FILE_TYPE': 'NETCDF_NCCF', },
         {'METPLUS_OBS_FILE_TYPE': 'file_type = NETCDF_NCCF;'}),

    ]
)
@pytest.mark.wrapper_b
def test_wavelet_stat_single_field(metplus_config, config_overrides, env_var_values):

    config = metplus_config
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = WaveletStatWrapper(config)
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

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    assert len(all_cmds) == len(expected_cmds)
    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        # including deprecated env vars (not in wrapper env var keys)
        for env_var_key in env_var_keys:
            print(f"ENV VAR: {env_var_key}")
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            actual_value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert actual_value == fcst_fmt
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert actual_value == obs_fmt
            else:
                assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.wrapper_b
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'WaveletStatConfig_wrapped')

    wrapper = WaveletStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'WAVELET_STAT_CONFIG_FILE', fake_config_name)
    wrapper = WaveletStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
