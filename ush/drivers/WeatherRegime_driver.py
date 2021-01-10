#!/usr/bin/env python3

import sys
import os
import numpy as np
import netCDF4
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.pardir,os.pardir)))
sys.path.insert(0, "/glade/u/home/kalb/UIUC/METplotpy_feature_74/metplotpy/contributed/weather_regime")
from WeatherRegime import WeatherRegimeCalculation
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
from ush.master_metplus import get_config_inputs_from_command_line
from metplus.wrappers import PCPCombineWrapper
from metplus.wrappers import RegridDataPlaneWrapper
import plot_weather_regime as pwr
from Blocking_WeatherRegime_util import find_input_files, parse_steps

def main():

    all_steps = ["REGRID","TIMEAVE","ELBOW","PLOTELBOW","CALCEOF","PLOTEOF","KMEANS","PLOTKMEANS"]

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

    elbow_config = config_metplus.replace_config_from_section(config,'WeatherRegime')
    elbow_config_init = config.find_section('WeatherRegime','INIT_BEG')
    elbow_config_valid = config.find_section('WeatherRegime','VALID_BEG')
    use_init =  is_loop_by_init(elbow_config)

    if ("ELBOW" in steps_list_obs):
        print('Running Obs Elbow.py')
        obs_infiles, yr_obs = find_input_files(elbow_config, use_init, 'OBS_WR_TEMPLATE')
        elbow_obs,lats_obs,lons_obs,yr_obs,K_obs,d_obs,mi_obs,line_obs,curve_obs = steps_obs.run_elbow(obs_infiles,yr_obs)

    if ("ELBOW" in steps_list_fcst):
        print('Running Forecast Elbow.py')
        fcst_infiles,yr_fcst = find_input_files(elbow_config, use_init, 'FCST_WR_TEMPLATE')
        elbow_fcst,lats_fcst,lons_fcst,yr_fcst,K_fcst,d_fcst,mi_fcst,line_fcst,curve_fcst = steps_obs.run_elbow(fcst_infiles,yr_fcst)

    if ("PLOTELBOW" in steps_list_obs):
        print('Creating Obs Elbow plot')
        elbow_plot_title = config.getstr('WeatherRegime','OBS_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = config.getstr('WeatherRegime','OBS_ELBOW_PLOT_OUTPUT_NAME','obs_elbow')
        pwr.plot_elbow(K_obs,d_obs,mi_obs,line_obs,curve_obs,elbow_plot_title,elbow_plot_outname)

    if ("PLOTELBOW" in steps_list_fcst):
        print('Creating Forecast Elbow plot')
        elbow_plot_title = config.getstr('WeatherRegime','FCST_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = config.getstr('WeatherRegime','FCST_ELBOW_PLOT_OUTPUT_NAME','fcst_elbow')
        pwr.plot_elbow(K_fcst,d_fcst,mi_fcst,line_fcst,curve_fcst,elbow_plot_title,elbow_plot_outname)


    if ("CALCEOF" in steps_list_obs):
        print('Running Obs EOF')
        steps_obs.Calc_EOF(elbow_obs,lats_obs,lons_obs)

    if ("CALCEOF" in steps_list_fcst):
        print('Running Forecast EOF')
        steps_fcst.Calc_EOF(elbow_fcst,lats_fcst,lons_fcst)

    if ("PLOTEOF" in steps_list_obs):
        print('Plotting Obs EOFs')

    if ("PLOTEOF" in steps_list_fcst):
        print('Plotting Forecast EOFs')


    if ("KMEANS" in steps_list_obs):
        print('Running Obs K Means')

    if ("KMEANS" in steps_list_fcst):
        print('Running Forecast K Means')

   if ("PLOTKMEANS" in steps_list_obs):
        print('Plotting Obs K Means')

    if ("PLOTKMEANS" in steps_list_fcst):
        print('Plotting Forecast K Means')


if __name__ == "__main__":
    main()
