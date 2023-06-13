'''
This script reads AMDAR hourly netcdf files, computes PBLH, and sends 11-column ascii table to MET for point-stat
See accompanying PointStat_python_embedding_obs_amdar_pblh.conf for settings and passing in env variables here 
Jason M. English, May 2023
'''

import os
import sys
import pandas as pd
import numpy as np
import netCDF4 as nc
#from met_point_obs import convert_point_data

# silence this annoying warning about numpy bool being deprecated in favor of python bool
from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

########################################################################

print("Python Script:\t" + repr(sys.argv[0]))

##
##  input file specified on the command line
##  load the data into the numpy array
##

loc_name = os.environ.get('AIRPORT') # "DENVER", "DALLAS", "BOSTON", "MINNEAPOLIS" # airport, not city
sf_include = os.environ.get('SOUNDING_FLAG')  # what sounding flags to include: ASC or DESC
pt_delta = float(os.environ.get('PT_DELTA')) #1.25  # potential temperature delta that triggers PBLH calculation (K)
val_time = os.environ.get('VAL_TIME')  # valid time for this call (nearest hour)
rbox = 2.0   #  +/- deg;  set bigger than you need so MET mask can cut from that later
alt_base = 200.  # highest altitude where the alt min is looked for to get base potential temperature
gap_max = 400.  # maximum allowable altitude gap (m) between the computed PBLH and the altitude of the data point below it (gap_max + pblh/20)
alt_dp = 4    # minimum number of data points for the flight to be considered
alt_adj = "yes"  # adjust minimum altitude to be >= 0 yes or no
out_rej = 2  # number of sigmas to trigger outlier reject

if loc_name == "DENVER":    
   gnd0 = 5300.*0.3048   # surface elevation at location (msl);  DIA is at 5430ft but up to 300 feet lower than that within 500m of the airport
   lat0 = 39.856
   lon0 = -104.6764
elif loc_name == "DALLAS":
   gnd0 = 550.*0.3048
   lat0 = 32.8998
   lon0 = -97.0403
elif loc_name == "MINNEAPOLIS":
   gnd0 = 840.*0.3048
   lat0 = 44.8848
   lon0 = -93.2223
elif loc_name == "BOSTON":
   gnd0 = 20.*0.3048  
   lat0 = 42.3656
   lon0 = -71.0096

# convert tail number array to readable character string
def get_tn(tn):  
  tnc = tn.astype(str)   # convert to character string
  tnc = np.char.array(tnc)   # removes whitespace and allows vectorized string operations
  tnc_splice = tnc[:,0]+tnc[:,1]+tnc[:,2]+tnc[:,3]+tnc[:,4]+tnc[:,5]+tnc[:,6]+tnc[:,7]+tnc[:,8]   # tail number spliced into a single string
  return tnc_splice
 
if len(sys.argv) != 2:
   print("ERROR: calc_amdar_pblh.py -> Must specify exactly one input file.")
   sys.exit(1)

# Read the input file as the first argument
input_file = os.path.expandvars(sys.argv[1])
try:
   print("Input File:\t" + repr(input_file))
   ncf = nc.Dataset(input_file)
    
   tn = ncf['tailNumber'][:]  
   sf = ncf['sounding_flag'][:]  # -1=descent, 0=cruising, 1=ascent 
   t = ncf['temperature'][:]
   alt = ncf['altitude'][:] - gnd0   # subtract surface height to get AGL
   lat = ncf['latitude'][:]
   lon = ncf['longitude'][:]
   ncf.close()

   # set to NaN if cruising flight (not ascent or descent)
   t = np.where(sf == 0, np.nan, t)
   if sf_include == "ASC":
     t = np.where(sf == -1, np.nan, t)  # discard descents
   if sf_include == "DESC":
     t = np.where(sf == 1, np.nan, t)  # discard ascents
 
   # set to NaN if outside alt, lat/lon  bounds
   t = np.where((lat > lat0-rbox) & (lat < lat0+rbox) & (lon > lon0-rbox ) & (lon < lon0+rbox), t, np.nan)
 
   # convert tail number array to readable character string
   tns = get_tn(tn)

   # set tail number array to NaN wherever temperature array is NaN
   tns = np.where(np.isnan(t), np.nan, tns)
   
   # get unique tail numbers within the specified lat/lon range
   tn_list = np.unique(tns)
   nflight = tn_list.size
   
   # Create arrays for saving PBLH and other fields for each flight
   pblh = np.full([nflight],np.nan)
   pblh_o = np.full([nflight],np.nan)   #pblh interpolated with outliers excluded
   pt_min = np.full([nflight],np.nan)  # potential temperature minimum 
   lat_avg = np.full([nflight],np.nan)  
   lon_avg = np.full([nflight],np.nan) 

   for i,tn_name in enumerate(tn_list):  #loop through tail numbers

      if tn_name != "nan":
        tn_arr = np.where(tns == tn_name, tns, 'null')   # set array to null if it doesn't  this tail number
        tn_ind = np.where(tns == tn_arr)   # get list of indices 
      
        # take the elements from each array ing only this flight (via the specified indices)
        tn_i  = np.squeeze(np.take(tn_arr, tn_ind)) 
        sf_i  = np.squeeze(np.take(sf, tn_ind)) 
        t_i   = np.squeeze(np.take(t, tn_ind))
        alt_i = np.squeeze(np.take(alt, tn_ind))
        lat_i = np.squeeze(np.take(lat, tn_ind))
        lon_i = np.squeeze(np.take(lon, tn_ind))
      
        # only include ascents/descents that have enough altitude/temperature data
        if (np.amin(alt_i) < alt_base) & (np.amax(alt_i) > alt_base) & (alt_i.size >= alt_dp):
  
          # sort altitude and temperature arrays to be ascending
          sort_inds = np.argsort(alt_i)
          t_d = np.copy(t_i[sort_inds])
          alt_d = np.copy(alt_i[sort_inds])
          lat_d = np.copy(lat_i[sort_inds])
          lon_d = np.copy(lon_i[sort_inds])

          # adjust altitude minimum to zero if it's negative
          if alt_adj == "yes":
            if np.nanmin(alt_d) < 0:
              alt_d[:] = alt_d[:] - np.nanmin(alt_d)

          # convert altitude to pressure 
          slp = 101325.  # Sea level pressure (Pa)
          expon = (-9.80665 *0.0289644) / (8.31432 * -0.0065)
          p_d = slp * (1. - (alt_d + gnd0)/44307.694)**expon   # needs to be pressure altitude (add ground ht) 
    
          # convert temperature to potential temperature
          pt_d = np.copy(t_d)
          pt_d[:] = t_d[:] * (slp/p_d[:])**0.286
  
          # Find minimum potential temperature that occurs below the specified altitude alt_base
          pt_min[i] = np.nanmin(np.where(alt_d < alt_base, pt_d, np.nan))
          pt_min_ind = np.where(pt_d == pt_min[i])[0][0]  # find array indexing that value

          # Only move forward if minimum PT is within a reasonable range
          if (pt_min[i] > 0) & (pt_min[i] < 3040): 

          # consider only potential temperature values above where pt_min was found when searching for pblh
            alt_d[:pt_min_ind] = np.nan
            pt_d[:pt_min_ind] = np.nan
            pt_dif = np.copy(pt_d)
            pt_dif[:] = pt_d[:] - pt_min[i] 
  
            # determine lowest height that exceeds the specified pt_delta (K)
            if np.nanmax(pt_d) >= (pt_min[i]+pt_delta):    # make sure it exists in this profile
              pblh_alt = np.nanmin(np.where(pt_d >= (pt_min[i]+pt_delta),alt_d, np.nan))
              pblh_ind = np.where(alt_d == pblh_alt)[0][0]   # altitude index where pblh is found
  
              # only include pblh if the altitude below it isn't too big of a gap
              if pblh_ind.size == 1:   # make sure only 1 index was found
                alt_gap = alt_d[pblh_ind]-alt_d[pblh_ind-1]
  
                if alt_gap < (gap_max + alt_d[pblh_ind]/20.):
                  pblh[i] = alt_d[pblh_ind]
       
                  # linear interpolate PBLH between this data point and the one below it
                  pblh[i] = np.interp((pt_min[i]+pt_delta), pt_d[pblh_ind-1:pblh_ind+1], alt_d[pblh_ind-1:pblh_ind+1]) 
  
                  # compute lat/lon for this flight by taking the avg lat/lon coordiantes over the flight
                  lat_avg[i] = np.average(lat_i)
                  lon_avg[i] = np.average(lon_i)

          print("tn=", tn_i[0], ", sf=", sf_include, ", n=", pt_d.size, ", pt_min (K)=", np.array2string(pt_min[i]), 
                ", pblh interp (m)=", np.array2string(pblh[i]), ", pblh closest (m)=", np.array2string(pblh[i])) 

########################################################################

   # Now that all flights at this hour have been computed, conduct statistics and averaging on them
   if np.count_nonzero(~np.isnan(pblh)) > 0:
     pblh_o[:] = np.where((pblh >= np.nanmean(pblh)-float(out_rej)*np.nanstd(pblh)) & 
                          (pblh <= np.nanmean(pblh)+float(out_rej)*np.nanstd(pblh)), pblh, np.nan)

     # only include flights with a computed PBLH value
     lat_avg[np.isnan(pblh_o)] = np.nan
     lon_avg[np.isnan(pblh_o)] = np.nan
     pblh_o = pblh_o[~np.isnan(pblh_o)] 
     lat_avg= lat_avg[~np.isnan(lat_avg)] 
     lon_avg= lon_avg[~np.isnan(lon_avg)] 

   # Read and format the input 11-column observations:
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

   point_data = pd.DataFrame({'typ':'ADPSFC', 'sid':loc_name, 'vld':val_time,
                               'lat':lat_avg, 'lon':lon_avg, 'elv':gnd0, 'var':'HPBL',
                               'lvl':0, 'hgt':0, 'qc':'AMDAR', 'obs':pblh_o}).values.tolist()
     
   print(point_data)
   print("     point_data: Data Length:\t" + repr(len(point_data)))
   print("     point_data: Data Type:\t" + repr(type(point_data)))
   #print(point_data.values.tolist())
   #met_point_data = convert_point_data(point_data.values.tolist())
   #print(" met_point_data: Data Type:\t" + repr(type(met_point_data)))
   
except NameError:
    print("Can't find the input file")
    sys.exit(1)
