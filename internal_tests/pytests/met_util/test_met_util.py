#!/usr/bin/env python
from __future__ import print_function
import sys
import pytest
import datetime
import met_util as util
import time_util
import produtil
import os
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
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'met_util test failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_add_common_items_to_dictionary():
    pytest.skip('Function is not used')
    conf = metplus_config()
    dictionary = dict()
    util.add_common_items_to_dictionary(conf, dictionary)
    assert(dictionary['WGRIB2_EXE'] == conf.getexe('WGRIB2'))


def test_threshold_gt():
    thresh_list = {"gt2.3", "gt5.5"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ge():
    thresh_list = {"ge2.3", "ge5.5"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_eq():
    thresh_list = {"eq2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ne():
    thresh_list = {"ne2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_lt():
    thresh_list = {"lt2.3", "lt1.1"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_le():
    thresh_list = {"le2.3", "le1.1"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_gt_symbol():
    thresh_list = {">2.3", ">5.5"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ge_symbol():
    thresh_list = {">=2.3", ">=5.5"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_eq_symbol():
    thresh_list = {"==2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ne_symbol():
    thresh_list = {"!=.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_lt_symbol():
    thresh_list = {"<2.3", "<1."}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_le_symbol():
    thresh_list = {"<=2.3", "<=1.1"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_gt_no_number():
    thresh_list = {"gta"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_ge_symbol_no_number():
    thresh_list = {">=a"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_just_number():
    thresh_list = {"2.3"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_only_one_fails():
    thresh_list = {"<=2.3", "2.4", "gt2.7"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_complex_comparison():
    thresh_list = {"<=2.3||>=4.2", "gt2.3&&lt4.2"}
    assert(util.validate_thresholds(thresh_list))

def test_get_number_from_threshold_gt_int():
    assert(util.get_number_from_threshold("gt4") == 4)

def test_get_number_from_threshold_gt_symbol():
    assert(util.get_number_from_threshold(">4.545") == 4.545)

def test_get_number_from_threshold_ge_symbol():
    assert(util.get_number_from_threshold(">=4.0") == 4.0)

def test_get_number_from_threshold_lt_symbol():
    assert(util.get_number_from_threshold("<4.5") == 4.5)

def test_get_number_from_threshold_le_symbol():
    assert(util.get_number_from_threshold("<=4.5") == 4.5)

def test_get_number_from_threshold_ne_symbol():
    assert(util.get_number_from_threshold("!=4.5") == 4.5)

def test_get_number_from_threshold_eq_symbol():
    assert(util.get_number_from_threshold("==4.5") == 4.5)

def test_get_number_from_threshold_gt():
    assert(util.get_number_from_threshold("gt4.5") == 4.5)

def test_get_number_from_threshold_ge():
    assert(util.get_number_from_threshold("ge4.5") == 4.5)

def test_get_number_from_threshold_lt():
    assert(util.get_number_from_threshold("lt4.5") == 4.5)

def test_get_number_from_threshold_le():
    assert(util.get_number_from_threshold("le4.5") == 4.5)

def test_get_number_from_threshold_ne():
    assert(util.get_number_from_threshold("ne10.5") == 10.5)

def test_get_number_from_threshold_eq():
    assert(util.get_number_from_threshold("eq4.5") == 4.5)

def test_get_number_from_threshold_eq_negative():
    assert(util.get_number_from_threshold("eq-4.5") == -4.5)

def test_get_number_from_threshold_eq_positive():
    assert(util.get_number_from_threshold("eq+4.5") == 4.5)

def test_get_number_from_threshold_eq_starts_with_decimal():
    assert(util.get_number_from_threshold("eq.5") == 0.5)

def test_get_number_from_threshold_eq_ends_with_decimal():
    assert(util.get_number_from_threshold("eq5.") == 5)

def test_get_comparison_from_threshold_gt_symbol():
    assert(util.get_comparison_from_threshold(">4.545") == ">")

def test_get_comparison_from_threshold_ge_symbol():
    assert(util.get_comparison_from_threshold(">=4.0") == ">=")

def test_get_comparison_from_threshold_lt_symbol():
    assert(util.get_comparison_from_threshold("<4.5") == "<")

def test_get_comparison_from_threshold_le_symbol():
    assert(util.get_comparison_from_threshold("<=4.5") == "<=")

def test_get_comparison_from_threshold_ne_symbol():
    assert(util.get_comparison_from_threshold("!=4.5") == "!=")

def test_get_comparison_from_threshold_eq_symbol():
    assert(util.get_comparison_from_threshold("==4.5") == "==")

def test_get_comparison_from_threshold_gt():
    assert(util.get_comparison_from_threshold("gt4.5") == "gt")

def test_get_comparison_from_threshold_ge():
    assert(util.get_comparison_from_threshold("ge4.5") == "ge")

def test_get_comparison_from_threshold_lt():
    assert(util.get_comparison_from_threshold("lt4.5") == "lt")

def test_get_comparison_from_threshold_le():
    assert(util.get_comparison_from_threshold("le4.5") == "le")

def test_get_comparison_from_threshold_ne():
    assert(util.get_comparison_from_threshold("ne10.5") == "ne")

def test_get_comparison_from_threshold_eq():
    assert(util.get_comparison_from_threshold("eq4.5") == "eq")

def test_get_comparison_from_threshold_complex():
    assert(util.get_comparison_from_threshold("<=2.3||>=4.2") == "<=")

def test_get_number_from_threshold_complex():
    assert(util.get_number_from_threshold("<=2.3||>=4.2") == 2.3)

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
def test_parse_var_list_fcst_only():
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "NAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "LEVELS21, LEVELS22")
    var_list = util.parse_var_list(conf)
    assert(var_list[0]['fcst_name'] == "NAME1" and \
           var_list[0]['obs_name'] == "NAME1" and \
           var_list[1]['fcst_name'] == "NAME1" and \
           var_list[1]['obs_name'] == "NAME1" and \
           var_list[2]['fcst_name'] == "NAME2" and \
           var_list[2]['obs_name'] == "NAME2" and \
           var_list[3]['fcst_name'] == "NAME2" and \
           var_list[3]['obs_name'] == "NAME2" and \
           var_list[0]['fcst_level'] == "LEVELS11" and \
           var_list[0]['obs_level'] == "LEVELS11" and \
           var_list[1]['fcst_level'] == "LEVELS12" and \
           var_list[1]['obs_level'] == "LEVELS12" and \
           var_list[2]['fcst_level'] == "LEVELS21" and \
           var_list[2]['obs_level'] == "LEVELS21" and \
           var_list[3]['fcst_level'] == "LEVELS22" and \
           var_list[3]['obs_level'] == "LEVELS22")

# field info only defined in the OBS_* variables
def test_parse_var_list_obs():
    conf = metplus_config()
    conf.set('config', 'OBS_VAR1_NAME', "NAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "NAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "LEVELS21, LEVELS22")
    var_list = util.parse_var_list(conf)
    assert(var_list[0]['fcst_name'] == "NAME1" and \
           var_list[0]['obs_name'] == "NAME1" and \
           var_list[1]['fcst_name'] == "NAME1" and \
           var_list[1]['obs_name'] == "NAME1" and \
           var_list[2]['fcst_name'] == "NAME2" and \
           var_list[2]['obs_name'] == "NAME2" and \
           var_list[3]['fcst_name'] == "NAME2" and \
           var_list[3]['obs_name'] == "NAME2" and \
           var_list[0]['fcst_level'] == "LEVELS11" and \
           var_list[0]['obs_level'] == "LEVELS11" and \
           var_list[1]['fcst_level'] == "LEVELS12" and \
           var_list[1]['obs_level'] == "LEVELS12" and \
           var_list[2]['fcst_level'] == "LEVELS21" and \
           var_list[2]['obs_level'] == "LEVELS21" and \
           var_list[3]['fcst_level'] == "LEVELS22" and \
           var_list[3]['obs_level'] == "LEVELS22")

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
    var_list = util.parse_var_list(conf)
    assert(var_list[0]['fcst_name'] == "FNAME1" and \
           var_list[0]['obs_name'] == "FNAME1" and \
           var_list[1]['fcst_name'] == "FNAME1" and \
           var_list[1]['obs_name'] == "FNAME1" and \
           var_list[2]['fcst_name'] == "ONAME2" and \
           var_list[2]['obs_name'] == "ONAME2" and \
           var_list[3]['fcst_name'] == "ONAME2" and \
           var_list[3]['obs_name'] == "ONAME2" and \
           var_list[0]['fcst_level'] == "FLEVELS11" and \
           var_list[0]['obs_level'] == "FLEVELS11" and \
           var_list[1]['fcst_level'] == "FLEVELS12" and \
           var_list[1]['obs_level'] == "FLEVELS12" and \
           var_list[2]['fcst_level'] == "OLEVELS21" and \
           var_list[2]['obs_level'] == "OLEVELS21" and \
           var_list[3]['fcst_level'] == "OLEVELS22" and \
           var_list[3]['obs_level'] == "OLEVELS22")

# VAR1 defined by OBS, VAR2 by FCST, VAR3 by both FCST AND OBS
def test_parse_var_list_fcst_and_obs_and_both():
    conf = metplus_config()
    conf.set('config', 'OBS_VAR1_NAME', "ONAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "OLEVELS11, OLEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "FNAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "FLEVELS21, FLEVELS22")
    conf.set('config', 'FCST_VAR3_NAME', "FNAME3")
    conf.set('config', 'FCST_VAR3_LEVELS', "FLEVELS31, FLEVELS32")
    conf.set('config', 'OBS_VAR3_NAME', "ONAME3")
    conf.set('config', 'OBS_VAR3_LEVELS', "OLEVELS31, OLEVELS32")

    var_list = util.parse_var_list(conf)
    assert(var_list[0]['fcst_name'] == "ONAME1" and \
           var_list[0]['obs_name'] == "ONAME1" and \
           var_list[1]['fcst_name'] == "ONAME1" and \
           var_list[1]['obs_name'] == "ONAME1" and \
           var_list[2]['fcst_name'] == "FNAME2" and \
           var_list[2]['obs_name'] == "FNAME2" and \
           var_list[3]['fcst_name'] == "FNAME2" and \
           var_list[3]['obs_name'] == "FNAME2" and \
           var_list[4]['fcst_name'] == "FNAME3" and \
           var_list[4]['obs_name'] == "ONAME3" and \
           var_list[5]['fcst_name'] == "FNAME3" and \
           var_list[5]['obs_name'] == "ONAME3" and \
           var_list[0]['fcst_level'] == "OLEVELS11" and \
           var_list[0]['obs_level'] == "OLEVELS11" and \
           var_list[1]['fcst_level'] == "OLEVELS12" and \
           var_list[1]['obs_level'] == "OLEVELS12" and \
           var_list[2]['fcst_level'] == "FLEVELS21" and \
           var_list[2]['obs_level'] == "FLEVELS21" and \
           var_list[3]['fcst_level'] == "FLEVELS22" and \
           var_list[3]['obs_level'] == "FLEVELS22" and \
           var_list[4]['fcst_level'] == "FLEVELS31" and \
           var_list[4]['obs_level'] == "OLEVELS31" and \
           var_list[5]['fcst_level'] == "FLEVELS32" and \
           var_list[5]['obs_level'] == "OLEVELS32" )

# option defined in obs only
def test_parse_var_list_fcst_only():
    conf = metplus_config()
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR1_THRESH', ">1, >2")
    conf.set('config', 'OBS_VAR1_OPTIONS', "OOPTIONS11")
    var_list = util.parse_var_list(conf)
    assert(var_list[0]['fcst_name'] == "NAME1" and \
           var_list[0]['obs_name'] == "NAME1" and \
           var_list[1]['fcst_name'] == "NAME1" and \
           var_list[1]['obs_name'] == "NAME1" and \
           var_list[0]['fcst_level'] == "LEVELS11" and \
           var_list[0]['obs_level'] == "LEVELS11" and \
           var_list[1]['fcst_level'] == "LEVELS12" and \
           var_list[1]['obs_level'] == "LEVELS12" and \
           var_list[0]['fcst_thresh'] ==  var_list[0]['obs_thresh'] and \
           var_list[1]['fcst_thresh'] ==  var_list[1]['obs_thresh'] and \
           var_list[0]['fcst_extra'] == "" and \
           var_list[0]['obs_extra'] == "OOPTIONS11" and \
           var_list[1]['fcst_extra'] == "" and \
           var_list[1]['obs_extra'] == "OOPTIONS11"
           )

def test_get_lead_sequence_lead():
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 13) }
    conf = metplus_config()
    conf.set('config', 'LEAD_SEQ', "3,6,9,12")
    test_seq = util.get_lead_sequence(conf, input_dict)
    hour_seq = []
    for test in test_seq:
        hour_seq.append(time_util.ti_get_seconds(test) // 3600)
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
        hour_seq.append(time_util.ti_get_seconds(test) // 3600)
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
    assert(test_seq == lead_seq)

def test_get_lead_sequence_init_min_10():
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 12) }
    conf = metplus_config()
    conf.set('config', 'INIT_SEQ', "0, 12")
    conf.set('config', 'LEAD_SEQ_MAX', 24)
    conf.set('config', 'LEAD_SEQ_MIN', 10)
    test_seq = util.get_lead_sequence(conf, input_dict)
    lead_seq = [ 12, 24 ]
    assert(test_seq == lead_seq)

@pytest.mark.parametrize(
    'key, value', [
        ('1m', datetime.datetime(2019, 3, 1, 0) ),
        ('-1m', datetime.datetime(2019, 1, 1, 0) ),
        ('1Y', datetime.datetime(2020, 2, 1, 0) ),
        ('-1Y', datetime.datetime(2018, 2, 1, 0) ),
        ('1d', datetime.datetime(2019, 2, 2, 0) ),
        ('-1d', datetime.datetime(2019, 1, 31, 0) ),
        ('1H', datetime.datetime(2019, 2, 1, 1) ),
        ('-1H', datetime.datetime(2019, 1, 31, 23) ),
        ('1M', datetime.datetime(2019, 2, 1, 0, 1) ),
        ('-1M', datetime.datetime(2019, 1, 31, 23, 59) ),
        ('1S', datetime.datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1S', datetime.datetime(2019, 1, 31, 23, 59, 59) ),
        ('1', datetime.datetime(2019, 2, 1, 0, 0, 1) ),
        ('-1', datetime.datetime(2019, 1, 31, 23, 59, 59) ),
        ('393d', datetime.datetime(2020, 2, 29, 0) ), # leap year
    ]
)
def test_get_relativedelta(key, value):
    # start time is 2019-02-01_0Z
    start_time = datetime.datetime(2019, 2, 1, 0)
    assert(start_time + util.get_relativedelta(key) == value)
