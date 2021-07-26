# This script calculates potential vorticity (PV) from variables found in the GFS analysis model grib2 files. This script is originally from Taylor Mandelbaum, SBU. 
# Adjustments have been made by Lindsay Blank, NCAR.
# July 2020
###################################################################################################

import sys
import os
import re
import datetime as dt
from metpy import calc as mpcalc
from metpy.units import units
import xarray as xr
import cfgrib

###################################################################################################

def sept(input_file):

    # Vars
    grib_vars = ['t']

    # Load a list of datasets, one for each variable we want
    ds_list = [cfgrib.open_datasets(input_file,backend_kwargs={'filter_by_keys':{'typeOfLevel':'isobaricInhPa','shortName':v},'indexpath':''}) for v in grib_vars]

    # Flatten the list of lists to a single list of datasets
    ds_flat = [x.sel(isobaricInhPa=x.isobaricInhPa[x.isobaricInhPa>=100.0].values) for ds in ds_list for x in ds]

    # Merge the variables into a single dataset
    ds = xr.merge(ds_flat)

    # Add pressure
    ds['p'] = xr.DataArray(ds.isobaricInhPa.values,dims=['isobaricInhPa'],coords={'isobaricInhPa':ds.isobaricInhPa.values},attrs={'units':'hPa'}).broadcast_like(ds['t'])

    # Calculate saturation equivalent potential temperature
    ds['sept'] = mpcalc.saturation_equivalent_potential_temperature(ds['p'].metpy.convert_units('Pa'),ds['t'])

    met_data = ds['sept'].sel(isobaricInhPa=slice(float(os.environ.get('SEPT_LAYER_MAX_PRESSURE',1000.0)),float(os.environ.get('SEPT_LAYER_MIN_PRESSURE',100.0)))).mean(axis=0).values

    return met_data

###################################################################################################

input_file = os.path.expandvars(sys.argv[1])

data = sept(input_file) #Call function to calculate PV

met_data = data
met_data = met_data.astype('float64')

print("max", data.max())
print("min", data.min())

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
#lead, rem = divmod((valid-init).total_seconds(), 3600)


print(valid)
print(init)

attrs = {
    'valid': valid.strftime("%Y%m%d_%H%M%S"),
    'init':  init.strftime("%Y%m%d_%H%M%S"),
    'lead':  '00',
    'accum': '00',
        
    'name':      'sept',
    'long_name': 'saturation_equivalent_potential_temperature',
    'level':     'Surface',
    'units':     'K',
        
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
