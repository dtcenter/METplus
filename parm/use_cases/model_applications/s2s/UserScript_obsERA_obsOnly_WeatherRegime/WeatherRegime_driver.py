#!/usr/bin/env python3
import sys
import os
import numpy as np
import netCDF4
import warnings
import atexit

from WeatherRegime import WeatherRegimeCalculation
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub, getlist
from metplotpy.contributed.weather_regime import plot_weather_regime as pwr
from Blocking_WeatherRegime_util import parse_steps, read_nc_met, write_mpr_file


def cleanup_daily_files(obs_dailyfile, fcst_dailyfile, keep_daily_files):
    if keep_daily_files == 'false':
        try:
            os.remove(obs_anomfile)
        except:
            pass

        try:
            os.remove(fcst_anomfile)
        except:
            pass


def main():

    all_steps = ["ELBOW","PLOTELBOW","EOF","PLOTEOF","KMEANS","PLOTKMEANS"]

    inconfig_list = sys.argv[1:]
    steps_list_fcst,steps_list_obs,config_list = parse_steps(inconfig_list)
    config = pre_run_setup(config_list)

    if not steps_list_obs and not steps_list_fcst:
        warnings.warn('No processing steps requested for either the model or observations,')
        warnings.warn('no data will be processed')


    ######################################################################
    # Blocking Calculation and Plotting
    ######################################################################
    # Set up the data
    steps_obs = WeatherRegimeCalculation(config,'OBS')
    steps_fcst = WeatherRegimeCalculation(config,'FCST')

    # Check to see if there is a plot directory
    oplot_dir = config.getstr('WeatherRegime','WR_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = obase+'/'+'plots'
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

     # Check to see if there is a mpr output directory
    mpr_outdir = config.getstr('WeatherRegime','WR_MPR_OUTPUT_DIR','')
    if not mpr_outdir:
        obase = config.getstr('config','OUTPUT_BASE')
        mpr_outdir = os.path.join(obase,'mpr')

     # Get number of seasons and days per season
    nseasons = config.getint('WeatherRegime','NUM_SEASONS')
    dseasons = config.getint('WeatherRegime','DAYS_PER_SEASON')

    # Grab the Daily (IBL) text files
    obs_wr_filetxt = config.getstr('WeatherRegime','OBS_WR_INPUT_TEXTFILE','')
    fcst_wr_filetxt = config.getstr('WeatherRegime','FCST_WR_INPUT_TEXTFILE','')
    keep_wr_textfile = config.getstr('WeatherRegime','KEEP_WR_FILE_LISTING', 'False').lower()
    atexit.register(cleanup_daily_files, obs_wr_filetxt, fcst_wr_filetxt, keep_wr_textfile)

    elbow_config = config_metplus.replace_config_from_section(config,'WeatherRegime')
    elbow_config_init = config.find_section('WeatherRegime','INIT_BEG')
    elbow_config_valid = config.find_section('WeatherRegime','VALID_BEG')
    use_init =  is_loop_by_init(elbow_config)


    if ("ELBOW" in steps_list_obs) or ("EOF" in steps_list_obs) or ("KMEANS" in steps_list_obs):
        with open(obs_wr_filetxt) as owl:
            obs_infiles = owl.read().splitlines()
        if len(obs_infiles) != (nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        obs_invar = config.getstr('WeatherRegime','OBS_WR_VAR','')
        z500_obs,lats_obs,lons_obs,timedict_obs = read_nc_met(obs_infiles,obs_invar,nseasons,dseasons)
        z500_detrend_obs,z500_detrend_2d_obs = steps_obs.weights_detrend(lats_obs,lons_obs,z500_obs)

    if ("ELBOW" in steps_list_fcst) or ("EOF" in steps_list_fcst) or("KMEANS" in steps_list_fcst):
        with open(fcst_wr_filetxt) as fwl:
            fcst_infiles = fwl.read().splitlines()
        if len(fcst_infiles) != (nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        fcst_invar = config.getstr('WeatherRegime','FCST_WR_VAR','')
        z500_fcst,lats_fcst,lons_fcst,timedict_fcst = read_nc_met(fcst_infiles,fcst_invar,nseasons,dseasons)
        z500_detrend_fcst,z500_detrend_2d_fcst = steps_fcst.weights_detrend(lats_fcst,lons_fcst,z500_fcst)


    if ("ELBOW" in steps_list_obs):
        print('Running Obs Elbow')
        K_obs,d_obs,mi_obs,line_obs,curve_obs = steps_obs.run_elbow(z500_detrend_2d_obs)

    if ("ELBOW" in steps_list_fcst):
        print('Running Forecast Elbow')
        K_fcst,d_fcst,mi_fcst,line_fcst,curve_fcst = steps_fcst.run_elbow(z500_detrend_2d_fcst)

    if ("PLOTELBOW" in steps_list_obs):
        if not ("ELBOW" in steps_list_obs):
            raise Exception('Must run observed Elbow before plotting observed elbow.')
        print('Creating Obs Elbow plot')
        elbow_plot_title = config.getstr('WeatherRegime','OBS_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','OBS_ELBOW_PLOT_OUTPUT_NAME','obs_elbow')
        pwr.plot_elbow(K_obs,d_obs,mi_obs,line_obs,curve_obs,elbow_plot_title,elbow_plot_outname)

    if ("PLOTELBOW" in steps_list_fcst):
        if not ("ELBOW" in steps_list_fcst):
            raise Exception('Must run forecast Elbow before plotting forecast elbow.')
        print('Creating Forecast Elbow plot')
        elbow_plot_title = config.getstr('WeatherRegime','FCST_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','FCST_ELBOW_PLOT_OUTPUT_NAME','fcst_elbow')
        pwr.plot_elbow(K_fcst,d_fcst,mi_fcst,line_fcst,curve_fcst,elbow_plot_title,elbow_plot_outname)


    if ("EOF" in steps_list_obs):
        print('Running Obs EOF')
        eof_obs,pc_obs,wrnum_obs,variance_fractions_obs = steps_obs.Calc_EOF(z500_obs)
        z500_detrend_2d_obs = steps_obs.reconstruct_heights(eof_obs,pc_obs,z500_detrend_2d_obs.shape)

    if ("EOF" in steps_list_fcst):
        print('Running Forecast EOF')
        eof_fcst,pc_fcst,wrnum_fcst,variance_fractions_fcst = steps_fcst.Calc_EOF(z500_fcst)
        z500_detrend_2d_fcst = steps_fcst.reconstruct_heights(eof_fcst,pc_fcst,z500_detrend_2d_fcst.shape)

    if ("PLOTEOF" in steps_list_obs):
        if not ("EOF" in steps_list_obs):
            raise Exception('Must run observed EOFs before plotting observed EOFs.')
        print('Plotting Obs EOFs')
        pltlvls_str = getlist(config.getstr('WeatherRegime','EOF_PLOT_LEVELS',''))
        pltlvls = [float(pp) for pp in pltlvls_str]
        eof_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','OBS_EOF_PLOT_OUTPUT_NAME','obs_eof')
        pwr.plot_eof(eof_obs,wrnum_obs,variance_fractions_obs,lons_obs,lats_obs,eof_plot_outname,pltlvls)

    if ("PLOTEOF" in steps_list_fcst):
        if not ("EOF" in steps_list_fcst):
            raise Exception('Must run forecast EOFs before plotting forecast EOFs.')
        print('Plotting Forecast EOFs')
        pltlvls_str = getlist(config.getstr('WeatherRegime','EOF_PLOT_LEVELS',''))
        pltlvls = [float(pp) for pp in pltlvls_str]
        eof_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','OBS_EOF_PLOT_OUTPUT_NAME','obs_eof')
        pwr.plot_eof(eof_fcst,wrnum_fcst,variance_fractions_fcst,lons_fcst,lats_fcst,eof_plot_outname,pltlvls)


    if ("KMEANS" in steps_list_obs):
        print('Running Obs K Means')
        kmeans_obs,wrnum_obs,perc_obs,wrc_obs= steps_obs.run_K_means(z500_detrend_2d_obs,timedict_obs,z500_obs.shape)

    if ("KMEANS" in steps_list_fcst):
        print('Running Forecast K Means')
        kmeans_fcst,wrnum_fcst,perc_fcst,wrc_fcst = steps_fcst.run_K_means(z500_detrend_2d_fcst,timedict_fcst,z500_fcst.shape)

    #if ("KMEANS" in steps_list_obs) and ("KMEANS" in steps_list_fcst):
    modname = config.getstr('WeatherRegime','MODEL_NAME','GFS')
    maskname = config.getstr('WeatherRegime','MASK_NAME','FULL')
    wr_outfile_prefix = os.path.join(mpr_outdir,'weather_regime_stat_'+modname)
    wrc_fcst = wrc_obs
    wrc_obs_mpr = wrc_obs[:,:,np.newaxis]
    wrc_fcst_mpr = wrc_fcst[:,:,np.newaxis]
    timedict_fcst = timedict_obs
    if not os.path.exists(mpr_outdir):
        os.makedirs(mpr_outdir)
    write_mpr_file(wrc_obs_mpr,wrc_fcst_mpr,[0.0],[0.0],timedict_obs,timedict_fcst,modname,
        'WeatherRegimeClass','Z500','WeatherRegimeClass','Z500',maskname,'500',wr_outfile_prefix)

    if ("PLOTKMEANS" in steps_list_obs):
        if not ("KMEANS" in steps_list_obs):
            raise Exception('Must run observed Kmeans before plotting observed Kmeans.')
        print('Plotting Obs K Means')
        pltlvls_str = getlist(config.getstr('WeatherRegime','KMEANS_PLOT_LEVELS',''))
        pltlvls = [float(pp) for pp in pltlvls_str]
        kmeans_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','OBS_KMEANS_PLOT_OUTPUT_NAME','obs_kmeans')
        pwr.plot_K_means(kmeans_obs,wrnum_obs,lons_obs,lats_obs,perc_obs,kmeans_plot_outname,pltlvls)

    if ("PLOTKMEANS" in steps_list_fcst):
        if not ("KMEANS" in steps_list_fcst):
            raise Exception('Must run forecast Kmeans before plotting forecast Kmeans.')
        print('Plotting Forecast K Means')
        pltlvls_str = getlist(config.getstr('WeatherRegime','KMEANS_PLOT_LEVELS',''))
        pltlvls = [float(pp) for pp in pltlvls_str]
        kmeans_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','FCST_KMEANS_PLOT_OUTPUT_NAME','fcst_kmeans')
        pwr.plot_K_means(kmeans_fcst,wrnum_fcst,lons_fcst,lats_fcst,perc_fcts,kmeans_plot_outname,pltlvls)


    if ("TIMEFREQ" in steps_list_obs):
        wrmean_obs,dlen_obs = steps_obs.compute_wr_freq(wrc_obs)

    if ("TIMEFREQ" in steps_list_fcst):
        wrmean_fcst,dlen_fcst = steps_fcst.compute_wr_freq(wrc_fcst)

    #if ("TIMEFREQ" in steps_list_obs) and ("TIMEFREQ" in steps_list_fcst):
    #modname = config.getstr('WeatherRegime','MODEL_NAME','GFS')
    #maskname = config.getstr('WeatherRegime','MASK_NAME','FULL')
    #wr_outfile_prefix = os.path.join(mpr_outdir,'weather_regime_freq_stat_'+modname)
    #wrmean_fcst = wrmean_obs
    #timedict_fcst = timedict_obs
    #wrmean_obs_mpr = wrmean_obs[:,:,np.newaxis]
    #wrmean_fcst_mpr wrmean_fcst[:,:,np.newaxis]
    #if not os.path.exists(mpr_outdir):
    #    os.makedirs(mpr_outdir)
    #write_mpr_file(wrmean_obs_mpr,wrmean_fcst_mpr,[0.0],[0.0],timedict_obs,timedict_fcst,modname,
    #    'WeatherRegimeClass','Z500','WeatherRegimeClass','Z500',maskname,'500',wr_outfile_prefix)

    if ("PLOTFREQ" in steps_list_obs):
        freq_plot_title = config.getstr('WeatherRegime','OBS_FREQ_PLOT_TITLE','Seasonal Cycle of WR Days/Week')
        freq_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','OBS_FREQ_PLOT_OUTPUT_NAME','obs_freq')
        pwr.plot_wr_frequency(wrmean_obs,wrnum_obs,dlen_obs,freq_plot_title,freq_plot_outname)

    if ("PLOTFREQ" in steps_list_fcst):
        freq_plot_title = config.getstr('WeatherRegime','FCST_FREQ_PLOT_TITLE','Seasonal Cycle of WR Days/Week')
        freq_plot_outname = oplot_dir+'/'+config.getstr('WeatherRegime','FCST_FREQ_PLOT_OUTPUT_NAME','fcst_freq')
        pwr.plot_wr_frequency(wrmean_fcst,wrnum_fcst,dlen_fcst,freq_plot_title,freq_plot_outname)


    #if ("ANOMALY_CORR" in steps_list_obs):


if __name__ == "__main__":
    main()
