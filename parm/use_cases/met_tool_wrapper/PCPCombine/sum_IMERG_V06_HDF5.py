#!/usr/bin/env python

from __future__ import print_function

import h5py
import numpy as np
import numpy.ma as ma 
import datetime as dt
import os
import sys
import math
import glob

########################################################################
##
##  This script processes IMERG V06 HDF5 data files:
##  https://pmm.nasa.gov/data-access/downloads/gpm
##
##  Expected naming convention example:
##    3B-HHR.MS.MRG.3IMERG.20180807-S143000-E145959.0870.V06B.HDF5
##
##  Usage: sum_IMERG_V06_HDF5.py input_dir var_name valid_time accum_hr
##    where "input_dir"  is a directory containing IMERG data
##          "var_name"   is the input variable name to be accumulated
##          "valid_time" is the desired valid time in YYYYMMDDHH format
##          "accum_hr"   is the desired accumulation interval in hours
##
########################################################################

## Constants
in_accum_hr = 0.5

########################################################################

# Function to read IMERG data
def read_IMERG_data(cur_file, var_name):

  # Read input file
  f = h5py.File(cur_file, 'r')

  # Read the requested variable
  d = f['Grid'][var_name]

  # Check for expected dimensions (time, lon, lat)
  if d.attrs['DimensionNames'] != b'time,lon,lat':
    print("Unexpected list of dimensions: " . d.attrs['DimensionNames'])
    sys.exit(1)

  # Get data for the first timestep
  data = np.float64(d[0,:]).transpose()

  # Flip data along the equator
  data = data[::-1]

  # Define mask for missing data
  m = ma.masked_less(data, -9999)

  # Convert rate to accumulation 
  units = d.attrs['units']
  if units == b"mm/hr":
    m = m * in_accum_hr
    units = "mm"

  print("Data Shape and Type  :" + repr(m.shape) + ", " + repr(m.dtype))

  # Create the metadata dictionary
  lat = np.float32(f['Grid']['lat'][:])
  lon = np.float32(f['Grid']['lon'][:])
  a = {
   'name':      var_name,
   'long_name': var_name,
   'level':     'Surface',
   'units':     units,

   'grid': {
     'name':       'IMERG-Grid',
     'type' :      'LatLon',
     'lat_ll' :    np.float64(min(lat)),
     'lon_ll' :    np.float64(min(lon)),
     'delta_lat' : round((max(lat)-min(lat))/(len(lat)-1), 4),
     'delta_lon' : round((max(lon)-min(lon))/(len(lon)-1), 4),
     'Nlat' :      len(lat),
     'Nlon' :      len(lon),
    }
  }
  return (m, a) 

########################################################################
if len(sys.argv) == 5:
  input_dir  = os.path.expandvars(sys.argv[1])
  var_name   = sys.argv[2]
  valid_time = dt.datetime.strptime(sys.argv[3], "%Y%m%d%H")
  accum_hr   = float(sys.argv[4])

  try:

    # Print command line options
    print("Input Directory      : " + repr(input_dir))
    print("Variable Name        : " + repr(var_name))
    print("Valid Time           : " + repr(valid_time))
    print("Accumulation (hr)    : " + repr(accum_hr))

    # Loop through timestamps
    cur_accum = 0
    cur_valid = valid_time
    while cur_accum < accum_hr:

      print("======================")
      print("Processing Valid Time: " + repr(cur_valid))

      # Build the expected input file name
      cur_glob = input_dir + "/" + "*IMERG." + \
                 (cur_valid - dt.timedelta(hours=in_accum_hr)).strftime("%Y%m%d-S%H%M%S") + \
                 (cur_valid - dt.timedelta(seconds=1)).strftime("-E%H%M%S") + "*.HDF5"
      cur_list = glob.glob(cur_glob)

      # Check for exactly one matching file
      if len(cur_list) != 1:
        print("ERROR: Found " + repr(len(cur_list)) + " files matching \"" + cur_glob + "\"")
        exit(1)
      else:
        cur_file = cur_list[0]

      # Process the current file
      print("Reading File Name    : " + repr(cur_file))
      (cur_data, attrs) = read_IMERG_data(cur_file, var_name)
      if cur_accum == 0:
        data  = cur_data
      else:
        data += cur_data

      # Increment accumulation and decrement valid time
      cur_accum += in_accum_hr
      cur_valid -= dt.timedelta(hours=in_accum_hr)

      print("Running Accum (hr)   : " + repr(cur_accum))

    print("======================")

    # Store mask values as -9999
    met_data = data.data.copy()
    met_data[data.mask] = -9999
    print("Valid Data    : " + \
          repr(data.count()) + " of " + \
          repr(data.size) + " (" + \
          repr(round(100.0*data.count()/data.size,0)) + "%)")
    print("Range of Data : " + repr(data.min()) + " to " + repr(data.max()))

    # Add timing information
    attrs.update( { 'valid' : valid_time.strftime("%Y%m%d_%H%M%S") } )
    attrs.update( { 'init'  : valid_time.strftime("%Y%m%d_%H%M%S") } )
    attrs.update( { 'lead'  : '00' } )
    attrs.update( { 'accum' : "%02d" % (accum_hr) } )
    print("Attributes    : " + repr(attrs))

  except NameError:
    print("Trouble reading data.")

else:
    print("Must specify exactly 4 arguments: input_dir, var_name, valid_time, accum_hr")
    sys.exit(1)

########################################################################
