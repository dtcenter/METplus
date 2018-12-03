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

def test_get_number_from_threshold_gt():
    assert(util.get_number_from_threshold("gt4.5") == 4.5)

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

def test_decompress_file_gz():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile.txt.gz"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile.txt"
    outpath = util.decompress_file(filepath, stage_dir)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_decompress_file_bz2():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile2.txt.bz2"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile2.txt"
    outpath = util.decompress_file(filepath, stage_dir)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_decompress_file_zip():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile3.txt.zip"
    stagepath = stage_dir + conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile3.txt"
    outpath = util.decompress_file(filepath, stage_dir)
    assert(stagepath == outpath and os.path.exists(outpath))

def test_decompress_file_unzipped():
    conf = metplus_config()
    stage_dir = conf.getdir('STAGING_DIR', os.path.join(conf.getdir('OUTPUT_BASE'),"stage"))
    filepath = conf.getdir('METPLUS_BASE')+"/internal_tests/data/zip/testfile4.txt"
    outpath = util.decompress_file(filepath, stage_dir)
    assert(filepath == outpath and os.path.exists(outpath))
