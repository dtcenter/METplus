'''
Name: plot_time_series.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make time series plots
History Log: First version
Usage: 
Parameters: None
Input Files: ASCII files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)
import os
import numpy as np
import plot_util as plot_util
import pandas as pd
import warnings
import logging
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
colors = ['black', 'darkgreen', 'darkred', 'indigo', 'blue', 'crimson', 'goldenrod', 'sandybrown', 'thistle']

verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
plot_time = os.environ['PLOT_TIME']
start_date_YYYYmmdd = os.environ['START_DATE_YYYYmmdd']
end_date_YYYYmmdd = os.environ['END_DATE_YYYYmmdd']
valid_time_info = os.environ['VALID_TIME_INFO'].replace('"','').split(", ")
init_time_info = os.environ['INIT_TIME_INFO'].replace('"','').split(", ")
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_extra = os.environ['FCST_VAR_EXTRA'].replace(" ", "").replace("=","").replace(";","").replace('"','').replace("'","").replace(",","-").replace("_","")
if fcst_var_extra == "None":
    fcst_var_extra = ""
if os.environ['FCST_VAR_EXTRA'] == "None":
    fcst_var_extra_title = ""
else:
    fcst_var_extra_title = " "+os.environ['FCST_VAR_EXTRA']+" "
fcst_var_level = os.environ['FCST_VAR_LEVEL']
fcst_var_thresh = os.environ['FCST_VAR_THRESH'].replace(" ","").replace(">=","ge").replace("<=","le").replace(">","gt").replace("<","lt").replace("==","eq").replace("!=","ne")
if fcst_var_thresh == "None":
    fcst_var_thresh = ""
    fcst_var_thresh_title = ""
else:
    fcst_var_thresh_title = " "+fcst_var_thresh
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_extra = os.environ['OBS_VAR_EXTRA'].replace(" ", "").replace("=","").replace(";","").replace('"','').replace("'","").replace(",","-").replace("_","")
if obs_var_extra == "None":
    obs_var_extra = ""
if os.environ['OBS_VAR_EXTRA'] == "None":
    obs_var_extra_title = ""
else:
    obs_var_extra_title = " "+os.environ['OBS_VAR_EXTRA']+" "
obs_var_level = os.environ['OBS_VAR_LEVEL']
obs_var_thresh = os.environ['OBS_VAR_THRESH'].replace(" ","").replace(">=","ge").replace("<=","le").replace(">","gt").replace("<","lt").replace("==","eq").replace("!=","ne")
if obs_var_thresh == "None":
    obs_var_thresh = ""
    obs_var_thresh_title = ""
else:
    obs_var_thresh_title = " "+obs_var_thresh
interp = os.environ['INTERP']
region = os.environ['REGION']
lead = os.environ['LEAD']
stat_file_input_dir_base = os.environ['STAT_FILES_INPUT_DIR']
plotting_out_dir = os.environ['PLOTTING_OUT_DIR_FULL']
plotting_out_dir_data = os.path.join(plotting_out_dir, "data", plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z")
plotting_out_dir_imgs = os.path.join(plotting_out_dir, "imgs", plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z")
if not os.path.exists(plotting_out_dir_data):
    os.makedirs(plotting_out_dir_data)
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)
plot_stats_list = os.environ['PLOT_STATS_LIST'].split(", ")
model_name_list = os.environ['MODEL_NAME_LIST'].split(" ")
model_plot_name_list = os.environ['MODEL_PLOT_NAME_LIST'].split(" ")
model_info = zip(model_name_list, model_plot_name_list)
ci_method = os.environ['CI_METHOD']
grid = os.environ['VERIF_GRID']
event_equalization = os.environ['EVENT_EQUALIZATION']
met_version = os.environ['MET_VERSION']
logger = logging.getLogger(os.environ['LOGGING_FILENAME'])
logger.setLevel(os.environ['LOGGING_LEVEL'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) ""%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(os.environ['LOGGING_FILENAME'], mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

plot_time_dates, expected_stat_file_dates = plot_util.get_date_arrays(plot_time, start_date_YYYYmmdd, end_date_YYYYmmdd, valid_time_info, init_time_info, lead)
total_days = len(plot_time_dates)
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)

logger.info("Reading in model data....")
for model in model_info:
    model_num = model_info.index(model) + 1
    model_name= model[0]
    model_plot_name = model[1]
    model_data_now_index = pd.MultiIndex.from_product([[model_plot_name], expected_stat_file_dates], names=['model_plot_name', 'dates'])
    model_stat_file = os.path.join(stat_file_input_dir_base, verif_case, verif_type, model_plot_name, plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z", model_plot_name+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_interp"+interp+"_region"+region+".stat")
    if os.path.exists(model_stat_file):
        nrow = sum(1 for line in open(model_stat_file))
        if nrow == 0:
            logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" empty")
            model_now_data = pd.DataFrame(np.nan, index=model_data_now_index, columns=[ 'TOTAL' ])
        else:
            logger.debug("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" exists")
            model_now_stat_file_data = pd.read_csv(model_stat_file, sep=" ", skiprows=1, skipinitialspace=True, header=None)
            model_now_stat_file_data.rename(columns=dict(zip(model_now_stat_file_data.columns[:len(stat_file_base_columns)], stat_file_base_columns)), inplace=True)
            line_type = model_now_stat_file_data['LINE_TYPE'][0]
            stat_file_line_type_columns = plot_util.get_stat_file_line_type_columns(logger, met_version, line_type)
            model_now_stat_file_data.rename(columns=dict(zip(model_now_stat_file_data.columns[len(stat_file_base_columns):], stat_file_line_type_columns)), inplace=True)
            model_now_stat_file_data_fcst_valid_dates = model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
            model_now_data = pd.DataFrame(np.nan, index=model_data_now_index, columns=stat_file_line_type_columns)
            for expected_date in expected_stat_file_dates:
                if expected_date in model_now_stat_file_data_fcst_valid_dates:
                     matching_date_index = model_now_stat_file_data_fcst_valid_dates.tolist().index(expected_date)
                     model_now_stat_file_data_indexed = model_now_stat_file_data.loc[matching_date_index][:]
                     for column in stat_file_line_type_columns:
                         model_now_data.loc[(model_plot_name, expected_date)][column] = model_now_stat_file_data_indexed.loc[:][column]
    else:
        logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" does not exist")
        model_now_data = pd.DataFrame(np.nan, index=model_data_now_index, columns=[ 'TOTAL' ])
    if model_num > 1:
        model_data = pd.concat([model_data, model_now_data])
    else:
        model_data = model_now_data

logger.info("Calculating and plotting statistics....")
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_values, stat_values_array, stat_plot_name = plot_util.calculate_stat(logger, model_data, stat)
    if event_equalization == "True":
        logger.debug("Doing event equalization")
        stat_values_array = np.ma.mask_cols(stat_values_array)
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name= model[0]
        model_plot_name = model[1]
        model_stat_values_array = stat_values_array[model_index,:]
        lead_mean_filename = os.path.join(plotting_out_dir_data, model_plot_name+"_"+stat+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_interp"+interp+"_region"+region+"_LEAD_MEAN.txt")
        logger.debug("Writing model "+str(model_num)+" "+model_name+" with name on plot "+model_plot_name+" lead "+lead+" mean to file: "+lead_mean_filename)
        with open(lead_mean_filename, 'a') as lead_mean_file:
            lead_mean_file.write(lead.ljust(6,'0')+' '+str(model_stat_values_array.mean())+ '\n')
        if ci_method == "None":
            logger.debug("Not calculating confidence intervals")
        else:
            if model_num == 1:
                model1_stat_values_array = model_stat_values_array
                model1_plot_name = model_plot_name
                model1_name = model_name
            elif model_num > 1:
                CI_filename = os.path.join(plotting_out_dir_data, model_plot_name+"_"+stat+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_interp"+interp+"_region"+region+"_CI_"+ci_method+".txt")
                stat_CI = plot_util.calculate_ci(logger, ci_method, model_stat_values_array, model1_stat_values_array, total_days)
                logger.debug("Writing "+ci_method+" confidence intervals for difference between model "+str(model_num)+" "+model_name+" with name on plot "+model_plot_name+" and model 1 "+model1_name+" with name on plot "+model1_plot_name+" lead "+lead+" to file: "+CI_filename)
                with open(CI_filename, 'a') as CI_file:
                    CI_file.write(lead.ljust(6,'0')+' '+str(stat_CI)+ '\n')
        logger.debug("Plotting model "+str(model_num)+" "+model_name+" with name on plot "+model_plot_name)
        if model_num == 1:
            fig, ax = plt.subplots(1,1,figsize=(10,6))
            ax.grid(True)
            ax.tick_params(axis='x', pad=10)
            ax.set_xlabel(plot_time.title()+" Date")
            ax.set_xlim([plot_time_dates[0],plot_time_dates[-1]])
            if len(plot_time_dates) < 31:
                day_interval=5
            else:
                day_interval=10
            ax.xaxis.set_major_locator(md.DayLocator(interval=day_interval))
            ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
            ax.xaxis.set_minor_locator(md.DayLocator())
            ax.tick_params(axis='y', pad=15)
            ax.set_ylabel(stat_plot_name)
            #ax.set_ylim()
        count = len(model_stat_values_array) - np.ma.count_masked(model_stat_values_array)
        ax.plot_date(plot_time_dates, model_stat_values_array, color=colors[model_index], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_plot_name+' '+str(round(model_stat_values_array.mean(),2))+' '+str(count))
    ax.legend(bbox_to_anchor=(1.025, 1.0, 0.375, 0.0), loc='upper right', ncol=1, fontsize='13', mode="expand", borderaxespad=0.)
    ax.set_title(stat_plot_name+"\n"+"Fcst: "+fcst_var_name+"_"+fcst_var_level+fcst_var_extra_title+fcst_var_thresh_title+", Obs: "+obs_var_name+"_"+obs_var_level+obs_var_extra_title+obs_var_thresh_title+" "+interp+" "+grid+"-"+region+"\n"+plot_time+": "+str(datetime.date.fromordinal(int(plot_time_dates[0])).strftime('%d%b%Y'))+"-"+str(datetime.date.fromordinal(int(plot_time_dates[-1])).strftime('%d%b%Y'))+", valid: "+valid_time_info[0][0:4]+"-"+valid_time_info[-1][0:4]+"Z, init: "+init_time_info[0][0:4]+"-"+init_time_info[-1][0:4]+"Z, forecast hour "+lead+"\n", fontsize=14, fontweight='bold')
    savefig_name = os.path.join(plotting_out_dir_imgs, stat+"_fhr"+lead+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_"+interp+"_"+grid+region+".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name, bbox_inches='tight')
    plt.close()
