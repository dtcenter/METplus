#!/usr/bin/env python
'''
Program Name: plot_grid2grid_pres_tpmean.py
Contact(s): Mallory Row
Abstract: Reads mean forecast hour files from plot_grid2grid_pres_ts.py to make lead-pressue plots
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
edate = os.environ['END_T']
eyear = int(edate[:4])
emon = int(edate[4:6])
emonth = month_name[emon-1]
eday = int(edate[6:8])
date_filter_method = os.environ['DATE_FILTER_METHOD']
#input info
stat_files_input_dir_base = os.environ['STAT_FILES_INPUT_DIR']
stat_files_input_dir = os.path.join(stat_files_input_dir_base, "pres")
model_names = os.environ['MODEL_NAMES'].replace(" ", ",").split(",")
nmodels = len(model_names)
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
plotting_out_dir = os.path.join(plotting_out_dir_base, "pres")
####################################################################
logger.info(" ")
logger.info("Running "+os.path.realpath(__file__))
logger.info("with "+date_filter_method+" start date:"+sdate+" "+date_filter_method+" end date:"+edate+" cycle:"+cycle+"Z region"+region+" fcst var:"+fcst_var_name+" obs var:"+obs_var_name)
#############################################################################
##### Create image directory if does not exist
if not os.path.exists(os.path.join(plotting_out_dir, "imgs", cycle+"Z")):
    os.makedirs(os.path.join(plotting_out_dir, "imgs", cycle+"Z"))
##### Read data in data and plot
#read in data
s=1
while s <= nstats: #loop over statistics
    stat_now = plot_stats_list[s-1]
    stat_formal_name_now = pd.get_stat_formal_name(stat_now)
    logger.debug(stat_now)
    create_data_array = True
    m=1
    while m <= nmodels: #loop over models
        model_now = model_names[m-1]
        vl = 1
        while vl <= nlevels:
            fcst_var_level_now = fcst_var_levels_list[vl-1]
            obs_var_level_now = obs_var_levels_list[vl-1]
            model_now_mean_file = plotting_out_dir+"/data/"+cycle+"Z/"+model_now+"/"+stat_now+"_mean_"+region+"_fcst"+fcst_var_name+fcst_var_level_now+"_obs"+obs_var_name+obs_var_level_now+".txt"
            if os.path.exists(model_now_mean_file):
                nrow = sum(1 for line in open(model_now_mean_file))
                if nrow == 0: #file blank if stat analysis filters were not all met
                    logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" empty")
                else:
                    logger.debug("Model "+str(m)+" "+model_now+": found "+model_now_mean_file)
                    #intialize data array
                    model_now_stat_now_means = np.ones_like(leads) * np.nan
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
                    #if first model, initialize partial sum data array for all models and all dates
                    if create_data_array:
                        stat_now_means = np.full([nmodels,len(leads),nlevels], np.nan)
                        create_data_array = False
                    stat_now_means[m-1, :, vl-1] = model_now_stat_now_means
            else:
                logger.warning("Model "+str(m)+" "+model_now+": "+model_now_mean_file+" missing") 
            vl+=1
        m+=1
    stat_now_means = np.ma.masked_invalid(stat_now_means)
    #do event equalization, if requested
    if event_equalization:
        logger.debug("Doing event equalization")
        vl = 1
        while vl <= nlevels:
            stat_now_means[:,:,vl-1] = np.ma.mask_cols(stat_now_means[:,:,vl-1])
            vl+=1
    #make plot
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
    elif nmodels > 6 and nmodels <=9:
        fig = plt.figure(figsize=(21,17))
        gs = gridspec.GridSpec(3,3)
        gs.update(wspace=0.35, hspace=0.25)
    else:
        logger.error("Too many models selected, max. is 9")
        exit(1)
    m=1
    yy,xx = np.meshgrid(fcst_var_levels_num, leads)
    while m <= nmodels: #loop over models
        model_now = model_names[m-1]
        logger.debug(str(m)+" "+model_now)
        model_now_stat_now_means = stat_now_means[m-1,:,:]
        #plot
        ax = plt.subplot(gs[m-1])
        if stat_now == 'bias':
            logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now)
            ax.set_title(model_now, loc='left')
            if m == 1:
                clevels_bias = pd.get_clevels(model_now_stat_now_means)
                CFm1 = ax.contourf(xx, yy, model_now_stat_now_means, levels=clevels_bias, cmap=cmap_bias, locator=matplotlib.ticker.MaxNLocator(symmetric=True), extend='both')
                Cm1 = ax.contour(xx, yy, model_now_stat_now_means, levels=CFm1.levels, colors='k', linewidths=1.0)
                ax.clabel(Cm1, CFm1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
            else:
                CFm = ax.contourf(xx, yy, model_now_stat_now_means, levels=CFm1.levels, cmap=cmap_bias, extend='both')
                Cm = ax.contour(xx, yy, model_now_stat_now_means, levels=CFm1.levels, colors='k', linewidths=1.0)
                ax.clabel(Cm, CFm.levels, fmt='%1.2f', inline=True, fontsize=12.5)
        else:
            if m == 1:
                logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now)
                model1_stat_now_means = model_now_stat_now_means
                ax.set_title(model_now, loc='left')
                CFm1 = ax.contourf(xx, yy, model_now_stat_now_means, cmap=cmap, extend='both')
                Cm1 = ax.contour(xx, yy, model_now_stat_now_means, levels=CFm1.levels, colors='k', linewidths=1.0)
                ax.clabel(Cm1, CFm1.levels, fmt='%1.2f', inline=True, fontsize=12.5)
            else:
                logger.debug("Plotting "+stat_now+" leads - pressure for "+model_now+" - "+model_names[0])
                ax.set_title(model_now+'-'+model_names[0], loc='left')
                if m == 2:
                    clevels_diff = pd.get_clevels(model_now_stat_now_means - model1_stat_now_means)
                    CFm2 = ax.contourf(xx, yy, model_now_stat_now_means - model1_stat_now_means, levels=clevels_diff, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                    Cm2 = ax.contour(xx, yy, model_now_stat_now_means - model1_stat_now_means, levels=CFm2.levels, colors='k', linewidths=1.0)
                    ax.clabel(Cm2, CFm2.levels, fmt='%1.2f', inline=True, fontsize=12.5)
                else:
                    CFm = ax.contourf(xx, yy, model_now_stat_now_means - model1_stat_now_means, levels=CFm2.levels, cmap=cmap_diff, locator=matplotlib.ticker.MaxNLocator(symmetric=True),extend='both')
                    Cm = ax.contour(xx, model_now_stat_now_means - model1_stat_now_means, levels=CFm2.levels, colors='k', linewidths=1.0)
                    ax.clabel(Cm, CFm.levels, fmt='%1.2f', inline=True, fontsize=12.5)
        ax.grid(True)
        ax.tick_params(axis='x', pad=10)
        ax.set_xlabel("Forecast Hour")
        ax.set_xticks(leads)
        ax.set_xlim([leads[0],leads[-1]])
        ax.tick_params(axis='y', pad=15)
        ax.set_ylabel("Pressure Level")
        ax.set_yscale("log")
        ax.invert_yaxis()
        ax.minorticks_off()
        ax.set_yticks(fcst_var_levels_num)
        ax.set_yticklabels(fcst_var_levels_num)
        ax.set_ylim([fcst_var_levels_num[0],fcst_var_levels_num[-1]])
        m+=1
    if nmodels > 1:
        cax = fig.add_axes([0.1, -0.05, 0.8, 0.05])
        if stat_now == 'bias':
            cbar = fig.colorbar(CFm, cax=cax, orientation='horizontal', ticks=CFm.levels)
        else:
            cbar = fig.colorbar(CFm2, cax=cax, orientation='horizontal', ticks=CFm2.levels)
    fig.suptitle("Fcst: "+fcst_var_name+" Obs: "+obs_var_name+" "+str(stat_formal_name_now)+'\n'+grid+"-"+region+" "+date_filter_method+" "+cycle+"Z "+str(sday)+smonth+str(syear)+"-"+str(eday)+emonth+str(eyear)+" Mean\n", fontsize=14, fontweight='bold') 
    logger.info("Saving image as "+plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png")
    plt.savefig(plotting_out_dir+"/imgs/"+cycle+"Z/"+stat_now+"_fhrmeans_fcst"+fcst_var_name+"_obs"+obs_var_name+"_"+grid+region+"_tp.png", bbox_inches='tight')
    s+=1
