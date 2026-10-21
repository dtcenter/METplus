import sys
import pandas as pd
import numpy as np
import datetime
import os

#set time as a callable datetime variable
time = datetime.datetime.strptime(sys.argv[1], '%Y%m%d_%H%M')

#get the INPUT_BASE used by METplus
input_base = sys.argv[2]
input_path = os.path.join(f'{input_base}','obs','mesonet')
meso_obs_varname = sys.argv[3]

#get the names of the previous file and current file
curr_file = f'{input_path}/mesonet_'+time.strftime("%Y%m%d_%H%M")+'.csv'
prev_file = f'{input_path}/mesonet_'+(time-datetime.timedelta(hours=1)).strftime("%Y%m%d_%H%M")+'.csv'
print("Current file name: ", curr_file)
print("previous file name: ", prev_file)
#read in the station id static file to gather station ID, lat/lon, and elevation
holder = pd.read_csv(f'{input_path}/geoinfo.csv',usecols=['stid','nlat','elon','elev'])
stid_list = holder['stid'].values.tolist()
lat_list = holder['nlat'].values.tolist()
lon_list = holder['elon'].values.tolist()
elv_list = holder['elev'].values.tolist()

#check to make sure all collected lists have the same length
length_check = len(stid_list)
if any(len(lst) != length_check for lst in [lat_list, lon_list, elv_list]):
    print("there is an array that has inconsistent data length\nLengths are:")
    for lst in [stid_list, lat_list, lon_list, elv_list]:
        print(len(lst))
    sys.exit()

#Get the previous hour's data
last_hour = pd.read_csv(prev_file,usecols=['STID','TIME',meso_obs_varname])
#remove any stations that had bad values. This may create STIDs that "didn't report out", but that will be caught in later QA
last_hour = last_hour[last_hour[meso_obs_varname] > -1]

#get current hour's data, stids, time
this_hour = pd.read_csv(curr_file, usecols=['STID','TIME',meso_obs_varname,'PRES'])
#remove any stations that had bad values.
this_hour = this_hour[this_hour[meso_obs_varname] > -1]
#remove any stations from last_hour that did not report this_hour
last_hour = last_hour[last_hour['STID'].isin(this_hour['STID'])]
#add a Boolean column for easier filtering after QA
this_hour = this_hour.assign(FILTER='TRUE')

#add columns to hold station lat/lon/elv info
this_hour = this_hour.assign(LAT=0.0)
this_hour = this_hour.assign(LON=0.0)
this_hour = this_hour.assign(ELV=0.0)

#do QA checks
for index, rows in this_hour.iterrows():
    #check that current hour STID reported in previous hour
    #this line is essentially a boolean if the station ID reported last time: 0 if no, 1 if yes
    if rows['STID'] not in last_hour['STID'].values:
        this_hour.at[index,'FILTER'] = 'FALSE'
    #capture station metadata
    try:
        ind_finder = stid_list.index(rows['STID'])
        this_hour.at[index,'LAT'] = lat_list[ind_finder]
        this_hour.at[index,'LON'] = lon_list[ind_finder]
        this_hour.at[index,'ELV'] = elv_list[ind_finder]
    except ValueError:
        print(rows['STID']+' was not found in the master list of station IDs. Will filter out')
        this_hour.at[index,'FILTER'] = 'FALSE'
    #ind = stid_list.index(rows['STID'])

#remove all entries in current data where Boolean was flagged
this_hour = this_hour[this_hour['FILTER'].str.contains('TRUE')]

if meso_obs_varname=='RAIN':
  #calculate rainfall for the hour
  obs = this_hour['RAIN'].values - last_hour['RAIN'].values
  #if there are any negative values, it is from the previous hour's file being 00UTC, which is 24 hour accumumation amounts
  #remove all negative values and replace them with 0.
  obs[obs < 0.] = 0.
else:
  obs = this_hour[meso_obs_varname]

#variables to set at the end when there's a final count
msg_typ = np.full(len(obs),'MSONET').tolist()
valid_time = np.full(len(obs),time.strftime('%Y%m%d_%H%M%S')).tolist()
var_name = np.full(len(obs),meso_obs_varname).tolist()
hght = np.zeros(len(obs), dtype=int).tolist()
qc = np.full(len(obs), 'NA').tolist()
#convert pandas entries to lists
obs = obs.tolist()
stid = this_hour['STID'].values.tolist()
lat = this_hour['LAT'].values.tolist()
lon = this_hour['LON'].values.tolist()
elv = this_hour['ELV'].values.tolist()
lvl = this_hour['PRES'].values.tolist()

#creat a list of lists
l_tuple = list(zip(msg_typ,stid,valid_time,lat,lon,elv,var_name,lvl,hght,qc,obs))
point_data = [list(ele) for ele in l_tuple]

print("Data Length:\t" + repr(len(point_data)))
print("Data Type:\t" + repr(type(point_data)))
