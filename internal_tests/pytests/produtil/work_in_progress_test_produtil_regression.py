#!/usr/bin/env python3

import os
import subprocess
import produtil
import sys
import logging
import pytest
import config_metplus
import config_launcher as launcher
import met_util as util


#
# These are tests (not necessarily unit tests) for the
# MET Point-Stat Wrapper, PointStatWrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  point_stat_test.conf.  This contains
# the information necessary for running all the tests.  Each test can be
# customized to replace various settings if needed.
#

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
# def pytest_addoption(parser):
#     parser.addoption("-c", action="store", help=" -c <test config file>")
#
#
# # @pytest.fixture
# def cmdopt(request):
#     return request.config.getoption("-c")


# ------------------------

def dummy():
    assert(True)


def get_config_obj():
    """! Create the configuration object that is used by all tests"""
    file_list = ["METplus/internal_tests/pytests/produtil"]
    config_obj = config_metplus.setup(file_list[0])

    return config_obj


def test_getstr_ok(regtest):
    """! Test that the expected string is retrieved via produtil's getstr
           method
    """
    conf_obj = get_config_obj()
    str_value = conf_obj.getstr('config', 'STRING_VALUE')
    expected_str_value = "someStringValue!#@$%"
    # print(str_value, file=regtest)
    regtest.write("done")
#
#
# def test_getint_ok(regtest):
#     """! Test that the expected int in the produtil_test.conf file has been
#             retrieved correctly.
#     """
#     conf_obj = get_config_obj()
#     expected_int_value = int(2908887)
#     int_value = conf_obj.getint('config', 'INT_VALUE')
#     # print(int_value, file=regtest)
#     regtest.write("done")
#
#
# def test_getraw_ok(regtest):
#     """! Test that the raw value in the produtil_test.conf file has been
#             retrieved correctly.
#     """
#     conf_obj = get_config_obj()
#     expected_raw = 'GRIB_lvl_type = 100'
#     raw_value = conf_obj.getraw('config', 'RAW_VALUE')
#     # print(raw_value, file=regtest)
#     # regtest.write("done")
#
#
# def test_getdir_ok(regtest):
#     """! Test that the directory in the produtil_test.conf file has been
#            correctly retrieved.
#     """
#     conf_obj = get_config_obj()
#     expected_dir = "/tmp/some_dir"
#     dir_retrieved = conf_obj.getdir('DIR_VALUE')
#     # print(dir_retrieved, file=regtest)
#
#
# def test_getdir_compound_ok(regtest):
#     """! Test that directories created from other directories, ie.
#             BASE_DIR = /base/dir
#             SPECIFIC_DIR = {BASE_DIR}/specific/dir
#
#             correctly returns the directory path for SPECIFIC_DIR
#     """
#     expected_specific_dir = "/tmp/specific_place"
#     conf_obj = get_config_obj()
#     specific_dir = conf_obj.getdir('SPECIFIC_DIR')
#     print(specific_dir, file=regtest)
#
#
# def test_no_value_as_string(regtest):
#     """! Tests that a key with no value returns an empty string."""
#
#     conf_obj = get_config_obj()
#     expected_unassigned = ''
#     unassigned = conf_obj.getstr('config', 'UNASSIGNED_VALUE')
#     # print(unassigned, file=regtest)
#
#
# def test_no_value_as_list(regtest):
#     """! Tests that a key with no list of strings returns an empty list."""
#
#     conf_obj = get_config_obj()
#     expected_unassigned = []
#     unassigned = util.getlist(conf_obj.getstr('config', 'UNASSIGNED_VALUE'))
#     assert unassigned == expected_unassigned
#     # print(unassigned, file=regtest)
#
#
# def test_new_lines_in_conf(regtest):
#     """! Test that any newlines in the configuration file are handled
#            properly
#     """
#
#     conf_obj = get_config_obj()
#     expected_string = \
#         "very long line requiring newline character to be tested 12345\n67890 end of the line."
#     long_line = conf_obj.getstr('config', 'NEW_LINES')
#     assert long_line == expected_string
#     # print(long_line, file=regtest)
#
#
# def test_get_exe_ok(regtest):
#     """! Test that executables are correctly retrieved."""
#     conf_obj = get_config_obj()
#     expected_exe = '/usr/local/bin/wgrib2'
#     executable = conf_obj.getexe('WGRIB2')
#     assert executable == expected_exe
#     # print(executable, file=regtest)
#
#
# def test_get_bool(regtest):
#     """! Test that boolean values are correctly retrieved."""
#     conf_obj = get_config_obj()
#     bool_val = conf_obj.getbool('config', 'BOOL_VALUE')
#     assert bool_val is True
#     # print(bool_val, file=regtest)
#
