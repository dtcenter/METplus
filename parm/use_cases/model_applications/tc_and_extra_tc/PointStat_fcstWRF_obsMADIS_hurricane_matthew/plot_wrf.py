#! /usr/bin/env python3

"""
plot_wrf.py

Written by: Jared A. Lee (jaredlee@ucar.edu)
Written on: 13 May 2024
"""

import sys
import argparse
import pathlib
import datetime as dt
import numpy as np
import pandas as pd
import netCDF4
import wrf
import matplotlib as mpl

# Import functions from a local file
import map_funcs

# def main(init_dt_first, init_dt_last, init_stride_h, plot_beg_lead_time, plot_end_lead_time, plot_stride, domain, exp_name):
def main(script_config_opts):
    # ==============
    # USER SETTINGS:
    # ==============

    # Default plot type selection
    plot_type = 'png'
    # plot_maps = True        # Plot 2D maps
    plot_subdomain = False  # Plot specified subdomain to zoom in on a defined area of interest
    plot_stations = True     # Plot station markers & labels on the map (e.g., cities of interest)

    # Which variables should be plotted?
    plot_TERRAIN = True     # terrain height [m]
    plot_T2 = True          # 2-m temperature [C]
    plot_RH2 = True         # 2-m relative humidity [%]
    plot_SLP = True         # sea level pressure [hPa] (NOTE: this requires several other variables in the wrfout file)
    plot_WS10 = True        # 10-m wind speed [m s-1]
    plot_REFL = True        # simulated radar reflectivity [dBZ]
    plot_RAIN = True        # total accumulated rainfall during the simulation [mm]
    plot_WS100 = True       # 100-m wind speed [m s-1]
    plot_GHT500 = True      # 500-hPa geopotential height [m]

    # Plot any overlays, like wind barbs?
    plot_wind_barbs_sfc = True  # overlay 10-m wind barbs for selected plots
    plot_wind_barbs_upr = True  # overlay upper-air wind barbs for selected plots

    # Default water color (generally use only in terrain plots)
    water_color = 'lightblue'

    # Set some other plot options
    suptitle_y = 1.00
    plot_fontsize = 13
    barb_thin = 10
    barb_width = 0.5

    # Set some text labels for demonstration
    if plot_stations:
        text1_lab = ['Miami', 'Jacksonville', 'Charleston']
        mark1_lat = np.asarray([25.7617, 30.3322, 32.7833])
        mark1_lon = np.asarray([-80.1918, -81.6557, -79.9320])
        text1_lat = np.asarray(mark1_lat) + np.asarray([-0.20, -0.20, -0.40])
        text1_lon = np.asarray(mark1_lon) + np.asarray([1.50, 3.00, 2.70])
        mark1_size = 36
        mark1_color = 'black'

    # Domain plotting ranges in (i,j) space (whole domain by default)
    i_beg, i_end = 0, -1
    j_beg, j_end = 0, -1
    # TODO: Implement subdomain plotting
    if plot_subdomain:
        # Adjust these if you want a different subdomain
        i_beg, i_end = 10, 81
        j_beg, j_end = 10, 90

    lat_labels = [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
    lon_labels = [-62, -64, -66, -68, -70, -72, -74, -76, -78, -80, -82, -84, -86, -88]

    # Set map contour plot limits
    min_terrain = 0.0
    max_terrain = 1500.1
    int_terrain = 100.0

    min_slp = 980.0
    max_slp = 1020.1
    int_slp = 2.0

    min_t2 = 0.0
    max_t2 = 40.1
    int_t2 = 2.0

    min_rh2 = 0.0
    max_rh2 = 100.1
    int_rh2 = 5.0

    min_ws10 = 0.0
    max_ws10 = 35.0
    int_ws10 = 2.5

    min_rain = 0.0
    max_rain = 100.1
    int_rain = 5.0

    # =======================================
    # CONSTANTS, FORMAT STATEMENTS, AND MORE:
    # =======================================

    G = 9.81  # graviational acceleration [m s-2]
    PI = 3.1415926
    DEG2RAD = PI / 180.0
    RAD2DEG = 180.0 / PI
    Rd = 297.048  # specific gas constant for dry air [J kg-1 K-1]
    Rv = 461.495  # specific gas constant for water vapor [J kg-1 K-1]
    C_to_K = 273.15  # additive conversion between degrees Celsius and Kelvin

    missing_val = -9999.0

    mpl_Wm2 = 'W $\mathregular{m^{-2}}$'
    mpl_ms1 = 'm $\mathregular{s^{-1}}$'
    mpl_s1 = '$\mathregular{s^{-1}}$'
    mpl_Jkg = 'J $\mathregular{kg^{-1}}$'
    mpl_um = u'\u03bcm'
    mpl_gkg1 = 'g $\mathregular{kg^{-1}}$'
    mpl_kgkg1 = 'kg $\mathregular{kg^{-1}}$'
    mpl_gm2s1 = 'g $\mathregular{m^{-2}}$ $\mathregular{s^{-1}}$'
    mpl_kgm2s1 = 'kg $\mathregular{m^{-2}} $\mathregular{s^{-1}}$'
    mpl_kgm2 = 'kg $\mathregular{m^{-2}}$'
    mpl_10m3 = '$\mathregular{10^{-3}}$'
    mpl_10m4 = '$\mathregular{10^{-4}}$'
    mpl_10m5 = '$\mathregular{10^{-5}}$'
    mpl_10m6 = '$\mathregular{10^{-6}}$'

    deg_uni = '\u00B0'
    en_dash = u'\u2013'
    em_dash = u'\u2014'

    fmt_yyyymmdd = '%Y%m%d'
    fmt_yyyymmddhh = '%Y%m%d%H'
    fmt_yyyymmdd_hh = '%Y%m%d_%H'
    fmt_yyyymmdd_hhmm = '%Y%m%d_%H%M'
    fmt_dt = '%Y%m%dT%H%M%S'
    fmt_yyyy = '%Y'
    fmt_mm = '%m'
    fmt_dd = '%d'
    fmt_hh = '%H'
    fmt_nn = '%M'

    fmt_wrf_dt_no_s = '%Y-%m-%d_%H:%M'
    fmt_wrf_date = '%Y-%m-%d'
    fmt_wrf_time = '%H:%M:%S'
    fmt_wrf_dt = fmt_wrf_date + '_' + fmt_wrf_time
    fmt_time_file = fmt_yyyymmdd_hhmm
    fmt_time_plot = '%d %b %Y/%H%M UTC'

    # Define a custom colormap for radar reflectivity plots
    # Modified to add gray for 0–5 dBZ and lightpurple for 75+ dBZ
    cmap_radar = np.array([
        [200, 200, 200], [4, 233, 231], [1, 159, 244], [3, 0, 244],
        [2, 253, 2], [1, 197, 1], [0, 142, 0],
        [253, 248, 2], [229, 188, 0], [253, 149, 0],
        [253, 0, 0], [212, 0, 0], [188, 0, 0],
        [248, 0, 253], [152, 84, 198], [228, 199, 243]], np.float32) / 255.0
    bounds_radar = np.arange(0., 75.01, 5.0)
    # Color names are approximate and only intended for assistance deciphering the RGB table above
    colors_radar = np.array([
        'gray', 'cyan', 'lightblue', 'darkblue',
        'lightgreen', 'green', 'darkgreen',
        'yellow', 'lightorange', 'orange',
        'red', 'darkred', 'brickred',
        'fuschia', 'violet', 'lavender'])

    read_zlev = False
    read_plev = False
    if plot_WS100:
        read_zlev = True
    if plot_GHT500:
        read_plev = True

    # =============
    # MAIN PROGRAM:
    # =============

    cycle_dt_str_first = script_config_opts['cycle_dt_first']
    cycle_dt_str_last = script_config_opts['cycle_dt_last']
    cycle_stride_h = script_config_opts['cycle_stride_h']
    cycle_dt_first = pd.to_datetime(cycle_dt_str_first, format=fmt_yyyymmdd_hh)
    cycle_dt_last = pd.to_datetime(cycle_dt_str_last, format=fmt_yyyymmdd_hh)
    cycle_dt_all = pd.date_range(start=cycle_dt_first, end=cycle_dt_last, freq=str(cycle_stride_h) + 'h')
    n_cycles = len(cycle_dt_all)

    dom_num = script_config_opts['domain']
    wrf_dom = 'd0' + dom_num

    # Loop over forecast cycles/initializations
    for cc in range(n_cycles):
        cycle_dt = cycle_dt_all[cc]
        cycle_dt_str = cycle_dt.strftime(fmt_yyyymmdd_hh)
        cycle_dt_plot = cycle_dt.strftime(fmt_time_plot)
        start_time_plot = 'Start: ' + cycle_dt_plot
        wrf_dir = script_config_opts['wrf_dir_parent'].joinpath(cycle_dt_str)
        out_dir = script_config_opts['out_dir_parent'].joinpath(cycle_dt_str, 'plots')

        # Build an array of the valid datetimes that need to be read and plotted
        beg_lead_h = int(script_config_opts['beg_lead_time'].split(':')[0])
        beg_lead_m = int(script_config_opts['beg_lead_time'].split(':')[1])
        end_lead_h = int(script_config_opts['end_lead_time'].split(':')[0])
        end_lead_m = int(script_config_opts['end_lead_time'].split(':')[1])
        valid_dt_beg = cycle_dt + dt.timedelta(hours=beg_lead_h, minutes=beg_lead_m)
        valid_dt_end = cycle_dt + dt.timedelta(hours=end_lead_h, minutes=end_lead_m)
        valid_dt_all = pd.date_range(start=valid_dt_beg, end=valid_dt_end,
                                     freq=str(script_config_opts['str_lead_time']) + 'min')
        n_valid = len(valid_dt_all)

        # Loop over valid times (this assumes one output time per file)
        for vv in range(n_valid):
            valid_dt = valid_dt_all[vv]
            valid_dt_wrf = valid_dt.strftime(fmt_wrf_dt)
            valid_dt_plot = valid_dt.strftime(fmt_time_plot)
            valid_dt_file = valid_dt.strftime(fmt_time_file)
            valid_time_plot = 'Valid: '+valid_dt_plot

            # suptitle = 'Hurricane Matthew ' + em_dash + ' Domain ' + dom_num
            suptitle = 'Hurricane Matthew Test Case'
            map_prefix = 'map_wrf_' + wrf_dom + '_'
            map_suffix = '_' + valid_dt_file + '.' + plot_type
            title_r = start_time_plot + '\n' + valid_time_plot
            title_r_no_valid = start_time_plot
            title_r_blank = ''

            wrf_fname = wrf_dir.joinpath('wrfout_' + wrf_dom + '_' + valid_dt_wrf)
            wrf_fname_zlev = wrf_dir.joinpath('wrfout_zlev_' + wrf_dom + '_' + valid_dt_wrf)
            wrf_fname_plev = wrf_dir.joinpath('wrfout_plev_' + wrf_dom + '_' + valid_dt_wrf)

            try:
                wrf_fname.is_file()
            except FileNotFoundError:
                print('WARNING: File '+str(wrf_fname) + 'does not exist. Continuing to the next valid time.')
                continue
            print('Reading ' + str(wrf_fname))
            # Use NetCDF4-python to open a Dataset, as wrf-python doesn't yet take an xarray Dataset
            # wrf.getvar will return an xarray Dataset by default, though
            ds_wrf_nc = netCDF4.Dataset(wrf_fname, mode='r')

            # Static fields only need to be read in once
            if cc == 0 and vv == 0:
                # Latitude, Longitude
                da_lat = wrf.getvar(ds_wrf_nc, 'lat', squeeze=False)
                da_lon = wrf.getvar(ds_wrf_nc, 'lon', squeeze=False)
                wrf_lat = da_lat.values[0, :, :]
                wrf_lon = da_lon.values[0, :, :]
                n_wrf_lat = wrf_lat.shape[0]
                n_wrf_lon = wrf_lon.shape[1]
                n_wrf_lev = int(getattr(ds_wrf_nc, 'BOTTOM-TOP_GRID_DIMENSION'))
                wrf_lats, wrf_lons = wrf.latlon_coords(da_lat)

                print('Getting cartopy mapping objects')
                cart_proj = wrf.get_cartopy(wrfin=ds_wrf_nc)
                cart_bounds = wrf.geo_bounds(var=da_lat[0, j_beg:j_end, i_beg:i_end])
                cart_xlim = wrf.cartopy_xlim(wrfin=ds_wrf_nc, geobounds=cart_bounds)
                cart_ylim = wrf.cartopy_ylim(wrfin=ds_wrf_nc, geobounds=cart_bounds)
                borders, states, oceans, lakes, rivers, land = map_funcs.get_cartopy_features()

                # Start populating dictionary for map plotting options. Update later with other options.
                map_opts = {
                    'cart_proj': cart_proj, 'cart_xlim': cart_xlim, 'cart_ylim': cart_ylim,
                    'borders': borders, 'states': states, 'oceans': oceans, 'lakes': lakes,
                    'lons': wrf_lons, 'lats': wrf_lats, 'suptitle': suptitle, 'suptitle_y': suptitle_y,
                    'lat_labels': lat_labels, 'lon_labels': lon_labels, 'fontsize': plot_fontsize,
                    'map_x_thin': barb_thin, 'map_y_thin': barb_thin, 'barb_width': barb_width,
                }

                if plot_stations:
                    map_opts['mark1_lat'] = mark1_lat
                    map_opts['mark1_lon'] = mark1_lon
                    map_opts['text1_lab'] = text1_lab
                    map_opts['text1_lat'] = text1_lat
                    map_opts['text1_lon'] = text1_lon
                    map_opts['mark1_size'] = mark1_size
                    map_opts['mark1_color'] = mark1_color

                # Terrain
                if plot_TERRAIN:
                    print('   Reading terrain')
                    da_terrain = wrf.getvar(ds_wrf_nc, 'ter', squeeze=False)
                    wrf_terrain = da_terrain.values[0, :, :]

                    var_file = 'TERRAIN'
                    var_name = 'Terrain Height'
                    var_unit = 'm'
                    wrf_var = wrf_terrain
                    min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                    max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                    extend = 'both'
                    cmap = map_funcs.truncate_cmap(mpl.cm.terrain, minval=0.20, maxval=0.95)
                    bounds = np.arange(min_terrain, max_terrain, int_terrain)
                    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                    map_opts['fill_var'] = wrf_var
                    map_opts['water_color'] = water_color
                    map_opts['extend'] = extend
                    map_opts['cmap'] = cmap
                    map_opts['bounds'] = bounds
                    map_opts['norm'] = norm
                    map_opts['cbar_lab'] = 'Model ' + var_name + ' [' + var_unit + ']'
                    map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + '.' + plot_type)
                    map_opts['title_l'] = title_l
                    map_opts['title_r'] = title_r_blank
                    map_funcs.map_plot(map_opts)

            # Make the water color transparent for all subsequent plots
            map_opts['water_color'] = 'none'
            map_opts['title_r'] = title_r

            if plot_wind_barbs_sfc or plot_WS10:
                print('   Reading 10-m wind components (rotated to earth-relative)')
                da_uv10 = wrf.getvar(ds_wrf_nc, 'uvmet10', squeeze=False)
                wrf_u10 = da_uv10.values[0, 0, :, :]
                wrf_v10 = da_uv10.values[1, 0, :, :]
                wrf_ws10 = np.sqrt(wrf_u10**2 + wrf_v10**2)

                if plot_WS10:
                    var_file = 'WS10'
                    var_name = '10-m Wind Speed'
                    var_unit = mpl_ms1
                    wrf_var = wrf_ws10
                    min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                    max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                    extend = 'max'
                    cmap = mpl.cm.BuGn
                    bounds = np.arange(min_ws10, max_ws10, int_ws10)
                    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                    map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                    if plot_wind_barbs_sfc:
                        var_file = var_file + '+barbs'
                        # var_name = var_name + '; Barbs'
                        map_opts['u'] = wrf_u10
                        map_opts['v'] = wrf_v10
                    else:
                        map_opts['u'] = None
                        map_opts['v'] = None
                    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                    map_opts['fill_var'] = wrf_var
                    map_opts['extend'] = extend
                    map_opts['cmap'] = cmap
                    map_opts['bounds'] = bounds
                    map_opts['norm'] = norm
                    map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                    map_opts['title_l'] = title_l
                    map_funcs.map_plot(map_opts)

            # Sea level pressuure
            if plot_SLP:
                print('   Reading sea level pressure')
                da_slp = wrf.getvar(ds_wrf_nc, 'slp', squeeze=False)
                wrf_slp = da_slp.values[0, :, :]

                var_file = 'SLP'
                var_name = 'Sea-Level Pressure'
                var_unit = 'hPa'
                wrf_var = wrf_slp
                min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                extend = 'both'
                cmap = mpl.cm.viridis
                bounds = np.arange(min_slp, max_slp, int_slp)
                norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                if plot_wind_barbs_sfc:
                    var_file = var_file + '+barbs'
                    # var_name = var_name + '; 10-m Barbs'
                    map_opts['u'] = wrf_u10
                    map_opts['v'] = wrf_v10
                else:
                    map_opts['u'] = None
                    map_opts['v'] = None
                title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                map_opts['fill_var'] = wrf_var
                map_opts['extend'] = extend
                map_opts['cmap'] = cmap
                map_opts['bounds'] = bounds
                map_opts['norm'] = norm
                map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                map_opts['title_l'] = title_l
                map_funcs.map_plot(map_opts)

            # 2-m air temperature
            if plot_T2:
                print('   Reading 2-m air temperature')
                da_t2 = wrf.getvar(ds_wrf_nc, 'T2', squeeze=False)
                if da_t2.attrs['units'] == 'K':
                    da_t2 = da_t2 - C_to_K
                    da_t2.attrs['units'] = 'degC'
                wrf_t2 = da_t2.values[0, :, :]

                var_file = 'T2'
                var_name = '2-m Air Temperature'
                var_unit = deg_uni + 'C'
                wrf_var = wrf_t2
                min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                extend = 'both'
                cmap = mpl.cm.rainbow
                bounds = np.arange(min_t2, max_t2, int_t2)
                norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                if plot_wind_barbs_sfc:
                    var_file = var_file + '+barbs'
                    # var_name = var_name + '; 10-m Barbs'
                    map_opts['u'] = wrf_u10
                    map_opts['v'] = wrf_v10
                else:
                    map_opts['u'] = None
                    map_opts['v'] = None
                title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                map_opts['fill_var'] = wrf_var
                map_opts['extend'] = extend
                map_opts['cmap'] = cmap
                map_opts['bounds'] = bounds
                map_opts['norm'] = norm
                map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                map_opts['title_l'] = title_l
                map_funcs.map_plot(map_opts)

            # 2-m relative humidity
            if plot_RH2:
                print('   Reading 2-m relative humidity')
                da_rh2 = wrf.getvar(ds_wrf_nc, 'rh2', squeeze=False)
                wrf_rh2 = da_rh2.values[0, :, :]

                var_file = 'RH2'
                var_name = '2-m Relative Humidity'
                var_unit = '%'
                wrf_var = wrf_rh2
                min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                extend = 'max'
                cmap = mpl.cm.YlGnBu
                bounds = np.arange(min_rh2, max_rh2, int_rh2)
                norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                if plot_wind_barbs_sfc:
                    var_file = var_file + '+barbs'
                    # var_name = var_name + '; 10-m Barbs'
                    map_opts['u'] = wrf_u10
                    map_opts['v'] = wrf_v10
                else:
                    map_opts['u'] = None
                    map_opts['v'] = None
                title_l = var_name + f'\nMin: {min_val:.1f}' + var_unit + f', Max: {max_val:.1f}' + var_unit
                map_opts['fill_var'] = wrf_var
                map_opts['extend'] = extend
                map_opts['cmap'] = cmap
                map_opts['bounds'] = bounds
                map_opts['norm'] = norm
                map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                map_opts['title_l'] = title_l
                map_funcs.map_plot(map_opts)

            # Accumulated rainfall
            if plot_RAIN and vv > 0:
                print('   Reading accumulated rainfall')
                da_rainc = wrf.getvar(ds_wrf_nc, 'RAINC', squeeze=False)
                da_rainnc = wrf.getvar(ds_wrf_nc, 'RAINNC', squeeze=False)
                wrf_rain = da_rainc.values[0, :, :] + da_rainnc.values[0, :, :]
                # Mask RAIN=0.0 for plotting
                wrf_rain_plot = np.ma.masked_equal(np.where(wrf_rain == 0.0, missing_val, wrf_rain), missing_val)

                var_file = 'RAIN'
                var_name = 'Accumulated Precipitation'
                var_unit = 'mm'
                wrf_var1 = wrf_rain
                wrf_var2 = wrf_rain_plot
                min_val = np.nanmin(wrf_var1[j_beg:j_end, i_beg:i_end])
                max_val = np.nanmax(wrf_var1[j_beg:j_end, i_beg:i_end])
                extend = 'max'
                cmap = mpl.cm.GnBu
                bounds = np.arange(min_rain, max_rain, int_rain)
                norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                map_opts['fill_var'] = wrf_var2
                map_opts['extend'] = extend
                map_opts['cmap'] = cmap
                map_opts['bounds'] = bounds
                map_opts['norm'] = norm
                map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                map_opts['title_l'] = title_l
                # print(wrf_var1.shape)
                # print(wrf_var2.shape)
                map_funcs.map_plot(map_opts)

            # Radar reflectivity
            if plot_REFL and vv > 0:
                print('   Reading radar reflectivity')
                da_refl = wrf.getvar(ds_wrf_nc, 'dbz', squeeze=False)
                wrf_refl = da_refl.values[0, 0, :, :]
                # Mask REFL <= 0.0 for plotting
                wrf_refl_plot = np.ma.masked_equal(np.where(wrf_refl <= 0.0, missing_val, wrf_refl), missing_val)

                var_file = 'REFL'
                var_name = 'Radar Reflectivity'
                var_unit = 'dBZ'
                wrf_var1 = wrf_refl
                wrf_var2 = wrf_refl_plot
                min_val = np.nanmin(wrf_var1[j_beg:j_end, i_beg:i_end])
                max_val = np.nanmax(wrf_var1[j_beg:j_end, i_beg:i_end])
                extend = 'max'
                refl_rgb = cmap_radar
                bounds = bounds_radar
                cmap, norm = mpl.colors.from_levels_and_colors(bounds, refl_rgb, extend=extend)
                map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                if plot_wind_barbs_sfc:
                    var_file = var_file + '+barbs'
                    var_name = var_name + '; 10-m Barbs'
                    map_opts['u'] = wrf_u10
                    map_opts['v'] = wrf_v10
                else:
                    map_opts['u'] = None
                    map_opts['v'] = None
                title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                map_opts['fill_var'] = wrf_var2
                map_opts['extend'] = extend
                map_opts['cmap'] = cmap
                map_opts['bounds'] = bounds
                map_opts['norm'] = norm
                map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                map_opts['title_l'] = title_l
                # print(wrf_var1.shape)
                # print(wrf_var2.shape)
                map_funcs.map_plot(map_opts)

            if read_zlev:
                try:
                    wrf_fname_zlev.is_file()
                except FileNotFoundError:
                    print('WARNING: File ' + str(wrf_fname_zlev) + 'does not exist. Continuing to the next valid time.')
                    continue
                print('Reading ' + str(wrf_fname_zlev))
                # Use NetCDF4-python to open a Dataset, as wrf-python doesn't yet take an xarray Dataset
                # wrf.getvar will return an xarray Dataset by default, though
                ds_wrf_zlev_nc = netCDF4.Dataset(wrf_fname_zlev, mode='r')
                wrf_z_zlev = wrf.getvar(ds_wrf_zlev_nc, 'Z_ZL', squeeze=False)

                # 100-m wind speed
                if plot_WS100:
                    ind_z = np.where(wrf_z_zlev == -100)[0][0]
                    wrf_ws100 = wrf.getvar(ds_wrf_zlev_nc, 'S_ZL', squeeze=False)[0, ind_z, :, :]

                    var_file = 'WS100'
                    var_name = '100-m Wind Speed'
                    var_unit = mpl_ms1
                    wrf_var = wrf_ws100
                    min_val = np.nanmin(wrf_var[j_beg:j_end, i_beg:i_end])
                    max_val = np.nanmax(wrf_var[j_beg:j_end, i_beg:i_end])
                    extend = 'max'
                    cmap = mpl.cm.BuGn
                    bounds = np.arange(min_ws10, max_ws10, int_ws10)
                    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)
                    map_opts['cbar_lab'] = var_name + ' [' + var_unit + ']'
                    if plot_wind_barbs_upr:
                        var_file = var_file + '+barbs'
                        var_name = var_name + '; Barbs'
                        wrf_u100 = wrf.getvar(ds_wrf_zlev_nc, 'U_ZL', squeeze=False).values[0, ind_z, :, :]
                        wrf_v100 = wrf.getvar(ds_wrf_zlev_nc, 'V_ZL', squeeze=False).values[0, ind_z, :, :]
                        map_opts['u'] = wrf_u100
                        map_opts['v'] = wrf_v100
                    else:
                        map_opts['u'] = None
                        map_opts['v'] = None
                    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit
                    map_opts['fill_var'] = wrf_var
                    map_opts['extend'] = extend
                    map_opts['cmap'] = cmap
                    map_opts['bounds'] = bounds
                    map_opts['norm'] = norm
                    map_opts['fname'] = out_dir.joinpath(map_prefix + var_file + map_suffix)
                    map_opts['title_l'] = title_l
                    map_funcs.map_plot(map_opts)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wrf_dir_parent', default='/data/input/wrf',
                        help='string specifying the directory path to the parent WRF output directories, '
                             'above any experiment or cycle datetime subdirectories (default: /data/input/wrf)')
    parser.add_argument('-o', '--out_dir_parent', default='/data/output/wrf',
                        help='string specifying the directory path to the parent plot directories (default: /data/output/wrf)')
    parser.add_argument('-f', '--cycle_dt_first', default='20161006_00',
                        help='beginning date/time of first WRF simulation [YYYYMMDD_HH] (default: 20161006_00)')
    parser.add_argument('-l', '--cycle_dt_last', default=None,
                        help='beginning date/time of last WRF simulation [YYYYMMDD_HH]')
    parser.add_argument('-i', '--cycle_stride_h', default=24, type=int,
                        help='stride in hours between cycles (default: 24)')
    parser.add_argument('-b', '--beg_lead_time', default='00:00',
                        help='beginning lead time for plotting WRF simulations [HH:MM] (default: 00:00)')
    parser.add_argument('-e', '--end_lead_time', default='48:00',
                        help='ending lead time for plotting WRF simulations [HH:MM] (default: 48:00)')
    parser.add_argument('-s', '--str_lead_time', default=180, type=int,
                        help='stride to create plots every N minutes (default: 180)')
    parser.add_argument('-d', '--domain', default='1', help='WRF domain number to be plotted (default: 1)')
    # parser.add_argument('-x', '--exp_name', default=None,
    #                     help='WRF experiment name(s), if applicable. If requesting plots for multiple experiments, '
    #                          'separate them by commas (e.g., exp01,exp02).')

    args = parser.parse_args()
    wrf_dir_parent = args.wrf_dir_parent
    out_dir_parent = args.out_dir_parent
    cycle_dt_first = args.cycle_dt_first
    cycle_dt_last = args.cycle_dt_last
    cycle_stride_h = args.cycle_stride_h
    beg_lead_time = args.beg_lead_time
    end_lead_time = args.end_lead_time
    str_lead_time = args.str_lead_time
    domain = args.domain
    # exp_names_inp = args.exp_name

    # if exp_names_inp is None:
    #     exp_name = None
    # else:
    #     exp_name = exp_names_inp.split(',')

    if out_dir_parent is None:
        out_dir_parent = wrf_dir_parent

    # Make both paths into pathlib objects
    wrf_dir_parent = pathlib.Path(wrf_dir_parent)
    out_dir_parent = pathlib.Path(out_dir_parent)

    if len(cycle_dt_first) != 11:
        print('ERROR! Incorrect length for positional argument init_dt_first. Exiting!')
        parser.print_help()
        sys.exit()
    elif cycle_dt_first[8] != '_':
        print('ERROR! Incorrect format for positional argument init_dt_first. Exiting!')
        parser.print_help()
        sys.exit()

    if cycle_dt_last != None:
        if len(cycle_dt_last) != 11:
            print('ERROR! Incorrect length for positional argument init_dt_last. Exiting!')
            parser.print_help()
            sys.exit()
        elif cycle_dt_last[8] != '_':
            print('ERROR! Incorrect format for positional argument init_dt_last. Exiting!')
            parser.print_help()
            sys.exit()
    else:
        cycle_dt_last = cycle_dt_first

    if len(beg_lead_time) != 5:
        print('ERROR! Incorrect length for optional argument -b (beg_lead_time). Exiting!')
        parser.print_help()
        sys.exit()
    elif beg_lead_time[2] != ':':
        print('ERROR! Incorrect format for optional argument -b (beg_lead_time). Exiting!')
        parser.print_help()
        sys.exit()

    if len(end_lead_time) != 5:
        print('ERROR! Incorrect length for optional argument -e (end_lead_time). Exiting!')
        parser.print_help()
        sys.exit()
    elif end_lead_time[2] != ':':
        print('ERROR! Incorrect format for optional argument -e (end_lead_time). Exiting!')
        parser.print_help()
        sys.exit()

    # Put all these configuration options into a dictionary, to make further development or customization easier
    script_config_opts = {
        'wrf_dir_parent': wrf_dir_parent,
        'out_dir_parent': out_dir_parent,
        'cycle_dt_first': cycle_dt_first,
        'cycle_dt_last': cycle_dt_last,
        'cycle_stride_h': cycle_stride_h,
        'beg_lead_time': beg_lead_time,
        'end_lead_time': end_lead_time,
        'str_lead_time': str_lead_time,
        'domain': domain,
        # 'exp_name': exp_name,
    }

    return script_config_opts
    # return init_dt_first, init_dt_last, init_stride_h, beg_lead_time, end_lead_time, plot_stride, domain, exp_name

if __name__ == '__main__':
    now_time_beg = dt.datetime.utcnow()
    # init_dt_first, init_dt_last, init_stride_h, plot_beg_lead_time, plot_end_lead_time, plot_stride, domain, exp_name = parse_args()
    # main(init_dt_first, init_dt_last, init_stride_h, plot_beg_lead_time, plot_end_lead_time, plot_stride, domain, exp_name)
    script_config_opts = parse_args()
    main(script_config_opts)
    now_time_end = dt.datetime.utcnow()
    run_time_tot = now_time_end - now_time_beg
    now_time_beg_str = now_time_beg.strftime('%Y-%m-%d %H:%M:%S')
    now_time_end_str = now_time_end.strftime('%Y-%m-%d %H:%M:%S')
    print('\nScript completed successfully.')
    print('   Beg time: '+now_time_beg_str)
    print('   End time: '+now_time_end_str)
    print('   Run time: '+str(run_time_tot)+'\n')
