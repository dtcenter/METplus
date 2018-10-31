#!/usr/bin/env python
'''
Program Name: plot_grid2obs_upper_air_vertprof.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_grid2obs_upper_air_ts.py to make vertical profile plots
History Log:  Second version
Usage: 
Parameters: None
Input Files: ASCII files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''
############################################################################
##### Import python modules
from __future__ import (print_function, division)
import os
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import warnings
import logging
import plot_defs as pd
import pandas as pandas
#############################################################################
##### Settings
np.set_printoptions(suppress=True)
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
warnings.filterwarnings('ignore')
colors = ['black', 'darkgreen', 'darkred', 'indigo', 'blue', 'crimson', 'goldenrod', 'sandybrown', 'thistle']
##############################################################################
##### Read in data and set variables
#forecast dates
month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
sdate = os.environ['START_T']
syear = int(sdate[:4])
smon = int(sdate[4:6])
smonth = month_name[smon-1]
sday = int(sdate[6:8])
edate = os.environ['END_T']
eyear = int(edate[:4])
emon = int(edate[4:6])
emonth = month_name[emon-1]
eday = int(edate[6:8])
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
model_names= os.environ['MODEL_NAMES'].replace(", ", ",").split(",")
nmodels = len(model_names)
cycle = os.environ['CYCLE']
region = os.environ['REGION']
grid = os.environ['REGRID_TO_GRID']
lead = os.environ['LEAD']
lead_int = int(lead)
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_levels_list = os.environ['FCST_VAR_LEVELS_LIST'].replace(", ", ",").split(",")
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_levels_list = os.environ['OBS_VAR_LEVELS_LIST'].replace(", ", ",").split(",")
nlevels = len(fcst_var_levels_list)
#remove 'P' prior to pressure level
fcst_var_levels_num = np.empty(nlevels, dtype=int)
obs_var_levels_num = np.empty(nlevels, dtype=int)
for vl in range(nlevels):
    fcst_var_levels_num[vl] = fcst_var_levels_list[vl][1:]
    obs_var_levels_num[vl] = obs_var_levels_list[vl][1:]
#ouput info
logging_filename = os.environ['LOGGING_FILENAME']
logger = logging.getLogger(logging_filename)
logger.setLevel("DEBUG")
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) ""%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(logging_filename, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
ch = logging.StreamHandler()
logger.addHandler(ch)
plotting_out_dir_base = os.environ['PLOTTING_OUT_DIR']
plotting_out_dir = os.path.join(plotting_out_dir_base, "upper_air")
####################################################################
logger.info(" ")
logger.info("------> Running "+os.path.realpath(__file__))
logger.debug("----- for "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z lead:"+lead+" mean vertical profile for region:"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
#############################################################################
##### Create image directory if does not exist
if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
    os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
##### Read data in data, compute statistics, and plot
#read in data
s=1
while s <= nstats: #loop over statistics
    stat_now = plot_stats_list[s-1]
    logger.debug("---- "+stat_now)
    stat_formal_name_now = pd.get_stat_formal_name(stat_now)
    m=1
    while m <= nmodels: #loop over models
        model_now = model_names[m-1]
        logger.debug("--- "+str(m)+" "+model_now)
        model_now_vals_vertprof = np.ones(nlevels) * np.nan
        if stat_now == 'avg':
            model_now_obar_vertprof = np.ones(nlevels) * np.nan
            mean_cols = [ "LEADS", "VALS", "OBAR" ]
        else:
            mean_cols = [ "LEADS", "VALS" ]
        vl=1
        while vl <= nlevels:
            fcst_var_level_now = fcst_var_levels_list[vl-1]
            obs_var_level_now = obs_var_levels_list[vl-1]
            model_now_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
            if os.path.exists(model_now_mean_file):
                nrow = sum(1 for line in open(model_now_mean_file))
                if nrow == 0:
                    logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" empty")
                else:
                    logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_mean_file)
                    model_now_data = pandas.read_csv(model_now_mean_file, sep=" ", header=None, names=mean_cols)
                    model_now_stat_now_leads = model_now_data.loc[:]['LEADS']
                    model_now_stat_now_vals = model_now_data.loc[:]['VALS']
                    #get mean value for correct lead time
                    lead_index = np.where(model_now_stat_now_leads == lead_int)[0]
                    if len(lead_index) != 0:
                        if model_now_stat_now_vals[lead_index[0]] == '--':
                            model_now_vals_vertprof[vl-1] = np.nan
                        else:
                            model_now_vals_vertprof[vl-1] = model_now_stat_now_vals[lead_index[0]]
                    else:
                        model_now_vals_vertprof[vl-1] = np.nan
                    if stat_now == 'avg':
                        model_now_stat_now_obar = model_now_data.loc[:]['OBAR']
                        if len(lead_index) != 0:
                            if model_now_stat_now_obar[lead_index[0]] == '--':
                                model_now_obar_vertprof[vl-1] = np.nan
                            else:
                                model_now_obar_vertprof[vl-1] = model_now_stat_now_obar[lead_index[0]]
                        else:
                            model_now_obar_vertprof[vl-1] = np.nan
                    model_now_obar_vertprof = np.ma.masked_invalid(model_now_obar_vertprof)
                    count_masked_obar = np.ma.count_masked(model_now_obar_vertprof)
            else:
                logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" missing")
            vl+=1
        model_now_vals_vertprof = np.ma.masked_invalid(model_now_vals_vertprof)
        count_masked_vals = np.ma.count_masked(model_now_vals_vertprof)
        #plot individual statistic vertical profile
        if m == 1:
            fig, ax = plt.subplots(1,1,figsize=(10,12))
            ax.grid(True)
            ax.tick_params(axis='x', pad=10)
            ax.set_xlabel(stat_formal_name_now)
            ax.tick_params(axis='y', pad=15)
            ax.set_ylabel('Pressure Level')
            ax.set_yscale("log")
            ax.invert_yaxis()
            ax.minorticks_off()
            ax.set_yticks(fcst_var_levels_num)
            ax.set_yticklabels(fcst_var_levels_num)
            ax.set_ylim([fcst_var_levels_num[0],fcst_var_levels_num[-1]])
            if stat_now == 'avg':
                logger.debug("Plotting obar vertical profile")
                ax.plot(model_now_obar_vertprof, fcst_var_levels_num, color='dimgrey', ls='-', linewidth=2.0, marker='o', markersize=7, label='obs')
                logger.debug("Plotting fbar vertical profile for "+model_now)
            else:
                logger.debug("Plotting "+stat_now+" vertical profile for "+model_now)
            ax.plot(model_now_vals_vertprof, fcst_var_levels_num, color=colors[m-1], ls='-', linewidth=1.0, marker='o', markersize=7, label=model_now)
        else:
            if stat_now == 'avg':
                logger.debug("Plotting fbar vertical profile for "+model_now)
            else:
                logger.debug("Plotting "+stat_now+" vertical profile for "+model_now)
            ax.plot(model_now_vals_vertprof, fcst_var_levels_num, color=colors[m-1], ls='-', linewidth=1.0, marker='o', markersize=7, label=model_now)
        m+=1
        if stat_now == 'avg':
            ax.legend(bbox_to_anchor=(0.025, 1.01, 0.95, .102), loc=3, ncol=nmodels+1, fontsize='13', mode="expand", borderaxespad=0.)
        else:
            ax.legend(bbox_to_anchor=(0.025, 1.01, 0.95, .102), loc=3, ncol=nmodels, fontsize='13', mode="expand", borderaxespad=0.)
        ax.set_title("Fcst: "+fcst_var_name+" Obs: "+obs_var_name+" "+str(stat_formal_name_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" forecast hour "+lead+" mean vertical profile\n\n", fontsize=14, fontweight='bold')
        logger.debug("--- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhr"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_vp.png")
        plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhr"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_vp.png", bbox_inches='tight')
    s+=1
