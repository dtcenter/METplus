#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import config_metplus
from pcp_combine_wrapper import PcpCombineWrapper
import met_util as util
from task_info import TaskInfo

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
@pytest.fixture
def pcp_combine_wrapper():
    """! Returns a default PcpCombineWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    conf = metplus_config()
    return PcpCombineWrapper(conf, None)


@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='PcpCombineWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='PcpCombineWrapper ')
        produtil.log.postmsg('pcp_combine_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'pcp_combine_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_search_day
# ------------------------
# Need to have directory of test data to be able to test this functionality
# they could be empty files, they just need to exist so we can find the files

def test_get_accumulation_1_to_6():
    pcw = pcp_combine_wrapper()
    data_src = "OBS"
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    valid_time = "2016090418"
    accum = 6

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
        
    pcw.set_input_dir(input_dir)
    pcw.get_accumulation(valid_time, accum, data_src,
                                           file_template, False)
    in_files = pcw.get_input_files()
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


def test_get_accumulation_6_to_6():
    pcw = pcp_combine_wrapper()
    data_src = "FCST"
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    valid_time = "2016090418"
    accum = 6

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    
    pcw.set_input_dir(input_dir)
    pcw.get_accumulation(valid_time, accum, data_src,
                                           file_template, False)
    in_files = pcw.get_input_files()    
    if  len(in_files) == 1 and input_dir+"/20160904/file.2016090418.06h" in in_files:
        assert True
    else:
        assert False


def test_get_lowest_forecast_file_dated_subdir():
    pcw = pcp_combine_wrapper()    
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = "201802012100"
    dtype = "FCST"
    template = util.getraw_interp(pcw.p, 'filename_templates', 'FCST_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc")


def test_get_lowest_forecast_file_no_subdir():
    pcw = pcp_combine_wrapper()    
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = "201802012100"
    dtype = "FCST2"
    template = util.getraw_interp(pcw.p, 'filename_templates', dtype+'_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018020118f003.nc")

def test_get_lowest_forecast_file_yesterday():
    pcw = pcp_combine_wrapper()
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = "201802010600"
    dtype = "FCST2"
    template = util.getraw_interp(pcw.p, 'filename_templates', 'FCST2_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018013118f012.nc")    


def test_search_day():
    pcw = pcp_combine_wrapper()
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/daily"
    file_time = "201802010600"
    search_time = "2018020100"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.search_day(input_dir, file_time, search_time, template)
    assert(out_file == input_dir+"/file.20180201.txt")

    
def test_find_closest_before_today():
    pcw = pcp_combine_wrapper()
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/daily"
    file_time = "201802010600"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.find_closest_before(input_dir, file_time, template)
    assert(out_file == input_dir+"/file.20180201.txt")

def test_find_closest_before_yesterday():
    pcw = pcp_combine_wrapper()
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/daily"
    file_time = "201802080000"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.find_closest_before(input_dir, file_time, template)
    assert(out_file == input_dir+"/file.20180207.txt")    

def test_get_daily_file():
    pcw = pcp_combine_wrapper()
    valid_time = "201802010000"
    accum = 1
    data_src = "OBS"
    file_template = "file.{valid?fmt=%Y%m%d}.txt"
    pcw.get_daily_file(valid_time,accum, data_src, file_template)

def test_setup_add_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "2016090418"
    var_info = util.FieldObj()
    var_info.fcst_name = "APCP"
    var_info.obs_name = "ACPCP"
    var_info.fcst_extra = ""
    var_info.obs_extra = ""
    var_info.fcst_level = "A06"
    var_info.obs_level = "A06"
    rl = "OBS"
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    output_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/fakeout"
    pcw.setup_add_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
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
def test_setup_sum_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "2016090418"
    task_info.lead = 0
    var_info = util.FieldObj()
    var_info.fcst_name = "APCP"
    var_info.obs_name = "ACPCP"
    var_info.fcst_extra = ""
    var_info.obs_extra = ""
    var_info.fcst_level = "A06"
    var_info.obs_level = "A06"
    rl = "OBS"
    input_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    output_dir = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/fakeout"
    pcw.setup_sum_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
    out_file = pcw.get_output_path()    
    assert(out_file == output_dir+"/20160904/outfile.2016090418_A06h")


def test_setup_subtract_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "201609041800"
    task_info.lead = 3
    var_info = util.FieldObj()
    var_info.fcst_name = "APCP"
    var_info.obs_name = "ACPCP"
    var_info.fcst_extra = ""
    var_info.obs_extra = ""
    var_info.fcst_level = "A06"
    var_info.obs_level = "A06"
    rl = "FCST"
    pcw.setup_subtract_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
    out_file = pcw.get_output_path()    
    assert(len(in_files) == 2)

