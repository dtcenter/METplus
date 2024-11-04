#!/usr/bin/env python3

import pytest

import os
import datetime

from metplus.wrappers.pb2nc_wrapper import PB2NCWrapper

from metplus.util import time_util
from metplus.util import do_string_sub

valid_beg = '20141031_18'
valid_end = '20141031_23'


def pb2nc_wrapper(metplus_config):
    """! Returns a default PB2NCWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values.
    """
    config = metplus_config
    config.set('config', 'PB2NC_INPUT_TEMPLATE',
               't{da_init?fmt=%2H}z.prepbufr.tm{offset?fmt=%2H}')
    return PB2NCWrapper(config)


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
def test_pb2nc_missing_inputs(metplus_config, get_test_data_dir, missing,
                              run, thresh, errors, allow_missing, runtime_freq):
    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'PB2NC_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'PB2NC_INPUT_THRESH', thresh)
    config.set('config', 'PB2NC_RUNTIME_FREQ', runtime_freq)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_LIST', '2017051001, 2017051003, 2017051201, 2017051203')
    if runtime_freq == 'RUN_ONCE_PER_LEAD':
        config.set('config', 'LEAD_SEQ', '6,9,12,15,18')
    else:
        config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'PB2NC_INPUT_DIR', get_test_data_dir('obs'))
    config.set('config', 'PB2NC_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
    config.set('config', 'PB2NC_OUTPUT_TEMPLATE', '{OUTPUT_BASE}/PB2NC/output/test.nc')

    wrapper = PB2NCWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


# ---------------------
# test_find_input_files
# test files can be found with find_input_files with varying offset lists
# ---------------------
@pytest.mark.parametrize(
    # offset = list of offsets to search
    # offset_to_find = expected offset file to find, None if no files should be found
    'offsets, offset_to_find', [
        ([6, 5, 4, 3], 5),
        ([6, 4, 3], 3),
        ([2, 3, 4, 5, 6], 3),
        ([2, 4, 6], None),
    ]
)
@pytest.mark.wrapper
def test_find_input_files(metplus_config, offsets, offset_to_find):
    pb = pb2nc_wrapper(metplus_config)
    # for valid 20190201_12, offsets 3 and 5, create files to find
    # in the fake input directory based on input template
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 12) }
    fake_input_dir = os.path.join(pb.config.getdir('OUTPUT_BASE'), 'pbin')

    if not os.path.exists(fake_input_dir):
        os.makedirs(fake_input_dir)

    pb.c_dict['OBS_INPUT_DIR'] = fake_input_dir

    for offset in [3, 5]:
        input_dict['offset'] = int(offset * 3600)
        time_info = time_util.ti_calculate(input_dict)

        create_file = do_string_sub(pb.c_dict['OBS_INPUT_TEMPLATE'],
                                    **time_info)
        create_fullpath = os.path.join(fake_input_dir, create_file)
        open(create_fullpath, 'a').close()

    # unset offset in time dictionary so it will be computed
    del input_dict['offset']

    # recompute time_info to pass to find file functions
    time_info = time_util.ti_calculate(input_dict)

    # set offset list
    pb.c_dict['OFFSETS'] = offsets

    pb.c_dict['ALL_FILES'] = pb.get_all_files_for_each(time_info)

    # look for input files based on offset list
    result = pb.find_input_files(time_info)

    # check if correct offset file was found, if None expected, check against None
    if offset_to_find is None:
        assert result is None
    else:
        assert result['offset_hours'] == offset_to_find


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'PB2NC_MESSAGE_TYPE': 'ADPUPA, ADPSFC'},
         {'METPLUS_MESSAGE_TYPE': 'message_type = ["ADPUPA", "ADPSFC"];'}),

        ({'PB2NC_STATION_ID': 'station1, station2'},
         {'METPLUS_STATION_ID': 'station_id = ["station1", "station2"];'}),

        ({'OBS_PB2NC_WINDOW_BEGIN': '-1800', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -1800;}'}),

        ({'OBS_PB2NC_WINDOW_END': '1800', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {end = 1800;}'}),

        ({
             'OBS_PB2NC_WINDOW_BEGIN': '-1800',
             'OBS_PB2NC_WINDOW_END': '1800',
         },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -1800;end = 1800;}'}),
        # test legacy PB2NC_WINDOW_[BEGIN/END]
        ({'PB2NC_WINDOW_BEGIN': '-1800', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {beg = -1800;}'}),

        ({'PB2NC_WINDOW_END': '1800', },
         {'METPLUS_OBS_WINDOW_DICT': 'obs_window = {end = 1800;}'}),

        ({'PB2NC_MASK_GRID': 'FULL', },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";}'}),

        ({'PB2NC_MASK_POLY': 'SAO.poly', },
         {'METPLUS_MASK_DICT': 'mask = {poly = "SAO.poly";}'}),

        ({'PB2NC_MASK_GRID': 'FULL',
          'PB2NC_MASK_POLY': 'SAO.poly'},
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";poly = "SAO.poly";}'}),

        ({'PB2NC_PB_REPORT_TYPE': '1, 2, 3, 4, 5', },
         {'METPLUS_PB_REPORT_TYPE': 'pb_report_type = [1, 2, 3, 4, 5];'}),

        ({'PB2NC_LEVEL_RANGE_BEGIN': '2', },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {beg = 2;}'}),

        ({'PB2NC_LEVEL_RANGE_END': '512', },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {end = 512;}'}),

        ({'PB2NC_LEVEL_RANGE_BEGIN': '2',
          'PB2NC_LEVEL_RANGE_END': '512',
         },
         {'METPLUS_LEVEL_RANGE_DICT': 'level_range = {beg = 2;end = 512;}'}),

        ({'PB2NC_LEVEL_CATEGORY': '0, 1, 4, 5, 6', },
         {'METPLUS_LEVEL_CATEGORY': 'level_category = [0, 1, 4, 5, 6];'}),

        ({'PB2NC_OBS_BUFR_VAR_LIST': 'QOB, TOB', },
         {'METPLUS_OBS_BUFR_VAR': 'obs_bufr_var = ["QOB", "TOB"];'}),

        ({'PB2NC_QUALITY_MARK_THRESH': '3', },
         {'METPLUS_QUALITY_MARK_THRESH': 'quality_mark_thresh = 3;'}),

        ({'PB2NC_TIME_SUMMARY_FLAG': 'True', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {flag = TRUE;}'}),

        ({'PB2NC_TIME_SUMMARY_RAW_DATA': 'True', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {raw_data = TRUE;}'}),

        ({'PB2NC_TIME_SUMMARY_BEG': '012345', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {beg = "012345";}'}),

        ({'PB2NC_TIME_SUMMARY_END': '234559', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {end = "234559";}'}),

        ({'PB2NC_TIME_SUMMARY_STEP': '200', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {step = 200;}'}),

        ({'PB2NC_TIME_SUMMARY_WIDTH': '500', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {width = 500;}'}),

        ({'PB2NC_TIME_SUMMARY_GRIB_CODES': '11, 204, 211', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {grib_code = [11, 204, 211];}'}),

        ({'PB2NC_TIME_SUMMARY_VAR_NAMES': 'PMO,TOB,TDO', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {obs_var = ["PMO", "TOB", "TDO"];}'}),

        ({'PB2NC_TIME_SUMMARY_TYPE': 'min, max, range', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {type = ["min", "max", "range"];}'}),

        ({'PB2NC_TIME_SUMMARY_VLD_FREQ': '1', },
         {'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {vld_freq = 1;}'}),

        ({'PB2NC_TIME_SUMMARY_VLD_THRESH': '0.1', },
         {
             'METPLUS_TIME_SUMMARY_DICT': 'time_summary = {vld_thresh = 0.1;}'}),

        ({
             'PB2NC_TIME_SUMMARY_FLAG': 'TRUE',
             'PB2NC_TIME_SUMMARY_RAW_DATA': 'TRUE',
             'PB2NC_TIME_SUMMARY_BEG': '012345',
             'PB2NC_TIME_SUMMARY_END': '234559',
             'PB2NC_TIME_SUMMARY_STEP': '200',
             'PB2NC_TIME_SUMMARY_WIDTH': '500',
             'PB2NC_TIME_SUMMARY_GRIB_CODES': '11, 204, 211',
             'PB2NC_TIME_SUMMARY_VAR_NAMES': 'PMO,TOB,TDO',
             'PB2NC_TIME_SUMMARY_TYPE': 'min, max, range',
             'PB2NC_TIME_SUMMARY_VLD_FREQ': '1',
             'PB2NC_TIME_SUMMARY_VLD_THRESH': '0.1',
         },
         {
             'METPLUS_TIME_SUMMARY_DICT': ('time_summary = {flag = TRUE;'
                                           'raw_data = TRUE;beg = "012345";'
                                           'end = "234559";step = 200;'
                                           'width = 500;grib_code = [11, 204, 211];'
                                           'obs_var = ["PMO", "TOB", "TDO"];'
                                           'type = ["min", "max", "range"];'
                                           'vld_freq = 1;'
                                           'vld_thresh = 0.1;}')}),
        ({'PB2NC_OBS_BUFR_MAP': '{key="POB"; val="PRES"; },{key="QOB"; val="SPFH";}', },
         {'METPLUS_OBS_BUFR_MAP': 'obs_bufr_map = [{key="POB"; val="PRES"; }, {key="QOB"; val="SPFH";}];'}),
        ({'PB2NC_VALID_BEGIN': valid_beg}, {}),
        ({'PB2NC_VALID_END': valid_end}, {}),
        ({'PB2NC_VALID_BEGIN': valid_beg, 'PB2NC_VALID_END': valid_end}, {}),
        # 1 extra file
        ({'PB2NC_INPUT_TEMPLATE': ('ndas.t{da_init?fmt=%H}z.prepbufr.tm{offset?fmt=%2H}.{da_init?fmt=%Y%m%d}.nr,'
                                   'another_file.nr')}, {}),
        # 2 extra files
        ({'PB2NC_INPUT_TEMPLATE': ('ndas.t{da_init?fmt=%H}z.prepbufr.tm{offset?fmt=%2H}.{da_init?fmt=%Y%m%d}.nr,'
                                   'another_file.nr,yet_another_file.nr')},
         {}),

    ]
)
@pytest.mark.wrapper
def test_pb2nc_all_fields(metplus_config, config_overrides, env_var_values,
                          compare_command_and_env_vars):
    input_dir = '/some/input/dir'
    config = metplus_config

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PB2NC')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'VALID_BEG', '2007033112')
    config.set('config', 'VALID_END', '2007040100')
    config.set('config', 'VALID_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '0')
    config.set('config', 'PB2NC_OFFSETS', '12')

    config.set('config', 'PB2NC_CONFIG_FILE',
               '{PARM_BASE}/met_config/PB2NCConfig_wrapped')
    config.set('config', 'PB2NC_INPUT_DIR', input_dir)
    config.set('config', 'PB2NC_INPUT_TEMPLATE',
               'ndas.t{da_init?fmt=%H}z.prepbufr.tm{offset?fmt=%2H}.{da_init?fmt=%Y%m%d}.nr')
    config.set('config', 'PB2NC_OUTPUT_DIR',
               '{OUTPUT_BASE}/PB2NC/output')
    config.set('config', 'PB2NC_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}.nc')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PB2NCWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    extra_file_args = ''
    if 'PB2NC_INPUT_TEMPLATE' in config_overrides:
        extra_files = config_overrides['PB2NC_INPUT_TEMPLATE'].split(',')[1:]
        for extra_file in extra_files:
            extra_file_args += f' -pbfile {input_dir}/{extra_file}'

    valid_args = ''
    if 'PB2NC_VALID_BEGIN' in config_overrides:
        valid_args += f' -valid_beg {valid_beg}'
    if 'PB2NC_VALID_END' in config_overrides:
        valid_args += f' -valid_end {valid_end}'

    expected_cmds = [(f"{app_path} "
                      f"{input_dir}/ndas.t00z.prepbufr.tm12.20070401.nr "
                      f"{out_dir}/2007033112.nc "
                      f"{config_file}{extra_file_args}{valid_args} {verbosity}"),
                     (f"{app_path} "
                      f"{input_dir}/ndas.t12z.prepbufr.tm12.20070401.nr "
                      f"{out_dir}/2007040100.nc "
                      f"{config_file}{extra_file_args}{valid_args} {verbosity}"),
                     ]

    all_cmds = wrapper.run_all_times()
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values, wrapper)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'PB2NCConfig_wrapped')

    wrapper = PB2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'PB2NC_CONFIG_FILE', fake_config_name)
    wrapper = PB2NCWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name


@pytest.mark.wrapper
def test_pb2nc_file_window(metplus_config):
    begin_value = -3600
    end_value = 3600

    config = metplus_config
    config.set('config', 'PB2NC_FILE_WINDOW_BEGIN', begin_value)
    config.set('config', 'PB2NC_FILE_WINDOW_END', end_value)
    wrapper = PB2NCWrapper(config)
    assert wrapper.c_dict['OBS_FILE_WINDOW_BEGIN'] == begin_value
    assert wrapper.c_dict['OBS_FILE_WINDOW_END'] == end_value
