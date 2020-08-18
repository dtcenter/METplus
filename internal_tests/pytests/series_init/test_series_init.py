import pytest
import os
import sys
import logging
import produtil

from metplus.wrappers.series_by_init_wrapper import SeriesByInitWrapper


def series_init_wrapper(metplus_config):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'series_init_test.conf'))
    config = metplus_config(extra_configs)
    config.set('config', 'LOOP_ORDER', 'processes')
    return SeriesByInitWrapper(config)

def test_wrapper_ok(metplus_config):
    """ Verify that the expected output directory for the
        series init wrapper is what we expected, based on the
        setting in the custom.conf config file.
    """
    pytest.skip('Hard-coded output directories do not match current setup')

    siw = series_init_wrapper(metplus_config)
    expected_output_dir = "/d1/METplus_test_input/series_init/series_analysis_init"
    assert siw.series_out_dir == expected_output_dir

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
    pytest.skip('Hard-coded output directories do not match current setup')

    init = '20141214_00'
    expected_num_storms = 12
    tile_dir = '/d1/METplus_test_input/series_init/extract_tiles'
    siw = series_init_wrapper(metplus_config)
    storm_list = siw.get_storms_for_init(init, tile_dir)
    assert len(storm_list) == expected_num_storms


