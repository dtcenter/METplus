#!/usr/bin/env python
from __future__ import print_function
import os
import config_metplus
import datetime
import sys
import logging
import pytest
from stat_analysis_wrapper import StatAnalysisWrapper
import met_util as util
import produtil.setup

#
# These are tests (not necessarily unit tests) for the
# MET stat_analysis wrapper, stat_analysis_wrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  stat_analysis_test.conf.  This contains
# the information necessary for running all the tests.  Each test can be
# customized to replace various settings if needed.
#

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")

#
# ------------Pytest fixtures that can be used for all tests ---------------
#
@pytest.fixture
def stat_analysis_wrapper():
    """! Returns a default StatAnalysisWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty PointStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return StatAnalysisWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='StatAnalysisWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='StatAnalysisWrapper ')
        produtil.log.postmsg('stat_analysis_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'stat_analysis_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------TESTS GO BELOW ---------------------------
#

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# To test numerous files for filesize, use parametrization:
# @pytest.mark.parametrize(
#     'key, value', [
#         ('/usr/local/met-6.1/bin/point_stat', 382180),
#         ('/usr/local/met-6.1/bin/stat_analysis', 3438944),
#         ('/usr/local/met-6.1/bin/pb2nc', 3009056)
#
#     ]
# )
# def test_file_sizes(key, value):
#     st = stat_analysis_wrapper()
#     # Retrieve the value of the class attribute that corresponds
#     # to the key in the parametrization
#     files_in_dir = []
#     for dirpath, dirnames, files in os.walk("/usr/local/met-6.1/bin"):
#         for name in files:
#             files_in_dir.append(os.path.join(dirpath, name))
#         if actual_key in files_in_dir:
#         # The actual_key is one of the files of interest we retrieved from
#         # the output directory.  Verify that it's file size is what we
#         # expected.
#             assert actual_key == key
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def test_run_at_time_valid_output_created():
    # Verify that you have created some output in the output dir

    init_time = -1
    valid_time = '201706010000'

    # Create a StatAnalysisWrapper object to invoke the methods.
    st = stat_analysis_wrapper()
    stat_analysis_out_dir = st.p.getdir('STAT_ANALYSIS_OUT_DIR')
    st.run_at_time(init_time, valid_time)

    # Check final output directory for files
    #
    files_in_dir = []
    for dirpath, dirnames, files in os.walk(stat_analysis_out_dir):
        for name in files:
            files_in_dir.append(name)

    # If empty list, assert is False and test fails.
    assert files_in_dir

def test_run_at_time_valid_check_file():
    # Check for a specific file that have expected file size

    init_time = -1
    valid_time = '201706010000'

    # Create a StatAnalysisWrapper object to invoke the methods.
    st = stat_analysis_wrapper()
    stat_analysis_out_dir = st.p.getdir('STAT_ANALYSIS_OUT_DIR')
    st.run_at_time(init_time, valid_time)
 
    # Test file info
    model_type = st.p.getstr('config', 'MODEL_TYPE')
    filter_time = valid_time
    date_YYYYMMDD = filter_time[0:8]
    cycle = filter_time[8:10]
    verif_case = st.p.getstr('config', 'VERIF_CASE')
    verif_type = st.p.getstr('config', 'VERIF_TYPE')
    #grid-to-grid checking valid at 'date_YYYYMMDD' at 'cycle'
    #grid-to-obs checking valid on 'date_YYYYMMDD' model intialized at 'cycle'
    test_file = os.path.join(stat_analysis_out_dir, cycle+"Z", model_type, model_type+"_"+date_YYYYMMDD+".stat")

    # Truth file info 
    truth_file_dir =  "/scratch4/NCEPDEV/global/save/Mallory.Row/VRFY/myMETplus_stuff/data_for_pytests"
    truth_file = os.path.join(truth_file_dir, verif_case, "VSDB_format", verif_type, cycle+"Z", model_type, model_type+"_"+date_YYYYMMDD+".stat")
    
    # Check final output directory for particular file with the correct
    # file size.
    #
    files_in_dir = []
    for dirpath, dirnames, files in os.walk(stat_analysis_out_dir):
        for name in files:
            files_in_dir.append(os.path.join(dirpath, name))
    if test_file in files_in_dir:
        # if the filesize for this specific file and init and valid times in the
        # test config file do not match what is expected, test fails.
        assert os.path.getsize(test_file) == os.path.getsize(truth_file) 
