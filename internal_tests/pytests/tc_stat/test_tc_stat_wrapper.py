#!/usr/bin/env python

import os
import sys
import pytest
import datetime

import produtil

from metplus.wrappers.tc_stat_wrapper import TCStatWrapper
from metplus.util import ti_calculate


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
         {'JOBS': ['-job filter -dump_row filter_201401214_00.tcst']}),

        ({'TC_STAT_JOB_ARGS': ('-job filter -dump_row filter_201401214_00.tcst,'
                              '-job summary -dump_row summary.tcst  '), },
         {'JOBS': ['-job filter -dump_row filter_201401214_00.tcst',
                   '-job summary -dump_row summary.tcst']}),

        ({'TC_STAT_MATCH_POINTS': 'yes', },
         {'MATCH_POINTS': 'match_points = TRUE;'}),

        ({'TC_STAT_LOOKIN_DIR': '/my/new/input/dir', },
         {'LOOKIN_DIR': '/my/new/input/dir'}),

    ]
    )
def test_override_config_in_c_dict(metplus_config, overrides, c_dict):
    wrapper = TCStatWrapper(get_config(metplus_config),
                            config_overrides=overrides)
    for key, expected_value in c_dict.items():
        assert (wrapper.c_dict.get(key) == expected_value)

@pytest.mark.parametrize(
    'jobs, init_dt, expected_output', [
        # single fake job
            (['job1'],
             None,
             'jobs = ["job1"];'
            ),
        # 2 jobs, no time info
            (['-job filter -dump_row <output_dir>/filt.tcst',
              '-job rirw -line_type TCMPR '],
             None,
             'jobs = ["-job filter -dump_row <output_dir>/filt.tcst",'
             '"-job rirw -line_type TCMPR"];'
            ),

        # 2 jobs, time info sub
        (['-job filter -dump_row <output_dir>/{init?fmt=%Y%m%d%H}.tcst',
          '-job rirw -line_type TCMPR '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/2019103112.tcst",'
         '"-job rirw -line_type TCMPR"];'
         ),
    ]
)
def test_handle_jobs(metplus_config, jobs, init_dt, expected_output):
    if init_dt:
        time_info = ti_calculate({'init': init_dt})
    else:
        time_info = None

    wrapper = tc_stat_wrapper(metplus_config)
    output_base = wrapper.config.getdir('OUTPUT_BASE')
    output_dir = os.path.join(output_base, 'test_handle_jobs')

    wrapper.c_dict['JOBS'] = []
    for job in jobs:
        wrapper.c_dict['JOBS'].append(job.replace('<output_dir>', output_dir))

    output = wrapper.handle_jobs(time_info)
    assert(output == expected_output.replace('<output_dir>', output_dir))


def cleanup_test_dirs(parent_dirs, output_dir):
    if parent_dirs:
        for parent_dir in parent_dirs:
            parent_dir_sub = parent_dir.replace('<output_dir>', output_dir)
            if os.path.exists(parent_dir_sub):
                os.removedirs(parent_dir_sub)

@pytest.mark.parametrize(
    'jobs, init_dt, expected_output, parent_dirs', [
        # single fake job, no parent dir
            (['job1'],
             None,
             'jobs = ["job1"];',
             None
            ),
        # 2 jobs, no time info, 1 parent dir
            (['-job filter -dump_row <output_dir>/filt.tcst',
              '-job rirw -line_type TCMPR '],
             None,
             'jobs = ["-job filter -dump_row <output_dir>/filt.tcst",'
             '"-job rirw -line_type TCMPR"];',
             ['<output_dir>'],
            ),

        # 2 jobs, time info sub, 1 parent dir
        (['-job filter -dump_row <output_dir>/{init?fmt=%Y%m%d%H}.tcst',
          '-job rirw -line_type TCMPR '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/2019103112.tcst",'
         '"-job rirw -line_type TCMPR"];',
         ['<output_dir>'],
         ),

        # 2 jobs, no time info, 2 parent dirs
        (['-job filter -dump_row <output_dir>/subdir1/filt.tcst',
          '-job filter -dump_row <output_dir>/subdir2/filt2.tcst '],
         None,
         'jobs = ["-job filter -dump_row <output_dir>/subdir1/filt.tcst",'
         '"-job filter -dump_row <output_dir>/subdir2/filt2.tcst"];',
         ['<output_dir>/subdir1',
          '<output_dir>/subdir2',
          ],
         ),

        # 2 jobs, time info sub, 2 parent dirs
        (['-job filter -dump_row <output_dir>/sub1/{init?fmt=%Y%m%d%H}.tcst',
          '-job filter -dump_row <output_dir>/sub2/{init?fmt=%Y%m%d}.tcst '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/sub1/2019103112.tcst",'
         '"-job filter -dump_row <output_dir>/sub2/20191031.tcst"];',
         ['<output_dir>/sub1',
          '<output_dir>/sub2',],
         ),
    ]
)
def test_handle_jobs_create_parent_dir(metplus_config, jobs, init_dt,
                                       expected_output, parent_dirs):
    # if init time is provided, calculate other time dict items
    if init_dt:
        time_info = ti_calculate({'init': init_dt})
    else:
        time_info = None

    wrapper = tc_stat_wrapper(metplus_config)

    # create directory path relative to OUTPUT_BASE to test that function
    # creates parent directories properly
    # Used to replace <output_dir> string found in test arguments
    output_base = wrapper.config.getdir('OUTPUT_BASE')
    output_dir = os.path.join(output_base, 'test_handle_jobs')

    # remove parent dirs if they exist
    cleanup_test_dirs(parent_dirs, output_dir)

    wrapper.c_dict['JOBS'] = []
    for job in jobs:
        wrapper.c_dict['JOBS'].append(job.replace('<output_dir>', output_dir))

    output = wrapper.handle_jobs(time_info)
    if output != expected_output.replace('<output_dir>', output_dir):
        assert False

    # check if parent dir was created
    if parent_dirs:
        for parent_dir in parent_dirs:
            parent_dir_sub = parent_dir.replace('<output_dir>', output_dir)
            if not os.path.exists(parent_dir_sub):
                assert False

    # remove parent dirs to clean up for next run
    cleanup_test_dirs(parent_dirs, output_dir)
