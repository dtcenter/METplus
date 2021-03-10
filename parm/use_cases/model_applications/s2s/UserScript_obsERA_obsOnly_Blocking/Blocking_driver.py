#!/usr/bin/env python3
import sys
import os
import numpy as np
import netCDF4
import re

from Blocking import BlockingCalculation
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
from metplotpy.contributed.blocking_s2s import plot_blocking as pb
from metplotpy.contributed.blocking_s2s.CBL_plot import create_cbl_plot
from Blocking_WeatherRegime_util import find_input_files, parse_steps

def main():

    #all_steps = ["REGRID","TIMEAVE","RUNMEAN","ANOMALY","CBL","PLOTCBL","IBL","PLOTIBL","GIBL","CALCBLOCKS","PLOTBLOCKS"]
    all_steps = ["CBL","PLOTCBL","IBL","PLOTIBL","GIBL","CALCBLOCKS","PLOTBLOCKS"]

    inconfig_list = sys.argv[1:]
    steps_list_fcst,steps_list_obs,config_list = parse_steps(inconfig_list)
    config = pre_run_setup(config_list)

    if not steps_list_obs and not steps_list_fcst:
        print('No processing steps requested for either the model or observations,')
        print('no data will be processed')


    ######################################################################
    # Pre-Process Data:
    ######################################################################
    # Regrid
    #if ("REGRID" in steps_list_obs):
    #    print('Regridding Observations')
    #    regrid_config = config_metplus.replace_config_from_section(config, 'regrid_obs')
    #    RegridDataPlaneWrapper(regrid_config).run_all_times()

    #if ("REGRID" in steps_list_fcst):
    #   print('Regridding Model')
    #   regrid_config = config_metplus.replace_config_from_section(config, 'regrid_fcst')
    #   RegridDataPlaneWrapper(regrid_config).run_all_times()

    #Compute Daily Average
    #if ("TIMEAVE" in steps_list_obs):
    #    print('Computing Time Averages')
    #    daily_config = config_metplus.replace_config_from_section(config, 'daily_mean_obs')
    #    PCPCombineWrapper(daily_config).run_all_times()

    #if ("TIMEAVE" in steps_list_fcst):
    #    print('Computing Time Averages')
    #    daily_config = config_metplus.replace_config_from_section(config, 'daily_mean_fcst')
    #    PCPCombineWrapper(daily_config).run_all_times()

    #Take a running mean
    #if ("RUNMEAN" in steps_list_obs):
    #    print('Computing Obs Running means')
    #    rmean_config = config_metplus.replace_config_from_section(config, 'running_mean_obs')
    #    PCPCombineWrapper(rmean_config).run_all_times()

    #if ("RUNMEAN" in steps_list_fcst):
    #    print('Computing Model Running means')
    #    rmean_config = config_metplus.replace_config_from_section(config, 'running_mean_fcst')
    #    PCPCombineWrapper(rmean_config).run_all_times()

    #Compute anomaly
    #if ("ANOMALY" in steps_list_obs):
    #    print('Computing Obs Anomalies')
    #    anomaly_config = config_metplus.replace_config_from_section(config, 'anomaly_obs')
    #    PCPCombineWrapper(anomaly_config).run_all_times()

    #if ("ANOMALY" in steps_list_fcst):
    #    print('Computing Model Anomalies')
    #    anomaly_config = config_metplus.replace_config_from_section(config, 'anomaly_fcst')
    #    PCPCombineWrapper(anomaly_config).run_all_times()


    ######################################################################
    # Blocking Calculation and Plotting
    ######################################################################
    # Set up the data
    steps_fcst = BlockingCalculation(config,'FCST')
    steps_obs = BlockingCalculation(config,'OBS')

    # Check to see if there is a plot directory
    oplot_dir = config.getstr('Blocking','BLOCKING_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = obase+'/'+'plots'
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Check to see if CBL's are used from an obs climatology
    use_cbl_obs = config.getbool('Blocking','USE_CBL_OBS',False)

    # Calculate Central Blocking Latitude
    cbl_config = config_metplus.replace_config_from_section(config,'Blocking')
    cbl_config_init = config.find_section('Blocking','CBL_INIT_BEG')
    cbl_config_valid = config.find_section('Blocking','CBL_VALID_BEG')
    use_init =  is_loop_by_init(cbl_config)
    if use_init:
        orig_beg = config.getstr('Blocking','INIT_BEG')
        orig_end = config.getstr('Blocking','INIT_END')
        if cbl_config_init is not None:
            config.set('Blocking','INIT_BEG',config.getstr('Blocking','CBL_INIT_BEG'))
            config.set('Blocking','INIT_END',config.getstr('Blocking','CBL_INIT_END'))
            cbl_config = config_metplus.replace_config_from_section(config, 'Blocking')
    else:
        orig_beg = config.getstr('Blocking','VALID_BEG')
        orig_end = config.getstr('Blocking','VALID_END')
        if cbl_config_valid is not None:
            config.set('Blocking','VALID_BEG',config.getstr('Blocking','CBL_VALID_BEG'))
            config.set('Blocking','VALID_END',config.getstr('Blocking','CBL_VALID_END'))
            cbl_config = config_metplus.replace_config_from_section(config, 'Blocking')

    if ("CBL" in steps_list_obs):
        print('Computing Obs CBLs')
        obs_infiles,yr_obs,mth_obs,day_obs,yr_full_obs = find_input_files(cbl_config, use_init, 'OBS_BLOCKING_ANOMALY_TEMPLATE')
        cbls_obs,lats_obs,lons_obs,yr_obs,mhweight_obs = steps_obs.run_CBL(obs_infiles,yr_obs)

    if ("CBL" in steps_list_fcst) and not use_cbl_obs:
        # Add in step to use obs for CBLS
        print('Computing Forecast CBLs')
        fcst_infiles,yr_fcst,mth_fcst,day_fcst,yr_full_fcst = find_input_files(cbl_config, use_init, 'FCST_BLOCKING_ANOMALY_TEMPLATE')
        cbls_fcst,lats_fcst,lons_fcst,yr_fcst,mhweight_fcst = steps_fcst.run_CBL(fcst_infiles,yr_fcst)
    elif ("CBL" in steps_list_fcst) and use_cbl_obs:
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before using them as a forecast.')
        cbls_fcst = cbls_obs
        lats_fcst = lats_obs
        lons_fcst = lons_obs
        yr_fcst = yr_obs
        mhweight_fcst = mhweight_obs

    #Plot Central Blocking Latitude
    if ("PLOTCBL" in steps_list_obs):
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before plotting them.')
        print('Plotting Obs CBLs')
        cbl_plot_mthstr = config.getstr('Blocking','OBS_CBL_PLOT_MTHSTR')
        cbl_plot_outname = oplot_dir+'/'+config.getstr('Blocking','OBS_CBL_PLOT_OUTPUT_NAME')
        create_cbl_plot(lons_obs, lats_obs, cbls_obs, mhweight_obs, cbl_plot_mthstr, cbl_plot_outname, 
            do_averaging=True)
    if ("PLOTCBL" in steps_list_fcst):
        if not ("CBL" in steps_list_fcst):
            raise Exception('Must run forecast CBLs before plotting them.')
        print('Plotting Forecast CBLs')
        cbl_plot_mthstr = config.getstr('Blocking','FCST_CBL_PLOT_MTHSTR')
        cbl_plot_outname = oplot_dir+'/'+config.getstr('Blocking','FCST_CBL_PLOT_OUTPUT_NAME')
        create_cbl_plot(lons_fcst, lats_fcst, cbls_fcst, mhweight_fcst, cbl_plot_mthstr, cbl_plot_outname, 
            do_averaging=True)


    # Run IBL
    if use_init:
       config.set('Blocking','INIT_BEG',orig_beg)
       config.set('Blocking','INIT_END',orig_end)
    else:
        config.set('Blocking','VALID_BEG',orig_beg)
        config.set('Blocking','VALID_END',orig_end)
    ibl_config = config_metplus.replace_config_from_section(config,'Blocking')
    if ("IBL" in steps_list_obs) and not ("IBL" in steps_list_fcst):
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before running IBLs.')
        print('Computing Obs IBLs')
        obs_infiles,yr_obs,mth_obs,day_obs,yr_full_obs = find_input_files(ibl_config, use_init, 'OBS_BLOCKING_TEMPLATE')
        ibls_obs = steps_obs.run_Calc_IBL(cbls_obs,obs_infiles,yr_obs)
        daynum_obs = np.arange(0,len(ibls_obs[0,:,0]),1)
    elif ("IBL" in steps_list_fcst) and not ("IBL" in steps_list_obs):
        if (not "CBL" in steps_list_fcst):
            raise Exception('Must run forecast CBLs or use observed CBLs before running IBLs.')
        print('Computing Forecast IBLs')
        fcst_infiles,yr_fcst,mth_fcst,day_fcst,yr_full_fcst = find_input_files(ibl_config, use_init, 'FCST_BLOCKING_TEMPLATE')
        ibls_fcst = steps_fcst.run_Calc_IBL(cbls_fcst,fcst_infiles,yr_fcst)
        daynum_fcst = np.arange(0,len(ibls_fcst[0,:,0]),1)
    elif ("IBL" in steps_list_obs) and ("IBL" in steps_list_fcst):
        if not ("CBL" in steps_list_obs) and not ("CBL" in steps_list_fcst):
            raise Exception('Must run observed and forecast CBLs before running IBLs.')
        both_infiles,yr_obs,mth_obs,day_obs = find_input_files(ibl_config, use_init, 'OBS_BLOCKING_TEMPLATE',
            secondtemplate='FCST_BLOCKING_TEMPLATE')
        obs_infiles = both_infiles[0]
        fcst_infiles = both_infiles[1]
        yr_fcst = yr_obs
        mth_fcst = mth_obs
        day_fcst = day_obs
        print('Computing Obs IBLs')
        ibls_obs = steps_obs.run_Calc_IBL(cbls_obs,obs_infiles,yr_obs)
        daynum_obs = np.arange(0,len(ibls_obs[0,:,0]),1)
        print('Computing Forecast IBLs')
        ibls_fcst = steps_fcst.run_Calc_IBL(cbls_fcst,fcst_infiles,yr_fcst)
        daynum_fcst = np.arange(0,len(ibls_fcst[0,:,0]),1)

    # Plot IBLS
    if("PLOTIBL" in steps_list_obs) and not ("PLOTIBL" in steps_list_fcst):
        if not ("IBL" in steps_list_obs):
            raise Exception('Must run observed IBLs before plotting them.')
        print('Plotting Obs IBLs')
        ibl_plot_title = config.getstr('Blocking','OBS_IBL_PLOT_TITLE','IBL Frequency')
        ibl_plot_outname = oplot_dir+'/'+config.getstr('Blocking','OBS_IBL_PLOT_OUTPUT_NAME','')
        ibl_plot_label1 = config.getstr('Blocking','IBL_PLOT_OBS_LABEL','')
        pb.plot_ibls(ibls_obs,lons_obs,ibl_plot_title,ibl_plot_outname,label1=ibl_plot_label1)
    elif ("PLOTIBL" in steps_list_fcst) and not ("PLOTIBL" in steps_list_obs):
        if not ("IBL" in steps_list_fcst):
            raise Exception('Must run forecast IBLs before plotting them.')
        print('Plotting Forecast IBLs')
        ibl_plot_title = config.getstr('Blocking','FCST_IBL_PLOT_TITLE','IBL Frequency')
        ibl_plot_outname = oplot_dir+'/'+config.getstr('Blocking','FCST_IBL_PLOT_OUTPUT_NAME')
        ibl_plot_label1 = config.getstr('Blocking','IBL_PLOT_FCST_LABEL',None)
        pb.plot_ibls(ibls_fcst,lons_fcst,ibl_plot_title,ibl_plot_outname,label1=ibl_plot_label1)
    elif ("PLOTIBL" in steps_list_obs) and ("PLOTIBL" in steps_list_fcst):
        if (not "IBL" in steps_list_obs) and (not "IBL" in steps_list_fcst):
            raise Exception('Must run forecast and observed IBLs before plotting them.')
        print('Plotting Obs and Forecast IBLs')
        ibl_plot_title = config.getstr('Blocking','IBL_PLOT_TITLE')
        ibl_plot_outname = oplot_dir+'/'+config.getstr('Blocking','IBL_PLOT_OUTPUT_NAME')
        #Check to see if there are plot legend labels
        ibl_plot_label1 = config.getstr('Blocking','IBL_PLOT_OBS_LABEL','Observation')
        ibl_plot_label2 = config.getstr('Blocking','IBL_PLOT_FCST_LABEL','Forecast')
        pb.plot_ibls(ibls_obs,lons_obs,ibl_plot_title,ibl_plot_outname,data2=ibls_fcst,lon2=lons_fcst,
            label1=ibl_plot_label1,label2=ibl_plot_label2)


    # Run GIBL
    if ("GIBL" in steps_list_obs):
        if not ("IBL" in steps_list_obs):
            raise Exception('Must run observed IBLs before running GIBLs.')
        print('Computing Obs GIBLs')
        gibls_obs = steps_obs.run_Calc_GIBL(ibls_obs,lons_obs)

    if ("GIBL" in steps_list_fcst):
        if not ("IBL" in steps_list_fcst):
            raise Exception('Must run Forecast IBLs before running GIBLs.')
        print('Computing Forecast GIBLs')
        gibls_fcst = steps_fcst.run_Calc_GIBL(ibls_fcst,lons_fcst)


    # Calc Blocks
    if ("CALCBLOCKS" in steps_list_obs):
        if not ("GIBL" in steps_list_obs):
            raise Exception('Must run observed GIBLs before calculating blocks.')
        print('Computing Blocks')
        block_freq_obs = steps_obs.run_Calc_Blocks(ibls_obs,gibls_obs,lons_obs,daynum_obs,yr_obs)

    if ("CALCBLOCKS" in steps_list_fcst):
        if not ("GIBL" in steps_list_fcst):
            raise Exception('Must run Forecast GIBLs before calculating blocks.')
        print('Computing Blocks')
        block_freq_fcst = steps_fcst.run_Calc_Blocks(ibls_fcst,gibls_fcst,lons_fcst,daynum_fcst,yr_fcst)

    # Plot Blocking Frequency
    if ("PLOTBLOCKS" in steps_list_obs):
        if not ("CALCBLOCKS" in steps_list_obs):
            raise Exception('Must compute observed blocks before plotting them.')
        print('Plotting Obs Blocks')
        blocking_plot_title = config.getstr('Blocking','OBS_BLOCKING_PLOT_TITLE')
        blocking_plot_outname = oplot_dir+'/'+config.getstr('Blocking','OBS_BLOCKING_PLOT_OUTPUT_NAME')
        pb.plot_blocks(block_freq_obs,gibls_obs,ibls_obs,lons_obs,blocking_plot_title,blocking_plot_outname)
    if ("PLOTBLOCKS" in steps_list_fcst):
        if not ("CALCBLOCKS" in steps_list_fcst):
            raise Exception('Must compute forecast blocks before plotting them.')
        print('Plotting Forecast Blocks')
        blocking_plot_title = config.getstr('Blocking','FCST_BLOCKING_PLOT_TITLE')
        blocking_plot_outname = oplot_dir+'/'+config.getstr('Blocking','FCST_BLOCKING_PLOT_OUTPUT_NAME')
        pb.plot_blocks(block_freq_fcst,gibls_fcst,ibls_fcst,lons_fcst,blocking_plot_title,blocking_plot_outname)


if __name__ == "__main__":
    main()
