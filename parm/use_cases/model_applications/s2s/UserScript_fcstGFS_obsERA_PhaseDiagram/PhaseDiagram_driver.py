#!/usr/bin/env python3
"""
Driver Script to read in OMI or RMM indices and plot phase diagram for specified dates. 
OMI values can be obtained from https://psl.noaa.gov/mjo/, RMM values can be obtained from 
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
"""

import os
import atexit
import numpy as np
import pandas as pd
import datetime
import warnings

import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi


def handle_exit(obs_timefile,fcst_timefile):
    try:
        os.remove(obs_timefile)
    except:
        pass

    try:
        os.remove(fcst_timefile)
    except:
        pass

def run_phasediagram_steps(inlabel, alldata_timefile, oplot_dir):

    # which index are we plotting
    indexname = os.environ['PLOT_INDEX']

    pltfile = os.path.join(os.environ[inlabel+'_PHASE_DIAGRAM_INPUT_DIR'],
        os.environ[inlabel+'_PHASE_DIAGRAM_INPUT_FILE'])

    # read data from text file
    if indexname=='OMI':
        data = pd.read_csv(pltfile, header=None, delim_whitespace=True, names=['yyyy','mm','dd','hh','pc1','pc2','amp'],
            parse_dates={'dtime':['yyyy','mm','dd','hh']})
    elif indexname=='RMM':
        data = pd.read_csv(pltfile,  header=None, delim_whitespace=True,
            names=['yyyy','mm','dd', 'pc1','pc2','phase','amp','source'], parse_dates={'dtime':['yyyy','mm','dd']})

    # Get the file with the listing of times and format of this file
    alldata_timefmt = os.environ[inlabel+'_PHASE_DIAGRAM_INPUT_TIME_FMT']

    # Read the file
    with open(alldata_timefile) as at:
        alldata_time = at.read().splitlines()

    keepdata = []
    for dd in alldata_time:
        timeloc = np.where(data.dtime == datetime.datetime.strptime(dd,alldata_timefmt))
        if len(timeloc[0]) > 0:
            for l in timeloc[0]:
                keepdata.append(l)

    pltdata = data.iloc[keepdata]
    dates = np.array(pltdata.dtime.dt.strftime('%Y%m%d').values,dtype=int)
    months = np.array(pltdata.dtime.dt.strftime('%m').values,dtype=int)
    days = np.array(pltdata.dtime.dt.strftime('%d').values,dtype=int)
    PC1 = np.array(pltdata.pc1.values)
    PC2 = np.array(pltdata.pc2.values)

    # plot the phase diagram
    phase_plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_NAME',inlabel+'_phase'))
    phase_plot_format = os.environ.get(inlabel+'_PHASE_PLOT_OUTPUT_FORMAT','png')

    # plot the phase diagram
    pmi.phase_diagram(indexname,PC1,PC2,dates,months,days,phase_plot_name,'png')


def main():

    obs_timelist = os.path.join(os.environ.get('OBS_PHASE_DIAGRAM_INPUT_DIR',''),
        os.environ.get('OBS_PHASE_DIAGRAM_INPUT_TIMELIST_TEXTFILE',''))
    fcst_timelist = os.path.join(os.environ.get('FCST_PHASE_DIAGRAM_INPUT_DIR',''),
        os.environ.get('FCST_PHASE_DIAGRAM_INPUT_TIMELIST_TEXTFILE',''))
    atexit.register(handle_exit,obs_timelist,fcst_timelist)

    # Check for an output plot directory in the configs.  Create one if it does not exist
    oplot_dir = os.environ.get('PHASE_DIAGRAM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = os.environ['OUTPUT_BASE']
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    # Determine if doing forecast or obs
    run_obs_phasediagram = os.environ.get('RUN_OBS','False').lower()
    run_fcst_phasediagram = os.environ.get('FCST_RUN_FCST','False').lower()

    # Run the steps to compute OMM
    # Observations
    if (run_obs_phasediagram == 'true'):
        run_phasediagram_steps('OBS', obs_timelist, oplot_dir)

    # Forecast
    if (run_fcst_phasediagram == 'true'):
        run_phasediagram_steps('FCST', fcst_timelist, oplot_dir)

    # nothing selected
    if (run_obs_phasediagram == 'false') and (run_fcst_phasediagram == 'false'):
        warnings.warn('Forecast and Obs runs not selected, no plots will be created')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
