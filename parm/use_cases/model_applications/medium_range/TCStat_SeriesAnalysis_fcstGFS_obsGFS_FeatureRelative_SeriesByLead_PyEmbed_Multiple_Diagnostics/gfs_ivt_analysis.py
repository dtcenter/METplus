# This script is a combination of two scripts originally from Taylor Mandelbaum, SBU. 
# Adjustments have been made by Lindsay Blank, NCAR. 
# May 2020
###################################################################################################

import pygrib
import numpy as np
import sys
import os
import re
import datetime as dt
import metpy.calc as mc

###################################################################################################

def ivt(input_file):
    grbs = pygrib.open(input_file)
    g = 9.81    # Setting gravity constant
    print(input_file)
    grbs.rewind()
    
    # Initialize variable arrays 
    levs = [] # Levels 
    q    = [] # Specific humidity
    hgt  = [] # Geopotential height
    temp = [] # Temperature
    u    = [] # u-wind
    v    = [] # v-wind
    
    # Fill in variable arrays from input file.
    for grb in grbs:
        if grb.level*100 <= 10000:
            continue
        elif np.logical_and('v-' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
            v.append(grb.values)        
        elif np.logical_and('u-' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
            u.append(grb.values)
        elif np.logical_and('Temperature' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
            temp.append(grb.values)
        elif np.logical_and('Geopotential' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
            hgt.append(grb.values)
        elif np.logical_and('Specific' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
            q.append(grb.values)
            levs.append(grb.level)
        
    temp = np.array(temp)
    hgt  = np.array(hgt)
    u    = np.array(u)
    v    = np.array(v)
    
    grbs.rewind()
    
    # If we didn't find specific humidity, look for relative humidity.
    if len(q) == 0:
        for grb in grbs:
            if grb.level*100 <= 10000:
                continue
            if np.logical_and('Relative' in grb.parameterName,grb.typeOfLevel=='isobaricInhPa'):
                q.append(grb.values)
                levs.append(grb.level)
            
        levs = np.array(levs)
        # Clausius-Clapeyron time
        es = 610.78*np.exp((17.67*(temp-273.15)/(temp-29.65))) # Calculate saturation vapor pressure
        e = es*(np.array(q)/100) # Calculate vapor pressure 
        w = 0.622*es/(levs[:,None,None]*100) # Calculate water vapor
        q = w/(w+1) # Calculate specific humidity
    q = np.array(q)
    
    uv = np.sqrt(u**2+v**2) # Calculate wind
    mflux_total = np.sum(q,axis=0)*(1/g)*np.mean(uv,axis=0)*(np.max(levs)-np.min(levs)) #calculate mass flux
    met_data = mflux_total.copy() #Pass mass flux to be used by MET tools
    print(np.max(met_data))
    #np.save('{}.npy'.format(sys.argv[1]),mflux_total)
    grbs.close()

    return met_data

###################################################################################################

input_file = os.path.expandvars(sys.argv[1])

data = ivt(input_file) #Call function to calculate IVT

met_data = data
met_data = met_data.astype('float64')

# Automatically fill out time information from input file. 
for token in os.path.basename(input_file).replace('-', '_').split('_'):
   if(re.search("[0-9]{8,8}", token)):
       ymd = dt.datetime.strptime(token[0:8],"%Y%m%d")
   elif(re.search("^[0-9]{4}$", token)):
       hh  = int(token[0:2])
   elif(re.search("^[0-9]{3}$", token)):
       day = int(token.replace("", ""))

print("Data Shape: " + repr(met_data.shape))
print("Data Type:  " + repr(met_data.dtype))

# GFS Analysis
valid  = ymd  + dt.timedelta(hours=hh)
init = valid

attrs = {
   'valid': valid.strftime("%Y%m%d_%H%M%S"),
   'init':  init.strftime("%Y%m%d_%H%M%S"),
   'lead':  '00',
   'accum': '00',

   'name':      'ivt',
   'long_name': 'integrated_vapor_transport',
   'level':     'Surface',
   'units':     'UNKNOWN',

   'grid': {
       'name': 'Global 0.5 Degree',
       'type' :   'LatLon',
       'lat_ll' : -90.0,
       'lon_ll' : 0.0,
       'delta_lat' :   0.5,
       'delta_lon' :   0.5,
       'Nlat' :      361,
       'Nlon' :      720,
   }
}

