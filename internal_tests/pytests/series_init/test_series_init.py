import pytest
import os
import sys
import logging
from datetime import datetime

import produtil

from metplus.wrappers.series_by_init_wrapper import SeriesByInitWrapper

def series_init_wrapper(metplus_config, config_overrides=None):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'series_init_test.conf'))
    config = metplus_config(extra_configs)
    config.set('config', 'LOOP_ORDER', 'processes')
    if config_overrides:
        for key, value in config_overrides.items():
            config.set('config', key, value)

    return SeriesByInitWrapper(config)

def test_get_fcst_file_info(metplus_config):
    """ Verify that the tuple created by get_fcst_file_info is
        not an empty tuple, and that the number, beginning
        fcst file and end fcst file are what we expected.
    """
    storm_id = 'ML1200942014'
    expected_num = str(9)
    expected_beg = 'F000'
    expected_end = 'F048'

    siw = series_init_wrapper(metplus_config)

    output_dir = (
        os.path.join(siw.config.getdir('METPLUS_BASE'),
                     'internal_tests',
                     'data',
                     'file_lists')
    )
    num, beg, end = siw.get_fcst_file_info(output_dir, storm_id)
    assert num == expected_num
    assert beg == expected_beg
    assert end == expected_end

def test_get_storms_for_init(metplus_config):
    """Verify that the expected number of storms
       are found for the init time 20141214_00
    """
    config = metplus_config()

    expected_storm_list = ['ML1201072014',
                           'ML1221072014',
                           'ML1241072014',
                           'ML1251072014'
                           ]
    time_info = {'init': datetime(2014, 12, 14, 00)}
    stat_input_dir = (
        os.path.join(config.getdir('METPLUS_BASE'),
                     'internal_tests',
                     'data',
                     'stat_data')
    )
    stat_input_template = 'fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    siw = series_init_wrapper(metplus_config)
    siw.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    siw.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template

    storm_list = siw.get_storms_for_init(time_info)
    assert storm_list == expected_storm_list

@pytest.mark.parametrize(
        'file_list, storm_id, expected_files', [
        # filter out storm ID = MY_STORM_ID
        (['/some/file/name',
          '/some/file/MY_STORM_ID',
          '/some/other/MY_STORM_ID/file'],
         'MY_STORM_ID',
         ['/some/file/MY_STORM_ID',
          '/some/other/MY_STORM_ID/file']
         ),
        # no filtering by storm ID
        (['/some/file/name',
          '/some/file/MY_STORM_ID',
          '/some/other/MY_STORM_ID/file'],
         None,
         ['/some/file/name',
          '/some/file/MY_STORM_ID',
          '/some/other/MY_STORM_ID/file']
         ),
        # filter by non-existent storm ID
        (['/some/file/name',
          '/some/file/MY_STORM_ID',
          '/some/other/MY_STORM_ID/file'],
         'OTHER_STORM_ID',
         []
         ),
    ]
)
def test_filter_tiles_storm_id(metplus_config, file_list, storm_id,
                               expected_files):
    siw = series_init_wrapper(metplus_config)
    assert(siw.filter_tiles(file_list,
                            storm_id=storm_id) == sorted(expected_files))

# added list of all files for reference for creating subsets
all_fake_fcst = ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F000_gfs_4_20141215_0000_000.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F006_gfs_4_20141215_0000_006.nc',
                 'fcst/20141215_00/ML1291072014/FCST_TILE_F012_gfs_4_20141215_0000_012.nc',
                  ]
all_fake_anly = ['anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
                 'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
                 'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
                 'anly/20141215_00/ML1291072014/ANLY_TILE_F000_gfs_4_20141215_0000_000.nc',
                 'anly/20141215_00/ML1291072014/ANLY_TILE_F006_gfs_4_20141215_0000_006.nc',
                 'anly/20141215_00/ML1291072014/ANLY_TILE_F012_gfs_4_20141215_0000_012.nc',
                  ]
@pytest.mark.parametrize(
        'time_info, expect_fcst_subset, expect_anly_subset', [
        # filter by init all storms
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': '*'},
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',]),
        # filter by init single storm
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': 'ML1201072014'},
         [
             'fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
             'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         [
             'anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
             'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
             'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # filter by init another single storm
        ({'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          'storm_id': 'ML1221072014'},
         [
             'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         [
             'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
             'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
             'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # filter by lead all storms
        ({'init': '*',
          'valid': '*',
          'lead': 21600,
          'storm_id': '*'},
         [
             'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
             'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         [
             'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
             'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
    ]
)
def test_get_all_files_and_subset(metplus_config, time_info, expect_fcst_subset, expect_anly_subset):
    """! Test to ensure that get_all_files only gets the files that are
    relevant to the runtime settings and not every file in the directory
    """
    config_overrides = {
        'LOOP_BY': 'INIT',
        'SERIES_ANALYSIS_RUNTIME_FREQ': 'RUN_ONCE',
        'INIT_TIME_FMT': '%Y%m%d',
        'INIT_BEG': '20141214',
        'INIT_END': '20141214',
        'INIT_INCREMENT': '12H',
        'LEAD_SEQ': '0H, 6H, 12H',
    }
    wrapper = series_init_wrapper(metplus_config, config_overrides)
    fake_data_dir = os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
    stat_input_dir = os.path.join(fake_data_dir,
                                  'stat_data')
    stat_input_template = 'another_fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    tile_input_dir = os.path.join(fake_data_dir,
                                  'tiles')
    fcst_input_dir = os.path.join(tile_input_dir,
                                  'fcst')
    anly_input_dir = os.path.join(tile_input_dir,
                                  'anly')

    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template
    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = anly_input_dir

    assert(wrapper.get_all_files())

    expected_fcst = [
        'fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
        'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
        'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    expected_fcst_files = []
    for expected in expected_fcst:
        expected_fcst_files.append(os.path.join(tile_input_dir, expected))


    expected_anly = [
        'anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
        'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
        'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
        'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
        'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
        'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
    ]
    expected_anly_files = []
    for expected in expected_anly:
        expected_anly_files.append(os.path.join(tile_input_dir, expected))

    # convert list of lists into a single list to compare to expected results
    fcst_files = [item['fcst'] for item in wrapper.c_dict['ALL_FILES']]
    fcst_files = [item for sub in fcst_files for item in sub]
    anly_files = [item['anly'] for item in wrapper.c_dict['ALL_FILES']]
    anly_files = [item for sub in anly_files for item in sub]

    assert(fcst_files == expected_fcst_files)
    assert(anly_files == expected_anly_files)

    fcst_files_sub, anly_files_sub = wrapper.subset_input_files(time_info)
    assert(fcst_files_sub and anly_files_sub)
    assert(len(fcst_files_sub) == len(anly_files_sub))

    for actual_file, expected_file in zip(fcst_files_sub, expect_fcst_subset):
        assert(actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file)

    for actual_file, expected_file in zip(anly_files_sub, expect_anly_subset):
        assert(actual_file.replace(tile_input_dir, '').lstrip('/') == expected_file)

@pytest.mark.parametrize(
        'config_overrides, time_info, storm_list, lead_group, expect_fcst_subset, expect_anly_subset', [
        # filter by init all storms
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitallstorms'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         ['*'],
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',]),
        # filter by init single storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitstormA'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         ['ML1201072014'],
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # filter by init another single storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "{init?fmt=%Y%m%d_%H}/{storm_id}/series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byinitstormB'},
         {'init': datetime(2014, 12, 14, 0, 0),
          'valid': '*',
          'lead': '*',
          },
         ['ML1221072014'],
         None,
         ['fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
        # filter by lead all storms
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadallstorms'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         ['*'],
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # filter by lead 1 storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadstormA'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         ['ML1201072014'],
         None,
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # filter by lead another storm
        ({'LEAD_SEQ': '0H, 6H, 12H',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadstormB'},
         {'init': '*',
          'valid': '*',
          'lead': 21600,
          },
         ['ML1221072014'],
         None,
         ['fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # filter by lead groups A all storms
        ({'LEAD_SEQ_1': '0H, 6H',
          'LEAD_SEQ_1_LABEL': 'Group1',
          'LEAD_SEQ_2': '12H',
          'LEAD_SEQ_2_LABEL': 'Group2',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadgroupAallstorms'},
         {'init': '*',
          'valid': '*',
          },
         ['*'],
         ('Group1', [0, 21600]),
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F000_gfs_4_20141214_0000_000.nc',
          'fcst/20141214_00/ML1201072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F006_gfs_4_20141214_0000_006.nc',
         ],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F000_gfs_4_20141214_0000_000.nc',
          'anly/20141214_00/ML1201072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F006_gfs_4_20141214_0000_006.nc',
         ]),
        # filter by lead groups B all storms
        ({'LEAD_SEQ_1': '0H, 6H',
          'LEAD_SEQ_1_LABEL': 'Group1',
          'LEAD_SEQ_2': '12H',
          'LEAD_SEQ_2_LABEL': 'Group2',
          'SERIES_ANALYSIS_OUTPUT_TEMPLATE': "series_{fcst_name}_{fcst_level}.nc",
          'TEST_OUTPUT_DIRNAME': 'byleadgroupBallstorms'},
         {'init': '*',
          'valid': '*',
          },
         ['*'],
         ('Group2', [43200]),
         ['fcst/20141214_00/ML1201072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
          'fcst/20141214_00/ML1221072014/FCST_TILE_F012_gfs_4_20141214_0000_012.nc',
         ],
         ['anly/20141214_00/ML1201072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
          'anly/20141214_00/ML1221072014/ANLY_TILE_F012_gfs_4_20141214_0000_012.nc',
         ]),
    ]
)
def test_create_ascii_storm_files_list(metplus_config, config_overrides,
                                       time_info, storm_list, lead_group,
                                       expect_fcst_subset, expect_anly_subset):
    all_config_overrides = {
        'LOOP_BY': 'INIT',
        'SERIES_ANALYSIS_RUNTIME_FREQ': 'RUN_ONCE',
        'INIT_TIME_FMT': '%Y%m%d',
        'INIT_BEG': '20141214',
        'INIT_END': '20141214',
        'INIT_INCREMENT': '12H',
    }
    all_config_overrides.update(config_overrides)
    wrapper = series_init_wrapper(metplus_config, all_config_overrides)
    fake_data_dir = os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                                 'internal_tests',
                                 'data')
    stat_input_dir = os.path.join(fake_data_dir,
                                  'stat_data')
    stat_input_template = 'another_fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    tile_input_dir = os.path.join(fake_data_dir,
                                  'tiles')
    fcst_input_dir = os.path.join(tile_input_dir,
                                  'fcst')
    anly_input_dir = os.path.join(tile_input_dir,
                                  'anly')

    wrapper.c_dict['TC_STAT_INPUT_DIR'] = stat_input_dir
    wrapper.c_dict['TC_STAT_INPUT_TEMPLATE'] = stat_input_template
    wrapper.c_dict['FCST_INPUT_DIR'] = fcst_input_dir
    wrapper.c_dict['OBS_INPUT_DIR'] = anly_input_dir
    test_out_dirname = wrapper.config.getstr('config', 'TEST_OUTPUT_DIRNAME')
    output_dir = os.path.join(wrapper.config.getdir('OUTPUT_BASE'),
                              'series_by',
                              'output',
                              test_out_dirname)
    wrapper.c_dict['OUTPUT_DIR'] = output_dir

    assert(wrapper.get_all_files())

    # read output files and compare to expected list
    if storm_list == ['*']:
        storm_dir = 'all_storms'
    else:
        storm_dir = storm_list[0]

    templates = config_overrides['SERIES_ANALYSIS_OUTPUT_TEMPLATE'].split('/')
    if len(templates) == 1:
        output_prefix = ''
    else:
        output_prefix = os.path.join('20141214_00', storm_dir)

    fcst_list_file = f"{wrapper.FCST_ASCII_FILE_PREFIX}{storm_dir}"
    fcst_file_path = os.path.join(output_dir,
                                  output_prefix,
                                  fcst_list_file)
    if os.path.exists(fcst_file_path):
        os.remove(fcst_file_path)

    anly_list_file = f"{wrapper.ANLY_ASCII_FILE_PREFIX}{storm_dir}"
    anly_file_path = os.path.join(output_dir,
                                  output_prefix,
                                  anly_list_file)
    if os.path.exists(anly_file_path):
        os.remove(anly_file_path)

    assert(wrapper.create_ascii_storm_files_list(time_info,
                                                 storm_list,
                                                 lead_group))

    with open(fcst_file_path, 'r') as file_handle:
        actual_fcsts = file_handle.readlines()
    actual_fcsts = [item.strip() for item in actual_fcsts[1:]]

    for actual_file, expected_file in zip(actual_fcsts, expect_fcst_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert(actual_file == expected_file)

    with open(anly_file_path, 'r') as file_handle:
        actual_anly_files = file_handle.readlines()
    actual_anly_files = [item.strip() for item in actual_anly_files[1:]]

    for actual_file, expected_file in zip(actual_anly_files, expect_anly_subset):
        actual_file = actual_file.replace(tile_input_dir, '').lstrip('/')
        assert(actual_file == expected_file)
