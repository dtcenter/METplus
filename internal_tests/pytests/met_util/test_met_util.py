#!/usr/bin/env python
from __future__ import print_function
import met_util as util


def test_get_date_from_path_subdirs_found():
    date_regex = ".*nam.(2[0-9]{7})"
    dir_to_search = "/d1/METplus_Pointstat/conus_sfc"
    dates_from_path = util.get_date_from_path(dir_to_search, date_regex)

    # Expect 7 dated subdirs to be found for this particular data set.
    num_expected_dates = 7
    assert len(dates_from_path) == num_expected_dates

def test_get_date_from_path_correct_dates():
    expected_dates = ['20170601', '20170602', '20170603', '20170604',
                      '20170605', '20170606', '20170607']
    date_regex = ".*nam.(2[0-9]{7})"
    dir_to_search = "/d1/METplus_Pointstat/conus_sfc"
    dates_from_path = util.get_date_from_path(dir_to_search, date_regex)
    counter =0
    expected_count = 7
    for date_tuple in dates_from_path:
        if date_tuple.data_date in expected_dates:
            counter += 1

    assert counter == expected_count
