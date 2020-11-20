#!/usr/bin/env python3

import sys
import pytest
import datetime
import os
import subprocess
import shutil
from dateutil.relativedelta import relativedelta
from csv import reader

import produtil

from metplus.util import met_util as util
from metplus.util import time_util

@pytest.mark.parametrize(
    'before, after', [
        ('string', 'string'),
        ('"string"', 'string'),
        ('', ''),
        ('""', ''),
        (None, ''),
    ]
)
def test_remove_quotes(before, after):
    assert(util.remove_quotes(before) == after)

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
def test_threshold(key, value):
    assert(util.validate_thresholds(key) == value)

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
def test_get_threshold_via_regex(key, value):
    assert(util.get_threshold_via_regex(key) == value)

@pytest.mark.parametrize(
    'filename, ext', [
        ('internal_tests/data/zip/testfile.txt', '.gz'),
        ('internal_tests/data/zip/testfile2.txt', '.bz2'),
        ('internal_tests/data/zip/testfile3.txt', '.zip'),
        ('internal_tests/data/zip/testfile4.txt', ''),
    ]
)
def test_preprocess_file_stage(metplus_config, filename, ext):
    conf = metplus_config()
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
    assert(stagepath == outpath and os.path.exists(outpath))

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
def test_preprocess_file_options(metplus_config,
                                 filename,
                                 data_type,
                                 allow_dir,
                                 expected):
    config = metplus_config()
    if filename == 'dir':
        filename = config.getdir('METPLUS_BASE')
        expected = filename
    result = util.preprocess_file(filename, data_type, config, allow_dir)
    assert(result == expected)

def test_getlist():
    l = 'gt2.7, >3.6, eq42'
    test_list = util.getlist(l)
    assert(test_list == ['gt2.7', '>3.6', 'eq42'])

def test_getlist_int():
    l = '6, 7, 42'
    test_list = util.getlistint(l)
    assert(test_list == [6, 7, 42])

def test_getlist_float():
    l = '6.2, 7.8, 42.0'
    test_list = util.getlistfloat(l)
    assert(test_list == [6.2, 7.8, 42.0])

def test_getlist_has_commas():
    l = 'gt2.7, >3.6, eq42, "has,commas,in,it"'
    test_list = util.getlist(l)
    assert(test_list == ['gt2.7', '>3.6', 'eq42', 'has,commas,in,it'])

def test_getlist_empty():
    l = ''
    test_list = util.getlist(l)
    assert(test_list == [])

# field info only defined in the FCST_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, False),
        ('FCST', True),
        ('OBS', False),
    ]
)
def test_parse_var_list_fcst_only(metplus_config, data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "NAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because OBS variables are missing
    if util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    # list will be created if requesting just OBS, but it should not be created if
    # nothing was requested because FCST values are missing
    if list_created:
        assert(var_list[0]['fcst_name'] == "NAME1" and \
               var_list[1]['fcst_name'] == "NAME1" and \
               var_list[2]['fcst_name'] == "NAME2" and \
               var_list[3]['fcst_name'] == "NAME2" and \
               var_list[0]['fcst_level'] == "LEVELS11" and \
               var_list[1]['fcst_level'] == "LEVELS12" and \
               var_list[2]['fcst_level'] == "LEVELS21" and \
               var_list[3]['fcst_level'] == "LEVELS22")
    else:
        assert(not var_list)

# field info only defined in the OBS_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, False),
        ('OBS', True),
        ('FCST', False),
    ]
)
def test_parse_var_list_obs(metplus_config, data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'OBS_VAR1_NAME', "NAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "NAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because FCST variables are missing
    if util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    # list will be created if requesting just OBS, but it should not be created if
    # nothing was requested because FCST values are missing
    if list_created:
        assert(var_list[0]['obs_name'] == "NAME1" and \
               var_list[1]['obs_name'] == "NAME1" and \
               var_list[2]['obs_name'] == "NAME2" and \
               var_list[3]['obs_name'] == "NAME2" and \
               var_list[0]['obs_level'] == "LEVELS11" and \
               var_list[1]['obs_level'] == "LEVELS12" and \
               var_list[2]['obs_level'] == "LEVELS21" and \
               var_list[3]['obs_level'] == "LEVELS22")
    else:
        assert(not var_list)


# field info only defined in the BOTH_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, 'fcst:obs'),
        ('FCST', 'fcst'),
        ('OBS', 'obs'),
    ]
)
def test_parse_var_list_both(metplus_config, data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'BOTH_VAR1_NAME', "NAME1")
    conf.set('config', 'BOTH_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'BOTH_VAR2_NAME', "NAME2")
    conf.set('config', 'BOTH_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because BOTH variables are used
    if not util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    for list_to_check in list_created.split(':'):
        if not var_list[0][f'{list_to_check}_name']  == "NAME1" or \
           not var_list[1][f'{list_to_check}_name']  == "NAME1" or \
           not var_list[2][f'{list_to_check}_name']  == "NAME2" or \
           not var_list[3][f'{list_to_check}_name']  == "NAME2" or \
           not var_list[0][f'{list_to_check}_level'] == "LEVELS11" or \
           not var_list[1][f'{list_to_check}_level'] == "LEVELS12" or \
           not var_list[2][f'{list_to_check}_level'] == "LEVELS21" or \
           not var_list[3][f'{list_to_check}_level'] == "LEVELS22":
           assert(False)

# field info defined in both FCST_* and OBS_* variables
def test_parse_var_list_fcst_and_obs(metplus_config):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "FNAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "FLEVELS11, FLEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "FNAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "FLEVELS21, FLEVELS22")
    conf.set('config', 'OBS_VAR1_NAME', "ONAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "OLEVELS11, OLEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "ONAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "OLEVELS21, OLEVELS22")

    # this should not occur because FCST and OBS variables are found
    if not util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf)

    assert(var_list[0]['fcst_name'] == "FNAME1" and \
           var_list[0]['obs_name'] == "ONAME1" and \
           var_list[1]['fcst_name'] == "FNAME1" and \
           var_list[1]['obs_name'] == "ONAME1" and \
           var_list[2]['fcst_name'] == "FNAME2" and \
           var_list[2]['obs_name'] == "ONAME2" and \
           var_list[3]['fcst_name'] == "FNAME2" and \
           var_list[3]['obs_name'] == "ONAME2" and \
           var_list[0]['fcst_level'] == "FLEVELS11" and \
           var_list[0]['obs_level'] == "OLEVELS11" and \
           var_list[1]['fcst_level'] == "FLEVELS12" and \
           var_list[1]['obs_level'] == "OLEVELS12" and \
           var_list[2]['fcst_level'] == "FLEVELS21" and \
           var_list[2]['obs_level'] == "OLEVELS21" and \
           var_list[3]['fcst_level'] == "FLEVELS22" and \
           var_list[3]['obs_level'] == "OLEVELS22")

# VAR1 defined by FCST, VAR2 defined by OBS
def test_parse_var_list_fcst_and_obs_alternate(metplus_config):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "FNAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "FLEVELS11, FLEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "ONAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "OLEVELS21, OLEVELS22")

    # configuration is invalid and parse var list should not give any results
    assert(not util.validate_configuration_variables(conf, force_check=True)[1] and not util.parse_var_list(conf))

# VAR1 defined by OBS, VAR2 by FCST, VAR3 by both FCST AND OBS
@pytest.mark.parametrize(
    'data_type, list_len, name_levels', [
        (None, 0, None),
        ('FCST', 4, ('FNAME2:FLEVELS21','FNAME2:FLEVELS22','FNAME3:FLEVELS31','FNAME3:FLEVELS32')),
        ('OBS', 4, ('ONAME1:OLEVELS11','ONAME1:OLEVELS12','ONAME3:OLEVELS31','ONAME3:OLEVELS32')),
    ]
)
def test_parse_var_list_fcst_and_obs_and_both(metplus_config, data_type, list_len, name_levels):
    conf = metplus_config()
    conf.set('config', 'OBS_VAR1_NAME', "ONAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "OLEVELS11, OLEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "FNAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "FLEVELS21, FLEVELS22")
    conf.set('config', 'FCST_VAR3_NAME', "FNAME3")
    conf.set('config', 'FCST_VAR3_LEVELS', "FLEVELS31, FLEVELS32")
    conf.set('config', 'OBS_VAR3_NAME', "ONAME3")
    conf.set('config', 'OBS_VAR3_LEVELS', "OLEVELS31, OLEVELS32")

    # configuration is invalid and parse var list should not give any results
    if util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    if len(var_list) != list_len:
        assert(False)

    if data_type is None:
        assert(len(var_list) == 0)

    if name_levels is not None:
        dt_lower = data_type.lower()
        expected = []
        for name_level in name_levels:
            name, level = name_level.split(':')
            expected.append({f'{dt_lower}_name': name,
                             f'{dt_lower}_level': level})

        for expect, reality in zip(expected,var_list):
            if expect[f'{dt_lower}_name'] != reality[f'{dt_lower}_name']:
                assert(False)

            if expect[f'{dt_lower}_level'] != reality[f'{dt_lower}_level']:
                assert(False)

        assert(True)

# option defined in obs only
@pytest.mark.parametrize(
    'data_type, list_len', [
        (None, 0),
        ('FCST', 2),
        ('OBS', 0),
    ]
)
def test_parse_var_list_fcst_only_options(metplus_config, data_type, list_len):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR1_THRESH', ">1, >2")
    conf.set('config', 'OBS_VAR1_OPTIONS', "OOPTIONS11")

    # this should not occur because OBS variables are missing
    if util.validate_configuration_variables(conf, force_check=True)[1]:
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    assert(len(var_list) == list_len)

@pytest.mark.parametrize(
    'met_tool, indices', [
        (None, {'1':['FCST']}),
        ('GRID_STAT', {'2':['FCST']}),
        ('ENSEMBLE_STAT', {}),
    ]
)
def test_find_var_indices_wrapper_specific(metplus_config, met_tool, indices):
    conf = metplus_config()
    data_type = 'FCST'
    conf.set('config', f'{data_type}_VAR1_NAME', "NAME1")
    conf.set('config', f'{data_type}_GRID_STAT_VAR2_NAME', "GSNAME2")

    var_name_indices = util.find_var_name_indices(conf, data_type=data_type,
                                                  met_tool=met_tool)

    assert(var_name_indices == indices)



def test_get_lead_sequence_lead(metplus_config):
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 13) }
    conf = metplus_config()
    conf.set('config', 'LEAD_SEQ', "3,6,9,12")
    test_seq = util.get_lead_sequence(conf, input_dict)
    hour_seq = []
    for test in test_seq:
        hour_seq.append(time_util.ti_get_seconds_from_relativedelta(test) // 3600)
    lead_seq = [ 3, 6, 9, 12 ]
    assert(hour_seq == lead_seq)


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
def test_get_lead_sequence_lead_list(metplus_config, key, value):
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 13) }
    conf = metplus_config()
    conf.set('config', 'LEAD_SEQ', key)
    test_seq = util.get_lead_sequence(conf, input_dict)
    hour_seq = []

    for test in test_seq:
        hour_seq.append(time_util.ti_get_seconds_from_relativedelta(test) // 3600)
    lead_seq = value
    assert(hour_seq == lead_seq)

@pytest.mark.parametrize(
    'list_string, output_list', [
        ('begin_end_incr(3,12,3)',
         ['3', '6', '9', '12']),

        ('1,2,3,4',
         ['1', '2', '3', '4']),

        (' 1,2,3,4',
         ['1', '2', '3', '4']),

        ('1,2,3,4 ',
         ['1', '2', '3', '4']),

        (' 1,2,3,4 ',
         ['1', '2', '3', '4']),

        ('1, 2,3,4',
         ['1', '2', '3', '4']),

        ('1,2, 3, 4',
         ['1', '2', '3', '4']),

        ('begin_end_incr( 3,12 , 3)',
         ['3', '6', '9', '12']),

        ('begin_end_incr(0,10,2)',
         ['0', '2', '4', '6', '8', '10']),

        ('begin_end_incr(10,0,-2)',
         ['10', '8', '6', '4', '2', '0']),

        ('begin_end_incr(2,2,20)',
         ['2']),

        ('begin_end_incr(0,2,1), begin_end_incr(3,9,3)',
         ['0','1','2','3','6','9']),

        ('mem_begin_end_incr(0,2,1), mem_begin_end_incr(3,9,3)',
         ['mem_0','mem_1','mem_2','mem_3','mem_6','mem_9']),

        ('mem_begin_end_incr(0,2,1,3), mem_begin_end_incr(3,12,3,3)',
         ['mem_000', 'mem_001', 'mem_002', 'mem_003', 'mem_006', 'mem_009', 'mem_012']),

        ('begin_end_incr(0,10,2)H, 12',  [ '0H', '2H', '4H', '6H', '8H', '10H', '12']),

        ('begin_end_incr(0,10800,3600)S, 4H',  [ '0S', '3600S', '7200S', '10800S', '4H']),

        ('data.{init?fmt=%Y%m%d%H?shift=begin_end_incr(0, 3, 3)H}.ext',
         ['data.{init?fmt=%Y%m%d%H?shift=0H}.ext',
          'data.{init?fmt=%Y%m%d%H?shift=3H}.ext',
          ]),

    ]
)
def test_getlist_begin_end_incr(list_string, output_list):
    assert(util.getlist(list_string) == output_list)

# @pytest.mark.parametrize(
#     'key, value', [
#         (0,  [ 0, 12, 24, 36]),
#         (1,  [ 1, 13, 25 ]),
#         (2,  [ 2, 14, 26 ]),
#         (3,  [ 3, 15, 27 ]),
#         (4,  [ 4, 16, 28 ]),
#         (5,  [ 5, 17, 29 ]),
#         (6,  [ 6, 18, 30 ]),
#         (7,  [ 7, 19, 31 ]),
#         (8,  [ 8, 20, 32 ]),
#         (9,  [ 9, 21, 33 ]),
#         (10, [ 10, 22, 34 ]),
#         (11, [ 11, 23, 35 ]),
#         (12, [ 0, 12, 24, 36 ]),
#         (13, [ 1, 13, 25 ]),
#         (14, [ 2, 14, 26 ]),
#         (15, [ 3, 15, 27 ]),
#         (16, [ 4, 16, 28 ]),
#         (17, [ 5, 17, 29 ]),
#         (18, [ 6, 18, 30 ]),
#         (19, [ 7, 19, 31 ]),
#         (20, [ 8, 20, 32 ]),
#         (21, [ 9, 21, 33 ]),
#         (22, [ 10, 22, 34 ]),
#         (23, [ 11, 23, 35 ])
#     ]
# )
# def test_get_lead_sequence_init(key, value):
#     input_dict = { 'valid' : datetime.datetime(2019, 2, 1, key) }
#     conf = metplus_config()
#     conf.set('config', 'INIT_SEQ', "0, 12")
#     conf.set('config', 'LEAD_SEQ_MAX', 36)
#     test_seq = util.get_lead_sequence(conf, input_dict)
#     lead_seq = value
#     assert(test_seq == [relativedelta(hours=lead) for lead in lead_seq])
#
# def test_get_lead_sequence_init_min_10():
#     input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 12) }
#     conf = metplus_config()
#     conf.set('config', 'INIT_SEQ', "0, 12")
#     conf.set('config', 'LEAD_SEQ_MAX', 24)
#     conf.set('config', 'LEAD_SEQ_MIN', 10)
#     test_seq = util.get_lead_sequence(conf, input_dict)
#     lead_seq = [ 12, 24 ]
#     assert(test_seq == [relativedelta(hours=lead) for lead in lead_seq])
#
@pytest.mark.parametrize(
    'item_list, extension, is_valid', [
        (['FCST'], 'NAME', False),
        (['OBS'], 'NAME', False),
        (['FCST', 'OBS'], 'NAME', True),
        (['BOTH'], 'NAME', True),
        (['FCST', 'OBS', 'BOTH'], 'NAME', False),
        (['FCST', 'ENS'], 'NAME', False),
        (['OBS', 'ENS'], 'NAME', False),
        (['FCST', 'OBS', 'ENS'], 'NAME', True),
        (['BOTH', 'ENS'], 'NAME', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'NAME', False),

        (['FCST'], 'THRESH', False),
        (['OBS'], 'THRESH', False),
        (['FCST', 'OBS'], 'THRESH', True),
        (['BOTH'], 'THRESH', True),
        (['FCST', 'OBS', 'BOTH'], 'THRESH', False),
        (['FCST', 'ENS'], 'THRESH', False),
        (['OBS', 'ENS'], 'THRESH', False),
        (['FCST', 'OBS', 'ENS'], 'THRESH', True),
        (['BOTH', 'ENS'], 'THRESH', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'THRESH', False),

        (['FCST'], 'OPTIONS', True),
        (['OBS'], 'OPTIONS', True),
        (['FCST', 'OBS'], 'OPTIONS', True),
        (['BOTH'], 'OPTIONS', True),
        (['FCST', 'OBS', 'BOTH'], 'OPTIONS', False),
        (['FCST', 'ENS'], 'OPTIONS', True),
        (['OBS', 'ENS'], 'OPTIONS', True),
        (['FCST', 'OBS', 'ENS'], 'OPTIONS', True),
        (['BOTH', 'ENS'], 'OPTIONS', True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], 'OPTIONS', False),

        (['FCST', 'OBS', 'BOTH'], 'LEVELS', False),
        (['FCST', 'OBS'], 'LEVELS', True),
        (['BOTH'], 'LEVELS', True),
        (['FCST', 'OBS', 'ENS'], 'LEVELS', True),
        (['BOTH', 'ENS'], 'LEVELS', True),

    ]
)
def test_is_var_item_valid(metplus_config, item_list, extension, is_valid):
    conf = metplus_config()
    assert(util.is_var_item_valid(item_list, '1', extension, conf)[0] == is_valid)

@pytest.mark.parametrize(
    'item_list, configs_to_set, is_valid', [

        (['FCST'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, True),
        (['FCST'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                    'FCST_VAR1_NAME': 'script_name.py something else'}, True),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                    'FCST_VAR1_NAME': 'APCP'}, False),

        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, True),
        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, True),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(*,*)"',
                   'FCST_VAR1_NAME': 'APCP'}, False),

        (['FCST'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, False),
        (['FCST'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS'], {'OBS_VAR1_LEVELS': '"(0,*,*)", "(1,*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, False),

        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'script_name.py something else'}, False),
        (['FCST', 'ENS'], {'FCST_VAR1_LEVELS': 'A06, A12',
                    'OBS_VAR1_NAME': 'APCP'}, False),
        (['OBS', 'ENS'], {'OBS_VAR1_LEVELS': '"(0,*,*)", "(1,*,*)"',
                   'FCST_VAR1_NAME': 'script_name.py something else'}, False),

    ]
)
def test_is_var_item_valid_levels(metplus_config, item_list, configs_to_set, is_valid):
    conf = metplus_config()
    for key, value in configs_to_set.items():
        conf.set('config', key, value)

    assert(util.is_var_item_valid(item_list, '1', 'LEVELS', conf)[0] == is_valid)

def test_remove_staged_files():
    ''' Verify that the remove_staged_files correctly removes
        the files with a filename pattern specified by the
        filename_regex that are owned by the current are
        removed, leaving all other files intact.

    '''

    # Create filter files (which are to be deleted later on) and some
    # other files with a different filename pattern
    staged_dir = '/tmp/test_cleanup'
    util.mkdir_p(staged_dir)
    filename_regex = 'filter_.*'
    files_to_create = ['foo.txt', 'bar.txt', 'baz.csv', 'filter_20191214_00', 'filter-do-not-delete-me.txt', 'filter_20121212.tcst']
    expected_deleted = ['filter_20191214_00','filter_20121212.tcst' ]

    for cur_file in files_to_create:
        full_file = os.path.join(staged_dir, cur_file)
        subprocess.run(['touch', full_file])

    util.remove_staged_files(staged_dir, filename_regex, None)

    # Now check the /tmp/test_cleanup dir and verify that we no longer have the two filter_xyz files
    # we deleted
    actual_remaining_files = util.get_files(staged_dir, ".*", None)
    for cur_deleted in expected_deleted:
        assert (cur_deleted not in actual_remaining_files)


    # Now clean up your /tmp/test_cleanup directory so we don't leave
    # unused files and directories remaining...
    shutil.rmtree(staged_dir)

# test that if wrapper specific field info is specified, it only gets
# values from that list. All generic values should be read if no
# wrapper specific field info variables are specified
def test_parse_var_list_wrapper_specific(metplus_config):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "ENAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "ELEVELS11, ELEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "ENAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "ELEVELS21, ELEVELS22")
    conf.set('config', 'FCST_GRID_STAT_VAR1_NAME', "GNAME1")
    conf.set('config', 'FCST_GRID_STAT_VAR1_LEVELS', "GLEVELS11, GLEVELS12")

    e_var_list = util.parse_var_list(conf,
                                     time_info=None,
                                     data_type='FCST',
                                     met_tool='ensemble_stat')

    g_var_list = util.parse_var_list(conf,
                                     time_info=None,
                                     data_type='FCST',
                                     met_tool='grid_stat')

    assert(len(e_var_list) == 4 and len(g_var_list) == 2 and
           e_var_list[0]['fcst_name'] == "ENAME1" and
           e_var_list[1]['fcst_name'] == "ENAME1" and
           e_var_list[2]['fcst_name'] == "ENAME2" and
           e_var_list[3]['fcst_name'] == "ENAME2" and
           e_var_list[0]['fcst_level'] == "ELEVELS11" and
           e_var_list[1]['fcst_level'] == "ELEVELS12" and
           e_var_list[2]['fcst_level'] == "ELEVELS21" and
           e_var_list[3]['fcst_level'] == "ELEVELS22" and
           g_var_list[0]['fcst_name'] == "GNAME1" and
           g_var_list[1]['fcst_name'] == "GNAME1" and
           g_var_list[0]['fcst_level'] == "GLEVELS11" and
           g_var_list[1]['fcst_level'] == "GLEVELS12")

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
        # remove MakePlots from list
        ('StatAnalysis, MakePlots', ['StatAnalysis']),
    ]
)
def test_get_process_list(metplus_config, input_list, expected_list):
    conf = metplus_config()
    conf.set('config', 'PROCESS_LIST', input_list)
    process_list = util.get_process_list(conf)
    output_list = [item[0] for item in process_list]
    assert(output_list == expected_list)

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
def test_get_process_list_instances(metplus_config, input_list, expected_list):
    conf = metplus_config()
    conf.set('config', 'PROCESS_LIST', input_list)
    output_list = util.get_process_list(conf)
    assert(output_list == expected_list)

@pytest.mark.parametrize(
    'time_from_conf, fmt, is_datetime', [
        ('', '%Y', False),
        ('a', '%Y', False),
        ('1987', '%Y', True),
        ('1987', '%Y%m', False),
        ('198702', '%Y%m', True),
        ('198702', '%Y%m%d', False),
        ('19870201', '%Y%m%d', True),
        ('19870201', '%Y%m%d%H', False),
        ('{now?fmt=%Y%m%d}', '%Y%m%d', True),
        ('{now?fmt=%Y%m%d}', '%Y%m%d%H', True),
        ('{now?fmt=%Y%m%d}00', '%Y%m%d%H', True),
        ('{today}', '%Y%m%d', True),
        ('{today}', '%Y%m%d%H', True),
    ]
)
def test_get_time_obj(time_from_conf, fmt, is_datetime):
    clock_time = datetime.datetime(2019, 12, 31, 15, 30)

    time_obj = util.get_time_obj(time_from_conf, fmt, clock_time)

    assert(isinstance(time_obj, datetime.datetime) == is_datetime)

@pytest.mark.parametrize(
     'list_str, expected_fixed_list', [
         ('some,items,here', ['some',
                              'items',
                              'here']),
         ('(*,*)', ['(*,*)']),
        ("-type solar_alt -thresh 'ge45' -name solar_altitude_ge_45_mask -input_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;' -mask_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;\'",
        ["-type solar_alt -thresh 'ge45' -name solar_altitude_ge_45_mask -input_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;' -mask_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;\'"]),
        ("(*,*),'level=\"(0,*,*)\"' -censor_thresh [lt12.3,gt8.8],other", ['(*,*)',
                                                                           "'level=\"(0,*,*)\"' -censor_thresh [lt12.3,gt8.8]",
                                                                           'other']),
     ]
)
def test_fix_list(list_str, expected_fixed_list):
    item_list = list(reader([list_str]))[0]
    fixed_list = util.fix_list(item_list)
    print("FIXED LIST:")
    for fixed in fixed_list:
        print(f"ITEM: {fixed}")

    print("EXPECTED LIST")
    for expected in expected_fixed_list:
        print(f"ITEM: {expected}")

    assert(fixed_list == expected_fixed_list)

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
        ('MakePlotsWrapper', 'make_plots_wrapper'),
        ('MODEWrapper', 'mode_wrapper'),
        ('MTDWrapper', 'mtd_wrapper'),
        ('PB2NCWrapper', 'pb2nc_wrapper'),
        ('PCPCombineWrapper', 'pcp_combine_wrapper'),
        ('Point2GridWrapper', 'point2grid_wrapper'),
        ('PointStatWrapper', 'point_stat_wrapper'),
        ('PyEmbedWrapper', 'py_embed_wrapper'),
        ('RegridDataPlaneWrapper', 'regrid_data_plane_wrapper'),
        ('SeriesAnalysisWrapper', 'series_analysis_wrapper'),
        ('SeriesByInitWrapper', 'series_by_init_wrapper'),
        ('SeriesByLeadWrapper', 'series_by_lead_wrapper'),
        ('StatAnalysisWrapper', 'stat_analysis_wrapper'),
        ('TCMPRPlotterWrapper', 'tcmpr_plotter_wrapper'),
        ('TCPairsWrapper', 'tc_pairs_wrapper'),
        ('TCStatWrapper', 'tc_stat_wrapper'),
    ]
)
def test_camel_to_underscore(camel, underscore):
    assert(util.camel_to_underscore(camel) == underscore)

@pytest.mark.parametrize(
    'filepath, template, expected_result', [
        (os.getcwd(), 'file.{valid?fmt=%Y%m%d%H}.ext', None),
        ('file.2019020104.ext', 'file.{valid?fmt=%Y%m%d%H}.ext', datetime.datetime(2019, 2, 1, 4)),
        ('filename.2019020104.ext', 'file.{valid?fmt=%Y%m%d%H}.ext', None),
        ('file.2019020104.ext.gz', 'file.{valid?fmt=%Y%m%d%H}.ext', datetime.datetime(2019, 2, 1, 4)),
        ('filename.2019020104.ext.gz', 'file.{valid?fmt=%Y%m%d%H}.ext', None),
    ]
)
def test_get_time_from_file(filepath, template, expected_result):
    result = util.get_time_from_file(filepath, template)

    if result is None:
        assert(expected_result is None)
    else:
        assert(result['valid'] == expected_result)

@pytest.mark.parametrize(
    'value, expected_result', [
        (3.3, 3.5),
        (3.1, 3.0),
        (-3.2, -3.0),
        (-3.8, -4.0),
    ]
)
def test_round_0p5(value, expected_result):
    assert(util.round_0p5(value) == expected_result)

@pytest.mark.parametrize(
    'expression, expected_result', [
        ('gt3', 'gt3'),
        ('>3', 'gt3'),
        ('le3.5', 'le3.5'),
        ('<=3.5', 'le3.5'),
        ('==4', 'eq4'),
        ('!=3.5', 'ne3.5'),
    ]
)
def test_comparison_to_letter_format(expression, expected_result):
    assert(util.comparison_to_letter_format(expression) == expected_result)

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
def test_get_custom_string_list(metplus_config, conf_items, met_tool, expected_result):
    config = metplus_config()
    for conf_key, conf_value in conf_items.items():
        config.set('config', conf_key, conf_value)

    assert(util.get_custom_string_list(config, met_tool) == expected_result)

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
def test_get_skip_times(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config()
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert(util.get_skip_times(conf) == expected_dict)

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
def test_get_skip_times_wrapper(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config()

    # set wrapper specific skip times, then ensure it is found
    conf.set('config', 'GRID_STAT_SKIP_TIMES', skip_times_conf)

    assert(util.get_skip_times(conf, 'grid_stat') == expected_dict)

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
def test_get_skip_times_wrapper_not_used(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config()

    # set generic SKIP_TIMES, then request grid_stat to ensure it uses generic
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert(util.get_skip_times(conf, 'grid_stat') == expected_dict)

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
def test_get_skip_time(run_time, skip_times, expected_result):
    time_info = time_util.ti_calculate({'valid': run_time})
    assert(util.skip_time(time_info, skip_times) == expected_result)

def test_get_skip_time_no_valid():
    input_dict ={'init': datetime.datetime(2019, 1, 29)}
    assert(util.skip_time(input_dict, {'%Y': ['2019']}) == False)

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
def test_expand_int_string_to_list(int_string, expected_result):
    result = util.expand_int_string_to_list(int_string)
    assert(result == expected_result)

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
def test_subset_list(subset_definition, expected_result):
    full_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    result = util.subset_list(full_list, subset_definition)
    assert(result == expected_result)

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
def test_get_storm_ids(metplus_config, filename, expected_result):
    config = metplus_config()
    filepath = os.path.join(config.getdir('METPLUS_BASE'),
                            'internal_tests',
                            'data',
                            'stat_data',
                            filename)

    assert(util.get_storm_ids(filepath) == expected_result)

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
def test_get_storms(metplus_config, filename, expected_result):
    storm_id_index = 4
    config = metplus_config()
    filepath = os.path.join(config.getdir('METPLUS_BASE'),
                            'internal_tests',
                            'data',
                            'stat_data',
                            filename)

    storm_dict = util.get_storms(filepath)
    print(storm_dict)
    assert(list(storm_dict.keys()) == expected_result)
    for storm_id in expected_result[1:]:
        for storm_line in storm_dict[storm_id]:
            # ensure storm_id_index matches storm ID
            assert(storm_line.split()[storm_id_index] == storm_id)

    # ensure header matches expected format
    if storm_dict:
        assert(storm_dict['header'].split()[storm_id_index] == 'STORM_ID')
