import pytest

import os

from metplus.wrappers.ioda2nc_wrapper import IODA2NCWrapper

time_fmt = '%Y%m%d%H'
run_times = ['2020031012', '2020031100']


def set_minimum_config_settings(config):
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'IODA2NC')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', time_fmt)
    config.set('config', 'VALID_BEG', run_times[0])
    config.set('config', 'VALID_END', run_times[-1])
    config.set('config', 'VALID_INCREMENT', '12H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'IODA2NC_INPUT_DIR',
               '{INPUT_BASE}/met_test/new/ioda')
    config.set('config', 'IODA2NC_INPUT_TEMPLATE',
               'ioda.NC001007.{valid?fmt=%Y%m%d%H}.nc')
    config.set('config', 'IODA2NC_OUTPUT_DIR',
               '{OUTPUT_BASE}/ioda2nc')
    config.set('config', 'IODA2NC_OUTPUT_TEMPLATE',
               'ioda.NC001007.{valid?fmt=%Y%m%d%H}.summary.nc')


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing, runtime_freq', [
        (16, 24, 0.3, 0, True, 'RUN_ONCE_FOR_EACH'),
        (16, 24, 0.7, 1, True, 'RUN_ONCE_FOR_EACH'),
        (16, 24, 0.3, 16, False, 'RUN_ONCE_FOR_EACH'),
        (2, 4, 0.4, 0, True, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (2, 4, 0.6, 1, True, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (2, 4, 0.6, 2, False, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (2, 5, 0.4, 0, True, 'RUN_ONCE_PER_LEAD'),
        (2, 5, 0.7, 1, True, 'RUN_ONCE_PER_LEAD'),
        (2, 5, 0.4, 2, False, 'RUN_ONCE_PER_LEAD'),
        (0, 1, 0.4, 0, True, 'RUN_ONCE'),
        (0, 1, 0.4, 0, False, 'RUN_ONCE'),
    ]
)
@pytest.mark.wrapper
def test_ioda2nc_missing_inputs(metplus_config, get_test_data_dir, missing,
                                run, thresh, errors, allow_missing, runtime_freq):
    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'IODA2NC_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'IODA2NC_INPUT_THRESH', thresh)
    config.set('config', 'IODA2NC_RUNTIME_FREQ', runtime_freq)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_LIST', '2017051001, 2017051003, 2017051201, 2017051203')
    if runtime_freq == 'RUN_ONCE_PER_LEAD':
        config.set('config', 'LEAD_SEQ', '6,9,12,15,18')
    else:
        config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'IODA2NC_INPUT_DIR', get_test_data_dir('obs'))
    config.set('config', 'IODA2NC_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
    config.set('config', 'IODA2NC_OUTPUT_TEMPLATE', '{OUTPUT_BASE}/IODA2NC/output/test.nc')

    wrapper = IODA2NCWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


@pytest.mark.parametrize(
    'config_overrides, env_var_values, extra_args', [
        # 0
        ({'IODA2NC_MESSAGE_TYPE': 'ADPUPA, ADPSFC', },
         {'METPLUS_MESSAGE_TYPE': 'message_type = ["ADPUPA", "ADPSFC"];'}, ''),
        # 1
        ({'IODA2NC_MESSAGE_TYPE_MAP': '{ key = “AIRCAR”; val = “AIRCAR_PROFILES”; }', },
         {'METPLUS_MESSAGE_TYPE_MAP': 'message_type_map = [{ key = “AIRCAR”; val = “AIRCAR_PROFILES”; }];'}, ''),
        # 2
        ({'IODA2NC_MESSAGE_TYPE_GROUP_MAP': '{ key = "SURFACE"; val = "ADPSFC,SFCSHP,MSONET";},{ key = "ANYAIR";  val = "AIRCAR,AIRCFT";}', },
         {'METPLUS_MESSAGE_TYPE_GROUP_MAP': 'message_type_group_map = [{ key = "SURFACE"; val = "ADPSFC,SFCSHP,MSONET";}, { key = "ANYAIR";  val = "AIRCAR,AIRCFT";}];'}, ''),
        # 3
        ({'IODA2NC_STATION_ID': 'value1, value2', },
         {'METPLUS_STATION_ID': 'station_id = ["value1", "value2"];'}, ''),
        # 4
        ({'IODA2NC_OBS_WINDOW_BEG': '-5400', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -5400;}'}, ''),
        # 5
        ({'IODA2NC_OBS_WINDOW_END': '5400', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {end = 5400;}'}, ''),
        # 6
        ({
             'IODA2NC_OBS_WINDOW_BEG': '-5400',
             'IODA2NC_OBS_WINDOW_END': '5400',
         },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -5400;end = 5400;}'}
         , ''),
        # 7
        ({'IODA2NC_MASK_GRID': 'FULL', },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";}'}, ''),
        # 8
        ({'IODA2NC_MASK_POLY': '/some/polyfile.nc', },
         {'METPLUS_MASK_DICT': 'mask = {poly = "/some/polyfile.nc";}'}, ''),
        # 9
        ({
             'IODA2NC_MASK_GRID': 'FULL',
             'IODA2NC_MASK_POLY': '/some/polyfile.nc',
         },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";poly = "/some/polyfile.nc";}'}, ''),
        # 10
        ({'IODA2NC_ELEVATION_RANGE_BEG': '-1000', },
         {'METPLUS_ELEVATION_RANGE_DICT': 'elevation_range = {beg = -1000;}'}, ''),
        # 11
        ({'IODA2NC_ELEVATION_RANGE_END': '100000', },
         {'METPLUS_ELEVATION_RANGE_DICT': 'elevation_range = {end = 100000;}'}, ''),
        # 12
        ({
             'IODA2NC_ELEVATION_RANGE_BEG': '-1000',
             'IODA2NC_ELEVATION_RANGE_END': '100000',
         },
         {'METPLUS_ELEVATION_RANGE_DICT': 'elevation_range = {beg = -1000;end = 100000;}'}, ''),
        # 13
        ({'IODA2NC_LEVEL_RANGE_BEG': '1', },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {beg = 1;}'}, ''),
        # 14
        ({'IODA2NC_LEVEL_RANGE_END': '255', },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {end = 255;}'}, ''),
        # 15
        ({
             'IODA2NC_LEVEL_RANGE_BEG': '1',
             'IODA2NC_LEVEL_RANGE_END': '255',
         },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {beg = 1;end = 255;}'}, ''),
        # 16
        ({'IODA2NC_OBS_VAR': 'TMP,WDIR,RH', },
         {'METPLUS_OBS_VAR': 'obs_var = ["TMP", "WDIR", "RH"];'}, ''),
        # 17
        ({'IODA2NC_OBS_NAME_MAP': '{ key = "message_type"; val = "msg_type"; },{ key = "station_id";   val = "report_identifier"; }', },
         {'METPLUS_OBS_NAME_MAP': 'obs_name_map = [{ key = "message_type"; val = "msg_type"; }, { key = "station_id";   val = "report_identifier"; }];'}, ''),
        # 18
        ({'IODA2NC_METADATA_MAP': '{ key = "message_type"; val = "msg_type"; },{ key = "station_id";   val = "report_identifier"; }', },
         {'METPLUS_METADATA_MAP': 'metadata_map = [{ key = "message_type"; val = "msg_type"; }, { key = "station_id";   val = "report_identifier"; }];'}, ''),
        # 19
        ({'IODA2NC_MISSING_THRESH': '<=-1e9, >=1e9, ==-9999', },
         {'METPLUS_MISSING_THRESH': 'missing_thresh = [<=-1e9, >=1e9, ==-9999];'}, ''),
        # 20
        ({'IODA2NC_QUALITY_MARK_THRESH': '2', },
         {'METPLUS_QUALITY_MARK_THRESH': 'quality_mark_thresh = 2;'}, ''),
        # 21
        ({},
         {'METPLUS_TIME_SUMMARY_DICT': ''}, ''),
        # 22
        ({'IODA2NC_TIME_SUMMARY_FLAG': 'True'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {flag = TRUE;}'}, ''),
        # 23
        ({'IODA2NC_TIME_SUMMARY_RAW_DATA': 'true'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {raw_data = TRUE;}'}, ''),
        # 24
        ({'IODA2NC_TIME_SUMMARY_BEG': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {beg = "123456";}'}, ''),
        # 25
        ({'IODA2NC_TIME_SUMMARY_END': '123456'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {end = "123456";}'}, ''),
        # 26
        ({'IODA2NC_TIME_SUMMARY_STEP': '500'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {step = 500;}'}, ''),
        # 27
        ({'IODA2NC_TIME_SUMMARY_WIDTH': '900'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {width = 900;}'}, ''),
        # 28 width as dictionary
        ({'IODA2NC_TIME_SUMMARY_WIDTH': '{ beg = -21600; end = 0; }'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {width = { beg = -21600; end = 0; };}'}, ''),
        # 29
        ({'IODA2NC_TIME_SUMMARY_GRIB_CODE': '12, 203, 212'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {grib_code = [12, 203, 212];}'}, ''),
        # 30
        ({'IODA2NC_TIME_SUMMARY_OBS_VAR': 'TMP, HGT, PRES'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {obs_var = ["TMP", "HGT", "PRES"];}'}, ''),
        # 31
        ({'IODA2NC_TIME_SUMMARY_TYPE': 'min, range, max'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {type = ["min", "range", "max"];}'}, ''),
        # 32
        ({'IODA2NC_TIME_SUMMARY_VALID_FREQ': '2'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {vld_freq = 2;}'}, ''),
        # 33
        ({'IODA2NC_TIME_SUMMARY_VALID_THRESH': '0.5'},
         {'METPLUS_TIME_SUMMARY_DICT':
          'time_summary = {vld_thresh = 0.5;}'}, ''),
        # 34 additional input file with full path
        ({'IODA2NC_INPUT_TEMPLATE': 'ioda.NC001007.{valid?fmt=%Y%m%d%H}.nc, /other/file.nc'},
         {}, ' -iodafile /other/file.nc'),
        # 35 additional input file with relative path
        ({'IODA2NC_INPUT_TEMPLATE': 'ioda.NC001007.{valid?fmt=%Y%m%d%H}.nc, other/file.nc'},
         {}, ' -iodafile *INPUT_DIR*/other/file.nc'),
        # 36
        ({'IODA2NC_VALID_BEG': '20200309_12'},
         {}, ' -valid_beg 20200309_12'),
        # 37
        ({'IODA2NC_VALID_END': '20200310_12'},
         {}, ' -valid_end 20200310_12'),
        # 38
        ({'IODA2NC_NMSG': '10'},
         {}, ' -nmsg 10'),
        # 39 all optional command line args
        ({'IODA2NC_INPUT_TEMPLATE': 'ioda.NC001007.{valid?fmt=%Y%m%d%H}.nc, other/file.nc',
          'IODA2NC_VALID_BEG': '20200309_12',
          'IODA2NC_VALID_END': '20200310_12',
          'IODA2NC_NMSG': '10',
          },
         {}, ' -iodafile *INPUT_DIR*/other/file.nc -valid_beg 20200309_12 -valid_end 20200310_12 -nmsg 10'),

    ]
)
@pytest.mark.wrapper
def test_ioda2nc_wrapper(metplus_config, config_overrides,
                         env_var_values, extra_args, compare_command_and_env_vars):
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = IODA2NCWrapper(config)
    assert wrapper.isOK

    input_dir = wrapper.c_dict.get('OBS_INPUT_DIR')
    output_dir = wrapper.c_dict.get('OUTPUT_DIR')

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')

    extra_args = extra_args.replace('*INPUT_DIR*', input_dir)
    expected_cmds = [
        (f"{app_path} {verbosity} {input_dir}/ioda.NC001007.2020031012.nc"
         f" {output_dir}/ioda.NC001007.2020031012.summary.nc"
         f" -config {config_file}{extra_args}"),
        (f"{app_path} {verbosity} {input_dir}/ioda.NC001007.2020031100.nc"
         f" {output_dir}/ioda.NC001007.2020031100.summary.nc"
         f" -config {config_file}{extra_args}"),
    ]

    all_cmds = wrapper.run_all_times()
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values, wrapper)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'
    config = metplus_config
    config.set('config', 'INPUT_MUST_EXIST', False)

    wrapper = IODA2NCWrapper(config)

    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'IODA2NCConfig_wrapped')

    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'IODA2NC_CONFIG_FILE', fake_config_name)
    wrapper = IODA2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
