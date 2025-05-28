"""
This script reads AMDAR hourly netcdf files, computes PBLH, and sends 11-column ascii table to MET for point-stat
An airport csv file is read in containing lat, lon, gnd height, and rbox for each airport
See accompanying PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.conf for settings and passing in env variables here
Jason M. English, May 2025
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import netCDF4 as nc
import math
from typing import Tuple
from collections import defaultdict
import warnings

# Suppress non-critical warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

print("Python Script:\t" + repr(sys.argv[0]))

##
##  input file specified on the command line
##  load the data into the numpy array
##

# ---------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# ---------------------------------------------------------------------------
val_time = os.environ.get('VAL_TIME') #'20220701_200000' #os.environ.get('VAL_TIME')
sf_include = os.environ.get('SOUNDING_FLAG') #'ALL' #os.environ.get('SOUNDING_FLAG') # 'ASCENTS', 'DESCENTS', or 'ALL'
airport_file = os.environ.get('AIRPORT_FILE') # airport file template

# ---------------------------------------------------------------------------
# CONFIGURATION & PHYSICS CONSTANTS
# ---------------------------------------------------------------------------
CONFIG = {
    "alt_dp": 4,
    "alt_adj_flag": True,
    "pt_delta": 1.25,
    "altmax_sfc": 200.,
    "gap_max": 400.,
    "gap_max_denom": 20.,
    "cbrn": 0.5,
    "zs": 40.,
    "ustar": 0.3,
    "beta": 100.,
}
PHYSICS = {
    "SLP": 101325.0,
    "GRAV": 9.80665,
    "M_MASS": 0.0289644,
    "R0": 8.31432,
    "LR": 0.0065,
    "H0": 44307.694
}
PHYSICS["EXPON"] = (-PHYSICS["GRAV"] * PHYSICS["M_MASS"]) / (PHYSICS["R0"] * -PHYSICS["LR"])

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------
def load_hourly_netcdf(filepath: Path) -> dict:
    """ Load raw AMDAR netcdf file (1d arrays of all data that hour). """
    with nc.Dataset(filepath, 'r') as ncf:
        data = {
            'tailNumber': np.array(ncf['tailNumber'][:]),
            'altitude': np.array(ncf['altitude'][:]),
            'latitude': np.array(ncf['latitude'][:]),
            'longitude': np.array(ncf['longitude'][:]),
            'temperature': np.array(ncf['temperature'][:]),
            'windSpeed': np.array(ncf['windSpeed'][:]),
            'windDir': np.array(ncf['windDir'][:]),
            'timeObs': np.array(ncf['timeObs'][:]),
            'sounding_flag': np.array(ncf['sounding_flag'][:])
        }
    return data

def sf_mask(sf_value: int) -> bool:
    """ Return sounding flag mask so we can process the desired flights. """
    if sf_value == 0:   # discard cruising flights
        return False
    if sf_include == "ALL":
        return True
    if sf_include == "ASCENTS":
        return sf_value == 1
    if sf_include == "DESCENTS":
        return sf_value == -1

def get_tail_number_string(tn_array: np.ndarray) -> np.ndarray:
    """Convert 9-character tail number array to a concatenated string."""
    tnc = np.char.array(tn_array.astype(str))
    return tnc[:, 0] + tnc[:, 1] + tnc[:, 2] + tnc[:, 3] + tnc[:, 4] + tnc[:, 5] + tnc[:, 6] + tnc[:, 7] + tnc[:, 8]

def compute_pressure(alt: np.ndarray, ground_level: float) -> np.ndarray:
    """Compute pressure (Pa) using the hypsometric formula."""
    z = alt + ground_level
    return PHYSICS["SLP"] * (1 - z / PHYSICS["H0"]) ** PHYSICS["EXPON"]

def compute_potential_temperature(temp: np.ndarray, pressure: np.ndarray) -> np.ndarray:
    """Compute potential temperature (K)."""
    return temp * (PHYSICS["SLP"] / pressure) ** 0.286

# ---------------------------------------------------------------------------
# PBLH COMPUTATION METHODS
# ---------------------------------------------------------------------------
def compute_pblh_ti(alt: np.ndarray, pt: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> Tuple[float, float, float]:
    """ 
    Compute PBLH via the theta increase (TI) method.
    Returns: (pblh, lat_pblh, lon_pblh)
    """
    valid = alt < CONFIG["altmax_sfc"]  # To find pt_min consider only alt below altmax_sfc
    if not np.any(valid):
        return np.nan, np.nan, np.nan
    pt_min = np.nanmin(np.where(valid, pt, np.nan))
    if pt_min <= 0 or pt_min >= 3040:
        return np.nan, np.nan, np.nan
    try:
        pt_min_index = np.where(pt == pt_min)[0][0]
    except IndexError:
        return np.nan, np.nan, np.nan
    # now mask out the profile below pt_min, and search above it for pt_delta
    alt_ti = alt.copy()
    alt_ti[:pt_min_index] = np.nan
    pt_ti = pt.copy()
    pt_ti[:pt_min_index] = np.nan
    pt_target = pt_min + CONFIG['pt_delta']
    inds = np.where(pt_ti >= pt_target)[0]
    if inds.size == 0 or inds[0] == 0:
        return np.nan, np.nan, np.nan
    pblh_index = inds[0]
    # discard this PBLH value if gap between data points is too big
    alt_gap = alt_ti[pblh_index] - alt_ti[pblh_index - 1]
    if alt_gap > CONFIG["gap_max"] + alt_ti[pblh_index] / CONFIG["gap_max_denom"]:
        return np.nan, np.nan, np.nan
    i1, i0 = inds[0], inds[0] - 1
    # interpolate between data points to get PBLH
    pblh = float(np.interp(pt_target, pt_ti[i0:i1+1], alt_ti[i0:i1+1]))
    lat_pblh = float(np.interp(pt_target, pt_ti[i0:i1+1], lat[i0:i1+1]))
    lon_pblh = float(np.interp(pt_target, pt_ti[i0:i1+1], lon[i0:i1+1]))
    return pblh, lat_pblh, lon_pblh

def compute_pblh_br(alt: np.ndarray, pt: np.ndarray, lat: np.ndarray, lon: np.ndarray,
                    ws: np.ndarray, wd: np.ndarray) -> Tuple[float, float, float]:
    """ 
    Compute PBLH via the Critical Bulk Richardson Number (CBRN) method.
    Returns: (pblh, lat_pblh, lon_pblh)
    """
    br_sfc_ind = np.argmin(np.abs(alt - CONFIG["zs"])) # Find data point closest to zs
    if alt[br_sfc_ind] > CONFIG["altmax_sfc"]:  # Make sure it's not too far from zs
        return np.nan, np.nan, np.nan
    if np.isnan(ws[br_sfc_ind]) or np.isnan(pt[br_sfc_ind]) or np.isnan(wd[br_sfc_ind]):
        return np.nan, np.nan, np.nan
    wd_math = (270.0 - wd) % 360.0
    u = ws * np.cos(np.radians(wd_math))
    v = ws * np.sin(np.radians(wd_math))
    u_sfc, v_sfc, pt_sfc = u[br_sfc_ind], v[br_sfc_ind], pt[br_sfc_ind]
    brn_prev, alt_prev, lat_prev, lon_prev = None, None, None, None
    for i in range(br_sfc_ind+1, len(alt)):
        if np.isnan(ws[i]) or np.isnan(pt[i]) or np.isnan(alt[i]):
            continue
        brn = (PHYSICS["GRAV"] / pt_sfc) * (pt[i] - pt_sfc) * (alt[i] - CONFIG["zs"]) / ( 
              (u[i] - u_sfc)**2 + (v[i] - v_sfc)**2 + CONFIG['beta'] * CONFIG['ustar']**2)
        if brn > CONFIG["cbrn"]:
            if i == 0 or brn_prev is None:
                return alt[i], lat[i], lon[i]
            # discard this PBLH value if gap between data points is too big
            alt_gap = alt[i] - alt_prev
            if alt_gap > CONFIG["gap_max"] + alt[i] / CONFIG["gap_max_denom"]:
                return np.nan, np.nan, np.nan
            # interpolate between data points to get PBLH
            pblh = float(np.interp(CONFIG["cbrn"], [brn_prev, brn], [alt_prev, alt[i]]))
            lat_pblh = float(np.interp(CONFIG["cbrn"], [brn_prev, brn], [lat_prev, lat[i]]))
            lon_pblh = float(np.interp(CONFIG["cbrn"], [brn_prev, brn], [lon_prev, lon[i]]))
            return pblh, lat_pblh, lon_pblh
        brn_prev, alt_prev, lat_prev, lon_prev = brn, alt[i], lat[i], lon[i]
    return np.nan, np.nan, np.nan

# ---------------------------------------------------------------------------
# FLIGHT PROCESSING
# ---------------------------------------------------------------------------
def process_flight(tail: str, indices: np.ndarray, data: dict,
                   ground_level: float) -> dict:
    """
    Process one flight/tail number. Sort the data points to be ascending. Compute PBLH via TI and BR methods.
    Returns: PBLH, lat, lon for that tail number.
    """
    flight_data = {k: np.take(data[k], indices, axis=0) for k in data}
    sort_order = np.argsort(flight_data['altitude'])
    for k in flight_data:
        flight_data[k] = flight_data[k][sort_order]
    alt = flight_data['altitude'] - ground_level
    if CONFIG["alt_adj_flag"] and np.nanmin(alt) < 0:  # if minimum altitude is negative, adjust to zero
        offset = float(np.trunc(np.nanmin(alt)))
        alt -= offset
    pres = compute_pressure(alt, ground_level)
    pt = compute_potential_temperature(flight_data['temperature'], pres)
    pblh_ti, lat_ti, lon_ti = compute_pblh_ti(alt, pt, flight_data['latitude'], flight_data['longitude'])
    pblh_br, lat_br, lon_br = compute_pblh_br(alt, pt, flight_data['latitude'], flight_data['longitude'],
                                               flight_data['windSpeed'], flight_data['windDir'])
    return {'tail_number': tail,
            'pblh_ti': pblh_ti, 'lat_ti': lat_ti, 'lon_ti': lon_ti,
            'pblh_br': pblh_br, 'lat_br': lat_br, 'lon_br': lon_br}

# ---------------------------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------------------------
def create_dataframe(sid_all, var_all, lat_all, lon_all, elev_all, pblh_all, val_time: str) -> pd.DataFrame:
    """ Create an 11-column dataframe in the format required by MET. """
    #   (1)  string:  Message_Type ('ADPSFC')
    #   (2)  string:  Station_ID (AIRPORT)
    #   (3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
    #   (4)  numeric: Lat(Deg North)
    #   (5)  numeric: Lon(Deg East)
    #   (6)  numeric: Elevation(msl) 
    #   (7)  string:  Var_Name(or GRIB_Code)
    #   (8)  numeric: Level
    #   (9)  numeric: Height(msl or agl)
    #   (10) string:  QC_String
    #   (11) numeric: Observation_Value
    df = pd.DataFrame({
        'typ': ['ADPSFC']*len(sid_all), 'sid': sid_all, 'vld': [val_time]*len(sid_all),
        'lat': lat_all, 'lon': lon_all, 'elv': elev_all, 'var': var_all,
        'lvl': [0]*len(sid_all), 'hgt': [0]*len(sid_all), 'qc': ['AMDAR']*len(sid_all), 'obs': pblh_all
    })
    return df[df['obs'].notna()]

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
# Load hourly AMDAR netcdf file
infile = Path(sys.argv[1]) if len(sys.argv)>1 else Path('221822000q.cdf')  # remove the end after debugging
data = load_hourly_netcdf(infile)

# Convert tail 2d char array to 1d string array
tn_str = get_tail_number_string(data['tailNumber'])
data['tailNumber'] = tn_str

# Apply sounding flag mask to the whole file (remove cruising flights, and asc/desc if specified)
sf = data['sounding_flag']
mask_sf = np.array([sf_mask(val) for val in sf])
for k in data:
    data[k] = data[k][mask_sf]

# Load airport csv file
airport_df = pd.read_csv(airport_file + ".csv", index_col=0)
airports = airport_df.index.tolist()

# Create empty lists to append
sid_all, var_all, lat_all, lon_all, elev_all, pblh_all = [], [], [], [], [], []

# Loop over airports, masking that lat/lon box for each
for airport in airports:
    code = airport_df.loc[airport, 'airport_code']
    lat0 = airport_df.loc[airport, 'lat_degN']
    lon0 = airport_df.loc[airport, 'lon_degE']
    gnd0 = airport_df.loc[airport, 'hgt_m_MSL']
    r0 = airport_df.loc[airport, 'airport_radius_deg']

    mask_box = ((data['latitude'] > lat0 - r0) & (data['latitude'] < lat0 + r0) &
                (data['longitude'] > lon0 - r0) & (data['longitude'] < lon0 + r0))

    # Filter tail numbers within box and remove NaNs
    filtered_tn = np.where(mask_box, data['tailNumber'], "nan")
    valid_tails = np.array([t for t in np.unique(filtered_tn) if isinstance(t, str) and t.lower() != "nan"])

    print(f"\n==Processing airport {airport} ({code}): {len(valid_tails)} flights==")

    if valid_tails.size == 0:
        continue

    # Loop through all flights (tail numbers) within the lat/lon box of this airport
    for tail in valid_tails:
        indices = np.where(filtered_tn == tail)[0]
        print(f"Processing flight {tail} with {len(indices)} points.")
        if len(indices) < CONFIG["alt_dp"]:
             print(f"Flight {tail}: insufficient data points ({len(indices)}). Skipping.")
             continue

        flight_result = process_flight(str(tail), indices, data, gnd0)

        # Append dataframe row with TI method if successful
        if not np.isnan(flight_result['pblh_ti']):
            sid_all.append(code)
            var_all.append('HPBL_TI')
            elev_all.append(gnd0)
            lat_all.append(flight_result['lat_ti'])
            lon_all.append(flight_result['lon_ti'])
            pblh_all.append(flight_result['pblh_ti'])

        # Append dataframe row with BR method if successful
        if not np.isnan(flight_result['pblh_br']):
            sid_all.append(code)
            var_all.append('HPBL_BR')
            elev_all.append(gnd0)
            lat_all.append(flight_result['lat_br'])
            lon_all.append(flight_result['lon_br'])
            pblh_all.append(flight_result['pblh_br'])

point_data = create_dataframe(sid_all, var_all,
                             lat_all, lon_all,
                             elev_all, pblh_all,
                             val_time)

pd.set_option('display.max_rows', None)
print(point_data)
print("     point_data: Data Length:\t" + repr(len(point_data)))
print("     point_data: Data Type:\t" + repr(type(point_data)))

point_data = point_data.values.tolist()

#except NameError:
#    print("Can't find the input file")
