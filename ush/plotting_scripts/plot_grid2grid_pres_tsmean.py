#!/usr/bin/env python
'''
Program Name: plot_grid2grid_pres_tsmean.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_grid2grid_pres_ts.py to make dieoff plots
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
model_names = os.environ['MODEL_NAMES'].replace(" ", ",").split(",")
nmodels = len(model_names)
cycle = os.environ['CYCLE']
lead_list = os.environ['LEAD_LIST'].replace(", ", ",").split(",")
leads = np.asarray(lead_list).astype(float)
region = os.environ['REGION']
grid = "G2"
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_levels_list = os.environ['FCST_VAR_LEVELS_LIST'].replace(", ", ",").split(",")
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_levels_list = os.environ['OBS_VAR_LEVELS_LIST'].replace(", ", ",").split(",")
nlevels = len(fcst_var_levels_list)
#ouput info
logging_filename = os.environ['LOGGING_FILENAME']
logger = logging.getLogger(logging_filename)
logging_level = os.environ['LOGGING_LEVEL']
logger.setLevel(logging_level)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) ""%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(logging_filename, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
plotting_out_dir_base = os.environ['PLOTTING_OUT_DIR']
plotting_out_dir = os.path.join(plotting_out_dir_base, "pres")
####################################################################
logger.info(" ")
logger.info("Running "+os.path.realpath(__file__))
logger.info("for "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z forecast hour means for region:"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
#############################################################################
##### Create image directory if does not exist
if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
    os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
##### Read data in data, compute statistics, and plot
#read in data
vl = 1
while vl <= nlevels:
    fcst_var_level_now = fcst_var_levels_list[vl-1]
    obs_var_level_now = obs_var_levels_list[vl-1]
    logger.info("fcst level:"+fcst_var_level_now+" obs level:"+obs_var_level_now)
    logger.info("Reading data and plotting means")
    s=1
    while s <= nstats: #loop over statistics
        stat_now = plot_stats_list[s-1]
        stat_formal_name_now = pd.get_stat_formal_name(stat_now)
        logger.debug(stat_now)
     	m=1
     	while m <= nmodels: #loop over models
             model_now = model_names[m-1]
             logger.debug(str(m)+" "+model_now)
             #intialize data array
             model_now_stat_now_means = np.ones_like(leads) * np.nan
             #get forecast hour mean file
             model_now_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
             if os.path.exists(model_now_mean_file):
                 nrow = sum(1 for line in open(model_now_mean_file))
                 if nrow == 0: #file blank
                     logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" empty")
                 else:
                     logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_mean_file)
                     mean_cols = [ "LEADS", "VALS" ]
                     model_now_data = pandas.read_csv(model_now_mean_file, sep=" ", header=None, names=mean_cols)
                     model_now_stat_now_leads = model_now_data.loc[:]['LEADS'] 
                     model_now_stat_now_vals = model_now_data.loc[:]['VALS']
                     #check for any missing data in current model for requested forecast leads
                     for l in range(len(leads)):
                         if leads[l] == model_now_stat_now_leads[l]:
                              if model_now_stat_now_vals[l] == '--':
                                  model_now_stat_now_means[l] = np.nan
                              else:
                                  model_now_stat_now_means[l] = model_now_stat_now_vals[l]
                         else:
                            ll = np.where(model_now_stat_now_leads == leads[l])[0]
                            if len(ll) != 0:
                                 if model_now_stat_now_vals[ll[0]] == '--':
                                     model_now_stat_now_means[l] = np.nan
                                 else:
                                     model_now_stat_now_means[l] = model_now_stat_now_vals[ll[0]]
                            else:
                                 model_now_stat_now_means[l] = np.nan
             else:
                 logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" missing")                 
             model_now_stat_now_means = np.ma.masked_invalid(model_now_stat_now_means)
             count_masked = np.ma.count_masked(model_now_stat_now_means)
             #plot individual statistic forecast hour mean with CI time seres
             if m == 1:
                 #set up plot
                 fig, (ax1, ax2) = plt.subplots(2,1,figsize=(10,12), sharex=True)
                 #forecast hour means
                 ax1.grid(True)
                 ax1.tick_params(axis='x', pad=10)
                 ax1.set_xticks(leads)
                 ax1.set_xlim([leads[0],leads[-1]])
                 ax1.tick_params(axis='y', pad=15)
                 ax1.set_ylabel("Mean")
                 #ax1.set_ylim()
                 #difference from model 1
                 ax2.grid(True)
                 ax2.tick_params(axis='x', pad=10)
                 ax2.set_xlabel("Forecast Hour")
                 ax2.tick_params(axis='y', pad=15)
                 ax2.set_ylabel("Difference")
                 #ax2.set_ylim()
                 ax2.set_title("Difference from "+model_names[0], loc="left")
                 boxstyle = matplotlib.patches.BoxStyle("Square", pad=0.25)
                 props = {'boxstyle': boxstyle,
                 'facecolor': 'white',
                 'linestyle': 'solid',
                 'linewidth': 1,
                 'edgecolor': 'black',}
                 ax2.text(0.7055, 1.05, "Note: differences outside the outline bars are significant\n at the 95% confidence interval", ha="center", va="center", fontsize=10, bbox=props, transform=ax2.transAxes)
                 logger.debug("Plotting "+stat_now+" lead forecst hour means for "+model_now)
                 ax1.plot(leads, model_now_stat_now_means, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_now)
                 ax2.plot(leads, np.zeros_like(leads), color=colors[m-1], ls='-', linewidth=2.0)
                 model1_stat_now_means = model_now_stat_now_means
             else:
                 #get CI data
                 #intialize data array
                 model_now_stat_now_CI = np.ones_like(leads) * np.nan
                 #get forecast hour mean file
                 model_now_CI_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_CI_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
                 if os.path.exists(model_now_CI_file):
                     nrow = sum(1 for line in open(model_now_CI_file))
                     if nrow == 0: #file blank
                         logger.warning("Model "+str(m)+" "+model_now+": "+model_now_CI_file+" empty")
                     else:
                         logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_CI_file)
                         mean_cols = [ "LEADS", "VALS" ]
                         model_now_data_CI = pandas.read_csv(model_now_CI_file, sep=" ", header=None, names=mean_cols)
                         model_now_stat_now_leads_CI = model_now_data_CI.loc[:]['LEADS']
                         model_now_stat_now_vals_CI = model_now_data_CI.loc[:]['VALS']
                         #check for any missing data in current model for requested forecast leads
                         for l in range(len(leads)):
                             if leads[l] == model_now_stat_now_leads_CI[l]:
                                 if model_now_stat_now_vals_CI[l] == '--':
                                     model_now_stat_now_CI[l] = np.nan
                                 else:
                                     model_now_stat_now_CI[l] = model_now_stat_now_vals_CI[l]
                             else:
                                 ll = np.where(model_now_stat_now_leads_CI == leads[l])[0]
                                 if len(ll) != 0:
                                     if model_now_stat_now_vals_CI[ll[0]] == '--':
                                         model_now_stat_now_means_CI[l] = np.nan
                                     else:
                                         model_now_stat_now_means_CI[l] = model_now_stat_now_vals_CI[ll[0]]
                                 else:
                                     model_now_stat_now_means_CI[l] = np.nan
                 else:
                     logger.warning("Model "+str(m)+" "+model_now+": "+model_now_CI_file+" missing")
                 model_now_stat_now_CI = np.ma.masked_invalid(model_now_stat_now_CI)
                 logger.debug("Plotting "+stat_now+" lead forecst hour means for "+model_now)
                 ax1.plot(leads, model_now_stat_now_means, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_now)
                 logger.debug("Plotting "+stat_now+" difference and CIs for "+model_now+" from "+model_names[0])
                 ax2.plot(leads, model_now_stat_now_means - model1_stat_now_means, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7)
                 ax2.bar(leads, 2*model_now_stat_now_CI, bottom=-1*model_now_stat_now_CI, color='None', width=1.5+((m-2)*0.2), edgecolor=colors[m-1], linewidth='1')
             m+=1
        ax1.legend(bbox_to_anchor=(0.0, 1.02, 1.0, .102), loc=3, ncol=nmodels, fontsize='13', mode="expand", borderaxespad=0.)
        ax1.set_title("Fcst: "+fcst_var_name+"_"+fcst_var_level_now+" Obs: "+obs_var_name+"_"+obs_var_level_now+" "+str(stat_formal_name_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" Means\n\n", fontsize=14, fontweight='bold')
        logger.info("Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+"_"+grid+region+".png")
        plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+"_"+grid+region+".png", bbox_inches='tight')
        s+=1
    vl+=1
