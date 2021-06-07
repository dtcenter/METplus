"""
Read in OMI or RMM indices and plot phase diagram for specified dates. OMI values
can be obtained from https://psl.noaa.gov/mjo/, RMM values can be obtained from 
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
"""

import numpy as np
import pandas as pd
import datetime

from plot_mjo_indices import phase_diagram


def run_phasediagram_steps(inlabel, inconfig, oplot_dir):

    fileconfig = config_metplus.replace_config_from_section(inconfig,'phase_diagram')
    use_init =  is_loop_by_init(inconfig)
    alldata_time = find_times(fileconfig, use_init)

    # which index are we plotting
    indexname = 'RMM'  # 'RMM' or 'OMI'

    # set dates to read and plot
    datestrt = 20120101
    datelast = 20120331

    # read data from text file
    if indexname=='OMI':
        data = pd.read_csv('omi.1x.txt', header=None, delim_whitespace=True, names=['yyyy','mm','dd','hh','pc1','pc2','amp'])
    elif indexname=='RMM':
        data = pd.read_csv('rmm.1x.txt',  header=None, delim_whitespace=True, names=['yyyy','mm','dd', 'pc1','pc2','phase','amp','source'])

    DATES = data.yyyy.values*10000 + data.mm.values*100 + data.dd.values
    MONTHS = data.mm.values
    DAYS = data.dd.values
    #print(dates)

    istrt = np.where(DATES==datestrt)[0][0]
    ilast = np.where(DATES==datelast)[0][0]
    print(DATES[istrt], DATES[ilast])
    #print(istrt, ilast)

    # subset data to only the dates we want to plot
    dates = DATES[istrt:ilast+1]
    months = MONTHS[istrt:ilast+1]
    days = DAYS[istrt:ilast+1]
    print(dates.min(), dates.max())
    PC1 = data.pc1.values[istrt:ilast+1]
    PC2 = data.pc2.values[istrt:ilast+1]

    # plot the phase diagram
    phase_diagram(indexname,PC1,PC2,dates,months,days,indexname+'_phase','png')

def main():

    # Start configs
    config_list = sys.argv[1:]
    config = pre_run_setup(config_list)

    # Check for an output plot directory in the configs.  Create one if it does not exist
    oplot_dir = config.getstr('phase_diagram','PHASE_DIAGRAM_PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = config.getstr('config','OUTPUT_BASE')
        oplot_dir = obase+'/'+'plots'
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir)

    #  Determine if doing forecast or obs
    run_obs_phasediagram = config.getbool('phase_diagram','OBS_RUN', False)
    run_fcst_phasediagram = config.getbool('phase_diagram','FCST_RUN', False)

    # Run the steps to compute OMM
    # Observations
    if run_obs_phasediagram:
        run_phasediagram_steps('OBS', config, oplot_dir)

    # Forecast
    if run_fcst_phasediagram:
        run_phasediagram_steps('FCST', config, oplot_dir)


if __name__ == "__main__":
    main()
