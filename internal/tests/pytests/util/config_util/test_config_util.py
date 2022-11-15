#!/usr/bin/env python3

import pytest

import pprint
import os
from datetime import datetime

from metplus.util.config_util import *
from metplus.util.time_util import ti_calculate


@pytest.mark.parametrize(
    'conf_items, met_tool, expected_result', [
        ({'CUSTOM_LOOP_LIST': "one, two, three"}, '', ['one', 'two', 'three']),
        ({'CUSTOM_LOOP_LIST': "one, two, three",
          'GRID_STAT_CUSTOM_LOOP_LIST': "four, five",}, 'grid_stat', ['four', 'five']),
        ({'CUSTOM_LOOP_LIST': "one, two, three",
          'GRID_STAT_CUSTOM_LOOP_LIST': "four, five",}, 'point_stat', ['one', 'two', 'three']),
        ({'CUSTOM_LOOP_LIST': "one, two, three",
          'ASCII2NC_CUSTOM_LOOP_LIST': "four, five",}, 'ascii2nc', ['four', 'five']),
        # fails to read custom loop list for point2grid because there are underscores in name
        ({'CUSTOM_LOOP_LIST': "one, two, three",
          'POINT_2_GRID_CUSTOM_LOOP_LIST': "four, five",}, 'point2grid', ['one', 'two', 'three']),
        ({'CUSTOM_LOOP_LIST': "one, two, three",
          'POINT2GRID_CUSTOM_LOOP_LIST': "four, five",}, 'point2grid', ['four', 'five']),
    ]
)
@pytest.mark.util
def test_get_custom_string_list(metplus_config, conf_items, met_tool, expected_result):
    config = metplus_config
    for conf_key, conf_value in conf_items.items():
        config.set('config', conf_key, conf_value)

    assert get_custom_string_list(config, met_tool) == expected_result


@pytest.mark.parametrize(
    'input_list, expected_list', [
        ('Point2Grid', ['Point2Grid']),
        # MET documentation syntax (with dashes)
        ('Pcp-Combine, Grid-Stat, Ensemble-Stat', ['PCPCombine',
                                                   'GridStat',
                                                   'EnsembleStat']),
        ('Point-Stat', ['PointStat']),
        ('Mode, MODE Time Domain', ['MODE',
                                    'MTD']),
        # actual tool name (lower case underscore)
        ('point_stat, grid_stat, ensemble_stat', ['PointStat',
                                                  'GridStat',
                                                  'EnsembleStat']),
        ('mode, mtd', ['MODE',
                       'MTD']),
        ('ascii2nc, pb2nc, regrid_data_plane', ['ASCII2NC',
                                                'PB2NC',
                                                'RegridDataPlane']),
        ('pcp_combine, tc_pairs, tc_stat', ['PCPCombine',
                                            'TCPairs',
                                            'TCStat']),
        ('gen_vx_mask, stat_analysis, series_analysis', ['GenVxMask',
                                                         'StatAnalysis',
                                                         'SeriesAnalysis']),
        # old capitalization format
        ('PcpCombine, Ascii2Nc, TcStat, TcPairs', ['PCPCombine',
                                                   'ASCII2NC',
                                                   'TCStat',
                                                   'TCPairs']),
    ]
)
@pytest.mark.util
def test_get_process_list(metplus_config, input_list, expected_list):
    conf = metplus_config
    conf.set('config', 'PROCESS_LIST', input_list)
    process_list = get_process_list(conf)
    output_list = [item[0] for item in process_list]
    assert output_list == expected_list


@pytest.mark.parametrize(
    'input_list, expected_list', [
        # no instances
        ('Point2Grid', [('Point2Grid', None)]),
        # one with instance one without
        ('PcpCombine, GridStat(my_instance)', [('PCPCombine', None),
                                               ('GridStat', 'my_instance')]),
        # duplicate process, one with instance one without
        ('TCStat, ExtractTiles, TCStat(for_series), SeriesAnalysis', (
                [('TCStat',None),
                 ('ExtractTiles',None),
                 ('TCStat', 'for_series'),
                 ('SeriesAnalysis',None),])),
        # two processes, both with instances
        ('mode(uno), mtd(dos)', [('MODE', 'uno'),
                                 ('MTD', 'dos')]),
        # lower-case names, first with instance, second without
        ('ascii2nc(some_name), pb2nc', [('ASCII2NC', 'some_name'),
                                        ('PB2NC', None)]),
        # duplicate process, both with different instances
        ('tc_stat(one), tc_pairs, tc_stat(two)', [('TCStat', 'one'),
                                                  ('TCPairs', None),
                                                  ('TCStat', 'two')]),
    ]
)
@pytest.mark.util
def test_get_process_list_instances(metplus_config, input_list, expected_list):
    conf = metplus_config
    conf.set('config', 'PROCESS_LIST', input_list)
    output_list = get_process_list(conf)
    assert output_list == expected_list
