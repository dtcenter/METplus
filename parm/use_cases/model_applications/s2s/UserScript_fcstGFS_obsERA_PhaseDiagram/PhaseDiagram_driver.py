#!/usr/bin/env python3
"""
Driver Script to read in OMI or RMM indices and plot phase diagram for specified dates. 
OMI values can be obtained from https://psl.noaa.gov/mjo/, RMM values can be obtained from 
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
"""

import os
import sys
import numpy as np
import pandas as pd
import datetime
import warnings

from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub
from RMM_OMI_util import find_times
import metplotpy.contributed.mjo_rmm_omi.plot_mjo_indices as pmi


def run_phasediagram_steps(inlabel, inconfig, oplot_dir):
#def run_phasediagram_steps(inlabel, oplot_dir):

    fileconfig = config_metplus.replace_config_from_section(inconfig,'phase_diagram')
    use_init =  is_loop_by_init(inconfig)
    alldata_time = find_times(fileconfig, use_init)

    # which index are we plotting
    indexname = os.environ['PLOT_INDEX']

    # Get input filename and make sure it exists
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
    alldata_timefile = os.environ['OBS_PHASE_DIAGRAM_INPUT_TEXTFILE'] 
    alldata_timefmt = os.environ['OBS_PHASE_DIAGRAM_INPUT_TIME_FMT']

    # Read the file
    with open(alldata_timefile) as at:
        alldata_time1 = at.read().splitlines()

    print(alldata_time)
    print(alldata_time1)
    exit()

    keepdata = []
    for dd in alldata_time:
        timeloc = np.where(data.dtime == dd['valid'])
        if len(timeloc[0]) > 0:
            for l in timeloc[0]:
                keepdata.append(l)

    #print()
    #print
    exit()
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

    # Start configs
    config_list = sys.argv[1:]
    config = pre_run_setup(config_list)

    # Check for an output plot directory in the configs.  Create one if it does not exist
    oplot_dir = os.environ.get('PHASE_DIAGRAM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = os.environ['OUTPUT_BASE']
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    #  Determine if doing forecast or obs
    run_obs_phasediagram = os.environ.get('RUN_OBS',False)
    run_fcst_phasediagram = os.environ.get('FCST_RUN_FCST', False)

    # Run the steps to compute OMM
    # Observations
    if run_obs_phasediagram:
        run_phasediagram_steps('OBS', config, oplot_dir)
        #run_phasediagram_steps('OBS', oplot_dir)

    # Forecast
    if run_fcst_phasediagram:
        run_phasediagram_steps('FCST', config, oplot_dir)
        #run_phasediagram_steps('FCST', oplot_dir)

    # nothing selected
    if not run_obs_phasediagram and not run_fcst_phasediagram:
        warnings.warn('Forecast and Obs runs not selected, no plots will be created')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')


if __name__ == "__main__":
    main()
