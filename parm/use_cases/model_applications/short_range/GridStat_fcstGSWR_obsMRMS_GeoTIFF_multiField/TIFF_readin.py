import sys
import os
import numpy as np
import datetime
import rioxarray


def get_variable_attributes(filename: str):
    """
    returns variable type, long name, and units based on filename
    """
    if 'CompRefl' in filename:
        return 'CompRefl', 'Composite Reflectivty', 'dBZ'
    if 'Vil' in filename:
        return 'VIL', 'Vertically Integrated Liquid', 'kg/m^2'
    if 'Et' in filename:
        return 'EchoTops', 'Echo Tops', 'kft'

    print(f"ERROR: Unsupported file: {filename}")
    sys.exit(1)

def get_variable_name(filename: str):
    var_name, *_ = get_variable_attributes(filename)
    return var_name

def open_file(filename: str):
    """
    Opens GSWR geotiff file using xarray and adds in some 
    additional metadata.
    """
    ds = rioxarray.open_rasterio(filename)
    ds = ds.to_dataset(name='band_data')
    ds['band'] = [get_variable_name(filename),]
    #rewrote this to also grab the lead (since its being calculated anyway)
    #and add it as a coord
    issue_time, valid_time, lead_time=parse_time(filename)
    ds = ds.assign_coords(issue_time=('issue_time', [issue_time,]))
    ds = ds.assign_coords(valid_time=('valid_time', [valid_time,]))
    ds = ds.assign_coords(lead_time=('lead_time', [lead_time,]))
    ds['band_data']=ds.band_data.expand_dims('valid_time')
    return ds

def parse_time(filename: str):
    """
    Returns issue time, valid time, and forecast lead in minutes from filename
    Example filename: /path/to/BlendedVilForecastMosaic_H=600.i241015010000.v241015110000.f0600.tif
    """
    try:
        _, issue_time, valid_time, *_ = os.path.basename(filename).split('.')
        issue_time = datetime.datetime.strptime(issue_time,'i%y%m%d%H%M%S')
        valid_time = datetime.datetime.strptime(valid_time,'v%y%m%d%H%M%S')
    except (TypeError, ValueError):
        print(f"ERROR: Could not parse time from filename: {filename}")
        sys.exit(1)

    lead = (valid_time-issue_time).total_seconds() / 60
    return issue_time, valid_time, lead

def decode_vil(vil8bitval: np.ndarray):
    vilval = np.zeros_like(vil8bitval)
    vilval[vil8bitval<=18] = ( vil8bitval[vil8bitval<=18] - 2 ) / 90.6591
    exparg = np.zeros_like(vil8bitval)
    exparg[vil8bitval > 18] = (vil8bitval[vil8bitval > 18]-83.9028)/38.8763
    vilval[vil8bitval > 18]= np.exp(exparg[vil8bitval > 18])
    vilval[vil8bitval<=5] = 0
    vilval[np.isnan(vil8bitval)]=np.nan
    return vilval

def get_time_attributes(filename):
    init, valid, lead = parse_time(filename)
    init = init.strftime('%Y%m%d_%H%M%S')
    valid = valid.strftime('%Y%m%d_%H%M%S')

    #if the lead is divisible by 60, then it has hours
    #we need to pull out that division and retain any minutes that are left
    #and format it all as a string
    if int(lead) / 60 > 0.9:
        lead = str(int(lead/60)).zfill(2) + str(int(lead) % 60).zfill(2) + '00'
    else:
        lead = '00'+ str(int(lead)) + '00'

    return init, valid, lead

def get_grid_attributes(ds):
    #we need to capture the deltas for lat and lon
    #as well as the ll's for each
    #while the current input has equal deltas for lat and lon,
    #a dynamic setting allows future flexibility

    lon_delta = float(abs(ds['x'][0] - ds['x'][1]))
    lat_delta = float(abs(ds['y'][0] - ds['y'][1]))
    lat_ll = float(min(ds['y'].values))
    lon_ll = float(min(ds['x'].values))
    return lon_delta, lat_delta, lat_ll, lon_ll

def get_met_data(ds):
    #change data values over to numpy array and open them to 
    #changes by creating a copy of the data

    data = np.array(ds.band_data.values.copy(),dtype='float32')

    if 'VIL' in name:
        data = decode_vil(data)

    met_data = data[0,0]

    #Need to change bad adata values; due to VIL needing adjustment to values,
    #bad data is anything over 81. All others are 255
    if 'VIL' in name:
        met_data[met_data>81.0]=-9999
    else:
        met_data[met_data==255]=-9999

    return met_data


# error if filepath was not provided as argument

if len(sys.argv) < 2:
    print("ERROR: Must supply filepath argument")
    sys.exit(1)

filepath = sys.argv[1]

# parse time and variable info from the filename

name, long_name, units = get_variable_attributes(filepath)
init, valid, lead = get_time_attributes(filepath)

# open file and read data and grid information

ds = open_file(filepath)

# get lat/lon info

lon_delta, lat_delta, lat_ll, lon_ll = get_grid_attributes(ds)

# get gridded data

met_data = get_met_data(ds)

attrs = {

        'valid': valid,
        'init': init,
        'name': name,
        'long_name': long_name,
        'lead': lead,
        'accum': '000000',
        'level': 'SURFACE',
        'units': units,

        'grid': {
            'name': 'LatitudeLongitude',
            'type': "LatLon",
            'lat_ll': lat_ll,
            'lon_ll': lon_ll,
            'delta_lat': lat_delta,
            'delta_lon': lon_delta,
            'Nlat': 4004,
            'Nlon': 8008,
            }
        }

print("Attributes:\t" + repr(attrs))
