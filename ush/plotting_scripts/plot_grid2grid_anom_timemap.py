#!/usr/bin/env python
'''
Program Name: plot_grid2grid_anom_timemap.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make lead - date plots
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
import datetime as datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.gridspec as gridspec
import plot_defs as pd
import warnings
import logging
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
edate = os.environ['END_T']
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
total_days = len(dates)
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
stat_files_input_dir_base = os.environ['STAT_FILES_INPUT_DIR']
stat_files_input_dir = os.path.join(stat_files_input_dir_base, "anom")
model_names = os.environ['MODEL_NAMES'].replace(" ", ",").split(",")
nmodels = len(model_names)
cycle = os.environ['CYCLE']
lead_list = os.environ['LEAD_LIST'].replace(", ", ",").split(",")
leads = np.asarray(lead_list).astype(float)
nleads = len(leads)
region = os.environ['REGION']
grid = "G2"
plot_stats_list = os.environ['PLOT_STATS_LIST'].replace(", ", ",").split(",")
nstats = len(plot_stats_list)
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_level = os.environ['FCST_VAR_LEVEL']
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_level = os.environ['OBS_VAR_LEVEL']
event_equalization = True
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
plotting_out_dir = os.path.join(plotting_out_dir_base, "anom")
####################################################################
logger.info(" ")
logger.info("Running "+os.path.realpath(__file__))
logger.info("with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
#############################################################################
##### Create image directory if does not exist
if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
    os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
##### Read data in data, compute statistics, and plot
#read in data
logger.info("Gathering data")
create_data_arrays = True
m=1
while m <= nmodels: #loop over models
    model_now = model_names[m-1]
    lead_count = 0 
    for lead in lead_list:
        lead_now = lead.zfill(2)
        model_now_stat_file = stat_files_input_dir+"/"+cycle+"Z/"+model_now+"/"+region+"/"+model_now+"_f"+lead_now+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat"
        if os.path.exists(model_now_stat_file):
            nrow = sum(1 for line in open(model_now_stat_file))
            if nrow == 0: #file blank if stat analysis filters were not all met
                logger.warning("Model "+str(m)+" "+model_now+": "+model_now_stat_file+" empty")
            else:
                logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_stat_file)
                met_cols = [ "VERSION", "MODEL", "DESC", "FCST_LEAD", "FCST_VALID_BEG", "FCST_VALID_END", "OBS_LEAD", "OBS_VALID_BEG", "OBS_VALID_END", "FCST_VAR", "FCST_LEV", "OBS_VAR", "OBS_LEV", "OBTYPE", "VX_MASK", "INTERP_MTHD", "INTERP_PNTS", "FCST_THRESH", "OBS_THRESH", "COV_THRESH", "ALPHA", "LINE_TYPE", "TOTAL", "A", "B", "C", "D", "E", "F", "G" ]
                model_now_data = pandas.read_csv(model_now_stat_file, sep=" ", skiprows=1, skipinitialspace=True, header=None, names=met_cols)
                #format dates in stat file
                model_now_dates = model_now_data.loc[:]['FCST_VALID_BEG']
                dateformat = "%Y%m%d_%H%M%S"
                model_now_dates_formatted = np.zeros_like(model_now_dates)
                for d in range(len(model_now_dates)):
                    if date_filter_method == 'Valid':
                        date_now = datetime.datetime.strptime(model_now_dates[d], dateformat)
                    elif date_filter_method == 'Initialization':
                        date_now = datetime.datetime.strptime(model_now_dates[d], dateformat) - datetime.timedelta(hours=lead_int)
                    model_now_dates_formatted[d] = md.date2num(date_now)
                #parse between sl1l2 and vl1l2 data
                data_line_type = model_now_data.loc[0]['LINE_TYPE']
                if data_line_type == 'SAL1L2':
                    #if create partial sum data arrays for all models and all dates, if not created yet
                    if create_data_arrays:
                        fabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        oabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        foabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        ffabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        ooabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        create_data_arrays = False
                    #read data for current model
                    #check for any missing data in current model from requested date span,
                    #arrange data in chronological order, and put in array
                    for d in range(total_days):
                         dd = np.where(model_now_dates_formatted == dates[d])[0]
                         if len(dd) == 1:
                             fabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['A']
                             oabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['B']
                             foabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['C']
                             ffabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['D']
                             ooabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['E']
                elif data_line_type == 'VAL1L2':
                    #if first model, initialize partial sum data arrays for all models and all dates
                    if create_data_arrays:
                        ufabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        vfabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        uoabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        voabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        uvfoabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        uvffabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        uvooabar_models_dates = np.full([nmodels,nleads,total_days], np.nan)
                        create_data_arrays = False
                    #read data for current model
                    #check for any missing data in current model from requested date span,
                    #arrange data in chronological order, and put in array
                    for d in range(total_days):
                        dd = np.where(model_now_dates_formatted == dates[d])[0]
                        if len(dd) == 1:
                            ufabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['A']
                            vfabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['B']
                            uoabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['C']
                            voabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['D']
                            uvfoabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['E']
                            uvffabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['F']
                            uvooabar_models_dates[m-1, lead_count, d] = model_now_data.loc[dd[0]]['G']
        else:
            logger.warning("Model "+str(m)+" "+model_now+": "+model_now_stat_file+" missing")
        lead_count+=1 
    m+=1
#compute statistics
logger.info("Calculating and plotting statistics")
s=1
while s <= nstats: #loop over statistics
    stat_now = plot_stats_list[s-1]
    stat_formal_name_now = pd.get_stat_formal_name(stat_now)
    logger.debug(stat_now)
    if data_line_type == 'SAL1L2':
        if stat_now == 'acc':
            stat_now_vals = np.ma.masked_invalid((foabar_models_dates - (fabar_models_dates*oabar_models_dates))/np.sqrt((ffabar_models_dates - (fabar_models_dates)**2)*(ooabar_models_dates - (oabar_models_dates)**2)))
        else:
            logger.error(stat_now+" cannot be computed")
            exit(1)    
    elif data_line_type == 'VAL1L2':
        if stat_now == 'acc':
            stat_now_vals = np.ma.masked_invalid((uvfoabar_models_dates)/np.sqrt(uvffabar_models_dates - uvooabar_models_dates))
        else:
            logger.error(stat_now+" cannot be computed") 
            exit(1)
    #do event equalization, if requested
    if event_equalization:
        logger.debug("Doing event equalization")
        for l in range(len(leads)):
            stat_now_vals[:,l,:] = np.ma.mask_cols(stat_now_vals[:,l,:])
    #make plot
    if nmodels == 1:
        fig = plt.figure(figsize=(10,12))
        gs = gridspec.GridSpec(2,1)
        gs.update(wspace=0.1, hspace=0.1)
    elif nmodels == 2:
        fig = plt.figure(figsize=(10,12))
        gs = gridspec.GridSpec(2,1)
        gs.update(wspace=0.1, hspace=0.2)
    elif nmodels > 2 and nmodels <= 4:
        fig = plt.figure(figsize=(15,12))
        gs = gridspec.GridSpec(2,2)
        gs.update(wspace=0.25, hspace=0.25)
    elif nmodels > 4 and nmodels <= 6:
        fig = plt.figure(figsize=(19,12))
        gs = gridspec.GridSpec(2,3)
        gs.update(wspace=0.3, hspace=0.25)
    elif nmodels > 6 and nmodels <=9:
        fig = plt.figure(figsize=(21,17))
        gs = gridspec.GridSpec(3,3)
        gs.update(wspace=0.25, hspace=0.25)
    else:
        logger.error("Too many models selected, max. is 9")
        exit(1)
    m=1
    yy,xx = np.meshgrid(dates, leads)
    while m <= nmodels: #loop over models
        model_now = model_names[m-1]
        logger.debug(str(m)+" "+model_now)
        model_now_stat_now_vals = stat_now_vals[m-1,:,:]
        #plot 
        ax = plt.subplot(gs[m-1])
        if m == 1:
            logger.debug("Plotting "+stat_now+" lead - date for "+model_now)
            CFm1 = ax.contourf(xx, yy, model_now_stat_now_vals, cmap=cmap, extend='both')
            Cm1 = ax.contour(xx, yy, model_now_stat_now_vals, levels=CFm1.levels, colors='k', linewidths=1.0)
            ax.clabel(Cm1, CFm1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
            ax.set_title(model_now, loc='left')
            model1_stat_now_vals = model_now_stat_now_vals
        else:
            logger.debug("Plotting "+stat_now+" lead - date for "+model_now+" - "+model_names[0])
            ax.set_title(model_now+'-'+model_names[0], loc='left')
            if m == 2:
               clevels_diff = pd.get_clevels(model_now_stat_now_vals - model1_stat_now_vals)
               CFm2 = ax.contourf(xx, yy, model_now_stat_now_vals - model1_stat_now_vals, levels=clevels_diff, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
               Cm2 = ax.contour(xx, yy, model_now_stat_now_vals - model1_stat_now_vals, levels=CFm2.levels, colors='k', linewidths=1.0)
               ax.clabel(Cm2, CFm2.levels, fmt='%1.2f', inline=True, fontsize=12.5) 
            else:
               CFm = ax.contourf(xx, yy, model_now_stat_now_vals - model1_stat_now_vals, levels=CFm2.levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
               Cm = ax.contour(xx, model_now_stat_now_vals - model1_stat_now_vals, levels=CFm2.levels, colors='k', linewidths=1.0)
               ax.clabel(Cm, CFm.levels, fmt='%1.2f', inline=True, fontsize=12.5) 
        ax.grid(True)
        ax.tick_params(axis='x', pad=10)
        ax.set_xlabel("Forecast Hour")
        ax.set_xticks(leads)
        ax.set_xlim([leads[0],leads[-1]])
        ax.tick_params(axis='y', pad=10)
        ax.set_ylabel(date_filter_method+" Date")
        ax.set_ylim([dates[0],dates[-1]])
        if len(dates) <= 31:
            ax.yaxis.set_major_locator(md.DayLocator(interval=7))
            ax.yaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
            ax.yaxis.set_minor_locator(md.DayLocator())
        else:
            ax.yxaxis.set_major_locator(md.MonthLocator())
            ax.yaxis.set_major_formatter(md.DateFormatter('%b%Y'))
            ax.yaxis.set_minor_locator(md.DayLocator())
        m+=1
    if nmodels > 1:
        cax = fig.add_axes([0.1, -0.05, 0.8, 0.05])
        cbar = fig.colorbar(CFm2, cax=cax, orientation='horizontal', ticks=CFm2.levels)
    fig.suptitle("Fcst: "+fcst_var_name+"_"+fcst_var_level+" Obs: "+obs_var_name+"_"+obs_var_level+" "+str(stat_formal_name_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+"\n\n", fontsize=14, fontweight='bold')
    logger.info("Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_timemap_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png")
    plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_timemap_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+grid+region+".png", bbox_inches='tight')
    #ax.legend(bbox_to_anchor=(1.025, 1.0, 0.375, 0.0), loc='upper right', ncol=1, fontsize='13', mode="expand", borderaxespad=0.)
    s+=1
