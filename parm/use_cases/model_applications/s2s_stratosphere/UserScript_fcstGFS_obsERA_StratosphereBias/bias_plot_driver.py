#!/usr/bin/env python3

"""
Creates a bias plot
"""
import os
import METreadnc.util.read_netcdf as read_netcdf
from metplotpy.contributed.stratosphere_diagnostics.stratosphere_plots import plot_zonal_bias


def main():
    """
    Read METplus environment variables
    """
    print('Reading Input Environment Variables')
    infile_u = [os.environ['PLOT_U_INPUT_FILE']]
    invar_u = os.environ['PLOT_U_BIAS_VAR']
    omvar_u = os.environ['PLOT_U_OBAR_VAR']
    plot_levels_u_str = os.environ['PLOT_U_LEVELS'].split(',')
    plot_levels_u = [int(pp) for pp in plot_levels_u_str]
    plot_title_u = os.environ['PLOT_U_TITLE']
    output_dir_u = os.environ['PLOT_U_OUTPUT_DIR']
    output_file_u = os.environ.get('PLOT_U_OUTPUT_FILE','bias_plot.png')
    plot_output_file_u = os.path.join(output_dir_u,output_file_u)

    infile_t = [os.environ['PLOT_T_INPUT_FILE']]
    invar_t = os.environ['PLOT_T_BIAS_VAR']
    omvar_t = os.environ['PLOT_T_OBAR_VAR']
    plot_levels_t_str = os.environ['PLOT_T_LEVELS'].split(',')
    plot_levels_t = [int(pp) for pp in plot_levels_t_str]
    plot_title_t = os.environ['PLOT_T_TITLE']
    output_dir_t = os.environ['PLOT_T_OUTPUT_DIR']
    output_file_t = os.environ.get('PLOT_T_OUTPUT_FILE','bias_plot.png')
    plot_output_file_t = os.path.join(output_dir_t,output_file_t)

    """
    Make plot output directory if it doesn't exist
    """
    if not os.path.exists(output_dir_u):
        os.makedirs(output_dir_u)

    if not os.path.exists(output_dir_t):
        os.makedirs(output_dir_t)

    """
    Read dataset
    """
    print('Reading Zonal Mean U Bias File: '+infile_u[0])
    file_reader_u = read_netcdf.ReadNetCDF()
    dsu = file_reader_u.read_into_xarray(infile_u)[0]
    bias_u = dsu[invar_u].values
    lats_u = dsu['lat'].values
    obar_u = dsu[omvar_u].values
    levels_u = dsu['level'].values

    print('Reading Zonal Mean T Bias File: '+infile_t[0])
    file_reader_t = read_netcdf.ReadNetCDF()
    dst = file_reader_t.read_into_xarray(infile_t)[0]
    bias_t = dst[invar_t].values
    lats_t = dst['lat'].values
    obar_t = dst[omvar_t].values
    levels_t = dst['level'].values

    """
    Create Bias Plots
    """
    print('Plotting Zonal Mean U Bias')
    plot_zonal_bias(lats_u,levels_u,bias_u,obar_u,plot_output_file_u,plot_title_u,plot_levels_u)
    print('Plotting Zonal Mean T Bias')
    plot_zonal_bias(lats_t,levels_t,bias_t,obar_t,plot_output_file_t,plot_title_t,plot_levels_t)


if __name__ == '__main__':
    main()
