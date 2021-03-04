import os
import sys
import re
import numpy as np
import datetime as dt

# var_info values are tuples (units, long_name)
# Taken from synoptic_files.f, with some units SI standardized
# e.g. mb->hPa
# Some of the long_names are unknown to me, hopefully
# someone more knowledgeable will fill these in
var_info = {
      'airtmp': ('C','Air Temperature'),
      'geopht': ('gpm','Geopotential Height'),
      'uuwind': ('m/s','Zonal Wind'),
      'vvwind': ('m/s','Meridional Wind'),
      'wndspd': ('m/s','Wind Speed'),
      'vpress': ('hPa','Vapor Pressure'),
      'prch2o': ('kg/m**2','Unknown'),
      'slpres': ('hPa','Sea Level Pressure'),
      'grdwet': ('percent','Ground Wetness'),
      'prtend': ('cPa/s','Unknown'),
      'grdtmp': ('K','Ground Temperature'),
      'terrht': ('m','Terrain Height'),
      'totcls': ('percent','Unknown'),
      'lowcld': ('percent','Low Cloud'),
      'midcld': ('percent','Mid Cloud'),
      'hghcld': ('percent','High Cloud'),
      'cupflx': ('kg/m**2/s','Unknown'),
      'conpcp': ('cm','Unknown'),
      'sblpcp': ('cm','Unknown'),
      'trpres': ('hPa','Terrain Pressure'),
      'snowdp': ('cm','Snow Depth'),
      'icecon': ('percent','Ice Concentration'),
      'conpcp': ('kg/m**2','Unknown'),
      'trdval': ('dval_m','Unkown'),
      'solflx': ('W/m**2','Solar Flux'),
      'cupcap': ('J/m**2','Unknown'),
      'irrflx': ('W/m**2','Unknown'),
      'slhflx': ('W/m**2','Unknown'),
      'sehflx': ('W/m**2','Unknown'),
      'totpcp': ('cm','Unknown'),
      'bouflx': ('W/m**2','Unknown'),
      'totflx': ('W/m**2','Total Flux'),
      'irflux': ('W/m**2','Infrared Flux'),
      'liftcl': ('m','Lifting Condensation Level'),
      'ht_sfc': ('m/s','Surface Height'),
      'uustrs': ('N/m**2','Zonal Wind Stress'),
      'vvstrs': ('N/m**2','Meridional Wind Stress'),
      'wngust': ('m/s','Wind Gust'),
      'dwptdp': ('C','Dewpoint Depression'),
      'diverg': ('1/s','Divergence'),
      'absvor': ('1/s','Vorticity'),
      'womega': ('cPa/s','Vertical Velocity'),
      'stmfun': ('m**2/s','Stream Function'),
      'velpot': ('m**2/s','Velocity Potential'),
      'stacld': ('percent','Stable Cloud'),
      'concld': ('percent','Convective Cloud'),
      'clouds': ('percent','Total Cloud'),
    }

###########################################

   ##
   ##  input file specified on the command line
   ##  load the data into the numpy array
   ##

if len(sys.argv) == 2:

    # Store the input file and record number
    input_file = os.path.expandvars(sys.argv[1])
    tokens = os.path.basename(input_file).replace('-', '_').split('_');
    varname = tokens[0]
    nlons = int(tokens[4][4:7])  # Usually 360
    nlats = int(tokens[4][8:])   # Usually 181
    try:
        # Print some output to verify that this script ran
        print("Input File: " + repr(input_file))

        # Read input file
        data = np.float64(np.fromfile(input_file, '>f'))

        # Read and re-orient the data
        met_data = data[::-1].reshape(nlats, nlons)[:,::-1].copy()

        print("Data Shape: " + repr(met_data.shape))
        print("Data Type:  " + repr(met_data.dtype))
        print("Data Range: " + repr(min(data)) + " to " + repr(max(data)) +
              " " + var_info[varname][0])
    except NameError:
        print("Trouble reading input file: " + input_file)
else:
    print("Must specify exactly one input file.")
    sys.exit(1)

###########################################

   ##
   ##  create the metadata dictionary
   ##

for token in tokens:
   if(re.search("[0-9]{10,10}", token)):
       ymdh = dt.datetime.strptime(token[0:10],"%Y%m%d%H")
   elif(re.search("[0-9]{8,8}", token)):
       fhr = int(token) / 10000

init  = ymdh
valid = init + dt.timedelta(hours=fhr)
lead, rem = divmod((valid-init).total_seconds(), 3600)

attrs = {
   'valid': valid.strftime("%Y%m%d_%H%M%S"),
   'init':  init.strftime("%Y%m%d_%H%M%S"),
   'lead':  str(int(lead)),
   'accum': '00',

   'name':      varname,
   'long_name': var_info[varname][1],
   'level':     tokens[1]+'_'+tokens[2],
   'units':     var_info[varname][0],

   'grid': {
       'name': 'Global 1 Degree',
       'type' : 'LatLon',
       'lat_ll' :    -90.0,
       'lon_ll' :      0.0,
       'delta_lat' :   1.0,
       'delta_lon' :   1.0,
       'Nlat' :      nlats,
       'Nlon' :      nlons,
   }
}

print("Attributes: " + repr(attrs))
