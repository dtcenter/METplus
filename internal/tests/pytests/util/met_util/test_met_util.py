#!/usr/bin/env python3

import pytest

import datetime
import os
from dateutil.relativedelta import relativedelta
import pprint

from metplus.util import met_util as util
from metplus.util import time_util
from metplus.util.config_metplus import parse_var_list


@pytest.mark.parametrize(
    'key, value', [
        ({"gt2.3", "gt5.5"}, True),
        ({"ge2.3", "ge5.5"}, True),
        ({"eq2.3"}, True),
        ({"ne2.3"}, True),
        ({"lt2.3", "lt1.1"}, True),
        ({"le2.3", "le1.1"}, True),
        ({">2.3", ">5.5"}, True),
        ({">=2.3", ">=5.5"}, True),
        ({"==2.3"}, True),
        ({"!=.3"}, True),
        ({"<2.3", "<1."}, True),
        ({"<=2.3", "<=1.1"}, True),
        ({"gta"}, False),
        ({"gt"}, False),
        ({">=a"}, False),
        ({"2.3"}, False),
        ({"<=2.3", "2.4", "gt2.7"}, False),
        ({"<=2.3||>=4.2", "gt2.3&&lt4.2"}, True),
        ({"gt2.3&&lt4.2a"}, True),
        ({"gt2sd.3&&lt4.2"}, True),
        ({"gt2.3&a&lt4.2"}, True), # invalid but is accepted
        ({'gt4&&lt5&&ne4.5'}, True),
        ({"<2.3", "ge5", ">SPF90"}, True),
        (["NA"], True),
        (["<USP90(2.5)"], True),
        ([""], False),
        ([">SFP70", ">SFP80", ">SFP90", ">SFP95"], True),
        ([">SFP70", ">SFP80", ">SFP90", ">SFP95"], True),
    ]
)
@pytest.mark.util
def test_threshold(key, value):
    assert util.validate_thresholds(key) == value


# parses a threshold and returns a list of tuples of
# comparison and number, i.e.:
# 'gt4' => [('gt', 4)]
# gt4&&lt5 => [('gt', 4), ('lt', 5)]
@pytest.mark.parametrize(
    'key, value', [
        ('gt4', [('gt', 4)]),
        ('gt4&&lt5', [('gt', 4), ('lt', 5)]),
        ('gt4&&lt5&&ne4.5', [('gt', 4), ('lt', 5), ('ne', 4.5)]),
        (">4.545", [('>', 4.545)]),
        (">=4.0", [('>=', 4.0)]),
        ("<4.5", [('<', 4.5)]),
        ("<=4.5", [('<=', 4.5)]),
        ("!=4.5", [('!=', 4.5)]),
        ("==4.5", [('==', 4.5)]),
        ("gt4.5", [('gt', 4.5)]),
        ("ge4.5", [('ge', 4.5)]),
        ("lt4.5", [('lt', 4.5)]),
        ("le4.5", [('le', 4.5)]),
        ("ne10.5", [('ne', 10.5)]),
        ("eq4.5", [('eq', 4.5)]),
        ("eq-4.5", [('eq', -4.5)]),
        ("eq+4.5", [('eq', 4.5)]),
        ("eq.5", [('eq', 0.5)]),
        ("eq5.", [('eq', 5)]),
        ("eq5.||ne0.0", [('eq', 5), ('ne', 0.0)]),
        (">SFP90", [('>', 'SFP90')]),
        ("SFP90", None),
        ("gtSFP90", [('gt', 'SFP90')]),
        ("goSFP90", None),
        ("NA", [('NA', '')]),
        ("<USP90(2.5)", [('<', 'USP90(2.5)')]),
    ]
)
@pytest.mark.util
def test_get_threshold_via_regex(key, value):
    assert util.get_threshold_via_regex(key) == value


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

    outpath = util.preprocess_file(filepath, None, conf)
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
    result = util.preprocess_file(filename, data_type, config, allow_dir)
    assert result == expected


def test_get_lead_sequence_lead(metplus_config):
    input_dict = {'valid': datetime.datetime(2019, 2, 1, 13)}
    conf = metplus_config
    conf.set('config', 'LEAD_SEQ', "3,6,9,12")
    test_seq = util.get_lead_sequence(conf, input_dict)
    hour_seq = []
    for test in test_seq:
        hour_seq.append(time_util.ti_get_hours_from_relativedelta(test))
    lead_seq = [3, 6, 9, 12]
    assert hour_seq == lead_seq


@pytest.mark.parametrize(
    'key, value', [
        ('begin_end_incr(3,12,3)',  [ 3, 6, 9, 12]),
        ('begin_end_incr( 3,12 , 3)',  [ 3, 6, 9, 12]),
        ('begin_end_incr(0,10,2)',  [ 0, 2, 4, 6, 8, 10]),
        ('begin_end_incr(10,0,-2)',  [ 10, 8, 6, 4, 2, 0]),
        ('begin_end_incr(2,2,20)',  [ 2 ]),
        ('begin_end_incr(72,72,6)',  [ 72 ]),
        ('begin_end_incr(0,12,1), begin_end_incr(15,60,3)', [0,1,2,3,4,5,6,7,8,9,10,11,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60]),
        ('begin_end_incr(0,10,2), 12',  [ 0, 2, 4, 6, 8, 10, 12]),
        ('begin_end_incr(0,10,2)H, 12',  [ 0, 2, 4, 6, 8, 10, 12]),
        ('begin_end_incr(0,10800,3600)S, 4H',  [ 0, 1, 2, 3, 4]),
    ]
)
@pytest.mark.util
def test_get_lead_sequence_lead_list(metplus_config, key, value):
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 13) }
    conf = metplus_config
    conf.set('config', 'LEAD_SEQ', key)
    test_seq = util.get_lead_sequence(conf, input_dict)
    hour_seq = []

    for test in test_seq:
        hour_seq.append(time_util.ti_get_hours_from_relativedelta(test))
    lead_seq = value
    assert hour_seq == lead_seq


@pytest.mark.parametrize(
    'config_dict, expected_list', [
        # 1 group
        ({'LEAD_SEQ_1': "0, 1, 2, 3",
          'LEAD_SEQ_1_LABEL': 'Day1',
          },  [0, 1, 2, 3]),
        # 2 groups, no overlap
        ({'LEAD_SEQ_1': "0, 1, 2, 3",
          'LEAD_SEQ_1_LABEL': 'Day1',
          'LEAD_SEQ_2': "8, 9, 10, 11",
          'LEAD_SEQ_2_LABEL': 'Day2',
          },  [0, 1, 2, 3, 8, 9, 10, 11]),
        # 2 groups, overlap
        ({'LEAD_SEQ_1': "0, 1, 2, 3",
          'LEAD_SEQ_1_LABEL': 'Day1',
          'LEAD_SEQ_2': "3, 4, 5, 6",
          'LEAD_SEQ_2_LABEL': 'Day2',
          }, [0, 1, 2, 3, 4, 5, 6]),
        # 2 groups, no overlap, out of order
        ({'LEAD_SEQ_1': "8, 9, 10, 11",
          'LEAD_SEQ_1_LABEL': 'Day2',
          'LEAD_SEQ_2': "0, 1, 2, 3",
          'LEAD_SEQ_2_LABEL': 'Day1',
          },  [8, 9, 10, 11, 0, 1, 2, 3]),
        # 2 groups, overlap, out of order
        ({'LEAD_SEQ_1': "3, 4, 5, 6",
          'LEAD_SEQ_1_LABEL': 'Day2',
          'LEAD_SEQ_2': "0, 1, 2, 3",
          'LEAD_SEQ_2_LABEL': 'Day1',
          }, [3, 4, 5, 6, 0, 1, 2]),
    ]
)
@pytest.mark.util
def test_get_lead_sequence_groups(metplus_config, config_dict, expected_list):
    config = metplus_config
    for key, value in config_dict.items():
        config.set('config', key, value)

    output_list = util.get_lead_sequence(config)
    hour_seq = []

    for output in output_list:
        hour_seq.append(
            time_util.ti_get_hours_from_relativedelta(output)
        )

    assert hour_seq == expected_list


@pytest.mark.parametrize(
    'current_hour, lead_seq', [
        (0,  [0, 12, 24, 36]),
        (1,  [1, 13, 25]),
        (2,  [2, 14, 26]),
        (3,  [3, 15, 27]),
        (4,  [4, 16, 28]),
        (5,  [5, 17, 29]),
        (6,  [6, 18, 30]),
        (7,  [7, 19, 31]),
        (8,  [8, 20, 32]),
        (9,  [9, 21, 33]),
        (10, [10, 22, 34]),
        (11, [11, 23, 35]),
        (12, [0, 12, 24, 36]),
        (13, [1, 13, 25]),
        (14, [2, 14, 26]),
        (15, [3, 15, 27]),
        (16, [4, 16, 28]),
        (17, [5, 17, 29]),
        (18, [6, 18, 30]),
        (19, [7, 19, 31]),
        (20, [8, 20, 32]),
        (21, [9, 21, 33]),
        (22, [10, 22, 34]),
        (23, [11, 23, 35])
    ]
)
@pytest.mark.util
def test_get_lead_sequence_init(metplus_config, current_hour, lead_seq):
    input_dict = {'valid': datetime.datetime(2019, 2, 1, current_hour)}
    conf = metplus_config
    conf.set('config', 'INIT_SEQ', "0, 12")
    conf.set('config', 'LEAD_SEQ_MAX', 36)
    test_seq = util.get_lead_sequence(conf, input_dict)
    assert test_seq == [relativedelta(hours=lead) for lead in lead_seq]


@pytest.mark.util
def test_get_lead_sequence_init_min_10(metplus_config):
    input_dict = {'valid': datetime.datetime(2019, 2, 1, 12)}
    conf = metplus_config
    conf.set('config', 'INIT_SEQ', "0, 12")
    conf.set('config', 'LEAD_SEQ_MAX', 24)
    conf.set('config', 'LEAD_SEQ_MIN', 10)
    test_seq = util.get_lead_sequence(conf, input_dict)
    lead_seq = [12, 24]
    assert test_seq == [relativedelta(hours=lead) for lead in lead_seq]


@pytest.mark.parametrize(
    'camel, underscore', [
        ('ASCII2NCWrapper', 'ascii2nc_wrapper'),
        ('CyclonePlotterWrapper', 'cyclone_plotter_wrapper'),
        ('EnsembleStatWrapper', 'ensemble_stat_wrapper'),
        ('ExampleWrapper', 'example_wrapper'),
        ('ExtractTilesWrapper', 'extract_tiles_wrapper'),
        ('GempakToCFWrapper', 'gempak_to_cf_wrapper'),
        ('GenVxMaskWrapper', 'gen_vx_mask_wrapper'),
        ('GridStatWrapper', 'grid_stat_wrapper'),
        ('MODEWrapper', 'mode_wrapper'),
        ('MTDWrapper', 'mtd_wrapper'),
        ('PB2NCWrapper', 'pb2nc_wrapper'),
        ('PCPCombineWrapper', 'pcp_combine_wrapper'),
        ('Point2GridWrapper', 'point2grid_wrapper'),
        ('PointStatWrapper', 'point_stat_wrapper'),
        ('PyEmbedWrapper', 'py_embed_wrapper'),
        ('RegridDataPlaneWrapper', 'regrid_data_plane_wrapper'),
        ('SeriesAnalysisWrapper', 'series_analysis_wrapper'),
        ('StatAnalysisWrapper', 'stat_analysis_wrapper'),
        ('TCMPRPlotterWrapper', 'tcmpr_plotter_wrapper'),
        ('TCPairsWrapper', 'tc_pairs_wrapper'),
        ('TCStatWrapper', 'tc_stat_wrapper'),
    ]
)
@pytest.mark.util
def test_camel_to_underscore(camel, underscore):
    assert util.camel_to_underscore(camel) == underscore


@pytest.mark.parametrize(
    'value, expected_result', [
        (3.3, 3.5),
        (3.1, 3.0),
        (-3.2, -3.0),
        (-3.8, -4.0),
    ]
)
@pytest.mark.util
def test_round_0p5(value, expected_result):
    assert util.round_0p5(value) == expected_result


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert util.get_skip_times(conf) == expected_dict


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times_wrapper(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config

    # set wrapper specific skip times, then ensure it is found
    conf.set('config', 'GRID_STAT_SKIP_TIMES', skip_times_conf)

    assert util.get_skip_times(conf, 'grid_stat') == expected_dict


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times_wrapper_not_used(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config

    # set generic SKIP_TIMES, then request grid_stat to ensure it uses generic
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert util.get_skip_times(conf, 'grid_stat') == expected_dict


@pytest.mark.parametrize(
    'run_time, skip_times, expected_result', [
        (datetime.datetime(2019, 12, 30), {'%d': ['30', '31']}, True),
        (datetime.datetime(2019, 12, 30), {'%d': ['29', '31']}, False),
        (datetime.datetime(2019, 2, 27), {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, False),
        (datetime.datetime(2019, 3, 30), {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime.datetime(2019, 3, 30), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime.datetime(2019, 3, 29), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime.datetime(2019, 1, 29), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, False),
        (datetime.datetime(2020, 10, 31), {'%Y%m%d': ['20201031']}, True),
        (datetime.datetime(2020, 3, 31), {'%Y%m%d': ['20201031']}, False),
        (datetime.datetime(2020, 10, 30), {'%Y%m%d': ['20201031']}, False),
        (datetime.datetime(2019, 10, 31), {'%Y%m%d': ['20201031']}, False),
        (datetime.datetime(2020, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime.datetime(2019, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime.datetime(2019, 1, 13), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime.datetime(2018, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, False),
        (datetime.datetime(2019, 12, 30, 12), {'%H': ['12', '18']}, True),
        (datetime.datetime(2019, 12, 30, 13), {'%H': ['12', '18']}, False),
    ]
)
@pytest.mark.util
def test_get_skip_time(run_time, skip_times, expected_result):
    time_info = time_util.ti_calculate({'valid': run_time})
    assert util.skip_time(time_info, skip_times) == expected_result


@pytest.mark.util
def test_get_skip_time_no_valid():
    input_dict ={'init': datetime.datetime(2019, 1, 29)}
    assert util.skip_time(input_dict, {'%Y': ['2019']}) == False


@pytest.mark.parametrize(
    'int_string, expected_result', [
        ('4', [4]),
        ('4-12', [4, 5, 6, 7, 8, 9, 10, 11, 12]),
        ('5,18-24,29', [5, 18, 19, 20, 21, 22, 23, 24, 29]),
        ('7,8,9,13', [7, 8, 9, 13]),
        ('4+', [4, '+']),
        ('4-12+', [4, 5, 6, 7, 8, 9, 10, 11, 12, '+']),
        ('5,18-24,29+', [5, 18, 19, 20, 21, 22, 23, 24, 29, '+']),
        ('7,8,9,13+', [7, 8, 9, 13, '+']),
    ]
)
@pytest.mark.util
def test_expand_int_string_to_list(int_string, expected_result):
    result = util.expand_int_string_to_list(int_string)
    assert result == expected_result


@pytest.mark.parametrize(
    'subset_definition, expected_result', [
        ([1, 3, 5], ['b', 'd', 'f']),
        ([1, 3, 5, '+'], ['b', 'd', 'f', 'g', 'h', 'i', 'j']),
        ([1], ['b']),
        (1, ['b']),
        ([3, '+'], ['d', 'e', 'f', 'g', 'h', 'i', 'j']),
        (None, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']),
        (slice(1,4,1), ['b', 'c', 'd']),
        (slice(2,9,2), ['c', 'e', 'g', 'i']),
    ]
)
@pytest.mark.util
def test_subset_list(subset_definition, expected_result):
    full_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    result = util.subset_list(full_list, subset_definition)
    assert result == expected_result


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

    assert util.get_storms(filepath, id_only=True) == expected_result


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

    storm_dict = util.get_storms(filepath)
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

    storm_dict = util.get_storms(filepath, sort_column=sort_column)
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
    'config_value, expected_result', [
        # 2 items semi-colon at end
        ('GRIB_lvl_typ = 234;  desc = "HI_CLOUD";',
         'GRIB_lvl_typ = 234; desc = "HI_CLOUD";'),
        # 2 items no semi-colon at end
        ('GRIB_lvl_typ = 234;  desc = "HI_CLOUD"',
         'GRIB_lvl_typ = 234; desc = "HI_CLOUD";'),
        # 1 item semi-colon at end
        ('GRIB_lvl_typ = 234;',
         'GRIB_lvl_typ = 234;'),
        # 1 item no semi-colon at end
        ('GRIB_lvl_typ = 234',
         'GRIB_lvl_typ = 234;'),
    ]
)
@pytest.mark.util
def test_format_var_items_options_semicolon(config_value,
                                            expected_result):
    time_info = {}

    field_configs = {'name': 'FNAME',
                     'levels': 'FLEVEL',
                     'options': config_value}

    var_items = util.format_var_items(field_configs, time_info)
    result = var_items.get('extra')
    assert result == expected_result


@pytest.mark.parametrize(
    'level, expected_result', [
        ('level', 'level'),
        ('P500', 'P500'),
        ('*,*', 'all_all'),
        ('1,*,*', '1_all_all'),
    ]
)
@pytest.mark.util
def test_format_level(level, expected_result):
    assert util.format_level(level) == expected_result


@pytest.mark.parametrize(
    'input_dict, expected_list', [
        ({'init': datetime.datetime(2019, 2, 1, 6),
          'lead': 7200, },
         [
             {'index': '1',
              'fcst_name': 'FNAME_2019',
              'fcst_level': 'Z06',
              'obs_name': 'ONAME_2019',
              'obs_level': 'L06',
             },
             {'index': '1',
              'fcst_name': 'FNAME_2019',
              'fcst_level': 'Z08',
              'obs_name': 'ONAME_2019',
              'obs_level': 'L08',
             },
         ]),
        ({'init': datetime.datetime(2021, 4, 13, 9),
          'lead': 10800, },
         [
             {'index': '1',
              'fcst_name': 'FNAME_2021',
              'fcst_level': 'Z09',
              'obs_name': 'ONAME_2021',
              'obs_level': 'L09',
              },
             {'index': '1',
              'fcst_name': 'FNAME_2021',
              'fcst_level': 'Z12',
              'obs_name': 'ONAME_2021',
              'obs_level': 'L12',
              },
         ]),
    ]
)
@pytest.mark.util
def test_sub_var_list(metplus_config, input_dict, expected_list):
    config = metplus_config
    config.set('config', 'FCST_VAR1_NAME', 'FNAME_{init?fmt=%Y}')
    config.set('config', 'FCST_VAR1_LEVELS', 'Z{init?fmt=%H}, Z{valid?fmt=%H}')
    config.set('config', 'OBS_VAR1_NAME', 'ONAME_{init?fmt=%Y}')
    config.set('config', 'OBS_VAR1_LEVELS', 'L{init?fmt=%H}, L{valid?fmt=%H}')

    time_info = time_util.ti_calculate(input_dict)

    actual_temp = parse_var_list(config)

    pp = pprint.PrettyPrinter()
    print(f'Actual var list (before sub):')
    pp.pprint(actual_temp)

    actual_list = util.sub_var_list(actual_temp, time_info)
    print(f'Actual var list (after sub):')
    pp.pprint(actual_list)

    assert len(actual_list) == len(expected_list)
    for actual, expected in zip(actual_list, expected_list):
        for key, value in expected.items():
            assert actual.get(key) == value
