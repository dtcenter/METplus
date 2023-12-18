"""
Mallory Row - SAIC at NOAA/NWS/NCEP/EMC
Designed to read in NASA OMI Total Column Ozone
"""

import sys
import os
import numpy as np
import netCDF4 as netcdf
import datetime

print("Python Script:\t" + repr(sys.argv[0]))

# Process script arguements
if len(sys.argv) != 3:
    print("Must specify the following elements: omi_file file_flag")
    sys.exit(1)
omi_file = os.path.expandvars(sys.argv[1]) 
if not os.path.exists(omi_file):
    print(f"OMI file {omi_file} does not exist, exit")
    sys.exit(1)
file_flag = sys.argv[2]
if file_flag not in ['fcst', 'obs']:
    print(f"File flag {file_flag} not valid (fcst, obs), exit")
    sys.exit(1)

print(f"Processing {omi_file} as {file_flag} data")

# Read in OMI data
omi_data = netcdf.Dataset(omi_file)
omi_StartUTC = omi_data['/HDFEOS/ADDITIONAL/FILE_ATTRIBUTES'].StartUTC
omi_StartUTC_dt = datetime.datetime.strptime(omi_StartUTC.split(':')[0],
                                             '%Y-%m-%dT%H')
omi_EndUTC = omi_data['/HDFEOS/ADDITIONAL/FILE_ATTRIBUTES'].EndUTC
omi_EndUTC_dt = datetime.datetime.strptime(omi_EndUTC.split(':')[0],
                                             '%Y-%m-%dT%H')
omi_delta_lat = float(eval(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].GridSpacing
)[0])
omi_delta_lon = float(eval(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].GridSpacing
)[1])
omi_ColumnAmountO3 = omi_data[
    '/HDFEOS/GRIDS/OMI Column Amount O3/Data Fields/ColumnAmountO3'
]
omi_lat_ll = float(eval(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].GridSpan
)[2])
omi_lon_ll = float(eval(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].GridSpan
)[0])
omi_nlat = int(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].NumberOfLatitudesInGrid
)
omi_nlon = int(
    omi_data['/HDFEOS/GRIDS/OMI Column Amount O3'].NumberOfLongitudesInGrid
)
omi_ColumnAmountO3_vals = omi_ColumnAmountO3[:]
omi_ColumnAmountO3_Units = omi_ColumnAmountO3.Units

# There is no geolocation data, so construct it ourselves.
latitude = np.arange(0., omi_nlat) * omi_delta_lat + omi_lat_ll + 0.125
longitude = np.arange(0., omi_nlon) * omi_delta_lon + omi_lon_ll + 0.125

# Set data up for MET
met_data = omi_ColumnAmountO3_vals.copy()
omi_MidPointUTC_dt = omi_StartUTC_dt + ((omi_EndUTC_dt - omi_StartUTC_dt)/2)
print(f"Data runs from {omi_StartUTC_dt:%Y%m%d_%H%M%S} to "
      +f"{omi_EndUTC_dt:%Y%m%d_%H%M%S}...setting valid date as "
      +f"{omi_EndUTC_dt:%Y%m%d_%H%M%S}")
met_data.attrs = {
    'valid': f"{omi_EndUTC_dt:%Y%m%d_%H%M%S}",
    'init': f"{omi_EndUTC_dt:%Y%m%d_%H%M%S}",
    'lead': '00',
    'accum': '00',
    'name': 'ColumnAmountO3',
    'standard_name': 'total_column_ozone',
    'long_name': 'total_column_ozone',
    'level': 'TotalColumn',
    'units': omi_ColumnAmountO3_Units,
    'grid': {
        'type': 'LatLon',
        'name': 'OMI Grid',
        'lat_ll': omi_lat_ll,
        'lon_ll': omi_lon_ll,
        'delta_lat': omi_delta_lat,
        'delta_lon': omi_delta_lon,
        'Nlat': omi_nlat,
        'Nlon': omi_nlon,
    }
}
attrs = met_data.attrs
