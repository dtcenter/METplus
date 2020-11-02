#!/usr/bin/env python

import os
import sys
import pytest
import produtil

from metplus.wrappers.tc_stat_wrapper import TCStatWrapper


#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#

# Add a test configuration
def pytest_addoption(parser):
    """! For supporting config files from the command line"""
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    """! For supporting the additional config files used by METplus"""
    return request.config.getoption("-c")

def get_config(metplus_config):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'tc_stat_conf.conf'))
    return metplus_config(extra_configs)

def tc_stat_wrapper(metplus_config):
    """! Returns a default TCStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TcStatWrapper with some configuration values set
    # to /path/to:
    config = get_config(metplus_config)
    return TCStatWrapper(config)

def test_validate_config_values(metplus_config):
    """! Test that when the COLUMN_THRESH_NAME and COLUMN_THRESH_VAL lists
         are of different length, the appropriate value is returned
         from config_lists_ok()
    """
    tcsw = tc_stat_wrapper(metplus_config)

    # Uneven lengths, expect False to be returned
    column_thresh_name = "A, B, C"
    column_thresh_val = "1,2"
    tcsw.c_dict['COLUMN_THRESH_NAME'] = column_thresh_name
    tcsw.c_dict['COLUMN_THRESH_VAL'] = column_thresh_val
    tcsw.validate_config_values(tcsw.c_dict)
    assert tcsw.isOK is False

@pytest.mark.parametrize(
        'overrides, c_dict', [
            ({'TC_STAT_INIT_BEG': '20150301',
              'TC_STAT_INIT_END': '20150304',
              'TC_STAT_BASIN': 'ML', },
             {'INIT_BEG': 'init_beg = "20150301";',
              'INIT_END': 'init_end = "20150304";',
              'BASIN': 'basin = ["ML"];',
              'CYCLONE': None,
              'STORM_NAME': None,}),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150304',
          'TC_STAT_CYCLONE': '030020', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150304";',
          'BASIN': None,
          'CYCLONE': 'cyclone = ["030020"];',
          'STORM_NAME': None, }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150325',
          'TC_STAT_STORM_NAME': '123', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150325";',
          'INIT_HOUR': 'init_hour = ["00"];', # from config file
          'BASIN': None,
          'CYCLONE': None,
          'STORM_NAME': 'storm_name = ["123"];', }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150325',
          'TC_STAT_STORM_ID': 'ML032015',
          'TC_STAT_INIT_HOUR': '',
         },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150325";',
          'INIT_HOUR': None,
          'BASIN': None,
          'CYCLONE': None,
          'STORM_ID': 'storm_id = ["ML032015"];', }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150304',
          'TC_STAT_INIT_HOUR': '',
          'TC_STAT_CYCLONE': '030020',
          'TC_STAT_BASIN': 'ML', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150304";',
          'INIT_HOUR': None,
          'BASIN': 'basin = ["ML"];',
          'CYCLONE': 'cyclone = ["030020"];',
          'STORM_NAME': None, }),

        ({'TC_STAT_JOB_ARGS': '-job filter -dump_row filter_201401214_00.tcst',},
         {'JOBS': '-job filter -dump_row filter_201401214_00.tcst'}),

        ({'TC_STAT_MATCH_POINTS': 'yes', },
         {'MATCH_POINTS': True}),

        ({'TC_STAT_INPUT_DIR': '/my/new/input/dir', },
         {'INPUT_DIR': '/my/new/input/dir'}),

    ]
    )
def test_override_config_in_c_dict(metplus_config, overrides, c_dict):
    wrapper = TCStatWrapper(get_config(metplus_config), overrides)
    for key, expected_value in c_dict.items():
        assert (wrapper.c_dict.get(key) == expected_value)
