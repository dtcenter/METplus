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
from grid_stat_wrapper import GridStatWrapper
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
def grid_stat_wrapper():
    """! Returns a default GridStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    conf = metplus_config()
    return GridStatWrapper(conf, None)


@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='GridStatWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='GridStatWrapper')
        produtil.log.postmsg('grid_stat_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'grid_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_find_obs_no_dated
# ------------------------
def test_find_obs_no_dated():
    pcw = grid_stat_wrapper()
    task_info = TaskInfo()
    task_info.valid_time = "201802010000"
    task_info.lead = 0

    pcw.cg_dict['OBS_INPUT_DIR'] = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
#    pcw.cg_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d_%H%M}"
    pcw.cg_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file = pcw.find_obs(task_info)
    assert(obs_file == pcw.cg_dict['OBS_INPUT_DIR']+'/20180201_0045')


def test_find_obs_dated():
    pcw = grid_stat_wrapper()
    task_info = TaskInfo()
    task_info.valid_time = "201802010000"
    task_info.lead = 0

    pcw.cg_dict['OBS_INPUT_DIR'] = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.cg_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    obs_file = pcw.find_obs(task_info)
    assert(obs_file == pcw.cg_dict['OBS_INPUT_DIR']+'/20180201/20180201_0013')

def test_find_obs_dated_previous_day():
    pcw = grid_stat_wrapper()
    task_info = TaskInfo()
    task_info.valid_time = "201802010000"
    task_info.lead = 0

    pcw.cg_dict['OBS_INPUT_DIR'] = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.cg_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.cg_dict['WINDOW_RANGE_BEG'] = -3600
    pcw.cg_dict['WINDOW_RANGE_END'] = 0
    obs_file = pcw.find_obs(task_info)
    assert(obs_file == pcw.cg_dict['OBS_INPUT_DIR']+'/20180131/20180131_2345')

def test_find_obs_dated_next_day():
    pcw = grid_stat_wrapper()
    task_info = TaskInfo()
    task_info.valid_time = "201802012345"
    task_info.lead = 0

    pcw.cg_dict['OBS_INPUT_DIR'] = pcw.p.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.cg_dict['OBS_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d}/{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}'
    pcw.cg_dict['WINDOW_RANGE_BEG'] = 0
    pcw.cg_dict['WINDOW_RANGE_END'] = 3600
    obs_file = pcw.find_obs(task_info)
    assert(obs_file == pcw.cg_dict['OBS_INPUT_DIR']+'/20180202/20180202_0013')
    
