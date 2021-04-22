#!/usr/bin/env python3

"""
This is an example script for plotting cross spectral components. The script reads in output files computed
by the example_cross_spectra.py script and uses the plotly plotting routines in spacetime_plot.py to generate
a panel plot of coherence spectra.
"""
import numpy as np
import os
import xarray as xr

import metplotpy.contributed.spacetime_plot.spacetime_plot as stp

# location of the output files from example_cross_spectra
# pathdata = '../data/'
pathdata = os.environ.get("DATA_PATH","/d2/METplus_Data")
# location of the plot files
# plotpath = '../plots/'
plotpath = './'

# plot layout parameters
flim = 0.5  # maximum frequency in cpd for plotting
nWavePlt = 20  # maximum wavenumber for plotting
contourmin = 0.1  # contour minimum
contourmax = 0.8  # contour maximum
contourspace = 0.1  # contour spacing
N = [1, 2]  # wave modes for plotting
source = ""
spd = 2

symmetry = "symm"      #("symm", "asymm", "latband")
filenames = os.environ.get("INPUT_FILE_NAMES","ERAI_TRMM_P_symn,ERAI_P_D850_symn,ERAI_P_D200_symn").split(",")
print(filenames)
#filenames = ['ERAI_TRMM_P_symm_'+str(spd)+'spd',
#             'ERAI_P_D850_symm_'+str(spd)+'spd',
#             'ERAI_P_D200_symm_'+str(spd)+'spd']
vars1 = ['ERAI P', 'ERAI P', 'ERAI P']
vars2 = ['TRMM', 'ERAI D850', 'ERAI D200']
nplot = len(vars1)

for pp in np.arange(0, nplot, 1):

    # read data from file
    var1 = vars1[pp]
    var2 = vars2[pp]
    #fin = xr.open_dataset(pathdata + 'SpaceTimeSpectra_' + filenames[pp] + '.nc')
    print("Filename ",filenames[pp])
    fin = xr.open_dataset(filenames[pp])
    STC = fin['STC'][:, :, :]
    wnum = fin['wnum']
    freq = fin['freq']

    ifreq = np.where((freq[:] >= 0) & (freq[:] <= flim))
    iwave = np.where(abs(wnum[:]) <= nWavePlt)

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
        Coh2 = np.empty([nplot, len(freq[ifreq]), len(wnum[iwave])])
        Phs1 = np.empty([nplot, len(freq[ifreq]), len(wnum[iwave])])
        Phs2 = np.empty([nplot, len(freq[ifreq]), len(wnum[iwave])])
        Pow1 = np.empty([nplot, len(freq[ifreq]), len(wnum[iwave])])
        Pow2 = np.empty([nplot, len(freq[ifreq]), len(wnum[iwave])])
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


# plot coherence
stp.plot_coherence(Coh2, Phs1, Phs2, symmetry, source, vars1, vars2, plotpath, flim, 20, contourmin, contourmax,
                   contourspace, nplot, N)

exit()
