#!/usr/bin/env python3

import os
import pytest
from unittest import mock

import metplus.util.system_util as su

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

    assert su.get_storms(filepath, id_only=True) == expected_result


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

    storm_dict = su.get_storms(filepath)
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

    storm_dict = su.get_storms(filepath, sort_column=sort_column)
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

    outpath = su.preprocess_file(filepath, None, conf)
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
        # python embedding command
        ('/some/path/pyscript.py /some/path/input_file', 'PYTHON', False, '"/some/path/pyscript.py /some/path/input_file"'),
        ('/some/path/pyscript.py /some/path/input_file', None, False, '"/some/path/pyscript.py /some/path/input_file"'),
        ('PYTHON_NUMPY=scripts/python/examples/read_ascii_point.py data/sample_obs/ascii/sample_ascii_obs.txt', None, False, '"PYTHON_NUMPY=scripts/python/examples/read_ascii_point.py data/sample_obs/ascii/sample_ascii_obs.txt"'),
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
    result = su.preprocess_file(filename, data_type, config, allow_dir)
    assert result == expected


@pytest.mark.parametrize(
    'input_exists,expected', [
        (False, '/some/fake/file.bigfoot'),
        (True, None)
    ]
)
@pytest.mark.util
def test_preprocess_file_not_exist(metplus_config, input_exists, expected):
    config = metplus_config
    config.set('config', 'INPUT_MUST_EXIST', input_exists)
    result = su.preprocess_file('/some/fake/file.bigfoot', None, config)
    assert result == expected


@pytest.mark.util
def test_preprocess_file_gempack(tmp_path_factory, metplus_config):
    config = metplus_config
    
    # setup files and paths
    tmp_dir = tmp_path_factory.mktemp('gempak')
    config.set('config', 'STAGING_DIR', '')
    file_path = os.path.join(tmp_dir, 'some_file.grd')
    open(file_path, 'a').close()
    expected = os.path.join(tmp_dir, 'some_file.nc')
    
    # we need to import so as to mock .build()
    from metplus.wrappers import GempakToCFWrapper
    
    with mock.patch.object(GempakToCFWrapper, 'build') as mock_build:
        result = su.preprocess_file(file_path, 'GEMPAK', config)
        mock_build.assert_called_once()

    assert result == expected

        
@pytest.mark.parametrize(
    'expected, user_err, id_err', [
    ('James(007)', None, None),
    ('007', OSError, None),
    ('James', None, AttributeError),
    ('', OSError, AttributeError),
    ]
)
@pytest.mark.util
def test_get_user_info(expected, user_err, id_err):
    with mock.patch.object(su.getpass, 'getuser', return_value='James', side_effect=user_err):
        with mock.patch.object(su.os, 'getuid', return_value='007', side_effect=id_err):
                actual = su.get_user_info()
    assert actual == expected
    

@pytest.mark.util
def test_write_list_to_file(tmp_path_factory):
    filename = tmp_path_factory.mktemp('util') / 'temp.txt'
    output_list =['some', 'file', 'content']
    su.write_list_to_file(filename, output_list)
    
    with open(filename, 'r') as f:
        actual = f.read()
        
    assert actual == '\n'.join(output_list) + '\n'


@pytest.mark.util
def test_prune_empty(tmp_path_factory):
    prune_dir = tmp_path_factory.mktemp('prune')
   
    dir1 = prune_dir / 'empty_file_dir'
    dir2 = prune_dir / 'not_empty_file_dir'
    dir3 = prune_dir / 'empty_dir'
    for d in [dir1, dir2, dir3]:
        os.makedirs(d)
    
    # make two files, one empty one not.
    open(os.path.join(dir1, 'empty.txt'), 'a').close()
    file_with_content = os.path.join(dir2, 'not_empty.txt')
    with open(file_with_content, 'w') as f:
        f.write('Fee fi fo fum.')
    
    su.prune_empty(prune_dir, mock.Mock())
    
    assert not os.path.exists(dir1)
    assert os.path.exists(file_with_content)
    assert not os.path.exists(dir3)


@pytest.mark.parametrize(
    'regex, expected', [
        (r'\d', ['bigfoot/123.txt', 'yeti/234.txt']),
        (r'23', ['yeti/234.txt']),
        (r'[\s\S]+nc4', ['yeti/sasquatch.nc4']),
        ('ha', ['bigfoot/hahaha.nc', 'sasquatch/harry.txt'])
    ]
)
@pytest.mark.util
def test_get_files(tmp_path_factory, regex, expected):
    search_dir = tmp_path_factory.mktemp('get_files')
    
    dirs = {
            'bigfoot':['123.txt', 'hahaha.nc'],
            'yeti': ['234.txt', 'sasquatch.nc4'],
            'sasquatch': ['harry.txt', 'hendersons.nc'],
            }
    
    for k, v in dirs.items():
        tmp_dir = os.path.join(search_dir, k)
        os.makedirs(tmp_dir)
        [open(os.path.join(tmp_dir, f), 'a').close() for f in v]
    
    actual = su.get_files(search_dir, regex)
    assert actual == [os.path.join(search_dir, e) for e in expected]
    