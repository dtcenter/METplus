#!/usr/bin/env python
from __future__ import print_function
import sys
import pytest
from dateutil.relativedelta import relativedelta

import time_util

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
    assert(time_util.ti_get_seconds(relative_delta) == seconds and\
           time_util.ti_get_lead_string(relative_delta) == time_string)

# write tests for ti_calculate
