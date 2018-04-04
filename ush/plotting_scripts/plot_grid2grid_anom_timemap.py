#!/usr/bin/env python
'''
Program Name: plot_grid2grid_anom_timemap.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make lead - date plots
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
###cmap = cmocean.cm.haline_r
###cmap_diff = cmocean.cm.balance
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
lead_list = os.environ['LEAD_LIST'].replace(", ", ",").split(",")
leads = np.asarray(lead_list).astype(float)
region = os.environ['REGION']
grid = "G2"
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_level = os.environ['FCST_VAR_LEVEL']
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_level = os.environ['OBS_VAR_LEVEL']
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
logger.debug("----- for "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
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
         gs.update(wspace=0.1, hspace=0.1)
     elif nmodels == 2:
         fig = plt.figure(figsize=(10,12))
         gs = gridspec.GridSpec(2,1)
         gs.update(wspace=0.1, hspace=0.2)
     elif nmodels > 2 and nmodels <= 4:
         fig = plt.figure(figsize=(15,10))
         gs = gridspec.GridSpec(2,2)
         gs.update(wspace=0.25, hspace=0.25)
     elif nmodels > 4 and nmodels <= 6:
         fig = plt.figure(figsize=(19,10))
         gs = gridspec.GridSpec(2,3)
         gs.update(wspace=0.3, hspace=0.25)
     elif nmodels > 6:
         fig = plt.figure(figsize=(21,12))
         gs = gridspec.GridSpec(3,3)
         gs.update(wspace=0.25, hspace=0.25)
     m=1
     while m <= nmodels: #loop over models
          model_now_stat_now_dates_array = np.empty([len(leads), len(dates)])
          model_now = model_list[m-1]
          logger.debug(str(m)+" "+model_now)
          lead_count = 0 
          for lead in lead_list:
              lead_now = lead.zfill(2)
              model_now_stat_file = stat_files_input_dir+"/"+cycle+"Z/"+model_now+"/"+region+"/"+model_now+"_f"+lead_now+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat"
              if os.path.exists(model_now_stat_file):
                  nrow = sum(1 for line in open(model_now_stat_file))
                  if nrow == 0: #file blank if stat analysis filters were not all met
                      logger.warning(model_now_stat_file+" was empty! Setting to NaN")
                      model_now_stat_now_dates_vals = np.ones_like(dates)*np.nan
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
                          ufabar = parsum[:,0]
                          vfavar = parsum[:,1]
                          uoabar = parsum[:,2]
                          voabar = parsum[:,3]
                          uvfoabar = parsum[:,4]
                          uvffabar = parsum[:,5]
                          uvooabar = parsum[:,6]
                          if stat_now == 'acc':
                              model_now_stat_now_vals = np.ma.masked_invalid((uvfoabar)/np.sqrt(uvffabar - uvooabar))
                          else:
                              logger.error(stat_now+" cannot be computed!")
                              exit(1)
                      else:
                          fabar = parsum[:,0]
                          oabar = parsum[:,1]
                          foabar = parsum[:,2]
                          ffabar = parsum[:,3]
                          ooabar = parsum[:,4]
                          if stat_now == 'acc':
                              model_now_stat_now_vals = np.ma.masked_invalid((foabar - (fabar*oabar))/np.sqrt((ffabar - (fabar)**2)*(ooabar - (oabar)**2)))     
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
                              model_now_stat_now_dates_vals[d] = model_now_stat_now_vals[dd[0]]
                          else:
                              model_now_stat_now_dates_vals[d] = np.nan
              else:
                  logger.error(model_now_stat_file+" NOT FOUND! Setting to NaN")
                  nrow = 0
                  model_now_stat_now_dates_vals = np.ones_like(dates)*np.nan
              model_now_stat_now_dates_vals = np.ma.masked_invalid(model_now_stat_now_dates_vals)
              model_now_stat_now_dates_array[lead_count,:] = model_now_stat_now_dates_vals
              lead_count+=1
          #create image directory if does not exist
          if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
             os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
          #make plot
          ax = plt.subplot(gs[m-1])
          yy,xx = np.meshgrid(dates, leads)
          ax.contourf(xx, yy, np.ones_like(xx)*np.nan) #contour valid dates and a forecast hour ranges
          if m == 1:
              logger.debug("Plotting "+stat_now+" lead - date for "+model_now)
              C0 = ax.contourf(xx, yy, model_now_stat_now_dates_array, cmap=cmap, extend='both')
              C = ax.contour(xx, yy, model_now_stat_now_dates_array, levels=C0.levels, colors='k', linewidths=1.0)
              ax.clabel(C,C0.levels, fmt='%1.2f', inline=True, fontsize=12.5)
              ax.set_title(model_now, loc='left')
              model_1_stat_now_dates_array = model_now_stat_now_dates_array
          elif m == 2:
              logger.debug("Plotting "+stat_now+" lead - date for "+model_now+" - "+model_list[0])
              c1levels = pd.get_clevels(model_now_stat_now_dates_array-model_1_stat_now_dates_array)
              C1 = ax.contourf(xx, yy, model_now_stat_now_dates_array-model_1_stat_now_dates_array, levels=c1levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric='True'), extend='both')
              C = ax.contour(xx, yy, model_now_stat_now_dates_array-model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
              ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
              ax.set_title(model_now+'-'+model_list[0], loc='left')
          elif m > 2:
              logger.debug("Plotting "+stat_now+" lead - date for "+model_now+" - "+model_list[0])
              ax.contourf(xx, yy, model_now_stat_now_dates_array-model_1_stat_now_dates_array, levels=C1.levels, cmap=cmap_diff, extend='both')
              C = ax.contour(xx, yy, model_now_stat_now_dates_array-model_1_stat_now_dates_array, levels=C1.levels, colors='k', linewidths=1.0)
              ax.clabel(C,C1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
              ax.set_title(model_now+'-'+model_list[0], loc='left')
          ax.grid(True)
          ax.set_xlabel("Forecast Hour")
          ax.set_xticks(leads)
          ax.set_xlim([leads[0],leads[-1]])
          ax.set_ylabel(date_filter_method+" Date")
          ax.set_ylim([dates[0],dates[-1]])
          if len(dates) <= 31:
              ax.yaxis.set_major_locator(md.DayLocator(interval=7))
              ax.yaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
              ax.yaxis.set_minor_locator(md.DayLocator())
          else:
              ax.yaxis.set_major_locator(md.MonthLocator())
              ax.yaxis.set_major_formatter(md.DateFormatter('%b%Y'))
              ax.yaxis.set_minor_locator(md.DayLocator())
          ax.tick_params(axis='x', pad=10)
          ax.tick_params(axis='y', pad=15)
          m+=1
     fig.suptitle("Fcst: "+fcst_var_name+"_"+fcst_var_level+" Obs: "+obs_var_name+"_"+obs_var_level+" "+str(stat_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+"\n\n", fontsize=14, fontweight='bold')
     logger.debug("---- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_timemap_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png")
     plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_timemap_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png", bbox_inches='tight')
     s+=1
print(" ")
