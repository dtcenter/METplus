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
def test_run_all_times_valid_output_created():
    # Verify that you have created some output in the output dir

    # Create a StatAnalysisWrapper object to invoke the methods.
    st = stat_analysis_wrapper()
    stat_analysis_out_dir = st.p.getdir('STAT_ANALYSIS_OUT_DIR')
    st.run_all_times()

    # Check final output directory for files
    #
    files_in_dir = []
    for dirpath, dirnames, files in os.walk(stat_analysis_out_dir):
        for name in files:
            files_in_dir.append(name)

    # If empty list, assert is False and test fails.
    assert files_in_dir

def test_run_all_times_valid_check_file():
    # Check for a specific file that have expected file size

    # Create a StatAnalysisWrapper object to invoke the methods.
    st = stat_analysis_wrapper()
    stat_analysis_out_dir = st.p.getdir('STAT_ANALYSIS_OUT_DIR')
    st.run_all_times()

    # Get output
    files_in_dir = []
    for dirpath, dirnames, files in os.walk(stat_analysis_out_dir):
        for name in files:
            files_in_dir.append(os.path.join(dirpath, name))    
 
    # Get run info
    truth_file_dir =  "/scratch4/NCEPDEV/global/save/Mallory.Row/VRFY/myMETplus_stuff/data_for_pytests"
    verif_case = st.p.getstr('config', 'VERIF_CASE')
    verif_type = st.p.getstr('config', 'VERIF_TYPE')
    var_name = st.p.getstr('config', 'FCST_VAR1_NAME')
    var_level_list = util.getlist(st.p.getstr('config', 'FCST_VAR1_LEVELS'))
    model_list = util.getlist(st.p.getstr('config', 'MODEL_LIST'))
    lead_list = util.getlist(st.p.getstr('config', 'LEAD_LIST'))
    region_list = util.getlist(st.p.getstr('config', 'REGION_LIST'))
    fourier_wv1_list = []
    if verif_case == 'grid2grid':
       loop_beg = st.p.getint('config', 'VALID_BEG')
       loop_end = st.p.getint('config', 'VALID_END')
       loop_inc = st.p.getint('config', 'VALID_INC')
       fourier_wv1_list.append("NONE")
       if verif_type == "anom" and var_name == "HGT":
          fourier_decomp_height = st.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
          if fourier_decomp_height:
              wave_num_beg_list = util.getlist(st.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
              wave_num_end_list = util.getlist(st.p.getstr('config', 'WAVE_NUM_END_LIST'))
              for wn in range(len(wave_num_beg_list)):
                  wb = wave_num_beg_list[wn]
                  we = wave_num_end_list[wn]
                  wave_num_pairing = "WV1_"+wb+"-"+we
                  fourier_wv1_list.append(wave_num_pairing)
    elif verif_case == 'grid2obs':
       loop_beg = st.p.getint('config', 'INIT_BEG')
       loop_end = st.p.getint('config', 'INIT_END')
       loop_inc = st.p.getint('config', 'INIT_INC')
       fourier_wv1_list.append("NONE")
    loop_hour = loop_beg
    while loop_hour <= loop_end:
        for model in model_list:
            for region in region_list:
                for lead in lead_list:
                     for var_level in var_level_list:
                         for fourier_wv1 in fourier_wv1_list:
                             if fourier_wv1 == "NONE":
                                  test_file = os.path.join(stat_analysis_out_dir, str(loop_hour).zfill(2)+"Z", model, region, model+"_f"+lead.zfill(2)+"_fcst"+var_name+var_level+"_obs"+var_name+var_level+".stat")
                                  truth_file = os.path.join(truth_file_dir, verif_case, "plot_format_data", verif_type, str(loop_hour).zfill(2)+"Z", model, region, model+"_f"+lead.zfill(2)+"_fcst"+var_name+var_level+"_obs"+var_name+var_level+".stat")
                             else:
                                  test_file = os.path.join(stat_analysis_out_dir, str(loop_hour).zfill(2)+"Z", model, region, model+"_f"+lead.zfill(2)+"_fcst"+var_name+var_level+"_obs"+var_name+var_level+"_"+fourier_wv1+".stat")
                                  truth_file = os.path.join(truth_file_dir, verif_case, "plot_format_data", verif_type, str(loop_hour).zfill(2)+"Z", model, region, model+"_f"+lead.zfill(2)+"_fcst"+var_name+var_level+"_obs"+var_name+var_level+"_"+fourier_wv1+".stat")
                             if test_file in files_in_dir:
                                 # if the filesize for this specific file and init and valid times in the
                                 # test config file do not match what is expected, test fails.
                                 assert os.path.getsize(test_file) == os.path.getsize(truth_file) 
        loop_hour+=loop_inc
