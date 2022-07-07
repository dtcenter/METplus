# !/usr/bin/env python3

import pytest

import os
import datetime

from metplus.wrappers.extract_tiles_wrapper import ExtractTilesWrapper


def get_config(metplus_config):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'extract_tiles_test.conf'))
    return metplus_config(extra_configs)


def extract_tiles_wrapper(metplus_config):
    config = get_config(metplus_config)

    config.set('config', 'LOOP_ORDER', 'processes')
    wrapper = ExtractTilesWrapper(config)
    return wrapper


def get_storm_lines(wrapper):
    filter_file = os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                            'internal_tests',
                            'data',
                            'stat_data',
                            'fake_filter_20141214_00.tcst')
    return get_input_lines(filter_file)


def get_mtd_lines(wrapper):
    input_file = os.path.join(wrapper.config.getdir('METPLUS_BASE'),
                              'internal_tests',
                              'data',
                              'mtd',
                              'fake_mtd_2d.txt')
    return get_input_lines(input_file)


def get_input_lines(filepath):
    with open(filepath, 'r') as file_handle:
        lines = file_handle.readlines()
    return lines


@pytest.mark.parametrize(
    'object_cats, expected_indices', [
        # 0: No object cats provided
        ([], None),
        # 1: 1 object (zero)
        (['CF000', 'CO000'], None),
        # 2: 1 object cat (non-zero)
        (['CF001', 'CO001'], ['001']),
        # 3: 2 object cat (out of order)
        (['CF002', 'CF001', 'CO002', 'CO001'], ['001', '002']),
    ]
)
@pytest.mark.wrapper
def test_get_object_indices(metplus_config, object_cats, expected_indices):
    wrapper = extract_tiles_wrapper(metplus_config)
    assert wrapper.get_object_indices(object_cats) == expected_indices


@pytest.mark.parametrize(
        'header_name, index', [
        ('VALID', 10),
        ('INIT', 8),
        ('LEAD', 9),
        ('ALAT', 19),
        ('ALON', 20),
        ('BLAT', 21),
        ('BLON', 22),
        ('AMODEL', 1),

    ]
)
@pytest.mark.wrapper
def test_get_header_indices(metplus_config,header_name, index):
    wrapper = extract_tiles_wrapper(metplus_config)
    header = get_storm_lines(wrapper)[0]
    idx_dict = wrapper.get_header_indices(header)
    assert(idx_dict[header_name] == index)


@pytest.mark.parametrize(
    'header_name, index', [
        ('CENTROID_LAT', 28),
        ('CENTROID_LON', 29),
        ('FCST_LEAD', 3),
        ('FCST_VALID', 4),
        ('MODEL', 1),
        ('OBJECT_CAT', 23),
        ('OBJECT_ID', 22),
    ]
)
@pytest.mark.wrapper
def test_get_header_indices_mtd(metplus_config, header_name, index):
    wrapper = extract_tiles_wrapper(metplus_config)
    header = get_mtd_lines(wrapper)[0]
    idx_dict = wrapper.get_header_indices(header, 'MTD')
    assert(idx_dict[header_name] == index)


@pytest.mark.parametrize(
        'header_name, value', [
        ('VALID', '20141214_060000'),
        ('INIT', '20141214_000000'),
        ('LEAD', '060000'),
        ('ALAT', '-52.3'),
        ('ALON', '130.8'),
        ('BLAT', '-52.2'),
        ('BLON', '131'),
        ('AMODEL', 'GFSO'),

    ]
)
@pytest.mark.wrapper
def test_get_data_from_track_line(metplus_config, header_name, value):
    wrapper = extract_tiles_wrapper(metplus_config)
    storm_lines = get_storm_lines(wrapper)
    header = storm_lines[0]
    idx_dict = wrapper.get_header_indices(header)
    storm_data = wrapper.get_data_from_track_line(idx_dict, storm_lines[2])
    assert(storm_data[header_name] == value)


@pytest.mark.parametrize(
    'header_name, value', [
        ('CENTROID_LAT', '37.26'),
        ('CENTROID_LON', '-61.49'),
        ('FCST_LEAD', '090000'),
        ('FCST_VALID', '20050807_090000'),
        ('MODEL', 'WRF'),
        ('OBJECT_CAT', 'CF001'),
        ('OBJECT_ID', 'F001'),
    ]
)
@pytest.mark.wrapper
def test_get_data_from_track_line_mtd(metplus_config, header_name, value):
    wrapper = extract_tiles_wrapper(metplus_config)
    storm_lines = get_mtd_lines(wrapper)
    header = storm_lines[0]
    idx_dict = wrapper.get_header_indices(header, 'MTD')
    storm_data = wrapper.get_data_from_track_line(idx_dict, storm_lines[2])
    assert(storm_data[header_name] == value)


@pytest.mark.wrapper
def test_set_time_info_from_track_data(metplus_config):
    storm_id = 'ML1221072014'
    wrapper = extract_tiles_wrapper(metplus_config)
    storm_lines = get_storm_lines(wrapper)
    header = storm_lines[0]
    idx_dict = wrapper.get_header_indices(header)
    storm_data = wrapper.get_data_from_track_line(idx_dict, storm_lines[2])
    time_info = wrapper.set_time_info_from_track_data(storm_data, storm_id)

    expected_time_info = {'init': datetime.datetime(2014, 12, 14, 0),
                          'valid': datetime.datetime(2014, 12, 14, 6),
                          'amodel': 'GFSO',
                          'storm_id': storm_id}
    for key, value in expected_time_info.items():
        assert(time_info[key] == value)


@pytest.mark.parametrize(
    'lat, lon, expected_result', [
        (-54.9, -168.6, 'latlon 60 60 -70.0 -183.5 0.5 0.5'),

    ]
)
@pytest.mark.wrapper
def test_get_grid_info(metplus_config, lat, lon, expected_result):
    wrapper = extract_tiles_wrapper(metplus_config)
    assert(wrapper.get_grid_info(lat, lon, 'FCST') == expected_result)


@pytest.mark.parametrize(
    'lat, lon, expected_result', [
        (-54.9, -168.6, 'latlon 60 60 -70.0 -183.5 0.5 0.5'),

    ]
)
@pytest.mark.wrapper
def test_get_grid(metplus_config, lat, lon, expected_result):
    wrapper = extract_tiles_wrapper(metplus_config)
    storm_data = {'ALAT': lat, 'ALON': lon}
    assert(wrapper.get_grid('FCST', storm_data) == expected_result)
