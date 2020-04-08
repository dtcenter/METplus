#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime
import config_metplus
from gen_vx_mask_wrapper import GenVxMaskWrapper
import met_util as util
import time_util

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
def gen_vx_mask_wrapper():
    """! Returns a default GenVxMaskWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return GenVxMaskWrapper(config, config.logger)

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='GenVxMaskWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='GenVxMaskWrapper')
        produtil.log.postmsg('gen_vx_mask_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        logger = util.get_logger(config)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'gen_vx_mask_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_
# ------------------------
def test_run_gen_vx_mask_once():
    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    wrap = gen_vx_mask_wrapper()
    wrap.c_dict['INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT']
    wrap.c_dict['OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                             'GenVxMask_test')
    wrap.c_dict['OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH_LAT_MASK.nc'
    wrap.c_dict['COMMAND_OPTIONS'] = ["-type lat -thresh 'ge30&&le50'"]
#    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT', 'LON']
#    wrap.c_dict['COMMAND_OPTIONS'] = ["-type lat -thresh 'ge30&&le50'", "-type lon -thresh 'le-70&&ge-130' -intersection"]

    wrap.run_at_time_all(time_info)

    expected_cmd = f"{wrap.app_path} 2018020100_ZENITH LAT {wrap.config.getdir('OUTPUT_BASE')}/GenVxMask_test/2018020100_ZENITH_LAT_MASK.nc -type lat -thresh 'ge30&&le50' -v 2"

    for cmd in wrap.all_commands:
        print(f"COMMAND:{cmd}")
        print("EXPECTED:{expected_cmd}")
        assert(cmd == expected_cmd)

def test_run_gen_vx_mask_twice():
    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    wrap = gen_vx_mask_wrapper()
    wrap.c_dict['INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['MASK_INPUT_TEMPLATES'] = ['LAT', 'LON']
    wrap.c_dict['OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                             'GenVxMask_test')
    wrap.c_dict['OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH_LAT_LON_MASK.nc'
    cmd_args = ["-type lat -thresh 'ge30&&le50'", "-type lon -thresh 'le-70&&ge-130' -intersection"]
    wrap.c_dict['COMMAND_OPTIONS'] = cmd_args

    wrap.run_at_time_all(time_info)

    expected_cmds = [f"{wrap.app_path} 2018020100_ZENITH LAT {wrap.config.getdir('OUTPUT_BASE')}/stage/gen_vx_mask/temp_0.nc {cmd_args[0]} -v 2",
                     f"{wrap.app_path} {wrap.config.getdir('OUTPUT_BASE')}/stage/gen_vx_mask/temp_0.nc LON {wrap.config.getdir('OUTPUT_BASE')}/GenVxMask_test/2018020100_ZENITH_LAT_LON_MASK.nc {cmd_args[1]} -v 2"]

    test_passed = True

    if len(wrap.all_commands) != len(expected_cmds):
        print("Number of commands run is not the same as expected")
        assert(False)

    for cmd, expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert(test_passed)

