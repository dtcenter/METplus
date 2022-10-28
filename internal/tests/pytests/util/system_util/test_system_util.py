#!/usr/bin/env python3

import pytest

from metplus.util.system_util import *

@pytest.mark.parametrize(
    'filename, expected_result', [
        # file does not exist
        ('filedoesnotexist.tcst', []),
        # file is empty
        ('empty_filter.tcst', []),
        # file has STORM_ID column with 4 values
        ('fake_filter_20141214_00.tcst', ['ML1201072014',
                                          'ML1221072014',
                                          'ML1241072014',
                                          'ML1251072014']),
        # file does not have STORM_ID column
        ('test_20190101.stat', []),
    ]
)
@pytest.mark.util
def test_get_storm_ids(metplus_config, filename, expected_result):
    config = metplus_config
    filepath = os.path.join(config.getdir('METPLUS_BASE'),
                            'internal', 'tests',
                            'data',
                            'stat_data',
                            filename)

    assert get_storms(filepath, id_only=True) == expected_result


@pytest.mark.parametrize(
    'filename, expected_result', [
        # file does not exist
        ('filedoesnotexist.tcst', []),
        # file is empty
        ('empty_filter.tcst', []),
        # file has STORM_ID column with 4 values
        ('fake_filter_20141214_00.tcst', ['header',
                                          'ML1201072014',
                                          'ML1221072014',
                                          'ML1241072014',
                                          'ML1251072014']),
        # file does not have STORM_ID column
        ('test_20190101.stat', []),
    ]
)
@pytest.mark.util
def test_get_storms(metplus_config, filename, expected_result):
    storm_id_index = 4
    config = metplus_config
    filepath = os.path.join(config.getdir('METPLUS_BASE'),
                            'internal', 'tests',
                            'data',
                            'stat_data',
                            filename)

    storm_dict = get_storms(filepath)
    print(storm_dict)
    assert list(storm_dict.keys()) == expected_result
    for storm_id in expected_result[1:]:
        for storm_line in storm_dict[storm_id]:
            # ensure storm_id_index matches storm ID
            assert storm_line.split()[storm_id_index] == storm_id

    # ensure header matches expected format
    if storm_dict:
        assert storm_dict['header'].split()[storm_id_index] == 'STORM_ID'


@pytest.mark.util
def test_get_storms_mtd(metplus_config):
    index = 23
    expected_result = [
        'header',
        'CF001',
        'CO001'
    ]
    sort_column = 'OBJECT_CAT'
    config = metplus_config
    filepath = os.path.join(config.getdir('METPLUS_BASE'),
                            'internal', 'tests',
                            'data',
                            'mtd',
                            'fake_mtd_2d.txt')

    storm_dict = get_storms(filepath, sort_column=sort_column)
    print(storm_dict)
    assert list(storm_dict.keys()) == expected_result
    for storm_id in expected_result[1:]:
        for storm_line in storm_dict[storm_id]:
            # ensure index matches storm ID
            assert storm_line.split()[index] == storm_id

    # ensure header matches expected format
    if storm_dict:
        assert storm_dict['header'].split()[index] == sort_column
