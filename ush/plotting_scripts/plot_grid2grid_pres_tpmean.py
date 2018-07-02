#!/usr/bin/env python
'''
Program Name: plot_grid2grid_pres_tpmean.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_grid2grid_pres_ts.py to make lead-pressue plots
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
import matplotlib.gridspec as gridspec
import plot_defs as pd
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
###import cmocean
###cmap_bias = cmocean.cm.curl
###cmap = cmocean.cm.tempo
###cmap_diff = cmocean.cm.balance
cmap_bias = plt.cm.PiYG_r
cmap = plt.cm.BuPu
cmap_diff = plt.cm.coolwarm
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
stat_files_input_dir = os.environ['STAT_FILES_INPUT_DIR']
model_list = os.environ['MODEL_LIST'].replace(", ", ",").split(",")
nmodels = len(model_list)
cycle = os.environ['CYCLE']
region = os.environ['REGION']
lead_list = os.environ['LEAD_LIST'].replace(", ", ",").split(",")
leads = np.asarray(lead_list).astype(float)
grid = "G2"
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_levels_list = os.environ['FCST_VAR_LEVELS_LIST'].replace(", P", ",P").split(",")
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_levels_list = os.environ['OBS_VAR_LEVELS_LIST'].replace(", P", ",P").split(",")
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
plotting_out_dir = os.environ['PLOTTING_OUT_DIR']
####################################################################
logger.info("------> Running "+os.path.realpath(__file__))
logger.debug("----- with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z region"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
#############################################################################
##### Read data in data, compute statistics, and plot
#read in data
s=1
while s <= nstats: #loop over statistics
     stat_now = plot_stats_list[s-1]
     logger.debug("---- "+stat_now)
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
     elif nmodels > 6:
         fig = plt.figure(figsize=(21,17))
         gs = gridspec.GridSpec(3,3)
         gs.update(wspace=0.35, hspace=0.25)
     m=1
     while m <= nmodels: #loop over models
         model_now_stat_now_means_array = np.empty([len(leads), nlevels])
         model_now = model_list[m-1]
         logger.debug(str(m)+" "+model_now)
         vl = 1
         while vl <= nlevels:
             fcst_var_level_now = fcst_var_levels_list[vl-1]
             obs_var_level_now = obs_var_levels_list[vl-1]
             #get forecast hour mean file
             model_now_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
             if os.path.exists(model_now_mean_file):
                 nrow = sum(1 for line in open(model_now_mean_file))
                 if nrow == 0: #file blank
                     logger.warning(model_now_mean_file+" was empty! Setting to NaN")
                     model_now_stat_now_means_array[:,vl-1] = np.ones_like(leads) * np.nan
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
                     model_now_leads = data_array[:,0].astype(float)
                     model_now_mean = data_array[:,1]
                     model_now_mean[model_now_mean == '--'] = np.nan    
                     model_now_stat_now_means_array[:,vl-1] = model_now_mean
                     #check for missing data
                     for l in range(len(leads)):
                         if leads[l] == model_now_leads[l]:
                              model_now_stat_now_means_array[l,vl-1] = model_now_stat_now_means_array[l,vl-1]
                         else:
                            ll = np.where(model_now_leads == leads[l])[0]
                            if len(ll) != 0:
                                 model_now_stat_now_means_array[l,vl-1] = model_now_stat_now_means_array[ll[0],vl-1]
                            else:
                                 model_now_stat_now_means_array[l,vl-1] = np.nan

             else:
                 logger.error(model_now_mean_file+" NOT FOUND! Setting to NaN")
                 model_now_stat_now_means_array[:,vl-1] = np.ones_like(leads) * np.nan
             vl+=1
         model_now_stat_now_means_array = model_now_stat_now_means_array.astype(float)
         model_now_stat_now_means_array = np.ma.masked_array(model_now_stat_now_means_array, mask=model_now_stat_now_means_array == np.nan)
         #create image directory if does not exist
         if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
            os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
         #make plot
         ax = plt.subplot(gs[m-1])
         yy,xx = np.meshgrid(fcst_var_levels_num, leads)
         if m == 1:
             logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now)
             if stat_now == 'bias':
                 c0levels = pd.get_clevels(model_now_stat_now_means_array)
                 C0 = ax.contourf(xx, yy, model_now_stat_now_means_array, levels=c0levels, cmap=cmap_bias, locator=matplotlib.ticker.MaxNLocator(symmetric=True), extend='both')      
             else:
                 C0 = ax.contourf(xx, yy, model_now_stat_now_means_array, cmap=cmap, extend='both')
                 model_1_stat_now_dates_array =  model_now_stat_now_means_array
             C = ax.contour(xx, yy, model_now_stat_now_means_array, levels=C0.levels, colors='k', linewidths=1.0)
             ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
             ax.set_title(model_now, loc='left')
         elif m == 2:
             if stat_now == 'bias':
                 logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now)
                 C1 = ax.contourf(xx, yy, model_now_stat_now_means_array, levels=C0.levels, cmap=cmap_bias, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_means_array, levels=C0.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now, loc='left')
             else:
                 logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now+" - "+model_list[0])
                 c1levels = pd.get_clevels(model_now_stat_now_means_array -  model_1_stat_now_dates_array)
                 C1 = ax.contourf(xx, yy, model_now_stat_now_means_array -  model_1_stat_now_dates_array, levels=c1levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_means_array -  model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now+'-'+model_list[0], loc='left')
         elif m > 2:
             if stat_now == 'bias':
                 logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now)
                 ax.contourf(xx, yy, model_now_stat_now_means_array, levels=C0.levels, cmap=cmap_bias, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_means_array, levels=C0.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now, loc='left')
             else:
                 logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now+" - "+model_list[0])
                 ax.contourf(xx, yy, model_now_stat_now_means_array -  model_1_stat_now_dates_array, levels=c1levels, cmap=cmap_diff, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_means_array -  model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now+'-'+model_list[0], loc='left')
         ax.grid(True)
         ax.set_xlabel("Forecast Hour")
         ax.set_xticks(leads)
         ax.set_xlim([leads[0],leads[-1]])
         ax.set_ylabel('Pressure Level')
         ax.set_yscale("log")
         ax.invert_yaxis()
         ax.minorticks_off()
         ax.set_yticks(fcst_var_levels_num)
         ax.set_yticklabels(fcst_var_levels_num)
         ax.set_ylim([fcst_var_levels_num[0],fcst_var_levels_num[-1]])
         ax.tick_params(axis='x', pad=10)
         ax.tick_params(axis='y', pad=15)
         m+=1
     if nmodels > 1:
         cax = fig.add_axes([0.1, -0.05, 0.8, 0.05])
         cbar = fig.colorbar(C1, cax=cax, orientation='horizontal', ticks=C1.levels)
     fig.suptitle("Fcst: "+fcst_var_name+" Obs: "+obs_var_name+" "+str(stat_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" Mean\n", fontsize=14, fontweight='bold') 
     logger.debug("---- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png")
     plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png", bbox_inches='tight')
     s+=1
