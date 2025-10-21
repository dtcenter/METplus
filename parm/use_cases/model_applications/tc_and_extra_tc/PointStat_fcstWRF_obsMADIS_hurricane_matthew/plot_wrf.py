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

ADD_BARBS_STRING = '+barbs'


def setup_plot_configuration():
    """Set up default plotting configuration and options."""
    return {
        'plot_type': 'png',
        'plot_subdomain': False,
        'plot_stations': True,
        'plot_terrain': True,
        'plot_t2': True,
        'plot_rh2': True,
        'plot_slp': True,
        'plot_ws10': True,
        'plot_refl': True,
        'plot_rain': True,
        'plot_ws100': True,
        'plot_wind_barbs_sfc': True,
        'plot_wind_barbs_upr': True,
        'water_color': 'lightblue',
        'suptitle_y': 1.00,
        'plot_fontsize': 13,
        'barb_thin': 10,
        'barb_width': 0.5,
        # Domain plotting ranges
        'i_beg': 0, 'i_end': -1,
        'j_beg': 0, 'j_end': -1,
        # Station data
        'text1_lab': ['Miami', 'Jacksonville', 'Charleston'],
        'mark1_lat': np.array([25.7617, 30.3322, 32.7833]),
        'mark1_lon': np.array([-80.1918, -81.6557, -79.9320]),
        'mark1_size': 36,
        'mark1_color': 'black',
        'lat_labels': [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40],
        'lon_labels': [-62, -64, -66, -68, -70, -72, -74, -76, -78, -80, -82, -84, -86, -88],
    }


def setup_plot_limits():
    """Set up plotting limits and contour intervals for all variables."""
    return {
        'terrain': {'min': 0.0, 'max': 1500.1, 'int': 100.0},
        'slp': {'min': 980.0, 'max': 1020.1, 'int': 2.0},
        't2': {'min': 0.0, 'max': 40.1, 'int': 2.0},
        'rh2': {'min': 0.0, 'max': 100.1, 'int': 5.0},
        'ws10': {'min': 0.0, 'max': 35.0, 'int': 2.5},
        'rain': {'min': 0.0, 'max': 100.1, 'int': 5.0},
    }


def setup_constants_and_formats():
    """Define constants, format strings, and other static values."""
    constants = {
        'c_to_k': 273.15,
        'missing_val': -9999.0,
        'mpl_ms1': r'm $\mathregular{s^{-1}}$',
        'deg_uni': '\u00B0',
    }

    formats = {
        'fmt_yyyymmdd_hh': '%Y%m%d_%H',
        'fmt_yyyymmdd_hhmm': '%Y%m%d_%H%M',
        'fmt_wrf_date': '%Y-%m-%d',
        'fmt_wrf_time': '%H:%M:%S',
        'fmt_time_plot': '%d %b %Y/%H%M UTC',
    }
    formats['fmt_wrf_dt'] = formats['fmt_wrf_date'] + '_' + formats['fmt_wrf_time']
    formats['fmt_time_file'] = formats['fmt_yyyymmdd_hhmm']

    # Define custom colormap for radar reflectivity
    cmap_radar = np.array([
        [200, 200, 200], [4, 233, 231], [1, 159, 244], [3, 0, 244],
        [2, 253, 2], [1, 197, 1], [0, 142, 0],
        [253, 248, 2], [229, 188, 0], [253, 149, 0],
        [253, 0, 0], [212, 0, 0], [188, 0, 0],
        [248, 0, 253], [152, 84, 198], [228, 199, 243]], np.float32) / 255.0
    bounds_radar = np.arange(0., 75.01, 5.0)

    return constants, formats, {'cmap_radar': cmap_radar, 'bounds_radar': bounds_radar}


def adjust_subdomain_ranges(config):
    """Adjust domain ranges if subdomain plotting is requested."""
    if config['plot_subdomain']:
        config['i_beg'], config['i_end'] = 10, 81
        config['j_beg'], config['j_end'] = 10, 90


def initialize_static_fields(ds_wrf_nc, config):
    """Initialize static WRF fields and mapping objects (run once)."""
    print('Initializing static fields...')

    # Adjust subdomain if needed
    adjust_subdomain_ranges(config)

    # Read latitude and longitude
    da_lat = wrf.getvar(ds_wrf_nc, 'lat', squeeze=False)
    wrf_lats, wrf_lons = wrf.latlon_coords(da_lat)

    # Setup cartopy mapping objects
    print('Getting cartopy mapping objects')
    cart_proj = wrf.get_cartopy(wrfin=ds_wrf_nc)
    cart_bounds = wrf.geo_bounds(var=da_lat[0, config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    cart_xlim = wrf.cartopy_xlim(wrfin=ds_wrf_nc, geobounds=cart_bounds)
    cart_ylim = wrf.cartopy_ylim(wrfin=ds_wrf_nc, geobounds=cart_bounds)
    borders, states, oceans, lakes, _, _ = map_funcs.get_cartopy_features()

    # Build base map options dictionary
    map_opts = {
        'cart_proj': cart_proj, 'cart_xlim': cart_xlim, 'cart_ylim': cart_ylim,
        'borders': borders, 'states': states, 'oceans': oceans, 'lakes': lakes,
        'lons': wrf_lons, 'lats': wrf_lats, 'suptitle': 'Hurricane Matthew Test Case',
        'suptitle_y': config['suptitle_y'], 'lat_labels': config['lat_labels'],
        'lon_labels': config['lon_labels'], 'fontsize': config['plot_fontsize'],
        'map_x_thin': config['barb_thin'], 'map_y_thin': config['barb_thin'],
        'barb_width': config['barb_width'],
    }

    # Add station markers if requested
    if config['plot_stations']:
        text1_lat = config['mark1_lat'] + np.array([-0.20, -0.20, -0.40])
        text1_lon = config['mark1_lon'] + np.array([1.50, 3.00, 2.70])
        map_opts.update({
            'mark1_lat': config['mark1_lat'], 'mark1_lon': config['mark1_lon'],
            'text1_lab': config['text1_lab'], 'text1_lat': text1_lat, 'text1_lon': text1_lon,
            'mark1_size': config['mark1_size'], 'mark1_color': config['mark1_color']
        })

    return map_opts, wrf_lats, wrf_lons


def plot_terrain(ds_wrf_nc, map_opts, config, limits, out_dir):
    """Plot terrain height."""
    print('   Reading terrain')
    da_terrain = wrf.getvar(ds_wrf_nc, 'ter', squeeze=False)
    wrf_terrain = da_terrain.values[0, :, :]

    var_file = 'TERRAIN'
    var_name = 'Terrain Height'
    var_unit = 'm'

    min_val = np.nanmin(wrf_terrain[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_terrain[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'both'
    cmap = map_funcs.truncate_cmap(mpl.cm.terrain, minval=0.20, maxval=0.95)
    bounds = np.arange(limits['terrain']['min'], limits['terrain']['max'], limits['terrain']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_terrain, 'water_color': config['water_color'], 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm,
        'cbar_lab': 'Model ' + var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + '.' + config['plot_type']),
        'title_l': title_l, 'title_r': ''
    })

    map_funcs.map_plot(plot_opts)


def read_surface_winds(ds_wrf_nc):
    """Read and return 10-m wind components and speed."""
    print('   Reading 10-m wind components (rotated to earth-relative)')
    da_uv10 = wrf.getvar(ds_wrf_nc, 'uvmet10', squeeze=False)
    wrf_u10 = da_uv10.values[0, 0, :, :]
    wrf_v10 = da_uv10.values[1, 0, :, :]
    wrf_ws10 = np.sqrt(wrf_u10 ** 2 + wrf_v10 ** 2)
    return wrf_u10, wrf_v10, wrf_ws10


def plot_wind_speed_10m(wrf_u10, wrf_v10, wrf_ws10, map_opts, config, limits, constants, map_suffix, out_dir):
    """Plot 10-m wind speed with optional wind barbs."""
    var_file = 'WS10'
    var_name = '10-m Wind Speed'
    var_unit = constants['mpl_ms1']

    min_val = np.nanmin(wrf_ws10[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_ws10[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'max'
    cmap = mpl.cm.BuGn
    bounds = np.arange(limits['ws10']['min'], limits['ws10']['max'], limits['ws10']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_ws10, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def plot_sea_level_pressure(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, map_suffix, out_dir):
    """Plot sea level pressure with optional wind barbs."""
    print('   Reading sea level pressure')
    da_slp = wrf.getvar(ds_wrf_nc, 'slp', squeeze=False)
    wrf_slp = da_slp.values[0, :, :]

    var_file = 'SLP'
    var_name = 'Sea-Level Pressure'
    var_unit = 'hPa'

    min_val = np.nanmin(wrf_slp[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_slp[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'both'
    cmap = mpl.cm.viridis
    bounds = np.arange(limits['slp']['min'], limits['slp']['max'], limits['slp']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_slp, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def plot_temperature_2m(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, constants, map_suffix, out_dir):
    """Plot 2-m air temperature with optional wind barbs."""
    print('   Reading 2-m air temperature')
    da_t2 = wrf.getvar(ds_wrf_nc, 'T2', squeeze=False)
    if da_t2.attrs['units'] == 'K':
        da_t2 = da_t2 - constants['c_to_k']
        da_t2.attrs['units'] = 'degC'
    wrf_t2 = da_t2.values[0, :, :]

    var_file = 'T2'
    var_name = '2-m Air Temperature'
    var_unit = constants['deg_uni'] + 'C'

    min_val = np.nanmin(wrf_t2[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_t2[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'both'
    cmap = mpl.cm.rainbow
    bounds = np.arange(limits['t2']['min'], limits['t2']['max'], limits['t2']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_t2, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def plot_humidity_2m(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, map_suffix, out_dir):
    """Plot 2-m relative humidity with optional wind barbs."""
    print('   Reading 2-m relative humidity')
    da_rh2 = wrf.getvar(ds_wrf_nc, 'rh2', squeeze=False)
    wrf_rh2 = da_rh2.values[0, :, :]

    var_file = 'RH2'
    var_name = '2-m Relative Humidity'
    var_unit = '%'

    min_val = np.nanmin(wrf_rh2[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_rh2[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'max'
    cmap = mpl.cm.YlGnBu
    bounds = np.arange(limits['rh2']['min'], limits['rh2']['max'], limits['rh2']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING

    title_l = var_name + f'\nMin: {min_val:.1f}' + var_unit + f', Max: {max_val:.1f}' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_rh2, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def plot_precipitation(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, constants, map_suffix, out_dir):
    """Plot accumulated precipitation."""
    print('   Reading accumulated rainfall')
    da_rainc = wrf.getvar(ds_wrf_nc, 'RAINC', squeeze=False)
    da_rainnc = wrf.getvar(ds_wrf_nc, 'RAINNC', squeeze=False)
    wrf_rain = da_rainc.values[0, :, :] + da_rainnc.values[0, :, :]

    # Mask RAIN=0.0 for plotting
    wrf_rain_plot = np.ma.masked_equal(np.where(np.isclose(wrf_rain, 0.0, rtol=1e-09, atol=1e-09), constants['missing_val'], wrf_rain),
                                       constants['missing_val'])

    var_file = 'RAIN'
    var_name = 'Accumulated Precipitation'
    var_unit = 'mm'

    min_val = np.nanmin(wrf_rain[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_rain[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'max'
    cmap = mpl.cm.GnBu
    bounds = np.arange(limits['rain']['min'], limits['rain']['max'], limits['rain']['int'])
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_rain_plot, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': var_name + ' [' + var_unit + ']',
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def plot_radar_reflectivity(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, constants, radar_data, map_suffix, out_dir):
    """Plot radar reflectivity with optional wind barbs."""
    print('   Reading radar reflectivity')
    da_refl = wrf.getvar(ds_wrf_nc, 'dbz', squeeze=False)
    wrf_refl = da_refl.values[0, 0, :, :]

    # Mask REFL <= 0.0 for plotting
    wrf_refl_plot = np.ma.masked_equal(np.where(wrf_refl <= 0.0, constants['missing_val'], wrf_refl),
                                       constants['missing_val'])

    var_file = 'REFL'
    var_name = 'Radar Reflectivity'
    var_unit = 'dBZ'

    min_val = np.nanmin(wrf_refl[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
    max_val = np.nanmax(wrf_refl[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

    extend = 'max'
    refl_rgb = radar_data['cmap_radar']
    bounds = radar_data['bounds_radar']
    cmap, norm = mpl.colors.from_levels_and_colors(bounds, refl_rgb, extend=extend)

    cbar_lab = var_name + ' [' + var_unit + ']'

    # Add wind barbs if requested
    u_var, v_var = (wrf_u10, wrf_v10) if config['plot_wind_barbs_sfc'] else (None, None)
    if config['plot_wind_barbs_sfc']:
        var_file += ADD_BARBS_STRING
        var_name += '; 10-m Barbs'

    title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

    plot_opts = map_opts.copy()
    plot_opts.update({
        'fill_var': wrf_refl_plot, 'water_color': 'none', 'extend': extend,
        'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
        'cbar_lab': cbar_lab,
        'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
        'title_l': title_l, 'title_r': config['title_r']
    })

    map_funcs.map_plot(plot_opts)


def check_and_open_zlev_file(wrf_fname_zlev):
    """Check if z-level file exists and open it."""
    try:
        if not wrf_fname_zlev.is_file():
            print(f'WARNING: File {wrf_fname_zlev} does not exist. Skipping upper-level winds.')
            return None
    except FileNotFoundError:
        print(f'WARNING: File {wrf_fname_zlev} does not exist. Skipping upper-level winds.')
        return None

    print(f'Reading {wrf_fname_zlev}')
    return netCDF4.Dataset(wrf_fname_zlev, mode='r')


def plot_upper_level_winds(wrf_fname_zlev, map_opts, config, limits, constants, map_suffix, out_dir):
    """Plot 100-m wind speed from z-level file with optional wind barbs."""
    ds_wrf_zlev_nc = check_and_open_zlev_file(wrf_fname_zlev)
    if ds_wrf_zlev_nc is None:
        return

    try:
        wrf_z_zlev = wrf.getvar(ds_wrf_zlev_nc, 'Z_ZL', squeeze=False)

        # Find 100-m level
        ind_z = np.nonzero(wrf_z_zlev == -100)[0][0]
        wrf_ws100 = wrf.getvar(ds_wrf_zlev_nc, 'S_ZL', squeeze=False)[0, ind_z, :, :]

        var_file = 'WS100'
        var_name = '100-m Wind Speed'
        var_unit = constants['mpl_ms1']

        min_val = np.nanmin(wrf_ws100[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])
        max_val = np.nanmax(wrf_ws100[config['j_beg']:config['j_end'], config['i_beg']:config['i_end']])

        extend = 'max'
        cmap = mpl.cm.BuGn
        bounds = np.arange(limits['ws10']['min'], limits['ws10']['max'], limits['ws10']['int'])
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend=extend)

        # Add wind barbs if requested
        u_var, v_var = None, None
        if config['plot_wind_barbs_upr']:
            var_file += ADD_BARBS_STRING
            var_name += '; Barbs'
            wrf_u100 = wrf.getvar(ds_wrf_zlev_nc, 'U_ZL', squeeze=False).values[0, ind_z, :, :]
            wrf_v100 = wrf.getvar(ds_wrf_zlev_nc, 'V_ZL', squeeze=False).values[0, ind_z, :, :]
            u_var, v_var = wrf_u100, wrf_v100

        title_l = var_name + f'\nMin: {min_val:.1f} ' + var_unit + f', Max: {max_val:.1f} ' + var_unit

        plot_opts = map_opts.copy()
        plot_opts.update({
            'fill_var': wrf_ws100, 'water_color': 'none', 'extend': extend,
            'cmap': cmap, 'bounds': bounds, 'norm': norm, 'u': u_var, 'v': v_var,
            'cbar_lab': var_name + ' [' + var_unit + ']',
            'fname': out_dir.joinpath('map_wrf_' + config['wrf_dom'] + '_' + var_file + map_suffix),
            'title_l': title_l, 'title_r': config['title_r']
        })

        map_funcs.map_plot(plot_opts)

    finally:
        ds_wrf_zlev_nc.close()


def determine_read_zlev(config):
    """Determine if z-level file needs to be read."""
    return config['plot_ws100']


def parse_time_ranges(script_config_opts, formats):
    """Parse and build time ranges for processing."""
    cycle_dt_first = pd.to_datetime(script_config_opts['cycle_dt_first'], format=formats['fmt_yyyymmdd_hh'])
    cycle_dt_last = pd.to_datetime(script_config_opts['cycle_dt_last'], format=formats['fmt_yyyymmdd_hh'])
    cycle_dt_all = pd.date_range(start=cycle_dt_first, end=cycle_dt_last,
                                 freq=str(script_config_opts['cycle_stride_h']) + 'h')
    return cycle_dt_all


def build_valid_times(cycle_dt, script_config_opts):
    """Build array of valid times for a forecast cycle."""
    beg_lead_h = int(script_config_opts['beg_lead_time'].split(':')[0])
    beg_lead_m = int(script_config_opts['beg_lead_time'].split(':')[1])
    end_lead_h = int(script_config_opts['end_lead_time'].split(':')[0])
    end_lead_m = int(script_config_opts['end_lead_time'].split(':')[1])
    valid_dt_beg = cycle_dt + dt.timedelta(hours=beg_lead_h, minutes=beg_lead_m)
    valid_dt_end = cycle_dt + dt.timedelta(hours=end_lead_h, minutes=end_lead_m)
    valid_dt_all = pd.date_range(start=valid_dt_beg, end=valid_dt_end,
                                 freq=str(script_config_opts['str_lead_time']) + 'min')
    return valid_dt_all


def process_forecast_cycle(cycle_dt, script_config_opts, static_data, config, constants, formats, limits, radar_data):
    """Process a single forecast cycle (all valid times)."""
    cycle_dt_str = cycle_dt.strftime(formats['fmt_yyyymmdd_hh'])
    cycle_dt_plot = cycle_dt.strftime(formats['fmt_time_plot'])
    start_time_plot = 'Start: ' + cycle_dt_plot
    wrf_dir = script_config_opts['wrf_dir_parent'].joinpath(cycle_dt_str)
    out_dir = script_config_opts['out_dir_parent'].joinpath(cycle_dt_str, 'plots')

    # Build valid time array
    valid_dt_all = build_valid_times(cycle_dt, script_config_opts)
    n_valid = len(valid_dt_all)

    # Loop over valid times (this assumes one output time per file)
    for vv in range(n_valid):
        valid_dt = valid_dt_all[vv]
        process_valid_time(valid_dt, vv, wrf_dir, out_dir, start_time_plot, static_data,
                           config, constants, formats, limits, radar_data, script_config_opts)


def process_valid_time(valid_dt, time_index, wrf_dir, out_dir, start_time_plot, static_data,
                       config, constants, formats, limits, radar_data, script_config_opts):
    """Process a single valid time within a forecast cycle."""
    valid_dt_wrf = valid_dt.strftime(formats['fmt_wrf_dt'])
    valid_dt_plot = valid_dt.strftime(formats['fmt_time_plot'])
    valid_dt_file = valid_dt.strftime(formats['fmt_time_file'])
    valid_time_plot = 'Valid: ' + valid_dt_plot

    config['title_r'] = start_time_plot + '\n' + valid_time_plot
    config['wrf_dom'] = 'd0' + script_config_opts['domain']
    map_suffix = '_' + valid_dt_file + '.' + config['plot_type']

    wrf_fname = wrf_dir.joinpath('wrfout_' + config['wrf_dom'] + '_' + valid_dt_wrf)
    wrf_fname_zlev = wrf_dir.joinpath('wrfout_zlev_' + config['wrf_dom'] + '_' + valid_dt_wrf)

    if not check_wrf_file_exists(wrf_fname):
        return

    print(f'Reading {wrf_fname}')
    ds_wrf_nc = netCDF4.Dataset(wrf_fname, mode='r')

    try:
        # Initialize static fields on first iteration
        if not static_data:
            map_opts, wrf_lats, wrf_lons = initialize_static_fields(ds_wrf_nc, config)
            static_data['map_opts'] = map_opts
            static_data['wrf_lats'] = wrf_lats
            static_data['wrf_lons'] = wrf_lons

            # Plot terrain (only once)
            if config['plot_terrain']:
                plot_terrain(ds_wrf_nc, map_opts, config, limits, out_dir)

        # Make the water color transparent for all subsequent plots
        static_data['map_opts']['water_color'] = 'none'

        plot_all_variables(ds_wrf_nc, wrf_fname_zlev, static_data['map_opts'], config,
                           limits, constants, radar_data, map_suffix, out_dir, time_index)

    finally:
        ds_wrf_nc.close()


def check_wrf_file_exists(wrf_fname):
    """Check if WRF file exists."""
    try:
        if not wrf_fname.is_file():
            print(f'WARNING: File {wrf_fname} does not exist. Continuing to the next valid time.')
            return False
    except FileNotFoundError:
        print(f'WARNING: File {wrf_fname} does not exist. Continuing to the next valid time.')
        return False
    return True


def plot_all_variables(ds_wrf_nc, wrf_fname_zlev, map_opts, config, limits, constants,
                       radar_data, map_suffix, out_dir, time_index):
    """Coordinate plotting of all requested variables."""
    # Read surface winds if needed for any plots
    wrf_u10, wrf_v10, wrf_ws10 = None, None, None
    if config['plot_wind_barbs_sfc'] or config['plot_ws10']:
        wrf_u10, wrf_v10, wrf_ws10 = read_surface_winds(ds_wrf_nc)

    # Plot 10-m wind speed
    if config['plot_ws10'] and wrf_ws10 is not None:
        plot_wind_speed_10m(wrf_u10, wrf_v10, wrf_ws10, map_opts, config, limits, constants, map_suffix, out_dir)

    # Plot sea level pressure
    if config['plot_slp']:
        plot_sea_level_pressure(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, map_suffix, out_dir)

    # Plot 2-m temperature
    if config['plot_t2']:
        plot_temperature_2m(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, constants, map_suffix, out_dir)

    # Plot 2-m relative humidity
    if config['plot_rh2']:
        plot_humidity_2m(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, map_suffix, out_dir)

    # Plot precipitation (skip first time step)
    if config['plot_rain'] and time_index > 0:
        plot_precipitation(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, limits, constants, map_suffix, out_dir)

    # Plot radar reflectivity (skip first time step)
    if config['plot_refl'] and time_index > 0:
        plot_radar_reflectivity(ds_wrf_nc, wrf_u10, wrf_v10, map_opts, config, constants, radar_data, map_suffix,
                                out_dir)

    # Plot upper-level winds if requested
    if determine_read_zlev(config):
        plot_upper_level_winds(wrf_fname_zlev, map_opts, config, limits, constants, map_suffix, out_dir)


def main(script_config_opts):
    """Main function with reduced complexity."""
    # Setup configuration and constants
    config = setup_plot_configuration()
    limits = setup_plot_limits()
    constants, formats, radar_data = setup_constants_and_formats()

    # Parse time ranges
    cycle_dt_all = parse_time_ranges(script_config_opts, formats)
    n_cycles = len(cycle_dt_all)

    # Initialize static data storage
    static_data = {}

    # Loop over forecast cycles/initializations
    for cc in range(n_cycles):
        cycle_dt = cycle_dt_all[cc]
        process_forecast_cycle(cycle_dt, script_config_opts, static_data, config,
                               constants, formats, limits, radar_data)


def parse_args():
    """Parse command line arguments."""
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

    if out_dir_parent is None:
        out_dir_parent = wrf_dir_parent

    # Make both paths into pathlib objects
    wrf_dir_parent = pathlib.Path(wrf_dir_parent)
    out_dir_parent = pathlib.Path(out_dir_parent)

    # Validate input formats
    validate_datetime_input(cycle_dt_first, 'init_dt_first', parser)

    if cycle_dt_last is not None:
        validate_datetime_input(cycle_dt_last, 'init_dt_last', parser)
    else:
        cycle_dt_last = cycle_dt_first

    validate_time_input(beg_lead_time, '-b (beg_lead_time)', parser)
    validate_time_input(end_lead_time, '-e (end_lead_time)', parser)

    # Put all these configuration options into a dictionary
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
    }

    return script_config_opts


def validate_datetime_input(dt_str, arg_name, parser):
    """Validate datetime string format."""
    if len(dt_str) != 11:
        print(f'ERROR! Incorrect length for positional argument {arg_name}. Exiting!')
        parser.print_help()
        sys.exit()
    elif dt_str[8] != '_':
        print(f'ERROR! Incorrect format for positional argument {arg_name}. Exiting!')
        parser.print_help()
        sys.exit()


def validate_time_input(time_str, arg_name, parser):
    """Validate time string format."""
    if len(time_str) != 5:
        print(f'ERROR! Incorrect length for optional argument {arg_name}. Exiting!')
        parser.print_help()
        sys.exit()
    elif time_str[2] != ':':
        print(f'ERROR! Incorrect format for optional argument {arg_name}. Exiting!')
        parser.print_help()
        sys.exit()


if __name__ == '__main__':
    now_time_beg = dt.datetime.now(dt.UTC)

    script_config_opts = parse_args()
    main(script_config_opts)

    now_time_end = dt.datetime.now(dt.UTC)
    run_time_tot = now_time_end - now_time_beg
    now_time_beg_str = now_time_beg.strftime('%Y-%m-%d %H:%M:%S')
    now_time_end_str = now_time_end.strftime('%Y-%m-%d %H:%M:%S')
    print('\nScript completed successfully.')
    print('   Beg time: ' + now_time_beg_str)
    print('   End time: ' + now_time_end_str)
    print('   Run time: ' + str(run_time_tot) + '\n')
