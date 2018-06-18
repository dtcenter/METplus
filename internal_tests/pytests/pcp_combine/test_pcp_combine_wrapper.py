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
    pcw.p[data_src+'_LEVEL'] = 1
    input_dir = "internal_tests/data/accum"
    valid_time = "2016090418"
    accum = 6

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
        
    pcw.set_input_dir(input_dir)
    pcw.get_accumulation(valid_time, accum, data_src,
                                           file_template, False)
    in_files = pcw.get_input_files()
    assert(len(in_files) == 6)
    assert(input_dir+"/20160904/file.2016090418.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090417.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090416.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090415.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090414.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090413.01h" in in_files)

def test_get_accumulation_6_to_6():
    pcw = pcp_combine_wrapper()
    data_src = "OBS"
    pcw.p[data_src+'_LEVEL'] = 6
    input_dir = "internal_tests/data/accum"
    valid_time = "2016090418"
    accum = 6

    file_template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    
    pcw.set_input_dir(input_dir)
    pcw.get_accumulation(valid_time, accum, data_src,
                                           file_template, False)
    in_files = pcw.get_input_files()    
    assert(len(in_files) == 1)
    assert(input_dir+"/20160904/file.2016090418.06h" in in_files)


def test_get_lowest_forecast_file_dated_subdir():
    pcw = pcp_combine_wrapper()    
    input_dir = "internal_tests/data/fcst"
    valid_time = "2018020121"
    search_time = "2018020121"
    template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, search_time, template)
    assert(out_file == input_dir+"/20180201/file.2018020118f003.nc")


def test_get_lowest_forecast_file_no_subdir():
    pcw = pcp_combine_wrapper()    
    input_dir = "internal_tests/data/fcst"
    valid_time = "2018020121"
    search_time = "2018020121"
    template = "file.{valid?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, search_time, template)
    assert(out_file == input_dir+"/file.2018020118f003.nc")

def test_get_lowest_forecast_file_yesterday():
    pcw = pcp_combine_wrapper()
    input_dir = "internal_tests/data/fcst"
    valid_time = "2018020106"
    search_time = "2018020106"
    template = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.nc"
    pcw.set_input_dir(input_dir)
    out_file = pcw.getLowestForecastFile(valid_time, search_time, template)
    assert(out_file == input_dir+"/file.2018013118f012.nc")    


def test_search_day():
    pcw = pcp_combine_wrapper()
    input_dir = "internal_tests/data/daily"
    file_time = "201802010600"
    search_time = "2018020100"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.search_day(input_dir, file_time, search_time, template)
    assert(out_file == input_dir+"/file.20180201.txt")

    
def test_find_closest_before_today():
    pcw = pcp_combine_wrapper()
    input_dir = "internal_tests/data/daily"
    file_time = "20180201"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.find_closest_before(input_dir, file_time, template)
    assert(out_file == input_dir+"/file.20180201.txt")

def test_find_closest_before_yesterday():
    pcw = pcp_combine_wrapper()
    input_dir = "internal_tests/data/daily"
    file_time = "20180208"
    template = "file.{valid?fmt=%Y%m%d}.txt"
    out_file = pcw.find_closest_before(input_dir, file_time, template)
    assert(out_file == input_dir+"/file.20180207.txt")    

def test_get_daily_file():
    pcw = pcp_combine_wrapper()
    valid_time = "201802010000"
    accum = 1
    data_src = "OBS"
    file_template = "file.{valid?fmt=%Y%m%d}.txt"
    pcw.p[data_src+'_DATA_INTERVAL'] = 1
    pcw.get_daily_file(valid_time,accum, data_src, file_template)

def test_setup_add_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "2016090418"
    var_list = []
    fo = util.FieldObj()
    fo.fcst_name = "APCP"
    fo.obs_name = "ACPCP"
    fo.fcst_extra = ""
    fo.obs_extra = ""
    fo.fcst_level = "A06"
    fo.obs_level = "A06"
    var_list.append(fo)
    rl = "OBS"
    input_dir = "internal_tests/data/accum"
    output_dir = "internal_tests/data/fakeout"
    pcw.p['PCP_COMBINE_INPUT_DIR'] = input_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    pcw.p['PCP_COMBINE_OUTPUT_DIR'] = output_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/outfile.{valid?fmt=%Y%m%d%H}_A{level?fmt=%HH}h"    
    pcw.p[rl+'_NATIVE_DATA_TYPE'] = "NETCDF"
    pcw.setup_add_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
    out_file = pcw.get_output_path()    
    assert(len(in_files) == 6)
    assert(input_dir+"/20160904/file.2016090418.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090417.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090416.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090415.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090414.01h" in in_files)
    assert(input_dir+"/20160904/file.2016090413.01h" in in_files)
    assert(out_file == output_dir+"/20160904/outfile.2016090418_A06h")
    assert("-name ACPCP" in pcw.args)

# how to test? check output?
def test_setup_sum_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "2016090418"
    var_list = []
    fo = util.FieldObj()
    fo.fcst_name = "APCP"
    fo.obs_name = "ACPCP"
    fo.fcst_extra = ""
    fo.obs_extra = ""
    fo.fcst_level = "A06"
    fo.obs_level = "A06"
    var_list.append(fo)
    rl = "OBS"
    input_dir = "internal_tests/data/accum"
    output_dir = "internal_tests/data/fakeout"
    pcw.p['PCP_COMBINE_INPUT_DIR'] = input_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    pcw.p['PCP_COMBINE_OUTPUT_DIR'] = output_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/outfile.{valid?fmt=%Y%m%d%H}_A{level?fmt=%HH}h"    
    pcw.p[rl+'_LEVEL'] = 1
    pcw.setup_sum_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
    out_file = pcw.get_output_path()    
    assert(len(in_files) == 4)
#    assert(input_dir+"/20160904/file.2016090418.01h" in in_files)
#    assert(input_dir+"/20160904/file.2016090417.01h" in in_files)
#    assert(input_dir+"/20160904/file.2016090416.01h" in in_files)
#    assert(input_dir+"/20160904/file.2016090415.01h" in in_files)
#    assert(out_file == output_dir+"/20160904/outfile.2016090418_A06h")
    

#'/usr/local/met-6.1/bin/pcp_combine')['-subtract','/d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f048','48','/d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f024','24','/d1/mccabe/test-newrr/gfs/bucket/gfs.2018030900_A024h','-v','2']
#DEBUG 1: Reading input file: /d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f048
#DEBUG 1: Reading input file: /d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f024
#DEBUG 2: Performing subtraction command.
#DEBUG 1: Writing output file: /d1/mccabe/test-newrr/gfs/bucket/gfs.2018030900_A024h
def test_setup_subtract_method():
    pcw = pcp_combine_wrapper()
    task_info = TaskInfo()
    task_info.init_time = -1
    task_info.valid_time = "2016090418"
    var_list = []
    fo = util.FieldObj()
    fo.fcst_name = "APCP"
    fo.obs_name = "ACPCP"
    fo.fcst_extra = ""
    fo.obs_extra = ""
    fo.fcst_level = "A06"
    fo.obs_level = "A06"
    var_list.append(fo)
    rl = "OBS"
    input_dir = "internal_tests/data/accum"
    output_dir = "internal_tests/data/fakeout"
    pcw.p['PCP_COMBINE_INPUT_DIR'] = input_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/file.{valid?fmt=%Y%m%d%H}.{level?fmt=%HH}h"
    pcw.p['PCP_COMBINE_OUTPUT_DIR'] = output_dir
    pcw.p['PCP_COMBINE_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/outfile.{valid?fmt=%Y%m%d%H}_A{level?fmt=%HH}h"
    pcw.setup_subtract_method(task_info, var_info, rl)
    
    in_files = pcw.get_input_files()
    out_file = pcw.get_output_path()    
    assert(len(in_files) == 2)

