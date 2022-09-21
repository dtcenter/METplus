#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.tc_gen_wrapper import TCGenWrapper


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [

        ({'TC_GEN_INIT_FREQUENCY': '8'},
         {'METPLUS_INIT_FREQ': 'init_freq = 8;'}),

        ({'TC_GEN_VALID_FREQUENCY': '8'},
         {'METPLUS_VALID_FREQ': 'valid_freq = 8;'}),

        ({'TC_GEN_FCST_HR_WINDOW_BEGIN': '7'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {beg = 7;}'}),

        ({'TC_GEN_FCST_HR_WINDOW_END': '119'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {end = 119;}'}),

        ({'TC_GEN_FCST_HR_WINDOW_BEGIN': '7',
          'TC_GEN_FCST_HR_WINDOW_END': '119'},
         {'METPLUS_FCST_HR_WINDOW_DICT': 'fcst_hr_window = {beg = 7;end = 119;}'}),

        ({'TC_GEN_MIN_DURATION': '13'},
         {'METPLUS_MIN_DURATION': 'min_duration = 13;'}),

        ({'TC_GEN_FCST_GENESIS_VMAX_THRESH': '>3'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {vmax_thresh = >3;}'}),

        ({'TC_GEN_FCST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {mslp_thresh = >4;}'}),

        ({'TC_GEN_FCST_GENESIS_VMAX_THRESH': '>3',
          'TC_GEN_FCST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_FCST_GENESIS_DICT': 'fcst_genesis = {vmax_thresh = >3;mslp_thresh = >4;}'}),

        ({'TC_GEN_BEST_GENESIS_TECHNIQUE': 'WORST'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {technique = "WORST";}'}),

        ({'TC_GEN_BEST_GENESIS_CATEGORY': 'PH, SH'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {category = ["PH", "SH"];}'}),

        ({'TC_GEN_BEST_GENESIS_VMAX_THRESH': '>3'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {vmax_thresh = >3;}'}),

        ({'TC_GEN_BEST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_BEST_GENESIS_DICT': 'best_genesis = {mslp_thresh = >4;}'}),

        ({'TC_GEN_BEST_GENESIS_TECHNIQUE': 'WORST',
          'TC_GEN_BEST_GENESIS_CATEGORY': 'PH, SH',
          'TC_GEN_BEST_GENESIS_VMAX_THRESH': '>3',
          'TC_GEN_BEST_GENESIS_MSLP_THRESH': '>4'},
         {'METPLUS_BEST_GENESIS_DICT': ('best_genesis = {technique = "WORST";'
                                        'category = ["PH", "SH"];'
                                        'vmax_thresh = >3;'
                                        'mslp_thresh = >4;}')}),

        ({'TC_GEN_OPER_TECHNIQUE': 'CARQ'},
         {'METPLUS_OPER_TECHNIQUE': 'oper_technique = "CARQ";'}),

        ({'TC_GEN_FILTER_1': 'desc = "uno";'},
         {'METPLUS_FILTER': 'filter = [{desc = "uno";}];'}),

        ({'TC_GEN_FILTER_2': 'desc = "dos";'},
         {'METPLUS_FILTER': 'filter = [{desc = "dos";}];'}),
        ({'TC_GEN_FILTER_1': 'desc = "uno";',
          'TC_GEN_FILTER_2': 'desc = "dos";'},
         {'METPLUS_FILTER': 'filter = [{desc = "uno";}, {desc = "dos";}];'}),

        ({'TC_GEN_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'MODEL': 'model1, model2'},
         {'METPLUS_MODEL': 'model = ["model1", "model2"];'}),

        ({'TC_GEN_STORM_ID': 'al062018, al092018'},
         {'METPLUS_STORM_ID': 'storm_id = ["al062018", "al092018"];'}),

        ({'TC_GEN_STORM_NAME': 'al062018, al092018'},
         {'METPLUS_STORM_NAME': 'storm_name = ["al062018", "al092018"];'}),

        ({'TC_GEN_INIT_BEG': '20160201_123045'},
         {'METPLUS_INIT_BEG': 'init_beg = "20160201_123045";'}),

        ({'TC_GEN_INIT_END': '20160201_123045'},
         {'METPLUS_INIT_END': 'init_end = "20160201_123045";'}),

        ({'TC_GEN_INIT_INC': '20160201_123045, 20160202_123045'},
         {'METPLUS_INIT_INC': ('init_inc = ["20160201_123045", '
                               '"20160202_123045"];')}),

        ({'TC_GEN_INIT_EXC': '20160201_123045, 20160202_123045'},
         {'METPLUS_INIT_EXC': ('init_exc = ["20160201_123045", '
                              '"20160202_123045"];')}),

        ({'TC_GEN_VALID_BEG': '20160201_123045'},
         {'METPLUS_VALID_BEG': 'valid_beg = "20160201_123045";'}),

        ({'TC_GEN_VALID_END': '20160201_123045'},
         {'METPLUS_VALID_END': 'valid_end = "20160201_123045";'}),

        ({'TC_GEN_INIT_HOUR': '123045, 123045'},
         {'METPLUS_INIT_HOUR': ('init_hour = ["123045", '
                               '"123045"];')}),

        ({'LEAD_SEQ': '12, 15'},
         {'METPLUS_LEAD': ('lead = ["12", "15"];')}),

        ({'TC_GEN_VX_MASK': 'my_vx_mask'},
         {'METPLUS_VX_MASK': 'vx_mask = "my_vx_mask";'}),

        ({'TC_GEN_BASIN_MASK': 'basin_mask1, basin_mask2'},
         {'METPLUS_BASIN_MASK': 'basin_mask = ["basin_mask1", "basin_mask2"];'}),

        ({'TC_GEN_DLAND_THRESH': '>12'},
         {'METPLUS_DLAND_THRESH': 'dland_thresh = >12;'}),

        ({'TC_GEN_GENESIS_MATCH_RADIUS': '502'},
         {'METPLUS_GENESIS_MATCH_RADIUS': 'genesis_match_radius = 502;'}),

        ({'TC_GEN_DEV_HIT_RADIUS': '502'},
         {'METPLUS_DEV_HIT_RADIUS': 'dev_hit_radius = 502;'}),

        ({'TC_GEN_DEV_HIT_WINDOW_BEG': '-30'},
         {'METPLUS_DEV_HIT_WINDOW_DICT': 'dev_hit_window = {beg = -30;}'}),

        ({'TC_GEN_DEV_HIT_WINDOW_BEGIN': '-30'},
         {'METPLUS_DEV_HIT_WINDOW_DICT': 'dev_hit_window = {beg = -30;}'}),

        ({'TC_GEN_DEV_HIT_WINDOW_END': '30'},
         {'METPLUS_DEV_HIT_WINDOW_DICT': 'dev_hit_window = {end = 30;}'}),

        ({'TC_GEN_DEV_HIT_WINDOW_BEG': '-30',
          'TC_GEN_DEV_HIT_WINDOW_END': '30'},
         {'METPLUS_DEV_HIT_WINDOW_DICT': 'dev_hit_window = {beg = -30;end = 30;}'}),

        ({'TC_GEN_DISCARD_INIT_POST_GENESIS_FLAG': 'False'},
         {'METPLUS_DISCARD_INIT_POST_GENESIS_FLAG': 'discard_init_post_genesis_flag = FALSE;'}),

        ({'TC_GEN_DEV_METHOD_FLAG': 'False'},
         {'METPLUS_DEV_METHOD_FLAG': 'dev_method_flag = FALSE;'}),

        ({'TC_GEN_OPS_METHOD_FLAG': 'False'},
         {'METPLUS_OPS_METHOD_FLAG': 'ops_method_flag = FALSE;'}),

        ({'TC_GEN_CI_ALPHA': '0.06'},
         {'METPLUS_CI_ALPHA': 'ci_alpha = 0.06;'}),

        ({'TC_GEN_OUTPUT_FLAG_FHO': 'BOTH'},
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {fho = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_CTC': 'NONE'},
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {ctc = NONE;}'}),

        ({'TC_GEN_OUTPUT_FLAG_CTS': 'BOTH'},
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {cts = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_PCT': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pct = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_PSTD': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pstd = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_PJC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {pjc = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_PRC': 'BOTH', },
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {prc = BOTH;}'}),

        ({'TC_GEN_OUTPUT_FLAG_GENMPR': 'NONE'},
         {'METPLUS_OUTPUT_FLAG_DICT': 'output_flag = {genmpr = NONE;}'}),

        ({'TC_GEN_OUTPUT_FLAG_FHO': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_CTC': 'NONE',
          'TC_GEN_OUTPUT_FLAG_CTS': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_PCT': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_PSTD': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_PJC': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_PRC': 'BOTH',
          'TC_GEN_OUTPUT_FLAG_GENMPR': 'NONE',
          },
         {'METPLUS_OUTPUT_FLAG_DICT': ('output_flag = {fho = BOTH;ctc = NONE;'
                                       'cts = BOTH;pct = BOTH;pstd = BOTH;'
                                       'pjc = BOTH;prc = BOTH;genmpr = NONE;}')
          }),

        ({'TC_GEN_NC_PAIRS_FLAG_LATLON': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {latlon = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_FCST_GENESIS': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {fcst_genesis = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_FCST_TRACKS': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {fcst_tracks = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_FCST_FY_OY': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {fcst_fy_oy = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_FCST_FY_ON': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {fcst_fy_on = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_BEST_GENESIS': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {best_genesis = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_BEST_TRACKS': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {best_tracks = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_BEST_FY_OY': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {best_fy_oy = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_BEST_FN_OY': 'false'},
         {'METPLUS_NC_PAIRS_FLAG_DICT': 'nc_pairs_flag = {best_fn_oy = FALSE;}'}),

        ({'TC_GEN_NC_PAIRS_FLAG_LATLON': 'false',
          'TC_GEN_NC_PAIRS_FLAG_FCST_GENESIS': 'false',
          'TC_GEN_NC_PAIRS_FLAG_FCST_TRACKS': 'false',
          'TC_GEN_NC_PAIRS_FLAG_FCST_FY_OY': 'false',
          'TC_GEN_NC_PAIRS_FLAG_FCST_FY_ON': 'false',
          'TC_GEN_NC_PAIRS_FLAG_BEST_GENESIS': 'false',
          'TC_GEN_NC_PAIRS_FLAG_BEST_TRACKS': 'false',
          'TC_GEN_NC_PAIRS_FLAG_BEST_FY_OY': 'false',
          'TC_GEN_NC_PAIRS_FLAG_BEST_FN_OY': 'false',
          },
         {'METPLUS_NC_PAIRS_FLAG_DICT': ('nc_pairs_flag = {latlon = FALSE;'
                                         'fcst_genesis = FALSE;'
                                         'fcst_tracks = FALSE;'
                                         'fcst_fy_oy = FALSE;'
                                         'fcst_fy_on = FALSE;'
                                         'best_genesis = FALSE;'
                                         'best_tracks = FALSE;'
                                         'best_fy_oy = FALSE;'
                                         'best_fn_oy = FALSE;'
                                         '}')}),

        ({'TC_GEN_VALID_MINUS_GENESIS_DIFF_THRESH': '>4'},
         {'METPLUS_VALID_MINUS_GENESIS_DIFF_THRESH': 'valid_minus_genesis_diff_thresh = >4;'}),

        ({'TC_GEN_BEST_UNIQUE_FLAG': 'false'},
         {'METPLUS_BEST_UNIQUE_FLAG': 'best_unique_flag = FALSE;'}),

        ({'TC_GEN_DLAND_FILE': 'MET_BASE/other_file.nc'},
         {'METPLUS_DLAND_FILE': 'dland_file = "MET_BASE/other_file.nc";'}),

        ({'TC_GEN_BASIN_FILE': 'MET_BASE/other_basin.nc'},
         {'METPLUS_BASIN_FILE': 'basin_file = "MET_BASE/other_basin.nc";'}),

        ({'TC_GEN_NC_PAIRS_GRID': 'G004'},
         {'METPLUS_NC_PAIRS_GRID': 'nc_pairs_grid = "G004";'}),

        ({'TC_GEN_GENESIS_MATCH_POINT_TO_TRACK': 'False', },
         {'METPLUS_GENESIS_MATCH_POINT_TO_TRACK': 'genesis_match_point_to_track = FALSE;'}),

        ({'TC_GEN_GENESIS_MATCH_WINDOW_BEG': '-1', },
         {
             'METPLUS_GENESIS_MATCH_WINDOW_DICT': 'genesis_match_window = {beg = -1;}'}),

        ({'TC_GEN_GENESIS_MATCH_WINDOW_END': '2', },
         {
             'METPLUS_GENESIS_MATCH_WINDOW_DICT': 'genesis_match_window = {end = 2;}'}),

        ({
             'TC_GEN_GENESIS_MATCH_WINDOW_BEG': '-2',
             'TC_GEN_GENESIS_MATCH_WINDOW_END': '1',
         },
         {'METPLUS_GENESIS_MATCH_WINDOW_DICT': 'genesis_match_window = {beg = -2;end = 1;}'}),
        ({'TC_GEN_OPS_HIT_WINDOW_BEG': '1', },
         {'METPLUS_OPS_HIT_WINDOW_DICT': 'ops_hit_window = {beg = 1;}'}),

        ({'TC_GEN_OPS_HIT_WINDOW_END': '47', },
         {'METPLUS_OPS_HIT_WINDOW_DICT': 'ops_hit_window = {end = 47;}'}),

        ({
             'TC_GEN_OPS_HIT_WINDOW_BEG': '1',
             'TC_GEN_OPS_HIT_WINDOW_END': '47',
         },
         {'METPLUS_OPS_HIT_WINDOW_DICT': 'ops_hit_window = {beg = 1;end = 47;}'}),

    ]
)
@pytest.mark.wrapper_a
def test_tc_gen(metplus_config, config_overrides, env_var_values):
    # expected number of 2016 files (including file_list line)
    expected_genesis_count = 7
    expected_track_count = expected_genesis_count
    expected_edeck_count = 6
    expected_shape_count = 5

    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal', 'tests',
                                 'data',
                                 'tc_gen')
    track_dir = os.path.join(test_data_dir, 'track')
    genesis_dir = os.path.join(test_data_dir, 'genesis')
    edeck_dir = os.path.join(test_data_dir, 'edeck')
    shape_dir = os.path.join(test_data_dir, 'shape')

    track_template = 'track_*{init?fmt=%Y}*'
    genesis_template = 'genesis_*{init?fmt=%Y}*'
    edeck_template = 'edeck_*{init?fmt=%Y}*'
    shape_template = 'shape_*{init?fmt=%Y}*'

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCGen')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y')
    config.set('config', 'INIT_BEG', '2016')
    config.set('config', 'LOOP_ORDER', 'processes')

    config.set('config', 'TC_GEN_TRACK_INPUT_DIR', track_dir)
    config.set('config', 'TC_GEN_TRACK_INPUT_TEMPLATE', track_template)
    config.set('config', 'TC_GEN_GENESIS_INPUT_DIR', genesis_dir)
    config.set('config', 'TC_GEN_GENESIS_INPUT_TEMPLATE', genesis_template)
    config.set('config', 'TC_GEN_EDECK_INPUT_DIR', edeck_dir)
    config.set('config', 'TC_GEN_EDECK_INPUT_TEMPLATE', edeck_template)
    config.set('config', 'TC_GEN_SHAPE_INPUT_DIR', shape_dir)
    config.set('config', 'TC_GEN_SHAPE_INPUT_TEMPLATE', shape_template)
    config.set('config', 'TC_GEN_OUTPUT_DIR', '{OUTPUT_BASE}/TCGen/output')
    config.set('config', 'TC_GEN_OUTPUT_TEMPLATE',
               'tc_gen_{custom}_{init?fmt=%Y}')

    config.set('config', 'TC_GEN_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCGenConfig_wrapped')

    config.set('config', 'TC_GEN_CUSTOM_LOOP_LIST', 'a, b')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCGenWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    file_list_dir = os.path.join(wrapper.config.getdir('STAGING_DIR'),
                                 'file_lists')
    genesis_path = os.path.join(file_list_dir,
                                '20160101000000_tc_gen_genesis.txt')
    edeck_path = os.path.join(file_list_dir,
                              '20160101000000_tc_gen_edeck.txt')
    shape_path = os.path.join(file_list_dir,
                              '20160101000000_tc_gen_shape.txt')
    track_path = os.path.join(file_list_dir,
                              '20160101000000_tc_gen_track.txt')

    # remove list files if they already exist
    for the_path in (genesis_path, edeck_path, shape_path, track_path):
        if os.path.exists(the_path):
            os.remove(the_path)

    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [
        (f"{app_path} {verbosity} "
         f"-genesis {genesis_path} "
         f"-edeck {edeck_path} "
         f"-shape {shape_path} "
         f"-track {track_path} "
         f"-config {config_file} -out {out_dir}/tc_gen_a_2016"),
        (f"{app_path} {verbosity} "
         f"-genesis {genesis_path} "
         f"-edeck {edeck_path} "
         f"-shape {shape_path} "
         f"-track {track_path} "
         f"-config {config_file} -out {out_dir}/tc_gen_b_2016"),
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
            assert match is not None
            value = match.split('=', 1)[1]
            assert env_var_values.get(env_var_key, '') == value

    # verify file count of genesis, edeck, shape, and track file list files
    with open(genesis_path, 'r') as file_handle:
        lines = file_handle.read().splitlines()
    assert len(lines) == expected_genesis_count

    with open(edeck_path, 'r') as file_handle:
        lines = file_handle.read().splitlines()
    assert len(lines) == expected_edeck_count

    with open(shape_path, 'r') as file_handle:
        lines = file_handle.read().splitlines()
    assert len(lines) == expected_shape_count

    with open(track_path, 'r') as file_handle:
        lines = file_handle.read().splitlines()
    assert len(lines) == expected_track_count


@pytest.mark.wrapper_a
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config()
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCGenConfig_wrapped')

    wrapper = TCGenWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_GEN_CONFIG_FILE', fake_config_name)
    wrapper = TCGenWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
