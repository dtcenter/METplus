#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.plot_point_obs_wrapper import PlotPointObsWrapper

obs_dir = '/some/path/obs'
input_template_one = (
    'pb2nc/ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr.tm00.nc'
)
input_template_two = (
    'pb2nc/ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr.tm00.nc,'
    'ascii2nc/trmm_{valid?fmt=%Y%m%d%H}_3hr.nc'
)

grid_dir = '/some/path/grid'
grid_template = 'nam_{init?fmt=%Y%m%d%H}_F{lead?fmt=%3H}.grib2'

output_dir = '{OUTPUT_BASE}/plot_point_obs'
output_template = 'nam_and_ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr_CONFIG.ps'

title = 'NAM 2012040900 F12 vs NDAS 500mb RH and TRMM 3h > 0'

point_data = ['{msg_typ = "ADPSFC";obs_gc = 61;obs_thresh = > 0.0;'
              'fill_color = [0,0,255];}',
              '{msg_typ = "ADPSFC";obs_var = "RH";'
              'fill_color = [100,100,100];}']
point_data_input = ', '.join(point_data)
point_data_format = f"[{point_data_input}];"

time_fmt = '%Y%m%d%H'
run_times = ['2012040912', '2012041000']


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PlotPointObs')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', time_fmt)
    config.set('config', 'VALID_BEG', run_times[0])
    config.set('config', 'VALID_END', run_times[-1])
    config.set('config', 'VALID_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'PLOT_POINT_OBS_INPUT_DIR', obs_dir)
    config.set('config', 'PLOT_POINT_OBS_INPUT_TEMPLATE', input_template_one)
    config.set('config', 'PLOT_POINT_OBS_OUTPUT_DIR', output_dir)
    config.set('config', 'PLOT_POINT_OBS_OUTPUT_TEMPLATE', output_template)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (6, 12, 0.5, 0, True),
        (6, 12, 0.6, 1, True),
        (6, 12, 0.5, 6, False),
    ]
)
@pytest.mark.wrapper_c
def test_plot_point_obs_missing_inputs(metplus_config, get_test_data_dir,
                                       missing, run, thresh, errors,
                                       allow_missing):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'PLOT_POINT_OBS_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'PLOT_POINT_OBS_INPUT_THRESH', thresh)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'PLOT_POINT_OBS_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'PLOT_POINT_OBS_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')

    wrapper = PlotPointObsWrapper(config)
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
        # 0: no additional settings
        ({},{}),
        # 1: input template with 2 paths
        ({'PLOT_POINT_OBS_INPUT_TEMPLATE': input_template_two},
         {}),
        # 2: grid input
        ({'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE': grid_template,
          'PLOT_POINT_OBS_GRID_INPUT_DIR': grid_dir},
         {}),
        # 3: input template with 2 paths and grid input
        ({'PLOT_POINT_OBS_INPUT_TEMPLATE': input_template_two,
          'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE': grid_template,
          'PLOT_POINT_OBS_GRID_INPUT_DIR': grid_dir},
         {}),
        # 4: title
        ({'PLOT_POINT_OBS_TITLE': title},
         {}),
        # 5: input template with 2 paths and grid input and title
        ({'PLOT_POINT_OBS_INPUT_TEMPLATE': input_template_two,
          'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE': grid_template,
          'PLOT_POINT_OBS_GRID_INPUT_DIR': grid_dir,
          'PLOT_POINT_OBS_TITLE': title},
         {}),
        # 6: grid_data.field
        ({'PLOT_POINT_OBS_GRID_DATA_FIELD': '{ name = "RH"; level = "P500"; }'},
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {field = [{ name = "RH"; level = "P500"; }];}'}),
        # 7: grid_data.regrid.to_grid
        ({'PLOT_POINT_OBS_GRID_DATA_REGRID_TO_GRID': 'FCST', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {regrid = {to_grid = FCST;}}'}),
        # 8: grid_data.regrid.method
        ({'PLOT_POINT_OBS_GRID_DATA_REGRID_METHOD': 'NEAREST', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {regrid = {method = NEAREST;}}'}),
        # 9: grid_data.regrid.width
        ({'PLOT_POINT_OBS_GRID_DATA_REGRID_WIDTH': '2', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {regrid = {width = 2;}}'}),
        # 10: grid_data.regrid.vld_thresh
        ({'PLOT_POINT_OBS_GRID_DATA_REGRID_VLD_THRESH': '0.4', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {regrid = {vld_thresh = 0.4;}}'}),
        # 11: grid_data.regrid.shape
        ({'PLOT_POINT_OBS_GRID_DATA_REGRID_SHAPE': 'SQUARE', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {regrid = {shape = SQUARE;}}'}),
        # 12: grid_data.plot_info.color_table
        ({'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {grid_plot_info = {color_table = "MET_BASE/colortables/met_default.ctable";}}'}),
        # 13: grid_data.plot_info.plot_min
        ({'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MIN': '0.1', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {grid_plot_info = {plot_min = 0.1;}}'}),
        # 14: grid_data.plot_info.plot_max
        ({'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MAX': '100.0', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {grid_plot_info = {plot_max = 100.0;}}'}),
        # 15: grid_data.plot_info.colorbar_flag
        ({'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLORBAR_FLAG': 'false', },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {grid_plot_info = {colorbar_flag = FALSE;}}'}),
        # 16: grid_data all
        ({'PLOT_POINT_OBS_GRID_DATA_FIELD': '{ name = "RH"; level = "P500"; }',
          'PLOT_POINT_OBS_GRID_DATA_REGRID_TO_GRID': 'FCST',
          'PLOT_POINT_OBS_GRID_DATA_REGRID_METHOD': 'NEAREST',
          'PLOT_POINT_OBS_GRID_DATA_REGRID_WIDTH': '2',
          'PLOT_POINT_OBS_GRID_DATA_REGRID_VLD_THRESH': '0.4',
          'PLOT_POINT_OBS_GRID_DATA_REGRID_SHAPE': 'SQUARE',
          'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable',
          'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MIN': '0.1',
          'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MAX': '100.0',
          'PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLORBAR_FLAG': 'False',
          },
         {'METPLUS_GRID_DATA_DICT': 'grid_data = {field = [{ name = "RH"; level = "P500"; }];regrid = {to_grid = FCST;method = NEAREST;width = 2;vld_thresh = 0.4;shape = SQUARE;}grid_plot_info = {color_table = "MET_BASE/colortables/met_default.ctable";plot_min = 0.1;plot_max = 100.0;colorbar_flag = FALSE;}}'}),
        # 17: msg_type
        ({'PLOT_POINT_OBS_MSG_TYP': 'ADPUPA, AIRCFT', },
         {'METPLUS_MSG_TYP': 'msg_typ = ["ADPUPA", "AIRCFT"];'}),
        # 18: sid_inc
        ({'PLOT_POINT_OBS_SID_INC': '72364,72265', },
         {'METPLUS_SID_INC': 'sid_inc = ["72364", "72265"];'}),
        # 19: sid_exc
        ({'PLOT_POINT_OBS_SID_EXC': '72274,72426', },
         {'METPLUS_SID_EXC': 'sid_exc = ["72274", "72426"];'}),
        # 20: obs_var
        ({'PLOT_POINT_OBS_OBS_VAR': 'SPFH,TMP', },
         {'METPLUS_OBS_VAR': 'obs_var = ["SPFH", "TMP"];'}),
        # 21: obs_gc
        ({'PLOT_POINT_OBS_OBS_GC': '2,1', },
         {'METPLUS_OBS_GC': 'obs_gc = [2, 1];'}),
        # 22: obs_quality
        ({'PLOT_POINT_OBS_OBS_QUALITY': '2,1', },
         {'METPLUS_OBS_QUALITY': 'obs_quality = ["2", "1"];'}),
        # 23: valid_beg
        ({'PLOT_POINT_OBS_VALID_BEG': '20101231_00', },
         {'METPLUS_VALID_BEG': 'valid_beg = "20101231_00";'}),
        # 24: valid_end
        ({'PLOT_POINT_OBS_VALID_END': '20101231_12', },
         {'METPLUS_VALID_END': 'valid_end = "20101231_12";'}),
        # 25: lat_thresh
        ({'PLOT_POINT_OBS_LAT_THRESH': '>1.0', },
         {'METPLUS_LAT_THRESH': 'lat_thresh = >1.0;'}),
        # 26: lon_thresh
        ({'PLOT_POINT_OBS_LON_THRESH': '>1.0', },
         {'METPLUS_LON_THRESH': 'lon_thresh = >1.0;'}),
        # 27: elv_thresh
        ({'PLOT_POINT_OBS_ELV_THRESH': '>1.0', },
         {'METPLUS_ELV_THRESH': 'elv_thresh = >1.0;'}),
        # 28: hgt_thresh
        ({'PLOT_POINT_OBS_HGT_THRESH': '>1.0', },
         {'METPLUS_HGT_THRESH': 'hgt_thresh = >1.0;'}),
        # 29: prs_thresh
        ({'PLOT_POINT_OBS_PRS_THRESH': '>1.0', },
         {'METPLUS_PRS_THRESH': 'prs_thresh = >1.0;'}),
        # 30: obs_thresh
        ({'PLOT_POINT_OBS_OBS_THRESH': '>1.0', },
         {'METPLUS_OBS_THRESH': 'obs_thresh = >1.0;'}),
        # 31: censor_thresh and censor_val
        ({'PLOT_POINT_OBS_CENSOR_THRESH': '>12000',
          'PLOT_POINT_OBS_CENSOR_VAL': '12000'},
         {'METPLUS_CENSOR_THRESH': 'censor_thresh = [>12000];',
          'METPLUS_CENSOR_VAL': 'censor_val = [12000];'}),
        # 32: dotsize
        ({'PLOT_POINT_OBS_DOTSIZE': '10.0', },
         {'METPLUS_DOTSIZE': 'dotsize(x) = 10.0;'}),
        # 33: line_color
        ({'PLOT_POINT_OBS_LINE_COLOR': '100,105,110', },
         {'METPLUS_LINE_COLOR': 'line_color = [100, 105, 110];'}),
        # 34: line_width
        ({'PLOT_POINT_OBS_LINE_WIDTH': '4', },
         {'METPLUS_LINE_WIDTH': 'line_width = 4;'}),
        # 35: fill_color
        ({'PLOT_POINT_OBS_FILL_COLOR': '0,10,15', },
         {'METPLUS_FILL_COLOR': 'fill_color = [0, 10, 15];'}),
        # 36: fill_plot_info.flag
        ({'PLOT_POINT_OBS_FILL_PLOT_INFO_FLAG': 'true', },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {flag = TRUE;}'}),
        # 37: fill_plot_info.color_table
        ({'PLOT_POINT_OBS_FILL_PLOT_INFO_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable', },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {color_table = "MET_BASE/colortables/met_default.ctable";}'}),
        # 38: fill_plot_info.plot_min
        ({'PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MIN': '0.1', },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {plot_min = 0.1;}'}),
        # 39: fill_plot_info.plot_max
        ({'PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MAX': '100.0', },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {plot_max = 100.0;}'}),
        # 40: fill_plot_info.colorbar_flag
        ({'PLOT_POINT_OBS_FILL_PLOT_INFO_COLORBAR_FLAG': 'False', },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {colorbar_flag = FALSE;}'}),
        # 41: fill_plot_info all
        ({
             'PLOT_POINT_OBS_FILL_PLOT_INFO_FLAG': 'true',
             'PLOT_POINT_OBS_FILL_PLOT_INFO_COLOR_TABLE': 'MET_BASE/colortables/met_default.ctable',
             'PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MIN': '0.1',
             'PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MAX': '100.0',
             'PLOT_POINT_OBS_FILL_PLOT_INFO_COLORBAR_FLAG': 'false',
         },
         {'METPLUS_FILL_PLOT_INFO_DICT': 'fill_plot_info = {flag = TRUE;color_table = "MET_BASE/colortables/met_default.ctable";plot_min = 0.1;plot_max = 100.0;colorbar_flag = FALSE;}'}),
        # 42: point_data
        ({'PLOT_POINT_OBS_POINT_DATA': point_data_input, },
         {'METPLUS_POINT_DATA': f'point_data = {point_data_format}'}),

        ({'PLOT_POINT_OBS_TIME_OFFSET_WARNING': 3},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 3;'}),
        ({'TIME_OFFSET_WARNING': 2},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 2;'}),
        ({'TIME_OFFSET_WARNING': 2, 'PLOT_POINT_OBS_TIME_OFFSET_WARNING': 4},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 4;'}),
    ]
)
@pytest.mark.wrapper_c
def test_plot_point_obs(metplus_config, config_overrides, env_var_values):

    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PlotPointObsWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    input_dir = wrapper.c_dict.get('INPUT_DIR')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [
        (f"{app_path} {verbosity} "
         f'"{input_dir}/pb2nc/ndas.20120409.t12z.prepbufr.tm00.nc" '
         f"{out_dir}/nam_and_ndas.20120409.t12z.prepbufr_CONFIG.ps"),
        (f"{app_path} {verbosity} "
         f'"{input_dir}/pb2nc/ndas.20120410.t00z.prepbufr.tm00.nc" '
         f"{out_dir}/nam_and_ndas.20120410.t00z.prepbufr_CONFIG.ps"),
    ]

    # add -point_obs argument if template has 2 items
    if ('PLOT_POINT_OBS_INPUT_TEMPLATE' in config_overrides and
            len(config_overrides['PLOT_POINT_OBS_INPUT_TEMPLATE'].split(',')) > 1):
        common_str = f' -point_obs "{input_dir}/ascii2nc/trmm_'
        expected_cmds[0] += f'{common_str}2012040912_3hr.nc"'
        expected_cmds[1] += f'{common_str}2012041000_3hr.nc"'

    # add -plot_grid argument if provided
    if 'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE' in config_overrides:
        common_str = f' -plot_grid {grid_dir}/nam_'
        expected_cmds[0] += f'{common_str}2012040900_F012.grib2'
        expected_cmds[1] += f'{common_str}2012040912_F012.grib2'

    # add -config argument
    expected_cmds = [f'{item} -config {config_file}' for item in expected_cmds]

    # add -title if set
    if 'PLOT_POINT_OBS_TITLE' in config_overrides:
        expected_cmds = [f'{item} -title "{title}"' for item in expected_cmds]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)
    assert not wrapper.errors

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
            actual_value = match.split('=', 1)[1]
            assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.wrapper_c
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'PlotPointObsConfig_wrapped')

    wrapper = PlotPointObsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'PLOT_POINT_OBS_CONFIG_FILE', fake_config_name)
    wrapper = PlotPointObsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
