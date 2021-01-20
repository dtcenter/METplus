#!/usr/bin/env python3

"""
Load fieldijn from npz file created with save_ensemble_data.py
helper function, compute ensemble mean and spread, compute
difficulty index for a set of thresholds, plot and save the results.
Author: Bill Campbell, NRL and Lindsay Blank, NCAR

Taken from original test_difficulty_index.py but replacing with METcalcpy and METplotpy.

"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from metcalcpy.calc_difficulty_index import forecast_difficulty as di
from metcalcpy.calc_difficulty_index import EPS
from metcalcpy.piecewise_linear import PiecewiseLinear as plin
import metplotpy.plots.difficulty_index.mycolormaps as mcmap
from metplotpy.plots.difficulty_index.plot_difficulty_index import plot_field


def load_data(filename):
    """Load ensemble data from file"""
    loaded = np.load(filename)
    lats, lons = (loaded['lats'], loaded['lons'])
    fieldijn = np.ma.masked_invalid(
        np.ma.masked_array(
            data=loaded['data']))

    return lats, lons, fieldijn


def compute_stats(field):
    """Compute mean and std dev"""
    mu = np.mean(field, axis=-1)
    sigma = np.std(field, axis=-1, ddof=1)

    return mu, sigma

def compute_wind_envelope():
    """
    Computes piecewise linear envelope for winds in knots.

    Returns
    -------
    Piecewise linear object

    """
    # Envelope for version 6.1, the default
    xunits = 'kn'
    A6_1_name = "A6_1"
    A6_1_left = 0.0
    A6_1_right = 0.0
    A6_1_xlist = [5.0, 28.0, 34.0, 50.0]
    A6_1_ylist = [0.0, 1.5, 1.5, 0.0]
    Aplin =\
            plin(A6_1_xlist, A6_1_ylist, xunits=xunits,
                    right=A6_1_right, left=A6_1_left, name=A6_1_name)

    return Aplin

def compute_difficulty_index(field, mu, sigma, thresholds, Aplin):
    """
    Compute difficulty index for an ensemble forecast given
    a set of thresholds, returning a dictionary of fields.
    """
    dij = {}
    for threshold in thresholds:
        dij[threshold] =\
            di(sigma, mu, threshold, field, Aplin=Aplin, sigma_over_mu_ref=EPS)

    return dij


def plot_difficulty_index(dij, lats, lons, thresholds, units):
    """
    Plot the difficulty index for a set of thresholds,
    returning a dictionary of figures
    """
    plt.close('all')
    myparams = {'figure.figsize': (8, 5),
                'figure.max_open_warning': 40}
    plt.rcParams.update(myparams)
    figs = {}
    cmap = mcmap.stoplight()
    for threshold in thresholds:
        if np.max(dij[threshold]) <= 1.0:
            vmax = 1.0
        else:
            vmax = 1.5
        figs[threshold] =\
            plot_field(dij[threshold],
                          lats, lons, vmin=0.0, vmax=vmax, cmap=cmap,
                          xlab='Longitude \u00b0E', ylab='Latitude',
                          clab='thresh={} {}'.format(threshold, units),
                          title='Forecast Decision Difficulty Index')

    return figs


def save_difficulty_figures(figs, save_thresh, units):
    """
    Save subset of difficulty index figures.
    """
    fig_fmt = os.environ.get('DIFF_INDEX_FIG_FMT')
    fig_basename = os.environ.get('DIFF_INDEX_FIG_BASENAME')

    # create output directory if it does not already exist
    output_dir = os.path.dirname(fig_basename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for thresh in save_thresh:
        thresh_str = '{:.2f}'.format(thresh).replace('.', '_')
        fig_name = (fig_basename + thresh_str +
                    '_' + units + '.' + fig_fmt)
        print('Saving {}...\n'.format(fig_name))
        figs[thresh].savefig(fig_name, format=fig_fmt)


def plot_statistics(mu, sigma, lats, lons, units='feet'):
    """Plot ensemble mean and spread, returning figure handles"""
    cmap = mcmap.spectral()
    mu_fig =\
        plot_field(mu, lats, lons, cmap=cmap, clab=units,
                      vmin=0.0, vmax=np.nanmax(mu),
                      xlab='Longitude \u00b0E',
                      ylab='Latitude',
                      title='Forecast Ensemble Mean')
    sigma_fig =\
        plot_field(sigma, lats, lons, cmap=cmap, clab=units,
                      vmin=0.0, vmax=np.nanmax(sigma),
                      xlab='Longitude \u00b0E',
                      ylab='Latitude',
                      title='Forecast Ensemble Std')

    return mu_fig, sigma_fig


def save_stats_figures(mu_fig, sigma_fig):
    """
    Save ensemble mean and spread figures.
    """

    fig_fmt = os.environ.get('DIFF_INDEX_FIG_FMT')
    fig_basename = os.environ.get('DIFF_INDEX_FIG_BASENAME')
    mu_name = fig_basename + 'mean.' + fig_fmt
    print('Saving {}...\n'.format(mu_name))
    mu_fig.savefig(mu_name, format=fig_fmt)
    sigma_name = fig_basename + 'std.' + fig_fmt
    print('Saving {}...\n'.format(sigma_name))
    sigma_fig.savefig(sigma_name, format=fig_fmt)


def main():
    """
    Load fieldijn from npz file created with NCEP_test.py
    helper function, compute ensemble mean and spread, compute
    difficulty index for a set of thresholds, plot and save the results.
    """

    filename = os.environ.get('DIFF_INDEX_INPUT_FILENAME')
    lats, lons, fieldijn = load_data(filename)
    # Convert m/s to knots
    units = os.environ.get('DIFF_INDEX_UNITS')
    mps2kn = 1.94384
    fieldijn = mps2kn * fieldijn
    # Ensemble mean, std dev
    muij, sigmaij = compute_stats(fieldijn)
    # Windspeed envelope
    Aplin = compute_wind_envelope()
    # Difficulty index for a set of thresholds
    #thresholds = np.arange(os.environ.get('DIFF_INDEX_THRESH_START'), os.environ.get('DIFF_INDEX_THRESH_END'), os.environ.get('DIFF_INDEX_THRESH_STEP'))
    start = float(os.environ.get('DIFF_INDEX_THRESH_START'))
    stop = float(os.environ.get('DIFF_INDEX_THRESH_END'))
    step = float(os.environ.get('DIFF_INDEX_THRESH_STEP'))
    thresholds = np.arange(start, stop, step)
    dij = compute_difficulty_index(fieldijn, muij, sigmaij, thresholds, Aplin=Aplin)
    # Plot and save difficulty index figures
    figs = plot_difficulty_index(dij, lats, lons, thresholds, units)
    save_start = float(os.environ.get('DIFF_INDEX_SAVE_THRESH_START'))
    save_stop = float(os.environ.get('DIFF_INDEX_SAVE_THRESH_STOP'))
    save_step = float(os.environ.get('DIFF_INDEX_SAVE_THRESH_STEP'))
    save_thresh = np.arange(save_start, save_stop, save_step)
    save_difficulty_figures(figs, save_thresh, units)
    # Plot and save ensemble mean, std_dev
    mu_fig, sigma_fig =\
        plot_statistics(muij, sigmaij, lats, lons, units=units)
    save_stats_figures(mu_fig, sigma_fig)


if __name__ == '__main__':
    main()
