#!/usr/bin/env python3

import pytest

import os

import glob

from metplus.wrappers.stat_analysis_wrapper import StatAnalysisWrapper
from metplus.util import handle_tmp_dir

METPLUS_BASE = os.getcwd().split('/internal_tests')[0]


def stat_analysis_wrapper(metplus_config):
    """! Returns a default StatAnalysisWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty StatAnalysisWrapper with some configuration values set
    # to /path/to:
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'test_plotting.conf'))
    config = metplus_config(extra_configs)
    handle_tmp_dir(config)
    return StatAnalysisWrapper(config)


@pytest.mark.plotting
def test_set_lists_as_loop_or_group(metplus_config):
    # Independently test that the lists that are set
    # in the config file are being set
    # accordingly based on their place
    # in GROUP_LIST_ITEMS and LOOP_LIST_ITEMS
    # and those not set are set to GROUP_LIST_ITEMS
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_lists_to_group_items = ['FCST_INIT_HOUR_LIST',
                                     'FCST_UNITS_LIST', 'OBS_UNITS_LIST',
                                     'FCST_THRESH_LIST', 'OBS_THRESH_LIST',
                                     'DESC_LIST', 'OBS_LEAD_LIST',
                                     'OBS_VALID_HOUR_LIST',
                                     'OBS_INIT_HOUR_LIST',
                                     'INTERP_MTHD_LIST', 'INTERP_PNTS_LIST',
                                     'COV_THRESH_LIST', 'ALPHA_LIST',
                                     'LINE_TYPE_LIST']
    expected_lists_to_loop_items = ['FCST_VALID_HOUR_LIST', 'MODEL_LIST',
                                    'FCST_VAR_LIST', 'OBS_VAR_LIST',
                                    'FCST_LEVEL_LIST', 'OBS_LEVEL_LIST',
                                    'FCST_LEAD_LIST', 'VX_MASK_LIST']

    config_dict = {}
    config_dict['LOOP_ORDER'] = 'processes'
    config_dict['OUTPUT_BASE_DIR'] = 'OUTPUT_BASE/stat_analysis'
    config_dict['GROUP_LIST_ITEMS'] = ['FCST_INIT_HOUR_LIST']
    config_dict['LOOP_LIST_ITEMS'] = ['FCST_VALID_HOUR_LIST']
    config_dict['FCST_VAR_LIST'] = ['HGT']
    config_dict['OBS_VAR_LIST'] = ['HGT']
    config_dict['FCST_LEVEL_LIST'] = ['P1000', 'P500']
    config_dict['OBS_LEVEL_LIST'] = ['P1000', 'P500']
    config_dict['FCST_UNITS_LIST'] = []
    config_dict['OBS_UNITS_LIST'] = []
    config_dict['FCST_THRESH_LIST'] = []
    config_dict['OBS_THRESH_LIST'] = []
    config_dict['MODEL_LIST'] = ['MODEL_TEST1', 'MODEL_TEST2']
    config_dict['DESC_LIST'] = []
    config_dict['FCST_LEAD_LIST'] = ['24', '48']
    config_dict['OBS_LEAD_LIST'] = []
    config_dict['FCST_VALID_HOUR_LIST'] = ['00', '06', '12', '18']
    config_dict['FCST_INIT_HOUR_LIST'] = ['00', '06', '12', '18']
    config_dict['OBS_VALID_HOUR_LIST'] = []
    config_dict['OBS_INIT_HOUR_LIST'] = []
    config_dict['VX_MASK_LIST'] = ['NHX']
    config_dict['INTERP_MTHD_LIST'] = []
    config_dict['INTERP_PNTS_LIST'] = []
    config_dict['COV_THRESH_LIST'] = []
    config_dict['ALPHA_LIST'] = []
    config_dict['LINE_TYPE_LIST'] = ['SL1L2', 'VL1L2']

    config_dict = st.set_lists_loop_or_group(config_dict)

    test_lists_to_loop_items = config_dict['LOOP_LIST_ITEMS']
    test_lists_to_group_items = config_dict['GROUP_LIST_ITEMS']

    assert (all(elem in expected_lists_to_group_items
                for elem in test_lists_to_group_items))
    assert (all(elem in expected_lists_to_loop_items
                for elem in test_lists_to_loop_items))


@pytest.mark.plotting
def test_get_output_filename(metplus_config):
    # Independently test the building of
    # the output file name
    # using string template substitution#
    # and test the values is
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '000000'
    config_dict['FCST_VAR'] = '"HGT"'
    config_dict['FCST_LEVEL'] = '"P1000"'
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = '"NHX"'
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = '"HGT"'
    config_dict['FCST_INIT_HOUR'] = '"000000", "060000", "120000", "180000"'
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = '"240000"'
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] = '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = '"P1000"'
    st.c_dict['DATE_BEG'] = '20190101'
    st.c_dict['DATE_END'] = '20190101'
    st.c_dict['DATE_TYPE'] = 'VALID'

    # Test 1
    lists_to_group = ['FCST_INIT_HOUR_LIST', 'FCST_UNITS_LIST',
                      'OBS_UNITS_LIST', 'FCST_THRESH_LIST',
                      'OBS_THRESH_LIST', 'DESC_LIST', 'OBS_LEAD_LIST',
                      'OBS_VALID_HOUR_LIST', 'OBS_INIT_HOUR_LIST',
                      'INTERP_MTHD_LIST', 'INTERP_PNTS_LIST',
                      'COV_THRESH_LIST', 'ALPHA_LIST', 'LINE_TYPE_LIST']
    lists_to_loop = ['FCST_VALID_HOUR_LIST', 'MODEL_LIST',
                     'FCST_VAR_LIST', 'OBS_VAR_LIST',
                     'FCST_LEVEL_LIST', 'OBS_LEVEL_LIST',
                     'FCST_LEAD_LIST', 'VX_MASK_LIST']
    expected_output_filename = (
            'MODEL_TEST_MODEL_TEST_ANL_valid20190101to20190101_valid0000to0000Z'
            + '_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
            + '_dump_row.stat'
    )
    output_type = 'dump_row'
    filename_template = (
        '{model?fmt=%s}_{obtype?fmt=%s}_valid{valid_beg?fmt=%Y%m%d}'
        'to{valid_end?fmt=%Y%m%d}_valid{valid_hour_beg?fmt=%H%M}to'
        '{valid_hour_end?fmt=%H%M}Z_init{init_hour_beg?fmt=%H%M}to'
        '{init_hour_end?fmt=%H%M}Z_fcst_lead{fcst_lead?fmt=%s}_'
        'fcst{fcst_var?fmt=%s}{fcst_level?fmt=%s}{fcst_thresh?fmt=%s}'
        '{interp_mthd?fmt=%s}_obs{obs_var?fmt=%s}{obs_level?fmt=%s}'
        '{obs_thresh?fmt=%s}{interp_mthd?fmt=%s}_vxmask{vx_mask?fmt=%s}'
        '_dump_row.stat'

    )
    filename_type = 'user'
    test_output_filename = st.get_output_filename(output_type,
                                                  filename_template,
                                                  filename_type,
                                                  lists_to_loop,
                                                  lists_to_group,
                                                  config_dict)
    assert expected_output_filename == test_output_filename


@pytest.mark.plotting
def test_filter_for_plotting(metplus_config):
    # Test running of stat_analysis
    st = stat_analysis_wrapper(metplus_config)

    # clear output directory for next run
    output_dir = st.config.getdir('OUTPUT_BASE') + '/plotting/stat_analysis'
    output_files = glob.glob(os.path.join(output_dir, '*'))
    for output_file in output_files:
        os.remove(output_file)

    # Test 1
    expected_filename1 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename2 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename3 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename4 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename5 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename6 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename7 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename8 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename9 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename10 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename11 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename12 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename13 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename14 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename15 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename16 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/MODEL_TEST1_MODEL_TEST1_ANL_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename17 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename18 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename19 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename20 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0000to0000Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename21 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename22 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename23 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename24 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid0600to0600Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename25 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename26 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename27 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename28 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1200to1200Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename29 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename30 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead240000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename31 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP1000_obsHGTP1000_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename32 = (
        st.config.getdir('OUTPUT_BASE')+'/plotting/stat_analysis'
        +'/TEST2_MODEL_ANLYS2_valid20190101to20190101_valid1800to1800Z'
        +'_init0000to1800Z_fcst_lead480000_fcstHGTP850_obsHGTP850_vxmaskNHX'
        +'_dump_row.stat'
    )
    expected_filename_list = [ expected_filename1, expected_filename2,
                               expected_filename3, expected_filename4,
                               expected_filename5, expected_filename6,
                               expected_filename7, expected_filename8,
                               expected_filename9, expected_filename10,
                               expected_filename11, expected_filename12,
                               expected_filename13, expected_filename14,
                               expected_filename15, expected_filename16,
                               expected_filename17, expected_filename18,
                               expected_filename19, expected_filename20,
                               expected_filename21, expected_filename22,
                               expected_filename23, expected_filename24,
                               expected_filename25, expected_filename26,
                               expected_filename27, expected_filename28,
                               expected_filename29, expected_filename30,
                               expected_filename31, expected_filename32 ]
    st.c_dict['DATE_TYPE'] = 'VALID'
    st.c_dict['VALID_BEG'] = '20190101'
    st.c_dict['VALID_END'] = '20190101'
    st.c_dict['INIT_BEG'] = ''
    st.c_dict['INIT_END'] = ''
    st.c_dict['DATE_BEG'] = st.c_dict['VALID_BEG']
    st.c_dict['DATE_END'] = st.c_dict['VALID_END']

    st.run_stat_analysis()
    ntest_files = len(
        os.listdir(st.config.getdir('OUTPUT_BASE')
                                    +'/plotting/stat_analysis')
    )
    assert ntest_files == 32
    for expected_filename in expected_filename_list:
        assert os.path.exists(expected_filename)
