#This script is designed to read in multiple ASCAT input data files, and strip out any/all observation points that land within
#the user's designated beginning and end times. The challenge of this script will be to ensure that each unique lat/lon pair
#recieves a unique station ID, as well as not allowing two different observation values to exist for a unique station ID that
#occur at the same time (different times are OK). The final list of observation points will be passed back to MET for verification.
#This script will also remain as flexible as possible, by not hardcoding the variable type read in, the message type assigned to
#the dataset, or the start and end times.

from netCDF4 import Dataset
import sys
import numpy as np
from os import listdir
from os.path import isfile, join
import datetime as dt

#Users are responsible for passing the following arguements at runtime:
##input directory to files (directory can contain any files, but only those matching the template of ascat_YYYYMMDDHHMMSS_*, where * can be any additional identifier
##start time in YYYYMMDDHHMMSS
##end time in YYYYMMDDHHMMSS
##Message type to code values as (suggested types are WDSATR and SATWND)
##Varible field to read in
#this will check that the correct number of args are passed at runtime. If not, the program exits
if len(sys.argv[1].split(':')) != 5:
    print("Run Command:\n\n read_ascat_data.py /path/to/input/input_files:start_date:end_date:Message_type:Variable\n\nCommands notes:\n-start and end dates are formatted YYYYMMDDHHMMSS\n-Suggested Message_types are WDSATR or SATWND, refer to MET User's Guide for more info\n")
    sys.exit(1)
try:
    input_dir,st_date,en_date,msg_typ,var_typ = sys.argv[1].split(':')
    #files need to be only the ASCAT format. Any other file types will result in an error in the later loop that collects files between the user stated times
    onlyfiles = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    #get times into correct format
    st_date = dt.datetime.strptime(st_date,"%Y%m%d%H%S")
    en_date = dt.datetime.strptime(en_date,"%Y%m%d%H%S")
except:
    print("input directory may not be set correctly, dates may not be in correct format. Please recheck")
    sys.exit(1)
#need to loop through all of the files and retain only those that are between the desired times
final_file_list = []
for i in onlyfiles:
    if st_date <= dt.datetime.strptime(i.split('_')[1],"%Y%m%d%H%S00") and en_date >= dt.datetime.strptime(i.split('_')[1],"%Y%m%d%H%S00"):
        final_file_list.append(i)
#establish boolean to figure out first run so arrays are initalized only once
first = True
#now loop through the files and pull out the data
for i in final_file_list:
    f_in = Dataset(input_dir+'/'+i,'r')
    if first:
        obs = np.array(f_in[var_typ][:])
        latitude = np.array(f_in['latitude'][:])
        longitude = np.array(f_in['longitude'][:])
        time = np.array(f_in['time'][:])
        first = False
    else:
        obs = np.append(obs, f_in[var_typ][:])
        latitude = np.append(latitude, f_in['latitude'][:])
        longitude = np.append(longitude, f_in['longitude'][:])
        time = np.append(time, f_in['time'][:])
#convert times to MET times
new_time = []
for i in range(len(time)):
    new_time.append(dt.datetime(1970,1,1) + dt.timedelta(seconds=int(time[i])))
    new_time[i] = new_time[i].strftime("%Y%m%d_%H%M%S")

#ALTERNATE METHOD instead of assigning individual IDs to each latlon pair (which is the commented out section below), this method assigns a value of "1" to each point effectively making every point read in the same station. This is a time saver, as well as a potential path to code by file/satellite type rather than by point on earth.
sid = np.full(len(latitude),"1")

"""    
#INDIVIDUAL ID METHOD this checks the lat lon pairs as station IDs are assigned. We'll create a new numpy array made of strings that are the lat-lon combinations. If there are duplicate strings then there are duplicate lat-lon pairs, and they'll get the same station ID. Otherwise, the station ID will be Unique for each lat-lon pair
lat_str = np.array(latitude, dtype=str)
lon_str = np.array(longitude, dtype=str)
lat_lon_str = np.char.add(lat_str, lon_str)
uniq_lat_lon_str, counts = np.unique(lat_lon_str, return_counts=True)
#   sid = np.full(len(lat_lon_str),"1").tolist()
sid = np.full(len(lat_lon_str),"0")
external_count = 1
#this loop will give each station ID an assigned lat-lon pair
for i in range(len(uniq_lat_lon_str)):
    if(counts[i]) == 1:
        sid[i] = str(external_count)
        external_count += 1
    else:
        holder = np.where(uniq_lat_lon_str[i] == lat_lon_str)
        for j in range(len(holder[0])):
            sid[holder[0][j]] = str(external_count)
        external_count += 1
"""

#get arrays into lists, then create a list of lists
#this also requires creating the last arrays of typ, elv, var, lvl, hgt, and qc
typ = np.full(len(latitude), msg_typ).tolist()
elv = np.zeros(len(latitude),dtype=int).tolist()
var = np.full(len(latitude), var_typ).tolist()
lvl = np.full(len(latitude),1013.25).tolist()
hgt = np.full(len(latitude),10,dtype=int).tolist()
qc = np.full(len(latitude),'NA').tolist()
    
sid = sid.tolist()
vld = new_time
lat = latitude.tolist()
lon = longitude.tolist()
obs = obs.tolist()
l_tuple = list(zip(typ,sid,vld,lat,lon,elv,var,lvl,hgt,qc,obs))
point_data = [list(ele) for ele in l_tuple]

print("Data Length:\t" + repr(len(point_data)))
print("Data Type:\t" + repr(type(point_data)))

#This will print out all of the files that were read in at runtime. If not desired, comment out.
print(final_file_list)
    

