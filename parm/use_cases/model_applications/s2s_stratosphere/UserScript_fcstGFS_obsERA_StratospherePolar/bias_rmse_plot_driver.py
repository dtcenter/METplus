#!/usr/bin/env python3

"""
Creates Polar Cap Bias and RMSE plots
"""
import os
import sys
import pandas as pd
import numpy as np
import METreadnc.util.read_netcdf as read_netcdf
from metplotpy.contributed.stratosphere_diagnostics.stratosphere_plots import plot_polar_bias,plot_polar_rmse


def main():
    plvar = sys.argv[1]

    """
    Read METplus environment variables
    """
    plot_bias_levels_str = os.environ['PLOT_'+plvar+'_BIAS_LEVELS'].split(',')
    plot_bias_levels = [float(pp) for pp in plot_bias_levels_str]
    plot_bias_title = os.environ['PLOT_'+plvar+'_BIAS_TITLE']
    plot_rmse_levels_str = os.environ['PLOT_'+plvar+'_RMSE_LEVELS'].split(',')
    plot_rmse_levels = [float(pp) for pp in plot_rmse_levels_str]
    plot_rmse_title = os.environ['PLOT_'+plvar+'_RMSE_TITLE']
    output_dir = os.environ['PLOT_OUTPUT_DIR']
    bias_output_file = os.environ.get('PLOT_'+plvar+'_BIAS_OUTPUT_FILE','bias_plot.png')
    rmse_output_file = os.environ.get('PLOT_'+plvar+'_RMSE_OUTPUT_FILE','rmse_plot.png')
    plot_bias_output_file = os.path.join(output_dir,bias_output_file)
    plot_rmse_output_file = os.path.join(output_dir,rmse_output_file)

    """
    Make plot output directory if it doesn't exist
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    """
    Read the list of files
    """
    stat_filetxt = os.environ.get('METPLUS_FILELIST_STAT_INPUT','')
    with open(stat_filetxt) as sf:
        stat_infiles = sf.read().splitlines()
        # Remove the first line if it's there
        if (stat_infiles[0] == 'file_list'):
            stat_infiles = stat_infiles[1:]

    """
    Read the first file and set up arrays
    """
    fleads = len(stat_infiles)
    dfin = pd.DataFrame(pd.read_csv(stat_infiles[0],delim_whitespace=True,header=0))
    dfin['FCST_LEV'] = dfin['FCST_LEV'].str.replace('P', '')
    dfin['FCST_LEV'] = dfin['FCST_LEV'].astype('float64')
    dfin = dfin.sort_values('FCST_LEV')
    flvls = len(dfin)
    plevels = np.empty([fleads,flvls],dtype=float)
    pleads = np.empty([fleads,flvls],dtype=float)
    prmse = np.empty([fleads,flvls],dtype=float)
    pme = np.empty([fleads,flvls],dtype=float)
    plevels[0,:] = dfin['FCST_LEV'].to_numpy()
    pleads[0,:] = dfin['FCST_LEAD'].to_numpy()/10000
    prmse[0,:] = dfin['RMSE'].astype('float64')
    pme[0,:] = dfin['ME'].astype('float64')
    
    """
    Read in the rest of the data
    """
    for i in range(1,len(stat_infiles)): 
        df = pd.DataFrame(pd.read_csv(stat_infiles[i],delim_whitespace=True,header=0))
        df['FCST_LEV'] = df['FCST_LEV'].str.replace('P', '')
        df['FCST_LEV'] = df['FCST_LEV'].astype('float64')
        dfnew = df.sort_values('FCST_LEV')
        plevels[i,:] = dfnew['FCST_LEV'].to_numpy()
        #pleads[i] = dfnew['FCST_LEAD'].to_numpy()[0]/10000
        pleads[i,:] = dfnew['FCST_LEAD'].to_numpy()/10000
        prmse[i,:] = dfnew['RMSE'].astype('float64')
        pme[i,:] = dfnew['ME'].astype('float64')

    """
    Create plots
    """
    print(plot_bias_levels)
    print(plot_rmse_levels)
    plot_polar_bias(pleads,plevels,pme,plot_bias_output_file,plot_bias_title,plot_bias_levels)
    plot_polar_rmse(pleads,plevels,prmse,plot_rmse_output_file,plot_rmse_title,plot_rmse_levels)


if __name__ == '__main__':
    main()
