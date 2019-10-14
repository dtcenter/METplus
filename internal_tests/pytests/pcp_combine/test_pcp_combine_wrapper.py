#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import logging
import datetime
from collections import namedtuple
import produtil
import pytest
import config_metplus
from pcp_combine_wrapper import PcpCombineWrapper
import time_util
import met_util as util

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
def pcp_combine_wrapper(d_type):
    """! Returns a default PcpCombineWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    conf = metplus_config()
    if d_type == "FCST":
        conf.set('config', 'FCST_PCP_COMBINE_RUN', True)
    elif d_type == "OBS":
        conf.set('config', 'OBS_PCP_COMBINE_RUN', True)
#    logger = logging.getLogger("dummy")
    return PcpCombineWrapper(conf, conf.logger)


#@pytest.fixture
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
        conf = config_metplus.setup(util.baseinputconfs)
        logger = util.get_logger(conf)
        return conf

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
    data_src = "OBS"
    pcw = pcp_combine_wrapper(data_src)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = time_util.ti_calculate(task_info)
    accum = 6

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
        
    pcw.input_dir = input_dir
    if not pcw.build_input_accum_list(data_src, time_info):
        assert False

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


def test_get_accumulation_6_to_6():
    data_src = "FCST"
    pcw = pcp_combine_wrapper(data_src)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/accum"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("2016090418", '%Y%m%d%H')
    time_info = time_util.ti_calculate(task_info)
    accum = 6

    pcw.c_dict['FCST_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    
    pcw.input_dir = input_dir
    if not pcw.build_input_accum_list(data_src, time_info):
        assert False

    pcw.get_accumulation(time_info, accum, data_src)
    in_files = pcw.infiles    
    if  len(in_files) == 1 and input_dir+"/20160904/file.2016090418.06h" in in_files:
        assert True
    else:
        assert False


def test_get_lowest_forecast_file_dated_subdir():
    dtype = "FCST"
    pcw = pcp_combine_wrapper(dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802012100", '%Y%m%d%H%M')
    template = pcw.config.getraw('filename_templates', 'FCST_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc")


def test_get_lowest_forecast_file_no_subdir():
    dtype = "FCST"
    pcw = pcp_combine_wrapper(dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802012100", '%Y%m%d%H%M')

    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
#    template = util.getraw(pcw.config, 'filename_templates', dtype+'_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018020118f003.nc")

def test_get_lowest_forecast_file_yesterday():
    dtype = "FCST"
    pcw = pcp_combine_wrapper(dtype)
    input_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    valid_time = datetime.datetime.strptime("201802010600", '%Y%m%d%H%M')
    template = "file.{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
#    template = util.getraw(pcw.config, 'filename_templates', 'FCST2_PCP_COMBINE_INPUT_TEMPLATE')
    pcw.input_dir = input_dir
    pcw.build_input_accum_list(dtype, {'valid': valid_time})
    out_file = pcw.getLowestForecastFile(valid_time, dtype, template)
    assert(out_file == input_dir+"/file.2018013118f012.nc")    

def test_get_daily_file():
    data_src = "OBS"
    pcw = pcp_combine_wrapper(data_src)
    time_info = {'valid' : datetime.datetime.strptime("201802010000", '%Y%m%d%H%M') }
    accum = 1
    file_template = "file.{valid?fmt=%Y%m%d}.txt"
    pcw.get_daily_file(time_info, accum, data_src, file_template)

def test_setup_add_method():
    rl = "OBS"
    pcw = pcp_combine_wrapper(rl)
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
    output_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fakeout"
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
def test_setup_sum_method():
    rl = "OBS"
    pcw = pcp_combine_wrapper(rl)
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
    output_dir = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fakeout"
    pcw.setup_sum_method(time_info, var_info, rl)
    
    in_files = pcw.infiles
    out_file = pcw.get_output_path()    
    assert(out_file == output_dir+"/20160904/outfile.2016090418_A06h")

def test_setup_subtract_method():
    rl = "FCST"
    pcw = pcp_combine_wrapper(rl)
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

