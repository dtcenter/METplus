#!/usr/bin/env python3

import sys
import os
import numpy as np
import netCDF4
import re

mp_fpath = os.path.abspath(__file__)
mp_fpath_split = str.split(mp_fpath,os.path.sep)
mp_loc_ind = mp_fpath_split.index('METplus')

sys.path.insert(0,os.path.sep.join(mp_fpath_split[0:mp_loc_ind+1]))
sys.path.insert(0, os.path.sep.join(mp_fpath_split[0:mp_loc_ind])+"/METplotpy_feature_74")
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
#    os.pardir,os.pardir)))
#sys.path.insert(0, "/glade/u/home/kalb/UIUC/METplotpy_feature_74/metplotpy/contributed/weather_regime")
from WeatherRegime import WeatherRegimeCalculation
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub, getlist
from ush.master_metplus import get_config_inputs_from_command_line
from metplus.wrappers import PCPCombineWrapper
from metplus.wrappers import RegridDataPlaneWrapper
from metplotpy.contributed.weather_regime import plot_weather_regime as pwr
from Blocking_WeatherRegime_util import find_input_files, parse_steps, read_nc_met

def main():

    all_steps = ["REGRID","TIMEAVE","ELBOW","PLOTELBOW","EOF","PLOTEOF","KMEANS","PLOTKMEANS"]

    inconfig_list = get_config_inputs_from_command_line()
    steps_list_fcst,steps_list_obs,config_list = parse_steps(inconfig_list)
    config = pre_run_setup(config_list)

    if not steps_list_obs and not steps_list_fcst:
        print('No processing steps requested for either the model or observations,')
        print('no data will be processed')


    ######################################################################
    # Pre-Process Data:
    ######################################################################
    # Regrid
    if ("REGRID" in steps_list_obs):
        print('Regridding Observations')
        regrid_config = config_metplus.replace_config_from_section(config, 'regrid_obs')
        RegridDataPlaneWrapper(regrid_config).run_all_times()

    if ("REGRID" in steps_list_fcst):
       print('Regridding Model')
       regrid_config = config_metplus.replace_config_from_section(config, 'regrid_fcst')
       RegridDataPlaneWrapper(regrid_config).run_all_times()

    #Compute Daily Average
    if ("TIMEAVE" in steps_list_obs):
        print('Computing Daily Averages')
        daily_config = config_metplus.replace_config_from_section(config, 'daily_mean_obs')
        PCPCombineWrapper(daily_config).run_all_times()

    if ("TIMEAVE" in steps_list_fcst):
        print('Computing Daily Averages')
        daily_config = config_metplus.replace_config_from_section(config, 'daily_mean_fcst')
        PCPCombineWrapper(daily_config).run_all_times()


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

    elbow_config = config_metplus.replace_config_from_section(config,'WeatherRegime')
    elbow_config_init = config.find_section('WeatherRegime','INIT_BEG')
    elbow_config_valid = config.find_section('WeatherRegime','VALID_BEG')
    use_init =  is_loop_by_init(elbow_config)


    if ("ELBOW" in steps_list_obs) or ("EOF" in steps_list_obs) or ("KMEANS" in steps_list_obs):
        obs_infiles,yr_obs,mth_obs,day_obs,yr_full_obs = find_input_files(elbow_config, use_init, 'OBS_WR_TEMPLATE')
        obs_invar = config.getstr('WeatherRegime','OBS_WR_VAR','')
        z500_obs,lats_obs,lons_obs,year_obs = read_nc_met(obs_infiles,yr_obs,obs_invar)
        z500_detrend_obs,z500_detrend_2d_obs = steps_obs.weights_detrend(lats_obs,lons_obs,z500_obs)

    if ("ELBOW" in steps_list_fcst) or ("EOF" in steps_list_fcst) or("KMEANS" in steps_list_fcst):
        fcst_infiles,yr_fcst, mth_fcst,day_fcst,yr_full_fcst = find_input_files(elbow_config, use_init, 'FCST_WR_TEMPLATE')
        fcst_invar = config.getstr('WeatherRegime','FCST_WR_VAR','')
        z500_fcst,lats_fcst,lons_fcst,year_fcst = read_nc_met(fcst_infiles,yr_fcst,fcst_invar)
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
        kmeans_obs,wrnum_obs,perc_obs = steps_obs.run_K_means(z500_detrend_2d_obs,yr_full_obs,mth_obs,day_obs,z500_obs.shape)

    if ("KMEANS" in steps_list_fcst):
        print('Running Forecast K Means')
        kmeans_fcst,wrnum_fcst,perc_fcst = steps_fcst.run_K_means(z500_detrend_2d_fcst,yr_full_fcst,mth_fcst,day_fcst,z500_fcst.shape)

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


if __name__ == "__main__":
    main()
