#!/usr/bin/env python
'''
Program Name: plot_grid2grid_pres_ts.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make time series plots
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
from scipy import stats
import datetime as datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
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
cycle_int = int(os.environ['CYCLE'])
lead_int = int(os.environ['LEAD'])
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
fcst_var_level = os.environ['FCST_VAR_LEVEL']
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_level = os.environ['OBS_VAR_LEVEL']
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
logger.debug("----- with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z lead:"+lead+" region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
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
          logger.debug(str(m)+" "+model_now)
          model_now_stat_file = stat_files_input_dir+"/"+cycle+"Z/"+model_now+"/"+region+"/"+model_now+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat"
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
                        if date_filter_method == 'Valid':
                            model_date = datetime.datetime.strptime(model_now_stat_file_dates[d], dateformat)
                        elif date_filter_method == 'Initialization':
                            model_date = datetime.datetime.strptime(model_now_stat_file_dates[d], dateformat) - datetime.timedelta(hours=lead_int)
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
              logger.warning(model_now_stat_file+" NOT FOUND! Setting to NaN")
              nrow = 0
              model_now_stat_now_dates_vals = np.ones_like(dates)*np.nan
          model_now_stat_now_dates_vals = np.ma.masked_invalid(model_now_stat_now_dates_vals)
          #write forecast hour mean to file
          if not os.path.exists(os.path.join(plotting_out_dir, "data", cycle+"Z", model_now)):
             os.makedirs(os.path.join(plotting_out_dir, "data", cycle+"Z", model_now))
          save_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".txt"
          if os.path.exists(save_mean_file):
              append_write = 'a' # append if already exists
          else:
              append_write = 'w' # make a new file if not
          logger.debug("Writing "+model_now+" f"+lead+" mean to "+save_mean_file)
          save_mean = open(save_mean_file,append_write)
          save_mean.write(lead+' '+str(model_now_stat_now_dates_vals.mean())+ '\n')
          save_mean.close()
          #calculate 95% confidence intervals for difference between model m>1 and model 1
          #first must save model 1 statistics
          if m == 1:
              model_1_stat_now_dates_vals = model_now_stat_now_dates_vals
          else:
              nobs, min_max, mean, var, skew, kurt = stats.describe(model_now_stat_now_dates_vals - model_1_stat_now_dates_vals, nan_policy='omit')
              std = np.sqrt(np.nanmean((model_now_stat_now_dates_vals - model_1_stat_now_dates_vals - mean) * (model_now_stat_now_dates_vals - model_1_stat_now_dates_vals - mean)))
              intvl = pd.intvl(nobs, std)
              #write CI to file
              save_CI_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_CI_"+region+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".txt"
              if os.path.exists(save_CI_file):
                  append_write = 'a' # append if already exists
              else:
                  append_write = 'w' # make a new file if not
              logger.debug("Writing "+model_now+"-"+model_list[0]+" f"+lead+" CI to "+save_CI_file)
              save_CI = open(save_CI_file,append_write)
              save_CI.write(lead+' '+str(intvl)+ '\n')
              save_CI.close()
          #create image directory if does not exist
          if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
             os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
          #plot individual statistic time series
          if m == 1:
              fig, ax = plt.subplots(1,1,figsize=(10,6))
              ax.plot_date(dates,np.ones_like(dates)*np.nan)
              if nrow > 0:
                  logger.debug("Plotting "+stat_now+" time series for "+model_now)
                  ax.plot_date(dates,model_now_stat_now_dates_vals, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_now+' '+str(round(model_now_stat_now_dates_vals.mean(),2))+' '+str(nrow-1))
              ax.grid(True)
              ax.set_xlabel(date_filter_method+" Date")
              ax.set_xlim([dates[0],dates[-1]])
              if len(dates) <= 31:
                  ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                  ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
                  ax.xaxis.set_minor_locator(md.DayLocator())
              else:
                  ax.xaxis.set_major_locator(md.MonthLocator())
                  ax.xaxis.set_major_formatter(md.DateFormatter('%b%Y'))
                  ax.xaxis.set_minor_locator(md.DayLocator())
              ax.tick_params(axis='x', pad=10)
              ax.tick_params(axis='y', pad=15)
          else:
              if nrow > 0:
                  logger.debug("Plotting "+stat_now+" time series for "+model_now)
                  ax.plot_date(dates,model_now_stat_now_dates_vals, color=colors[m-1], ls='-', linewidth=2.0, marker='o', markersize=7, label=model_now+' '+str(round(model_now_stat_now_dates_vals.mean(),2))+' '+str(nrow-1))
          m+=1
     ax.legend(bbox_to_anchor=(1.025, 1.0, 0.375, 0.0), loc='upper right', ncol=1, fontsize='13', mode="expand", borderaxespad=0.)
     ax.set_title("Fcst: "+fcst_var_name+"_"+fcst_var_level+" Obs: "+obs_var_name+"_"+obs_var_level+" "+str(stat_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" f"+lead+"\n", fontsize=14, fontweight='bold')
     logger.debug("---- Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png")
     plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_f"+lead+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png", bbox_inches='tight')
     s+=1
