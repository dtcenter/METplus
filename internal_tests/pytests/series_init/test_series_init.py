import pytest
import os
import sys
import logging
import datetime

import produtil

from metplus.wrappers.series_by_init_wrapper import SeriesByInitWrapper

def series_init_wrapper(metplus_config):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'series_init_test.conf'))
    config = metplus_config(extra_configs)
    config.set('config', 'LOOP_ORDER', 'processes')
    return SeriesByInitWrapper(config)

def test_storm_files_list_OK(metplus_config):
    """ Verify that for the input data (extract tiles output),
        we are generating a list of storm files that match
        the init time and storm basin specified in the config
        file.
    """
    pytest.skip('Hard-coded output directories do not match current setup')

    siw = series_init_wrapper(metplus_config)
    tile_dir = '/d1/METplus_test_input/series_init/extract_tiles'
    storm_list = siw.get_ascii_storm_files_list(tile_dir)
    assert len(storm_list) > 0

def test_build_and_run_series_request_OK(metplus_config):
    """ Verify that the command that is
        created produces output.
        ***NOTE***:  This tests creates
        numerous met_config_nnnnn_n files!

    """
    pytest.skip('Hard-coded output directories do not match current setup')

    siw = series_init_wrapper(metplus_config)
    tile_dir = '/d1/METplus_test_input/series_init/extract_tiles'
    sorted_filter_init = siw.get_ascii_storm_files_list(tile_dir)
    assert len(sorted_filter_init) > 0
    # siw.build_and_run_series_request(sorted_filter_init, tile_dir)
    # assert len(siw.get_command()) > 0

def test_get_fcst_file_info_OK(metplus_config):
    """ Verify that the tuple created by get_fcst_file_info is
        not an empty tuple, and that the number, beginning
        fcst file and end fcst file are what we expected.
    """
    pytest.skip('Wrapper needs refactor')

    # number of forecast files we expect for specified storm;
    # this information is found in the series_init_filtered directory.
    expected_num = 9
    expected_beg = 'F000'
    expected_end = 'F048'
    siw = series_init_wrapper(metplus_config)
    filtered_out_dir = siw.series_filtered_out_dir
    cur_init = '20141214_00'
    cur_storm = 'ML1200942014'

    num,beg,end = siw.get_fcst_file_info(filtered_out_dir, cur_init, cur_storm)
    siw.get_fcst_file_info(filtered_out_dir, cur_init, cur_storm)
    assert num == expected_num
    assert beg == expected_beg
    assert end == expected_end


def test_storms_for_init_OK(metplus_config):
    """Verify that the expected number of storms
       are found for the init time 20141214_00
    """
    config = metplus_config()

    expected_storm_list = ['ML1201072014',
                           'ML1221072014',
                           'ML1241072014',
                           'ML1251072014'
                           ]
    time_info = {'init': datetime.datetime(2014, 12, 14, 00)}
    stat_input_dir = (
        os.path.join(config.getdir('METPLUS_BASE'),
                     'internal_tests',
                     'data',
                     'stat_data')
    )
    stat_input_template = 'fake_filter_{init?fmt=%Y%m%d_%H}.tcst'

    siw = series_init_wrapper(metplus_config)
    siw.c_dict['STAT_INPUT_DIR'] = stat_input_dir
    siw.c_dict['STAT_INPUT_TEMPLATE'] = stat_input_template

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