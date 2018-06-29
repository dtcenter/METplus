#!/usr/bin/env python
'''
Program Name: plot_grid2obs_upper_air_tsmean.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_grid2obs_upper_air_ts.py to make dieoff plots
History Log:  Initial version
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
edate=os.environ['END_T']
eyear = int(edate[:4])
emon = int(edate[4:6])
emonth = month_name[emon-1]
eday = int(edate[6:8])
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
model_list = os.environ['MODEL_LIST'].replace(", ", ",").split(",")
nmodels = len(model_list)
cycle = os.environ['CYCLE']
region = os.environ['REGION']
grid = os.environ['REGRID_TO_GRID']
lead = os.environ['LEAD']
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
formatter = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(logging_filename, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
ch = logging.StreamHandler()
logger.addHandler(ch)
plotting_out_dir = os.environ['PLOTTING_OUT_DIR']
####################################################################
logger.info("------> Running "+os.path.realpath(__file__))
logger.debug("----- for "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z lead:"+lead+" vertical profile for region:"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
#############################################################################
##### Read data in data, compute statistics, and plot
#read in data
s=1
while s <= nstats: #loop over statistics
    stat_now = plot_stats_list[s-1]
    logger.debug("---- "+stat_now)
    m=1
    while m <= nmodels: #loop over models
         model_now = model_list[m-1]
         logger.debug("--- "+str(m)+" "+model_now)
         if stat_now == 'avg':
            model_now_fbar_vertprof = np.ones(nlevels) * np.nan
            model_now_obar_vertprof = np.ones(nlevels) * np.nan
         else:
            model_now_vals_vertprof = np.ones(nlevels) * np.nan 
         vl = 1
         while vl <= nlevels:
             fcst_var_level_now = fcst_var_levels_list[vl-1]
             obs_var_level_now = obs_var_levels_list[vl-1]
             logger.debug("fcst level:"+fcst_var_level_now+" obs level:"+obs_var_level_now)
             if stat_now == 'avg':
                 #get forecast hour mean file
                 model_now_fbar_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/fbar_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
                 if os.path.exists(model_now_fbar_mean_file):
                     nrow = sum(1 for line in open(model_now_fbar_mean_file))
                     if nrow == 0: #file blank
                         logger.warning(model_now_fbar_mean_file+" was empty! Setting to NaN")
                         model_now_fbar_vertprof[vl-1] = np.nan
                     else:
                         logger.debug("Found "+model_now_fbar_mean_file)
                         #read data file and put in array
                         data = list()
                         with open(model_now_fbar_mean_file) as f:
                             for line in f:
                                 line_split = line.split()
                                 data.append(line_split)
                         data_array = np.asarray(data)
                         #assign variables
                         model_now_fbar_leads = data_array[:,0]
                         model_now_fbar_mean = data_array[:,1]
                         lead_index = np.where(model_now_fbar_leads == lead)[0]
                         if len(lead_index) != 0:
                             if model_now_fbar_mean[lead_index[0]] == '--':
                                 model_now_fbar_vertprof[vl-1] = np.nan
                             else:
                                 model_now_fbar_vertprof[vl-1] = model_now_fbar_mean[lead_index[0]]
                         else:
                             model_now_fbar_vertprof[vl-1] = np.nan
                 else:
                     logger.error(model_now_fbar_mean_file+" NOT FOUND! Setting to NaN")
                     model_now_fbar_vertprof[vl-1] = np.nan
                 #get forecast hour mean file
                 model_now_obar_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/obar_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
                 if os.path.exists(model_now_obar_mean_file):
                     nrow = sum(1 for line in open(model_now_obar_mean_file))
                     if nrow == 0: #file blank
                         logger.warning(model_now_obar_mean_file+" was empty! Setting to NaN")
                         model_now_obar_vertprof[vl-1] = np.nan
                     else:
                         logger.debug("Found "+model_now_obar_mean_file)
                         #read data file and put in array
                         data = list()
                         with open(model_now_obar_mean_file) as f:
                             for line in f:
                                 line_split = line.split()
                                 data.append(line_split)
                         data_array = np.asarray(data)
                         #assign variables
                         model_now_obar_leads = data_array[:,0]
                         model_now_obar_mean = data_array[:,1]
                         lead_index = np.where(model_now_obar_leads == lead)[0]
                         if len(lead_index) != 0:
                             if model_now_obar_mean[lead_index[0]] == '--':
                                 model_now_obar_vertprof[vl-1] = np.nan
                             else:
                                 model_now_obar_vertprof[vl-1] = model_now_obar_mean[lead_index[0]]
                         else:
                             model_now_obar_vertprof[vl-1] = np.nan
                 else:
                     logger.error(model_now_obar_mean_file+" NOT FOUND! Setting to NaN")
                     model_now_obar_vertprof[vl-1] = np.nan
             else:
                 #get forecast hour mean file
                 model_now_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
                 if os.path.exists(model_now_mean_file):
                     nrow = sum(1 for line in open(model_now_mean_file))
                     if nrow == 0: #file blank
                         logger.warning(model_now_mean_file+" was empty! Setting to NaN")
                         model_now_vals_vertprof[vl-1] = np.nan
                     else:
                         logger.debug("Found "+model_now_mean_file)
                         #read data file and put in array
                         data = list()
                         with open(model_now_mean_file) as f:
                             for line in f:
                                 line_split = line.split()
                                 data.append(line_split)
                         data_array = np.asarray(data)
                         #assign variables
                         model_now_leads = data_array[:,0]
                         model_now_stat_now_mean = data_array[:,1]
                         lead_index = np.where(model_now_leads == lead)[0]
                         if len(lead_index) != 0:
                             if model_now_stat_now_mean[lead_index[0]] == '--':
                                 model_now_vals_vertprof[vl-1] = np.nan
                             else:
                                 model_now_vals_vertprof[vl-1] = model_now_stat_now_mean[lead_index[0]]
                         else:
                             model_now_vals_vertprof[vl-1] = np.nan
                 else:
                     logger.error(model_now_mean_file+" NOT FOUND! Setting to NaN")
                     model_now_vals_vertprof[vl-1] = np.nan
                 ##count_masked = np.ma.count_masked(model_now_stat_now_mean)
             vl+=1
         #create image directory if does not exist
         if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
             os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
         if stat_now == 'avg':
             model_now_fbar_vertprof = np.ma.masked_invalid(model_now_fbar_vertprof)
             count_masked_fbar = np.ma.count_masked(model_now_fbar_vertprof)
             model_now_obar_vertprof = np.ma.masked_invalid(model_now_obar_vertprof)
             count_masked_obar = np.ma.count_masked(model_now_obar_vertprof)
             if m == 1:
                 fig, ax = plt.subplots(1,1,figsize=(10,12))
                 if count_masked_obar != len(model_now_obar_vertprof):
                     logger.debug("Plotting obar vertical profile")
                     ax.plot(model_now_obar_vertprof, fcst_var_levels_num, color='dimgrey', ls='-', linewidth=3.0, marker='o', markersize=7, label='obs')
                 if count_masked_fbar != len(model_now_fbar_vertprof):
                     logger.debug("Plotting fbar vertical profile for "+model_now)
                     ax.plot(model_now_fbar_vertprof, fcst_var_levels_num, color=colors[m-1], ls='-', linewidth=1.0, marker='o', markersize=7, label=model_now)
                 ax.grid(True)
                 ax.set_xlabel(stat_now)
                 ax.set_ylabel('Pressure Level')
                 ax.set_yscale("log")
                 ax.invert_yaxis()
                 ax.minorticks_off()
                 ax.set_yticks(fcst_var_levels_num)
                 ax.set_yticklabels(fcst_var_levels_num)
                 ax.set_ylim([fcst_var_levels_num[0],fcst_var_levels_num[-1]])
                 ax.tick_params(axis='x', pad=10)
                 ax.tick_params(axis='y', pad=15)
             else:
                 logger.debug("Plotting fbar vertical profile for "+model_now)
                 if count_masked_fbar != len(model_now_fbar_vertprof):
                        ax.plot(model_now_fbar_vertprof, fcst_var_levels_num, color=colors[m-1],  ls='-', linewidth=1.0,  marker='o', markersize=7, label=model_now)
         else:
             model_now_vals_vertprof = np.ma.masked_invalid(model_now_vals_vertprof)
             count_masked = np.ma.count_masked(model_now_vals_vertprof)
             if m == 1:
                 logger.debug("Plotting "+stat_now+" vertical profile for "+model_now)
                 fig, ax = plt.subplots(1,1,figsize=(10,12))
                 if count_masked != len(model_now_vals_vertprof):
                     ax.plot(model_now_vals_vertprof, fcst_var_levels_num, color=colors[m-1], ls='-', linewidth=1.0, marker='o', markersize=7, label=model_now)
                 ax.grid(True)
                 ax.set_xlabel(stat_now)
                 ax.set_ylabel('Pressure Level')
                 ax.set_yscale("log")
                 ax.invert_yaxis()
                 ax.minorticks_off()
                 ax.set_yticks(fcst_var_levels_num)
                 ax.set_yticklabels(fcst_var_levels_num)
                 ax.set_ylim([fcst_var_levels_num[0],fcst_var_levels_num[-1]])
                 ax.tick_params(axis='x', pad=10)
                 ax.tick_params(axis='y', pad=15)
             else:
                 logger.debug("Plotting "+stat_now+" vertical profile for "+model_now)
                 if count_masked != len(model_now_vals_vertprof):
                        ax.plot(model_now_vals_vertprof, fcst_var_levels_num, color=colors[m-1],  ls='-', linewidth=1.0,  marker='o', markersize=7, label=model_now)
         m+=1
    if stat_now == 'avg':
        plt.legend(bbox_to_anchor=(0.025, 1.01, 0.95, .102), loc=3, ncol=nmodels+1, fontsize='13', mode="expand", borderaxespad=0.)
    else:
        plt.legend(bbox_to_anchor=(0.025, 1.01, 0.95, .102), loc=3, ncol=nmodels, fontsize='13', mode="expand", borderaxespad=0.)
    ax.set_title("Fcst: "+fcst_var_name+" Obs: "+obs_var_name+" "+str(stat_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" Vertical Profile\n\n", fontsize=14, fontweight='bold')
    logger.debug("--- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_vp.png")
    plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_vp.png", bbox_inches='tight')
    s+=1
