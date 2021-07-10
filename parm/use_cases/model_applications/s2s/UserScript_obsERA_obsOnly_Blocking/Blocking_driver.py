#!/usr/bin/env python3
import sys
import os
import numpy as np
import datetime
import netCDF4

from Blocking import BlockingCalculation
from metplus.util import pre_run_setup, config_metplus
from metplotpy.contributed.blocking_s2s import plot_blocking as pb
from metplotpy.contributed.blocking_s2s.CBL_plot import create_cbl_plot
from Blocking_WeatherRegime_util import parse_steps, write_mpr_file


def main():

    inconfig_list = sys.argv[1:]
    steps_list_fcst,steps_list_obs,config_list = parse_steps(inconfig_list)
    config = pre_run_setup(config_list)

    if not steps_list_obs and not steps_list_fcst:
        print('No processing steps requested for either the model or observations,')
        print('no data will be processed')


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
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Check to see if there is a mpr output directory
    mpr_dir = config.getstr('Blocking','BLOCKING_MPR_OUTPUT_DIR','')
    if not mpr_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        mpr_dir = os.path.join(obase,'mpr')

    # Check to see if CBL's are used from an obs climatology
    use_cbl_obs = config.getbool('Blocking','USE_CBL_OBS',False)

    # Get the days per season
    dseasons = config.getint('Blocking','DAYS_PER_SEASON')


    # Calculate Central Blocking Latitude
    if ("CBL" in steps_list_obs):
        print('Computing Obs CBLs')
        # Read in the list of CBL files
        cbl_nseasons = config.getint('Blocking','CBL_NUM_SEASONS')
        obs_cbl_filetxt = config.getstr('Blocking','OBS_CBL_INPUT_TEXTFILE')
        with open(obs_cbl_filetxt) as ocl:
            obs_infiles = ocl.read().splitlines()
        if len(obs_infiles) != (cbl_nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        cbls_obs,lats_obs,lons_obs,mhweight_obs,cbl_time_obs = steps_obs.run_CBL(obs_infiles,cbl_nseasons,dseasons)

    if ("CBL" in steps_list_fcst) and not use_cbl_obs:
        # Add in step to use obs for CBLS
        print('Computing Forecast CBLs')
        cbl_nseasons = config.getint('Blocking','CBL_NUM_SEASONS')
        fcst_cbl_filetxt = config.getstr('Blocking','FCST_CBL_INPUT_TEXTFILE')
        with open(fcst_cbl_filetxt) as fcl:
            fcst_infiles = fcl.read().splitlines()
        if len(fcst_infiles) != (cbl_nseasons*dseasons):
            raise Exception('Invalid Fcst data; each year must contain the same date range to calculate seasonal averages.')
        cbls_fcst,lats_fcst,lons_fcst,mhweight_fcst,cbl_time_fcst = steps_fcst.run_CBL(fcst_infiles,cbl_nseasons,dseasons)
    elif ("CBL" in steps_list_fcst) and use_cbl_obs:
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before using them as a forecast.')
        cbls_fcst = cbls_obs
        lats_fcst = lats_obs
        lons_fcst = lons_obs
        mhweight_fcst = mhweight_obs
        cbl_time_fcst = cbl_time_obs

    #Plot Central Blocking Latitude
    if ("PLOTCBL" in steps_list_obs):
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before plotting them.')
        print('Plotting Obs CBLs')
        cbl_plot_mthstr = config.getstr('Blocking','OBS_CBL_PLOT_MTHSTR')
        cbl_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','OBS_CBL_PLOT_OUTPUT_NAME'))
        create_cbl_plot(lons_obs, lats_obs, cbls_obs, mhweight_obs, cbl_plot_mthstr, cbl_plot_outname, 
            do_averaging=True)
    if ("PLOTCBL" in steps_list_fcst):
        if not ("CBL" in steps_list_fcst):
            raise Exception('Must run forecast CBLs before plotting them.')
        print('Plotting Forecast CBLs')
        cbl_plot_mthstr = config.getstr('Blocking','FCST_CBL_PLOT_MTHSTR')
        cbl_plot_outname = os.path.join(oplot_dir,+config.getstr('Blocking','FCST_CBL_PLOT_OUTPUT_NAME'))
        create_cbl_plot(lons_fcst, lats_fcst, cbls_fcst, mhweight_fcst, cbl_plot_mthstr, cbl_plot_outname, 
            do_averaging=True)


    # Run IBL
    if ("IBL" in steps_list_obs):
        if not ("CBL" in steps_list_obs):
            raise Exception('Must run observed CBLs before running IBLs.')
        print('Computing Obs IBLs')
        ibl_nseasons = config.getint('Blocking','IBL_NUM_SEASONS')
        obs_ibl_filetxt = config.getstr('Blocking','OBS_IBL_INPUT_TEXTFILE')
        with open(obs_ibl_filetxt) as oil:
            obs_infiles = oil.read().splitlines()
        if len(obs_infiles) != (ibl_nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        ibls_obs,ibl_time_obs = steps_obs.run_Calc_IBL(cbls_obs,obs_infiles,ibl_nseasons,dseasons)
        daynum_obs = np.arange(0,len(ibls_obs[0,:,0]),1)
    if ("IBL" in steps_list_fcst):
        if (not "CBL" in steps_list_fcst):
            raise Exception('Must run forecast CBLs or use observed CBLs before running IBLs.')
        print('Computing Forecast IBLs')
        ibl_nseasons = config.getint('Blocking','IBL_NUM_SEASONS')
        fcst_ibl_filetxt = config.getstr('Blocking','FCST_IBL_INPUT_TEXTFILE')
        with open(fcst_ibl_filetxt) as fil:
            fcst_infiles = fil.read().splitlines()
        if len(fcst_infiles) != (ibl_nseasons*dseasons):
            raise Exception('Invalid Fcst data; each year must contain the same date range to calculate seasonal averages.')
        ibls_fcst,ibl_time_fcst = steps_fcst.run_Calc_IBL(cbls_fcst,fcst_infiles,ibl_nseasons,dseasons)
        daynum_fcst = np.arange(0,len(ibls_fcst[0,:,0]),1)

    if ("IBL" in steps_list_obs) and ("IBL" in steps_list_fcst):
        # Print IBLs to output matched pair file
        i_mpr_outdir = os.path.join(mpr_dir,'IBL')
        if not os.path.exists(i_mpr_outdir):
            os.makedirs(i_mpr_outdir)
        modname = config.getstr('Blocking','MODEL_NAME','GFS')
        maskname = config.getstr('Blocking','MASK_NAME','FULL')
        ibl_outfile_prefix = os.path.join(i_mpr_outdir,'IBL_stat_'+modname)
        cbls_avg = np.nanmean(cbls_obs,axis=0)
        write_mpr_file(ibls_obs,ibls_fcst,cbls_obs,lons_obs,ibl_time_obs,ibl_time_fcst,modname,
            'Inst_Blocked_Lats','Z500','Inst_Blocked_Lats','Z500',maskname,'500',ibl_outfile_prefix)

    # Plot IBLS
    if("PLOTIBL" in steps_list_obs) and not ("PLOTIBL" in steps_list_fcst):
        if not ("IBL" in steps_list_obs):
            raise Exception('Must run observed IBLs before plotting them.')
        print('Plotting Obs IBLs')
        ibl_plot_title = config.getstr('Blocking','OBS_IBL_PLOT_TITLE','IBL Frequency')
        ibl_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','OBS_IBL_PLOT_OUTPUT_NAME'))
        ibl_plot_label1 = config.getstr('Blocking','IBL_PLOT_OBS_LABEL','')
        pb.plot_ibls(ibls_obs,lons_obs,ibl_plot_title,ibl_plot_outname,label1=ibl_plot_label1)
    elif ("PLOTIBL" in steps_list_fcst) and not ("PLOTIBL" in steps_list_obs):
        if not ("IBL" in steps_list_fcst):
            raise Exception('Must run forecast IBLs before plotting them.')
        print('Plotting Forecast IBLs')
        ibl_plot_title = config.getstr('Blocking','FCST_IBL_PLOT_TITLE','IBL Frequency')
        ibl_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','FCST_IBL_PLOT_OUTPUT_NAME'))
        ibl_plot_label1 = config.getstr('Blocking','IBL_PLOT_FCST_LABEL',None)
        pb.plot_ibls(ibls_fcst,lons_fcst,ibl_plot_title,ibl_plot_outname,label1=ibl_plot_label1)
    elif ("PLOTIBL" in steps_list_obs) and ("PLOTIBL" in steps_list_fcst):
        if (not "IBL" in steps_list_obs) and (not "IBL" in steps_list_fcst):
            raise Exception('Must run forecast and observed IBLs before plotting them.')
        print('Plotting Obs and Forecast IBLs')
        ibl_plot_title = config.getstr('Blocking','IBL_PLOT_TITLE')
        ibl_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','IBL_PLOT_OUTPUT_NAME'))
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
        block_freq_obs = steps_obs.run_Calc_Blocks(ibls_obs,gibls_obs,lons_obs,daynum_obs)

    if ("CALCBLOCKS" in steps_list_fcst):
        if not ("GIBL" in steps_list_fcst):
            raise Exception('Must run Forecast GIBLs before calculating blocks.')
        print('Computing Blocks')
        block_freq_fcst = steps_fcst.run_Calc_Blocks(ibls_fcst,gibls_fcst,lons_fcst,daynum_fcst)

    if ("CALCBLOCKS" in steps_list_obs) and ("CALCBLOCKS" in steps_list_fcst):
        b_mpr_outdir = os.path.join(mpr_dir,'Blocks')
        if not os.path.exists(b_mpr_outdir):
            os.makedirs(b_mpr_outdir)
        # Print Blocks to output matched pair file
        modname = config.getstr('Blocking','MODEL_NAME','GFS')
        maskname = config.getstr('Blocking','MASK_NAME','FULL')
        blocks_outfile_prefix = os.path.join(b_mpr_outdir,'blocking_stat_'+modname)
        cbls_avg = np.nanmean(cbls_obs,axis=0)
        write_mpr_file(block_freq_obs,block_freq_fcst,cbls_avg,lons_obs,ibl_time_obs,ibl_time_fcst,modname,
            'Blocked_Lon','Z500','Blocked_Lon','Z500',maskname,'500',blocks_outfile_prefix)


    # Plot Blocking Frequency
    if ("PLOTBLOCKS" in steps_list_obs):
        if not ("CALCBLOCKS" in steps_list_obs):
            raise Exception('Must compute observed blocks before plotting them.')
        print('Plotting Obs Blocks')
        blocking_plot_title = config.getstr('Blocking','OBS_BLOCKING_PLOT_TITLE')
        blocking_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','OBS_BLOCKING_PLOT_OUTPUT_NAME'))
        pb.plot_blocks(block_freq_obs,gibls_obs,ibls_obs,lons_obs,blocking_plot_title,blocking_plot_outname)
    if ("PLOTBLOCKS" in steps_list_fcst):
        if not ("CALCBLOCKS" in steps_list_fcst):
            raise Exception('Must compute forecast blocks before plotting them.')
        print('Plotting Forecast Blocks')
        blocking_plot_title = config.getstr('Blocking','FCST_BLOCKING_PLOT_TITLE')
        blocking_plot_outname = os.path.join(oplot_dir,config.getstr('Blocking','FCST_BLOCKING_PLOT_OUTPUT_NAME'))
        pb.plot_blocks(block_freq_fcst,gibls_fcst,ibls_fcst,lons_fcst,blocking_plot_title,blocking_plot_outname)


if __name__ == "__main__":
    main()
