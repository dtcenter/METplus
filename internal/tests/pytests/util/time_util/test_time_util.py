#!/usr/bin/env python3

import sys
import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.util import time_util


@pytest.mark.parametrize(
    'time_str, shift, expected_output', [
        ('20221101000000', -1, '20221031235959'),
    ]
)
@pytest.mark.util
def test_shift_time_seconds(time_str, shift, expected_output):
    assert time_util.shift_time_seconds(time_str, shift) == expected_output


@pytest.mark.parametrize(
    'input_str, expected_output', [
        ('', []),
        ('0,1,2,3', ['000000', '010000', '020000', '030000']),
        ('12, 24', ['120000', '240000']),
        ('196', ['1960000']),
        ('12H, 24H', ['120000', '240000']),
        ('45M', ['004500']),
        ('42S', ['000042']),
        ('24, 48, 72, 96, 120, 144, 168, 192, 216, 240',
         ['240000', '480000', '720000', '960000', '1200000',
          '1440000', '1680000', '1920000', '2160000', '2400000']),
    ]
)
@pytest.mark.util
def test_get_met_time_list(input_str, expected_output):
    assert time_util.get_met_time_list(input_str) == expected_output


@pytest.mark.parametrize(
    'rd, seconds, time_string, time_letter_only, hours', [
        (relativedelta(seconds=1), 1, '1 second', '1S', 0),
        (relativedelta(seconds=-1), -1, '-1 second', '-1S', 0),
        (relativedelta(seconds=36), 36, '36 seconds', '36S', 0),
        (relativedelta(seconds=-36), -36, '-36 seconds', '-36S', 0),
        (relativedelta(minutes=1), 60, '1 minute', '1M', 0),
        (relativedelta(minutes=-1), -60, '-1 minute', '-1M', 0),
        (relativedelta(minutes=4), 240, '4 minutes', '4M', 0),
        (relativedelta(minutes=-4), -240, '-4 minutes', '-4M', 0),
        (relativedelta(hours=1), 3600, '1 hour', '1H', 1),
        (relativedelta(hours=-1), -3600, '-1 hour', '-1H', -1),
        (relativedelta(hours=2), 7200, '2 hours', '2H', 2),
        (relativedelta(hours=-2), -7200, '-2 hours', '-2H', -2),
        (relativedelta(days=1), 86400, '1 day', '1d', 24),
        (relativedelta(days=-1), -86400, '-1 day', '-1d', -24),
        (relativedelta(days=2), 172800, '2 days', '2d', 48),
        (relativedelta(days=-2), -172800, '-2 days', '-2d', -48),
        (relativedelta(months=1), None, '1 month', '1m', None),
        (relativedelta(months=-1), None, '-1 month', '-1m', None),
        (relativedelta(months=6), None, '6 months', '6m', None),
        (relativedelta(months=-6), None, '-6 months', '-6m', None),
        (relativedelta(years=1), None, '1 year', '1Y', None),
        (relativedelta(years=-1), None, '-1 year', '-1Y', None),
        (relativedelta(years=6), None, '6 years', '6Y', None),
        (relativedelta(years=-6), None, '-6 years', '-6Y', None),
        (relativedelta(seconds=61), 61, '1 minute 1 second', '1M1S', 0),
        (relativedelta(seconds=-61), -61, '-1 minute 1 second', '-1M1S', 0),
        (relativedelta(seconds=3602), 3602, '1 hour 2 seconds', '1H2S', 1),
        (relativedelta(seconds=-3602), -3602, '-1 hour 2 seconds', '-1H2S', -1),
        (relativedelta(seconds=3721), 3721, '1 hour 2 minutes 1 second', '1H2M1S', 1),
        (relativedelta(seconds=-3721), -3721, '-1 hour 2 minutes 1 second', '-1H2M1S', -1),
    ]
)
@pytest.mark.util
def test_ti_get_seconds_and_string(rd, seconds, time_string, time_letter_only, hours):
    assert time_util.ti_get_seconds_from_relativedelta(rd) == seconds
    assert time_util.ti_get_lead_string(rd) == time_string
    assert time_util.ti_get_lead_string(rd, letter_only=True) == time_letter_only
    assert time_util.ti_get_hours_from_relativedelta(rd) == hours


@pytest.mark.parametrize(
    'key, value', [
        ('1m', datetime(2019, 3, 1, 0) ),
        ('-1m', datetime(2019, 1, 1, 0) ),
        ('1Y', datetime(2020, 2, 1, 0) ),
        ('-1Y', datetime(2018, 2, 1, 0) ),
        ('1d', datetime(2019, 2, 2, 0) ),
        ('-1d', datetime(2019, 1, 31, 0) ),
        ('1H', datetime(2019, 2, 1, 1) ),
        ('-1H', datetime(2019, 1, 31, 23) ),
        ('1M', datetime(2019, 2, 1, 0, 1) ),
        ('-1M', datetime(2019, 1, 31, 23, 59) ),
        ('1S', datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1S', datetime(2019, 1, 31, 23, 59, 59) ),
        ('1', datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1', datetime(2019, 1, 31, 23, 59, 59) ),
        ('393d', datetime(2020, 2, 29, 0) ), # leap year
    ]
)
@pytest.mark.util
def test_get_relativedelta(key, value):
    # start time is 2019-02-01_0Z
    start_time = datetime(2019, 2, 1, 0)
    assert start_time + time_util.get_relativedelta(key) == value


@pytest.mark.parametrize(
    'time_string, default_unit, met_time', [
        ('3H', None, '03'),
        ('3M', None, '000300'),
        ('3S', None, '000003'),
        ('3', 'H', '03'),
        ('3', 'M', '000300'),
        ('3', 'S', '000003'),
        ('12345H', None, '12345'),
        ('123456H', None, '1234560000'),
        ('123456', 'H', '1234560000'),
        ('90M', None, '013000'),
        ('90S', None, '000130'),
        ('3723S', None, '010203'),
        ]
)
@pytest.mark.util
def test_time_string_to_met_time(time_string, default_unit, met_time):
    assert time_util.time_string_to_met_time(time_string, default_unit) == met_time


@pytest.mark.parametrize(
    'input_dict, expected_time_info', [
        # init and lead input
        ({'init': datetime(2014, 10, 31, 12), 'lead': relativedelta(hours=3)},
         {'init': datetime(2014, 10, 31, 12), 'lead': 10800, 'valid':  datetime(2014, 10, 31, 15)}),
        # valid and lead input
        ({'valid': datetime(2014, 10, 31, 12), 'lead': relativedelta(hours=3)},
         {'valid': datetime(2014, 10, 31, 12), 'lead': 10800, 'init':  datetime(2014, 10, 31, 9)}),
        # init/valid/lead input, loop_by init
        ({'init': datetime(2014, 10, 31, 12), 'lead': relativedelta(hours=6), 'valid': datetime(2014, 10, 31, 15), 'loop_by': 'init'},
         {'init': datetime(2014, 10, 31, 12), 'lead': 21600, 'valid':  datetime(2014, 10, 31, 18)}),
        # init/valid/lead input, loop_by valid
        ({'valid': datetime(2014, 10, 31, 12), 'lead': relativedelta(hours=6), 'init':  datetime(2014, 10, 31, 9), 'loop_by': 'valid'},
         {'valid': datetime(2014, 10, 31, 12), 'lead': 21600, 'init':  datetime(2014, 10, 31, 6)}),
        # RUN_ONCE: init/valid/lead all wildcards
        ({'init': '*', 'valid': '*', 'lead': '*'},
         {'init': '*', 'valid': '*', 'lead': '*', 'date': '*'}),
        # RUN_ONCE_PER_INIT_OR_VALID: init/valid is time, wildcard lead/opposite
        ({'init': datetime(2014, 10, 31, 12), 'valid': '*', 'lead': '*'},
         {'init': datetime(2014, 10, 31, 12), 'valid': '*', 'lead': '*', 'date': datetime(2014, 10, 31, 12)}),
        ({'init': '*', 'valid': datetime(2014, 10, 31, 12), 'lead': '*'},
         {'init': '*', 'valid': datetime(2014, 10, 31, 12), 'lead': '*', 'date': datetime(2014, 10, 31, 12)}),
        # RUN_ONCE_PER_LEAD: lead is time interval, init/valid are wildcards
        ({'init': '*', 'valid': '*', 'lead': relativedelta(hours=3)},
         {'init': '*', 'valid': '*', 'lead': relativedelta(hours=3), 'date': '*'}),
        # case that failed in GFDLTracker wrapper
        ({'init': datetime(2021, 7, 13, 0, 0), 'lead': 21600, 'offset_hours': 0},
         {'init': datetime(2021, 7, 13, 0, 0), 'lead': 21600, 'valid': datetime(2021, 7, 13, 6, 0), 'offset': 0}),
        # lead is months or years (relativedelta)
        # allows lead to remain relativedelta in case init/valid change but still computes lead hours
        ({'init': datetime(2021, 7, 13, 0, 0), 'lead': relativedelta(months=1)},
         {'init': datetime(2021, 7, 13, 0, 0), 'lead': relativedelta(months=1), 'valid': datetime(2021, 8, 13, 0, 0), 'lead_hours': 744}),
        ]
)
@pytest.mark.util
def test_ti_calculate(input_dict, expected_time_info):
    # pass input_dict into ti_calculate and check that expected values are set
    time_info = time_util.ti_calculate(input_dict)
    for key, value in expected_time_info.items():
        assert time_info[key] == value

    # pass output of ti_calculate back into ti_calculate and check values
    time_info2 = time_util.ti_calculate(time_info)
    for key, value in expected_time_info.items():
        assert time_info[key] == value
        assert time_info2[key] == value


@pytest.mark.parametrize(
    'lead, valid_time, expected_val', [
        # returns None if lead is not a relativedelta object
        (None, None, None),
        (1, None, None),
        ('1', None, None),
        # leads that can be computed without a reference time
        (relativedelta(seconds=3), None, 3),
        (relativedelta(minutes=3), None, 180),
        (relativedelta(hours=3), None, 10800),
        (relativedelta(days=3), None, 259200),
        (relativedelta(minutes=3, seconds=3), None, 183),
        # leads that cannot be computed without a reference time
        (relativedelta(months=3), None, None),
        (relativedelta(years=3), None, None),
        (relativedelta(months=3, years=3), None, None),
        # valid time is string 'ALL' - should behave the same as no valid time
        (relativedelta(seconds=3), 'ALL', 3),
        (relativedelta(minutes=3), 'ALL', 180),
        (relativedelta(hours=3), 'ALL', 10800),
        (relativedelta(days=3), 'ALL', 259200),
        (relativedelta(minutes=3, seconds=3), 'ALL', 183),
        (relativedelta(months=3), 'ALL', None),
        (relativedelta(years=3), 'ALL', None),
        (relativedelta(months=3, years=3), 'ALL', None),
        # valid time is datetime object - months and years should work
        (relativedelta(seconds=3), datetime(2014, 10, 31, 12), 3),
        (relativedelta(minutes=3), datetime(2014, 10, 31, 12), 180),
        (relativedelta(hours=3), datetime(2014, 10, 31, 12), 10800),
        (relativedelta(days=3), datetime(2014, 10, 31, 12), 259200),
        (relativedelta(minutes=3, seconds=3), datetime(2014, 10, 31, 12), 183),
        (relativedelta(months=1), datetime(2014, 10, 31, 12), 2678400),
        (relativedelta(years=1), datetime(2014, 10, 31, 12), 31536000),
        (relativedelta(months=1, years=1), datetime(2014, 10, 31, 12), 34214400),
    ]
)
@pytest.mark.util
def test_ti_get_seconds_from_relativedelta(lead, valid_time, expected_val):
    assert time_util.ti_get_seconds_from_relativedelta(lead, valid_time) == expected_val
