"""
This python embedding code reads in the FLUXNET2015 NETCDF data
and passed to point_data. User need to pass on the season. 
User can change the verifying variable 
"""


import numpy
import sys
import os
import glob
import numpy as np 
import xarray as xr
import datetime
from datetime import date, timedelta
import pandas as pd 


if len(sys.argv) < 2:
    print("Must specify the following elements: FLUXNET2015_file season")
    sys.exit(1)

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
