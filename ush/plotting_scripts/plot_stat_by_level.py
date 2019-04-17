'''
Name: plot_stat_by_level.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_time_series.py to make stat-pressue plots
History Log: First version
Usage: Called by make_plots_wrapper.py 
Parameters: None
Input Files: Text files
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
colors = ['black', 'darkgreen', 'darkred', 'indigo', 'blue', 'crimson', 'goldenrod', 'sandybrown', 'thistle']

verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
plot_time = os.environ['PLOT_TIME']
start_date_YYYYmmdd = os.environ['START_DATE_YYYYmmdd']
end_date_YYYYmmdd = os.environ['END_DATE_YYYYmmdd']
start_date_YYYYmmdd_dt = datetime.datetime.strptime(os.environ['START_DATE_YYYYmmdd'], "%Y%m%d")
end_date_YYYYmmdd_dt = datetime.datetime.strptime(os.environ['END_DATE_YYYYmmdd'], "%Y%m%d")
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
mean_file_cols = [ "LEADS", "VALS" ]
grid = os.environ['VERIF_GRID']
logger = logging.getLogger(os.environ['LOGGING_FILENAME'])
logger.setLevel(os.environ['LOGGING_LEVEL'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) ""%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(os.environ['LOGGING_FILENAME'], mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

fcst_var_levels = np.empty(len(fcst_var_level_list), dtype=int)
for vl in range(len(fcst_var_level_list)):
    fcst_var_levels[vl] = fcst_var_level_list[vl][1:]

for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    if stat == "fbar_obar":
        logger.warning(stat+" is not currently supported for this type of plot")
        continue
    stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
    logger.info("Reading in model data")
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_level_mean_data = np.empty([len(fcst_var_level_list)])
        model_level_mean_data.fill(np.nan)
        for vl in range(len(fcst_var_level_list)):
            fcst_var_level = fcst_var_level_list[vl]
            obs_var_level = obs_var_level_list[vl]
            logger.debug("Processing data for FCST_VAR_LEVEL "+fcst_var_level+" OBS_VAR_LEVEL "+obs_var_level)
            model_mean_file = os.path.join(plotting_out_dir_data, model_plot_name+"_"+stat+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh+"_interp"+interp+"_region"+region+"_LEAD_MEAN.txt")
            if os.path.exists(model_mean_file):
                nrow = sum(1 for line in open(model_mean_file))
                if nrow == 0: 
                    logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_mean_file+" empty")
                else:
                    logger.debug("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_mean_file+" exists")
                    model_mean_file_data = pd.read_csv(model_mean_file, sep=" ", header=None, names=mean_file_cols, dtype=str)
                    model_mean_file_data_leads = model_mean_file_data.loc[:]['LEADS'].tolist()
                    model_mean_file_data_vals = model_mean_file_data.loc[:]['VALS'].tolist()
                    if lead.ljust(6,'0') in model_mean_file_data_leads:
                        model_mean_file_data_lead_index = model_mean_file_data_leads.index(lead.ljust(6,'0'))
                        if model_mean_file_data_vals[model_mean_file_data_lead_index] == "--":
                            model_level_mean_data[vl] = np.nan
                        else:
                            model_level_mean_data[vl] = float(model_mean_file_data_vals[model_mean_file_data_lead_index])
            else:
                logger.warning("Model "+str(model_num)+" "+model_name+" with plot name "+model_plot_name+" file: "+model_mean_file+" does not exist")
        if model_num == 1:
            fig, ax = plt.subplots(1,1,figsize=(10,12))
            ax.grid(True)
            ax.tick_params(axis='x', pad=10)
            ax.set_xlabel(stat_plot_name)
            ax.tick_params(axis='y', pad=15)
            ax.set_ylabel('Pressure Level')
            ax.set_yscale("log")
            ax.invert_yaxis()
            ax.minorticks_off()
            ax.set_yticks(fcst_var_levels)
            ax.set_yticklabels(fcst_var_levels)
            ax.set_ylim([fcst_var_levels[0],fcst_var_levels[-1]])
            fig.suptitle(stat_plot_name+"\n"+"Fcst: "+fcst_var_name+" "+fcst_var_extra_title+fcst_var_thresh_title+" Obs: "+obs_var_name+" "+obs_var_extra_title+obs_var_thresh_title+" "+interp+" "+grid+"-"+region+"\n"+plot_time+": "+start_date_YYYYmmdd_dt.strftime("%d%b%Y")+"-"+end_date_YYYYmmdd_dt.strftime("%d%b%Y")+", valid: "+valid_time_info[0][0:4]+"-"+valid_time_info[-1][0:4]+"Z, init: "+init_time_info[0][0:4]+"-"+init_time_info[-1][0:4]+"Z, forecast hour "+lead+"\n", fontsize=14, fontweight='bold')
        ax.plot(model_level_mean_data, fcst_var_levels, color=colors[model_index], ls='-', linewidth=1.0, marker='o', markersize=7, label=model_plot_name)
    ax.legend(bbox_to_anchor=(0.025, 1.01, 0.95, .102), loc=3, ncol=nmodels, fontsize='13', mode="expand", borderaxespad=0.)
    savefig_name = os.path.join(plotting_out_dir_imgs, stat+"_fhr"+lead+"_fcst"+fcst_var_name+fcst_var_extra+fcst_var_thresh+"_obs"+obs_var_name+obs_var_extra+obs_var_thresh+"_"+interp+"_"+grid+region+".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name, bbox_inches='tight')
    plt.close()
