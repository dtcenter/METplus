#!/usr/bin/env python

import sys
import pytest
import datetime
from dateutil.relativedelta import relativedelta

from metplus.util import time_util

@pytest.mark.parametrize(
    'relative_delta, seconds, time_string', [
        (relativedelta(seconds=1), 1, '1 second' ),
        (relativedelta(seconds=-1), -1, '-1 second' ),
        (relativedelta(seconds=36), 36, '36 seconds' ),
        (relativedelta(seconds=-36), -36, '-36 seconds' ),
        (relativedelta(minutes=1), 60, '1 minute' ),
        (relativedelta(minutes=-1), -60, '-1 minute' ),
        (relativedelta(minutes=4), 240, '4 minutes' ),
        (relativedelta(minutes=-4), -240, '-4 minutes' ),
        (relativedelta(hours=1), 3600, '1 hour' ),
        (relativedelta(hours=-1), -3600, '-1 hour' ),
        (relativedelta(hours=2), 7200, '2 hours' ),
        (relativedelta(hours=-2), -7200, '-2 hours' ),
        (relativedelta(days=1), 86400, '1 day' ),
        (relativedelta(days=-1), -86400, '-1 day' ),
        (relativedelta(days=2), 172800, '2 days' ),
        (relativedelta(days=-2), -172800, '-2 days' ),
        (relativedelta(months=1), None, '1 month' ),
        (relativedelta(months=-1), None, '-1 month' ),
        (relativedelta(months=6), None, '6 months' ),
        (relativedelta(months=-6), None, '-6 months' ),
        (relativedelta(years=1), None, '1 year' ),
        (relativedelta(years=-1), None, '-1 year' ),
        (relativedelta(years=6), None, '6 years' ),
        (relativedelta(years=-6), None, '-6 years' ),
        (relativedelta(seconds=61), 61, '1 minute 1 second' ),
        (relativedelta(seconds=-61), -61, '-1 minute -1 second' ),
        (relativedelta(seconds=3602), 3602, '1 hour 2 seconds' ),
        (relativedelta(seconds=-3602), -3602, '-1 hour -2 seconds' ),
        (relativedelta(seconds=3721), 3721, '1 hour 2 minutes 1 second' ),
        (relativedelta(seconds=-3721), -3721, '-1 hour -2 minutes -1 second' ),
    ]
)
def test_ti_get_seconds_and_string(relative_delta, seconds, time_string):
    assert(time_util.ti_get_seconds_from_relativedelta(relative_delta) == seconds and\
           time_util.ti_get_lead_string(relative_delta) == time_string)

@pytest.mark.parametrize(
    'key, value', [
        ('1m', datetime.datetime(2019, 3, 1, 0) ),
        ('-1m', datetime.datetime(2019, 1, 1, 0) ),
        ('1Y', datetime.datetime(2020, 2, 1, 0) ),
        ('-1Y', datetime.datetime(2018, 2, 1, 0) ),
        ('1d', datetime.datetime(2019, 2, 2, 0) ),
        ('-1d', datetime.datetime(2019, 1, 31, 0) ),
        ('1H', datetime.datetime(2019, 2, 1, 1) ),
        ('-1H', datetime.datetime(2019, 1, 31, 23) ),
        ('1M', datetime.datetime(2019, 2, 1, 0, 1) ),
        ('-1M', datetime.datetime(2019, 1, 31, 23, 59) ),
        ('1S', datetime.datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1S', datetime.datetime(2019, 1, 31, 23, 59, 59) ),
        ('1', datetime.datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1', datetime.datetime(2019, 1, 31, 23, 59, 59) ),
        ('393d', datetime.datetime(2020, 2, 29, 0) ), # leap year
    ]
)
def test_get_relativedelta(key, value):
    # start time is 2019-02-01_0Z
    start_time = datetime.datetime(2019, 2, 1, 0)
    assert(start_time + time_util.get_relativedelta(key) == value)

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
def test_time_string_to_met_time(time_string, default_unit, met_time):
  assert(time_util.time_string_to_met_time(time_string, default_unit) == met_time)

# write tests for ti_calculate
