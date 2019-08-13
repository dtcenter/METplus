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
from mtd_wrapper import MTDWrapper
from config_wrapper import ConfigWrapper
import met_util as util
#from met_util import FieldObj
#from task_info import TaskInfo

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
def mtd_wrapper(lead_seq=None):
    """! Returns a default MTDWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'FCST_VAR1_NAME', 'APCP')
    config.set('config', 'FCST_VAR1_LEVELS', 'A06')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'MTD_CONV_THRESH', '>=10')
    config.set('config', 'MTD_CONV_RADIUS', '15')
    if lead_seq:
        config.set('config', 'LEAD_SEQ', lead_seq)

    return MTDWrapper(config, config.logger)


#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='MTDWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='MTDWrapper')
        produtil.log.postmsg('mtd_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        logger = util.get_logger(config)
        config = ConfigWrapper(config, logger)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'mtd_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------

def test_mtd_by_init_all_found():
    mw = mtd_wrapper('1,2,3')
    obs_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    fcst_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    mw.c_dict['OBS_INPUT_DIR'] = obs_dir
    mw.c_dict['FCST_INPUT_DIR'] = fcst_dir
    mw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc"
    mw.c_dict['FCST_INPUT_TEMPLATE'] = "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2"
    input_dict = {'init' : datetime.datetime.strptime("201705100300", '%Y%m%d%H%M') }
    
    mw.run_at_time(input_dict)
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    assert(fcst_list[0] == os.path.join(fcst_dir,'20170510', '20170510_i03_f001_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_dir,'20170510', '20170510_i03_f002_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_dir,'20170510', 'qpe_2017051004_A06.nc') and
           obs_list[1] == os.path.join(obs_dir,'20170510', 'qpe_2017051005_A06.nc') and
           obs_list[2] == os.path.join(obs_dir,'20170510', 'qpe_2017051006_A06.nc')
           )

def test_mtd_by_valid_all_found():
    mw = mtd_wrapper('1, 2, 3')
    obs_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    fcst_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    mw.c_dict['OBS_INPUT_DIR'] = obs_dir
    mw.c_dict['FCST_INPUT_DIR'] = fcst_dir
    mw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc"
    mw.c_dict['FCST_INPUT_TEMPLATE'] = "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2"
    input_dict = {'valid' : datetime.datetime.strptime("201705100300", '%Y%m%d%H%M') }
    
    mw.run_at_time(input_dict)
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    assert(fcst_list[0] == os.path.join(fcst_dir,'20170510', '20170510_i02_f001_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_dir,'20170510', '20170510_i01_f002_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_dir,'20170510', '20170510_i00_f003_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_dir,'20170510', 'qpe_2017051003_A06.nc') and
           obs_list[1] == os.path.join(obs_dir,'20170510', 'qpe_2017051003_A06.nc') and
           obs_list[2] == os.path.join(obs_dir,'20170510', 'qpe_2017051003_A06.nc')
           )
           
def test_mtd_by_init_miss_fcst():
    mw = mtd_wrapper('3, 6, 9, 12')
    obs_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    fcst_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    mw.c_dict['OBS_INPUT_DIR'] = obs_dir
    mw.c_dict['FCST_INPUT_DIR'] = fcst_dir
    mw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc"
    mw.c_dict['FCST_INPUT_TEMPLATE'] = "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2"
    input_dict = {'init' : datetime.datetime.strptime("201705100300", '%Y%m%d%H%M') }
    
    mw.run_at_time(input_dict)
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    assert(fcst_list[0] == os.path.join(fcst_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_dir,'20170510', '20170510_i03_f006_HRRRTLE_PHPT.grb2') and
           fcst_list[2] == os.path.join(fcst_dir,'20170510', '20170510_i03_f012_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_dir,'20170510', 'qpe_2017051006_A06.nc') and
           obs_list[1] == os.path.join(obs_dir,'20170510', 'qpe_2017051009_A06.nc') and
           obs_list[2] == os.path.join(obs_dir,'20170510', 'qpe_2017051015_A06.nc')
           )

def test_mtd_by_init_miss_both():
    mw = mtd_wrapper('6, 12, 18')
    obs_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    fcst_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    mw.c_dict['OBS_INPUT_DIR'] = obs_dir
    mw.c_dict['FCST_INPUT_DIR'] = fcst_dir
    mw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A{level?fmt=%.2H}.nc"
    mw.c_dict['FCST_INPUT_TEMPLATE'] = "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2"
    input_dict = {'init' : datetime.datetime.strptime("201705100300", '%Y%m%d%H%M') }
    
    mw.run_at_time(input_dict)
    fcst_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_fcst_APCP.txt')
    obs_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_obs_APCP.txt')
    with open(fcst_list_file) as f:
        fcst_list = f.readlines()
    fcst_list = [x.strip() for x in fcst_list]
    with open(obs_list_file) as f:
        obs_list = f.readlines()
    obs_list = [x.strip() for x in obs_list]

    assert(fcst_list[0] == os.path.join(fcst_dir,'20170510', '20170510_i03_f006_HRRRTLE_PHPT.grb2') and
           fcst_list[1] == os.path.join(fcst_dir,'20170510', '20170510_i03_f012_HRRRTLE_PHPT.grb2') and
           obs_list[0] == os.path.join(obs_dir,'20170510', 'qpe_2017051009_A06.nc') and
           obs_list[1] == os.path.join(obs_dir,'20170510', 'qpe_2017051015_A06.nc')
           )


def test_mtd_single():
    mw = mtd_wrapper('1, 2, 3')
    fcst_dir = mw.config.getdir('METPLUS_BASE')+"/internal_tests/data/fcst"
    mw.c_dict['SINGLE_RUN'] = True
    mw.c_dict['SINGLE_DATA_SRC'] = 'FCST'
    mw.c_dict['FCST_INPUT_DIR'] = fcst_dir
    mw.c_dict['FCST_INPUT_TEMPLATE'] = "{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d}_i{init?fmt=%H}_f{lead?fmt=%.3H}_HRRRTLE_PHPT.grb2"
    input_dict = {'init' : datetime.datetime.strptime("201705100300", '%Y%m%d%H%M') }
    
    mw.run_at_time(input_dict)
    single_list_file = os.path.join(mw.config.getdir('STAGING_DIR'), 'file_lists', '201705100300_mtd_single_APCP.txt')
    with open(single_list_file) as f:
        single_list = f.readlines()
    single_list = [x.strip() for x in single_list]

    assert(single_list[0] == os.path.join(fcst_dir,'20170510', '20170510_i03_f001_HRRRTLE_PHPT.grb2') and
           single_list[1] == os.path.join(fcst_dir,'20170510', '20170510_i03_f002_HRRRTLE_PHPT.grb2') and
           single_list[2] == os.path.join(fcst_dir,'20170510', '20170510_i03_f003_HRRRTLE_PHPT.grb2')
           )
