#!/usr/bin/env python
from __future__ import print_function
import os
import config_metplus
import datetime
import sys
import logging
import pytest
from make_plots_wrapper import MakePlotsWrapper
import met_util as util
import produtil.setup

#
# These are tests (not necessarily unit tests) for the
# make_plots_wrapper.py
# NOTE:  This test requires pytest, which is NOT part of the standard Python
# library.
# These tests require one configuration file in addition to the three
# required METplus configuration files:  make_plots_test.conf.  This contains
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
def make_plots_wrapper():
    """! Returns a default MakePlotsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty PointStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return MakePlotsWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='MakePlotsWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='MakePlotsWrapper ')
        produtil.log.postmsg('make_plots_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'make_plots_wrapper failed: %s' % (str(e),), exc_info=True)
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
def test_valid_output_created():
    # Verify that you have created some output in the output dir

    # Create a MakePlotsWrapper object to invoke the methods.
    mp = make_plots_wrapper()
    plotting_out_dir = mp.p.getdir('PLOTTING_OUT_DIR')
    mp.run_all_times()

    # Check final output directory for files
    #
    files_in_dir = []
    for dirpath, dirnames, files in os.walk(plotting_out_dir):
        for name in files:
            files_in_dir.append(name)
    # If empty list, assert is False and test fails.
    assert files_in_dir

def test_valid_check_mean_file():
    # Check for a specific file that have expected file size
    
    # Create a MakePlotsWrapper object to invoke the methods.
    mp = make_plots_wrapper()
    plotting_out_dir = mp.p.getdir('PLOTTING_OUT_DIR')
    mp.run_all_times()
    
    # Get test output
    files_in_test_dir = []
    for dirpath, dirnames, files in os.walk(plotting_out_dir):
        for name in files:
            files_in_test_dir.append(os.path.join(dirpath,name))
    files_in_test_dir.sort()

    # Get truth output
    files_in_truth_dir = []
    truth_file_dir =  "/scratch4/NCEPDEV/global/save/Mallory.Row/VRFY/myMETplus_stuff/data_for_pytests"
    verif_case = mp.p.getstr('config', 'VERIF_CASE')
    verif_type = mp.p.getstr('config', 'VERIF_TYPE')
    for dirpath, dirnames, files in os.walk(os.path.join(truth_file_dir, verif_case, "make_plots", verif_type)):
        for name in files:
            files_in_truth_dir.append(os.path.join(dirpath, name))
    files_in_truth_dir.sort()

    # Check number of files is the same, if so check file basenames the same, if so check sizes
    if len(files_in_test_dir) == len(files_in_truth_dir):
        for f in range(len(files_in_test_dir)):
            basename_test = os.path.basename(files_in_test_dir[f])
            basename_truth = os.path.basename(files_in_truth_dir[f])
            if basename_test == basename_truth:
               assert os.path.getsize(files_in_test_dir[f]) ==  os.path.getsize(files_in_truth_dir[f])
            else:
                # Fails if namming of files not the same
                assert True is False
    else:
       # Fails if number of files not the same
       assert True is False
