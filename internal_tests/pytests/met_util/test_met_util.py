#!/usr/bin/env python

import sys
import pytest
import datetime
import met_util as util
import time_util
import produtil
import os
from dateutil.relativedelta import relativedelta
import config_metplus

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='test ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test ')
        produtil.log.postmsg('met_util test is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        logger = util.get_logger(config)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'met_util test failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)

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
        ({">=a"}, False),
        ({"2.3"}, False),
        ({"<=2.3", "2.4", "gt2.7"}, False),
        ({"<=2.3||>=4.2", "gt2.3&&lt4.2"}, True),
        ({"gt2.3&&lt4.2a"}, False),
        ({"gt2sd.3&&lt4.2"}, False),
        ({"gt2.3&a&lt4.2"}, False),
        ({'gt4&&lt5&&ne4.5'}, True),
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

    ]
)
def test_get_threshold_via_regex(key, value):
    assert(util.get_threshold_via_regex(key) == value)

def test_preprocess_file_gz():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile.txt.gz"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile.txt"
    outpath = util.preprocess_file(filepath, None, conf)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_preprocess_file_bz2():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile2.txt.bz2"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile2.txt"
    outpath = util.preprocess_file(filepath, None, conf)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_preprocess_file_zip():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile3.txt.zip"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile3.txt"
    outpath = util.preprocess_file(filepath, None, conf)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_preprocess_file_unzipped():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile4.txt"
    outpath = util.preprocess_file(filepath, None, conf)
    assert(filepath == outpath and os.path.exists(outpath))

def test_preprocess_file_none():
    conf = metplus_config()
    outpath = util.preprocess_file(None, None, conf)
    assert(outpath is None)

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

# field info only defined in the FCST_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, False),
        ('FCST', True),
        ('OBS', False),
    ]
)
def test_parse_var_list_fcst_only(data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "NAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because OBS variables are missing
    if util.validate_configuration_variables(conf):
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
def test_parse_var_list_obs(data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'OBS_VAR1_NAME', "NAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "NAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because FCST variables are missing
    if util.validate_configuration_variables(conf):
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
def test_parse_var_list_both(data_type, list_created):
    conf = metplus_config()
    conf.set('config', 'BOTH_VAR1_NAME', "NAME1")
    conf.set('config', 'BOTH_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'BOTH_VAR2_NAME', "NAME2")
    conf.set('config', 'BOTH_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because BOTH variables are used
    if not util.validate_configuration_variables(conf):
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
def test_parse_var_list_fcst_and_obs():
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
    if not util.validate_configuration_variables(conf):
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
def test_parse_var_list_fcst_and_obs_alternate():
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "FNAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "FLEVELS11, FLEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "ONAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "OLEVELS21, OLEVELS22")

    # configuration is invalid and parse var list should not give any results
    assert(not util.validate_configuration_variables(conf) and not util.parse_var_list(conf))

# VAR1 defined by OBS, VAR2 by FCST, VAR3 by both FCST AND OBS
@pytest.mark.parametrize(
    'data_type, list_len, name_levels', [
        (None, 0, None),
        ('FCST', 4, ('FNAME2:FLEVELS21','FNAME2:FLEVELS22','FNAME3:FLEVELS31','FNAME3:FLEVELS32')),
        ('OBS', 4, ('ONAME1:OLEVELS11','ONAME1:OLEVELS12','ONAME3:OLEVELS31','ONAME3:OLEVELS32')),
    ]
)
def test_parse_var_list_fcst_and_obs_and_both(data_type, list_len, name_levels):
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
    if util.validate_configuration_variables(conf):
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
def test_parse_var_list_fcst_only_options(data_type, list_len):
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR1_THRESH', ">1, >2")
    conf.set('config', 'OBS_VAR1_OPTIONS', "OOPTIONS11")

    # this should not occur because OBS variables are missing
    if util.validate_configuration_variables(conf):
        assert(False)

    var_list = util.parse_var_list(conf, time_info=None, data_type=data_type)

    assert(len(var_list) == list_len)

def test_get_lead_sequence_lead():
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
        ('begin_end_incr(72,72,6)',  [ 72 ])
    ]
)
def test_get_lead_sequence_lead_list(key, value):
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
    'key, value', [
        (0,  [ 0, 12, 24, 36]),
        (1,  [ 1, 13, 25 ]),
        (2,  [ 2, 14, 26 ]),
        (3,  [ 3, 15, 27 ]),
        (4,  [ 4, 16, 28 ]),
        (5,  [ 5, 17, 29 ]),
        (6,  [ 6, 18, 30 ]),
        (7,  [ 7, 19, 31 ]),
        (8,  [ 8, 20, 32 ]),
        (9,  [ 9, 21, 33 ]),
        (10, [ 10, 22, 34 ]),
        (11, [ 11, 23, 35 ]),
        (12, [ 0, 12, 24, 36 ]),
        (13, [ 1, 13, 25 ]),
        (14, [ 2, 14, 26 ]),
        (15, [ 3, 15, 27 ]),
        (16, [ 4, 16, 28 ]),
        (17, [ 5, 17, 29 ]),
        (18, [ 6, 18, 30 ]),
        (19, [ 7, 19, 31 ]),
        (20, [ 8, 20, 32 ]),
        (21, [ 9, 21, 33 ]),
        (22, [ 10, 22, 34 ]),
        (23, [ 11, 23, 35 ])
    ]
)
def test_get_lead_sequence_init(key, value):
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, key) }
    conf = metplus_config()
    conf.set('config', 'INIT_SEQ', "0, 12")
    conf.set('config', 'LEAD_SEQ_MAX', 36)
    test_seq = util.get_lead_sequence(conf, input_dict)
    lead_seq = value
    assert(test_seq == [relativedelta(hours=lead) for lead in lead_seq])

def test_get_lead_sequence_init_min_10():
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 12) }
    conf = metplus_config()
    conf.set('config', 'INIT_SEQ', "0, 12")
    conf.set('config', 'LEAD_SEQ_MAX', 24)
    conf.set('config', 'LEAD_SEQ_MIN', 10)
    test_seq = util.get_lead_sequence(conf, input_dict)
    lead_seq = [ 12, 24 ]
    assert(test_seq == [relativedelta(hours=lead) for lead in lead_seq])

@pytest.mark.parametrize(
    'item_list, is_valid', [
        (['FCST'], False),
        (['OBS'], False),
        (['FCST', 'OBS'], True),
        (['BOTH'], True),
        (['FCST', 'OBS', 'BOTH'], False),
        (['FCST', 'ENS'], False),
        (['OBS', 'ENS'], False),
        (['FCST', 'OBS', 'ENS'], True),
        (['BOTH', 'ENS'], True),
        (['FCST', 'OBS', 'BOTH', 'ENS'], False),
    ]
)

def test_is_var_item_valid(item_list, is_valid):
    conf = metplus_config()
    assert(util.is_var_item_valid(item_list, conf)[0] == is_valid)
