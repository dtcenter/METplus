""" Tests for the ExtractTiles wrapper, extract_tiles_wrapper.py using tc_pairs output
    generated from running the TcPairs wrapper, tc_pairs_wrapper.py and using the
    sample data on 'eyewall': /d1/METplus_Data/cyclone_track_feature/reduced_model_data


"""
from __future__ import (print_function, division)

# !/usr/bin/env python
import sys
import os
import datetime
import logging
import re
import pytest
from extract_tiles_wrapper import ExtractTilesWrapper
import produtil
import config_metplus
import met_util
from string_template_substitution import StringSub


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
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
@pytest.fixture
def extract_tiles_wrapper():
    """! Returns a default PB2NCWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    conf = metplus_config()
    logger = logging.getLogger("dummy")

    conf.set('config', 'LOOP_ORDER', 'processes')
    return ExtractTilesWrapper(conf, logger)

@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='ExtractTilesWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='ExtractTilesWrapper ')
        produtil.log.postmsg('extract_tiles_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'extract tiles wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def create_input_dict(config):
    """Create the input time dictionary that is needed by run_at_time()
       for the extract tiles wrapper.  Logic was extracted from the
       met_util.py loop_over_times_and_call() function.

       Return:
           input_dict: The dictionary with the init and now datetimes
    """
    input_dict = {}
    init_beg = config.getstr('config', 'INIT_BEG')
    clock_time_obj = datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                '%Y%m%d%H%M%S')

    time_format = config.getstr('config', 'INIT_TIME_FMT')
    today = clock_time_obj.strftime('%Y%m%d')
    # loop_time =  datetime.datetime.strptime(today, time_format)
    loop_time =  datetime.datetime.strptime(init_beg, time_format)
    input_dict['now'] = clock_time_obj

    input_dict['init'] = loop_time

    return input_dict


# ------------------------ TESTS GO HERE --------------------------

def test_output_exists(metplus_config):
    """
    Expect 186 netcdf files to be generated from the tc_pairs files
    generated via the TcPairsWrapper, input directory is
    the
    """

    input_dict = create_input_dict(metplus_config)
    etw = extract_tiles_wrapper()
    etw.run_at_time(input_dict)
    dir_section = metplus_config.items('dir')
    expected_num_nc_files = 186
    actual_nc_files = []

    for section, value in dir_section:
        match = re.match(r'OUTPUT_BASE', section)
        if match:
            output_dir = os.path.join(value, 'extract_tiles')
            # break out as soon as we find a match to the OUTPUT_BASE in the dir section.
            break

    for root, dirs, files in os.walk(output_dir):
        for cur_file in files:
            if cur_file.endswith('.nc'):
               actual_nc_files.append(cur_file)


    assert(expected_num_nc_files == len(actual_nc_files))