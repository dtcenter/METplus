'''
Name: plot_time_series.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper
          run_all_times to make time series plots
History Log: Third version
Usage: Called by make_plots_wrapper.py 
Parameters: None
Input Files: MET .stat files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import os
import numpy as np
import pandas as pd
import itertools
import warnings
import logging
import datetime
import math
import re
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md

import plot_util as plot_util
from plot_util import get_ci_file, get_lead_avg_file

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..')))
from metplus.util import do_string_sub

# Read environment variables set in make_plots_wrapper.py
verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
date_type = os.environ['DATE_TYPE']
valid_beg = os.environ['VALID_BEG']
valid_end = os.environ['VALID_END']
init_beg = os.environ['INIT_BEG']
init_end = os.environ['INIT_END']
fcst_valid_hour_list = os.environ['FCST_VALID_HOUR'].split(', ')
fcst_valid_hour = os.environ['FCST_VALID_HOUR']
fcst_init_hour_list = os.environ['FCST_INIT_HOUR'].split(', ')
fcst_init_hour = os.environ['FCST_INIT_HOUR']
obs_valid_hour_list = os.environ['OBS_VALID_HOUR'].split(', ')
obs_valid_hour = os.environ['OBS_VALID_HOUR']
obs_init_hour_list = os.environ['OBS_INIT_HOUR'].split(', ')
obs_init_hour = os.environ['OBS_INIT_HOUR']
fcst_lead_list = os.environ['FCST_LEAD'].split(', ')
fcst_var_name = os.environ['FCST_VAR']
fcst_var_units = os.environ['FCST_UNITS']
fcst_var_level_list = os.environ['FCST_LEVEL'].split(', ')
fcst_var_thresh_list = os.environ['FCST_THRESH'].split(', ')
obs_var_name = os.environ['OBS_VAR']
obs_var_units = os.environ['OBS_UNITS']
obs_var_level_list = os.environ['OBS_LEVEL'].split(', ')
obs_var_thresh_list = os.environ['OBS_THRESH'].split(', ')
interp_mthd = os.environ['INTERP_MTHD']
interp_pnts = os.environ['INTERP_PNTS']
vx_mask = os.environ['VX_MASK']
alpha = os.environ['ALPHA']
desc = os.environ['DESC']
obs_lead = os.environ['OBS_LEAD']
cov_thresh = os.environ['COV_THRESH']
stats_list = os.environ['STATS'].split(', ')
model_list = os.environ['MODEL'].split(', ')
model_obtype_list = os.environ['MODEL_OBTYPE'].split(', ')
model_reference_name_list = os.environ['MODEL_REFERENCE_NAME'].split(', ')
dump_row_filename_template = os.environ['DUMP_ROW_FILENAME']
average_method = os.environ['AVERAGE_METHOD']
ci_method = os.environ['CI_METHOD']
verif_grid = os.environ['VERIF_GRID']
event_equalization = os.environ['EVENT_EQUALIZATION']
met_version = os.environ['MET_VERSION']
input_base_dir = os.environ['INPUT_BASE_DIR']
output_base_dir = os.environ['OUTPUT_BASE_DIR']
log_metplus = os.environ['LOG_METPLUS']
log_level = os.environ['LOG_LEVEL']

# General set up and settings
# Plots
warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
colors = [
    '#000000', '#2F1E80', '#D55E00', '#882255', 
    '#018C66', '#D6B616', '#036398', '#CC79A7'
]
# Logging
logger = logging.getLogger(log_metplus)
logger.setLevel(log_level)
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    +'%(message)s',
    '%m/%d %H:%M:%S'
    )
file_handler = logging.FileHandler(log_metplus, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
output_data_dir = os.path.join(output_base_dir, 'data')
output_imgs_dir = os.path.join(output_base_dir, 'imgs')
# Model info
model_info_list = list(
    zip(model_list,
        model_reference_name_list,
        model_obtype_list,
    )
)
nmodels = len(model_info_list)
# Plot info
plot_info_list = list(
    itertools.product(*[fcst_lead_list, 
                        fcst_var_level_list, 
                        fcst_var_thresh_list])
    )
# Date and time infomation and build title for plot
date_beg = os.environ[date_type+'_BEG']
date_end = os.environ[date_type+'_END']
date_plot_title = (
    date_type.title()+': '
    +str(datetime.datetime.strptime(date_beg, '%Y%m%d').strftime('%d%b%Y'))
    +'-'
    +str(datetime.datetime.strptime(date_end, '%Y%m%d').strftime('%d%b%Y'))
)
valid_init_dict = {
    'fcst_valid_hour_beg': fcst_valid_hour_list[0],
    'fcst_valid_hour_end': fcst_valid_hour_list[-1],
    'fcst_init_hour_beg': fcst_init_hour_list[0],
    'fcst_init_hour_end': fcst_init_hour_list[-1],
    'obs_valid_hour_beg': obs_valid_hour_list[0],
    'obs_valid_hour_end': obs_valid_hour_list[-1],
    'obs_init_hour_beg': obs_init_hour_list[0],
    'obs_init_hour_end': obs_init_hour_list[-1],
    'valid_hour_beg': '',
    'valid_hour_end': '',
    'init_hour_beg': '',
    'init_hour_end': ''
}
valid_init_type_list = [ 
    'valid_hour_beg', 'valid_hour_end', 'init_hour_beg', 'init_hour_end'
]
for vitype in valid_init_type_list:
    if (valid_init_dict['fcst_'+vitype] != '' 
            and valid_init_dict['obs_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]
    elif (valid_init_dict['obs_'+vitype] != '' 
            and valid_init_dict['fcst_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['obs_'+vitype]
    if valid_init_dict['fcst_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['fcst_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['fcst_'+vitype] = '235959'
    if valid_init_dict['obs_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['obs_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['obs_'+vitype] = '235959'
    if valid_init_dict['fcst_'+vitype] == valid_init_dict['obs_'+vitype]:
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]
time_plot_title = ''
for vi in ['valid_hour', 'init_hour']:
    beg_hr = valid_init_dict[vi+'_beg']
    end_hr = valid_init_dict[vi+'_end']
    fcst_beg_hr = valid_init_dict['fcst_'+vi+'_beg']
    fcst_end_hr = valid_init_dict['fcst_'+vi+'_end']
    obs_beg_hr = valid_init_dict['obs_'+vi+'_beg']
    obs_end_hr = valid_init_dict['obs_'+vi+'_end']
    time_label = vi.split('_')[0].title()
    if beg_hr != '' and end_hr != '':
        if beg_hr == end_hr:
            time_plot_title+=', '+time_label+': '+beg_hr[0:4]+'Z'
        else:
            time_plot_title+=(
                ', '+time_label+': '+beg_hr[0:4]+'-'+end_hr[0:4]+'Z'
            )
    else:
        if fcst_beg_hr == fcst_end_hr:
            time_plot_title+=', Fcst '+time_label+': '+fcst_beg_hr[0:4]+'Z'
        else:
            time_plot_title+=(
                ', Fcst '+time_label+': '+fcst_beg_hr[0:4]+'-'
                 +fcst_end_hr[0:4]+'Z'
            )
        if obs_beg_hr == obs_end_hr:
            time_plot_title+=', Obs '+time_label+': '+obs_beg_hr[0:4]+'Z'
        else:
            time_plot_title+=(
                ', Obs '+time_label+': '+obs_beg_hr[0:4]+'-'
                +obs_end_hr[0:4]+'Z'
            )
# Common plotting information and build title for plot
if 'WV1' not in interp_mthd or interp_mthd != '':
    extra_plot_title = verif_grid+'-'+vx_mask
else:
    extra_plot_title = interp_mthd+', '+verif_grid+'-'+vx_mask
if desc != '':
    extra_plot_title+=', Desc: '+desc
if obs_lead != '':
    extra_plot_title+=', Obs Lead: '+obs_lead
if interp_pnts != '':
    extra_plot_title+=', Interp. Pts.: '+interp_pnts
if cov_thresh != '':
    extra_plot_title+=', Cov. Thresh:'+cov_thresh
if alpha != '':
    extra_plot_title+=', Alpha: '+alpha
# MET .stat file formatting
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)
nbase_columns = len(stat_file_base_columns)
# Significance testing info
# need to set up random number array [nmodels, ntests, ndays]
# for EMC Monte Carlo testing. Each model has its own 
# "series" of random numbers used at all forecast hours
# and thresholds.
mc_dates, mc_expected_stat_file_dates = plot_util.get_date_arrays(
    date_type, date_beg, date_end,
    fcst_valid_hour, fcst_init_hour,
    obs_valid_hour, obs_init_hour,
    '000000'
)
ndays = len(mc_expected_stat_file_dates)
ntests = 10000
randx = np.random.rand(nmodels,ntests,ndays)

# Start looping to make plots
for plot_info in plot_info_list:
    fcst_lead = plot_info[0]
    fcst_var_level = plot_info[1]
    obs_var_level = obs_var_level_list[
        fcst_var_level_list.index(fcst_var_level)
    ]
    fcst_var_thresh = plot_info[2]
    obs_var_thresh = obs_var_thresh_list[
        fcst_var_thresh_list.index(fcst_var_thresh)
    ]
    fcst_var_thresh_symbol, fcst_var_thresh_letter = plot_util.format_thresh(
        fcst_var_thresh
    )
    obs_var_thresh_symbol, obs_var_thresh_letter = plot_util.format_thresh(
        obs_var_thresh
    )
    # Build plot title for variable info
    fcst_var_plot_title = 'Fcst: '+fcst_var_name+' '+fcst_var_level
    obs_var_plot_title = 'Obs: '+obs_var_name+' '+obs_var_level
    if 'WV1' in interp_mthd:
        fcst_var_plot_title+=' '+interp_mthd
        obs_var_plot_title+=' '+interp_mthd 
    if fcst_var_thresh != '':
        fcst_var_plot_title+=' '+fcst_var_thresh
    if obs_var_thresh != '':
        obs_var_plot_title+=' '+obs_var_thresh
    if fcst_var_units == '':
        fcst_var_units_list = []
    else:
        fcst_var_units_list = fcst_var_units.split(', ')
    if obs_var_units == '':
        obs_var_units_list = []
    else:
        obs_var_units_list = obs_var_units.split(', ')
    # Build plot title for forecast lead
    fcst_lead_plot_title = 'Fcst Lead: '+fcst_lead[:-4]+'hr'
    if fcst_lead[-4:-2] != '00':
        fcst_lead_plot_title+=fcst_lead[-4:-2]+'min'
    if fcst_lead[-2:] != '00':
        fcst_lead_plot_title+=fcst_lead[-2:]+'sec'
    # Clean up time information for plot title
    # if valid/init is a single hour, then init/valid
    # is also a single hour
    date_time_plot_title = date_plot_title+time_plot_title
    date_type_beg_hour = valid_init_dict[date_type.lower()+'_hour_beg']
    date_type_end_hour = valid_init_dict[date_type.lower()+'_hour_end']
    if (date_type_beg_hour != '' and date_type_end_hour != ''
            and date_type_beg_hour == date_type_end_hour):
        fcst_lead_timedelta = datetime.timedelta(
            hours=int(fcst_lead[:-4]),
            minutes=int(fcst_lead[-4:-2]),
            seconds=int(fcst_lead[-2:])
        )
        date_type_timedelta = datetime.timedelta(
            hours=int(date_type_beg_hour[0:2]),
            minutes=int(date_type_beg_hour[2:4]),
            seconds=int(date_type_beg_hour[4:])
        )
        if date_type == 'VALID':
             check_time_plot_title = 'Init'
             time_diff = (
                 date_type_timedelta - fcst_lead_timedelta
             ).total_seconds()
        elif date_type == 'INIT':
             check_time_plot_title = 'Valid'
             time_diff = (
                 date_type_timedelta - fcst_lead_timedelta
             ).total_seconds()
        day_diff = time_diff//86400
        hr_diff = (time_diff - (day_diff*86400))//3600
        min_diff = (time_diff%3600) // 60
        sec_diff = (time_diff%3600)%60
        time_title_replace = re.search(check_time_plot_title+': (.*)Z',
                                       date_time_plot_title)
        date_time_plot_title = date_time_plot_title.replace(
            check_time_plot_title+': '+time_title_replace.group(1),
            check_time_plot_title+': '+str(int(hr_diff)).zfill(2)
            +str(int(min_diff)).zfill(2)
        )
    logger.info("Working on forecast lead "+fcst_lead+" "
                +"and forecast variable "+fcst_var_name+" "+fcst_var_level+" "
                +fcst_var_thresh)
    # Set up base name for file naming convention for MET .stat files,
    # and output data and images
    base_name = date_type.lower()+date_beg+'to'+date_end
    if (valid_init_dict['valid_hour_beg'] != ''
            and valid_init_dict['valid_hour_end'] != ''):
        base_name+=(
            '_valid'+valid_init_dict['valid_hour_beg'][0:4]
            +'to'+valid_init_dict['valid_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_valid'+valid_init_dict['fcst_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_valid_hour_end'][0:4]+'Z'
            +'_obs_valid'+valid_init_dict['obs_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_valid_hour_end'][0:4]+'Z'
        )
    if (valid_init_dict['init_hour_beg'] != ''
            and valid_init_dict['init_hour_end'] != ''):
        base_name+=(
            '_init'+valid_init_dict['init_hour_beg'][0:4]
            +'to'+valid_init_dict['init_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_init'+valid_init_dict['fcst_init_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_init_hour_end'][0:4]+'Z'
            +'_obs_init'+valid_init_dict['obs_init_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_init_hour_end']+'Z'
        )
    base_name+=(
        '_fcst_lead'+fcst_lead
        +'_fcst'+fcst_var_name+fcst_var_level
        +fcst_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_obs'+obs_var_name+obs_var_level
        +obs_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_vxmask'+vx_mask
    )
    if desc != '':
        base_name+='_desc'+desc
    if obs_lead != '':
        base_name+='_obs_lead'+obs_lead
    if interp_pnts != '':
        base_name+='_interp_pnts'+interp_pnts
    if cov_thresh != '':
        cov_thresh_symbol, cov_thresh_letter = plot_util.format_thresh(
            cov_thresh
        )
        base_name+='_cov_thresh'+cov_thresh_letter.replace(',', '_')
    if alpha != '':
        base_name+='_alpha'+alpha
    # Set up expected date in MET .stat file and date plot information
    plot_time_dates, expected_stat_file_dates = plot_util.get_date_arrays(
        date_type, date_beg, date_end,
        fcst_valid_hour, fcst_init_hour,
        obs_valid_hour, obs_init_hour,
        fcst_lead
    )
    total_dates = len(plot_time_dates)
    if len(plot_time_dates) == 0:
        logger.error("Date array constructed information from METplus "
                     +"conf file has length of 0. Not enough information "
                     +"was provided to build date information. Please check "
                     +"provided VALID/INIT_BEG/END and "
                     +"OBS/FCST_INIT/VALID_HOUR_LIST")
        exit(1)
    elif len(plot_time_dates) <= 3:
        date_tick_intvl = 1
    elif len(plot_time_dates) > 3 and len(plot_time_dates) <= 10:
        date_tick_intvl = 2
    elif len(plot_time_dates) > 10 and len(plot_time_dates) < 31:
        date_tick_intvl = 5 
    else:
        date_tick_intvl = 10
    # Reading in model .stat files from stat_analysis
    logger.info("Reading in model data")
    for model_info in model_info_list:
        model_num = model_info_list.index(model_info) + 1
        model_name = model_info[0]
        model_plot_name = model_info[1]
        model_obtype = model_info[2]
        model_data_now_index = pd.MultiIndex.from_product(
            [[model_plot_name], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
        )
#        model_stat_filename = (
#            model_plot_name+'_'+model_obtype+'_'
#            +base_name
#            +'_dump_row.stat'
#        )
#        model_stat_file = os.path.join(input_base_dir, model_stat_filename)
        model_stat_template = dump_row_filename_template
        string_sub_dict = {
            'model': model_name,
            'model_reference': model_plot_name,
            'obtype': model_obtype,
            'fcst_lead': fcst_lead,
            'fcst_level': fcst_var_level,
            'obs_level': obs_var_level,
            'fcst_thresh': fcst_var_thresh,
            'obs_thresh': obs_var_thresh,
        }
        model_stat_file = do_string_sub(model_stat_template,
                                        **string_sub_dict)
        if os.path.exists(model_stat_file):
            nrow = sum(1 for line in open(model_stat_file))
            if nrow == 0:
                logger.warning("Model "+str(model_num)+" "+model_name+" "
                               +"with plot name "+model_plot_name+" "
                               +"file: "+model_stat_file+" empty")
                model_now_data = pd.DataFrame(np.nan,
                                              index=model_data_now_index,
                                              columns=[ 'TOTAL' ])
            else:
                logger.debug("Model "+str(model_num)+" "+model_name+" "
                             +"with plot name "+model_plot_name+" "
                             +"file: "+model_stat_file+" exists")
                model_now_stat_file_data = pd.read_csv(
                    model_stat_file, sep=" ", skiprows=1,
                    skipinitialspace=True, header=None
                )
                model_now_stat_file_data.rename(
                    columns=dict(zip(
                        model_now_stat_file_data.columns[:nbase_columns],
                        stat_file_base_columns
                    )), inplace=True
                )
                line_type = model_now_stat_file_data['LINE_TYPE'][0]
                stat_file_line_type_columns = (
                    plot_util.get_stat_file_line_type_columns(logger,
                                                              met_version,
                                                              line_type)
                )
                model_now_stat_file_data.rename(
                    columns=dict(zip(
                        model_now_stat_file_data.columns[nbase_columns:],
                        stat_file_line_type_columns
                    )), inplace=True
                )
                model_now_stat_file_data_fcst_valid_dates = (
                    model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
                )
                model_now_data = (
                    pd.DataFrame(np.nan, index=model_data_now_index,
                                 columns=stat_file_line_type_columns)
                )
                model_now_stat_file_data.fillna(
                    {'FCST_UNITS':'NA', 'OBS_UNITS':'NA', 'VX_MASK':'NA'},
                    inplace=True
                )
                if float(met_version) >= 8.1:
                    model_now_fcst_units = (
                        model_now_stat_file_data.loc[0]['FCST_UNITS']
                    )
                    model_now_obs_units = (      
                        model_now_stat_file_data.loc[0]['OBS_UNITS']
                    )
                    if model_now_fcst_units != 'NA':
                        fcst_var_units_list.append(model_now_fcst_units)
                    if model_now_obs_units != 'NA':
                        obs_var_units_list.append(model_now_obs_units)
                for expected_date in expected_stat_file_dates:
                    if expected_date in \
                            model_now_stat_file_data_fcst_valid_dates:
                        matching_date_idx = (
                            model_now_stat_file_data_fcst_valid_dates \
                            .tolist().index(expected_date)
                        )
                        model_now_stat_file_data_indexed = (
                            model_now_stat_file_data.loc[matching_date_idx][:]
                        )
                        for col in stat_file_line_type_columns:
                            model_now_data.loc[
                                (model_plot_name, expected_date)
                            ][col] = (
                                model_now_stat_file_data_indexed.loc[:][col]
                            )
        else:
            logger.warning("Model "+str(model_num)+" "+model_name+" "
                           +"with plot name "+model_plot_name+" "
                           +"file: "+model_stat_file+" does not exist")
            model_now_data = pd.DataFrame(np.nan,
                                          index=model_data_now_index,
                                          columns=[ 'TOTAL' ])
        if model_num > 1:
            model_data = pd.concat([model_data, model_now_data])
        else:
            model_data = model_now_data
    if fcst_var_units_list != []:
        fcst_var_units_plot_title = (
            '['+', '.join(list(set(fcst_var_units_list)))+']'
        )
    else:
        fcst_var_units_plot_title = ''
    if obs_var_units_list != []:
        obs_var_units_plot_title = (
            '['+', '.join(list(set(obs_var_units_list)))+']'
        )
    else:
        obs_var_units_plot_title = ''
    # Calculate statistics and plots
    logger.info("Calculating and plotting statistics")
    for stat in stats_list:
        logger.debug("Working on "+stat)
        stat_values, stat_values_array, stat_plot_name = (
            plot_util.calculate_stat(logger, model_data, stat)
        )
        if event_equalization == 'True':
            logger.debug("Doing event equalization")
            for l in range(len(stat_values_array[:,0,0])):
                stat_values_array[l,:,:] = (
                    np.ma.mask_cols(stat_values_array[l,:,:])
                )
        np.ma.set_fill_value(stat_values_array, np.nan)
        for model_info in model_info_list:
            model_num = model_info_list.index(model_info) + 1
            model_idx = model_info_list.index(model_info)
            model_name = model_info[0]
            model_plot_name = model_info[1]
            model_obtype = model_info[2]
            model_stat_values_array = stat_values_array[:,model_idx,:]

#            lead_avg_filename = stat + '_' + os.path.basename(model_info[3])

            # if fcst_leadX is in filename, replace it with fcst_lead_avgs
            # and add .txt to end of filename
#            if 'fcst_lead' + fcst_lead in model_info[3]:
#                lead_avg_filename.replace('fcst_lead' + fcst_lead, 'fcst_lead_avgs')
#                lead_avg_filename += '.txt'

            # if not, remove mention of forecast lead and
            # add fcst_lead_avgs.txt to end of filename
#            else:
#                lead_avg_filename.replace('fcst_lead' + fcst_lead, '')
#                lead_avg_filename += '_fcst_lead_avgs.txt'

#            lead_avg_file = os.path.join(output_base_dir, 'data',
#                                         lead_avg_filename)


            # Write model forecast lead average to file
            model_stat_template = dump_row_filename_template
            string_sub_dict = {
                'model': model_name,
                'model_reference': model_plot_name,
                'obtype': model_obtype,
                'fcst_lead': fcst_lead,
                'fcst_level': fcst_var_level,
                'obs_level': obs_var_level,
                'fcst_thresh': fcst_var_thresh,
                'obs_thresh': obs_var_thresh,
            }
            model_stat_file = do_string_sub(model_stat_template,
                                            **string_sub_dict)
            lead_avg_file = get_lead_avg_file(stat,
                                              model_stat_file,
                                              fcst_lead,
                                              output_base_dir)

            logger.debug("Writing model "+str(model_num)+" "+model_name+" "
                         +"with name on plot "+model_plot_name+" lead "
                         +fcst_lead+" average to file: "+lead_avg_file)
            model_stat_average_array = plot_util.calculate_average(
                logger, average_method, stat, model_data.loc[[model_plot_name]],
                model_stat_values_array
            )
            with open(lead_avg_file, 'a') as file2write:
                file2write.write(fcst_lead)
                if fcst_var_units_plot_title != '':
                    file2write.write(' '+fcst_var_units_plot_title)
                else:
                    file2write.write(' [NA]')
                if obs_var_units_plot_title != '':
                    file2write.write(' '+obs_var_units_plot_title)
                else:
                    file2write.write(' [NA]')
                for l in range(len(model_stat_average_array)):
                    file2write.write(
                        ' '+str(model_stat_average_array[l])
                    )
                file2write.write('\n') 
            # Write confidence intervals to file, if requested,
            # using similar naming to model forecast lead average
            if ci_method != 'NONE':
#                CI_filename = (
#                    stat+'_'
#                    +model_plot_name+'_'+model_obtype+'_'
#                    +base_name
#                    +'_CI_'+ci_method+'.txt'
#                ).replace('fcst_lead'+fcst_lead, 'fcst_lead_avgs')
#                CI_filename = stat + '_' + os.path.basename(model_info[3])
                # if fcst_leadX is in filename, replace it with fcst_lead_avgs
                # and add .txt to end of filename
#                if 'fcst_lead' + fcst_lead in model_info[3]:
#                    CI_filename.replace('fcst_lead' + fcst_lead, 'fcst_lead_avgs')
#                    CI_filename += '.txt'

                 # if not, remove mention of forecast lead and
                 # add fcst_lead_avgs.txt to end of filename
#                 else:
#                     CI_filename.replace('fcst_lead' + fcst_lead, '')
#                     CI_filename += '_fcst_lead_avgs'

#                CI_filename += '_CI_' + ci_method + '.txt'

#                CI_file = os.path.join(output_base_dir, 'data',
#                                       CI_filename)

                CI_file = get_ci_file(stat,
                                      model_stat_file,
                                      fcst_lead,
                                      output_base_dir,
                                      ci_method)


                if (stat == 'fbar_obar' or stat == 'orate_frate'
                        or stat == 'baser_frate'):
                    logger.debug("Writing "+ci_method+" confidence intervals "
                                 +"for difference between model "
                                 +str(model_num)+" "+model_name+" with name "
                                 +"on plot "+model_plot_name+" and the "
                                 +"observations at lead "+fcst_lead+" to "
                                 +"file: "+CI_file)
                    if ci_method == 'EMC_MONTE_CARLO':
                        logger.warning("Monte Carlo resampling not "
                                       +"done for fbar_obar, orate_frate, "
                                       +"or baser_frate.")
                        stat_CI = '--'
                    else:
                        stat_CI = plot_util.calculate_ci(
                            logger, ci_method, model_stat_values_array[0,:],
                            model_stat_values_array[1,:],total_dates,
                            stat, average_method, randx[model_idx,:,:]
                        )
                    with open(CI_file, 'a') as file2write:
                        file2write.write(fcst_lead+' '+str(stat_CI)+'\n')
                else:
                    if model_num == 1:
                        model1_stat_values_array = (
                            model_stat_values_array[0,:]
                        )
                        model1_plot_name = model_plot_name
                        model1_name = model_name
                    else:
                        logger.debug("Writing "+ci_method+" confidence "
                                     +"intervals for difference between "
                                     +"model "+str(model_num)+" "
                                     +model_name+" with name on plot "
                                     +model_plot_name+" and model 1 "
                                     +model1_name+" with name on plot "
                                     +model1_plot_name+" at lead "
                                     +fcst_lead+" to file: "+CI_file)
                        if ci_method == 'EMC_MONTE_CARLO':
                            stat_CI = plot_util.calculate_ci(
                                logger, ci_method,
                                model_data.loc[[model_plot_name]],
                                model_data.loc[[model1_plot_name]], total_dates,
                                stat, average_method, randx[model_idx,:,:]
                            )    
                        else:
                            stat_CI = plot_util.calculate_ci(
                                logger, ci_method, model_stat_values_array,
                                model1_stat_values_array, total_dates,
                                stat, average_method, randx[model_idx,:,:]
                            )
                        with open(CI_file, 'a') as file2write:
                            file2write.write(fcst_lead+' '+str(stat_CI)+'\n')
            logger.debug("Plotting model "+str(model_num)+" "+model_name+" "
                         +"with name on plot "+model_plot_name)
            if model_num == 1:
                fig, ax = plt.subplots(1,1,figsize=(10,6))
                ax.grid(True)
                ax.tick_params(axis='x', pad=15)
                ax.set_xlabel(date_type.title()+' Date', labelpad=30)
                ax.set_xlim([plot_time_dates[0],plot_time_dates[-1]])
                ax.xaxis.set_major_locator(
                    md.DayLocator(interval=date_tick_intvl)
                )
                ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
                ax.xaxis.set_minor_locator(md.DayLocator())
                ax.tick_params(axis='y', pad=15)
                ax.set_ylabel(stat_plot_name, labelpad=30)
                if (stat == 'fbar_obar' or stat == 'orate_frate'
                        or stat == 'baser_frate'):
                    obs_stat_values_array = model_stat_values_array[1,:]
                    obs_count = (
                        len(obs_stat_values_array) 
                        - np.ma.count_masked(obs_stat_values_array)
                    )
                    plot_time_dates_m = np.ma.masked_where(
                        np.ma.getmask(obs_stat_values_array), plot_time_dates
                    )
                    plot_time_dates_mc = np.ma.compressed(plot_time_dates_m)
                    obs_stat_values_mc = np.ma.compressed(
                        obs_stat_values_array
                    )
                    if np.ma.is_masked(model_stat_average_array[1]):
                        obs_legend_label = (
                            'obs '
                            +str(model_stat_average_array[1])+' '
                            +str(obs_count)
                        )
                    else:
                        obs_legend_label = (
                            'obs '
                            +str(round(model_stat_average_array[1],3))+' '
                            +str(obs_count)
                        )
                    ax.plot_date(plot_time_dates_mc,
                                 obs_stat_values_mc,
                                 color='#888888',
                                 ls='-', linewidth=2.0,
                                 marker='o', markersize=7,
                                 label=obs_legend_label,
                                 zorder=4)
            count = (
                len(model_stat_values_array[0,:])
                - np.ma.count_masked(model_stat_values_array[0,:])
            )
            plot_time_dates_m = np.ma.masked_where(
                np.ma.getmask(model_stat_values_array[0,:]), plot_time_dates
            )
            plot_time_dates_mc = np.ma.compressed(plot_time_dates_m)
            model_stat_values_mc = np.ma.compressed(
                model_stat_values_array[0,:]
            )
            if np.ma.is_masked(model_stat_average_array[0]):
                model_legend_label = (
                    model_plot_name+' '
                    +str(model_stat_average_array[0])+' '
                    +str(count)
                )
            else:
                model_legend_label = (
                    model_plot_name+' '
                    +str(round(model_stat_average_array[0],3))+' '
                    +str(count)
                )
            ax.plot_date(plot_time_dates_mc, model_stat_values_mc, 
                         color=colors[model_idx], 
                         ls='-', linewidth=2.0,
                         marker='o', markersize=7,
                         label=model_legend_label,
                         zorder=(nmodels-model_idx)+4)
        ax.legend(bbox_to_anchor=(1.025, 1.0, 0.375, 0.0), loc='upper right',
                  ncol=1, fontsize='13', mode='expand', borderaxespad=0.)
        ax.set_title(stat_plot_name+'\n'
                     +fcst_var_plot_title+' '+fcst_var_units_plot_title
                     +', '+obs_var_plot_title+' '+obs_var_units_plot_title+'\n'
                     +extra_plot_title+'\n'
                     +date_time_plot_title+', '+fcst_lead_plot_title+'\n',
                     fontsize=14, fontweight='bold')
        savefig_imagename = stat+'_'+base_name+'.png'
        savefig_image = os.path.join(output_base_dir, 'images',
                                     savefig_imagename)
        logger.info("Saving image as "+savefig_image)
        plt.savefig(savefig_image, bbox_inches='tight')
        plt.close()
