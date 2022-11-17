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


@pytest.mark.parametrize(
    'filename, ext', [
        ('internal/tests/data/zip/testfile.txt', '.gz'),
        ('internal/tests/data/zip/testfile2.txt', '.bz2'),
        ('internal/tests/data/zip/testfile3.txt', '.zip'),
        ('internal/tests/data/zip/testfile4.txt', ''),
    ]
)
@pytest.mark.util
def test_preprocess_file_stage(metplus_config, filename, ext):
    conf = metplus_config
    metplus_base = conf.getdir('METPLUS_BASE')
    stage_dir = conf.getdir('STAGING_DIR',
                            os.path.join(conf.getdir('OUTPUT_BASE'),
                                         'stage'))
    filepath = os.path.join(metplus_base,
                            filename+ext)
    if ext:
        stagepath = stage_dir + os.path.join(metplus_base,
                                             filename)
        if os.path.exists(stagepath):
            os.remove(stagepath)
    else:
        stagepath = filepath

    outpath = preprocess_file(filepath, None, conf)
    assert stagepath == outpath and os.path.exists(outpath)


@pytest.mark.parametrize(
    'filename, data_type, allow_dir, expected', [
        # filename is None or empty string - return None
        (None, None, False, None),
        ('', None, False, None),
        # python data types - pass through full filename value
        ('some:set:of:words', 'PYTHON_NUMPY', False, 'some:set:of:words'),
        ('some:set:of:words', 'PYTHON_XARRAY', False, 'some:set:of:words'),
        ('some:set:of:words', 'PYTHON_PANDAS', False, 'some:set:of:words'),
        # allow directory - pass through full dir path
        ('dir', None, True, 'dir'),
        # base filename is python embedding type - return python embed type
        ('/some/path/PYTHON_NUMPY', None, False, 'PYTHON_NUMPY'),
        ('/some/path/PYTHON_XARRAY', None, False, 'PYTHON_XARRAY'),
        ('/some/path/PYTHON_PANDAS', None, False, 'PYTHON_PANDAS'),
    ]
)
@pytest.mark.util
def test_preprocess_file_options(metplus_config,
                                 filename,
                                 data_type,
                                 allow_dir,
                                 expected):
    config = metplus_config
    if filename == 'dir':
        filename = config.getdir('METPLUS_BASE')
        expected = filename
    result = preprocess_file(filename, data_type, config, allow_dir)
    assert result == expected
