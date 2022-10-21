#!/usr/bin/env python3

import pytest

from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.wrappers.runtime_freq_wrapper import RuntimeFreqWrapper


@pytest.mark.parametrize(
    'runtime, filetime, expected_result', [
        # match same times
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
        # match same times w/ both relativedelta leads
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': relativedelta(hours=3)},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': relativedelta(hours=3)},
         True),
        # match same times w/ 1 relativedelta leads
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': relativedelta(hours=3)},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
        # no match different times
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 14, 0, 0),
          'lead': 7200},
         False),
        # match wildcard init/valid
        ({'init': '*',
          'valid': '*',
          'lead': 10800},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
        # no match wildcard init/valid
        ({'init': '*',
          'valid': '*',
          'lead': 10800},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 7200},
         False),
        # match wildcard init/lead
        ({'init': '*',
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': '*'},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
        # no match wildcard init/lead
        ({'init': '*',
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': '*'},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 14, 0, 0),
          'lead': 7200},
         False),
        # match wildcard valid/lead
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': '*',
          'lead': '*'},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
        # no match wildcard valid/lead
        ({'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': '*',
          'lead': '*'},
         {'init': datetime(2019, 1, 5, 13, 0, 0),
          'valid': datetime(2019, 1, 5, 16, 0, 0),
          'lead': 10800},
         False),
        # match all wildcards
        ({'init': '*',
          'valid': '*',
          'lead': '*'},
         {'init': datetime(2019, 1, 5, 12, 0, 0),
          'valid': datetime(2019, 1, 5, 15, 0, 0),
          'lead': 10800},
         True),
    ]
)
@pytest.mark.wrapper
def test_compare_time_info(metplus_config, runtime, filetime, expected_result):
    config = metplus_config

    wrapper = RuntimeFreqWrapper(config)
    actual_result = wrapper.compare_time_info(runtime, filetime)
    assert actual_result == expected_result
