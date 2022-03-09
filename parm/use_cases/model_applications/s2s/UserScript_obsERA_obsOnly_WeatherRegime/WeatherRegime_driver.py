#!/usr/bin/env python3
import sys
import os
import numpy as np
import netCDF4
import warnings

from metcalcpy.contributed.blocking_weather_regime.WeatherRegime import WeatherRegimeCalculation
from metcalcpy.contributed.blocking_weather_regime.Blocking_WeatherRegime_util import parse_steps, read_nc_met, write_mpr_file, reorder_fcst_regimes
from metplotpy.contributed.weather_regime import plot_weather_regime as pwr


def main():

    steps_list_fcst,steps_list_obs = parse_steps()

    if not steps_list_obs and not steps_list_fcst:
        warnings.warn('No processing steps requested for either the model or observations,')
        warnings.warn('No data will be processed')


    ######################################################################
    # Blocking Calculation and Plotting
    ######################################################################
    # Set up the data
    steps_obs = WeatherRegimeCalculation('OBS')
    steps_fcst = WeatherRegimeCalculation('FCST')

    # Check to see if there is a plot directory
    oplot_dir = os.environ.get('WR_PLOT_OUTPUT_DIR','')
    obase = os.environ['SCRIPT_OUTPUT_BASE']
    if not oplot_dir:
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

     # Check to see if there is a mpr output directory
    mpr_outdir = os.environ.get('WR_MPR_OUTPUT_DIR','')
    if not mpr_outdir:
        mpr_outdir = os.path.join(obase,'mpr')

     # Get number of seasons and days per season
    nseasons = int(os.environ['NUM_SEASONS'])
    dseasons = int(os.environ['DAYS_PER_SEASON'])

    # Grab the Daily text files
    obs_wr_filetxt = os.environ.get('METPLUS_FILELIST_OBS_INPUT','')
    fcst_wr_filetxt = os.environ.get('METPLUS_FILELIST_FCST_INPUT','')

    if ("ELBOW" in steps_list_obs) or ("EOF" in steps_list_obs) or ("KMEANS" in steps_list_obs):
        with open(obs_wr_filetxt) as owl:
            obs_infiles = owl.read().splitlines()
        # Remove the first line if it's there
        if (obs_infiles[0] == 'file_list'):
            obs_infiles = obs_infiles[1:]
        if len(obs_infiles) != (nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        obs_invar = os.environ.get('OBS_WR_VAR','')
        z500_obs,lats_obs,lons_obs,timedict_obs = read_nc_met(obs_infiles,obs_invar,nseasons,dseasons)
        z500_detrend_obs,z500_detrend_2d_obs = steps_obs.weights_detrend(lats_obs,lons_obs,z500_obs)

    if ("ELBOW" in steps_list_fcst) or ("EOF" in steps_list_fcst) or("KMEANS" in steps_list_fcst):
        with open(fcst_wr_filetxt) as fwl:
            fcst_infiles = fwl.read().splitlines()
        # Remove the first line if it's there
        if (fcst_infiles[0] == 'file_list'):
            fcst_infiles = fcst_infiles[1:]
        if len(fcst_infiles) != (nseasons*dseasons):
            raise Exception('Invalid Obs data; each year must contain the same date range to calculate seasonal averages.')
        fcst_invar = os.environ.get('FCST_WR_VAR','')
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
        elbow_plot_title = os.environ.get('OBS_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = os.path.join(oplot_dir,os.environ.get('OBS_ELBOW_PLOT_OUTPUT_NAME','obs_elbow'))
        pwr.plot_elbow(K_obs,d_obs,mi_obs,line_obs,curve_obs,elbow_plot_title,elbow_plot_outname)

    if ("PLOTELBOW" in steps_list_fcst):
        if not ("ELBOW" in steps_list_fcst):
            raise Exception('Must run forecast Elbow before plotting forecast elbow.')
        print('Creating Forecast Elbow plot')
        elbow_plot_title = os.environ.get('FCST_ELBOW_PLOT_TITLE','Elbow Method For Optimal k')
        elbow_plot_outname = os.path.join(oplot_dir,os.environ.get('FCST_ELBOW_PLOT_OUTPUT_NAME','fcst_elbow'))
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
        pltlvls_str = os.environ['EOF_PLOT_LEVELS'].split(',')
        pltlvls = [float(pp) for pp in pltlvls_str]
        eof_plot_outname = os.path.join(oplot_dir,os.environ.get('OBS_EOF_PLOT_OUTPUT_NAME','obs_eof'))
        pwr.plot_eof(eof_obs,wrnum_obs,variance_fractions_obs,lons_obs,lats_obs,eof_plot_outname,pltlvls)

    if ("PLOTEOF" in steps_list_fcst):
        if not ("EOF" in steps_list_fcst):
            raise Exception('Must run forecast EOFs before plotting forecast EOFs.')
        print('Plotting Forecast EOFs')
        pltlvls_str = os.environ['EOF_PLOT_LEVELS'].split(',')
        pltlvls = [float(pp) for pp in pltlvls_str]
        eof_plot_outname = os.path.join(oplot_dir,os.environ.get('FCST_EOF_PLOT_OUTPUT_NAME','fcst_eof'))
        pwr.plot_eof(eof_fcst,wrnum_fcst,variance_fractions_fcst,lons_fcst,lats_fcst,eof_plot_outname,pltlvls)


    if ("KMEANS" in steps_list_obs):
        print('Running Obs K Means')
        kmeans_obs,wrnum_obs,perc_obs,wrc_obs= steps_obs.run_K_means(z500_detrend_2d_obs,timedict_obs,z500_obs.shape)

    if ("KMEANS" in steps_list_fcst):
        print('Running Forecast K Means')
        kmeans_fcst,wrnum_fcst,perc_fcst,wrc_fcst = steps_fcst.run_K_means(z500_detrend_2d_fcst,timedict_fcst,
            z500_fcst.shape)

    if ("KMEANS" in steps_list_obs) and ("KMEANS" in steps_list_fcst):
        # Check to see if reordering the data so that the weather regime patterns match between
        # the forecast and observations, is needed
        #TODO:  make this automated based on spatial correlations
        reorder_fcst = os.environ.get('REORDER_FCST','False').lower()
        fcst_order_str = os.environ['FCST_ORDER'].split(',')
        fcst_order = [int(fo) for fo in fcst_order_str]
        if reorder_fcst == 'true':
            kmeans_fcst,perc_fcst,wrc_fcst = reorder_fcst_regimes(kmeans_fcst,perc_fcst,wrc_fcst,wrnum_fcst,fcst_order)

        # Write matched pair output for weather regime classification
        modname = os.environ.get('MODEL_NAME','GFS')
        maskname = os.environ.get('MASK_NAME','FULL')
        mpr_full_outdir = os.path.join(mpr_outdir,'WeatherRegime')
        wr_outfile_prefix = os.path.join(mpr_full_outdir,'weather_regime_stat_'+modname)
        wrc_obs_mpr = wrc_obs[:,:,np.newaxis]
        wrc_fcst_mpr = wrc_fcst[:,:,np.newaxis]
        if not os.path.exists(mpr_full_outdir):
            os.makedirs(mpr_full_outdir)
        write_mpr_file(wrc_obs_mpr,wrc_fcst_mpr,[0.0],[0.0],timedict_obs,timedict_fcst,modname,'NA',
            'WeatherRegimeClass','class','Z500','WeatherRegimeClass','class','Z500',maskname,'500',wr_outfile_prefix)

    if ("PLOTKMEANS" in steps_list_obs):
        if not ("KMEANS" in steps_list_obs):
            raise Exception('Must run observed Kmeans before plotting observed Kmeans.')
        print('Plotting Obs K Means')
        pltlvls_str = os.environ['KMEANS_PLOT_LEVELS'].split(',')
        pltlvls = [float(pp) for pp in pltlvls_str]
        kmeans_plot_outname = os.path.join(oplot_dir,os.environ.get('OBS_KMEANS_PLOT_OUTPUT_NAME','obs_kmeans'))
        pwr.plot_K_means(kmeans_obs,wrnum_obs,lons_obs,lats_obs,perc_obs,kmeans_plot_outname,pltlvls)

    if ("PLOTKMEANS" in steps_list_fcst):
        if not ("KMEANS" in steps_list_fcst):
            raise Exception('Must run forecast Kmeans before plotting forecast Kmeans.')
        print('Plotting Forecast K Means')
        pltlvls_str = os.environ['KMEANS_PLOT_LEVELS'].split(',')
        pltlvls = [float(pp) for pp in pltlvls_str]
        kmeans_plot_outname = os.path.join(oplot_dir,os.environ.get('FCST_KMEANS_PLOT_OUTPUT_NAME','fcst_kmeans'))
        pwr.plot_K_means(kmeans_fcst,wrnum_fcst,lons_fcst,lats_fcst,perc_fcst,kmeans_plot_outname,pltlvls)


    if ("TIMEFREQ" in steps_list_obs):
        wrfreq_obs,dlen_obs,ts_diff_obs = steps_obs.compute_wr_freq(wrc_obs)

    if ("TIMEFREQ" in steps_list_fcst):
        wrfreq_fcst,dlen_fcst,ts_diff_fcst = steps_fcst.compute_wr_freq(wrc_fcst)

    if ("TIMEFREQ" in steps_list_obs) and ("TIMEFREQ" in steps_list_fcst):
        # Write matched pair output for frequency of each weather regime
        modname = os.environ.get('MODEL_NAME','GFS')
        maskname = os.environ.get('MASK_NAME','FULL')
        mpr_full_outdir = os.path.join(mpr_outdir,'freq')
        timedict_obs_mpr = {'init':timedict_obs['init'][:,ts_diff_obs-1:],
            'valid':timedict_obs['valid'][:,ts_diff_obs-1:],'lead':timedict_obs['lead'][:,ts_diff_obs-1:]}
        timedict_fcst_mpr = {'init':timedict_fcst['init'][:,ts_diff_fcst-1:],
            'valid':timedict_fcst['valid'][:,ts_diff_fcst-1:],'lead':timedict_fcst['lead'][:,ts_diff_fcst-1:]}
        wrfreq_obs_mpr = wrfreq_obs[:,:,:,np.newaxis]
        wrfreq_fcst_mpr = wrfreq_fcst[:,:,:,np.newaxis]
        if not os.path.exists(mpr_full_outdir):
            os.makedirs(mpr_full_outdir)
        for wrn in np.arange(wrnum_obs):
            wr_outfile_prefix = os.path.join(mpr_full_outdir,'weather_regime'+str(wrn+1).zfill(2)+'_freq_stat_'+modname)
            write_mpr_file(wrfreq_obs_mpr[wrn,:,:,:],wrfreq_fcst_mpr[wrn,:,:,:],[0.0],[0.0],timedict_obs,
                timedict_fcst,modname,str(wrn+1).zfill(2),'WeatherRegimeFreq','percent','Z500','WeatherRegimeFreq',
                'percent','Z500',maskname,'500',wr_outfile_prefix)

    if ("PLOTFREQ" in steps_list_obs):
        if not ("TIMEFREQ" in steps_list_obs):
            raise Exception('Must run observed Frequency calculation before plotting the frequencies.')
        freq_plot_title = os.environ.get('OBS_FREQ_PLOT_TITLE','Seasonal Cycle of WR Days/Week')
        freq_plot_outname = os.path.join(oplot_dir,os.environ.get('OBS_FREQ_PLOT_OUTPUT_NAME','obs_freq'))
        # Compute mean
        wrmean_obs = np.nanmean(wrfreq_obs,axis=1)
        pwr.plot_wr_frequency(wrmean_obs,wrnum_obs,dlen_obs,freq_plot_title,freq_plot_outname)

    if ("PLOTFREQ" in steps_list_fcst):
        if not ("TIMEFREQ" in steps_list_fcst):
            raise Exception('Must run forecast Frequency calculation before plotting the frequencies.')
        freq_plot_title = os.environ.get('FCST_FREQ_PLOT_TITLE','Seasonal Cycle of WR Days/Week')
        freq_plot_outname = os.path.join(oplot_dir,os.environ.get('FCST_FREQ_PLOT_OUTPUT_NAME','fcst_freq'))
        # Compute mean
        wrmean_fcst = np.nanmean(wrfreq_fcst,axis=1)
        pwr.plot_wr_frequency(wrmean_fcst,wrnum_fcst,dlen_fcst,freq_plot_title,freq_plot_outname)


if __name__ == "__main__":
    main()
