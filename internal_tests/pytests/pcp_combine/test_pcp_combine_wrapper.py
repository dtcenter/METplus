#!/usr/bin/env python

import os
import sys
import re
import logging
import datetime
from collections import namedtuple
import pytest

import produtil

from metplus.wrappers.pcp_combine_wrapper import PCPCombineWrapper
from metplus.util import time_util
from metplus.util import met_util as util

# --------------------TEST CONFIGURATION and FIXTURE SUPPORT -------------
#
# The test configuration and fixture support the additional configuration
# files used in METplus
#              !!!!!!!!!!!!!!!
#              !!!IMPORTANT!!!
#              !!!!!!!!!!!!!!!
# The following two methods should be included in ALL pytest tests for METplus.
#
#
#def pytest_addoption(parser):
#    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
#def cmdopt(request):
#    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
#@pytest.fixture
def pcp_combine_wrapper(metplus_config, d_type):
    """! Returns a default PCPCombineWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'test1.conf'))
    config = metplus_config(extra_configs)
    if d_type == "FCST":
        config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    elif d_type == "OBS":
        config.set('config', 'OBS_PCP_COMBINE_RUN', True)

    return PCPCombineWrapper(config)

# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_search_day
# ------------------------
# Need to have directory of test data to be able to test this functionality
# they could be empty files, they just need to exist so we can find the files

def test_get_accumulation_1_to_6(metplus_config):
    data_src = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = time_util.ti_calculate(task_info)
    # 6 hours in seconds
    accum = 6 * 3600

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
        
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(data_src, time_info)

    pcw.get_accumulation(time_info, accum, data_src)
    in_files = pcw.infiles
    if len(in_files) == 6 and \
      input_dir+"/20160904/file.2016090418.01h" in in_files and \
      input_dir+"/20160904/file.2016090417.01h" in in_files and \
      input_dir+"/20160904/file.2016090416.01h" in in_files and \
      input_dir+"/20160904/file.2016090415.01h" in in_files and \
      input_dir+"/20160904/file.2016090414.01h" in in_files and \
      input_dir+"/20160904/file.2016090413.01h" in in_files:
        assert True
    else:
        assert False


def test_get_accumulation_6_to_6(metplus_config):
    data_src = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = time_util.ti_calculate(task_info)
    accum = 6 * 3600

    pcw.c_dict['FCST_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(data_src, time_info)

    pcw.get_accumulation(time_info, accum, data_src)
    in_files = pcw.infiles    
    if  len(in_files) == 1 and input_dir+"/20160904/file.2016090418.06h" in in_files:
        assert True
    else:
        assert False


def test_get_lowest_forecast_file_dated_subdir(metplus_config):
    dtype = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802012100", '%Y%m%d%H%M')
    template = pcw.config.getraw('filename_templates', 'FCST_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file, fcst = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc" and fcst == 10800)

def test_forecast_constant_init(metplus_config):
    dtype = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, dtype)
    pcw.c_dict['FCST_CONSTANT_INIT'] = True
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    init_time = datetime.datetime.strptime("2018020112", '%Y%m%d%H')
    valid_time = datetime.datetime.strptime("2018020121", '%Y%m%d%H')
    template = pcw.config.getraw('filename_templates', 'FCST_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    out_file, fcst = pcw.find_input_file(template, init_time, valid_time, 0, dtype)
    assert(out_file == input_dir+"/20180201/file.2018020112f009.nc" and fcst == 32400)

def test_forecast_not_constant_init(metplus_config):
    dtype = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, dtype)
    pcw.c_dict['FCST_CONSTANT_INIT'] = False
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    init_time = datetime.datetime.strptime("2018020112", '%Y%m%d%H')
    valid_time = datetime.datetime.strptime("2018020121", '%Y%m%d%H')
    template = pcw.config.getraw('filename_templates', 'FCST_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file, fcst = pcw.find_input_file(template, init_time, valid_time, 0, dtype)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc" and fcst == 10800)


def test_get_lowest_forecast_file_no_subdir(metplus_config):
    dtype = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802012100", '%Y%m%d%H%M')

    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file, fcst = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018020118f003.nc" and fcst == 10800)

def test_get_lowest_forecast_file_yesterday(metplus_config):
    dtype = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802010600", '%Y%m%d%H%M')
    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file, fcst = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018013118f012.nc" and fcst == 43200)

def test_setup_add_method(metplus_config):
    rl = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, rl)
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = time_util.ti_calculate(task_info)
    var_info = {}
    var_info['fcst_name'] = "APCP"
    var_info['obs_name'] = "ACPCP"
    var_info['fcst_extra'] = ""
    var_info['obs_extra'] = ""
    var_info['fcst_level'] = "A06"
    var_info['obs_level'] = "A06"
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    output_dir = pcw.config.getdir('OUTPUT_BASE')+"/internal_tests/data/fakeout"
    pcw.setup_add_method(time_info, var_info, rl)
    
    in_files = pcw.infiles
    out_file = pcw.get_output_path()
    if len(in_files) == 6 and \
      input_dir+"/20160904/file.2016090418.01h" in in_files and \
      input_dir+"/20160904/file.2016090417.01h" in in_files and \
      input_dir+"/20160904/file.2016090416.01h" in in_files and \
      input_dir+"/20160904/file.2016090415.01h" in in_files and \
      input_dir+"/20160904/file.2016090414.01h" in in_files and \
      input_dir+"/20160904/file.2016090413.01h" in in_files and \
       out_file == output_dir+"/20160904/outfile.2016090418_A06h":
        assert True
    else:
        assert False


# how to test? check output?
def test_setup_sum_method(metplus_config):
    rl = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, rl)
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    var_info = {}
    var_info['fcst_name'] = "APCP"
    var_info['obs_name'] = "ACPCP"
    var_info['fcst_extra'] = ""
    var_info['obs_extra'] = ""
    var_info['fcst_level'] = "A06"
    var_info['obs_level'] = "A06"
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    output_dir = pcw.config.getdir('OUTPUT_BASE')+"/internal_tests/data/fakeout"
    pcw.setup_sum_method(time_info, var_info, rl)
    
    in_files = pcw.infiles
    out_file = pcw.get_output_path()    
    assert(out_file == output_dir+"/20160904/outfile.2016090418_A06h")

def test_setup_subtract_method(metplus_config):
    rl = "FCST"
    pcw = pcp_combine_wrapper(metplus_config, rl)
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201609050000", '%Y%m%d%H%M')
    task_info['lead_hours'] = 9
    time_info = time_util.ti_calculate(task_info)
    var_info = {}
    var_info['fcst_name'] = "APCP"
    var_info['obs_name'] = "ACPCP"
    var_info['fcst_extra'] = ""
    var_info['obs_extra'] = ""
    var_info['fcst_level'] = "A06"
    var_info['obs_level'] = "A06"
    pcw.setup_subtract_method(time_info, var_info, rl)
    in_files = pcw.infiles
    out_file = pcw.get_output_path()    
    assert(len(in_files) == 2)

def test_pcp_combine_add_subhourly(metplus_config):
    fcst_name = 'A000500'
    fcst_level = 'Surface'
    fcst_output_name = 'A001500'
    fcst_fmt = f'\'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      "-add "
                      f"-name {fcst_output_name} "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1815.nc "
                      f"{fcst_fmt} "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1810.nc "
                      f"{fcst_fmt} "
                      f"{fcst_input_dir}/20190802_i1800_m0_f1805.nc "
                      f"{fcst_fmt} "
                      f"{out_dir}/5min_mem00_lag00.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

def test_pcp_combine_bucket(metplus_config):
    fcst_output_name = 'APCP'
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      "-add "
                      f"-name {fcst_output_name} "
                      f"{fcst_input_dir}/2012040900_F015.grib 03 "
                      f"{fcst_input_dir}/2012040900_F012.grib 06 "
                      f"{fcst_input_dir}/2012040900_F006.grib 06 "
                      f"{out_dir}/2012040915_A015.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

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
def test_pcp_combine_derive(metplus_config, config_overrides, extra_fields):
    stat_list = 'sum,min,max,range,mean,stdev,vld_count'
    fcst_name = 'APCP'
    fcst_level = 'A03'
    fcst_fmt = f'-field \'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

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
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

def test_pcp_combine_loop_custom(metplus_config):
    fcst_name = 'APCP'
    ens_list = ['ens1', 'ens2', 'ens3', 'ens4', 'ens5', 'ens6']
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = []
    for ens in ens_list:
        cmd = (f"{app_path} {verbosity} "
               f"-add "
               f"-name {fcst_name} "
               f"{fcst_input_dir}/{ens}/2009123112_02400.grib 24 "
               f"{out_dir}/{ens}/2009123112_02400.nc")
        expected_cmds.append(cmd)

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

def test_pcp_combine_subtract(metplus_config):
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    out_dir = wrapper.c_dict.get('FCST_OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"-subtract "
                      f"{fcst_input_dir}/2005080700/18.tm00_G212 18 "
                      f"{fcst_input_dir}/2005080700/15.tm00_G212 15 "
                      f"{out_dir}/2005080718_A003.nc"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

def test_pcp_combine_sum_subhourly(metplus_config):
    fcst_name = 'A000500'
    fcst_level = 'Surface'
    fcst_output_name = 'A001500'
    fcst_fmt = f'-field \'name="{fcst_name}"; level="{fcst_level}";\''
    config = metplus_config()

    test_data_dir = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
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
    assert(wrapper.isOK)

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
    assert(len(all_cmds) == len(expected_cmds))

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

@pytest.mark.parametrize(
    'output_name,extra_output,expected_result', [
        (None, None, None),
        ('out_name1', None, '"out_name1"'),
        ('out_name1', '"out_name2"', '"out_name1","out_name2"'),
        ('out_name1', '"out_name2","out_name3"',
         '"out_name1","out_name2","out_name3"'),
    ]
)
def test_get_output_string(metplus_config, output_name, extra_output,
                           expected_result):
    config = metplus_config()
    wrapper = PCPCombineWrapper(config)
    wrapper.output_name = output_name
    wrapper.extra_output = extra_output
    actual_result = wrapper.get_output_string()
    assert(actual_result == expected_result)


@pytest.mark.parametrize(
    'names,levels,out_names,expected_input,expected_output', [
        # none specified
        ('', '', '',
         None, None),
        # 1 input name, no level
        ('input1', '', '',
         "-field 'name=\"input1\";'", None),
        # 1 input name, 1 level
        ('input1', 'level1', '',
         "-field 'name=\"input1\"; level=\"level1\";'", None),
        # 2 input names, no levels
        ('input1,input2', '', '',
         "-field 'name=\"input1\";' -field 'name=\"input2\";'", None),
        # 2 input names, 2 levels
        ('input1,input2', 'level1,level2', '',
         ("-field 'name=\"input1\"; level=\"level1\";' "
          "-field 'name=\"input2\"; level=\"level2\";'"), None),
        # 2 input names, 1 level
        ('input1,input2', 'level1', '',
         ("-field 'name=\"input1\"; level=\"level1\";' "
          "-field 'name=\"input2\";'"),
         None),
        # 1 input name, 1 level, 1 output
        ('input1', 'level1', 'output1',
         "-field 'name=\"input1\"; level=\"level1\";'", '"output1"'),
        # 2 input names, 2 levels, 2 outputs
        ('input1,input2', 'level1,level2', 'output1,output2',
         ("-field 'name=\"input1\"; level=\"level1\";' "
          "-field 'name=\"input2\"; level=\"level2\";'"),
         '"output1","output2"'),
    ]
)
def test_get_extra_fields(metplus_config, names, levels, out_names,
                          expected_input, expected_output):
    config = metplus_config()
    config.set('config', 'FCST_PCP_COMBINE_RUN', True)
    config.set('config', 'FCST_PCP_COMBINE_METHOD', 'ADD')
    config.set('config', 'FCST_PCP_COMBINE_EXTRA_NAMES', names)
    config.set('config', 'FCST_PCP_COMBINE_EXTRA_LEVELS', levels)
    config.set('config', 'FCST_PCP_COMBINE_EXTRA_OUTPUT_NAMES', out_names)

    wrapper = PCPCombineWrapper(config)

    actual_input, actual_output = wrapper.get_extra_fields('FCST')
    assert(actual_input == expected_input)
    assert (actual_output == expected_output)
