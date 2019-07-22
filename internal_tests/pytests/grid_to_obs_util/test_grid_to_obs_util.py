#!/usr/bin/env python
from __future__ import print_function
import sys
import re
import grid_to_obs_util as g2o_util
import pytest
import produtil
import os
import config_metplus

@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='test ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test ')
        produtil.log.postmsg('met_util test is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'met_util test failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_get_date_from_path_subdirs_found():
    """
       Verifying that the expected number of dated nam files
       are returned, based on the VALID_INIT_BEG = 20170601 and
       VALID_INIT_END = 20170603
    :return:
    """
    date_regex = ".*(2[0-9]{7})"
    # This data is on the DTC NCAR host 'eyewall'
    dir_to_search = "/d1/METplus_Pointstat/dummy_data/nam/conus_sfc"
    dates_from_path = g2o_util.get_date_from_path(dir_to_search, date_regex)

    # Expect 3 dated subdirs to be found for this particular data set.
    num_expected_dates = 3
    assert len(dates_from_path) == num_expected_dates


def test_get_date_from_path_correct_dates():
    expected_dates = ['20170601', '20170602', '20170603']
    file_regex = "nam.2[0-9]{9}.nc"
    date_regex = ".*(2[0-9]{7})"

    # This data is on the DTC NCAR host 'eyewall'
    dir_to_search = "/d1/METplus_Pointstat/dummy_data/nam/conus_sfc"
    dates_from_path = g2o_util.get_date_from_path(dir_to_search, date_regex)

    # Get all the nam files from all the dated subdirectories
    all_nam_files = []
    for cur_date in dates_from_path:
        for root, dates, files in os.walk(cur_date.subdir_filepath):
            for cur_file in files:
                all_nam_files.append(cur_file)


    counter = 0
    expected_count = 3
    for nam_file in all_nam_files:
        match = re.match(file_regex, nam_file)
        if match:
            counter = counter + 1


    assert counter == expected_count

