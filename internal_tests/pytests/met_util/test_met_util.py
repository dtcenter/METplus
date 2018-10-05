#!/usr/bin/env python
from __future__ import print_function
import sys
import pytest
import met_util as util
import produtil
import os
import config_metplus

@pytest.fixture
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
    conf = metplus_config()
    dictionary = dict()
    util.add_common_items_to_dictionary(conf, dictionary)
    assert(dictionary['WGRIB2'] == conf.getexe('WGRIB2'))


def test_threshold_gt():
    thresh_list = {"gt2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ge():
    thresh_list = {"ge2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_eq():
    thresh_list = {"eq2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ne():
    thresh_list = {"ne2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_lt():
    thresh_list = {"lt2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_le():
    thresh_list = {"le2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_gt_symbol():
    thresh_list = {">2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ge_symbol():
    thresh_list = {">=2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_eq_symbol():
    thresh_list = {"==2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_ne_symbol():
    thresh_list = {"!=2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_lt_symbol():
    thresh_list = {"<2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_le_symbol():
    thresh_list = {"<=2.3"}
    assert(util.validate_thresholds(thresh_list))

def test_threshold_gt_no_number():
    thresh_list = {"gta"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_just_number():
    thresh_list = {"2.3"}
    assert(util.validate_thresholds(thresh_list) == False)

def test_threshold_only_one_fails():
    thresh_list = {"<=2.3", "2.4", "gt2.7"}
    assert(util.validate_thresholds(thresh_list) == False)


    
