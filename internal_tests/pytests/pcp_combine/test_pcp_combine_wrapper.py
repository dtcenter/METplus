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
    accum = 6

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
    accum = 6

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
#    template = util.getraw(pcw.config, 'filename_templates', dtype+'_PCP_COMBINE_INPUT_TEMPLATE')
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
#    template = util.getraw(pcw.config, 'filename_templates', 'FCST2_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file, fcst = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018013118f012.nc" and fcst == 43200)

def test_get_daily_file(metplus_config):
    data_src = "OBS"
    pcw = pcp_combine_wrapper(metplus_config, data_src)
    time_info = {'valid' : datetime.datetime.strptime("201802010000", '%Y%m%d%H%M') }
    accum = 1
    file_template = "file.{valid?fmt=%Y%m%d}.txt"
    pcw.get_daily_file(time_info, accum, data_src, file_template)

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

