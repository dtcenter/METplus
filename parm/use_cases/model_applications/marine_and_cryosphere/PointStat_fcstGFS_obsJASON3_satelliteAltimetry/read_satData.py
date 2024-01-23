#This script is designed to ingest one of three types of satellite netCDF files: JASON-3, SARAL, and Sentinel-6a.
#It also grabs the lat, lon, and time information and puts it into a list of lists, the accepted format of MET.
#Currently the script can accept any variable in the netCDFs; however, it's important to note that
#JASON-3 and Sentinel-6a data use groups and non-groups for data organization, which could cause an issue if the requested
#variable is outside of the hardcoded group. The original intent of the use case was for wind speeds and significant wave heights.
#FOR FUTURE REFERENCE
#JASON-3 is swh_ocean, SARAL is swh, and Sentinel-6a is swh_ocean 

from netCDF4 import Dataset
import sys
import numpy as np
from os import listdir
from os.path import isfile, join
import datetime as dt
import xarray as xr
import pandas as pd

#Users are responsible for passing the following arguements at runtime:
##input file
##Varible field to read in
##type of file (JASON, SARAL, or SENTINEL)
if len(sys.argv[1].split(':')) == 3:
    try:
        input_file,field_name,file_type = sys.argv[1].split(':')

    except:
        print("input directory may not be set correctly, dates may not be in correct format. Please recheck")
        sys.exit()
    
    if file_type == 'JASON' or file_type == 'SENTINEL':
        #need to check if the variable is in the data_01 group or data_01/ku group
        try:
            ds = xr.open_dataset(input_file, group="/data_01/ku")
            du = xr.open_dataset(input_file, group="/data_01")
            obs_hold = ds[field_name]
        except KeyError:
            ds = xr.open_dataset(input_file, group="/data_01")
            du = xr.open_dataset(input_file, group="/data_01")
            obs_hold = ds[field_name]
        obs = obs_hold.values
        latitude = np.array(du.latitude.values)
        longitude = np.array(du.longitude.values)
        time = np.array(du.time.values)
        
        #convert times to MET readable
        new_time = []
        for i in range(len(time)):
            new_time.append(pd.to_datetime(str(time[i])).strftime("%Y%m%d_%H%M%S"))
    
    elif file_type == 'SARAL':
        f_in = Dataset(input_file,'r')
        obs = np.array(f_in[field_name][:])
        latitude = np.array(f_in['lat'][:])
        longitude = np.array(f_in['lon'][:])
        time = np.array(f_in['time'][:])
        
        #adjust times to MET time
        new_time = []
        for i in range(len(time)):
            new_time.append(dt.datetime(2000,1,1) + dt.timedelta(seconds=int(time[i])))
            new_time[i] = new_time[i].strftime("%Y%m%d_%H%M%S")

    else:
        print('file type '+file_type+' not supported. Please use JASON, SARAL, or SENTINEL')
        sys.exit()

    #Currently, all station IDs are assigned the same value. If this is not the desired behavior it will require
    #additional coding
    sid = np.full(len(latitude),"1")

    #get arrays into lists, then create a list of lists
    #this also requires creating the last arrays of typ, elv, var, lvl, hgt, and qc
    typ = np.full(len(latitude), 'WDSATR').tolist()
    elv = np.zeros(len(latitude),dtype=int).tolist()
    var = np.full(len(latitude), field_name).tolist()
    lvl = np.full(len(latitude),1013.25).tolist()
    #adding additional check; if 'wind' appears in the variable name, it's assumed
    #to be a wind speed and gets a height of 10m; otherwise its a height of 0
    if field_name.rfind('wind') != -1:
        hgt = np.full(len(latitude),0,dtype=int).tolist()
    else:
        hgt = np.full(len(latitude),0,dtype=int).tolist()
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

#if the incorrect number of args are passed, the system will print out the usage statement and end
else:
    print("Run Command:\n\n read_satData.py /path/to/input/input_file:variable_field_name:file_type\n\nCommands notes:\nIf only certain variable fields return errors, the field may not be supported or outisde of the expected netCDF group. Additional coding changes may be required.\nfile names currently supported: JASON SARAL SENTINEL\nCurrent Message_type is hard-coded to WDSATR\n")
    sys.exit()

