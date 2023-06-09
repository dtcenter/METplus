#!/usr/bin/env python3

"""
This is an example script for plotting cross spectral components. The script reads in output files computed
by the example_cross_spectra.py script and uses the plotly plotting routines in spacetime_plot.py to generate
a panel plot of coherence spectra.
"""
import numpy as np
import os
import sys
import xarray as xr

import metplotpy.contributed.spacetime_plot.spacetime_plot as stp
import metcalcpy.util.read_env_vars_in_config as readconfig


# Read in the YAML config file
# user can use their own, if none specified at the command line,
# use the "default" example YAML config file, spectra_plot_coh2.py
# Using a custom YAML reader so we can use environment variables
plot_config_file = os.getenv("PLOT_SPECTRA_YAML_CONFIG_NAME","spectra_plot.yaml")

config_dict = readconfig.parse_config(plot_config_file)

# Retrieve settings from config file
#pathdata is now set in the METplus conf file
#pathdata = config_dict['pathdata'][0]
plotpath = config_dict['plotpath'][0]
print("Output path ",plotpath)
model = config_dict['model']
var2 = config_dict['var2']
var3 = config_dict['var3']

# plot layout parameters
flim = 0.5  # maximum frequency in cpd for plotting
nWavePlt = 20  # maximum wavenumber for plotting
contourmin = 0.1  # contour minimum
contourmax = 0.8  # contour maximum
contourspace = 0.1  # contour spacing
N = [1, 2]  # wave modes for plotting
source = ""
spd = 4

symmetry = "symm"      #("symm", "asymm", "latband")
#filenames = os.environ.get("INPUT_FILE_NAMES","ERAI_TRMM_P_symn,ERAI_P_D850_symn,ERAI_P_D200_symn").split(",")
#vars1 = ['ERAI P', 'ERAI P', 'ERAI P']
#vars2 = ['TRMM', 'ERAI D850', 'ERAI D200']
filenames = os.environ.get("PLOT_SPECTRA_INPUT_FILE_NAMES","ERAI_P_D850_symn,ERAI_P_D200_symn,ERAI_P_D200_symn").split(",")
vars1 = [model+' P',model+' P',model+' P']
vars2 = [model+' '+var2,model+' '+var3,model+' '+var3]
nplot = len(vars1)

npanel =3
for pp in np.arange(0, nplot, 1):

    # read data from file
    var1 = vars1[pp]
    var2 = vars2[pp]
    print("Filename ",filenames[pp])
    fin = xr.open_dataset(filenames[pp])
    STC = fin['STC'][:, :, :]
    wnum = fin['wnum']
    freq = fin['freq']

    #ifreq = np.where((freq[:] >= 0) & (freq[:] <= flim))
    #iwave = np.where(abs(wnum[:]) <= nWavePlt)

    STC[:, freq[:] == 0, :] = 0.
    STC = STC.sel(wnum=slice(-nWavePlt, nWavePlt))
    STC = STC.sel(freq=slice(0, flim))
    coh2 = np.squeeze(STC[4, :, :])
    phs1 = np.squeeze(STC[6, :, :])
    phs2 = np.squeeze(STC[7, :, :])
    phs1.where(coh2 <= contourmin, drop=True)
    phs2.where(coh2 <= contourmin, drop=True)
    pow1 = np.squeeze(STC[0, :, :])
    pow2 = np.squeeze(STC[1, :, :])
    pow1.where(pow1 <= 0, drop=True)
    pow2.where(pow2 <= 0, drop=True)

    if pp == 0:
        ifreq = np.where((freq[:] >= 0) & (freq[:] <= flim))
        iwave = np.where(abs(wnum[:]) <= nWavePlt)
        Coh2 = np.full([npanel, len(freq[ifreq]), len(wnum[iwave])], np.nan)
        Phs1 = np.full([npanel, len(freq[ifreq]), len(wnum[iwave])], np.nan)
        Phs2 = np.full([npanel, len(freq[ifreq]), len(wnum[iwave])], np.nan)
        Pow1 = np.full([npanel, len(freq[ifreq]), len(wnum[iwave])], np.nan)
        Pow2 = np.full([npanel, len(freq[ifreq]), len(wnum[iwave])], np.nan)
        k = wnum[iwave]
        w = freq[ifreq]

    Coh2[pp, :, :] = coh2
    Phs1[pp, :, :] = phs1
    Phs2[pp, :, :] = phs2
    Pow1[pp, :, :] = np.log10(pow1)
    Pow2[pp, :, :] = np.log10(pow2)

    phstmp = Phs1
    phstmp = np.square(Phs1) + np.square(Phs2)
    phstmp = np.where(phstmp == 0, np.nan, phstmp)
    scl_one = np.sqrt(1 / phstmp)
    Phs1 = scl_one * Phs1
    Phs2 = scl_one * Phs2

# create output directory if it does not exist
if not os.path.exists(plotpath):
    print(f"Creating output directory: {plotpath}")
    os.makedirs(plotpath)

# plot coherence
stp.plot_coherence(Coh2, Phs1, Phs2, symmetry, source, vars1, vars2, plotpath, flim, 20, contourmin, contourmax,
                   contourspace, npanel, N)

# check if output file exists since plotting function
# doesn't return an error code on failure
expected_file = os.path.join(plotpath,
                             'SpaceTimeCoherence_.png')
if not os.path.exists(expected_file):
    print(f"ERROR: Could not create output file: {expected_file}")
    sys.exit(1)
