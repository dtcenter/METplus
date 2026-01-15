#!/usr/bin/env python3

import sys
import netCDF4
from datetime import datetime
from metpy.calc import wind_components,relative_humidity_from_dewpoint,altimeter_to_station_pressure
from metpy.units import units


# Get Arguments
if len(sys.argv) != 2:
    print("ERROR: Must supply input file to script")
    sys.exit(1)

# read input data
infile = sys.argv[1]

var_list = ['WIND','GUST','RH']

# Read the file
ncin = netCDF4.Dataset(infile)

# Read in latitude, longitude, and elevation
lat_arr = ncin['latitude'][:]
lon_arr = ncin['longitude'][:]
elev_arr = ncin['elevation'][:]

dlen = len(lat_arr)

# Read in the station and time
station = ncin['stationName'][:]
timevar = ncin['timeObs']
timevar_cftime = netCDF4.num2date(timevar[:],timevar.units)
valid_time = [datetime.strftime(datetime(tv.year, tv.month, tv.day, tv.hour, tv.minute, tv.second), '%Y%m%d_%H%M%S') for tv in timevar_cftime]

# Set up output data list
point_data = []

# Read in or calculate variable
for var in var_list:
    if var == 'WIND':
        outvar = ncin['windSpeed'][:]
        var_lvl = 10
        var_qc = ncin['windSpeedDD'][:]

    elif var == 'GUST':
        outvar = ncin['windGust'][:]
        var_lvl = 10
        var_qc = ncin['windGustDD'][:]

    elif var == 'RH':
        tmp = ncin['temperature'][:]
        tmp_units = ncin['temperature'].units
        dpt = ncin['dewpoint'][:]
        dpt_units = ncin['dewpoint'].units

        # Add Units
        tmp = units.Quantity(tmp,tmp_units)
        dpt = units.Quantity(dpt,dpt_units)

        # Calculate RH
        rhcalc = relative_humidity_from_dewpoint(tmp,dpt).to('percent')
        outvar = rhcalc.magnitude
        var_lvl = 2
        var_qc = ncin['dewpointDD'][:]

    else:
        # No support for selected variable
        # Error with message
        raise NameError('Variable '+ var+' not currently supported')
        print('Use WIND or RH in the input variable list')
        sys.exit(1)


    # Create the point_data object MET expects
    for dl in range(dlen):
        cur_qc = var_qc[dl].tobytes().decode('utf-8')
        if (cur_qc != 'Z') and (cur_qc != 'X'):
            cur_valid_time = datetime.strftime(datetime(timevar_cftime[dl].year, timevar_cftime[dl].month, 
                timevar_cftime[dl].day, timevar_cftime[dl].hour, timevar_cftime[dl].minute, 
                timevar_cftime[dl].second), '%Y%m%d_%H%M%S')
            point_data.append(['ADPSFC',station[dl].tobytes().decode('utf-8').split('\x00',1)[0],cur_valid_time,
                lat_arr[dl].item(),lon_arr[dl].item(),elev_arr[dl].item(),var,var_lvl,elev_arr[dl].item(),
                cur_qc,outvar[dl].item()])
