#!/usr/bin/env /nrit/ral/anaconda3/bin/python3

##KE Spectra plotting code
##Written by Maria Frediani, NSF NCAR / RAL, 2022
##Modifications by Will Mayfield, 2024
##Modifications by Christina Kalb, 2025

import os
import sys
import numpy as np
import datetime
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
from netCDF4 import Dataset

import metcalcpy.util.read_env_vars_in_config as readconfig

def start_plot(dom_kmax, kmax, grid_res, **kwargs):

    mpl.rcParams['font.size'] = 14
    plt.ion()

    # Defaults
    fig = plt.figure(figsize=(10, 10))

    # Gridspec
    grrows = 1
    grcols = 1
    gs = mpl.gridspec.GridSpec(grrows, grcols)

    tt = fig.text(0.5,
                  0.985,
                  kwargs.get('title', ''),
                  ha='center',
                  va='top',
                  fontsize=14)

    iplt = 0
    ax = fig.add_subplot(gs[iplt])

    # --------------------------------------------------------

    ax.grid(which='both', color='grey', ls='--', lw=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')

    ###################################
    ##set plot limits
    ###################################
    ax.set_xlim(left=2)
    ax.set_xlim(right=dom_kmax)
    ax.set_ylim(bottom=5e-8)
    ax.set_ylim(top=1000)

    factork = 2 * np.pi
    lmb = 200  # Wavelength of slope switch [km]
    kx = int(dom_kmax * grid_res / lmb)

    k = np.arange(1, kmax + 1)

    ax.plot(2 * k[kx:], [(k / factork)**(-5 / 3) for k in k[kx:]],
            color='grey',
            lw=0.8,
            ls='--')

    ax.plot(2 * k[:kx + 1], [(k / factork / 1.5)**(-3) for k in k[:kx + 1]],
            color='grey',
            lw=0.8,
            ls='--')

    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xscale('log')
    wl = [1000, 500, 100, 50,
          15, 6]  # min lambda: 5dx = 15km, max lambda: 2*N*dx/(k=2) = 3066km
    kwl = [2 * dom_kmax * grid_res / l for l in wl]

    ax.plot([kwl[-1], kwl[-1]], ax.get_ylim(), color='darkgrey', lw=1, ls='--')

    ax2.set_xticks(kwl)
    ax2.set_xticklabels(wl)
    ax2.grid(None)
    ax2.tick_params(axis='x', which='minor', top=False)
    ax2.tick_params(axis='x',
                    which='major',
                    direction='out',
                    width=1,
                    length=5,
                    color='lightgrey',
                    top=True)

    ax.tick_params(axis='both',
                   which='major',
                   direction='out',
                   width=1,
                   length=5,
                   color='lightgrey',
                   bottom=True,
                   left=True)
    ax.tick_params(axis='x', which='minor', bottom=False)

    ax.set_xlabel('Wavenumber k')
    ax2.set_xlabel('Wavelength [km]')
    ax.set_ylabel('KE error')

    return [ax, tt]


def main():
    # Get the list of files and yaml config
    grid_diag_filetxt = os.environ.get('METPLUS_FILELIST_POWER_SPECTRA_INPUT','')
    plot_config_file = os.getenv("PLOT_SPECTRA_YAML_CONFIG_NAME","spectra_plot.yaml")
    config_dict = readconfig.parse_config(plot_config_file)

    # Read in the list of files
    with open(grid_diag_filetxt) as gdl:
        grid_diag_files = gdl.read().splitlines()
    if grid_diag_files[0] == 'file_list':
        grid_diag_files = grid_diag_files[1:]
    nfiles = len(grid_diag_files)

    # Get the config options
    ptitle = config_dict['plot_title']
    fname = config_dict['plot_filename']
    grid_km = config_dict['grid_km']

    # Make a plot directory if it doesn't exist
    plotdir = os.path.dirname(fname)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)

    snsc = mpl.colormaps.get_cmap('tab10')
    lwidth = 1.8
    ls = ['-', '--', ':', '-.']

    for idx2,grid_diag_file in enumerate(grid_diag_files):#separate plot for forecast hours

        nc = Dataset(grid_diag_file, 'r')
        var = 'error_power_spectrum_KENG_CTRL_P500_KENG_EXPT_P500'
        eKE = nc.variables[var][:]
        eKEp1 = eKE

        fhr_full = nc.getncattr("lead_beg")
        fhr = fhr_full[0:2]

        # Set up the periodic domain
        # This follows from the paper Denis et al 2002 (MWR) and Durran et al 2017 (MWR)
        eKE_kp1 = eKEp1[0:-2:2] + eKEp1[1:-1:2]

        # Setup k, kmx, kmax
        eKE_dims = eKE_kp1.shape
        k = np.arange(2, 2*eKE_dims[0] + 1, 2)
        kmx = eKE_dims[0] - 1
        kmax = eKE.shape[0] + 1

        # --------------------------------------------------------
        # --------------------------------------------------------
        # Plot
        # Start Plot
        if idx2 == 0:
            ax, tt = start_plot(kmax, k[kmx], grid_km, title=ptitle)
        color_index = idx2

        #il = 0
        lw = lwidth

        ax.plot(k[:kmx + 1],
                eKE_kp1[:kmx + 1],
                lw=lw,
                ls=ls[0],
                color=snsc.colors[color_index],
                label=f'{fhr:02}h')

    # --------------------------------------------------------
    ax.legend(loc='lower left',prop={'size': 11})
    plt.savefig(fname, bbox_inches='tight', dpi=100)
    if idx2 == (nfiles-1):
        plt.close()


if __name__ == "__main__":
    main()
