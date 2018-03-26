#!/usr/bin/env python
'''
Program Name: plot_grid2grid_pres_tp.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make date-pressure plots
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
import datetime as datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
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
cmap_bias = plt.cm.PiYG
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
cycle_int = int(os.environ['CYCLE'])
sd = datetime.datetime(syear, smon, sday, cycle_int)
ed = datetime.datetime(eyear, emon, eday, cycle_int)+datetime.timedelta(days=1)
tdelta = datetime.timedelta(days=1)
dates = md.drange(sd, ed, tdelta)
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
stat_files_input_dir = os.environ['STAT_FILES_INPUT_DIR']
model_list = os.environ['MODEL_LIST'].replace(", ", ",").split(",")
nmodels = len(model_list)
cycle = os.environ['CYCLE']
lead = os.environ['LEAD']
region = os.environ['REGION']
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
formatter = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(logging_filename, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
ch = logging.StreamHandler()
logger.addHandler(ch)
plotting_out_dir = os.environ['PLOTTING_OUT_DIR']
####################################################################
logger.info("------> Running "+os.path.realpath(__file__))
logger.debug("----- with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z lead:"+lead+" region:"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
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
         model_now_stat_now_dates_array = np.empty([len(dates), nlevels])
         model_now = model_list[m-1]
         logger.debug(str(m)+" "+model_now)
         vl = 1
         while vl <= nlevels:
             fcst_var_level_now = fcst_var_levels_list[vl-1]
             obs_var_level_now = obs_var_levels_list[vl-1]
             model_now_stat_file = stat_files_input_dir+"/"+cycle+"Z/"+model_now+"/"+region+"/"+model_now+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".stat"
             if os.path.exists(model_now_stat_file):
                 nrow = sum(1 for line in open(model_now_stat_file))
                 if nrow == 0: #file blank if stat analysis filters were not all met
                     logger.warning(model_now_stat_file+" was empty! Setting to NaN")
                     model_now_stat_now_dates_array[:,vl-1] = np.ones_like(dates) * np.nan
                 else:
                     logger.debug("Found "+model_now_stat_file)
                     #read data file and put in array
                     data = list()
                     l = 0
                     with open(model_now_stat_file) as f:
                         for line in f:
                             if l != 0: #skip reading header file
                                 line_split = line.split()
                                 data.append(line_split)
                             l+=1
                     data_array = np.asarray(data)
                     #parse between sl1l2 and vl1l2 data and set variables
                     parsum = data_array[:,23:].astype(float)
                     if fcst_var_name == 'UGRD_VGRD' or obs_var_name == 'UGRD_VGRD':
                         ufbar = parsum[:,0]
                         vfbar = parsum[:,1]
                         uobar = parsum[:,2]
                         vobar = parsum[:,3]
                         uvfobar = parsum[:,4]
                         uvffbar = parsum[:,5]
                         uvoobar = parsum[:,6]
                         if stat_now == 'bias':
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt(uvffbar) - np.sqrt(uvoobar))
                         elif stat_now == 'rmse':
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt(uvffbar + uvoobar - (2*uvfobar)))
                         elif stat_now == 'msess':
                             mse = uvffbar + uvoobar - (2*uvfobar)
                             var_o = uvoobar - (uobar**2) - (vobar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid(1 - (mse/var_o))
                         elif stat_now == 'rsd':
                             var_f = uvffbar - (ufbar**2) - (vfbar**2)
                             var_o = uvoobar - (uobar**2) - (vobar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid((np.sqrt(var_f))/(np.sqrt(var_o)))
                         elif stat_now == 'rmse_md':
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt((ufbar - uobar)**2 + (vfbar - vobar)**2))
                         elif stat_now == 'rmse_pv':
                             var_f = uvffbar - (ufbar**2) - (vfbar**2)
                             var_o = uvoobar - (uobar**2) - (vobar**2)
                             R = (uvfobar -  (ufbar*uobar) - (vfbar*vobar))/np.sqrt(var_f*var_o)
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt(var_f + var_o - (2*np.sqrt(var_f*var_o)*R)))
                         elif stat_now == 'pcor':
                             var_f = uvffbar - (ufbar**2) - (vfbar**2)
                             var_o = uvoobar - (uobar**2) - (vobar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid((uvfobar -  (ufbar*uobar) - (vfbar*vobar))/np.sqrt(var_f*var_o))
                         else:
                             logger.error(stat_now+" cannot be computed!")
                             exit(1)
                     else:
                         fbar = parsum[:,0]
                         obar = parsum[:,1]
                         fobar = parsum[:,2]
                         ffbar = parsum[:,3]
                         oobar = parsum[:,4]
                         if stat_now == 'bias':
                             model_now_stat_now_vals = np.ma.masked_invalid(fbar - obar)
                         elif stat_now == 'rmse':
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt(ffbar + oobar - (2*fobar)))
                         elif stat_now == 'msess':
                             mse = ffbar + oobar - (2*fobar)
                             var_o = oobar - (obar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid(1 - (mse/var_o))
                         elif stat_now == 'rsd':
                             var_f = ffbar - (fbar**2)
                             var_o = oobar - (obar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid((np.sqrt(var_f))/(np.sqrt(var_o)))
                         elif stat_now == 'rmse_md':
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt((fbar - obar)**2))
                         elif stat_now == 'rmse_pv':
                             var_f = ffbar - (fbar**2)
                             var_o = oobar - (obar**2)
                             R = (fobar - (fbar*obar))/np.sqrt(var_f*var_o)
                             model_now_stat_now_vals = np.ma.masked_invalid(np.sqrt(var_f + var_o - (2*np.sqrt(var_f*var_o)*R)))
                         elif stat_now == 'pcor':
                             var_f = ffbar - (fbar**2)
                             var_o = oobar - (obar**2)
                             model_now_stat_now_vals = np.ma.masked_invalid((fobar - (fbar*obar))/np.sqrt(var_f*var_o))
                         else:
                             logger.error(stat_now+" cannot be computed!")
                             exit(1)
                     #get existing model date files
                     model_now_dates_list = []
                     model_now_stat_file_dates = data_array[:,4]
                     dateformat = "%Y%m%d_%H%M%S"
                     for d in range(len(model_now_stat_file_dates)):
                         model_date = datetime.datetime.strptime(model_now_stat_file_dates[d], dateformat)
                         model_now_dates_list.append(md.date2num(model_date))
                     model_now_dates = np.asarray(model_now_dates_list)
                     #account for missing data
                     model_now_stat_now_dates_vals = np.zeros_like(dates)
                     for d in range(len(dates)):
                          dd = np.where(model_now_dates == dates[d])[0]
                          if len(dd) != 0:
                              model_now_stat_now_dates_array[d,vl-1] = model_now_stat_now_vals[dd[0]]
                          else:
                              model_now_stat_now_dates_array[d,vl-1] = np.nan
             else:
                 logger.error(model_now_stat_file+" NOT FOUND! Setting to NaN")
                 model_now_stat_now_dates_array[:,vl-1] = np.ones_like(dates) * np.nan
             vl+=1
         #create image directory if does not exist
         if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
            os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
         model_now_stat_now_dates_array = np.ma.masked_invalid(model_now_stat_now_dates_array)
         #make plot
         ax = plt.subplot(gs[m-1])
         yy,xx = np.meshgrid(fcst_var_levels_num, dates)
         if m == 1:
             logger.debug("Plotting "+stat_now+" "+date_filter_method+" date - pressure for "+model_now)
             if stat_now == 'bias':
                 c0levels = pd.get_clevels(model_now_stat_now_dates_array)
                 C0 = ax.contourf(xx, yy, model_now_stat_now_dates_array, levels=c0levels, cmap=cmap_bias, locator=matplotlib.ticker.MaxNLocator(symmetric=True), extend='both')      
             else:
                 C0 = ax.contourf(xx, yy, model_now_stat_now_dates_array, cmap=cmap, extend='both')
                 model_1_stat_now_dates_array =  model_now_stat_now_dates_array
             C = ax.contour(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, colors='k', linewidths=1.0)
             ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
             ax.set_title(model_now, loc='left')
         elif m == 2:
             if stat_now == 'bias':
                 logger.debug("Plotting "+stat_now+" "+date_filter_method+" date - pressure for "+model_now)
                 C1 = ax.contourf(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, cmap=cmap_bias, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now, loc='left')
             else:
                 logger.debug("Plotting "+stat_now+" "+date_filter_method+" date - pressure for "+model_now+" - "+model_list[0])
                 c1levels = pd.get_clevels(model_now_stat_now_dates_array -  model_1_stat_now_dates_array)
                 C1 = ax.contourf(xx, yy, model_now_stat_now_dates_array -  model_1_stat_now_dates_array, levels=c1levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_dates_array -  model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now+'-'+model_list[0], loc='left')
         elif m > 2:
             if stat_now == 'bias':
                 logger.debug("Plotting "+stat_now+" "+date_filter_method+" date - pressure for "+model_now)
                 ax.contourf(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, cmap=cmap_bias, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now, loc='left')
             else:
                 logger.debug("Plotting "+stat_now+" "+date_filter_method+" date - pressure for "+model_now+" - "+model_list[0])
                 ax.contourf(xx, yy, model_now_stat_now_dates_array -  model_1_stat_now_dates_array, levels=c1levels, cmap=cmap_diff, extend='both')
                 C = ax.contour(xx, yy, model_now_stat_now_dates_array -  model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
                 ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                 ax.set_title(model_now+'-'+model_list[0], loc='left')
         ax.grid(True)
         ax.set_xlabel(date_filter_method+" Date")
         if len(dates) <= 31:
            ax.xaxis.set_major_locator(md.DayLocator(interval=7))
            ax.xaxis.set_major_formatter(md.DateFormatter('%d%b\n%Y'))
            ax.xaxis.set_minor_locator(md.DayLocator())
         else:
            ax.xaxis.set_major_locator(md.MonthLocator())
            ax.xaxis.set_major_formatter(md.DateFormatter('%b%Y'))
            ax.xaxis.set_minor_locator(md.DayLocator())
         ax.set_xlim([dates[0],dates[-1]])
         ax.set_ylabel("Pressure Level")
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
     fig.suptitle("Fcst: "+fcst_var_name+" Obs: "+obs_var_name+" "+str(stat_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" f"+lead+"\n", fontsize=14, fontweight='bold') 
     logger.debug("---- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png")
     plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png", bbox_inches='tight')
     s+=1
print(" ")
