#!/usr/bin/env python
from __future__ import print_function
import sys
import grid_to_obs_util as g2o_util
import pytest
import met_util as util
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
    date_regex = ".*nam.(2[0-9]{7})"
    # This data is on the DTC NCAR host 'eyewall'
    dir_to_search = "/d1/METplus_Pointstat/dummy_data"
    dates_from_path = g2o_util.get_date_from_path(dir_to_search, date_regex)

    # Expect 7 dated subdirs to be found for this particular data set.
    num_expected_dates = 7
    assert len(dates_from_path) == num_expected_dates


def test_get_date_from_path_correct_dates():
    expected_dates = ['20170601', '20170602', '20170603', '20170604',
                      '20170605', '20170606', '20170607']
    date_regex = ".*nam.(2[0-9]{7})"
    # This data is on the DTC NCAR host 'eyewall'
    dir_to_search = "/d1/METplus_Pointstat/dummy_data"
    dates_from_path = g2o_util.get_date_from_path(dir_to_search, date_regex)
    counter = 0
    expected_count = 7
    for date_tuple in dates_from_path:
        if date_tuple.data_date in expected_dates:
            counter += 1

    assert counter == expected_count

