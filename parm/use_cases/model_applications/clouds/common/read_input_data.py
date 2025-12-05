#this code was provided by Craig Schwartz
#and is largely unaltered from its original
#function.

import os
import sys
import numpy as np
from datetime import datetime, timezone
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from scipy.interpolate import NearestNDInterpolator, LinearNDInterpolator
#### for Plotting
import fnmatch
import pygrib
#####

###########################################

missing_values = -9999.0  # for MET

# UPP top layer bounds (Pa) for cloud layers
PTOP_LOW_UPP  = 64200. # low for > 64200 Pa
PTOP_MID_UPP  = 35000. # mid between 35000-64200 Pa
PTOP_HIGH_UPP = 15000. # high between 15000-35000 Pa

# Values for 4 x 4 contingency table
Na, Nb, Nc, Nd = 1, 2, 3, 4 
Ne, Nf, Ng, Nh = 5, 6, 7, 8 
Ni, Nj, Nk, Nl = 9, 10, 11, 12
Nm, Nn, No, Np = 13, 14, 15, 16

# Notes:
# 1) Entry for 'point' is for point-to-point comparison and is all dummy data (except for gridType) that is overwritten by point2point
# 2) ERA5 on NCAR CISL RDA changed at some point.  Old is ERA5_2017 (not used anymore), new is ERA5, which we'll use for 2020 data
griddedDatasets =  {
   'MERRA2'   : { 'gridType':'LatLon', 'latVar':'lat',     'latDef':[-90.0,0.50,361], 'lonVar':'lon',       'lonDef':[-180.0,0.625,576],   'flipY':True, 'ftype':'nc'},
   'SATCORPS' : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.25,721], 'lonVar':'longitude', 'lonDef':[-180.0,0.3125,1152], 'flipY':False, 'ftype':'nc' },
   'ERA5_2017': { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-89.7848769072,0.281016829130516,640], 'lonVar':'longitude', 'lonDef':[0.0,0.28125,1280], 'flipY':False, 'ftype':'nc' },
   'ERA5'     : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.25,721], 'lonVar':'longitude', 'lonDef':[0.0,0.25,1440], 'flipY':False, 'ftype':'nc' },
   'GFS'      : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[90.0,0.25,721], 'lonVar':'longitude',  'lonDef':[0.0,0.25,1440],   'flipY':False, 'ftype':'grib'},
   'GALWEM'   : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.25,721], 'lonVar':'longitude',  'lonDef':[0.0,0.25,1440],   'flipY':True, 'ftype':'grib'},
   'GALWEM17' : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-89.921875,0.156250,1152], 'lonVar':'longitude',  'lonDef':[0.117187,0.234375,1536], 'flipY':False, 'ftype':'grib'},
   'WWMCA'    : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.25,721], 'lonVar':'longitude',  'lonDef':[0.0,0.25,1440],   'flipY':False, 'ftype':'grib'},
   'MPAS'     : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.25,721],  'lonVar':'longitude',  'lonDef':[0.0,0.25,1440],   'flipY':False, 'ftype':'nc'},
   'SAT_WWMCA_MEAN' : { 'gridType':'LatLon', 'latVar':'lat','latDef':[-90.0,0.25,721], 'lonVar':'lon', 'lonDef':[0.0,0.25,1440], 'flipY':False, 'ftype':'nc' },
   'point'    : { 'gridType':'LatLon', 'latVar':'latitude','latDef':[-90.0,0.156250,1152], 'lonVar':'longitude',  'lonDef':[0.117187,0.234375,1536],   'flipY':False, 'ftype':'nc'},
}
   # Correct one, but MET can ingest a Gaussian grid only in Grib2 format (from Randy B.)
   #'ERA5'     : { 'gridType':'Gaussian', 'nx':1280, 'ny':640, 'lon_zero':0, 'latVar':'latitude', 'lonVar':'longitude', 'flipY':False, },

#GALWEM, both 17-km and 0.25-degree
lowCloudFrac_GALWEM  =  { 'parameterCategory':6, 'parameterNumber':3, 'typeOfFirstFixedSurface':10, 'shortName':'lcc' }
midCloudFrac_GALWEM  =  { 'parameterCategory':6, 'parameterNumber':4, 'typeOfFirstFixedSurface':10, 'shortName':'mcc' }
highCloudFrac_GALWEM =  { 'parameterCategory':6, 'parameterNumber':5, 'typeOfFirstFixedSurface':10, 'shortName':'hcc' }
totalCloudFrac_GALWEM = { 'parameterCategory':6, 'parameterNumber':1, 'typeOfFirstFixedSurface':10, 'shortName':'tcc' }
cloudTopHeight_GALWEM =  { 'parameterCategory':6, 'parameterNumber':12, 'typeOfFirstFixedSurface':3, 'shortName':'cdct' }
cloudBaseHeight_GALWEM =  { 'parameterCategory':6, 'parameterNumber':11, 'typeOfFirstFixedSurface':2, 'shortName':'cdcb' }

#GFS
lowCloudFrac_GFS  =  { 'parameterCategory':6, 'parameterNumber':1, 'typeOfFirstFixedSurface':214, 'shortName':'tcc' }
midCloudFrac_GFS  =  { 'parameterCategory':6, 'parameterNumber':1, 'typeOfFirstFixedSurface':224, 'shortName':'tcc' }
highCloudFrac_GFS =  { 'parameterCategory':6, 'parameterNumber':1, 'typeOfFirstFixedSurface':234, 'shortName':'tcc' }

#WWMCA
totalCloudFrac_WWMCA  = { 'parameterName':71, 'typeOfLevel':'entireAtmosphere', 'level':0 }

cloudTopHeightLev1_WWMCA  = { 'parameterName':228, 'typeOfLevel':'hybrid', 'level':1 }
cloudTopHeightLev2_WWMCA  = { 'parameterName':228, 'typeOfLevel':'hybrid', 'level':2 }
cloudTopHeightLev3_WWMCA  = { 'parameterName':228, 'typeOfLevel':'hybrid', 'level':3 }
cloudTopHeightLev4_WWMCA  = { 'parameterName':228, 'typeOfLevel':'hybrid', 'level':4 }
cloudTopHeight_WWMCA      = [ cloudTopHeightLev1_WWMCA, cloudTopHeightLev2_WWMCA, cloudTopHeightLev3_WWMCA, cloudTopHeightLev4_WWMCA ]

cloudBaseHeightLev1_WWMCA  = { 'parameterName':227, 'typeOfLevel':'hybrid', 'level':1 }
cloudBaseHeightLev2_WWMCA  = { 'parameterName':227, 'typeOfLevel':'hybrid', 'level':2 }
cloudBaseHeightLev3_WWMCA  = { 'parameterName':227, 'typeOfLevel':'hybrid', 'level':3 }
cloudBaseHeightLev4_WWMCA  = { 'parameterName':227, 'typeOfLevel':'hybrid', 'level':4 }
cloudBaseHeight_WWMCA      = [ cloudBaseHeightLev1_WWMCA, cloudBaseHeightLev2_WWMCA, cloudBaseHeightLev3_WWMCA, cloudBaseHeightLev4_WWMCA ]

verifVariablesModel = {
    'binaryCloud'    :  {'GFS':[''], 'GALWEM17':[totalCloudFrac_GALWEM],  'GALWEM':[totalCloudFrac_GALWEM], 'MPAS':['cldfrac_tot_UM_rand']},
    'totalCloudFrac' :  {'GFS':[''], 'GALWEM17':[totalCloudFrac_GALWEM],  'GALWEM':[totalCloudFrac_GALWEM], 'MPAS':['cldfrac_tot_UM_rand']},
    'lowCloudFrac'   :  {'GFS':[lowCloudFrac_GFS], 'GALWEM17':[lowCloudFrac_GALWEM], 'GALWEM':[lowCloudFrac_GALWEM], 'MPAS':['cldfrac_low_UM']},
    'midCloudFrac'   :  {'GFS':[midCloudFrac_GFS], 'GALWEM17':[midCloudFrac_GALWEM], 'GALWEM':[midCloudFrac_GALWEM], 'MPAS':['cldfrac_mid_UM']},
    'highCloudFrac'  :  {'GFS':[highCloudFrac_GFS], 'GALWEM17':[highCloudFrac_GALWEM], 'GALWEM':[highCloudFrac_GALWEM], 'MPAS':['cldfrac_high_UM']},
    'cloudTopHeight' :  {'GFS':['']               , 'GALWEM17':[cloudTopHeight_GALWEM], 'GALWEM':[cloudTopHeight_GALWEM], 'MPAS':['cldht_top_UM']},
    'cloudBaseHeight' : {'GFS':['']               , 'GALWEM17':[cloudBaseHeight_GALWEM], 'GALWEM':[cloudBaseHeight_GALWEM], 'MPAS':['cldht_base_UM']},
}

cloudFracCatThresholds = '>0, <10.0, >=10.0, >=20.0, >=30.0, >=40.0, >=50.0, >=60.0, >=70.0, >=80.0, >=90.0' # MET format string
brightnessTempThresholds = '<280.0, <275.0, <273.15, <270.0, <265.0, <260.0, <255.0, <250.0, <245.0, <240.0, <235.0, <230.0, <225.0, <220.0, <215.0, <210.0, <=SFP1, <=SFP5, <=SFP10, <=SFP25, <=SFP50, >=SFP50, >=SFP75, >=SFP90, >=SFP95, >=SFP99'
verifVariables = {
   'binaryCloud'    : { 'MERRA2':['CLDTOT'], 'SATCORPS':['cloud_percentage_level'],      'ERA5':['TCC'], 'WWMCA':[totalCloudFrac_WWMCA], 'SAT_WWMCA_MEAN':['Mean_WWMCA_SATCORPS'], 'units':'NA',  'thresholds':'>0.0', 'interpMethod':'nearest' },
   'totalCloudFrac' : { 'MERRA2':['CLDTOT'], 'SATCORPS':['cloud_percentage_level'],      'ERA5':['tcc'], 'WWMCA':[totalCloudFrac_WWMCA], 'SAT_WWMCA_MEAN':['Mean_WWMCA_SATCORPS'], 'units':'%',   'thresholds':cloudFracCatThresholds, 'interpMethod':'bilin' },
   'lowCloudFrac'   : { 'MERRA2':['CLDLOW'], 'SATCORPS':['cloud_percentage_level'],      'ERA5':['lcc'], 'units':'%',   'thresholds':cloudFracCatThresholds, 'interpMethod':'bilin' },
   'midCloudFrac'   : { 'MERRA2':['CLDMID'], 'SATCORPS':['cloud_percentage_level'],      'ERA5':['MCC'], 'units':'%',   'thresholds':cloudFracCatThresholds, 'interpMethod':'bilin' },
   'highCloudFrac'  : { 'MERRA2':['CLDHGH'], 'SATCORPS':['cloud_percentage_level'],      'ERA5':['HCC'], 'units':'%',   'thresholds':cloudFracCatThresholds, 'interpMethod':'bilin' },
   'cloudTopTemp'   : { 'MERRA2':['CLDTMP'], 'SATCORPS':['cloud_temperature_top_level'], 'ERA5':['']   , 'units':'K',   'thresholds':'NA', 'interpMethod':'bilin'},
   'cloudTopPres'   : { 'MERRA2':['CLDPRS'], 'SATCORPS':['cloud_pressure_top_level'],    'ERA5':['']   , 'units':'hPa', 'thresholds':'NA', 'interpMethod':'bilin'},
   'cloudTopHeight' : { 'MERRA2':['']      , 'SATCORPS':['cloud_height_top_level'],      'ERA5':['']   , 'WWMCA':cloudTopHeight_WWMCA,  'units':'m',   'thresholds':'NA', 'interpMethod':'nearest'},
   'cloudBaseHeight': { 'MERRA2':['']      , 'SATCORPS':['cloud_height_base_level'],     'ERA5':['cbh'], 'WWMCA':cloudBaseHeight_WWMCA, 'units':'m',   'thresholds':'NA', 'interpMethod':'nearest'},
   'cloudCeiling'   : { 'MERRA2':['']      , 'SATCORPS':[''],                            'ERA5':['']   , 'units':'m',   'thresholds':'NA', 'interpMethod':'bilin'},
   'brightnessTemp' : { 'MERRA2':['']      , 'SATCORPS':[''],                            'ERA5':['']   , 'units':'K',   'thresholds':brightnessTempThresholds, 'interpMethod':'bilin'},
}

# Combine the two dictionaries
# Only reason verifVariablesModel exists is just for space--verifVaribles gets too long if we keep adding more datasets
for key in verifVariablesModel.keys():
  x = verifVariablesModel[key]
  for key1 in x.keys():
     verifVariables[key][key1] = x[key1]

#f = '/glade/u/home/schwartz/cloud_verification/GFS_grib_0.25deg/2018112412/gfs.0p25.2018112412.f006.grib2'
#grbs = pygrib.open(f)
#idx = pygrib.index(f,'parameterCategory','parameterNumber','typeOfFirstFixedSurface')
#model = 'GFS'
#variable = 'totCloudCover'
#x = verifVariablesModel[variable][model] # returns a list, whose ith element is a dictionary
# e.g., idx(parameterCategory=6,parameterNumber=1,typeOfFirstFixedSurface=234)
#idx(parameterCategory=x[0]['parameterCategory'],parameterNumber=x[0]['parameterNumber'],typeOfFirstFixedSurface=x[0]['typeOfFirstFixedSurface'])

# to read in an environmental variable
#x = os.getenv('a') # probably type string no matter what

###########

def get_threshold(variable):
   x = verifVariables[variable]['thresholds']
   print(x) # needed for python 3 to read variable into csh variable
   return x

def get_interp_method(variable):
   x = verifVariables[variable]['interpMethod'].upper()
   print(x) # needed for python 3 to read variable into csh variable
   return x

def get_total_cloud_frac(source, data):
   if source == 'SATCORPS':
      x = (data[0][0,:,:,1]  + data[0][0,:,:,2] + data[0][0,:,:,3])*1.0E-2  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] * 100.0 # the ith element of data is a numpy array
      print(x.min(), x.max())
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] * 100.0
      except IndexError: x = data[0][0,:,:] * 100.0
   elif source == 'MPAS':
      x = data[0][0,:,:] * 100.0
   elif source == 'SAT_WWMCA_MEAN':
      x = data[0][0,:,:] # already in %
   else:
      x = data[0]

   x = np.where( x < 0.0  , 0.0,   x) # Force negative values to zero
   x = np.where( x > 100.0, 100.0, x) # Force values > 100% to 100%
   return x

def get_binary_cloud(source, data):
   y = get_total_cloud_frac(source, data)
   # keep NaNs as is, but then set everything else to either 100% or 0%
   x = np.where( np.isnan(y), y, np.where(y > 0.0, 100.0, 0.0) )
   return x

def get_layer_cloud_frac(source, data, layer):
   if source == 'SATCORPS':
      if layer.lower().strip() == 'low'  : i = 1
      if layer.lower().strip() == 'mid'  : i = 2
      if layer.lower().strip() == 'high' : i = 3
      x = data[0][0,:,:,i] * 1.0E-2  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] * 100.0
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] * 100.0
      except IndexError: x = data[0][0,:,:] * 100.0
   elif source == 'MPAS':
      x = data[0][0,:,:] * 100.0
   else:
      x = data[0]

   x = np.where( x < 0.0, 0.0, x) # Force negative values to zero
   x = np.where( x > 100.0, 100.0, x) # Force values > 100% to 100%

   return x

def get_cloud_top_temp(source, data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E-2  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] 
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except IndexError: x = data[0][0,:,:]
   else:
      x = data[0]
   return x

def get_cloud_top_pres(source, data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E-1  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] * 1.0E-2  # scaling [Pa] -> [hPa]
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except IndexError: x = data[0][0,:,:]
   else:
      x = data[0]
   return x

def get_cloud_top_height(source, data):
   return get_cloud_top(source, data, get_base=False)

def get_cloud_base_height(source, data):
   return get_cloud_top(source, data, get_base=True)

def get_cloud_top(source, data, get_base):
   """If get_base is True, get cloud base, otherwise get cloud top."""
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E+1  # scaling to [meters]
   elif source == 'MERRA2':
      x = data[0][0,:,:]     #TBD
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except IndexError: x = data[0][0,:,:]
   elif source == 'GALWEM17':
      x = data[0] * 1000.0 * 0.3048  # kilofeet -> meters
   elif source == 'MPAS':
      x = data[0][0,:,:] # already in meters
   elif source == 'WWMCA':
      # data is a list (should be length 4)
      if len(data) != 4:
         print('error with WWMCA Cloud top height')
         sys.exit()
      tmp = np.array(data) # already in meters
      tmp = np.where( tmp <= 0, np.nan, tmp) # replace 0 or negative values with NAN
      if get_base:
         x = np.nanmin(tmp,axis=0)
      else:
         x = np.nanmax(tmp,axis=0) # get maximum cloud top height across all layers
   else:
      x = data[0]

   # Eliminate unphysical values (assume cloud top shouldn't be > 50000 meters)
   y = np.where( x > 50000.0 , np.nan, x )

   return y

def get_cloud_ceiling(source, data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0]   #TBD
   elif source == 'MERRA2':
      x = data[0][0,:,:]     #TBD
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] # TBD
      except IndexError: x = data[0][0,:,:]
   return x

# add other functions for different variables

###########

def get_data_array(input_file, source, variable, data_source):
   # 1) input_file:  File name--either observations or forecast
   # 2) source:     Obsevation source (e.g., MERRA, SATCORP, etc.)
   # 3) variable:   Variable to verify
   # 4) data_source: If 1, process forecast file. If 2 process obs file.

#   # specifying names here temporarily. file names should be passed in to python from shell script
#   if source == 'merra':      nc_file = '/gpfs/fs1/scratch/schwartz/MERRA/MERRA2_400.tavg1_2d_rad_Nx.20181101.nc4'
#   elif source == 'satcorp':  nc_file = '/glade/scratch/bjung/met/test_satcorps/GEO-MRGD.2018334.0000.GRID.NC'
#   elif source == 'era5':     nc_file = '/glade/scratch/bjung/met/test_era5/e5.oper.fc.sfc.instan.128_164_tcc.regn320sc.2018111606_2018120112.nc'

   source = source.upper().strip()  # Force uppercase and get rid of blank spaces, for safety

   print('dataSource = ', data_source)

   ftype = griddedDatasets[source]['ftype'].lower().strip()

   # dataSource == 1 means forecast, 2 means obs
   #  if dataSource == 1: vars_to_read = verifVariablesModel[variable][source] # if ftype == 'grib', returns a list whose ith element is a dictionary. otherwise, just a list
   #  if dataSource == 2: vars_to_read = verifVariables[variable][source] # returns a list
   vars_to_read = verifVariables[variable][source]  # if ftype == 'grib', returns a list whose ith element is a dictionary. otherwise, just a list

   print('Trying to read ', input_file)

   # Get file handle
   if ftype == 'nc':
      data = get_nc_data(input_file, vars_to_read)
   elif ftype == 'grib':
       data = get_grib_data(input_file, vars_to_read, source, variable)
   else:
      print(f"ERROR: Invalid ftype: {ftype}. Should be nc or grib")
      sys.exit(1)

   # Call a function to get the variable of interest.
   # Add a new function for each variable
   if variable == 'binaryCloud':     raw_data = get_binary_cloud(source, data)
   elif variable == 'totalCloudFrac':  raw_data = get_total_cloud_frac(source, data)
   elif variable == 'lowCloudFrac':    raw_data = get_layer_cloud_frac(source, data, 'low')
   elif variable == 'midCloudFrac':    raw_data = get_layer_cloud_frac(source, data, 'mid')
   elif variable == 'highCloudFrac':   raw_data = get_layer_cloud_frac(source, data, 'high')
   elif variable == 'cloudTopTemp':    raw_data = get_cloud_top_temp(source, data)
   elif variable == 'cloudTopPres':    raw_data = get_cloud_top_pres(source, data)
   elif variable == 'cloudTopHeight':  raw_data = get_cloud_top_height(source, data)
   elif variable == 'cloudBaseHeight': raw_data = get_cloud_base_height(source, data)
   elif variable == 'cloudCeiling':    raw_data = get_cloud_ceiling(source, data)
   else:
      print(f'ERROR: Invalid variable: {variable}. '
            'Should be binaryCloud, totalCloudFrac, lowCloudFrac, midCloudFrac, highCloudFrac, cloudTopTemp, '
            'cloudTopPres, cloudTopHeight, cloudBaseHeight, cloudCeiling')
      sys.exit(1)

   raw_data = np.where(np.isnan(raw_data), missing_values, raw_data) # replace np.nan to missing_values (for MET)

   # Array met_data is passed to MET
   # Graphics should plot $met_data to make sure things look correct
   if griddedDatasets[source]['flipY']: 
      print('flipping ',source,' data about y-axis')
      met_data=np.flip(raw_data,axis=0).astype(float)
   else:
      met_data=raw_data.astype(float)

   return met_data

def get_nc_data(input_file, vars_to_read):
   data = []
   nc_fid = Dataset(input_file, "r", format="NETCDF4")
   for v in vars_to_read:
      print('Reading ', v)
      read_var = nc_fid.variables[v]  # extract/copy the data
      try:
         read_missing = read_var.missing_value  # get variable attributes. Each dataset has own missing values.
      except AttributeError:
         read_missing = -9999.  # set a default missing value. probably only need to do this for MPAS

      this_var = np.array( read_var )        # to numpy array
      this_var = np.where( this_var==read_missing, np.nan, this_var )
      data.append(this_var) # ith element of the list is a NUMPY ARRAY for the ith variable

   nc_fid.close()
   return data

def get_grib_data(input_file, vars_to_read, source, variable):
   data = []
   if source == 'WWMCA':
      idx = pygrib.index(input_file, 'parameterName', 'typeOfLevel', 'level')
   else:
      idx = pygrib.index(input_file, 'parameterCategory', 'parameterNumber', 'typeOfFirstFixedSurface')

   for v in vars_to_read:
      print('Reading ', v)
      if source == 'WWMCA':
         x = idx(parameterName=v['parameterName'], typeOfLevel=v['typeOfLevel'], level=v['level'])[0]  # by getting element 0, you get a pygrib message
      else:
         # e.g., idx(parameterCategory=6,parameterNumber=1,typeOfFirstFixedSurface=234)
         if (variable == 'cloudTopHeight' or variable == 'cloudBaseHeight') and source == 'GALWEM17':
            element_idx = 1
         else:
            element_idx = 0

         x = idx(parameterCategory=v['parameterCategory'], parameterNumber=v['parameterNumber'], typeOfFirstFixedSurface=v['typeOfFirstFixedSurface'])[element_idx]
         if x.shortName != v['shortName']: print('Name mismatch!')
         # ADDED BY JOHN O
         print(x)
         print('Reading ', x.shortName, 'at level ', x.typeOfFirstFixedSurface)

      read_var = x.values  # same x.data()[0]
      read_missing = x.missingValue
      print('missing value = ', read_missing)

      # The missing value (read_missing) for GALWEM17 and GALWEM cloud base/height is 9999, which is not the best choice because
      # those could be actual values. So we need to use the masked array part (below) to handle which
      # values are missing.  We also set read_missing to something unphysical to essentially disable it.
      # Finally, if we don't change the 'missingValue' property in the GRIB2 file we are eventually outputting,
      # the bitmap will get all messed up, because it will be based on 9999 instead of $missing_values
      if variable == 'cloudTopHeight' or variable == 'cloudBaseHeight':
         read_missing = -9999.
         x['missingValue'] = read_missing
         if source == 'GALWEM17':
            # These are masked numpy arrays, with mask = True where there is a missing value (no cloud)
            # Use np.ma.filled to create an ndarray where mask = True values are set to np.nan
            read_var = np.ma.filled(read_var.astype(read_var.dtype), np.nan)

      this_var = np.array( read_var )        # to numpy array
      this_var = np.where( this_var==read_missing, np.nan, this_var )
      data.append(this_var) # ith element of the list is a NUMPY ARRAY for the ith variable

   idx.close()  # Close the input GRIB file
   return data

def get_fcst_cloud_frac(cfr, pmid, psfc, layer_definitions): # cfr is cloud fraction(%), pmid is 3D pressure(Pa), psfc is surface pressure (Pa) code from UPP ./INITPOST.F

   if pmid.shape != cfr.shape:  # sanity check
      print('dimension mismatch bewteen cldfra and pressure')
      sys.exit()

   nlocs, _ = pmid.shape

   if len(psfc) != nlocs: # another sanity check
      print('dimension mismatch bewteen cldfra and surface pressure')
      sys.exit()

   cfracl = np.zeros(nlocs)
   cfracm = np.zeros(nlocs)
   cfrach = np.zeros(nlocs)

   for i in range(0,nlocs):

      PTOP_HIGH = PTOP_HIGH_UPP
      if layer_definitions.upper().strip() == 'ERA5':
         PTOP_LOW = 0.8*psfc[i]
         PTOP_MID = 0.45*psfc[i]
      elif layer_definitions.upper().strip() == 'UPP':
         PTOP_LOW = PTOP_LOW_UPP
         PTOP_MID = PTOP_MID_UPP

      idx_low  = np.nonzero(   pmid[i,:] >= PTOP_LOW)[0] # using np.where with just 1 argument returns tuple
      idx_mid  = np.nonzero(  (pmid[i,:] <  PTOP_LOW) & (pmid[i,:] >= PTOP_MID))[0]
      idx_high = np.nonzero(  (pmid[i,:] <  PTOP_MID) & (pmid[i,:] >= PTOP_HIGH))[0]

      # use conditions in case all indices are missing
      if (len(idx_low) >0 ):  cfracl[i] = np.max( cfr[i,idx_low] )
      if (len(idx_mid) >0 ):  cfracm[i] = np.max( cfr[i,idx_mid] )
      if (len(idx_high) >0 ): cfrach[i] = np.max( cfr[i,idx_high] )

   tmp = np.vstack( (cfracl,cfracm,cfrach)) # stack the rows into one 2d array
   cldfra_max = np.max(tmp,axis=0) # get maximum value across low/mid/high for each pixel (minimum overlap assumption)

   # This is the fortran code put into python format...double loop unnecessary and slow
   #for i in range(0,nlocs):
   #   for k in range(0,nlevs):
   #      if pmid(i,k) >= PTOP_LOW:
   #	 cfracl(i) = np.max( [cfracl(i),cfr(i,k)] ) # Low
   #      elif pmid(i,k) < PTOP_LOW and pmid(i,k) >= PTOP_MID:
   #	 cfracm(i) = np.max( [cfracm(i),cfr(i,k)] ) # Mid
   #      elif pmid(i,k) < PTOP_MID and pmid(i,k) >= PTOP_HIGH: # High
   #	 cfrach(i) = np.max( [cfrach(i),cfr(i,k)] )

   return cfracl, cfracm, cfrach, cldfra_max

def get_goes16_lat_lon(g16_data_file):

   # Start timer
   start_time = datetime.now(timezone.utc)

   # designate dataset
   g16nc = Dataset(g16_data_file, 'r')

   # GOES-R projection info and retrieving relevant constants
   proj_info = g16nc.variables['goes_imager_projection']
   lon_origin = proj_info.longitude_of_projection_origin
   H = proj_info.perspective_point_height+proj_info.semi_major_axis
   r_eq = proj_info.semi_major_axis
   r_pol = proj_info.semi_minor_axis

   # Data info
   lat_rad_1d = g16nc.variables['x'][:]
   lon_rad_1d = g16nc.variables['y'][:]

   # close file when finished
   g16nc.close()
   g16nc = None

   # create meshgrid filled with radian angles
   lat_rad,lon_rad = np.meshgrid(lat_rad_1d,lon_rad_1d)

   # lat/lon calc routine from satellite radian angle vectors

   lambda_0 = (lon_origin*np.pi)/180.0

   a_var = np.power(np.sin(lat_rad),2.0) + (np.power(np.cos(lat_rad),2.0)*(np.power(np.cos(lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(lon_rad),2.0))))
   b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
   c_var = (H**2.0)-(r_eq**2.0)

   r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

   s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
   s_y = - r_s*np.sin(lat_rad)
   s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

   lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*(s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y)))))
   lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)

   # End timer
   end_time = datetime.now(timezone.utc)
   time = (end_time - start_time).microseconds / (1000.0*1000.0)
   print('took %f4.1 seconds to get GOES16 lat/lon'%(time))

   return lon,lat # lat/lon are 2-d arrays

# --
def get_goes_retrival_data(goes_file, goes_var):

   if not os.path.exists(goes_file):
      print(goes_file + ' not there. exit')
      sys.exit()

   # First get GOES lat/lon
   goes_lon2d, goes_lat2d = get_goes16_lat_lon(goes_file) # 2-d arrays
   goes_lon = goes_lon2d.flatten() # 1-d arrays
   goes_lat = goes_lat2d.flatten()

   # Now open the file and get the data we want
   nc_goes = Dataset(goes_file, "r", format="NETCDF4")

   # If the next line is true (it should be), this indicates the variable needs to be treated
   #  as an "unsigned 16-bit integer". This is a pain.  So we must use the "astype" method
   #  to change the variable type BEFORE applying scale_factor and add_offset.  After the conversion
   #  we then can manually apply the scale factor and offset
   #goesVar = 'PRES'
   goes_var = goes_var.strip() # for safety
   if nc_goes.variables[goes_var]._Unsigned.lower().strip() == 'true':
      nc_goes.set_auto_scale(False) # Don't automatically apply scale_factor and add_offset to variable
      goes_data2d = np.array(nc_goes.variables[goes_var]).astype(np.uint16)
      goes_data2d = goes_data2d * nc_goes.variables[goes_var].scale_factor + nc_goes.variables[goes_var].add_offset
      goes_qc2d  = np.array( nc_goes.variables['DQF']).astype(np.uint8)
   else:
      goes_data2d = np.array(nc_goes.variables[goes_var])
      goes_qc2d  = np.array( nc_goes.variables['DQF'])

   # Make variables 1-d
   goes_qc  = goes_qc2d.flatten()
   goes_data = goes_data2d.flatten()
   nc_goes.close()

   # Get rid of NaNs; base it on longitude
   goes_data = goes_data[~np.isnan(goes_lon)] # Handle data arrays first before changing lat/lon itself
   goes_qc  = goes_qc[~np.isnan(goes_lon)]
   goes_lon = goes_lon[~np.isnan(goes_lon)] # ~ is "logical not", also np.logical_not
   goes_lat = goes_lat[~np.isnan(goes_lat)]
   if goes_lon.shape != goes_lat.shape:
      print('GOES lat/lon shape mismatch')
      sys.exit()

   # If goes_qc == 0, good QC and there was a cloud with a valid pressure.
   # If goes_qc == 4, no cloud; probably clear sky.
   # All other QC means no data, and we want to remove those points
   idx = np.logical_or( goes_qc == 0, goes_qc == 4) # Only keep QC == 0 or 4
   goes_data = goes_data[idx]
   goes_qc  = goes_qc[idx]
   goes_lon = goes_lon[idx]
   goes_lat = goes_lat[idx]

   # Only QC with 0 or 4 are left; now set QC == 4 to missing to indicate clear sky
   goes_data = np.where( goes_qc != 0, missing_values, goes_data)

   # Get longitude to between (0,360) for consistency with JEDI files (this check is applied to JEDI files, too)
   goes_lon = np.where( goes_lon < 0, goes_lon + 360.0, goes_lon )

   print('Min GOES Lon = ',np.min(goes_lon))
   print('Max GOES Lon = ',np.max(goes_lon))

   return goes_lon, goes_lat, goes_data

###########
def get_grid_info(source, grid_type):

   if grid_type == 'LatLon':
      lat_def = griddedDatasets[source]['latDef']
      lon_def = griddedDatasets[source]['lonDef']
      grid_info = {
         'type':      grid_type,
         'name':      source,
         'lat_ll':    lat_def[0], #-90.000,
         'lon_ll':    lon_def[0], #-180.000,
         'delta_lat': lat_def[1], #0.5000,
         'delta_lon': lon_def[1], #0.625,
         'Nlat':      lat_def[2], #361,
         'Nlon':      lon_def[2], #576,
      }
   elif grid_type == 'Gaussian':
      grid_info = {
        'type':     grid_type,
        'name':     source,
        'nx':       griddedDatasets[source]['nx'],
        'ny':       griddedDatasets[source]['ny'],
        'lon_zero': griddedDatasets[source]['lon_zero'],
      }
 
   return grid_info

def get_attr_array(source, variable, init_time, valid_time):

   init = datetime.strptime(init_time, "%Y%m%d%H")
   valid = datetime.strptime(valid_time, "%Y%m%d%H")
   lead, _ = divmod((valid-init).total_seconds(), 3600)

   attrs = {

      'valid': valid.strftime("%Y%m%d_%H%M%S"),
      'init':  init.strftime("%Y%m%d_%H%M%S"),
      'lead':  str(int(lead)),
      'accum': '000000',

      'name':      variable,  #'MERRA2_Cloud_Percentage'
      'long_name': variable,  #'Cloud Percentage Levels',
      'level':     'ALL',
      'units':     verifVariables[variable]['units'],

      'grid': get_grid_info(source, griddedDatasets[source]['gridType'])
   }

   return attrs

######## END FUNCTIONS   ##########


#if __name__ == "__main__":
dataFile, dataSource, variable, i_date, v_date, flag = sys.argv[1].split(":")
met_data = get_data_array(dataFile, dataSource, variable, flag)
attrs = get_attr_array(dataSource, variable, i_date, v_date)
print(attrs)
