'''
Name: plot_date_by_level.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make date-pressure plots
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
import matplotlib.gridspec as gridspec

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
###import cmocean
###cmap_bias = cmocean.cm.curl
###cmap = cmocean.cm.tempo
###cmap_diff = cmocean.cm.balance
cmap_bias = plt.cm.PiYG_r
cmap = plt.cm.BuPu
cmap_diff = plt.cm.coolwarm

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
fcst_var_level_list = os.environ['FCST_VAR_LEVEL_LIST'].split(" ")
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
obs_var_level_list = os.environ['OBS_VAR_LEVEL_LIST'].split(" ")
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
nmodels = len(model_name_list)
model_plot_name_list = os.environ['MODEL_PLOT_NAME_LIST'].split(" ")
model_info = zip(model_name_list, model_plot_name_list)
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
fcst_var_levels = np.empty(len(fcst_var_level_list), dtype=int)
for vl in range(len(fcst_var_level_list)):
    fcst_var_levels[vl] = fcst_var_level_list[vl][1:]
xx, yy = np.meshgrid(plot_time_dates, fcst_var_levels)

logger.info("Reading in model data")
for model in model_info:
    model_num = model_info.index(model) + 1
    model_name= model[0]
    model_plot_name = model[1]
    for vl in range(len(fcst_var_level_list)):
        fcst_var_level = fcst_var_level_list[vl]
        obs_var_level = obs_var_level_list[vl]
        logger.debug("Processing data for FCST_VAR_LEVEL "+fcst_var_level+" OBS_VAR_LEVEL "+obs_var_level)
        model_level_data_now_index = pd.MultiIndex.from_product([[model_plot_name], [fcst_var_level], expected_stat_file_dates], names=['model_plot_name', 'levels', 'dates'])
        model_stat_file = os.path.join(stat_file_input_dir_base, verif_case, verif_type, model_plot_name, plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z", model_plot_name+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_interp"+interp+"_region"+region+".stat")
        if os.path.exists(model_stat_file):
            nrow = sum(1 for line in open(model_stat_file))
            if nrow == 0:
                logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" empty")
                model_level_now_data = pd.DataFrame(np.nan, index=model_level_data_now_index, columns=[ 'TOTAL' ])
            else:
                logger.debug("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" exists")
                model_now_stat_file_data = pd.read_csv(model_stat_file, sep=" ", skiprows=1, skipinitialspace=True, header=None)
                model_now_stat_file_data.rename(columns=dict(zip(model_now_stat_file_data.columns[:len(stat_file_base_columns)], stat_file_base_columns)), inplace=True)
                line_type = model_now_stat_file_data['LINE_TYPE'][0]
                stat_file_line_type_columns = plot_util.get_stat_file_line_type_columns(logger, met_version, line_type)
                model_now_stat_file_data.rename(columns=dict(zip(model_now_stat_file_data.columns[len(stat_file_base_columns):], stat_file_line_type_columns)), inplace=True)
                model_now_stat_file_data_fcst_valid_dates = model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
                model_level_now_data = pd.DataFrame(np.nan, index=model_level_data_now_index, columns=stat_file_line_type_columns)
                for expected_date in expected_stat_file_dates:
                    if expected_date in model_now_stat_file_data_fcst_valid_dates:
                         matching_date_index = model_now_stat_file_data_fcst_valid_dates.tolist().index(expected_date)
                         model_now_stat_file_data_indexed = model_now_stat_file_data.loc[matching_date_index][:]
                         for column in stat_file_line_type_columns:
                             model_level_now_data.loc[(model_plot_name, fcst_var_level, expected_date)][column] = model_now_stat_file_data_indexed.loc[:][column]
        else:
            logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_stat_file+" does not exist")
            model_level_now_data = pd.DataFrame(np.nan, index=model_level_data_now_index, columns=[ 'TOTAL' ])
        if vl > 0:
            model_now_data = pd.concat([model_now_data, model_level_now_data])
        else:
            model_now_data = model_level_now_data
    if model_num > 1:
        model_data = pd.concat([model_data, model_now_data])
    else:
        model_data = model_now_data

logger.info("Calculating and plotting statistics")
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_values, stat_values_array, stat_plot_name = plot_util.calculate_stat(logger, model_data, stat)
    if stat == "fbar_obar":
        logger.warning(stat+" is not currently supported for this type of plot")
        continue
    if event_equalization == "True":
        logger.debug("Doing event equalization")
        for vl in range(len(fcst_var_level_list)):
            stat_values_array[:,vl,:] = np.ma.mask_cols(stat_values_array[:,vl,:])
    if nmodels == 1:
        fig = plt.figure(figsize=(10,12))
        gs = gridspec.GridSpec(2,1)
        gs.update(wspace=0.3, hspace=0.25)
    elif nmodels == 2:
        fig = plt.figure(figsize=(10,12))
        gs = gridspec.GridSpec(2,1)
        gs.update(wspace=0.3, hspace=0.25)
    elif nmodels > 2 and nmodels <= 4:
        fig = plt.figure(figsize=(15,12))
        gs = gridspec.GridSpec(2,2)
        gs.update(wspace=0.3, hspace=0.25)
    elif nmodels > 4 and nmodels <= 6:
        fig = plt.figure(figsize=(19,12))
        gs = gridspec.GridSpec(2,3)
        gs.update(wspace=0.3, hspace=0.25)
    elif nmodels > 6 and nmodels <= 9:
        fig = plt.figure(figsize=(21,17))
        gs = gridspec.GridSpec(3,3)
        gs.update(wspace=0.35, hspace=0.25)
    else:
        logger.error("Too many models selected, max. is 9")
        exit(1)
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_stat_values_array = stat_values_array[model_index,:,:]
        ax = plt.subplot(gs[model_index])
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
        ax.set_ylabel("Pressure Level")
        ax.set_yscale("log")
        ax.invert_yaxis()
        ax.minorticks_off()
        ax.set_yticks(fcst_var_levels)
        ax.set_yticklabels(fcst_var_levels)
        ax.set_ylim([fcst_var_levels[0],fcst_var_levels[-1]])
        if stat == "bias":
            logger.debug("Plotting model "+str(model_num)+" "+model_name+" with name on plot "+model_plot_name)
            ax.set_title(model_plot_name, loc='left')
            if model_num == 1:
                clevels_bias = plot_util.get_clevels(model_stat_values_array)
                CF1 = ax.contourf(xx, yy, model_stat_values_array, levels=clevels_bias, cmap=cmap_bias, locator=matplotlib.ticker.MaxNLocator(symmetric=True), extend='both')
                C1 = ax.contour(xx, yy, model_stat_values_array, levels=CF1.levels, colors='k', linewidths=1.0)
                ax.clabel(C1, CF1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
            else:
                CF = ax.contourf(xx, yy, model_stat_values_array, levels=CF1.levels, cmap=cmap_bias, extend='both')
                C = ax.contour(xx, yy, model_stat_values_array, levels=CF1.levels, colors='k', linewidths=1.0)
                ax.clabel(C, CF.levels, fmt='%1.2f', inline=True, fontsize=12.5)
        else:
            if model_num == 1:
                logger.debug("Plotting model "+str(model_num)+" "+model_name+" with name on plot "+model_plot_name)   
                model1_name = model_name
                model1_plot_name = model_plot_name
                model1_stat_values_array = model_stat_values_array
                ax.set_title(model_plot_name, loc='left')
                CF1 = ax.contourf(xx, yy, model_stat_values_array, cmap=cmap, extend='both')
                C1 = ax.contour(xx, yy, model_stat_values_array, levels=CF1.levels, colors='k', linewidths=1.0)
                ax.clabel(C1, CF1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
            else:
                logger.debug("Plotting model "+str(model_num)+" "+model_name+" - model 1 "+model1_name+" with name on plot "+model_plot_name+"-"+model1_plot_name)
                ax.set_title(model_plot_name+"-"+model1_plot_name, loc='left')
                model_model1_diff = model_stat_values_array - model1_stat_values_array
                if model_num == 2:
                    clevels_diff = plot_util.get_clevels(model_model1_diff)
                    CF2 = ax.contourf(xx, yy, model_model1_diff, levels=clevels_diff, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                    C2 = ax.contour(xx, yy, model_model1_diff, levels=CF2.levels, colors='k', linewidths=1.0)
                    ax.clabel(C2, CF2.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                else:
                    CF = ax.contourf(xx, yy, model_model1_diff, levels=CF2.levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                    C = ax.contour(xx, yy, model_model1_diff, levels=CF2.levels, colors='k', linewidths=1.0)
                    ax.clabel(C, C.levels, fmt='%1.2f', inline=True, fontsize=12.5)
    if nmodels > 1:
        cax = fig.add_axes([0.1, -0.05, 0.8, 0.05])
        if stat == "bias":
            cbar = fig.colorbar(CF1, cax=cax, orientation='horizontal', ticks=CF1.levels)
        else:
            cbar = fig.colorbar(CF2, cax=cax, orientation='horizontal', ticks=CF2.levels)
    fig.suptitle(stat_plot_name+"\n"+"Fcst: "+fcst_var_name+" "+fcst_var_extra_title+fcst_var_thresh_title+" Obs: "+obs_var_name+" "+obs_var_extra_title+obs_var_thresh_title+" "+interp+" "+grid+"-"+region+"\n"+plot_time+": "+str(datetime.date.fromordinal(int(plot_time_dates[0])).strftime('%d%b%Y'))+"-"+str(datetime.date.fromordinal(int(plot_time_dates[-1])).strftime('%d%b%Y'))+", valid: "+valid_time_info[0][0:4]+"-"+valid_time_info[-1][0:4]+"Z, init: "+init_time_info[0][0:4]+"-"+init_time_info[-1][0:4]+"Z, forecast hour "+lead+"\n", fontsize=14, fontweight='bold')
    savefig_name = os.path.join(plotting_out_dir_imgs, stat+"_fhr"+lead+"_fcst"+fcst_var_name+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_extra+obs_var_thresh+"_"+interp+"_"+grid+region+".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name, bbox_inches='tight')
    plt.close()
