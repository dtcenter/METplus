#!/usr/bin/env python3

import os
import warnings

import numpy as np

from metcalcpy.contributed.blocking_weather_regime.WeatherRegime import WeatherRegimeCalculation
from metcalcpy.contributed.blocking_weather_regime.Blocking_WeatherRegime_util import parse_steps, read_nc_met, write_mpr_file, reorder_fcst_regimes,reorder_fcst_regimes_correlate
from metplotpy.contributed.weather_regime import plot_weather_regime as pwr


def main():

    steps_list_fcst, steps_list_obs = parse_steps()

    if not steps_list_obs and not steps_list_fcst:
        warnings.warn('No processing steps requested for either the model or observations,')
        warnings.warn(' nothing will be run')
        warnings.warn('Set FCST_STEPS and/or OBS_STEPS in the [user_env_vars] section to process data')

    ######################################################################
    # Weather Regime Calculation and Plotting
    ######################################################################
    # Set up the data
    steps_obs = WeatherRegimeCalculation('OBS')
    steps_fcst = WeatherRegimeCalculation('FCST')

    oplot_dir, mpr_outdir = get_output_dirs()

    z500_obs, lats_obs, lons_obs, timedict_obs, z500_detrend_2d_obs = (
        get_data('OBS', steps_list_obs, steps_obs)
    )
    z500_fcst, lats_fcst, lons_fcst, timedict_fcst, z500_detrend_2d_fcst = (
        get_data('FCST', steps_list_fcst, steps_fcst)
    )

    handle_elbow('OBS', steps_list_obs, steps_obs, z500_detrend_2d_obs, oplot_dir)
    handle_elbow('FCST', steps_list_fcst, steps_fcst, z500_detrend_2d_fcst, oplot_dir)

    z500_detrend_2d_obs = handle_eof('OBS', steps_list_obs, steps_obs, z500_obs, z500_detrend_2d_obs, lons_obs, lats_obs, oplot_dir)
    z500_detrend_2d_fcst = handle_eof('FCST', steps_list_fcst, steps_fcst, z500_fcst, z500_detrend_2d_fcst, lons_fcst, lats_fcst, oplot_dir)

    kmeans_obs, wrnum_obs, perc_obs, wrc_obs = (
        handle_kmeans('OBS', steps_list_obs, steps_obs, z500_detrend_2d_obs, z500_obs, timedict_obs, None)
    )
    kmeans_fcst, wrnum_fcst, perc_fcst, wrc_fcst = (
        handle_kmeans('FCST', steps_list_fcst, steps_fcst, z500_detrend_2d_fcst, z500_fcst, timedict_fcst, kmeans_obs)
    )

    handle_kmeans_mpr(wrc_fcst, wrc_obs, timedict_fcst, timedict_obs, mpr_outdir)

    handle_kmeans_plot('OBS', steps_list_obs, kmeans_obs, wrnum_obs, perc_obs, lons_obs, lats_obs, oplot_dir)
    handle_kmeans_plot('FCST', steps_list_fcst, kmeans_fcst, wrnum_fcst, perc_fcst, lons_fcst, lats_fcst, oplot_dir)

    wrfreq_obs, dlen_obs = handle_time_freq('OBS', steps_list_obs, steps_obs, wrc_obs)
    wrfreq_fcst, dlen_fcst = handle_time_freq('FCST', steps_list_fcst, steps_fcst, wrc_fcst)

    handle_time_freq_mpr(wrfreq_fcst, wrfreq_obs, timedict_fcst, timedict_obs, wrnum_obs, mpr_outdir)

    handle_freq_plot('OBS', steps_list_obs, wrfreq_obs, wrnum_obs, dlen_obs, oplot_dir)
    handle_freq_plot('FCST', steps_list_fcst, wrfreq_fcst, wrnum_fcst, dlen_fcst, oplot_dir)


def get_output_dirs():
    # Check to see if there is a plot directory
    oplot_dir = os.environ.get('WR_PLOT_OUTPUT_DIR','')
    output_base = os.environ['SCRIPT_OUTPUT_BASE']

    if not oplot_dir:
        oplot_dir = os.path.join(output_base, 'plots')

    # create plot dir if it doesn't already exist
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

     # Check to see if there is a mpr output directory
    mpr_outdir = os.environ.get('WR_MPR_OUTPUT_DIR','')
    if not mpr_outdir:
        mpr_outdir = os.path.join(output_base, 'mpr')

    return oplot_dir, mpr_outdir


def get_data(data_type, steps_list, steps):
    if "ELBOW" not in steps_list and "EOF" not in steps_list and "KMEANS" not in steps_list:
        return None, None, None, None, None

     # Get number of seasons and days per season
    nseasons = int(os.environ['NUM_SEASONS'])
    dseasons = int(os.environ['DAYS_PER_SEASON'])

    # Grab the Daily text files
    wr_filetxt = os.environ.get(f'METPLUS_FILELIST_{data_type}_INPUT','')

    with open(wr_filetxt) as wl:
        infiles = wl.read().splitlines()

    # Remove the first line if it's there
    if infiles[0] == 'file_list':
        infiles = infiles[1:]

    if len(infiles) != (nseasons*dseasons):
        raise ValueError(f'Invalid {data_type.capitalize()} data; each year must contain the same date range to calculate seasonal averages.')

    invar = os.environ.get(f'{data_type}_WR_VAR','')
    z500, lats, lons, timedict = read_nc_met(infiles, invar, nseasons, dseasons)
    _, z500_detrend_2d = steps.weights_detrend(lats, lons, z500)
    return z500, lats, lons, timedict, z500_detrend_2d


def handle_elbow(data_type, steps_list, steps, z500_detrend_2d, plot_dir):
    if "ELBOW" not in steps_list:
        # error if elbow plot is requested without running elbow
        if "PLOTELBOW" in steps_list:
            raise ValueError(f'Must set ELBOW in {data_type}_LIST if PLOTELBOW is set.')

        # do nothing if elbow is not requested
        return

    print(f'Running {data_type.capitalize()} Elbow')
    k, d, mi, line, curve = steps.run_elbow(z500_detrend_2d)

    if "PLOTELBOW" not in steps_list:
        # skip plot if not requested
        return

    print(f'Creating {data_type.capitalize()} Elbow plot')
    elbow_plot_title = os.environ.get(f'{data_type}_ELBOW_PLOT_TITLE', 'Elbow Method For Optimal k')
    elbow_plot_outname = os.environ.get(f'{data_type}_ELBOW_PLOT_OUTPUT_NAME', f'{data_type.lower()}_elbow')
    elbow_plot_outname = os.path.join(plot_dir, elbow_plot_outname)
    pwr.plot_elbow(k, d, mi, line, curve, elbow_plot_title, elbow_plot_outname)


def handle_eof(data_type, steps_list, steps, z500, z500_detrend_2d, lons, lats, oplot_dir):
    if "EOF" not in steps_list:
        if "PLOTEOF" in steps_list:
            raise ValueError(f'Must set EOF in {data_type}_LIST if PLOTEOF is set.')
        return z500_detrend_2d

    print(f'Running {data_type.capitalize()} EOF')
    eof, pc, wrnum, variance_fractions = steps.Calc_EOF(z500)
    z500_detrend_2d = steps.reconstruct_heights(eof,pc,z500_detrend_2d.shape)

    if "PLOTEOF" in steps_list:
        print(f'Plotting {data_type.capitalize()} EOFs')
        pltlvls_str = os.environ['EOF_PLOT_LEVELS'].split(',')
        pltlvls = [float(pp) for pp in pltlvls_str]
        eof_plot_outname = os.environ.get(f'{data_type}_EOF_PLOT_OUTPUT_NAME', f'{data_type.lower()}_eof')
        eof_plot_outname = os.path.join(oplot_dir, eof_plot_outname)
        pwr.plot_eof(eof, wrnum, variance_fractions, lons, lats, eof_plot_outname, pltlvls)

    return z500_detrend_2d


def handle_kmeans(data_type, steps_list, steps, z500_detrend_2d, z500, timedict, kmeans_obs):
    if "KMEANS" not in steps_list:
        return None, None, None, None

    print(f'Running {data_type.capitalize()} K Means')
    kmeans, wrnum, perc, wrc = steps.run_K_means(z500_detrend_2d,timedict, z500.shape)

    # handle reordering of kmeans, perc, and wrc for forecast only
    if data_type == 'FCST':
        reorder_fcst = os.environ.get('REORDER_FCST', 'False').lower() == 'true'
        reorder_fcst_manual = os.environ.get('REORDER_FCST_MANUAL', 'False').lower() == 'true'
        if reorder_fcst and kmeans_obs is not None:
            kmeans, perc, wrc = reorder_fcst_regimes_correlate(kmeans_obs, kmeans, perc, wrc, wrnum)
        if reorder_fcst_manual:
            fcst_order_str = os.environ['FCST_ORDER'].split(',')
            fcst_order = [int(fo) for fo in fcst_order_str]
            kmeans, perc, wrc = reorder_fcst_regimes(kmeans, perc, wrc, wrnum, fcst_order)

    steps.write_K_means_file(timedict, wrc)
    return kmeans, wrnum, perc, wrc


def handle_kmeans_mpr(wrc_fcst, wrc_obs, timedict_fcst, timedict_obs, mpr_outdir):
    # this check will be hit if KMEANS was not requested in either fcst or obs lists
    if wrc_fcst is None or wrc_obs is None:
        return

    # Write matched pair output for weather regime classification
    modname = os.environ.get('MODEL_NAME', 'GFS')
    maskname = os.environ.get('MASK_NAME', 'FULL')
    mpr_full_outdir = os.path.join(mpr_outdir, 'WeatherRegime')
    wr_outfile_prefix = os.path.join(mpr_full_outdir, f'weather_regime_stat_{modname}')
    wrc_obs_mpr = wrc_obs[:,:,np.newaxis]
    wrc_fcst_mpr = wrc_fcst[:,:,np.newaxis]

    if not os.path.exists(mpr_full_outdir):
        os.makedirs(mpr_full_outdir)

    write_mpr_file(wrc_obs_mpr, wrc_fcst_mpr, [0.0], [0.0], timedict_obs, timedict_fcst, modname, 'NA',
                   'WeatherRegimeClass', 'class', 'Z500', 'WeatherRegimeClass', 'class', 'Z500', maskname,'500',wr_outfile_prefix)


def handle_kmeans_plot(data_type, steps_list, kmeans, wrnum, perc, lons, lats, plot_dir):
    if "PLOTKMEANS" not in steps_list:
        return

    if kmeans is None or wrnum is None or perc is None:
        raise ValueError(f'Must run {data_type.lower()} Kmeans before plotting {data_type.lower()} Kmeans.')

    print(f'Plotting {data_type.capitalize()} K Means')
    pltlvls_str = os.environ['KMEANS_PLOT_LEVELS'].split(',')
    pltlvls = [float(pp) for pp in pltlvls_str]
    kmeans_plot_outname = os.environ.get(f'{data_type}_KMEANS_PLOT_OUTPUT_NAME', f'{data_type.lower()}_kmeans')
    kmeans_plot_outname = os.path.join(plot_dir, kmeans_plot_outname)
    pwr.plot_K_means(kmeans, wrnum, lons, lats, perc, kmeans_plot_outname, pltlvls)


def handle_time_freq(data_type, steps_list, steps, wrc):
    if "TIMEFREQ" not in steps_list:
        return None, None

    if wrc is None:
        raise ValueError(f'Must run {data_type.capitalize()} Kmeans before running frequencies.')

    wrfreq, dlen, _ = steps.compute_wr_freq(wrc)
    return wrfreq, dlen


def handle_time_freq_mpr(wrfreq_fcst, wrfreq_obs, timedict_fcst, timedict_obs, wrnum_obs, mpr_outdir):
    # do not write MPR file if fcst or obs frequency were not requested
    if wrfreq_fcst is None or wrfreq_obs is None or wrnum_obs is None:
        return

    # Write matched pair output for frequency of each weather regime
    modname = os.environ.get('MODEL_NAME', 'GFS')
    maskname = os.environ.get('MASK_NAME', 'FULL')
    mpr_full_outdir = os.path.join(mpr_outdir, 'freq')
    wrfreq_obs_mpr = wrfreq_obs[:,:,:,np.newaxis]
    wrfreq_fcst_mpr = wrfreq_fcst[:,:,:,np.newaxis]

    if not os.path.exists(mpr_full_outdir):
        os.makedirs(mpr_full_outdir)

    for wrn in np.arange(wrnum_obs):
        wr_outfile_prefix = os.path.join(mpr_full_outdir,'weather_regime'+str(wrn+1).zfill(2)+'_freq_stat_'+modname)
        write_mpr_file(wrfreq_obs_mpr[wrn,:,:,:],wrfreq_fcst_mpr[wrn,:,:,:],[0.0],[0.0],timedict_obs,
            timedict_fcst,modname,str(wrn+1).zfill(2),'WeatherRegimeFreq','percent','Z500','WeatherRegimeFreq',
            'percent','Z500',maskname,'500',wr_outfile_prefix)


def handle_freq_plot(data_type, steps_list, wrfreq, wrnum, dlen, oplot_dir):
    if "PLOTFREQ" not in steps_list:
        return

    if wrfreq is None or wrnum is None or dlen is None:
        raise ValueError(f'Must run {data_type.capitalize()} Frequency calculation before plotting the frequencies.')

    freq_plot_title = os.environ.get(f'{data_type}_FREQ_PLOT_TITLE', 'Seasonal Cycle of WR Days/Week')
    freq_plot_outname = os.environ.get(f'{data_type}_FREQ_PLOT_OUTPUT_NAME',f'{data_type.lower()}_freq')
    freq_plot_outname = os.path.join(oplot_dir, freq_plot_outname)

    # Compute mean
    wrmean = np.nanmean(wrfreq, axis=1)
    pwr.plot_wr_frequency(wrmean, wrnum, dlen, freq_plot_title, freq_plot_outname)


if __name__ == "__main__":
    main()
