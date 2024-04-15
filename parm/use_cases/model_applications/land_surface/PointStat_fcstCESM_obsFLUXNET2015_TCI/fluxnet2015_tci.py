"""
This python embedding code reads in the FLUXNET2015 NETCDF data
and passed to point_data. User need to pass on the season. 
User can change the verifying variable 
"""

import datetime
import glob
import metcalcpy.diagnostics.land_surface as land_sfc
import numpy as np 
import pandas as pd 
import os
import sys
import xarray as xr

# Extra debugging
DEBUG = os.getenv('FLUXNET_DEBUG',False)
DEBUG = bool(DEBUG)

# Climate model data typically doesn't include leap days, so it is excluded from observations by default
SKIP_LEAP = os.getenv('FLUXNET_SKIP_LEAP_DAYS',True)
SKIP_LEAP = bool(SKIP_LEAP)

# For the finer resolution data, what fraction at the finer resoultion should pass QC to use the daily value?
DAILY_QC_THRESH = os.getenv('FLUXNET_HIGHRES_QC_THRESH',0.8)
DAILY_QC_THRESH = float(DAILY_QC_THRESH)

# Number of days in an individual season to require
MIN_DAYS_SEASON = os.getenv('FLUXNET_MIN_DAYS_PER_SEASON',1)
MIN_DAYS_SEASON = int(MIN_DAYS_SEASON)

# For all seasons (i.e. DJF 2000 + DJF 2001 ... DJF XXXX) in the analysis period, how many total days per site?
MIN_DAYS_SITE = os.getenv('FLUXNET_MIN_DAYS_PER_SITE_ALL_SEASONS',10)
MIN_DAYS_SITE = int(MIN_DAYS_SITE)

# Pattern to use for searching for fluxnet files
#FILENAME_PATTERN = os.getenv('FLUXNET_RAW_FILENAME_PATTERN','AMF_*_DD_*.csv')
FILENAME_PATTERN = os.getenv('FLUXNET_RAW_FILENAME_PATTERN','FLX_*_DD_*.csv')
FILENAME_PATTERN = str(FILENAME_PATTERN)

def get_season_start_end(s,refdate):
  
  if s=='DJF':
    if refdate.strftime('%m') in ['01','02']:
      start = datetime.datetime((refdate.year)-1,12,1,0,0,0)
      end = datetime.datetime(refdate.year,3,1,0,0,0)
    else:
      start = datetime.datetime(refdate.year,12,1,0,0,0)
      end = datetime.datetime((refdate.year)+1,3,1,0,0,0)
  elif season=='MAM':
     start = datetime.datetime(refdate.year,3,1,0,0,0)
     end = datetime.datetime(refdate.year,6,1,0,0,0)
  elif season=='JJA':
     start = datetime.datetime(refdate.year,6,1,0,0,0)
     end = datetime.datetime(refdate.year,9,1,0,0,0)
  elif season=='SON':
     start = datetime.datetime(refdate.year,9,1,0,0,0)
     end = datetime.datetime(refdate.year,12,1,0,0,0)

  return start, end

# The script expects five arguments:
# raw_fluxnet_dir = Full path to the directory where the raw FLUXNET files are stored
# sfc_flux_varname = Field name in the raw_fluxnet_file to use when computing TCI
# soil_varname = Field name in the raw_fluxnet_file to use when computing TCI
# season = "DJF", "MAM", "JAJ", or "SON
if len(sys.argv) < 5:
  print("Must specify the following elements: ")
  print("raw_fluxnet_dir")
  print("sfc_flux_varname")
  print("soil_varname")
  print("season (DJF, MAM, JJA, or SON)")
  print("fluxnet_station_metadata_file")
  sys.exit(1)

# Store command line arguments
fndir = os.path.expandvars(sys.argv[1])
sfc_flux_varname = varCAM = sys.argv[2]
sfc_qc = sfc_flux_varname+'_QC'
soil_varname = varCLM = sys.argv[3]
soil_qc = soil_varname+'_QC'
season = sys.argv[4]
fluxnetmeta = sys.argv[5]
if season not in ['DJF','MAM','JJA','SON']:
  print("ERROR: UNRECOGNIZED SEASON IN fluxnet2015_tci.py")
  sys.exit(1)

# Dictionary mapping of which months go with which seasons
smap = {'DJF':[12,1,2],'MAM':[3,4,5],'JJA':[6,7,8],'SON':[9,10,11]}

# Read station information from static file, because the raw FLUXNET data does not contain
# required metadata like station latitude/longitude that is required by MET.
if not os.path.exists(fluxnetmeta):
  print("ERROR! FLUXNET METADATA FILE NOT PRESENT.")
  sys.exit(1)
else:
  sd = pd.read_csv(fluxnetmeta)

print("Starting Terrestrial Coupling Index Calculation for: "+season)
# Locate files at the input directory
if not os.path.exists(fndir):
  print("ERROR: FLUXNET INPUT DIRECTORY DOES NOT EXIST.")
  sys.exit(1)
else:
  fn_file_list = glob.glob(os.path.join(fndir,FILENAME_PATTERN))
  fn_stations = [os.path.basename(x).split('_')[1] for x in fn_file_list]
  if fn_stations == []:
    print("ERROR! NO FLUXNET DATA FOUND MATCHING FILE PATTERN "+FILENAME_PATTERN)
    sys.exit(1)
  else:
    if DEBUG:
      print("FOUND FLUXNET FILES FOR STATIONS:")
      print(fn_stations)
    else:
      print("fluxnet2015_tci.py INFO: FOUND DATA FOR %04d FLUXNET SITES." % (int(len(fn_stations))))
  
  # Let's try using a dictionary where the key is the site name and the value is the site file
  # in an effort to keep the site ID's and filenames aligned for now
  file_info = {station:file for station,file in tuple(zip(fn_stations,fn_file_list))}

# Loop over all stations we have data for and ensure we have the required metadata
# and required variables in the data file.
# If we don't have the metadata or required variables,
# remove the station and file from the analysis
dflist = []
discard = []
allfiles = len(file_info)
for station,stationfile in file_info.items():
  if not sd['station'].astype('str').str.contains(station).any():
    if DEBUG:
      print("WARNING! EXCLUDING SITE %s, NO METADATA FOUND IN fluxnetstations.csv" % (station))
    discard.append(station)
  df = pd.read_csv(stationfile)
  if (sfc_flux_varname in df.columns and soil_varname in df.columns and soil_qc in df.columns and sfc_qc in df.columns):
    dflist.append(df)
  else:
    if DEBUG:
      print("WARNING! EXCLUDING SITE %s, MISSING ONE OR MORE REQUIRED VARIABLES." % (station))
    discard.append(station)

# Reset the file info
final_files = {station:stationfile for station,stationfile in file_info.items() if station not in discard}
print("fluxnet2015_tci.py INFO: DISCARDED %04d SITES DUE TO MISSING METADATA OR VARIABLES." % (int(allfiles-len(final_files))))

# Create a MET dataframe
metdf = pd.DataFrame(columns=['typ','sid','vld','lat','lon','elv','var','lvl','hgt','qc','obs'])
metdf['sid'] = final_files.keys()
metdf['typ'] = ['ADPSFC']*len(metdf)
metdf['elv'] = [10]*len(metdf)
metdf['lvl'] = [10]*len(metdf)
metdf['var'] = ['TCI']*len(metdf)
metdf['qc'] = ['NA']*len(metdf)
metdf['hgt'] = [0]*len(metdf)
metdf['lat'] = [sd[sd['station']==s]['lat'].values[0] for s in final_files.keys()]
metdf['lon'] = [sd[sd['station']==s]['lon'].values[0] for s in final_files.keys()]

# Check and see what the length of metdf is here. If it is empty/zero, no FLUXNET data were found.
if len(metdf)==0:
  print("ERROR! FOUND NO FLUXNET DATA FOR FILENAME_PATTERN AND METADATA PROVIDED. "+\
         "PLEASE RECONFIGURE AND TRY AGAIN.")
  sys.exit(1)

# Because the time record for each station is not the same, the dataframes cannot be merged.
# Since the goal is a single value for each site for all dates that fall in a season, 
# the dataframes can remain separate.
for df,stn in tuple(zip(dflist,final_files.keys())):

  if DEBUG:
    print("==============================")
    print("PROCESSING STATION: %s" % (stn))

  # Length of all data
  alldays = len(df)
  if DEBUG:
    print("NUMBER OF DAYS AT THIS SITE: %04d" % (alldays))

  # Do some checking for missing data. FLUXNET says that -9999 is usecd for missing data.
  # Both the soil and surface variable must be present to compute TCI, so we only want
  # to retain days where both are not missing.
  df = df[(df[sfc_flux_varname]!=-9999.) & (df[soil_varname]!=-9999.)]
  if DEBUG:
    missdiff = int(alldays)-int(len(df))
    print("DISCARDED %04d DAYS WITH MISSING DATA (%3.2f %%)." % (int(alldays)-int(len(df)),((float(missdiff)/float(alldays))*100.0)))

  # Reset length of good data
  alldays = len(df)

  # Only save data with quality above the threshold and reset the index
  df = df[(df[sfc_qc].astype('float')>=DAILY_QC_THRESH)&(df[soil_qc].astype('float')>=DAILY_QC_THRESH)].reset_index()
  if DEBUG:
    print("DISCARDED %04d DAYS OF LOW QUALITY DATA FOR ALL SEASONS AT %s" % (int(alldays)-int(len(df)),stn))

  # Print the number of days remaining after filtering
  if DEBUG:
    print("NUMBER OF DAYS AFTER FILTERING AT THIS SITE: %04d" % (alldays))

  # Double check there's any valid data here
  if len(df) <= 0:
    if DEBUG:
      print("WARNING! NO DATA LEFT AFTER QC FILTERING.")
    metdf.loc[metdf['sid']==stn,'qc'] = '-9999'
    continue
 
  # Add datetime column
  df['datetime'] = pd.to_datetime(df['TIMESTAMP'],format='%Y%m%d')

  # Add a month column
  df['month'] = df['datetime'].dt.strftime('%m')

  # Add a season column
  df['season'] = [szn for mon in df['month'] for szn in smap if int(mon) in smap[szn]]

  # Add a station column
  df['station_id'] = [stn]*len(df)

  # Subset by the requested season
  df = df[df['season']==season]
  if DEBUG:
    print("TOTAL DAYS FOR %s AT THIS SITE: %04d" % (season,len(df)))
  
  # Double check there's any valid data here
  if len(df) <= 0:
    if DEBUG:
      print("WARNING! NO DATA FOR REQUESTED SEASON.")
    metdf.loc[metdf['sid']==stn,'qc'] = '-9999'
    continue

  # If the season is DJF, remove leap days from February if requested
  if season=='DJF' and SKIP_LEAP:
    withleap = len(df)
    df = df[~((df.datetime.dt.month == 2) & (df.datetime.dt.day == 29))]
    if DEBUG:
      print("REMOVED %03d LEAP DAYS." % (int(withleap)-int(len(df))))

  # Get the start and end of the season of the first year
  start, end = get_season_start_end(season,df['datetime'].iloc[0])

  # We know the start and end date of the first season. We assume there is data in every season forward
  # in time until we exceed the last date in the file.
  badyrs = []
  limit = df['datetime'].iloc[-1]
  while start <= limit:
    year = end.strftime('%Y')
    ndays = len(df[(df['datetime']>=start) & (df['datetime']<=(end-datetime.timedelta(days=1)))])
    if DEBUG:
      print("FOR "+season+" ENDING %s FOUND %04d DAYS." % (year,ndays))
   
    # Store the season ending years where there are not enough days 
    if ndays < MIN_DAYS_SEASON:
      badyrs.append(year)
   
    # Move to the same season in the next consecutive year 
    start = datetime.datetime((start.year)+1,start.month,start.day,0,0,0)
    end = datetime.datetime((end.year)+1,end.month,end.day,0,0,0)

  # Now actually remove the data we don't want to use
  for year in badyrs:
    start, end = get_season_start_end(season,datetime.datetime(int(year),1,1,0,0,0))
    if DEBUG:
      print("REMOVING "+season+" ENDING %s" % (year))
    df = df[(df['datetime']<start)|(df['datetime']>(end-datetime.timedelta(days=1)))]

  # Double check there are sufficient days at this site for all seasons
  if len(df)<MIN_DAYS_SITE:
    if DEBUG:
      print("ERROR! INSUFFICIENT DATA FOR COMPUTING TCI AT "+stn+" FOR "+season)
      print("NDAYS = %04d" % (int(len(df))))
    metdf.loc[metdf['sid']==stn,'qc'] = '-9999'
    continue
  else:
    if DEBUG:
      print("USING %04d DAYS OF DATA AT %s FOR %s" % (int(len(df)),stn,season))

  # Compute TCI
  metdf.loc[metdf['sid']==stn,'obs'] = land_sfc.calc_tci(df[soil_varname],df[sfc_flux_varname])

  # Set the valid time as the first time in the record for this site
  metdf.loc[metdf['sid']==stn,'vld'] = pd.to_datetime(df['TIMESTAMP'].iloc[0],format='%Y%m%d').strftime('%Y%m%d_%H%M%S')

# At this point, 'qc' should be '-9999' anywhere we discarded a site due to insufficient data above. 
# Remove these here.
print("fluxnet2015_tci.py INFO: REMOVING %04d SITES DUE TO LACK OF DATA." % (int(len(metdf[metdf['qc']=='-9999']))))
metdf = metdf[metdf['qc']=='NA']
#print(metdf)

# Convert to the object MET needs
point_data = metdf.values.tolist()
#print(point_data)
