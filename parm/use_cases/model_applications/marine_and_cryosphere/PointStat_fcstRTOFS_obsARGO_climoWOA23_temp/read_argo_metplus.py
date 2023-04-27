#! /usr/bin/env python3

import sys
import os
import datetime

import netCDF4
import numpy
from numpy.ma import is_masked

# set to true to output more info
DEBUG = False

# constant values that will be used for every observation
MESSAGE_TYPE = 'ARGO'
ELEVATION = 'NA'
LEVEL = 'NA'
QC_STRING = '1'

# skip data if PRES_ADJUSTED_ERROR value is greater than this value
MAX_PRESSURE_ERROR = 20

"""Read and format the input 11-column observations:
(1)  string:  Message_Type
(2)  string:  Station_ID
(3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
(4)  numeric: Lat(Deg North)
(5)  numeric: Lon(Deg East)
(6)  numeric: Elevation(msl)
(7)  string:  Var_Name(or GRIB_Code)
(8)  numeric: Level
(9)  numeric: Height(msl or agl)
(10) string:  QC_String
(11) numeric: Observation_Value
"""


def get_string_value(var):
    """!Get string value from NetCDF variable. The string variables are stored
    as bytes, so decode them and strip off any whitespace before or after.

    @param var NetCDF variable to read
    @returns string value from variable
    """
    return var[:].tobytes().decode('utf-8').strip()


def get_val_check_qc(nc_obj, field_name, idx_p, idx_l=None, error_max=None):
    """!Get field value unless quality control checks do not pass.
    The conditions to skip data are as follows:
    1) If {field_name}_QC is masked.
    2) If {field_name} is masked.
    3) If {field_name}_QC value is not equal to 1 (recommended from ARGO docs).
    4) If error_max is set, skip if {field_name}_ERROR is not masked and less
    than the error_max value.

    @param nc_obj NetCDF object
    @param field_name name of field to read
    @param idx_p index of profile (1st dimension of data)
    @param idx_l (optional) index of level (2nd dimension of data). Defaults to
    None which assumes field is not 2D
    @param error_max (optional) value to compare to {field_name}_ERROR. Skip if
    error value is less than this value
    @returns numpy.float64 field value if all QC checks pass or None
    """
    if idx_l is None:
        qc = nc_obj.variables[f'{field_name}_QC'][idx_p]
        field = nc_obj.variables[field_name][idx_p]
        data_str = f'{field_name}[{idx_p}]'
    else:
        qc = nc_obj.variables[f'{field_name}_QC'][idx_p][idx_l]
        field = nc_obj.variables[field_name][idx_p][idx_l]
        data_str = f'{field_name}[{idx_p}][{idx_l}]'

    qc_mask = is_masked(qc)
    field_mask = is_masked(field)

    if qc_mask:
        if DEBUG:
            print(f"Skip {data_str} {field_name}_QC is masked")
        return None

    if field_mask:
        if DEBUG:
            print(f"Skip {data_str} {field_name} is masked")
        return None

    if int(qc) != 1:
        if DEBUG:
            print(f"Skip {data_str} {field_name}_QC value ({int(qc)}) != 1")
        return None

    if error_max:
        err = nc_obj.variables.get(f'{field_name}_ERROR')
        if err:
            err = err[idx_p] if idx_l is None else err[idx_p][idx_l]
            if not is_masked(err) and err > error_max:
                print(f"Skip {data_str} {field_name}_ERROR > {error_max}")
                return None

    return numpy.float64(field)


def get_valid_time(ref_dt, nc_obj, idx):
    """!Get valid time by adding julian days to the reference date time.

    @param ref_dt Datetime object of reference date time
    @param nc_obj NetCDF object
    @param idx index of profile to read
    @returns string of valid time in YYYYMMDD_HHMMSS format
    """
    julian_days = nc_obj.variables['JULD'][idx]
    day_offset = datetime.timedelta(days=float(julian_days))
    valid_dt = ref_dt + day_offset
    return valid_dt.strftime('%Y%m%d_%H%M%S')


def get_lat_lon(nc_obj, idx):
    """!Read latitude and longitude values from NetCDF file at profile index.

    @param nc_obj NetCDF object
    @param idx index of profile to read
    @returns tuple of lat and lon values as floats
    """
    return (numpy.float64(nc_obj.variables['LATITUDE'][idx]),
            numpy.float64(nc_obj.variables['LONGITUDE'][idx]))


if len(sys.argv) < 2:
    print(f"ERROR: {__file__} - Must provide at least 1 input file argument")
    sys.exit(1)

is_ok = True
input_files = []
for arg in sys.argv[1:]:
    if arg.endswith('debug'):
        print('Debugging output turned on')
        DEBUG = True
        continue

    input_file = os.path.expandvars(arg)
    if not os.path.exists(input_file):
        print(f'ERROR: Input file does not exist: {input_file}')
        is_ok = False
        continue

    input_files.append(input_file)

if not is_ok:
    sys.exit(1)

print(f'Number of input files: {len(input_files)}')

point_data = []
for input_file in input_files:
    print(f'Processing file: {input_file}')

    nc_in = netCDF4.Dataset(input_file, 'r')

    # get reference date time
    time_str = get_string_value(nc_in.variables['REFERENCE_DATE_TIME'])
    reference_date_time = datetime.datetime.strptime(time_str, '%Y%m%d%H%M%S')

    # get number of profiles and levels
    num_profiles = nc_in.dimensions['N_PROF'].size
    num_levels = nc_in.dimensions['N_LEVELS'].size

    new_point_data = []
    for index_p in range(0, num_profiles):
        # check QC and mask of JULD to skip profiles with bad time info
        if get_val_check_qc(nc_in, 'JULD', index_p) is None:
            continue

        valid_time = get_valid_time(reference_date_time, nc_in, index_p)
        station_id = get_string_value(
            nc_in.variables['PLATFORM_NUMBER'][index_p]
        )
        lat, lon = get_lat_lon(nc_in, index_p)

        # loop through levels
        for index_l in range(0, num_levels):
            # read pressure data to get height in meters of sea water (msw)
            height = get_val_check_qc(nc_in, 'PRES_ADJUSTED', index_p, index_l,
                                      error_max=MAX_PRESSURE_ERROR)
            if height is None:
                continue

            # get temperature and ocean salinity values
            for var_name in ('TEMP', 'PSAL'):
                observation_value = get_val_check_qc(nc_in,
                                                     f'{var_name}_ADJUSTED',
                                                     index_p, index_l)
                if observation_value is None:
                    continue

                point = [
                    MESSAGE_TYPE, station_id, valid_time, lat, lon, ELEVATION,
                    var_name, LEVEL, height, QC_STRING, observation_value,
                ]
                new_point_data.append(point)
                if DEBUG:
                    print(', '.join([str(val) for val in point]))

    point_data.extend(new_point_data)
    nc_in.close()

print("     point_data: Data Length:\t" + repr(len(point_data)))
print("     point_data: Data Type:\t" + repr(type(point_data)))
