import os
import sys
import datetime as dt
import pandas as pd
import numpy as np

# Accept command line arguments from METplus (valid time beginning and valid time end).
arg_cnt = len(sys.argv)
if arg_cnt < 6:
    print("ERROR: read_nysm.py -> Missing command line argument(s).")
    print("Usage: read_nysm.py VALID_TIME_BEG VALID_TIME_END")
    sys.exit(1)

last_index = 6
if last_index < arg_cnt:
    print(" INFO: read_nysm.py -> Too many arguments, ignored {o}.".format(
        o=' '.join(sys.argv[last_index:])))
    print("Usage: read_nysm.py VALID_TIME_BEG VALID_TIME_END")

valid_time = sys.argv[1]
metplus_usecase_dir = sys.argv[2]
metplus_obs_input_dir = sys.argv[3]
min_latent_heat_flux = float(sys.argv[4])
obs_avg_interval = sys.argv[5]
window_around_valid_seconds = float(sys.argv[6])

# Handle the obs_avg_interval
if not obs_avg_interval in ['1h','h','24h']:
  print("")
  print(f"FATAL! OBS_AVG_INTERVAL {obs_avg_interval} NOT SUPPORTED in read_nysm.py.")
  exit(1)

# Set the list of variables to include.
orig_variable_list = ['TMP', 'RH', 'TSOIL', 'SOILW', 'WIND', 'SNOD']
orig_flux_var_list = ['LHTFL', 'SHTFL', 'FRICV', 'GFLUX','BOWEN']

# Set the list of levels for soil temp and moisture
orig_level_list = ['0-0.1m', '0.1-0.4m', '0.4-1m']

# Set the list of flux site qc variables to include
flux_site_qc_vars = ['flux LE_ok','flux H_ok','flux G_6cm_ok','flux LE_QC','flux H_QC']

# Dictionary mapping grib variable names to variable names in the obs files
var_map = {'RH': 'relh',
           'SNOD': 'snow_depth',
           'SOILW': 'sm',
           'TMP': 'tair',
           'TSOIL': 'ts',
           'WIND': 'wspd_merge',
           'LHTFL': 'flux_LE',
           'SHTFL': 'flux_H',
           'FRICV': 'flux_USTAR',
           'GFLUX': 'flux_G_6cm',
           'BOWEN': 'flux_Bowen_ratio',
           }
level_map = {'0-0.1m': '05',
             '0.1-0.4m': '25',
             '0.4-1m': '50'}
variable_list = []
for var in orig_variable_list:
    if var in ['RH', 'SNOD', 'TMP', 'WIND', 'LHTFL', 'SHTFL', 'FRICV', 'GFLUX']:
        variable_list.append(var_map[var])
    elif var in ['SOILW', 'TSOIL']:
        for lev in orig_level_list:
            variable_list.append('{}{}'.format(var_map[var], level_map[lev]))
flux_var_list = []
for var in orig_flux_var_list:
    flux_var_list.append(var_map[var])
flux_var_list_file = ['flux LE', 'flux H', 'flux USTAR', 'flux G_6cm', 'flux Bowen_ratio'] + flux_site_qc_vars
full_var_list = variable_list + flux_var_list

# Determine whether a single monthly file or two monthly files are needed based on the valid
# time and time window (+/- 60 minutes or 3600 seconds around the valid time).
# Flux files are yearly instead of monthly, so they need a separate file date list.
time_window = window_around_valid_seconds
valid_beg_dt = dt.datetime.strptime(valid_time, '%Y%m%d%H')
valid_end_dt = dt.datetime.strptime(valid_time, '%Y%m%d%H')
valid_time_window_beg = valid_beg_dt - dt.timedelta(seconds=time_window)
valid_time_window_end = valid_end_dt + dt.timedelta(seconds=time_window)
valid_time_beg_str = valid_time_window_beg.strftime('%Y%m%d%H')
valid_time_end_str = valid_time_window_end.strftime('%Y%m%d%H')

print("")
print("INFO: in read_nysm.py:")
print(f"INFO: LOOKING FOR OBSERVATIONS AROUND: {valid_time}")
print(f"INFO: STARTING AT: {valid_time_beg_str}")
print(f"INFO: ENDING AT: {valid_time_end_str}")
print(f"INFO: USING AVERAGING WINDOW: {obs_avg_interval}")
print("")

if valid_time_window_beg.strftime('%Y%m') == valid_time_window_end.strftime('%Y%m'):
    file_date_list = [valid_time_window_beg]
else:
    file_date_list = [valid_time_window_beg, valid_time_window_end]

if valid_time_window_beg.strftime('%Y') == valid_time_window_end.strftime('%Y'):
    flux_date_list = [valid_time_window_beg]
else:
    flux_date_list = [valid_time_window_beg, valid_time_window_end]

site_data = []

# Open the station metadata files (nysm_standard.csv and nysm_flux.csv).
station_file = os.path.join(metplus_usecase_dir,'nysm_standard.csv')
station_metadata = pd.read_csv(station_file, usecols=['stid', 'lat [degrees]', 'lon [degrees]', 'elevation [m]'])
station_metadata = station_metadata.rename(columns={'lat [degrees]': 'lat', 'lon [degrees]': 'lon', 'elevation [m]': 'elevation'})
flux_file = os.path.join(metplus_usecase_dir,'nysm_flux.csv')
flux_sites = pd.read_csv(flux_file, usecols=['stid'])
flux_sites = flux_sites['stid'].to_list()

# Loop over each station ID, open the required file(s) for station, and subset data by only keeping time window and selected variables.
for row in station_metadata.itertuples():

    data = pd.DataFrame()

    print(f'LOOKING FOR STANDARD DATA FOR: {row.stid}')

    # Open and save the standard data.
    for file_date in file_date_list:
        file = os.path.join(metplus_obs_input_dir,"standard_sites/{}/{}_STANDARD_{}.csv".format(
                file_date.strftime('%m'), file_date.strftime('%Y%m'), row.stid))
        try:
            file_data = pd.read_csv(file, usecols=['datetime'] + variable_list)
            file_data['datetime'] = pd.to_datetime(file_data['datetime'], format='%Y%m%dT%H%M')
            file_data = file_data.loc[(file_data['datetime'] >= valid_time_window_beg) & (file_data['datetime'] <= valid_time_window_end)]
            data = pd.concat([data, file_data], ignore_index=True)
        except FileNotFoundError:
            print("File: {} does not exist. Skipping file.".format(file))

    # If there was no standard data found, report and move to the next site
    if len(file_data)==0:
      print(f"NO STANDARD DATA FOUND FOR {row.stid}\n")
      continue
    else:
      print(f"ADDING STANDARD DATA FOR STATION: {row.stid}\n")

    # If the station is a flux site, open and save the flux data.
    if row.stid in flux_sites:
        
        print(f'\nLOOKING FOR FLUX DATA FOR FLUX SITE {row.stid}')

        for flux_date in flux_date_list:
            file = os.path.join(metplus_obs_input_dir,"flux_sites/{}{}.csv".format(row.stid, flux_date.strftime('%Y')))
            try:
                file_data = pd.read_csv(file, usecols=['flux TIMESTAMP_END'] + flux_var_list_file)
                file_data = file_data.rename(columns={'flux TIMESTAMP_END': 'datetime', 'flux LE': 'flux_LE', 'flux H': 'flux_H',
                                                      'flux USTAR': 'flux_USTAR', 'flux G_6cm': 'flux_G_6cm',
                                                      'flux Bowen_ratio': 'flux_Bowen_ratio'}) 
                file_data['datetime'] = pd.to_datetime(file_data['datetime'], format='%Y%m%d%H%M')
                file_data = file_data.loc[(file_data['datetime'] >= valid_time_window_beg) & (file_data['datetime'] <= valid_time_window_end)]
                data = pd.concat([data, file_data], ignore_index=True)
            except FileNotFoundError:
                print("File: {} does not exist. Skipping file.".format(file))
        
        # If for some reason there was no flux data found for the date range requested, report and move to the next site
        if len(file_data)==0:
          print(f"WARNING! NO FLUX DATA FOUND FOR {row.stid} FOR REQUESTED DATES.\n")
        else:
          print(f"ADDING FLUX DATA FOR STATION: {row.stid}\n")
    
          print(f"PERFORMING QC FOR STATION: {row.stid}\n")
          # Apply the QC filtering. We should insert missing data value, so that the time averaging can still occur 
          # but insert missing data which we will then correct to MET's missing data value below.
          LE_qc_condition = (data['flux LE_ok']>0) & (data['flux LE_QC']>0) & (data['flux LE_QC']<7)
          data['flux_LE'] = data['flux_LE'].where(LE_qc_condition,other=np.nan)
    
          H_qc_condition = (data['flux H_ok']>0) & (data['flux H_QC']>0) & (data['flux H_QC']<7)
          data['flux_H'] = data['flux_H'].where(H_qc_condition,other=np.nan)

          G_qc_condition = (data['flux G_6cm_ok']>0)
          data['flux_G_6cm'] = data['flux_G_6cm'].where(G_qc_condition,other=np.nan)

          # Drop the QC vars as they are no longer needed
          data = data.drop(flux_site_qc_vars,axis=1)

    else:
        data[flux_var_list] = np.nan

    # Perform the averaging across time (or whatever aggregation) to obtain a single value for the variable(s)
    # by using pd.resample. This currently works for resampling to hourly.
    data_mean = data.resample(obs_avg_interval, on='datetime', origin='start', label='right', closed='right').mean()

    # Populate the 11-column object for MET
    # Read and format the input 11-column observations:
    #   (1)  string:  Message_Type
    #   (2)  string:  Station_ID
    #   (3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
    #   (4)  numeric: Lat(Deg North)
    #   (5)  numeric: Lon(Deg East)
    #   (6)  numeric: Elevation(msl)
    #   (7)  string:  Var_Name(or GRIB_Code)
    #   (8)  numeric: Level
    #   (9)  numeric: Height(msl or agl)
    #   (10) string:  QC_String
    #   (11) numeric: Observation_Value

    msg_type = "ADPSFC"
    qc_string = "NA"

    # Reset the index so it's just integers and not the times
    data_mean = data_mean.reset_index()

    # I think we just need to "melt" the dataframe
    # Use "melt" from Pandas to switch this from a wide dataframe to a long dataframe for each variable and time
    met_df = pd.melt(data_mean,
                     id_vars="datetime",
                     value_vars=full_var_list,
                     var_name='var',
                     value_name='obs')

    # Add the station and other MET-specific columns
    met_df['sid'] = [row.stid] * len(met_df)
    met_df['lat'] = [row.lat] * len(met_df)
    met_df['lon'] = [row.lon] * len(met_df)
    met_df['elv'] = [row.elevation] * len(met_df)
    met_df['qc'] = qc_string
    met_df['typ'] = msg_type
    met_df['vld'] = met_df['datetime'].dt.strftime('%Y%m%d_%H%M%S')
    met_df['lvl'] = ['NA'] * len(met_df)
    met_df['hgt'] = [-9999.] * len(met_df)

    # Handle levels and names for some variables
    met_df.loc[met_df['var']=='tair', 'var'] = 'TMP'
    met_df.loc[met_df['var']=='relh', 'var'] = 'RH'
    met_df.loc[met_df['var']=='wspd_merge', 'var'] = 'WIND'
    met_df.loc[met_df['var']=='snow_depth', 'var'] = 'SNOD'
    hgt_zero = (met_df['var'] == 'TMP') | (met_df['var'] == 'RH') | (met_df['var'] == 'WIND') | (met_df['var'] == 'SNOD')
    met_df.loc[hgt_zero, 'hgt'] = 0

    # Handle soil moisture levels and names
    sm05 = met_df['var'] == 'sm05'
    met_df.loc[sm05, 'hgt'] = 0.05
    met_df.loc[sm05, 'var'] = 'SOILW'
    met_df.loc[sm05, 'typ'] = 'SOILWDEPTH'

    sm25 = met_df['var'] == 'sm25'
    met_df.loc[sm25, 'hgt'] = 0.25
    met_df.loc[sm25, 'var'] = 'SOILW'
    met_df.loc[sm25, 'typ'] = 'SOILWDEPTH'

    sm50 = met_df['var'] == 'sm50'
    met_df.loc[sm50, 'hgt'] = 0.5
    met_df.loc[sm50, 'var'] = 'SOILW'
    met_df.loc[sm50, 'typ'] = 'SOILWDEPTH'

    # Handle soil temperature levels and names
    ts05 = met_df['var'] == 'ts05'
    met_df.loc[ts05, 'hgt'] = 0.05
    met_df.loc[ts05, 'var'] = 'TSOIL'
    met_df.loc[ts05, 'typ'] = 'TSOILDEPTH'

    ts25 = met_df['var'] == 'ts25'
    met_df.loc[ts25, 'hgt'] = 0.25
    met_df.loc[ts25, 'var'] = 'TSOIL'
    met_df.loc[ts25, 'typ'] = 'TSOILDEPTH'

    ts50 = met_df['var'] == 'ts50'
    met_df.loc[ts50, 'hgt'] = 0.5
    met_df.loc[ts50, 'var'] = 'TSOIL'
    met_df.loc[ts50, 'typ'] = 'TSOILDEPTH'

    # Handle flux variable levels and names
    fluxLE = met_df['var'] == 'flux_LE'
    met_df.loc[fluxLE, 'var'] = 'LHTFL'
    met_df.loc[fluxLE, 'lvl'] = 'L0'

    fluxH = met_df['var'] == 'flux_H'
    met_df.loc[fluxH, 'var'] = 'SHTFL'
    met_df.loc[fluxH, 'lvl'] = 'L0'

    fluxUSTAR = met_df['var'] == 'flux_USTAR'
    met_df.loc[fluxUSTAR, 'var'] = 'FRICV'
    met_df.loc[fluxUSTAR, 'lvl'] = 'L0'

    fluxG6cm = met_df['var'] == 'flux_G_6cm'
    met_df.loc[fluxG6cm, 'var'] = 'GFLUX'
    met_df.loc[fluxG6cm, 'lvl'] = 'L0'

    fluxBOW = met_df['var'] == 'flux_Bowen_ratio'
    met_df.loc[fluxBOW, 'hgt'] = 0
    met_df.loc[fluxBOW, 'var'] = 'BOWEN'
    met_df.loc[fluxBOW, 'lvl'] = 'L0'

    # Reorder the columns to the order MET expects
    met_df = met_df[['typ','sid','vld','lat','lon','elv','var','lvl','hgt','qc','obs']]
   
    # Replace NaN values with MET's missing data value
    met_df['obs'] = met_df['obs'].where(~met_df['obs'].isna(),-9999.)

    # Append each site's time-averaged data to a list
    site_data.append(met_df)

# If we found no data report and exit
if len(site_data)==0:
  print(f"NO DATA TO PROCESS.")
  exit(1)

# Concatenate data from all sites into a single Dataframe
all_sites = pd.concat(site_data)

# Convert the Dataframe to the object MET expects
point_data = all_sites.values.tolist()
