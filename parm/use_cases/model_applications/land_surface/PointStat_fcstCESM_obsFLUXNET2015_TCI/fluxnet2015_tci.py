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

# For the finer resolution data, what percentage at the finer resoultion should pass for the daily data?
DAILY_QC_THRESH=0.8
# TODO: This needs to be evaluated PER season, not on all days in all DJF's, for example
MIN_DAYS_SEASON=80
MIN_DAYS_SITE=450

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

# The script expects four arguments:
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
  sys.exit(1)

# Store command line arguments
fndir = os.path.expandvars(sys.argv[1])
sfc_flux_varname = varCAM = sys.argv[2]
sfc_qc = sfc_flux_varname+'_QC'
soil_varname = varCLM = sys.argv[3]
soil_qc = soil_varname+'_QC'
season = sys.argv[4]
if season not in ['DJF','MAM','JJA','SON']:
  print("ERROR: UNRECOGNIZED SEASON IN tci_from_cesm.py")
  sys.exit(1)

# Dictionary mapping of which months go with which seasons
smap = {'DJF':[12,1,2],'MAM':[3,4,5],'JJA':[6,7,8],'SON':[9,10,11]}

# Read station information from static file, because the raw FLUXNET data does not contain
# required metadata like station latitude/longitude that is required by MET.
sd = pd.read_csv('fluxnetstations.csv')

print("Starting Terrestrial Coupling Index Calculation for: "+season)
# Locate files at the input directory
if not os.path.exists(fndir):
  print("ERROR: FLUXNET INPUT DIRECTORY DOES NOT EXIST.")
  sys.exit(1)
else:
  fn_file_list = glob.glob(os.path.join(fndir,'FLX_*_DD_*.csv'))
  fn_stations = [os.path.basename(x).split('_')[1] for x in fn_file_list]
  print("FOUND FLUXNET FILES FOR STATIONS:")
  [print(x) for x in fn_stations]

# Loop over all stations we have data for and ensure we have the required metadata
keep_stations = []
for s in fn_stations:
  if not sd['station'].astype('str').str.contains(s).any():
    print("WARNING! EXCLUDING SITE %s, NO METADATA FOUND IN fluxnetstations.csv" % (s))
  else:
    keep_stations.append(s)
fn_stations = keep_stations

# Create a MET dataframe
metdf = pd.DataFrame(columns=['typ','sid','vld','lat','lon','elv','var','lvl','hgt','qc','obs'])
metdf['sid'] = fn_stations
metdf['typ'] = ['ADPSFC']*len(metdf)
metdf['elv'] = [10]*len(metdf)
metdf['lvl'] = [10]*len(metdf)
metdf['var'] = ['TCI']*len(metdf)
metdf['qc'] = ['NA']*len(metdf)
metdf['hgt'] = [0]*len(metdf)
metdf['lat'] = [sd[sd['station']==s]['lat'].values[0] for s in fn_stations]
metdf['lon'] = [sd[sd['station']==s]['lon'].values[0] for s in fn_stations]

# TODO: DEBUG
print(metdf)

# Open each of the fluxnet files as a pandas dataframe
# HH files have different time columns than DD files
#dflist = [pd.read_csv(x,header=0,usecols=['TIMESTAMP_START','TIMESTAMP_END',sfc_flux_varname,soil_varname]) for x in fn_file_list]
dflist = [pd.read_csv(x,usecols=['TIMESTAMP',sfc_flux_varname,sfc_qc,soil_varname,soil_qc]) for x in fn_file_list]

# Because the time record for each station is not the same, the dataframes cannot be merged.
# Given the goal is a single value for each site for all dates that fall in a season,
# the dataframes can remain separate.

sample_df = []

for df,stn in tuple(zip(dflist,fn_stations)):

  print("PROCESSING STATION: %s" % (stn))

  # Length of all data
  alldays = len(df)

  # Only save data with quality above the threshold and reset the index
  df = df[(df[sfc_qc].astype('float')>=DAILY_QC_THRESH)&(df[soil_qc].astype('float')>=DAILY_QC_THRESH)].reset_index()

  print("INFO: DISCARDED %04d DAYS OF LOW QUALITY DATA FOR ALL SEASONS AT %s" % (int(alldays)-int(len(df)),stn))
 
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

  # Get the start and end of the season of the first year
  start, end = get_season_start_end(season,df['datetime'].iloc[0])

  # We know the start and end date of the first season. We assume there is data in every season forward
  # in time until we exceed the last date in the file.
  badyrs = []
  limit = df['datetime'].iloc[-1]
  while start <= limit:
    year = end.strftime('%Y')
    ndays = len(df[(df['datetime']>=start) & (df['datetime']<=(end-datetime.timedelta(days=1)))])
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
    print("REMOVING "+season+" ENDING %s" % (year))
    df = df[(df['datetime']<start)|(df['datetime']>(end-datetime.timedelta(days=1)))]

  # TODO: Double check each season has at least 80 days?
  print("INFO: USING %04d DAYS OF DATA AT %s FOR %s" % (int(len(df)),stn,season))

  # Double check there are sufficient days at this site for all seasons
  if len(df)<MIN_DAYS_SITE:
    print("ERROR! INSUFFICIENT DATA FOR COMPUTING TCI AT "+stn+" FOR "+season)
    print("NDAYS = %04d" % (int(len(df))))
    metdf.loc[metdf['sid']==stn,'qc'] = -9999
    continue

  # Compute TCI. We need to figure out how to aggregate TCI, since we will get a single TCI
  # value for each day in the season, how do we get the seasonal value? Or should we average before
  # computingTCI?
  #df['tci'] = calc_tci(df[soil_varname],df[sfc_flux_varname])
  sample_df.append(df)
  metdf.loc[metdf['sid']==stn,'obs'] = land_sfc.calc_tci(df[soil_varname],df[sfc_flux_varname])

  # Set the valid time as the first time in the record for this site
  metdf.loc[metdf['sid']==stn,'vld'] = pd.to_datetime(df['TIMESTAMP'].iloc[0],format='%Y%m%d').strftime('%Y%m%d_%H%M%S')

print(sample_df)
print(pd.concat(sample_df))
pd.concat(sample_df).reset_index().to_csv('calc_tci_jja_pandas_input.csv',index=False)
exit()

# At this point, 'qc' should be '-9999' anywhere we discarded a site due to insufficient data above. 
# Remove these here.
metdf = metdf[metdf['qc']=='NA']

print(metdf)
exit()

# Add a 
print(dflist)

[print(pd.to_datetime(df['TIMESTAMP']).dt.season) for df in dflist]
[print(df[soil_varname].max()) for df in dflist]
exit()  

# TODO:
# 1. Glob input directory for FLUXNET2015 CSV files (one file per site)
# 2. Determine site name from filename- what other metadata is in the file?
# 3. Read fluxnet file with pandas
# 4. Subset by vars/season in pandas
# 5. Sanitize data in pandas (missing, dtypes)
# 6. Call function to compute TCI
# 7. Prepare data for MET

obsfile = os.path.expandvars(sys.argv[1])
season = sys.argv[2]

f2015data         = xr.open_dataset(obsfile, decode_times=False)

if season=="DJF":
    ss = 0
elif season=="MAM":
    ss = 1
elif season=="JJA":
    ss = 2
elif season=="SON":
    ss = 3
else:
    print('Unrecognized season, please use DJF, MAM, JJA, SON')
    exit()

start_year=f2015data['Start year'].values.tolist()
end_year=f2015data['End year'].values.tolist()
vld=pd.to_datetime(start_year,format='%Y')
vld=vld.strftime("%Y%m%d")
vld=vld+ '_000000'

sid=f2015data['Station'].values.tolist()
print("Length :",len(sid))
print("SID :",sid)

lat=f2015data['Latitude'].values.tolist()
lon=f2015data['Longitude'].values.tolist()
# User can change the name of the variable below
obs=f2015data['CI Sfc_SM Latent_Heat'].values.tolist()
obs=np.array(obs)
obs=obs[:,ss]


#create dummy lists for the message type, elevation, variable name, level, height, and qc string
#numpy is more efficient at creating the lists, but need to convert to Pythonic lists
typ = np.full(len(sid),'ADPSFC').tolist()
elv = np.full(len(sid),10).tolist()
var = np.full(len(sid),'TCI').tolist()
lvl = np.full(len(sid),10).tolist()
hgt = np.zeros(len(sid),dtype=int).tolist()
qc = np.full(len(sid),'NA').tolist()
obs = np.where(np.isnan(obs), -9999, obs)
obs = np.full(len(sid),obs).tolist()
vld = np.full(len(sid),vld).tolist()

l_tuple = list(zip(typ,sid,vld,lat,lon,elv,var,lvl,hgt,qc,obs))
point_data = [list(ele) for ele in l_tuple]

#print("Data Length:\t" + repr(len(point_data)))
#print("Data Type:\t" + repr(type(point_data)))

#print(" Point Data Shape: ",np.shape(point_data))
print(" Point Data: ",point_data)
