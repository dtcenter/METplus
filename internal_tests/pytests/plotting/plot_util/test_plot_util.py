#!/usr/bin/env python

import os
import datetime
import sys
import logging
import pytest
import datetime
import numpy as np
import pandas as pd

import produtil.setup

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
METPLUS_BASE = os.getcwd().split('/internal_tests')[0]
sys.path.append(METPLUS_BASE+'/ush/plotting_scripts')
import plot_util
logger = logging.getLogger('~/metplus_pytest_plot_util.log')

def test_get_date_arrays():
    # Independently test the creation of 
    # the date arrays, one used for plotting
    # the other the expected dates in the
    # MET .stat file format
    # Test 1
    date_type = 'VALID'
    date_beg = '20190101'
    date_end = '20190105'
    fcst_valid_hour = '000000'
    fcst_init_hour = '000000'
    obs_valid_hour = ''
    obs_init_hour = ''
    lead = '240000'
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(days=i) for i in range(5)]
    )
    expected_plot_time_dates = []
    expected_expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
        expected_plot_time_dates.append(date.toordinal() + seconds/86400.)
        expected_expected_stat_file_dates.append(
            date.strftime('%Y%m%d_%H%M%S')
        )
    test_plot_time_dates, test_expected_stat_file_dates = (
        plot_util.get_date_arrays(date_type, date_beg, date_end,
                                  fcst_valid_hour, fcst_init_hour, 
                                  obs_valid_hour, obs_init_hour, lead)
    )
    assert(len(test_plot_time_dates) ==
            len(expected_plot_time_dates))
    for l in range(len(test_plot_time_dates)):
        assert(test_plot_time_dates[l] ==
                expected_plot_time_dates[l])
    assert(len(test_expected_stat_file_dates) == 
            len(expected_expected_stat_file_dates))
    for l in range(len(test_expected_stat_file_dates)):
        assert(test_expected_stat_file_dates[l] == 
                expected_expected_stat_file_dates[l])
    # Test 2
    date_type = 'VALID'
    date_beg = '20190101'
    date_end = '20190105'
    fcst_valid_hour = '000000, 060000, 120000, 180000'
    fcst_init_hour = '000000, 060000, 120000, 180000'
    obs_valid_hour = ''
    obs_init_hour = ''
    lead = '480000'
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(hours=i) for i in range(0,120,6)]
    )
    expected_plot_time_dates = []
    expected_expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
        expected_plot_time_dates.append(date.toordinal() + seconds/86400.)
        expected_expected_stat_file_dates.append(
            date.strftime('%Y%m%d_%H%M%S')
        )
    test_plot_time_dates, test_expected_stat_file_dates = (
        plot_util.get_date_arrays(date_type, date_beg, date_end,
                                  fcst_valid_hour, fcst_init_hour,
                                  obs_valid_hour, obs_init_hour, lead)
    )
    assert(len(test_plot_time_dates) ==
            len(expected_plot_time_dates))
    for l in range(len(test_plot_time_dates)):
        assert(test_plot_time_dates[l] ==
                expected_plot_time_dates[l])
    assert(len(test_expected_stat_file_dates) ==    
            len(expected_expected_stat_file_dates))
    for l in range(len(test_expected_stat_file_dates)):
        assert(test_expected_stat_file_dates[l] ==    
                expected_expected_stat_file_dates[l])
    # Test 3
    date_type = 'INIT'
    date_beg = '20190101'
    date_end = '20190105'
    fcst_valid_hour = '000000'
    fcst_init_hour = '000000'
    obs_valid_hour = ''
    obs_init_hour = ''
    lead = '360000'
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(days=i) for i in range(5)]
    )
    lead_hour_seconds = int(int(lead[:-4])) * 3600
    lead_min_seconds = int(lead[-4:-2]) * 60
    lead_seconds = int(lead[-2:])
    lead_offset = datetime.timedelta(
        seconds=lead_hour_seconds + lead_min_seconds + lead_seconds
    )
    expected_plot_time_dates = []
    expected_expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
        expected_plot_time_dates.append(date.toordinal() + seconds/86400.)
        expected_expected_stat_file_dates.append(
            (date + lead_offset).strftime('%Y%m%d_%H%M%S')
        )
    test_plot_time_dates, test_expected_stat_file_dates = (
        plot_util.get_date_arrays(date_type, date_beg, date_end,
                                  fcst_valid_hour, fcst_init_hour,
                                  obs_valid_hour, obs_init_hour, lead)
    )
    assert(len(test_plot_time_dates) ==
            len(expected_plot_time_dates))
    for l in range(len(test_plot_time_dates)):
        assert(test_plot_time_dates[l] ==
                expected_plot_time_dates[l])
    assert(len(test_expected_stat_file_dates) ==    
            len(expected_expected_stat_file_dates))
    for l in range(len(test_expected_stat_file_dates)):
        assert(test_expected_stat_file_dates[l] ==    
                expected_expected_stat_file_dates[l])
    # Test 4
    date_type = 'INIT'
    date_beg = '20190101'
    date_end = '20190105'
    fcst_valid_hour = '000000, 060000, 120000, 180000'
    fcst_init_hour = '000000, 060000, 120000, 180000'
    obs_valid_hour = ''
    obs_init_hour = ''
    lead = '120000'
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(hours=i) for i in range(0,120,6)]
    )
    lead_hour_seconds = int(int(lead[:-4])) * 3600
    lead_min_seconds = int(lead[-4:-2]) * 60
    lead_seconds = int(lead[-2:])
    lead_offset = datetime.timedelta(
        seconds=lead_hour_seconds + lead_min_seconds + lead_seconds
    )
    expected_plot_time_dates = []
    expected_expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
        expected_plot_time_dates.append(date.toordinal() + seconds/86400.)
        expected_expected_stat_file_dates.append(
            (date + lead_offset).strftime('%Y%m%d_%H%M%S')
        )
    test_plot_time_dates, test_expected_stat_file_dates = (
        plot_util.get_date_arrays(date_type, date_beg, date_end,
                                  fcst_valid_hour, fcst_init_hour,
                                  obs_valid_hour, obs_init_hour, lead)
    )
    assert(len(test_plot_time_dates) ==
            len(expected_plot_time_dates))
    for l in range(len(test_plot_time_dates)):
        assert(test_plot_time_dates[l] ==
                expected_plot_time_dates[l])
    assert(len(test_expected_stat_file_dates) ==    
            len(expected_expected_stat_file_dates))
    for l in range(len(test_expected_stat_file_dates)):
        assert(test_expected_stat_file_dates[l] ==    
                expected_expected_stat_file_dates[l])

def test_format_thresh():
    # Independently test the formatting
    # of thresholds
    # Test 1
    thresh = '>=5'
    expected_thresh_symbol = '>=5'
    expected_thresh_letter = 'ge5'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 2
    thresh = 'ge5'
    expected_thresh_symbol = '>=5'
    expected_thresh_letter = 'ge5'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 3
    thresh = '>15'
    expected_thresh_symbol = '>15'
    expected_thresh_letter = 'gt15'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 4
    thresh = 'gt15'
    expected_thresh_symbol = '>15'
    expected_thresh_letter = 'gt15'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 5
    thresh = '==1'
    expected_thresh_symbol = '==1'
    expected_thresh_letter = 'eq1'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 6
    thresh = 'eq1'
    expected_thresh_symbol = '==1'
    expected_thresh_letter = 'eq1'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 7
    thresh = '!=0.5'
    expected_thresh_symbol = '!=0.5'
    expected_thresh_letter = 'ne0.5'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 8
    thresh = 'ne0.5'
    expected_thresh_symbol = '!=0.5'
    expected_thresh_letter = 'ne0.5'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 9
    thresh = '<=1000'
    expected_thresh_symbol = '<=1000'
    expected_thresh_letter = 'le1000'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 10
    thresh = 'le1000'
    expected_thresh_symbol = '<=1000'
    expected_thresh_letter = 'le1000'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 11
    thresh = '<0.001'
    expected_thresh_symbol = '<0.001'
    expected_thresh_letter = 'lt0.001'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)
    # Test 12
    thresh = 'lt0.001'
    expected_thresh_symbol = '<0.001'
    expected_thresh_letter = 'lt0.001'
    test_thresh_symbol, test_thresh_letter = plot_util.format_thresh(thresh)
    assert(test_thresh_symbol == expected_thresh_symbol)
    assert(test_thresh_letter == expected_thresh_letter)

def test_get_stat_file_base_columns():
    # Independently test getting list
    # of the base MET version .stat file columns
    # Test 1
    met_version = '8.0'
    expected_stat_file_base_columns = [ 'VERSION', 'MODEL', 'DESC',
                                        'FCST_LEAD', 'FCST_VALID_BEG',
                                        'FCST_VALID_END', 'OBS_LEAD',
                                        'OBS_VALID_BEG', 'OBS_VALID_END',
                                        'FCST_VAR', 'FCST_LEV', 'OBS_VAR',
                                        'OBS_LEV', 'OBTYPE', 'VX_MASK',
                                        'INTERP_MTHD', 'INTERP_PNTS',
                                        'FCST_THRESH', 'OBS_THRESH',
                                        'COV_THRESH', 'ALPHA', 'LINE_TYPE' ]
    test_stat_file_base_columns = plot_util.get_stat_file_base_columns(
        met_version
    )
    assert(test_stat_file_base_columns == expected_stat_file_base_columns)
    # Test 2
    met_version = '8.1'
    expected_stat_file_base_columns = [ 'VERSION', 'MODEL', 'DESC',
                                        'FCST_LEAD', 'FCST_VALID_BEG',
                                        'FCST_VALID_END', 'OBS_LEAD',
                                        'OBS_VALID_BEG', 'OBS_VALID_END',
                                        'FCST_VAR', 'FCST_UNITS', 'FCST_LEV',
                                        'OBS_VAR', 'OBS_UNITS', 'OBS_LEV',
                                        'OBTYPE', 'VX_MASK', 'INTERP_MTHD', 
                                        'INTERP_PNTS', 'FCST_THRESH',
                                        'OBS_THRESH', 'COV_THRESH', 'ALPHA',
                                        'LINE_TYPE' ]
    test_stat_file_base_columns = plot_util.get_stat_file_base_columns(
        met_version
    )
    assert(test_stat_file_base_columns == expected_stat_file_base_columns)

def test_get_stat_file_line_type_columns():
    # Independently test getting list
    # of the line type MET version .stat file columns
    # Test 1
    met_version = '8.1'
    line_type = 'SL1L2'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'FBAR', 'OBAR', 'FOBAR',
                                             'FFBAR', 'OOBAR', 'MAE' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)
    # Test 2
    met_version = '8.1'
    line_type = 'SAL1L2'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'FABAR', 'OABAR',
                                             'FOABAR', 'FFABAR', 'OOABAR',
                                             'MAE' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)
    # Test 3
    met_version = '6.1'
    line_type = 'VL1L2'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'UFBAR', 'VFBAR',
                                             'UOBAR', 'VOBAR', 'UVFOBAR',
                                             'UVFFBAR', 'UVOOBAR' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)
    # Test 4
    met_version = '8.1'
    line_type = 'VL1L2'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'UFBAR', 'VFBAR',
                                             'UOBAR', 'VOBAR', 'UVFOBAR',
                                             'UVFFBAR', 'UVOOBAR',
                                             'F_SPEED_BAR', 'O_SPEED_BAR' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)
    # Test 5
    met_version = '8.1'
    line_type = 'VAL1L2'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'UFABAR', 'VFABAR',
                                             'UOABAR', 'VOABAR', 'UVFOABAR',
                                             'UVFFABAR', 'UVOOABAR' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    # Test 6
    met_version = '8.1'
    line_type = 'VCNT'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'FBAR', 'FBAR_NCL',
                                             'FBAR_NCU', 'OBAR', 'OBAR_NCL',
                                             'OBAR_NCU', 'FS_RMS',
                                             'FS_RMS_NCL', 'FS_RMS_NCU',
                                             'OS_RMS', 'OS_RMS_NCL',
                                             'OS_RMS_NCU', 'MSVE', 'MSVE_NCL',
                                             'MSVE_NCU', 'RMSVE', 'RMSVE_NCL',
                                             'RMSVE_NCU', 'FSTDEV',
                                             'FSTDEV_NCL', 'FSTDEV_NCU',
                                             'OSTDEV', 'OSTDEV_NCL',
                                             'OSTDEV_NCU', 'FDIR', 'FDIR_NCL',
                                             'FDIR_NCU', 'ODIR', 'ODIR_NCL',
                                             'ODIR_NCU', 'FBAR_SPEED',
                                             'FBAR_SPEED_NCL',
                                             'FBAR_SPEED_NCU', 'OBAR_SPEED',
                                             'OBAR_SPEED_NCL',
                                             'OBAR_SPEED_NCU', 'VDIFF_SPEED',
                                             'VDIFF_SPEED_NCL',
                                             'VDIFF_SPEED_NCU', 'VDIFF_DIR',
                                             'VDIFF_DIR_NCL', 'VDIFF_DIR_NCU',
                                             'SPEED_ERR', 'SPEED_ERR_NCL',
                                             'SPEED_ERR_NCU', 'SPEED_ABSERR',
                                             'SPEED_ABSERR_NCL',
                                             'SPEED_ABSERR_NCU', 'DIR_ERR',
                                             'DIR_ERR_NCL', 'DIR_ERR_NCU',
                                             'DIR_ABSERR', 'DIR_ABSERR_NCL',
                                             'DIR_ABSERR_NCU' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)
    # Test 7
    met_version = '8.1'
    line_type = 'CTC'
    expected_stat_file_line_type_columns = [ 'TOTAL', 'FY_OY', 'FY_ON',
                                             'FN_OY', 'FN_ON' ]
    test_stat_file_line_type_columns = (
        plot_util.get_stat_file_line_type_columns(logger, met_version,
                                                  line_type)
    )
    assert(test_stat_file_line_type_columns ==
            expected_stat_file_line_type_columns)

def get_clevels():
    # Independently test creating an array
    # of levels centered about 0 to plot
    # Test 1
    data = np.array([ 7.89643761, 2.98214969, 4.04690632, 1.1047872,
                      -3.42288272, 1.0111309, 8.02330262, -8.03515159,
                      -8.89454837, 2.45191295, 9.43015692, -0.53815455,
                      4.34984478, 4.54528989, -1.35164646 ])
    expected_clevels = np.array([-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10])
    test_clevels = plot_util.get_clevels(data)
    assert(test_clevels == expected_clevels)

def test_calculate_average():
    # Independently test getting the average
    # of a data array based on method
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(days=i) for i in range(5)]
    )
    expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        expected_stat_file_dates.append(
            date.strftime('%Y%m%d_%H%M%S')
        )
    model_data_index = pd.MultiIndex.from_product(
            [['MODEL_TEST'], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
    )
    model_data_array = np.array([
        [3600, 5525.75062, 5525.66493, 30615218.26089, 30615764.49722,
         30614724.90979, 5.06746],
        [3600, 5519.11108, 5519.1014, 30549413.45946, 30549220.68868,
         30549654.24048, 5.12344],
        [3600, 5516.80228, 5516.79513, 30522742.16484, 30522884.89927,
         30522660.30975, 5.61752],
        [3600, 5516.93924, 5517.80544, 30525709.03932, 30520984.50965,
         30530479.99675, 4.94325],
        [3600, 5514.52274, 5514.68224, 30495695.82208, 30494633.24046,
         30496805.48259, 5.20369]
    ])
    model_data = pd.DataFrame(model_data_array, index=model_data_index,
                              columns=[ 'TOTAL', 'FBAR', 'OBAR', 'FOBAR',
                                        'FFBAR', 'OOBAR', 'MAE' ])
    stat_values_array = np.array([[[(5525.75062 - 5525.66493),
                                    (5519.11108 - 5519.1014),
                                    (5516.80228 - 5516.79513),
                                    (5516.93924 - 5517.80544),
                                    (5514.52274 - 5514.68224)
                                  ]]])
    # Test 1
    average_method = 'MEAN'
    stat = 'bias'
    model_dataframe = model_data
    model_stat_values = stat_values_array[:,0,:]
    expected_average_array = np.array([-0.184636])
    test_average_array = plot_util.calculate_average(logger, average_method,
                                                     stat, model_dataframe,
                                                     model_stat_values)
    assert(len(test_average_array) == len(expected_average_array))
    for l in range(len(test_average_array)):
        assert(round(test_average_array[l],6) == expected_average_array[l])
    # Test 2
    average_method = 'MEDIAN'
    stat = 'bias'
    model_dataframe = model_data
    model_stat_values = stat_values_array[:,0,:]
    expected_average_array = np.array([0.00715])
    test_average_array = plot_util.calculate_average(logger, average_method,
                                                     stat, model_dataframe,
                                                     model_stat_values)
    assert(len(test_average_array) == len(expected_average_array))
    for l in range(len(test_average_array)):
        assert(round(test_average_array[l],6) == expected_average_array[l])
    # Test 3
    average_method = 'AGGREGATION'
    stat = 'bias'
    model_dataframe = model_data
    model_stat_values = stat_values_array[:,0,:]
    expected_average_array = np.array([-0.184636])
    test_average_array = plot_util.calculate_average(logger, average_method,
                                                     stat, model_dataframe,
                                                     model_stat_values)
    assert(len(test_average_array) == len(expected_average_array))
    for l in range(len(test_average_array)):
        assert(round(test_average_array[l],6) == expected_average_array[l])
    # Test 4
    stat_values_array = np.array([[[5525.75062, 5519.11108,
                                    5516.80228, 5516.93924,
                                    5514.52274]],
                                  [[5525.66493, 5519.1014,
                                    5516.79513, 5517.80544,
                                    5514.68224
                                 ]]])
    average_method = 'MEAN'
    stat = 'fbar_obar'
    model_dataframe = model_data
    model_stat_values = stat_values_array[:,0,:]
    expected_average_array = np.array([5518.625192,5518.809828])
    test_average_array = plot_util.calculate_average(logger, average_method,
                                                     stat, model_dataframe,
                                                     model_stat_values)
    assert(len(test_average_array) == len(expected_average_array))
    for l in range(len(test_average_array)):
        assert(round(test_average_array[l],6) == expected_average_array[l])
    # Test 5
    average_method = 'MEDIAN'
    stat = 'fbar_obar'
    model_dataframe = model_data
    model_stat_values = stat_values_array[:,0,:]
    expected_average_array = np.array([5516.93924, 5517.80544])
    test_average_array = plot_util.calculate_average(logger, average_method,
                                                     stat, model_dataframe,
                                                     model_stat_values)
    assert(len(test_average_array) == len(expected_average_array))
    for l in range(len(test_average_array)):
        assert(round(test_average_array[l],6) == expected_average_array[l])
 
def test_calculate_ci():
    pytest.skip("Takes far too long to run")
    # Independently test getting the
    # confidence interval between two data arrays
    # based on method
    randx_seed = np.random.seed(0)
    # Test 1
    ci_method = 'EMC'
    modelB_values = np.array([0.4983181, 0.63076339, 0.73753565,
                              0.97960614, 0.74599612, 0.18829818,
                              0.29490815, 0.5063043, 0.15074971,
                              0.89009979, 0.81246532, 0.45399668,
                              0.98247594, 0.38211414, 0.26690678])
    modelA_values = np.array([0.37520287, 0.89286092, 0.66785908,
                              0.55742834, 0.60978346, 0.5760979,
                              0.55055558, 0.00388764, 0.55821689,
                              0.56042747, 0.30637593, 0.83325185,
                              0.84098604, 0.04021844, 0.57214717])
    total_days = 15
    stat = 'bias'
    average_method = 'MEAN'
    randx = np.random.rand(10000, total_days)
    expected_std = np.sqrt(
        ((
            (modelB_values - modelA_values)
            - (modelB_values - modelA_values).mean()
        )**2).mean()
    )
    expected_intvl = 2.228*expected_std/np.sqrt(total_days-1)
    test_intvl = plot_util.calculate_ci(logger, ci_method, modelB_values,
                                        modelA_values, total_days,
                                        stat, average_method, randx)
    assert(test_intvl == expected_intvl)
    # Test 2
    ci_method = 'EMC'
    modelB_values = np.array([0.4983181, 0.63076339, 0.73753565,
                              0.97960614, 0.74599612, 0.18829818,
                              0.29490815, 0.5063043, 0.15074971,
                              0.89009979, 0.81246532, 0.45399668,
                              0.98247594, 0.38211414, 0.26690678,
                              0.64162609, 0.01370935, 0.79477382,
                              0.31573415, 0.35282921, 0.57511574,
                              0.27815519, 0.49562973, 0.4859588,
                              0.16461642, 0.75849444, 0.44332183,
                              0.94935173, 0.62597888, 0.12819335])
    modelA_values = np.array([0.37520287, 0.89286092, 0.66785908,
                              0.55742834, 0.60978346, 0.5760979,
                              0.55055558, 0.00388764, 0.55821689,
                              0.56042747, 0.30637593, 0.83325185,
                              0.84098604, 0.04021844, 0.57214717,
                              0.75091023, 0.47321941, 0.12862311,
                              0.8644722, 0.92040807, 0.61376225,
                              0.24347848, 0.69990467, 0.69711331,
                              0.91866337, 0.63945963, 0.59999792,
                              0.2920741, 0.64972479, 0.25025121])
    total_days = 30
    stat = 'bias'
    average_method = 'MEAN'
    randx = np.random.rand(10000, total_days)
    expected_std = np.sqrt(
        ((
            (modelB_values - modelA_values)
            - (modelB_values - modelA_values).mean()
        )**2).mean()
    )
    expected_intvl = 2.042*expected_std/np.sqrt(total_days-1)
    test_intvl = plot_util.calculate_ci(logger, ci_method, modelB_values,
                                        modelA_values, total_days,
                                        stat, average_method, randx)
    assert(test_intvl == expected_intvl)
    # Test 3
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(days=i) for i in range(5)]
    )
    expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        expected_stat_file_dates.append(
            date.strftime('%Y%m%d_%H%M%S')
        )
    model_data_indexA = pd.MultiIndex.from_product(
            [['MODEL_TESTA'], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
    )
    model_data_arrayA = np.array([
        [3600, 5525.75062, 5525.66493, 30615218.26089, 30615764.49722,
         30614724.90979, 5.06746],
        [3600, 5519.11108, 5519.1014, 30549413.45946, 30549220.68868,
         30549654.24048, 5.12344],
        [3600, 5516.80228, 5516.79513, 30522742.16484, 30522884.89927,
         30522660.30975, 5.61752],
        [3600, 5516.93924, 5517.80544, 30525709.03932, 30520984.50965,
         30530479.99675, 4.94325],
        [3600, 5514.52274, 5514.68224, 30495695.82208, 30494633.24046,
         30496805.48259, 5.20369]
    ])
    model_dataA = pd.DataFrame(model_data_arrayA, index=model_data_indexA,
                               columns=[ 'TOTAL', 'FBAR', 'OBAR', 'FOBAR',
                                         'FFBAR', 'OOBAR', 'MAE' ])
    model_data_arrayB = np.array([
        [3600, 5527.43726, 5527.79714, 30635385.37277, 30633128.08035,
         30637667.9488, 3.74623],
        [3600, 5520.22487, 5520.5867, 30562940.31742, 30560471.32084, 
         30565442.31244, 4.17792],
        [3600, 5518.16049, 5518.53379, 30538694.69234, 30536683.66886,
         30540732.11308, 3.86693],
        [3600, 5519.20033, 5519.38443, 30545925.19732, 30544766.74602, 
         30547108.75357, 3.7534],
        [3600, 5515.78776, 5516.17552, 30509811.84136, 30507573.43899,
         30512077.12263, 4.02554]
    ])
    model_data_indexB = pd.MultiIndex.from_product(
            [['MODEL_TESTB'], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
    )
    model_dataB = pd.DataFrame(model_data_arrayB, index=model_data_indexB,
                               columns=[ 'TOTAL', 'FBAR', 'OBAR', 'FOBAR',
                                         'FFBAR', 'OOBAR', 'MAE' ])
    ci_method = 'EMC_MONTE_CARLO'
    modelB_values = model_dataB
    modelA_values = model_dataA
    total_days = 5
    stat = 'bias'
    average_method = 'AGGREGATION'
    randx = np.random.rand(10000, total_days)
    expected_intvl = 0.3893656076904014
    test_intvl = plot_util.calculate_ci(logger, ci_method, modelB_values,
                                        modelA_values, total_days,
                                        stat, average_method, randx)
    assert(test_intvl == expected_intvl)

def test_get_stat_plot_name():
    # Independently test getting the
    # a more formalized statistic name
    # Test 1
    stat = 'bias'
    expected_stat_plot_name = 'Bias'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 2
    stat = 'rmse_md'
    expected_stat_plot_name = 'Root Mean Square Error from Mean Error'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 3
    stat = 'fbar_obar'
    expected_stat_plot_name = 'Forecast and Observation Averages'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 4
    stat = 'acc'
    expected_stat_plot_name = 'Anomaly Correlation Coefficient'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 5
    stat = 'vdiff_speed'
    expected_stat_plot_name = 'Difference Vector Speed'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 6
    stat = 'baser'
    expected_stat_plot_name = 'Base Rate'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 7
    stat = 'fbias'
    expected_stat_plot_name = 'Frequency Bias'
    test_stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    assert(test_stat_plot_name == expected_stat_plot_name)

def test_calculate_stat():
    # Independently test calculating
    # statistic values
    date_base = datetime.datetime(2019, 1, 1)
    date_array = np.array(
        [date_base + datetime.timedelta(days=i) for i in range(5)]
    )
    expected_stat_file_dates = []
    for date in date_array:
        dt = date.time()
        expected_stat_file_dates.append(
            date.strftime('%Y%m%d_%H%M%S')
        )
    model_data_index = pd.MultiIndex.from_product(
            [['MODEL_TEST'], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
    )
    model_data_array = np.array([
        [3600, 5525.75062, 5525.66493, 30615218.26089, 30615764.49722,
         30614724.90979, 5.06746],
        [3600, 5519.11108, 5519.1014, 30549413.45946, 30549220.68868,
         30549654.24048, 5.12344],
        [3600, 5516.80228, 5516.79513, 30522742.16484, 30522884.89927,
         30522660.30975, 5.61752],
        [3600, 5516.93924, 5517.80544, 30525709.03932, 30520984.50965,
         30530479.99675, 4.94325],
        [3600, 5514.52274, 5514.68224, 30495695.82208, 30494633.24046,
         30496805.48259, 5.20369]
    ])
    model_data = pd.DataFrame(model_data_array, index=model_data_index,
                              columns=[ 'TOTAL', 'FBAR', 'OBAR', 'FOBAR',
                                        'FFBAR', 'OOBAR', 'MAE' ])
    # Test 1
    stat = 'bias'
    expected_stat_values_array = np.array([[[(5525.75062 - 5525.66493),
                                           (5519.11108 - 5519.1014),
                                           (5516.80228 - 5516.79513),
                                           (5516.93924 - 5517.80544),
                                           (5514.52274 - 5514.68224)
                                          ]]])
    expected_stat_values = pd.Series(expected_stat_values_array[0,0,:],
                                     index=model_data_index)
    expected_stat_plot_name = 'Bias'
    test_stat_values, test_stat_values_array, test_stat_plot_name = (
        plot_util.calculate_stat(logger, model_data, stat)
    )
    assert(test_stat_values.equals(expected_stat_values))
    assert(len(test_stat_values_array[0,0,:]) ==
            len(expected_stat_values_array[0,0,:]))
    for l in range(len(test_stat_values_array[0,0,:])):
        assert(test_stat_values_array[0,0,l] ==
                expected_stat_values_array[0,0,l])
    assert(test_stat_plot_name == expected_stat_plot_name)
    # Test 2
    stat = 'fbar_obar'
    expected_stat_values_array = np.array([[[5525.75062, 5519.11108,
                                             5516.80228, 5516.93924,
                                             5514.52274]],
                                          [[5525.66493, 5519.1014,
                                            5516.79513, 5517.80544,
                                            5514.68224
                                          ]]])
    expected_stat_values = pd.DataFrame(expected_stat_values_array[:,0,:].T,
                                        index=model_data_index,
                                        columns=[ 'FBAR', 'OBAR' ])
    expected_stat_plot_name = 'Forecast and Observation Averages'
    test_stat_values, test_stat_values_array, test_stat_plot_name = (
        plot_util.calculate_stat(logger, model_data, stat)
    )
    assert(test_stat_values.equals(expected_stat_values))
    assert(len(test_stat_values_array[0,0,:]) ==
            len(expected_stat_values_array[0,0,:]))
    for l in range(len(test_stat_values_array[0,0,:])):
        assert(test_stat_values_array[0,0,l] ==
                expected_stat_values_array[0,0,l])
    assert(len(test_stat_values_array[1,0,:]) ==
            len(expected_stat_values_array[1,0,:]))
    for l in range(len(test_stat_values_array[1,0,:])):
        assert(test_stat_values_array[1,0,l] ==
                expected_stat_values_array[1,0,l])
    assert(test_stat_plot_name == expected_stat_plot_name)
