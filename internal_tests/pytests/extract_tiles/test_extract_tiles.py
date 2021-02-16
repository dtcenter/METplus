# !/usr/bin/env python3

import sys
import os
import datetime
import logging
import re
import pytest

import produtil

from metplus.wrappers.extract_tiles_wrapper import ExtractTilesWrapper

def get_config(metplus_config):
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__),
                                      'extract_tiles_test.conf'))
    return metplus_config(extra_configs)

def extract_tiles_wrapper(metplus_config):
    config = get_config(metplus_config)

    config.set('config', 'LOOP_ORDER', 'processes')
    etw = ExtractTilesWrapper(config)
    return etw

def get_storm_lines(etw):
    filter_file = os.path.join(etw.config.getdir('METPLUS_BASE'),
                            'internal_tests',
                            'data',
                            'stat_data',
                            'fake_filter_20141214_00.tcst')
    with open(filter_file, 'r') as file_handle:
        lines = file_handle.readlines()

    return lines

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
def test_get_header_indices(metplus_config,header_name, index):
    etw = extract_tiles_wrapper(metplus_config)
    header = get_storm_lines(etw)[0]
    idx_dict = etw.get_header_indices(header)
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
def test_get_storm_data_from_track(metplus_config, header_name, value):
    etw = extract_tiles_wrapper(metplus_config)
    storm_lines = get_storm_lines(etw)
    header = storm_lines[0]
    idx_dict = etw.get_header_indices(header)
    storm_data = etw.get_storm_data_from_track_line(idx_dict, storm_lines[2])
    assert(storm_data[header_name] == value)

def test_set_time_info_from_storm_data(metplus_config):
    storm_id = 'ML1221072014'
    etw = extract_tiles_wrapper(metplus_config)
    storm_lines = get_storm_lines(etw)
    header = storm_lines[0]
    idx_dict = etw.get_header_indices(header)
    storm_data = etw.get_storm_data_from_track_line(idx_dict, storm_lines[2])
    time_info = etw.set_time_info_from_storm_data(storm_id, storm_data)

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
def test_get_grid_info(metplus_config, lat, lon, expected_result):
    etw = extract_tiles_wrapper(metplus_config)
    assert(etw.get_grid_info(lat, lon, 'FCST') == expected_result)

@pytest.mark.parametrize(
        'lat, lon, expected_result', [
        (-54.9, -168.6, 'latlon 60 60 -70.0 -183.5 0.5 0.5'),

    ]
)
def test_get_grid(metplus_config, lat, lon, expected_result):
    etw = extract_tiles_wrapper(metplus_config)
    storm_data = {'ALAT': lat, 'ALON': lon}
    assert(etw.get_grid('FCST', storm_data) == expected_result)
