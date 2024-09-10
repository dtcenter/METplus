#!/usr/bin/env python3

import pytest

import os
import datetime

from metplus.wrappers.mtd_wrapper import MTDWrapper

fcst_dir = '/some/path/fcst'
obs_dir = '/some/path/obs'
fcst_name = 'APCP'
fcst_level = 'A03'
fcst_thresh = 'gt12.7'
obs_name = 'APCP_03'
obs_level_no_quotes = '(*,*)'
obs_level = f'"{obs_level_no_quotes}"'
obs_thresh = 'gt12.7'
fcst_fmt = f'field = {{ name="{fcst_name}"; level="{fcst_level}"; cat_thresh=[ gt12.7 ]; }};'
obs_fmt = (f'field = {{ name="{obs_name}"; '
           f'level="{obs_level_no_quotes}"; cat_thresh=[ gt12.7 ]; }};')


def mtd_wrapper(metplus_config, config_overrides):
    """! Returns a default MTDWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'BOTH_VAR1_NAME', 'APCP')
    config.set('config', 'BOTH_VAR1_LEVELS', 'A06')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'MTD_CONV_THRESH', '>=10')
    config.set('config', 'MTD_CONV_RADIUS', '15')
    for key, value in config_overrides.items():
        config.set('config', key, value)

    return MTDWrapper(config)


def set_minimum_config_settings(config, set_inputs=True):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'MTD')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080700')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '6H, 9H, 12H')
    config.set('config', 'MTD_CONFIG_FILE',
               '{PARM_BASE}/met_config/MTDConfig_wrapped')
    if set_inputs:
        config.set('config', 'FCST_MTD_INPUT_DIR', fcst_dir)
        config.set('config', 'OBS_MTD_INPUT_DIR', obs_dir)
        config.set('config', 'FCST_MTD_INPUT_TEMPLATE',
                   '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
        config.set('config', 'OBS_MTD_INPUT_TEMPLATE',
                   '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'MTD_OUTPUT_DIR',
               '{OUTPUT_BASE}/MTD/output')
    config.set('config', 'MTD_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'FCST_VAR1_THRESH', fcst_thresh)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)
    config.set('config', 'OBS_VAR1_THRESH', obs_thresh)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing, inputs', [
        (1, 3, 0.3, 0, True, 'CHOCOLATE'),
        (1, 3, 0.3, 0, True, 'BOTH'),
        (1, 3, 0.8, 1, True, 'BOTH'),
        (1, 3, 0.8, 1, False, 'BOTH'),
        (1, 3, 0.3, 0, True, 'FCST'),
        (1, 3, 0.8, 1, True, 'FCST'),
        (1, 3, 0.8, 1, False, 'FCST'),
        (1, 3, 0.3, 0, True, 'OBS'),
        (1, 3, 0.8, 1, True, 'OBS'),
        (1, 3, 0.8, 1, False, 'OBS'),
    ]
)
@pytest.mark.wrapper_a
def test_mtd_missing_inputs(metplus_config, get_test_data_dir,
                            missing, run, thresh, errors, allow_missing, inputs):
    config = metplus_config
    set_minimum_config_settings(config, set_inputs=False)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'MTD_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'MTD_INPUT_THRESH', thresh)
    config.set('config', 'INIT_LIST', '2017051001, 2017051003, 2017051303')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    if inputs in ('BOTH', 'FCST'):
        config.set('config', 'FCST_MTD_INPUT_DIR', get_test_data_dir('fcst'))
        config.set('config', 'FCST_MTD_INPUT_TEMPLATE',
                   '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    if inputs in ('BOTH', 'OBS'):
        config.set('config', 'OBS_MTD_INPUT_DIR', get_test_data_dir('obs'))
        config.set('config', 'OBS_MTD_INPUT_TEMPLATE',
                   '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
    if inputs != 'BOTH':
        config.set('config', 'MTD_SINGLE_RUN', True)
        config.set('config', 'MTD_SINGLE_DATA_SRC', inputs)

    wrapper = MTDWrapper(config)
    if inputs == 'CHOCOLATE':
        assert not wrapper.isOK
        return

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

        ({'MTD_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'MTD_REGRID_TO_GRID': 'FCST',},
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'MTD_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'MTD_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'MTD_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'MTD_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'MTD_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'MTD_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'MTD_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'MTD_REGRID_TO_GRID': 'FCST',
          'MTD_REGRID_METHOD': 'NEAREST',
          'MTD_REGRID_WIDTH': '1',
          'MTD_REGRID_VLD_THRESH': '0.5',
          'MTD_REGRID_SHAPE': 'SQUARE',
          'MTD_REGRID_CONVERT': '2*x',
          'MTD_REGRID_CENSOR_THRESH': '>12000,<5000',
          'MTD_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )}),

        ({'FCST_MTD_CONV_RADIUS': '40.0/grid_res'},
         {'METPLUS_FCST_CONV_RADIUS': 'conv_radius = 40.0/grid_res;'}),

        ({'OBS_MTD_CONV_RADIUS': '40.0/grid_res'},
         {'METPLUS_OBS_CONV_RADIUS': 'conv_radius = 40.0/grid_res;'}),

        ({'FCST_MTD_CONV_THRESH': '>=10.0'},
         {'METPLUS_FCST_CONV_THRESH': 'conv_thresh = >=10.0;'}),

        ({'OBS_MTD_CONV_THRESH': '>=10.0'},
         {'METPLUS_OBS_CONV_THRESH': 'conv_thresh = >=10.0;'}),

        ({'MTD_MIN_VOLUME': '1000'},
         {'METPLUS_MIN_VOLUME': 'min_volume = 1000;'}),

        ({'MTD_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'MTD_TIME_OFFSET_WARNING': 3},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 3;'}),
        ({'TIME_OFFSET_WARNING': 2},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 2;'}),
        ({'TIME_OFFSET_WARNING': 2, 'MTD_TIME_OFFSET_WARNING': 4},
         {'METPLUS_TIME_OFFSET_WARNING': 'time_offset_warning = 4;'}),
    ]
)
@pytest.mark.wrapper
def test_mode_single_field(metplus_config, config_overrides, env_var_values,
                           compare_command_and_env_vars):
    config = metplus_config

    # set config variables needed to run
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = MTDWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"-fcst {file_list_dir}/"
                      f"20050807060000_mtd_fcst_{fcst_name}.txt "
                      f"-obs {file_list_dir}/"
                      f"20050807060000_mtd_obs_{obs_name}.txt "
                      f"-config {config_file} "
                      f"-outdir {out_dir}/2005080706"),
                     ]

    all_cmds = wrapper.run_all_times()
    special_values = {
        'METPLUS_FCST_FIELD': fcst_fmt,
        'METPLUS_OBS_FIELD': obs_fmt,
    }
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values,
                                 wrapper, special_values)


@pytest.mark.wrapper
def test_mtd_by_init_all_found(metplus_config, get_test_data_dir):
    obs_data_dir = get_test_data_dir('obs')
    fcst_data_dir = get_test_data_dir('fcst')
    overrides = {
        'LEAD_SEQ': '1,2,3',
        'FCST_MTD_INPUT_DIR': fcst_data_dir,
        'OBS_MTD_INPUT_DIR': obs_data_dir,
        'FCST_MTD_INPUT_TEMPLATE': "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2",
        'OBS_MTD_INPUT_TEMPLATE': "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc",
        'LOOP_BY': 'INIT',
        'INIT_TIME_FMT': '%Y%m%d%H%M',
        'INIT_BEG': '201705100300'
    }
    mw = mtd_wrapper(metplus_config, overrides)
    mw.run_all_times()
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510040000_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510040000_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    # remove file_list line from lists
    fcst_list = fcst_list[1:]
    obs_list = obs_list[1:]

    assert(fcst_list[0] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f001_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f002_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051004_A06.nc') and
           obs_list[1] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051005_A06.nc') and
           obs_list[2] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051006_A06.nc')
           )


@pytest.mark.wrapper
def test_mtd_by_valid_all_found(metplus_config, get_test_data_dir):
    obs_data_dir = get_test_data_dir('obs')
    fcst_data_dir = get_test_data_dir('fcst')
    overrides = {
        'LEAD_SEQ': '1, 2, 3',
        'FCST_MTD_INPUT_DIR': fcst_data_dir,
        'OBS_MTD_INPUT_DIR': obs_data_dir,
        'FCST_MTD_INPUT_TEMPLATE': "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2",
        'OBS_MTD_INPUT_TEMPLATE': "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc",
        'LOOP_BY': 'VALID',
        'VALID_TIME_FMT': '%Y%m%d%H%M',
        'VALID_BEG': '201705100300'
    }
    mw = mtd_wrapper(metplus_config, overrides)
    mw.run_all_times()
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510030000_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510030000_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    # remove file_list line from lists
    fcst_list = fcst_list[1:]
    obs_list = obs_list[1:]

    assert(fcst_list[0] == os.path.join(fcst_data_dir,'20170510', '20170510_i02_f001_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_data_dir,'20170510', '20170510_i01_f002_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_data_dir,'20170510', '20170510_i00_f003_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051003_A06.nc') and
           obs_list[1] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051003_A06.nc') and
           obs_list[2] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051003_A06.nc')
           )


@pytest.mark.wrapper
def test_mtd_by_init_miss_fcst(metplus_config, get_test_data_dir):
    obs_data_dir = get_test_data_dir('obs')
    fcst_data_dir = get_test_data_dir('fcst')
    overrides = {
        'LEAD_SEQ': '3, 6, 9, 12',
        'FCST_MTD_INPUT_DIR': fcst_data_dir,
        'OBS_MTD_INPUT_DIR': obs_data_dir,
        'FCST_MTD_INPUT_TEMPLATE': "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2",
        'OBS_MTD_INPUT_TEMPLATE': "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc",
        'LOOP_BY': 'INIT',
        'INIT_TIME_FMT': '%Y%m%d%H%M',
        'INIT_BEG': '201705100300'
    }
    mw = mtd_wrapper(metplus_config, overrides)
    mw.run_all_times()
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510060000_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510060000_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    # remove file_list line from lists
    fcst_list = fcst_list[1:]
    obs_list = obs_list[1:]

    assert(fcst_list[0] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f006_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f012_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051006_A06.nc') and
           obs_list[1] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051009_A06.nc') and
           obs_list[2] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051015_A06.nc')
           )


@pytest.mark.wrapper
def test_mtd_by_init_miss_both(metplus_config, get_test_data_dir):
    obs_data_dir = get_test_data_dir('obs')
    fcst_data_dir = get_test_data_dir('fcst')
    overrides = {
        'LEAD_SEQ': '6, 12, 18',
        'FCST_MTD_INPUT_DIR': fcst_data_dir,
        'OBS_MTD_INPUT_DIR': obs_data_dir,
        'FCST_MTD_INPUT_TEMPLATE': "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2",
        'OBS_MTD_INPUT_TEMPLATE': "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc",
        'LOOP_BY': 'INIT',
        'INIT_TIME_FMT': '%Y%m%d%H%M',
        'INIT_BEG': '201705100300'
    }
    mw = mtd_wrapper(metplus_config, overrides)
    mw.run_all_times()
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510090000_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510090000_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    # remove file_list line from lists
    fcst_list = fcst_list[1:]
    obs_list = obs_list[1:]

    assert(fcst_list[0] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f006_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f012_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051009_A06.nc') and
           obs_list[1] == os.path.join(obs_data_dir,'20170510', 'qpe_2017051015_A06.nc')
           )


@pytest.mark.wrapper
def test_mtd_single(metplus_config, get_test_data_dir):
    fcst_data_dir = get_test_data_dir('fcst')
    overrides = {
        'LEAD_SEQ': '1, 2, 3',
        'MTD_SINGLE_RUN': True,
        'MTD_SINGLE_DATA_SRC': 'FCST',
        'FCST_MTD_INPUT_DIR': fcst_data_dir,
        'FCST_MTD_INPUT_TEMPLATE': "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2",
        'LOOP_BY': 'INIT',
        'INIT_TIME_FMT': '%Y%m%d%H%M',
        'INIT_BEG': '201705100300'
    }
    mw = mtd_wrapper(metplus_config, overrides)
    mw.run_all_times()
    single_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '20170510040000_mtd_single_APCP.txt')
    with open(single_list_file) as f:
        single_list = f.readlines()
    single_list = [x.strip() for x in single_list]

    # remove file_list line from lists
    single_list = single_list[1:]

    assert(single_list[0] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f001_HRRRTLE_PHPT.grb2') and
           single_list[1] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f002_HRRRTLE_PHPT.grb2') and
           single_list[2] == os.path.join(fcst_data_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2')
           )


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'MTDConfig_wrapped')

    wrapper = MTDWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'MTD_CONFIG_FILE', fake_config_name)
    wrapper = MTDWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
