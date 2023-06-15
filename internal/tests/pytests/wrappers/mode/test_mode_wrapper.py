#!/usr/bin/env python3

import pytest

import os


from metplus.wrappers.mode_wrapper import MODEWrapper

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'
fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level_no_quotes = '(*,*)'
obs_level = f'"{obs_level_no_quotes}"'
fcst_fmt = f'field = {{ name="{fcst_name}"; level="{fcst_level}"; }};'
obs_fmt = (f'field = {{ name="{obs_name}"; '
           f'level="{obs_level_no_quotes}"; }};')

fcst_multi_fmt = (f'field = [{{ name="{fcst_name}"; level="{fcst_level}"; }},'
                  f'{{ name="{fcst_name}"; level="{fcst_level}"; }}];')
obs_multi_fmt = (f'field = [{{ name="{obs_name}"; '
                 f'level="{obs_level_no_quotes}"; }},'
                 f'{{ name="{obs_name}"; level="{obs_level_no_quotes}"; }}];')


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'MODE')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080712')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'MODE_CONFIG_FILE',
               '{PARM_BASE}/met_config/MODEConfig_wrapped')
    config.set('config', 'FCST_MODE_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_MODE_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_MODE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_MODE_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'MODE_OUTPUT_DIR',
               '{OUTPUT_BASE}/MODE/output')
    config.set('config', 'MODE_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'MODE_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'MODE_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}',
          'REGRID_TO_GRID': 'FCST'}),

        ({'MODE_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'MODE_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'MODE_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'MODE_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'MODE_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'MODE_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {
             'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'MODE_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'MODE_REGRID_TO_GRID': 'FCST',
          'MODE_REGRID_METHOD': 'NEAREST',
          'MODE_REGRID_WIDTH': '1',
          'MODE_REGRID_VLD_THRESH': '0.5',
          'MODE_REGRID_SHAPE': 'SQUARE',
          'MODE_REGRID_CONVERT': '2*x',
          'MODE_REGRID_CENSOR_THRESH': '>12000,<5000',
          'MODE_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  ),
          'REGRID_TO_GRID': 'FCST'}),

        ({'MODE_QUILT': 'True'},
         {'METPLUS_QUILT': 'quilt = TRUE;'}),

        ({'MODE_FCST_CONV_RADIUS': '40.0/grid_res'},
         {'METPLUS_FCST_CONV_RADIUS': 'conv_radius = [40.0/grid_res];'}),
        ({'MODE_OBS_CONV_RADIUS': '40.0/grid_res'},
         {'METPLUS_OBS_CONV_RADIUS': 'conv_radius = [40.0/grid_res];'}),

        ({'FCST_MODE_CONV_THRESH': '>=10.0'},
         {'METPLUS_FCST_CONV_THRESH': 'conv_thresh = [>=10.0];'}),
        ({'OBS_MODE_CONV_THRESH': '>=10.0'},
         {'METPLUS_OBS_CONV_THRESH': 'conv_thresh = [>=10.0];'}),

        ({'FCST_MODE_MERGE_THRESH': '>=10.0'},
         {'METPLUS_FCST_MERGE_THRESH': 'merge_thresh = [>=10.0];'}),
        ({'OBS_MODE_MERGE_THRESH': '>=10.0'},
         {'METPLUS_OBS_MERGE_THRESH': 'merge_thresh = [>=10.0];'}),

        ({'FCST_MODE_MERGE_FLAG': 'Thresh'},
         {'METPLUS_FCST_MERGE_FLAG': 'merge_flag = THRESH;'}),
        ({'OBS_MODE_MERGE_FLAG': 'Thresh'},
         {'METPLUS_OBS_MERGE_FLAG': 'merge_flag = THRESH;'}),

        ({'MODE_FCST_FILTER_ATTR_NAME': 'ONE, TWO'},
         {'METPLUS_FCST_FILTER_ATTR_NAME': 'filter_attr_name = ["ONE", "TWO"];'}),
        ({'MODE_OBS_FILTER_ATTR_NAME': 'ONE, TWO'},
         {'METPLUS_OBS_FILTER_ATTR_NAME': 'filter_attr_name = ["ONE", "TWO"];'}),

        ({'MODE_FCST_FILTER_ATTR_THRESH': '>=1.0, >=2.0'},
         {'METPLUS_FCST_FILTER_ATTR_THRESH': 'filter_attr_thresh = [>=1.0, >=2.0];'}),
        ({'MODE_OBS_FILTER_ATTR_THRESH': '>=1.0, >=2.0'},
         {'METPLUS_OBS_FILTER_ATTR_THRESH': 'filter_attr_thresh = [>=1.0, >=2.0];'}),

        ({'MODE_FCST_CENSOR_THRESH': '>=1.0, >=2.0'},
         {'METPLUS_FCST_CENSOR_THRESH': 'censor_thresh = [>=1.0, >=2.0];'}),
        ({'MODE_OBS_CENSOR_THRESH': '>=1.0, >=2.0'},
         {'METPLUS_OBS_CENSOR_THRESH': 'censor_thresh = [>=1.0, >=2.0];'}),

        ({'MODE_FCST_CENSOR_VAL': '1.0, 2.0'},
         {'METPLUS_FCST_CENSOR_VAL': 'censor_val = [1.0, 2.0];'}),
        ({'MODE_OBS_CENSOR_VAL': '1.0, 2.0'},
         {'METPLUS_OBS_CENSOR_VAL': 'censor_val = [1.0, 2.0];'}),

        ({'MODE_FCST_VLD_THRESH': '0.6'},
         {'METPLUS_FCST_VLD_THRESH': 'vld_thresh = 0.6;'}),
        ({'MODE_OBS_VLD_THRESH': '0.6'},
         {'METPLUS_OBS_VLD_THRESH': 'vld_thresh = 0.6;'}),

        # mask grid value
        ({'MODE_MASK_GRID': 'FULL',
          },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";}',
          }),
        # mask poly (old config var)
        ({'MODE_VERIFICATION_MASK_TEMPLATE': 'one',
          },
         {'METPLUS_MASK_DICT': 'mask = {poly = "one";}',
          }),
        # mask poly (new config var)
        ({'MODE_MASK_POLY': 'one',
          },
         {'METPLUS_MASK_DICT': 'mask = {poly = "one";}',
          }),
        # mask poly_flag
        ({'MODE_MASK_POLY_FLAG': 'Fcst',
          },
         {'METPLUS_MASK_DICT': 'mask = {poly_flag = FCST;}',
          }),
        # mask grid_flag
        ({'MODE_MASK_GRID_FLAG': 'obs',
          },
         {'METPLUS_MASK_DICT': 'mask = {grid_flag = OBS;}',
          }),
        # mask all
        ({'MODE_MASK_GRID': 'FULL',
          'MODE_MASK_POLY': 'one',
          'MODE_MASK_POLY_FLAG': 'Fcst',
          'MODE_MASK_GRID_FLAG': 'obs',
          },
         {'METPLUS_MASK_DICT': ('mask = {grid = "FULL";poly = "one";'
                                'grid_flag = OBS;poly_flag = FCST;}'),
          }),
        ({'MODE_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'MODE_GRID_RES': '40.0'},
         {'METPLUS_GRID_RES': 'grid_res = 40.0;'}),

        ({'MODE_MATCH_FLAG': 'merge_both'},
         {'METPLUS_MATCH_FLAG': 'match_flag = MERGE_BOTH;'}),

        # single weight values
        ({'MODE_WEIGHT_CENTROID_DIST': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {centroid_dist = 4.0;}'}),
        ({'MODE_WEIGHT_BOUNDARY_DIST': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {boundary_dist = 4.0;}'}),
        ({'MODE_WEIGHT_CONVEX_HULL_DIST': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {convex_hull_dist = 4.0;}'}),
        ({'MODE_WEIGHT_ANGLE_DIFF': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {angle_diff = 4.0;}'}),
        ({'MODE_WEIGHT_ASPECT_DIFF': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {aspect_diff = 4.0;}'}),
        ({'MODE_WEIGHT_AREA_RATIO': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {area_ratio = 4.0;}'}),
        ({'MODE_WEIGHT_INT_AREA_RATIO': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {int_area_ratio = 4.0;}'}),
        ({'MODE_WEIGHT_CURVATURE_RATIO': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {curvature_ratio = 4.0;}'}),
        ({'MODE_WEIGHT_COMPLEXITY_RATIO': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {complexity_ratio = 4.0;}'}),
        ({'MODE_WEIGHT_INTEN_PERC_RATIO': '4.0', },
         {'METPLUS_WEIGHT_DICT': 'weight = {inten_perc_ratio = 4.0;}'}),
        ({'MODE_WEIGHT_INTEN_PERC_VALUE': '40', },
         {'METPLUS_WEIGHT_DICT': 'weight = {inten_perc_value = 40;}'}),

        # all weight values
        ({'MODE_WEIGHT_CENTROID_DIST': '4.0',
          'MODE_WEIGHT_BOUNDARY_DIST': '4.0',
          'MODE_WEIGHT_CONVEX_HULL_DIST': '4.0',
          'MODE_WEIGHT_ANGLE_DIFF': '4.0',
          'MODE_WEIGHT_ASPECT_DIFF': '4.0',
          'MODE_WEIGHT_AREA_RATIO': '4.0',
          'MODE_WEIGHT_INT_AREA_RATIO': '4.0',
          'MODE_WEIGHT_CURVATURE_RATIO': '4.0',
          'MODE_WEIGHT_COMPLEXITY_RATIO': '4.0',
          'MODE_WEIGHT_INTEN_PERC_RATIO': '4.0',
          'MODE_WEIGHT_INTEN_PERC_VALUE': '40',
          },
         {'METPLUS_WEIGHT_DICT': ('weight = {centroid_dist = 4.0;'
                                  'boundary_dist = 4.0;convex_hull_dist = 4.0;'
                                  'angle_diff = 4.0;aspect_diff = 4.0;'
                                  'area_ratio = 4.0;int_area_ratio = 4.0;'
                                  'curvature_ratio = 4.0;'
                                  'complexity_ratio = 4.0;'
                                  'inten_perc_ratio = 4.0;'
                                  'inten_perc_value = 40;}')}),

        ({'MODE_NC_PAIRS_FLAG_LATLON': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {latlon = FALSE;}'}),

        ({'MODE_NC_PAIRS_FLAG_RAW': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {raw = FALSE;}'}),

        ({'MODE_NC_PAIRS_FLAG_OBJECT_RAW': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {object_raw = FALSE;}'}),

        ({'MODE_NC_PAIRS_FLAG_OBJECT_ID': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {object_id = FALSE;}'}),

        ({'MODE_NC_PAIRS_FLAG_CLUSTER_ID': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {cluster_id = FALSE;}'}),

        ({'MODE_NC_PAIRS_FLAG_POLYLINES': 'FALSE', },
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {polylines = FALSE;}'}),

        ({
             'MODE_NC_PAIRS_FLAG_LATLON': 'FALSE',
             'MODE_NC_PAIRS_FLAG_RAW': 'FALSE',
             'MODE_NC_PAIRS_FLAG_OBJECT_RAW': 'FALSE',
             'MODE_NC_PAIRS_FLAG_OBJECT_ID': 'FALSE',
             'MODE_NC_PAIRS_FLAG_CLUSTER_ID': 'FALSE',
             'MODE_NC_PAIRS_FLAG_POLYLINES': 'FALSE',
         },
         {
             'METPLUS_NC_PAIRS_FLAG_DICT': ('nc_pairs_flag = {latlon = FALSE;'
                                            'raw = FALSE;object_raw = FALSE;'
                                            'object_id = FALSE;'
                                            'cluster_id = FALSE;'
                                            'polylines = FALSE;}')}),

        ({'MODE_MAX_CENTROID_DIST': '400.0/grid_res'},
         {'METPLUS_MAX_CENTROID_DIST': 'max_centroid_dist = 400.0/grid_res;'}),

        ({'MODE_TOTAL_INTEREST_THRESH': '0.4'},
         {'METPLUS_TOTAL_INTEREST_THRESH': 'total_interest_thresh = 0.4;'}),

        ({'MODE_INTEREST_FUNCTION_CENTROID_DIST': ('((0.0, 2.0) '
                                                   '(30.0/grid_res, 1.0)'
                                                   '300.0/grid_res, 1.0))')},
         {'METPLUS_INTEREST_FUNCTION_CENTROID_DIST': ('centroid_dist = ('
                                                      '(0.0, 2.0) '
                                                      '(30.0/grid_res, 1.0)'
                                                      '300.0/grid_res, 1.0)'
                                                      ');')}),

        ({'MODE_INTEREST_FUNCTION_BOUNDARY_DIST': ('((0.0, 2.0) '
                                                   '200.0/grid_res, 1.0))')},
         {'METPLUS_INTEREST_FUNCTION_BOUNDARY_DIST': ('boundary_dist = ('
                                                      '(0.0, 2.0) '
                                                      '200.0/grid_res, 1.0)'
                                                      ');')}),

        ({'MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST': ('((0.0, 2.0) '
                                                   '200.0/grid_res, 1.0))')},
         {'METPLUS_INTEREST_FUNCTION_CONVEX_HULL_DIST': ('convex_hull_dist = ('
                                                      '(0.0, 2.0) '
                                                      '200.0/grid_res, 1.0)'
                                                      ');')}),
        ({'MODE_PS_PLOT_FLAG': 'True', },
         {'METPLUS_PS_PLOT_FLAG': 'ps_plot_flag = TRUE;'}),
        ({'MODE_CT_STATS_FLAG': 'True', },
         {'METPLUS_CT_STATS_FLAG': 'ct_stats_flag = TRUE;'}),
        ({'MODE_FCST_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_FCST_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'MODE_OBS_FILE_TYPE': 'NETCDF_PINT', },
         {'METPLUS_OBS_FILE_TYPE': 'file_type = NETCDF_PINT;'}),
        ({'MODE_MASK_MISSING_FLAG': 'BOTH', },
         {'METPLUS_MASK_MISSING_FLAG': 'mask_missing_flag = BOTH;'}),

        ({'MODE_MULTIVAR_INTENSITY': 'false, true,true', },
         {'METPLUS_MULTIVAR_INTENSITY': 'multivar_intensity = [FALSE, TRUE, TRUE];'}),

        ({'MODE_FCST_MULTIVAR_NAME': 'Snow', },
         {'METPLUS_FCST_MULTIVAR_NAME': 'multivar_name = "Snow";'}),

        ({'MODE_FCST_MULTIVAR_LEVEL': 'L0', },
         {'METPLUS_FCST_MULTIVAR_LEVEL': 'multivar_level = "L0";'}),

        ({'MODE_OBS_MULTIVAR_NAME': 'Precip', },
         {'METPLUS_OBS_MULTIVAR_NAME': 'multivar_name = "Precip";'}),

        ({'MODE_OBS_MULTIVAR_LEVEL': 'Z10', },
         {'METPLUS_OBS_MULTIVAR_LEVEL': 'multivar_level = "Z10";'}),

    ]
)
@pytest.mark.wrapper_a
def test_mode_single_field(metplus_config, config_overrides, env_var_values):
    config = metplus_config

    # set config variables needed to run
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = MODEWrapper(config)
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

    # set default values in expected output list
    # only if they are not set and if MODE_GRID_RES is set
    if 'MODE_GRID_RES' in config_overrides:
        met_remove_prefixes = ['interest_function_', 'fcst_', 'obs_']
        met_lists = ['conv_radius']
        for name, default_val in wrapper.DEFAULT_VALUES.items():
            if f'MODE_{name}' not in config_overrides:
                met_name = name.lower()
                # remove prefix that corresponds to dictionary not variable
                for met_remove_prefix in met_remove_prefixes:
                    if met_name.startswith(met_remove_prefix):
                        met_name = met_name.split(met_remove_prefix)[1]
                        break

                # convert value to list if variable expects a list
                if met_name in met_lists:
                    default_val = f'[{default_val}]'

                env_var_values[f'METPLUS_{name}'] = (
                    f'{met_name} = {default_val};'
                )

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


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODE_MULTIVAR_LOGIC': '#1 && #2 && #3', },
         {'METPLUS_MULTIVAR_LOGIC': 'multivar_logic = "#1 && #2 && #3";'}),
    ]
)
@pytest.mark.wrapper_a
def test_mode_multi_variate(metplus_config, config_overrides,
                            env_var_values):
    config = metplus_config

    # set config variables needed to run
    set_minimum_config_settings(config)

    # change config values to reflect an expected multi-variate run
    # multiple fields and input files
    config.set('config', 'FCST_VAR2_NAME', fcst_name)
    config.set('config', 'FCST_VAR2_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR2_NAME', obs_name)
    config.set('config', 'OBS_VAR2_LEVELS', obs_level)
    config.set('config', 'FCST_MODE_INPUT_TEMPLATE',
               ('{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H},'
                '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}'))
    config.set('config', 'OBS_MODE_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file,{valid?fmt=%Y%m%d%H}/obs_file')

    wrapper = MODEWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    file_list_dir = os.path.join(config.getdir('STAGING_DIR'), 'file_lists')

    expected_cmds = [(f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807000000_12_mode_fcst.txt "
                      f"{file_list_dir}/20050807000000_12_mode_obs.txt "
                      f"{config_file} -outdir {out_dir}/2005080712"),
                     (f"{app_path} {verbosity} "
                      f"{file_list_dir}/20050807120000_12_mode_fcst.txt "
                      f"{file_list_dir}/20050807120000_12_mode_obs.txt "
                      f"{config_file} -outdir {out_dir}/2005080800"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

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
                assert value == fcst_multi_fmt
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert value == obs_multi_fmt
            else:
                assert env_var_values.get(env_var_key, '') == value


@pytest.mark.parametrize(
    'config_name, env_var_name, met_name, var_type', [
        ('FCST_MODE_CONV_RADIUS', 'METPLUS_FCST_CONV_RADIUS',
         'conv_radius', 'list'),
        ('MODE_FCST_CONV_RADIUS', 'METPLUS_FCST_CONV_RADIUS',
         'conv_radius', 'list'),
        ('MODE_CONV_RADIUS', 'METPLUS_FCST_CONV_RADIUS',
         'conv_radius', 'list'),

        ('FCST_MODE_CONV_THRESH', 'METPLUS_FCST_CONV_THRESH',
         'conv_thresh', 'list'),
        ('MODE_FCST_CONV_THRESH', 'METPLUS_FCST_CONV_THRESH',
         'conv_thresh', 'list'),
        ('MODE_CONV_THRESH', 'METPLUS_FCST_CONV_THRESH',
         'conv_thresh', 'list'),

        ('FCST_MODE_MERGE_THRESH', 'METPLUS_FCST_MERGE_THRESH',
         'merge_thresh', 'list'),
        ('MODE_FCST_MERGE_THRESH', 'METPLUS_FCST_MERGE_THRESH',
         'merge_thresh', 'list'),
        ('MODE_MERGE_THRESH', 'METPLUS_FCST_MERGE_THRESH',
         'merge_thresh', 'list'),

        ('FCST_MODE_MERGE_FLAG', 'METPLUS_FCST_MERGE_FLAG',
         'merge_flag', 'upper'),
        ('MODE_FCST_MERGE_FLAG', 'METPLUS_FCST_MERGE_FLAG',
         'merge_flag', 'upper'),
        ('MODE_MERGE_FLAG', 'METPLUS_FCST_MERGE_FLAG',
         'merge_flag', 'upper'),

        ('FCST_MODE_VLD_THRESH', 'METPLUS_FCST_VLD_THRESH',
         'vld_thresh', 'float'),
        ('FCST_MODE_VALID_THRESH', 'METPLUS_FCST_VLD_THRESH',
         'vld_thresh', 'float'),
        ('MODE_FCST_VLD_THRESH', 'METPLUS_FCST_VLD_THRESH',
         'vld_thresh', 'float'),
        ('MODE_FCST_VALID_THRESH', 'METPLUS_FCST_VLD_THRESH',
         'vld_thresh', 'float'),

    ]
)
@pytest.mark.wrapper_a
def test_config_synonyms(metplus_config, config_name, env_var_name,
                         met_name, var_type):
    """! Ensure that different METplus config variable names set the correct
         value in the environment variables list
    """
    in_value = 'out_value'

    if var_type == 'list':
        out_value = f'[{in_value}]'
    elif var_type == 'upper':
        out_value = in_value.upper()
    elif var_type == 'float':
        in_value = out_value = 4.0

    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', config_name, in_value)
    wrapper = MODEWrapper(config)
    assert wrapper.isOK

    expected_output = f'{met_name} = {out_value};'
    assert wrapper.env_var_dict[env_var_name] == expected_output


@pytest.mark.wrapper_a
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'MODEConfig_wrapped')

    wrapper = MODEWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'MODE_CONFIG_FILE', fake_config_name)
    wrapper = MODEWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
