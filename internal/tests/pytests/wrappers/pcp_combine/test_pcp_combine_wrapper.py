#!/usr/bin/env python3

import pytest

import os
from datetime import datetime

from metplus.wrappers.pcp_combine_wrapper import PCPCombineWrapper
from metplus.util import ti_calculate


def get_test_data_dir(config, subdir=None):
    top_dir = os.path.join(config.getdir('METPLUS_BASE'),
                           'internal', 'tests', 'data')
    if subdir:
        top_dir = os.path.join(top_dir, subdir)
    return top_dir

def pcp_combine_wrapper(metplus_config, d_type):
    """! Returns a default PCPCombineWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PCPCombineWrapper with configuration values determined by what is set in
    # the test1.conf file.
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'test1.conf'))
    config = metplus_config(extra_configs)
    if d_type == "FCST":
        config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    elif d_type == "OBS":
        config.set('config', 'OBS_PCP_COMBINE_RUN', True)

    return PCPCombineWrapper(config)


@pytest.mark.wrapper
def test_get_accumulation_1_to_6(metplus_config):
    data_src = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = get_test_data_dir(pcw.config, subdir='accum')
    task_info = {}
    task_info['valid'] = datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = ti_calculate(task_info)
    # 6 hours in seconds
    accum = 6 * 3600

    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, time_info)

    files_found = pcw.get_accumulation(time_info, accum, data_src)
    in_files = [item[0] for item in files_found]
    assert (len(in_files) == 6 and
            input_dir+"/20160904/file.2016090418.01h" in in_files and
            input_dir+"/20160904/file.2016090417.01h" in in_files and
            input_dir+"/20160904/file.2016090416.01h" in in_files and
            input_dir+"/20160904/file.2016090415.01h" in in_files and
            input_dir+"/20160904/file.2016090414.01h" in in_files and
            input_dir+"/20160904/file.2016090413.01h" in in_files)


@pytest.mark.wrapper
def test_get_accumulation_6_to_6(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = get_test_data_dir(pcw.config, subdir='accum')
    task_info = {}
    task_info['valid'] = datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = ti_calculate(task_info)
    accum = 6 * 3600

    template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    pcw.c_dict['FCST_INPUT_TEMPLATE'] = template

    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, time_info)

    files_found = pcw.get_accumulation(time_info, accum, data_src)
    in_files = [item[0] for item in files_found]
    assert (len(in_files) == 1 and
            input_dir+"/20160904/file.2016090418.06h" in in_files)


@pytest.mark.wrapper
def test_get_lowest_forecast_file_dated_subdir(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = get_test_data_dir(pcw.config, subdir='fcst')
    valid_time = datetime.strptime("201802012100", '%Y%m%d%H%M')
    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, {'valid': valid_time})
    out_file, fcst = pcw.get_lowest_fcst_file(valid_time, data_src)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc" and
           fcst == 10800)


@pytest.mark.wrapper
def test_forecast_constant_init(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    pcw.c_dict['FCST_CONSTANT_INIT'] = True
    input_dir = get_test_data_dir(pcw.config, subdir='fcst')
    init_time = datetime.strptime("2018020112", '%Y%m%d%H')
    valid_time = datetime.strptime("2018020121", '%Y%m%d%H')
    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    out_file, fcst = pcw.find_input_file(init_time, valid_time, 0, data_src)
    assert(out_file == input_dir+"/20180201/file.2018020112f009.nc" and
           fcst == 32400)


@pytest.mark.wrapper
def test_forecast_not_constant_init(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    pcw.c_dict['FCST_CONSTANT_INIT'] = False
    input_dir = get_test_data_dir(pcw.config, subdir='fcst')
    init_time = datetime.strptime("2018020112", '%Y%m%d%H')
    valid_time = datetime.strptime("2018020121", '%Y%m%d%H')
    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, {'valid': valid_time})
    out_file, fcst = pcw.find_input_file(init_time, valid_time, 0, data_src)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc" and
           fcst == 10800)


@pytest.mark.wrapper
def test_get_lowest_forecast_file_no_subdir(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = get_test_data_dir(pcw.config, subdir='fcst')
    valid_time = datetime.strptime("201802012100", '%Y%m%d%H%M')
    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.c_dict[f'{data_src}_INPUT_TEMPLATE'] = template
    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, {'valid': valid_time})
    out_file, fcst = pcw.get_lowest_fcst_file(valid_time, data_src)
    assert(out_file == input_dir+"/file.2018020118f003.nc" and fcst == 10800)


@pytest.mark.wrapper
def test_get_lowest_forecast_file_yesterday(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = get_test_data_dir(pcw.config, subdir='fcst')
    valid_time = datetime.strptime("201802010600", '%Y%m%d%H%M')
    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.c_dict[f'{data_src}_INPUT_TEMPLATE'] = template
    pcw.c_dict[f'{data_src}_INPUT_DIR'] = input_dir
    pcw._build_input_accum_list(data_src, {'valid': valid_time})
    out_file, fcst = pcw.get_lowest_fcst_file(valid_time, data_src)
    assert(out_file == input_dir+"/file.2018013118f012.nc" and fcst == 43200)


@pytest.mark.wrapper
def test_setup_add_method(metplus_config):
    data_src = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    task_info = {}
    task_info['valid'] = datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = ti_calculate(task_info)

    input_dir = get_test_data_dir(pcw.config, subdir='accum')
    lookback = 6 * 3600
    files_found = pcw.setup_add_method(time_info, lookback, data_src)
    assert files_found
    
    in_files = [item[0] for item in files_found]
    print(f"Infiles: {in_files}")
    assert (len(in_files) == 6 and
            input_dir+"/20160904/file.2016090418.01h" in in_files and
            input_dir+"/20160904/file.2016090417.01h" in in_files and
            input_dir+"/20160904/file.2016090416.01h" in in_files and
            input_dir+"/20160904/file.2016090415.01h" in in_files and
            input_dir+"/20160904/file.2016090414.01h" in in_files and
            input_dir+"/20160904/file.2016090413.01h" in in_files)


# how to test? check output?
@pytest.mark.wrapper
def test_setup_sum_method(metplus_config):
    data_src = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    task_info = {}
    task_info['valid'] = datetime.strptime("2016090418", '%Y%m%d%H')
    task_info['lead'] = 0
    time_info = ti_calculate(task_info)
    lookback = 6 * 3600
    assert pcw.setup_sum_method(time_info, lookback, data_src)


@pytest.mark.wrapper
def test_setup_subtract_method(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    task_info = {}
    task_info['valid'] = datetime.strptime("201609050000", '%Y%m%d%H%M')
    task_info['lead_hours'] = 9
    time_info = ti_calculate(task_info)
    lookback = 6 * 3600
    files_found = pcw.setup_subtract_method(time_info, lookback, data_src)
    in_files = [item[0] for item in files_found]

    assert len(in_files) == 2


@pytest.mark.wrapper
def test_pcp_combine_add_subhourly(metplus_config):
    fcst_name = 'A000500'
    fcst_level = 'Surface'
    fcst_output_name = 'A001500'
    fcst_fmt = f'\'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'add')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/add'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d%H%M')
    config.set('config', 'VALID_BEG', '201908021815')
    config.set('config', 'VALID_END', '201908021815')
    config.set('config', 'VALID_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '15M')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}_i{init?fmt=%H%M}_m0_f{valid?fmt=%H%M}.nc')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '5min_mem00_lag00.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '5M')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_NAMES', fcst_name)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_LEVELS', fcst_level)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', fcst_output_name)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '15M')

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      "-add "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1815.nc "
                      f"{fcst_fmt} "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1810.nc "
                      f"{fcst_fmt} "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1805.nc "
                      f"{fcst_fmt} "
                      f'-name "{fcst_output_name}" '
                      f"{out_dir}/5min_mem00_lag00.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_pcp_combine_bucket(metplus_config):
    fcst_output_name = 'APCP'
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'bucket')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/bucket'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2012040900')
    config.set('config', 'INIT_END', '2012040900')
    config.set('config', 'INIT_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '15H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}_F{lead?fmt=%3H}.grib')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}_A{level?fmt=%3H}.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_BUCKET_INTERVAL', '6H')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '{lead}')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', fcst_output_name)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '15H')

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      "-add "
                      f"{fcst_input_dir}/2012040900_F015.grib "
                      "'name=\"APCP\"; level=\"A03\";' "
                      f"{fcst_input_dir}/2012040900_F012.grib "
                      "'name=\"APCP\"; level=\"A06\";' "
                      f"{fcst_input_dir}/2012040900_F006.grib "
                      "'name=\"APCP\"; level=\"A06\";' "
                      f'-name "{fcst_output_name}" '
                      f"{out_dir}/2012040915_A015.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.parametrize(
    'config_overrides, extra_fields', [
        ({},
         ''),
        ({'FCST_PCP_COMBINE_EXTRA_NAMES': 'NAME1',
          'FCST_PCP_COMBINE_EXTRA_LEVELS': 'LEVEL1', },
         "-field 'name=\"NAME1\"; level=\"LEVEL1\";' "),
        ({'FCST_PCP_COMBINE_EXTRA_NAMES': 'NAME1, NAME2',
          'FCST_PCP_COMBINE_EXTRA_LEVELS': 'LEVEL1, LEVEL2', },
         ("-field 'name=\"NAME1\"; level=\"LEVEL1\";' "
          "-field 'name=\"NAME2\"; level=\"LEVEL2\";' ")),
    ]
)
@pytest.mark.wrapper
def test_pcp_combine_derive(metplus_config, config_overrides, extra_fields):
    stat_list = 'sum,min,max,range,mean,stdev,vld_count'
    fcst_name = 'APCP'
    fcst_level = 'A03'
    fcst_fmt = f'-field \'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'derive')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/derive'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080700')
    config.set('config', 'INIT_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '24H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'DERIVE')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/{lead?fmt=%HH}.tm00_G212')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}_f{lead?fmt=%HH}_A{level?fmt=%HH}.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '3H')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_NAMES', fcst_name)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_LEVELS', fcst_level)
    config.set('config', 'FCST_PCP_COMBINE_DERIVE_LOOKBACK', '18H')
    config.set('config', 'FCST_PCP_COMBINE_MIN_FORECAST', '9H')
    config.set('config', 'FCST_PCP_COMBINE_MAX_FORECAST', '2d')
    config.set('config', 'FCST_PCP_COMBINE_STAT_LIST', stat_list)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '18M')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"-derive {stat_list} "
                      f"{fcst_input_dir}/2005080700/24.tm00_G212 "
                      f"{fcst_input_dir}/2005080700/21.tm00_G212 "
                      f"{fcst_input_dir}/2005080700/18.tm00_G212 "
                      f"{fcst_input_dir}/2005080700/15.tm00_G212 "
                      f"{fcst_input_dir}/2005080700/12.tm00_G212 "
                      f"{fcst_input_dir}/2005080700/09.tm00_G212 "
                      f"{fcst_fmt} {extra_fields}"
                      f"{out_dir}/2005080700_f24_A18.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_pcp_combine_loop_custom(metplus_config):
    fcst_name = 'APCP'
    ens_list = ['ens1', 'ens2', 'ens3', 'ens4', 'ens5', 'ens6']
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'loop_custom')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/loop_custom'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2009123112')
    config.set('config', 'INIT_END', '2009123112')
    config.set('config', 'INIT_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '24H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_CONSTANT_INIT', 'True')
    config.set('config', 'PCP_COMBINE_CUSTOM_LOOP_LIST', ', '.join(ens_list))
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{custom?fmt=%s}/{init?fmt=%Y%m%d%H}_0{lead?fmt=%HH}00.grib')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{custom?fmt=%s}/{init?fmt=%Y%m%d%H}_0{lead?fmt=%HH}00.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '24H')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '24H')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', fcst_name)

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = []
    for ens in ens_list:
        cmd = (f"{app_path} {verbosity} "
               f"-add "
               f"{fcst_input_dir}/{ens}/2009123112_02400.grib "
               "'name=\"APCP\"; level=\"A24\";' "
               f'-name "{fcst_name}" '
               f"{out_dir}/{ens}/2009123112_02400.nc")
        expected_cmds.append(cmd)

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_pcp_combine_subtract(metplus_config):
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'derive')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/subtract'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080700')
    config.set('config', 'INIT_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '18H')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'SUBTRACT')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/{lead?fmt=%HH}.tm00_G212')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}_A{level?fmt=%3H}.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '3H')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', 'APCP')

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"-subtract "
                      f"{fcst_input_dir}/2005080700/18.tm00_G212 "
                      "'name=\"APCP\"; level=\"A18\";' "
                      f"{fcst_input_dir}/2005080700/15.tm00_G212 "
                      "'name=\"APCP\"; level=\"A15\";' "
                      '-name "APCP" '
                      f"{out_dir}/2005080718_A003.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_pcp_combine_sum_subhourly(metplus_config):
    fcst_name = 'A000500'
    fcst_level = 'Surface'
    fcst_output_name = 'A001500'
    fcst_fmt = f'-field \'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = get_test_data_dir(config)
    fcst_input_dir = os.path.join(test_data_dir,
                                  'pcp_in',
                                  'add')
    fcst_output_dir = '{OUTPUT_BASE}/PCP/sum'
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d%H%M')
    config.set('config', 'VALID_BEG', '201908021815')
    config.set('config', 'VALID_END', '201908021815')
    config.set('config', 'VALID_INCREMENT', '1M')
    config.set('config', 'LEAD_SEQ', '15M')
    config.set('config', 'LOOP_ORDER', 'times')
    config.set('config', 'FCST_PCP_COMBINE_RUN', 'True')
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'SUM')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', fcst_input_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}_i{init?fmt=%H%M}_m0_f*')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', fcst_output_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '5min_mem00_lag00.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', 'GRIB')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '5M')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_NAMES', fcst_name)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_LEVELS', fcst_level)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', fcst_output_name)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '15M')

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      "-sum "
                      "20190802_180000 000500 "
                      "20190802_181500 001500 "
                      f"-pcpdir {fcst_input_dir} "
                      f"-pcprx 20190802_i1800_m0_f* "
                      f"{fcst_fmt} "
                      f"-name \"{fcst_output_name}\" "
                      f"{out_dir}/5min_mem00_lag00.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.parametrize(
    'output_name,extra_output,expected_results', [
        # 0
        ('', [''], []),
        # 1
        ('out_name1', None, ['-name "out_name1"']),
        # 2
        ('out_name1', ['out_name2'], ['-name "out_name1","out_name2"']),
        # 3
        ('out_name1', ['out_name2', 'out_name3'],
         ['-name "out_name1","out_name2","out_name3"']),
    ]
)
@pytest.mark.wrapper
def test_handle_name_argument(metplus_config, output_name, extra_output,
                              expected_results):
    data_src = 'FCST'
    config = metplus_config()
    wrapper = PCPCombineWrapper(config)
    wrapper.c_dict[data_src + '_EXTRA_OUTPUT_NAMES'] = extra_output
    wrapper._handle_name_argument(output_name, data_src)
    actual_results = wrapper.args
    print(f"Actual: {actual_results}")
    print(f"Expected: {expected_results}")
    assert len(actual_results) == len(expected_results)
    for index, expected_result in enumerate(expected_results):
        assert actual_results[index] == expected_result


@pytest.mark.parametrize(
    'names,levels,expected_args', [
        # 0: none specified
        ('', '',
         []),
        # 1: 1 input name, no level
        ('input1', '',
         ["-field 'name=\"input1\";'"]),
        # 2: 1 input name, 1 level
         ('input1', 'level1',
          ["-field 'name=\"input1\"; level=\"level1\";'"]),
        # 3: 2 input names, no levels
         ('input1,input2', '',
          ["-field 'name=\"input1\";'", "-field 'name=\"input2\";'"]),
        # 4: 2 input names, 2 levels
         ('input1,input2', 'level1,level2',
          ["-field 'name=\"input1\"; level=\"level1\";'",
           "-field 'name=\"input2\"; level=\"level2\";'"]),
        # 5: 2 input names, 1 level
         ('input1,input2', 'level1',
          ["-field 'name=\"input1\"; level=\"level1\";'",
           "-field 'name=\"input2\";'"]),
    ]
)
@pytest.mark.wrapper
def test_get_extra_fields(metplus_config, names, levels, expected_args):
    data_src = 'FCST'
    config = metplus_config()
    config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_EXTRA_NAMES', names)
    config.set('config', 'FCST_PCP_COMBINE_EXTRA_LEVELS', levels)

    wrapper = PCPCombineWrapper(config)

    wrapper._handle_extra_field_arguments(data_src)
    wrapper._handle_name_argument('', data_src)
    for index, expected_arg in enumerate(expected_args):
        assert wrapper.args[index] == expected_arg


@pytest.mark.wrapper
def test_add_method_single_file(metplus_config):
    data_src = 'FCST'
    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H%M')
    config.set('config', 'INIT_BEG', '2019100200')
    config.set('config', 'INIT_END', '2019100200')
    config.set('config', 'INIT_INCREMENT', '3H')
    config.set('config', 'LEAD_SEQ', '24,27,30')
    config.set('config', 'LOOP_ORDER', 'times')

    config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_CONSTANT_INIT', True)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', '/some/input/dir')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}_prec_1hracc_75hrfcst_e00.nc')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', '/some/output/dir')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}_prec_{level?fmt=%H}hracc_e00.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '1H')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_NAMES', 'rf')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_LEVELS',
               '"({valid?fmt=%Y%m%d_%H},*,*)"')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '3H')

    wrapper = PCPCombineWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    in_file = (f"{wrapper.c_dict.get('FCST_INPUT_DIR')}/"
               "20191002_prec_1hracc_75hrfcst_e00.nc")
    expected_cmds = [
        (f"{app_path} {verbosity} -add "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_00,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191002_23,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191002_22,*,*)\";' "
         f"{out_dir}/2019100300_prec_03hracc_e00.nc"),
        (f"{app_path} {verbosity} -add "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_03,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_02,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_01,*,*)\";' "
         f"{out_dir}/2019100303_prec_03hracc_e00.nc"),
        (f"{app_path} {verbosity} -add "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_06,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_05,*,*)\";' "
         f"{in_file} 'name=\"rf\"; level=\"(20191003_04,*,*)\";' "
         f"{out_dir}/2019100306_prec_03hracc_e00.nc"),
    ]

    assert len(all_cmds) == len(expected_cmds)

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_subtract_method_zero_accum(metplus_config):
    input_name = 'stratiform_rainfall_amount'
    input_level = '"(*,*)"'
    in_dir = '/some/input/dir'
    out_dir = '/some/output/dir'
    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PCPCombine')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H%M')
    config.set('config', 'INIT_BEG', '2019100200')
    config.set('config', 'INIT_END', '2019100200')
    config.set('config', 'INIT_INCREMENT', '3H')
    config.set('config', 'LEAD_SEQ', '1')
    config.set('config', 'LOOP_ORDER', 'times')

    config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'SUBTRACT')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_DIR', in_dir)
    config.set('config', 'FCST_PCP_COMBINE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%dT%H%M}Z_pverb{lead?fmt=%3H}.nc')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_DIR', out_dir)
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}_f{level?fmt=%3H}.nc')
    config.set('config', 'FCST_PCP_COMBINE_INPUT_ACCUMS', '1H')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_ACCUM', '1H')
    config.set('config', 'FCST_PCP_COMBINE_OUTPUT_NAME', input_name)


    # NETCDF example should use zero accum, GRIB example should not (use -add)
    expected_cmds_dict = {}
    expected_cmds_dict['NETCDF'] = [
        (f"-subtract "
         f"{in_dir}/20191002T0000Z_pverb001.nc "
         f"'name=\"{input_name}\"; level={input_level};' "
         f"{in_dir}/20191002T0000Z_pverb000.nc "
         f"'name=\"{input_name}\"; level={input_level};' "
         f"-name \"{input_name}\" "
         f"{out_dir}/2019100200_f001.nc"),
    ]
    expected_cmds_dict['GRIB'] = [
        (f"-add "
         f"{in_dir}/20191002T0000Z_pverb001.nc "
         "'name=\"APCP\"; level=\"A01\";' "
         f"-name \"{input_name}\" "
         f"{out_dir}/2019100200_f001.nc"
         ),
    ]

    for data_type in ['GRIB', 'NETCDF']:
        config.set('config', 'FCST_PCP_COMBINE_INPUT_DATATYPE', data_type)

        if data_type == 'NETCDF':
            config.set('config', 'FCST_PCP_COMBINE_INPUT_NAMES', input_name)
            config.set('config', 'FCST_PCP_COMBINE_INPUT_LEVELS', input_level)
            config.set('config', 'FCST_PCP_COMBINE_USE_ZERO_ACCUM', 'True')
        else:
            config.set('config', 'FCST_PCP_COMBINE_USE_ZERO_ACCUM', 'False')

        wrapper = PCPCombineWrapper(config)
        assert wrapper.isOK

        all_cmds = wrapper.run_all_times()

        app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
        verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
        expected_cmds = [f"{app_path} {verbosity} {item}"
                         for item in expected_cmds_dict[data_type]]
        assert len(all_cmds) == len(expected_cmds)

        for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
            # ensure commands are generated as expected
            assert cmd == expected_cmd
