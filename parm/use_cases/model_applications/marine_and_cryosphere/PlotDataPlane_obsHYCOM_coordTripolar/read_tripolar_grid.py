import os
import sys
import pandas as pd
import xarray as xr
import xesmf as xe

###############################################################################
# This script reads in tripolar grid ice data from the rtofs model and
# passes it to MET tools through python embedding.
# Written by George McCabe, NCAR
# January 2021
# Python embedding structure adapted from read_PostProcessed_WRF.py from
# the DTC MET User's Page.
# Tripolar grid logic adapted from ice_cover.py
# from Todd Spindler, NOAA/NCEP/EMC.
# Based on a script written by Lindsay Blank, NCAR in April 2020
# Arguments:
#  input filename - path to input NetCDF file to process
#  field name - name of field to read (ice_coverage or ice thickness)
#  hemisphere - hemisphere to process (north or south)
# Example call: read_tripolar_grid.py /path/to/file.nc ice_coverage north
###############################################################################


# degrees between lat/lon points in output grid
LATITUDE_SPACING = 0.25
LONGITUDE_SPACING = 0.25

# set DEBUG to True to get debugging output
DEBUG = False

# latitude boundaries where curved data begins
# we are only concerned with data outside of the boundary for this case
# so we crop data that is below (for north) or above (for south)
LAT_BOUND_NORTH = 30.98
LAT_BOUND_SOUTH = -39.23


# list of valid values to specify for hemisphere
HEMISPHERES = ['north', 'south']

def print_min_max(ds):
    print(f"MIN LAT: {float(ds['lat'].min())} and "
          f"MIN LON: {float(ds['lon'].min())}")
    print(f"MAX LAT: {float(ds['lat'].max())} and "
          f"MAX LON: {float(ds['lon'].max())}")

if len(sys.argv) < 4:
    print("Must specify exactly one input file and variable name.")
    sys.exit(1)

# Read the input file as the first argument
input_file = os.path.expandvars(sys.argv[1])
var = sys.argv[2]
hemisphere = sys.argv[3]

# read optional weight file if provided
if len(sys.argv) > 4:
    weight_file = sys.argv[4]
else:
    weight_file = f'weight_{hemisphere}.nc'

if hemisphere not in HEMISPHERES:
    print(f"ERROR: Invalid hemisphere value ({hemisphere}) "
          f"Valid options are {HEMISPHERES}")
    sys.exit(1)

try:
    # Print some output to verify that this script ran
    print(f"Input File: {repr(input_file)}")
    print(f"Variable: {repr(var)}")
    print(f"Hemisphere: {repr(hemisphere)}")

    # read input file
    xr_dataset = xr.load_dataset(input_file,
                                 decode_times=True)
except NameError:
    print("Trouble reading data from input file")
    sys.exit(1)

# get time information
dt = pd.to_datetime(str(xr_dataset.MT[0].values))
valid_time = dt.strftime('%Y%m%d_%H%M%S')

# rename Latitude and Longitude to format that xesmf expects
xr_dataset = xr_dataset.rename({'Longitude': 'lon', 'Latitude': 'lat'})
# drop singleton time dimension for this example
xr_dataset = xr_dataset.squeeze()

# print out input data for debugging
if DEBUG:
    print("INPUT DATASET:")
    print(xr_dataset)
    print_min_max(xr_dataset)
    print('\n\n')

# get field name values to read into attrs
standard_name = xr_dataset[var].standard_name
long_name = xr_dataset[var].long_name.strip()

# trim off row of data
xr_dataset = xr_dataset.isel(Y=slice(0,-1))

# remove data inside boundary latitude to get only curved data
if hemisphere == 'north':
    xr_out_bounds = xr_dataset.where(xr_dataset.lat >= LAT_BOUND_NORTH,
                                     drop=True)
    lat_min = xr_out_bounds.lat.min()
    lat_max = 90
else:
    xr_out_bounds = xr_dataset.where(xr_dataset.lat <= LAT_BOUND_SOUTH,
                                     drop=True)
    lat_min = max(-79, xr_out_bounds.lat.min())
    lat_max = xr_out_bounds.lat.max()


if DEBUG:
    print("OUTSIDE BOUNDARY LAT")
    print(xr_out_bounds)
    print_min_max(xr_out_bounds)
    print('\n\n')

# create output grid using lat/lon bounds of data outside boundary
out_grid = xe.util.grid_2d(0,
                           360,
                           LONGITUDE_SPACING,
                           lat_min,
                           lat_max,
                           LATITUDE_SPACING)

# create regridder using cropped data and output grid
# NOTE: this creates a temporary file in the current directory!
# consider supplying path to file in tmp directory using filename arg
# set reuse_weights=True to read temporary weight file if it exists
regridder = xe.Regridder(xr_out_bounds,
                         out_grid,
                         'bilinear',
                         ignore_degenerate=True,
                         reuse_weights=True,
                         filename=weight_file)

# regrid data
xr_out_regrid = regridder(xr_out_bounds)
met_data = xr_out_regrid[var]

# flip the data
met_data = met_data[::-1, ]

if DEBUG:
    print("PRINT MET DATA")
    print(met_data)

    print("Data Shape: " + repr(met_data.shape))
    print("Data Type:  " + repr(met_data.dtype))
    print("Max: " + repr(met_data.max))
    print_min_max(met_data)
    print('\n\n')

# Calculate attributes
lat_lower_left = float(met_data['lat'].min())
lon_lower_left = float(met_data['lon'].min())
n_lat = met_data['lat'].shape[0]
n_lon = met_data['lon'].shape[1]
delta_lat = (float(met_data['lat'].max()) - float(met_data['lat'].min()))/float(n_lat)
delta_lon = (float(met_data['lon'].max()) - float(met_data['lon'].min()))/float(n_lon)

# create the attributes dictionary to describe the data to pass to MET
met_data.attrs = {
        'valid': valid_time,
        'init': valid_time,
        'lead': "00",
        'accum': "00",
        'name': var,
        'standard_name': standard_name,
        'long_name': long_name,
        'level': "SURFACE",
        'units': "UNKNOWN",

        # Definition for LatLon grid
        'grid': {
            'type': "LatLon",
            'name': "RTOFS Grid",
            'lat_ll': lat_lower_left,
            'lon_ll': lon_lower_left,
            'delta_lat': delta_lat,
            'delta_lon': delta_lon,
            'Nlat': n_lat,
            'Nlon': n_lon,
            }
        }
attrs = met_data.attrs
print("Attributes: " + repr(met_data.attrs))
