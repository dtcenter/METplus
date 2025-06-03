"""
map_funcs.py

Created by: Jared A. Lee (jaredlee@ucar.edu)
Created on: 28 May 2024

This file contains common functions and procedures useful for plotting maps with Cartopy,
typically from WRF model output.
"""

import sys
import os
import numpy as np
import datetime as dt
import wrf
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.mpl.geoaxes import GeoAxes

def calc_bearing(lon1, lat1, lon2, lat2):
    """
    Function to calculate the bearing angle between two points (lon1, lat1) and (lon2, lat2).
    -- Inputs:
        - lon1, lat1: floats, longitude and latitude of point 1
        - lon2, lat2: floats, longitude and latitude of point 2
    -- Outputs:
        - bearing_geog: float, geographical bearing (0 deg = north, 90 deg = east, etc.)
        - bearing_math: float, mathematical bearing (0 deg = east, 90 deg = north, etc.)
    -- Reference:
        - https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/
    """
    DEG2RAD = np.pi / 180.0
    RAD2DEG = 180.0 / np.pi
    x = np.cos(lat2 * DEG2RAD) * np.sin((lon2 - lon1) * DEG2RAD)
    y = ((np.cos(lat1 * DEG2RAD) * np.sin(lat2 * DEG2RAD)) -
         (np.sin(lat1 * DEG2RAD) * np.cos(lat2 * DEG2RAD) * np.cos((lon2-lon1)*DEG2RAD)))
    bearing_geog = np.arctan2(x, y) * RAD2DEG
    bearing_math = 90.0 - bearing_geog
    # Perhaps unnecessary, but keeps it in the range (-180, 180]
    if bearing_math <= -180.0:
        bearing_math += 360.0

    return bearing_geog, bearing_math

def get_cartopy_features():
    """
    Function to get some commonly used Cartopy features (borders, states, oceans, lakes, rivers, land)
    for use in Matplotlib/Cartopy plots.
    -- Inputs: None.
    -- Outputs:
      - borders, states, oceans, lakes, rivers, land
    """

    borders = cartopy.feature.BORDERS
    states  = cartopy.feature.NaturalEarthFeature(category='cultural', scale='10m', facecolor='none',
                                                  name='admin_1_states_provinces_lakes')
    oceans  = cartopy.feature.OCEAN
    lakes   = cartopy.feature.LAKES
    rivers  = cartopy.feature.RIVERS
    land    = cartopy.feature.LAND

    return borders, states, oceans, lakes, rivers, land

def truncate_cmap(cmap, minval=0.0, maxval=1.0, n=100):
    """
    Function to truncate a matplotlib colormap. Particularly useful when plotting terrain.
    -- Required Positional Inputs:
        - cmap: Original Matplotlib colormap
    -- Optional Inputs:
        - minval: Fraction into the original colormap to start the new colormap (default: 0.0)
        - maxval: Fraction into the original colormap to end the new colormap (default: 1.0)
        - n: Number of colors to create in the new colormap (default: 100)
    -- Output:
        - new_cmap: New, truncated colormap
    """
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval), cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def map_plot(opts):
    """
    Procedure to make a map plot with filled contours using matplotlib and Cartopy.
    Optionally overlays the map with wind barbs, markers, text labels, a polygon, or cross-section path.
    -- Input:
        - opts: Dictionary containing plotting options
            Required keys:
            - fname: string or pathlib object specifying the output file name
            - fill_var: 2D variable array to be plotted with filled contours
            - suptitle: string for overall plot title (usually one line)
            - cbar_lab: string for colorbar label (e.g., 'Wind Speed [m/s]')
            - cart_proj: Cartopy object, map projection
            - lons: 1D or 2D array of longitude values
            - lats: 1D or 2D array of latitude values
            - cmap: Matplotlib colormap
            - bounds: Matplotlib colormap bounds
            - norm: matplotlib colormap norm
            Optional keys:
            - cart_xlim: Cartopy object, x-axis limits
            - cart_ylim: Cartopy object, y-axis limits
            - extend: string for colorbar caps ('max', 'min', 'both' [default])
            - fontsize: integer, base fontsize (default: 14)
            - figsize: 2D tuple, defining the figure size (default: (10, 8))
            - cbar_loc: string, identifier for positioning of the colorbar ('bottom' [default], 'top', 'right', 'left')
            - borders, states, oceans, lakes, rivers, land: Cartopy feature objects for the map
            - border_width: numerical line thickness for national borders & coastlines (default: 1.5)
            - water_color: string defining water color for the map (default: 'none' [transparent])
            - lat_labels: array of latitude values to label explicitly on the map
            - lon_labels: array of longitude values to label explicitly on the map
            - suptitle_y: float, y-axis position of the suptitle (default: 0.95)
            - title_l: string, plot subtitle (1 or 2 lines) that gets placed above the top-left corner of the plot axes
            - title_r: string, plot subtitle (1 or 2 lines) that gets placed above the top-right corner of the plot axes
            - title_c: string, plot subtitle (1 or 2 lines) that gets placed above the center of the plot axes
            - map_x_thin: integer, thin wind barb location overlays in x-direction (every Nth grid point) (default: 25)
            - map_y_thin: integer, thin wind barb location overlays in y-direction (every Nth grid point) (default: 25)
            - barb_width: float, linewidth of wind barbs (default: 0.25)
            - u: array-like, define the barb directions
            - v: array-like, define the barb directions
            - mark1_lon: array of longitude values for set 1 of markers
            - mark1_lat: array of latitude values for set 1 of markers
            - mark1_size: integer specifying marker size for set 1 of markers (default: 100)
            - mark1_style: string specifying marker style for set 1 of markers (default: 'o')
            - mark1_color: string specifying the marker color for set 1 of markers
            - mark1_edgecolor: string specifying the marker edge color for set 1 of markers (default: 'black')
            - mark1_width: float specifying linewidth for set 1 of markers
            - mark1_val_fill: boolean flag to fill set 1 of markers from data value, cmap, and norm (default: False)
            - mark1_var: variable containing data to fill in set 1 of markers (e.g., plot obs station data)
            - mark1_zorder: integer indicator of the Matplotlib draw order for set 1 of markers (default: 10)
            - mark2_lon: array of longitude values for set 2 of markers
            - mark2_lat: array of latitude values for set 2 of markers
            - mark2_size: integer specifying marker size for set 2 of markers (default: 100)
            - mark2_style: string specifying marker style for set 2 of markers (default: 'o')
            - mark2_color: string specifying the marker color for set 2 of markers
            - mark2_edgecolor: string specifying the marker edge color for set 2 of markers (default: 'black')
            - mark2_width: float specifying linewidth for set 2 of markers
            - mark2_val_fill: boolean flag to fill set 2 of markers from data value, cmap, and norm (default: False)
            - mark2_var: variable containing data to fill in set 2 of markers (e.g., plot obs station data)
            - mark2_zorder: integer indicator of the Matplotlib draw order for set 2 of markers (default: 11)
            - text1_lat: array of floats for latitudes for set 1 of text
            - text1_lon: array of floats for longitudes for set 1 of text
            - text1_lab: array of strings for labels for set 1 of text
            - text1_lab_wt: numeric or string indicating font weight for set 1 of text (default: 'normal')
            - text2_lat: array of floats for latitudes for set 2 of text
            - text2_lon: array of floats for longitudes for set 2 of text
            - text2_lab: array of strings for labels for set 2 of text
            - text2_lab_wt: numeric or string indicating font weight for set 2 of text (default: 'normal')
            - lg_text: array of legend labels
            - lg_loc: string, defining legend placement
            - lg_fontsize: integer fontsize for legend labels
    -- Output:
        - generates a plot saved to fname
    """
    # Set default values for optional dictionary entries
    opts.setdefault('cart_xlim', None)
    opts.setdefault('cart_ylim', None)
    opts.setdefault('extend', 'both')
    opts.setdefault('fontsize', 14)
    opts.setdefault('figsize', (10,8))
    opts.setdefault('cbar_loc', 'bottom')
    opts.setdefault('borders', None)
    opts.setdefault('states', None)
    opts.setdefault('oceans', None)
    opts.setdefault('lakes', None)
    opts.setdefault('rivers', None)
    opts.setdefault('land', None)
    opts.setdefault('water_color', 'none')
    opts.setdefault('border_width', 1.5)
    opts.setdefault('lat_labels', None)
    opts.setdefault('lon_labels', None)
    opts.setdefault('suptitle_y', 0.95)
    opts.setdefault('title_l', None)
    opts.setdefault('title_r', None)
    opts.setdefault('title_c', None)
    opts.setdefault('map_x_thin', 25)
    opts.setdefault('map_y_thin', 25)
    opts.setdefault('barb_width', 0.25)
    opts.setdefault('u', None)
    opts.setdefault('v', None)
    opts.setdefault('mark1_lat', None)
    opts.setdefault('mark1_lon', None)
    opts.setdefault('mark1_size', 100)
    opts.setdefault('mark1_style', 'o')
    opts.setdefault('mark1_color', None)
    opts.setdefault('mark1_edgecolor', 'black')
    opts.setdefault('mark1_width', 1.5)
    opts.setdefault('mark1_val_fill', False)
    opts.setdefault('mark1_var', None)
    opts.setdefault('mark1_zorder', 10)
    opts.setdefault('mark2_lat', None)
    opts.setdefault('mark2_lon', None)
    opts.setdefault('mark2_size', 100)
    opts.setdefault('mark2_style', 'o')
    opts.setdefault('mark2_color', None)
    opts.setdefault('mark2_edgecolor', 'black')
    opts.setdefault('mark2_width', 1.5)
    opts.setdefault('mark2_val_fill', False)
    opts.setdefault('mark2_var', None)
    opts.setdefault('mark2_zorder', 11)
    opts.setdefault('text1_lat', None)
    opts.setdefault('text1_lon', None)
    opts.setdefault('text1_lab', None)
    opts.setdefault('text1_lab_wt', 'normal')
    opts.setdefault('text2_lat', None)
    opts.setdefault('text2_lon', None)
    opts.setdefault('text2_lab', None)
    opts.setdefault('text2_lab_wt', 'normal')
    opts.setdefault('lg_text', None)
    opts.setdefault('lg_loc', 'lower left')
    opts.setdefault('lg_fontsize', 14)

    # Pull everything out of the opts dict into variables for cleaner code later on
    fname = opts['fname']
    fill_var = opts['fill_var']
    suptitle = opts['suptitle']
    cbar_lab = opts['cbar_lab']
    cart_proj = opts['cart_proj']
    cart_xlim = opts['cart_xlim']
    cart_ylim = opts['cart_ylim']
    lons = opts['lons']
    lats = opts['lats']
    cmap = opts['cmap']
    bounds = opts['bounds']
    norm = opts['norm']
    extend = opts['extend']
    fontsize = opts['fontsize']
    figsize = opts['figsize']
    cbar_loc = opts['cbar_loc']
    borders = opts['borders']
    states = opts['states']
    oceans = opts['oceans']
    lakes = opts['lakes']
    rivers = opts['rivers']
    land = opts['land']
    water_color = opts['water_color']
    border_width = opts['border_width']
    lat_labels = opts['lat_labels']
    lon_labels = opts['lon_labels']
    suptitle_y = opts['suptitle_y']
    title_l = opts['title_l']
    title_r = opts['title_r']
    title_c = opts['title_c']
    map_x_thin = opts['map_x_thin']
    map_y_thin = opts['map_y_thin']
    barb_width = opts['barb_width']
    u = opts['u']
    v = opts['v']
    mark1_lat = opts['mark1_lat']
    mark1_lon = opts['mark1_lon']
    mark1_size = opts['mark1_size']
    mark1_style = opts['mark1_style']
    mark1_color = opts['mark1_color']
    mark1_edgecolor = opts['mark1_edgecolor']
    mark1_width = opts['mark1_width']
    mark1_val_fill = opts['mark1_val_fill']
    mark1_var = opts['mark1_var']
    mark1_zorder = opts['mark1_zorder']
    mark2_lat = opts['mark2_lat']
    mark2_lon = opts['mark2_lon']
    mark2_size = opts['mark2_size']
    mark2_style = opts['mark2_style']
    mark2_color = opts['mark2_color']
    mark2_edgecolor = opts['mark2_edgecolor']
    mark2_width = opts['mark2_width']
    mark2_val_fill = opts['mark2_val_fill']
    mark2_var = opts['mark2_var']
    mark2_zorder = opts['mark2_zorder']
    text1_lat = opts['text1_lat']
    text1_lon = opts['text1_lon']
    text1_lab = opts['text1_lab']
    text1_lab_wt = opts['text1_lab_wt']
    text2_lat = opts['text2_lat']
    text2_lon = opts['text2_lon']
    text2_lab = opts['text2_lab']
    text2_lab_wt = opts['text2_lab_wt']
    lg_text = opts['lg_text']
    lg_loc = opts['lg_loc']
    lg_fontsize = opts['lg_fontsize']

    # Set some Matplotlib resources
    mpl.rcParams['figure.figsize'] = figsize
    mpl.rcParams['grid.color'] = 'gray'
    mpl.rcParams['grid.linestyle'] = ':'
    mpl.rcParams['font.size'] = fontsize + 2
    mpl.rcParams['figure.titlesize'] = fontsize + 2
    mpl.rcParams['savefig.bbox'] = 'tight'
    ll_size = fontsize - 2
    data_crs = ccrs.PlateCarree()

    print('-- Plotting ' + str(fname))

    # Define the figure and axes
    fig = plt.figure()
    ax = plt.subplot(projection=cart_proj)

    # If cart_xlim and cart_ylim tuples are not provided, then set plot limits from lat/lon data directly
    if cart_xlim is not None and cart_ylim is not None:
        ax.set_xlim(cart_xlim)
        ax.set_ylim(cart_ylim)
    else:
        ax.set_extent([np.min(lons), np.max(lons), np.min(lats), np.max(lats)], crs=cart_proj)

    # If lons & lats are 1D, make them into 2D arrays
    if lons.ndim == 1 and lats.ndim == 1:
        ll2d = np.meshgrid(lons, lats)
        lons = ll2d[0]
        lats = ll2d[1]

    # Optional: Add various cartopy features
    if borders != None:
        ax.add_feature(borders, linewidth=border_width, linestyle='-', zorder=3)
    if states != None:
        ax.add_feature(states, linewidth=border_width/3.0, edgecolor='black', zorder=4)
    if oceans != None:
        # Drawing the oceans can be VERY slow with Cartopy 0.20+ for some domains, so may want to skip it
        # Can set the facecolor for the axes to water_color instead (usually we want this 'none' except for terrain)
        ax.add_feature(oceans, facecolor=water_color, zorder=2)
        # ax.add_feature(oceans, facecolor='none', zorder=2)
        # ax.set_facecolor(opts['water_color'])
    if lakes != None:
        # Unless facecolor='none', lakes w/ facecolor will appear above filled contour plot, which is undesirable
        ax.add_feature(lakes, facecolor=water_color, linewidth=0.25, edgecolor='black', zorder=5)
    ax.coastlines(zorder=6, linewidth=border_width)

    # Sometimes longitude labels show up on y-axis, and latitude labels on x-axis in older versions of Cartopy
    # Print lat/lon labels only for a specified set (determined by trial & error) to avoid this problem for now
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)
    gl.rotate_labels = False
    # If specific lat/lon labels are not specified, then just label the default gridlines
    if lon_labels is not None:
        gl.xlocator = mticker.FixedLocator(lon_labels)
    if lat_labels is not None:
        gl.ylocator = mticker.FixedLocator(lat_labels)
    gl.top_labels = True
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = True
    gl.xlabel_style = {'size': ll_size}
    gl.ylabel_style = {'size': ll_size}

    # Draw the actual filled contour plot
    # NOTE: Sometimes a cartopy contourf plot may fail with a Shapely TopologicalError.
    #       It appears to happen sometimes when projecting a dataset onto a different projection.
    #       This error occurs more often if nans are present.
    #       Replacing nans with scipy.interpolate.griddata solves some of these errors, but not all.
    #       Interestingly, plt.contour still seems to work in these situations as a (suboptimal) workaround.
    #       This bug occurs with Shapely 1.8.0, Cartopy 0.20.1.
    #       This issue was resolved with Cartopy 0.20.2 (https://github.com/SciTools/cartopy/issues/1936).
    # Using the transform_first argument results in a noticeable speed-up:
    #    https://scitools.org.uk/cartopy/docs/latest/gallery/scalar_data/contour_transforms.html
    #  - This also requires the X and Y variables to be 2-D arrays.
    #  - This also resolves TopologyException: side location conflict errors that can occur when NaNs are present.

    # If the variable has the same shape as lats, then plot the filled contour field
    if fill_var.shape == lats.shape:
        contourf = True
        plt.contourf(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(fill_var), bounds,
                     cmap=cmap, norm=norm, extend=extend, transform=data_crs, transform_first=(ax, True))
    # Otherwise, we presumably need to plot an empty map and then plot markers
    else:
        contourf = False
        if mark1_lon is None or mark1_lat is None:
            print('ERROR: map_plot in map_funcs.py:')
            print('   var does not match the shape of lons or lats.')
            print('   If plotting a contour map, fix the mismatch in shape between fill_var and lons/lats.')
            print('   Otherwise, this could imply a need for a blank map with markers.')
            print('   However, mark1_lon and/or mark1_lat are not provided either.')
            print('   If a filled contour map is desired, ensure fill_var is the same shape as lons and lats.')
            print('   If a blank map with markers is desired instead, provide mark1_lon and mark1_lat.')
            print('   If the markers should be filled according to a data value, then set mark1_val_fill=True.')
            print('   Or if a future use case is identified that requires a blank map & no markers, then modify code.')
            print('   Exiting!')
            sys.exit()

    # Optional: Add marker set 1 to the plot
    if mark1_lon is not None and mark1_lat is not None:
        if mark1_lat.shape != mark1_lon.shape:
            print('ERROR: map_plot in map_funcs.py:')
            print(       'mark1_lat and mark1_lon do not have the same shape.')
            print('       Exiting!')
            sys.exit()
        if lg_text is None:
            lg_lab1 = None
        else:
            lg_lab1 = lg_text[0]
        if mark1_val_fill:
            # Fill markers according to their data value, cmap, and norm
            # NOTE: If plotting markers over a blank map, must use plt.scatter, not ax.scatter, to avoid an error about
            #       the lack of a mappable when drawing the colorbar below.
            if mark1_var.shape == mark1_lat.shape:
                if contourf:
                    ax.scatter(mark1_lon, mark1_lat, c=mark1_var, marker=mark1_style, s=mark1_size,
                               edgecolors=mark1_edgecolor, label=lg_lab1, linewidths=mark1_width,
                               cmap=cmap, norm=norm, transform=data_crs, zorder=mark1_zorder)
                else:
                    plt.scatter(mark1_lon, mark1_lat, c=mark1_var, marker=mark1_style, s=mark1_size,
                                edgecolors=mark1_edgecolor, label=lg_lab1, linewidths=mark1_width,
                                cmap=cmap, norm=norm, transform=data_crs, zorder=mark1_zorder)
            else:
                print('ERROR: map_plot in map_funcs.py:')
                print('       mark1_var, mark1_lat, and mark1_lon are not all the same shape.')
                print('       Exiting!')
                sys.exit()
        # Marker set 1 not filled by any data values
        else:
            ax.scatter(mark1_lon, mark1_lat, marker=mark1_style, s=mark1_size, color=mark1_color,
                       edgecolors=mark1_edgecolor, label=lg_lab1, linewidths=mark1_width,
                       transform=data_crs, zorder=mark1_zorder)

    # Optional: Add marker set 2 to the plot
    if mark2_lon is not None and mark2_lat is not None:
        if mark2_lat.shape != mark2_lon.shape:
            print('ERROR: map_plot in map_funcs.py:')
            print(       'mark2_lat and mark2_lon do not have the same shape.')
            print('       Exiting!')
            sys.exit()
        if lg_text is None:
            lg_lab2 = None
        else:
            lg_lab2 = lg_text[1]
        # Marker set 2 filled by data values
        if mark2_val_fill:
            # Fill markers according to their data value, cmap, and norm
            # NOTE: If plotting markers over a blank map, must use plt.scatter, not ax.scatter, to avoid an error about
            #       the lack of a mappable when drawing the colorbar below.
            if mark2_var.shape == mark2_lat.shape:
                if contourf:
                    ax.scatter(mark2_lon, mark2_lat, c=mark2_var, marker=mark2_style, s=mark2_size,
                               edgecolors=mark2_edgecolor, label=lg_lab2, linewidths=mark2_width,
                               cmap=cmap, norm=norm, transform=data_crs, zorder=mark2_zorder)
                else:
                    plt.scatter(mark2_lon, mark2_lat, c=mark2_var, marker=mark2_style, s=mark2_size,
                                edgecolors=mark2_edgecolor, label=lg_lab2, linewidths=mark2_width,
                                cmap=cmap, norm=norm, transform=data_crs, zorder=mark2_zorder)
            else:
                print('ERROR: map_plot in map_funcs.py:')
                print('       mark2_var, mark2_lat, and mark2_lon are not all the same shape.')
                print('       Exiting!')
                sys.exit()
        # Marker set 2 not filled by data values
        else:
            ax.scatter(mark2_lon, mark2_lat, marker=mark2_style, s=mark2_size, color=mark2_color,
                       edgecolors=mark2_edgecolor, label=lg_lab2, linewidths=mark2_width,
                       transform=data_crs, zorder=mark1_zorder)

    # Draw the colorbar
    # Credit: https://stackoverflow.com/questions/30030328/correct-placement-of-colorbar-relative-to-geo-axes-cartopy
    # Create colorbar axes (temporarily) anywhere
    cax = fig.add_axes([0, 0, 0.1, 0.1])
    # Find the location of the main plot axes
    posn = ax.get_position()
    # Adjust the positioning and orientation of the colorbar, and then draw it
    # The colorbar will inherit the norm/extend attributes from the plt.contourf or plt.scatter call above
    if cbar_loc == 'bottom':
        cax.set_position([posn.x0, posn.y0-0.09, posn.width, 0.05])
        plt.colorbar(cax=cax, orientation='horizontal', label=cbar_lab)
    elif cbar_loc == 'right':
        cax.set_position([posn.x0+posn.width+0.05, posn.y0, 0.04, posn.height])
        plt.colorbar(cax=cax, orientation='vertical', label=cbar_lab)
    elif cbar_loc == 'top' or cbar_loc == 'left':
        print('WARNING: cbar_loc=' + cbar_loc + ' requested. Unsupported option. Colorbar will not be drawn.')
        print('   Add directives in map_funcs.map_plot to handle that option and draw the colorbar.')

    # Add the overall plot title
    plt.suptitle(suptitle, y=suptitle_y)

    # Optional: Add titles to the subplot
    if title_l is not None:
        ax.set_title(title_l, fontsize=fontsize, loc='left')
    if title_r is not None:
        ax.set_title(title_r, fontsize=fontsize, loc='right')
    if title_c is not None:
        ax.set_title(title_c, fontsize=fontsize, loc='center')

    # Optional: Add set 1 of text labels to the plot
    if text1_lab is not None and text1_lat is not None and text1_lon is not None:
        if len(text1_lab) != len(text1_lat) or len(text1_lab) != len(text1_lon):
            print('ERROR: map_plot in map_funcs.py:')
            print('       text1_lab, text1_lat, and text1_lon do not all have the same length.')
            print('       Exiting!')
            sys.exit()
        n_text = len(text1_lab)
        for xx in range(n_text):
            ax.text(text1_lon[xx], text1_lat[xx], text1_lab[xx], horizontalalignment='center',
                    transform=data_crs, size=fontsize, zorder=13, weight=text1_lab_wt)

    # Optional: Add set 2 of text labels to the plot
    if text2_lab is not None and text2_lat is not None and text2_lon is not None:
        if len(text2_lab) != len(text2_lat) or len(text2_lab) != len(text2_lon):
            print('ERROR: map_plot in map_funcs.py:')
            print('       text2_lab, text2_lat, and text2_lon do not all have the same length.')
            print('       Exiting!')
            sys.exit()
        n_text = len(text2_lab)
        for xx in range(n_text):
            ax.text(text2_lon[xx], text2_lat[xx], text2_lab[xx], horizontalalignment='center',
                    transform=data_crs, size=fontsize, zorder=14, weight=text2_lab_wt)

    # Optional: Draw wind barbs
    if u is not None and v is not None:
        if isinstance(lons, np.ndarray):
            x_thin = lons[::map_y_thin, ::map_x_thin]
        else:
            x_thin = lons[::map_y_thin, ::map_x_thin].values
        if isinstance(lats, np.ndarray):
            y_thin = lats[::map_y_thin, ::map_x_thin]
        else:
            y_thin = lats[::map_y_thin, ::map_x_thin].values
        u_thin = u[::map_y_thin, ::map_x_thin]
        v_thin = v[::map_y_thin, ::map_x_thin]
        # Assume winds input to here are in m/s instead of kts, so reduce the barb_increments from 5/10/50 to 2.5/5/25
        ax.barbs(x_thin, y_thin, u_thin, v_thin, length=5, transform=data_crs, linewidth=barb_width,
                 barb_increments={'half': 2.5, 'full': 5, 'flag': 25})

    # Optional: Add a legend (most useful if 2+ sets of markers)
    if lg_text is not None:
        ax.legend(loc=lg_loc, fontsize=lg_fontsize).set_zorder(15)

    # create output directory if it does not already exist
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    # Save and close the figure
    plt.savefig(fname)
    plt.close()
