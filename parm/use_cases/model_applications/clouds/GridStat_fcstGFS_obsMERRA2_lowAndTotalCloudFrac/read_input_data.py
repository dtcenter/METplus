#this code was provided by Craig Schwartz
#and is largely unaltered from its original
#function.

#from __future__ import print_function
import os
import sys
import numpy as np
import datetime as dt
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from scipy.interpolate import NearestNDInterpolator, LinearNDInterpolator
#### for Plotting
import matplotlib.cm as cm
import matplotlib.axes as maxes
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mpl_toolkits.basemap import Basemap
import fnmatch
import pygrib
import pickle as pk
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
   #TODO:Correct one, but MET can ingest a Gaussian grid only in Grib2 format (from Randy B.)
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

def getThreshold(variable):
   x = verifVariables[variable]['thresholds']
   print(x) # needed for python 3 to read variable into csh variable
   return x

def getInterpMethod(variable):
   x = verifVariables[variable]['interpMethod'].upper()
   print(x) # needed for python 3 to read variable into csh variable
   return x

def getTotalCloudFrac(source,data):
   if source == 'SATCORPS':
    # x = data[0][0,:,:,0] * 1.0E-2  # scaling
      x = (data[0][0,:,:,1]  + data[0][0,:,:,2] + data[0][0,:,:,3])*1.0E-2  # scaling
   #  y = data[0]
   #  x = np.sum( y[:,:,:,1:4],axis=3)
   elif source == 'MERRA2':
#      x = ( data[0][0,:,:]+data[1][0,:,:]+data[2][0,:,:] ) *100.0 # the ith element of data is a numpy array
      x = data[0][0,:,:] * 100.0 # the ith element of data is a numpy array
      print(x.min(), x.max())
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] * 100.0
      except: x = data[0][0,:,:] * 100.0
   elif source == 'MPAS':
      x = data[0][0,:,:] * 100.0
   elif source == 'SAT_WWMCA_MEAN':
      x = data[0][0,:,:] # already in %
   else:
      x = data[0]

   # This next line is WRONG.
   # Missing should be set to missing
   # Then, the non-missing values are 1s and 0s
   #output = np.where(x > 0.0, x, 0.0)
   #output = np.where(x < 0.0, -9999.0, x) # missing. currently used for SATCORPS

   x = np.where( x < 0.0  , 0.0,   x) # Force negative values to zero
   x = np.where( x > 100.0, 100.0, x) # Force values > 100% to 100%
   return x

def getBinaryCloud(source,data):
   y = getTotalCloudFrac(source,data)
   # keep NaNs as is, but then set everything else to either 100% or 0%
   x = np.where( np.isnan(y), y, np.where(y > 0.0, 100.0, 0.0) )
   return x

def getLayerCloudFrac(source,data,layer):
   if source == 'SATCORPS':
      if layer.lower().strip() == 'low'  : i = 1
      if layer.lower().strip() == 'mid'  : i = 2
      if layer.lower().strip() == 'high' : i = 3
      x = data[0][0,:,:,i] * 1.0E-2  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] * 100.0
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] * 100.0
      except: x = data[0][0,:,:] * 100.0
   elif source == 'MPAS':
      x = data[0][0,:,:] * 100.0
   else:
      x = data[0]

   x = np.where( x < 0.0, 0.0, x) # Force negative values to zero
   x = np.where( x > 100.0, 100.0, x) # Force values > 100% to 100%

   return x

def getCloudTopTemp(source,data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E-2  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] 
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except: x = data[0][0,:,:]
   else:
      x = data[0]
   return x

def getCloudTopPres(source,data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E-1  # scaling
   elif source == 'MERRA2':
      x = data[0][0,:,:] * 1.0E-2  # scaling [Pa] -> [hPa]
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except: x = data[0][0,:,:]
   else:
      x = data[0]
   return x

def getCloudTopHeight(source,data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E+1  # scaling to [meters]
   elif source == 'MERRA2':
      x = data[0][0,:,:]     #TBD
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except: x = data[0][0,:,:]
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
      x = np.nanmax(tmp,axis=0) # get maximum cloud top height across all layers
   else:
      x = data[0]

   # Eliminate unphysical values (assume cloud top shouldn't be > 50000 meters)
   y = np.where( x > 50000.0 , np.nan, x )

   return y

def getCloudBaseHeight(source,data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0] * 1.0E+1  # scaling to [meters]
   elif source == 'MERRA2':
      x = data[0][0,:,:]     #TBD
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:]
      except: x = data[0][0,:,:]
   elif source == 'GALWEM17':
      x = data[0] * 1000.0 * 0.3048  # kilofeet -> meters
   elif source == 'MPAS':
      x = data[0][0,:,:] # already in meters
   elif source == 'WWMCA':
      # data is a list (should be length 4)
      if len(data) != 4:
         print('error with WWMCA Cloud base height')
         sys.exit()
      tmp = np.array(data) # already in meters
      tmp = np.where( tmp <= 0, np.nan, tmp) # replace 0 or negative values with NAN
      x = np.nanmin(tmp,axis=0) # get lowest cloud base over all layers
   else:
      x = data[0]

   # Eliminate unphysical values (assume cloud base shouldn't be > 50000 meters)
   y = np.where( x > 50000.0 , np.nan, x )

   return y

def getCloudCeiling(source,data):
   if source == 'SATCORPS':
      x = data[0][0,:,:,0]   #TBD
   elif source == 'MERRA2':
      x = data[0][0,:,:]     #TBD
   elif source == 'ERA5':
      try:    x = data[0][0,0,:,:] # TBD
      except: x = data[0][0,:,:]
   return x

# add other functions for different variables

###########

def getDataArray(inputFile,source,variable,dataSource):
   # 1) inputFile:  File name--either observations or forecast
   # 2) source:     Obsevation source (e.g., MERRA, SATCORP, etc.)
   # 3) variable:   Variable to verify
   # 4) dataSource: If 1, process forecast file. If 2 process obs file.

#   # specifying names here temporarily. file names should be passed in to python from shell script
#   if source == 'merra':      nc_file = '/gpfs/fs1/scratch/schwartz/MERRA/MERRA2_400.tavg1_2d_rad_Nx.20181101.nc4'
#   elif source == 'satcorp':  nc_file = '/glade/scratch/bjung/met/test_satcorps/GEO-MRGD.2018334.0000.GRID.NC'
#   elif source == 'era5':     nc_file = '/glade/scratch/bjung/met/test_era5/e5.oper.fc.sfc.instan.128_164_tcc.regn320sc.2018111606_2018120112.nc'

   source = source.upper().strip()  # Force uppercase and get rid of blank spaces, for safety

   print('dataSource = ',dataSource)

   ftype = griddedDatasets[source]['ftype'].lower().strip()

   # Get file handle
   if ftype == 'nc':
      nc_fid = Dataset(inputFile, "r", format="NETCDF4")
      #nc_fid.set_auto_scale(True)
   elif ftype == 'grib':
      if source == 'WWMCA':
        idx = pygrib.index(inputFile,'parameterName','typeOfLevel','level')
      else:
        idx = pygrib.index(inputFile,'parameterCategory','parameterNumber','typeOfFirstFixedSurface')

   # dataSource == 1 means forecast, 2 means obs
#  if dataSource == 1: varsToRead = verifVariablesModel[variable][source] # if ftype == 'grib', returns a list whose ith element is a dictionary. otherwise, just a list
#  if dataSource == 2: varsToRead = verifVariables[variable][source] # returns a list
   varsToRead = verifVariables[variable][source] # if ftype == 'grib', returns a list whose ith element is a dictionary. otherwise, just a list

   print('Trying to read ',inputFile)

   # Get lat/lon information--currently not used
  #latVar = griddedDatasets[source]['latVar']
  #lonVar = griddedDatasets[source]['lonVar']
  #lats = np.array(nc_fid.variables[latVar][:])   # extract/copy the data
  #lons = np.array(nc_fid.variables[lonVar][:] )

   #print(lats.max())
   #print(lons.max())

   # one way to deal with scale factors
   # probably using something like nc_fid.set_auto_scale(True) is better...
  #latMax = lats.max()
  #while latMax > 90.0:
  #   lons = lons * 0.1
  #   lats = lats * 0.1
  #   latMax = lats.max()

   # get data
   data = []
   for v in varsToRead:
      if ftype == 'grib':
         if source == 'WWMCA':
           x = idx(parameterName=v['parameterName'],typeOfLevel=v['typeOfLevel'],level=v['level'])[0] # by getting element 0, you get a pygrib message
         else:
            # e.g., idx(parameterCategory=6,parameterNumber=1,typeOfFirstFixedSurface=234)
            if ( variable == 'cloudTopHeight' or variable == 'cloudBaseHeight') and source == 'GALWEM17': 
               x = idx(parameterCategory=v['parameterCategory'],parameterNumber=v['parameterNumber'],typeOfFirstFixedSurface=v['typeOfFirstFixedSurface'])[1] # by getting element 1, you get a pygrib message
            else:
               x = idx(parameterCategory=v['parameterCategory'],parameterNumber=v['parameterNumber'],typeOfFirstFixedSurface=v['typeOfFirstFixedSurface'])[0] # by getting element 0, you get a pygrib message
            if x.shortName != v['shortName']: print('Name mismatch!')
            #ADDED BY JOHN O
            print(x)
            print('Reading ', x.shortName, 'at level ', x.typeOfFirstFixedSurface)
         read_var = x.values # same x.data()[0]
         read_missing = x.missingValue
         print('missing value = ',read_missing)

         # The missing value (read_missing) for GALWEM17 and GALWEM cloud base/height is 9999, which is not the best choice because
         # those could be actual values. So we need to use the masked array part (below) to handle which
         # values are missing.  We also set read_missing to something unphysical to essentially disable it.
         # Finally, if we don't change the 'missingValue' property in the GRIB2 file we are eventually outputting,
         # the bitmap will get all messed up, because it will be based on 9999 instead of $missing_values
         if variable == 'cloudTopHeight' or variable == 'cloudBaseHeight':
            read_missing = -9999.
            x['missingValue'] = read_missing
            if source == 'GALWEM17':
               #These are masked numpy arrays, with mask = True where there is a missing value (no cloud)
               #Use np.ma.filled to create an ndarray where mask = True values are set to np.nan
               read_var = np.ma.filled(read_var.astype(read_var.dtype), np.nan)
      elif ftype == 'nc':
         read_var = nc_fid.variables[v]         # extract/copy the data
         try:
            read_missing = read_var.missing_value  # get variable attributes. Each dataset has own missing values.
         except:
            read_missing = -9999. # set a default missing value. probably only need to do this for MPAS

      print('Reading ', v)

      this_var = np.array( read_var )        # to numpy array
     #print(read_missing, np.nan)
      this_var = np.where( this_var==read_missing, np.nan, this_var )
     #print(this_var.shape)
      data.append(this_var) # ith element of the list is a NUMPY ARRAY for the ith variable
     #print(type(this_var))
     #print(type(data))

   # Call a function to get the variable of interest.
   # Add a new function for each variable
   if variable == 'binaryCloud':     raw_data = getBinaryCloud(source,data)
   if variable == 'totalCloudFrac':  raw_data = getTotalCloudFrac(source,data)
   if variable == 'lowCloudFrac':    raw_data = getLayerCloudFrac(source,data,'low')
   if variable == 'midCloudFrac':    raw_data = getLayerCloudFrac(source,data,'mid')
   if variable == 'highCloudFrac':   raw_data = getLayerCloudFrac(source,data,'high')
   if variable == 'cloudTopTemp':    raw_data = getCloudTopTemp(source,data)
   if variable == 'cloudTopPres':    raw_data = getCloudTopPres(source,data)
   if variable == 'cloudTopHeight':  raw_data = getCloudTopHeight(source,data)
   if variable == 'cloudBaseHeight': raw_data = getCloudBaseHeight(source,data)
   if variable == 'cloudCeiling':    raw_data = getCloudCeiling(source,data)

   raw_data = np.where(np.isnan(raw_data), missing_values, raw_data) # replace np.nan to missing_values (for MET)

   # Array met_data is passed to MET
   # Graphics should plot $met_data to make sure things look correct
   if griddedDatasets[source]['flipY']: 
      print('flipping ',source,' data about y-axis')
      met_data=np.flip(raw_data,axis=0).astype(float)
   else:
      met_data=raw_data.astype(float)

   # Make plotting optional or Just use plot_data_plane
#   plt_data=np.where(met_data<0, np.nan, met_data)
#   map=Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c')
#   map.drawcoastlines()
#   map.drawcountries()
#   map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1])
#   map.drawmeridians(np.arange(0,360,60),labels=[1,1,0,1])
#   plt.contourf(lons,lats,plt_data,20,origin='upper',cmap=cm.Greens) #cm.gist_rainbow)
#   title=source+"_"+variable+"_"+str(validTime)
#   plt.title(title)
#   plt.colorbar(orientation='horizontal')
#   plt.savefig(title+".png")

   # If a forecast file, output a GRIB file with 
   # 1 record containing the met_data
   # This is a hack, because right now, MET python embedding doesn't work with pygrib,
   #    so output the data to a temporary file, and then have MET read the temporary grib file.
   # Starting with version 9.0 of MET, the hack isn't needed, and MET python embedding works with pygrib
   outputFcstFile = False  # MUST be True for MET version < 9.0.  For MET 9.0+, optional
   if dataSource == 1 and ftype == 'grib': 
      if outputFcstFile:
         grbtmp = x
         grbtmp['values']=met_data
         grbout = open('temp_fcst.grb2','ab')
         grbout.write(grbtmp.tostring())
         grbout.close() # Close the outfile GRIB file
         print('Successfully output temp_fcst.grb2')

   # Close files
   if ftype == 'grib': idx.close()    # Close the input GRIB file
   if ftype == 'nc':   nc_fid.close() # Close the netCDF file

   return met_data

def obsError(fcstData,obsErrorFile,validDate,dataSource):

   print('Adding noise to the cloud fraction fields')
   print('Using obsErrorFile',obsErrorFile)

   # First load the obsError information
   #obsErrorFile = 'ob_errors.pk'
   infile = open(obsErrorFile,'rb')
   binEdges, binStddev = pk.load(infile) # 'numpy.ndarray' types
   infile.close()

   # Get 1d forecast data
   shape = fcstData.shape
   fcst = fcstData.flatten()

   # Set random number seed based on valid time and model
   if   dataSource.upper().strip() == 'MPAS':   ii = 10
   elif dataSource.upper().strip() == 'GALWEM': ii = 20
   elif dataSource.upper().strip() == 'GFS':    ii = 30
   np.random.seed(int(validDate*.1 + ii)) 

   # Find which bin the data is in
   for i in range(0,len(binEdges)-1):
      idx = np.where( (fcst >= binEdges[i]) & (fcst < binEdges[i+1]) )[0]
      n = len(idx) # number of points in the ith bin
      if n > 0: # check for empty bins
         randVals = np.random.normal(0,binStddev[i],n)
         fcst[idx] = fcst[idx] + randVals

   # bound forecast values to between 0 and 100%
   fcst = np.where( fcst < 0.0,     0.0,   fcst)
   fcst = np.where( fcst > 100.0,   100.0, fcst)

   # now reshape forecast data back to 2D
   output = fcst.reshape(shape)
   
   # data will have NaNs where bad.
   return output

def getFcstCloudFrac(cfr,pmid,psfc,layerDefinitions): # cfr is cloud fraction(%), pmid is 3D pressure(Pa), psfc is surface pressure (Pa) code from UPP ./INITPOST.F

   if pmid.shape != cfr.shape:  # sanity check
      print('dimension mismatch bewteen cldfra and pressure')
      sys.exit()

   nlocs, nlevs = pmid.shape

   if len(psfc) != nlocs: # another sanity check
      print('dimension mismatch bewteen cldfra and surface pressure')
      sys.exit()

   cfracl = np.zeros(nlocs)
   cfracm = np.zeros(nlocs)
   cfrach = np.zeros(nlocs)

   for i in range(0,nlocs):

      PTOP_HIGH = PTOP_HIGH_UPP
      if layerDefinitions.upper().strip() == 'ERA5':
         PTOP_LOW = 0.8*psfc[i]
         PTOP_MID = 0.45*psfc[i]
      elif layerDefinitions.upper().strip() == 'UPP':
         PTOP_LOW = PTOP_LOW_UPP
         PTOP_MID = PTOP_MID_UPP

      idxLow  = np.where(   pmid[i,:] >= PTOP_LOW)[0] # using np.where with just 1 argument returns tuple
      idxMid  = np.where(  (pmid[i,:] <  PTOP_LOW) & (pmid[i,:] >= PTOP_MID))[0]
      idxHigh = np.where(  (pmid[i,:] <  PTOP_MID) & (pmid[i,:] >= PTOP_HIGH))[0]

      # use conditions in case all indices are missing
      if (len(idxLow) >0 ):  cfracl[i] = np.max( cfr[i,idxLow] )
      if (len(idxMid) >0 ):  cfracm[i] = np.max( cfr[i,idxMid] )
      if (len(idxHigh) >0 ): cfrach[i] = np.max( cfr[i,idxHigh] )

   tmp = np.vstack( (cfracl,cfracm,cfrach)) # stack the rows into one 2d array
   cldfraMax = np.max(tmp,axis=0) # get maximum value across low/mid/high for each pixel (minimum overlap assumption)

   # This is the fortran code put into python format...double loop unnecessary and slow
   #for i in range(0,nlocs):
   #   for k in range(0,nlevs):
   #      if pmid(i,k) >= PTOP_LOW:
   #	 cfracl(i) = np.max( [cfracl(i),cfr(i,k)] ) # Low
   #      elif pmid(i,k) < PTOP_LOW and pmid(i,k) >= PTOP_MID:
   #	 cfracm(i) = np.max( [cfracm(i),cfr(i,k)] ) # Mid
   #      elif pmid(i,k) < PTOP_MID and pmid(i,k) >= PTOP_HIGH: # High
   #	 cfrach(i) = np.max( [cfrach(i),cfr(i,k)] )

   return cfracl, cfracm, cfrach, cldfraMax

def getGOES16LatLon(g16_data_file):

   # Start timer
   startTime = dt.datetime.utcnow()

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

   lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
   lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)

   # End timer
   endTime = dt.datetime.utcnow()
   time = (endTime - startTime).microseconds / (1000.0*1000.0)
   print('took %f4.1 seconds to get GOES16 lat/lon'%(time))

   return lon,lat # lat/lon are 2-d arrays

# --
def getGOESRetrivalData(goesFile,goesVar):

   if not os.path.exists(goesFile):
      print(goesFile+' not there. exit')
      sys.exit()

   # First get GOES lat/lon
   goesLon2d, goesLat2d = getGOES16LatLon(goesFile) # 2-d arrays
   goesLon = goesLon2d.flatten() # 1-d arrays
   goesLat = goesLat2d.flatten()

   # Now open the file and get the data we want
   nc_goes = Dataset(goesFile, "r", format="NETCDF4")

   # If the next line is true (it should be), this indicates the variable needs to be treated
   #  as an "unsigned 16-bit integer". This is a pain.  So we must use the "astype" method
   #  to change the variable type BEFORE applying scale_factor and add_offset.  After the conversion
   #  we then can manually apply the scale factor and offset
   #goesVar = 'PRES'
   goesVar = goesVar.strip() # for safety
   if nc_goes.variables[goesVar]._Unsigned.lower().strip() == 'true':
      nc_goes.set_auto_scale(False) # Don't automatically apply scale_factor and add_offset to variable
      goesData2d = np.array( nc_goes.variables[goesVar]).astype(np.uint16)
      goesData2d = goesData2d * nc_goes.variables[goesVar].scale_factor + nc_goes.variables[goesVar].add_offset
      goesQC2d  = np.array( nc_goes.variables['DQF']).astype(np.uint8)
   else:
      goesData2d = np.array( nc_goes.variables[goesVar])
      goesQC2d  = np.array( nc_goes.variables['DQF'])

   # Make variables 1-d
   goesQC  = goesQC2d.flatten()
   goesData = goesData2d.flatten()
   nc_goes.close()

   # Get rid of NaNs; base it on longitude
   goesData = goesData[~np.isnan(goesLon)] # Handle data arrays first before changing lat/lon itself
   goesQC  = goesQC[~np.isnan(goesLon)]
   goesLon = goesLon[~np.isnan(goesLon)] # ~ is "logical not", also np.logical_not
   goesLat = goesLat[~np.isnan(goesLat)]
   if goesLon.shape != goesLat.shape:
      print('GOES lat/lon shape mismatch')
      sys.exit()

   # If goesQC == 0, good QC and there was a cloud with a valid pressure.
   # If goesQC == 4, no cloud; probably clear sky.
   # All other QC means no data, and we want to remove those points
   idx = np.logical_or( goesQC == 0, goesQC == 4) # Only keep QC == 0 or 4
   goesData = goesData[idx]
   goesQC  = goesQC[idx]
   goesLon = goesLon[idx]
   goesLat = goesLat[idx]

   # Only QC with 0 or 4 are left; now set QC == 4 to missing to indicate clear sky
   goesData = np.where( goesQC != 0, missing_values, goesData)

   # Get longitude to between (0,360) for consistency with JEDI files (this check is applied to JEDI files, too)
   goesLon = np.where( goesLon < 0, goesLon + 360.0, goesLon )

   print('Min GOES Lon = ',np.min(goesLon))
   print('Max GOES Lon = ',np.max(goesLon))

   return goesLon, goesLat, goesData

def point2point(source,inputDir,satellite,channel,goesFile,condition,layerDefinitions,dataSource):

   # Static Variables for QC and obs
   qcVar  = 'brightness_temperature_'+str(channel)+'@EffectiveQC' #'@EffectiveQC0' # QC variable
   obsVar = 'brightness_temperature_'+str(channel)+'@ObsValue'  # Observation variable

   # Get GOES-16 retrieval file with auxiliary information
   if 'abi' in satellite or 'ahi' in satellite:
      goesLon, goesLat, goesData = getGOESRetrivalData(goesFile,'PRES') # return 1-d arrays
      lonlatGOES = np.array( list(zip(goesLon, goesLat))) # lon/lat pairs for each GOES ob (nobs_GOES, 2)
     #print('shape lonlatGOES = ',lonlatGOES.shape)
      print('getting data from ',goesFile)
      myGOESInterpolator = NearestNDInterpolator(lonlatGOES,goesData)

   # First check to see if there's a concatenated file with all obs.
   #  If so, use that.  If not, have to process one file per processor, which takes a lot more time
   if os.path.exists(inputDir+'/obsout_omb_'+satellite+'_ALL.nc4'):
      inputFiles =  [inputDir+'/obsout_omb_'+satellite+'_ALL.nc4'] # needs to be in a list since we loop over inputFiles
   else:
      # Get list of OMB files to process.  There is one file per processor.
      # Need to get them in order so they are called in the same order for the 
      # forecast and observed passes through this subroutine.
      files = os.listdir(inputDir)
      inputFiles = fnmatch.filter(files,'obsout*_'+satellite+'*nc4') # returns relative path names
      inputFiles = [inputDir+'/'+s for s in inputFiles] # add on directory name
      inputFiles.sort() # Get in order from low to high
   if len(inputFiles) == 0: return -99999, -99999 # if no matching files, force a failure

   # Variable to pull for brightness temperature
#  if dataSource == 1: v = 'brightness_temperature_'+str(channel)+'@GsiHofXBc' # Forecast variable
   if dataSource == 1: v = 'brightness_temperature_'+str(channel)+'@hofx' #'@depbg' # OMB
   if dataSource == 2: v = obsVar

   # Read the files and put data in array
   allData, allDataQC = [], []
   for inputFile in inputFiles:
      nc_fid = Dataset(inputFile, "r", format="NETCDF4") #Dataset is the class behavior to open the file
      print('Trying to read ',v,' from ',inputFile)

      # Read forecast/obs data
      read_var = nc_fid.variables[v]         # extract/copy the data
   #  read_missing = read_var.missing_value  # get variable attributes. Each dataset has own missing values.
      this_var = np.array( read_var )        # to numpy array
   #  this_var = np.where( this_var==read_missing, np.nan, this_var )

     #if dataSource == 1: # If true, we just read in OMB data, but we want B
     #   obsData = np.array( nc_fid.variables[obsVar])
     #   this_var = obsData - this_var # get background/forecast value (O - OMB = B)

      #Read QC data
      qcData = np.array(nc_fid.variables[qcVar])

      # Sanity check...shapes should match
      if qcData.shape != this_var.shape: return -99999, -99999

      if 'abi' in satellite or 'ahi' in satellite:

         # Get the GOES-16 retrieval data at the observation locations in this file
         #   GOES values < 0 mean clear sky
         lats = np.array(nc_fid.variables['latitude@MetaData'])
         lons = np.array(nc_fid.variables['longitude@MetaData'])

	 # Get longitude to between (0,360) for consistency with GOES-16 files
         lons = np.where( lons < 0, lons + 360.0, lons )

         lonlat = np.array( list(zip(lons,lats)))  # lon/lat pairs for each ob (nobs, 2)
         thisGOESData = myGOESInterpolator(lonlat) # GOES data at obs locations in this file. If pressure, units are hPa
         thisGOESData = thisGOESData * 100.0 # get into Pa

         #obsCldfra = np.array( nc_fid.variables['cloud_area_fraction@MetaData'] )*100.0 # Get into %...observed cloud fraction (AHI/ABI only)

         geoValsFile = inputFile.replace('obsout','geoval')
         if not os.path.exists(geoValsFile):
            print(geoValsFile+' not there. exit')
            sys.exit()

         nc_fid2 = Dataset(geoValsFile, "r", format="NETCDF4")
         fcstCldfra = np.array( nc_fid2.variables['cloud_area_fraction_in_atmosphere_layer'])*100.0 # Get into %
         pressure   = np.array( nc_fid2.variables['air_pressure']) # Pa
         pressure_edges   = np.array( nc_fid2.variables['air_pressure_levels']) # Pa
         psfc = pressure_edges[:,-1]  # Surface pressure (Pa)...array order is top down
         if layerDefinitions.upper().strip() == 'ERA5':
            PTOP_LOW = 0.8*psfc # these are arrays
            PTOP_MID = 0.45*psfc
            PTOP_HIGH = PTOP_HIGH_UPP * np.ones_like(psfc)
         elif layerDefinitions.upper().strip() == 'UPP':
            PTOP_LOW = PTOP_LOW_UPP # these are constants
            PTOP_MID = PTOP_MID_UPP
            PTOP_HIGH = PTOP_HIGH_UPP
         else:
            print('layerDefinitions = ',layerDefinitions,'is invalid. exit')
            sys.exit()
         fcstLow,fcstMid,fcstHigh,fcstTotCldFra = getFcstCloudFrac(fcstCldfra,pressure,psfc,layerDefinitions) # get low/mid/high/total forecast cloud fractions for each ob
         nc_fid2.close()

	 # Modify QC data based on correspondence between forecast and obs. qcData used to select good data later
         # It's possible that there are multiple forecast layers, such that fcstLow,fcstMid,fcstHigh are all > $cldfraThresh
         # However, GOES-16 CTP doesn't really account for layering.  So, we need to remove layered clouds from the forecast, 
	 #   focusing only on the layers that we asked for when doing {low,mid,high}Only conditions
	 # The "|" is symbol for "np.logcal_or"
         yes = 2.0
         no  = 0.0
         cldfraThresh = 20.0 # percent
         if qcData.shape == fcstTotCldFra.shape == thisGOESData.shape:  # these should all match
            print('Using condition ',condition,'for ABI/AHI')

	    # Note that "&" is "np.logical_and" for boolean (true/false) quantities.
	    # Thus, each condition should be enclosed in parentheses
            if   condition.lower().strip() == 'clearOnly'.lower():  # clear in both forecast and obs
               qcData = np.where( (fcstTotCldFra < cldfraThresh)  & (thisGOESData <= 0.0), qcData, missing_values)
            elif condition.lower().strip() == 'cloudyOnly'.lower(): # cloudy in both forecast and obs
               qcData = np.where( (fcstTotCldFra >= cldfraThresh) & (thisGOESData > 0.0), qcData, missing_values)
            elif condition.lower().strip() == 'lowOnly'.lower(): # low clouds in both forecast and obs
               fcstLow = np.where( (fcstMid >= cldfraThresh) | ( fcstHigh >= cldfraThresh), missing_values, fcstLow) # remove mid, high
               qcData = np.where( (fcstLow >= cldfraThresh) & ( thisGOESData >= PTOP_LOW), qcData, missing_values)
            elif condition.lower().strip() == 'midOnly'.lower(): # mid clouds in both forecast and obs
               fcstMid = np.where( (fcstLow >= cldfraThresh) | ( fcstHigh >= cldfraThresh), missing_values, fcstMid) # remove low, high
               qcData = np.where( (fcstMid >= cldfraThresh) & (thisGOESData <  PTOP_LOW) & (thisGOESData >= PTOP_MID),   qcData, missing_values)
            elif condition.lower().strip() == 'highOnly'.lower(): # high clouds in both forecast and obs
               fcstHigh = np.where( (fcstLow >= cldfraThresh) | ( fcstMid >= cldfraThresh), missing_values, fcstHigh) # remove mid, high
               qcData = np.where( (fcstHigh >= cldfraThresh) & (thisGOESData <  PTOP_MID) & (thisGOESData >= PTOP_HIGH), qcData, missing_values)
            elif condition.lower().strip() == 'fcstLow'.lower(): # low clouds in forecast (layers possible); obs could be anything
               qcData = np.where( fcstLow >= cldfraThresh , qcData, missing_values)
            elif condition.lower().strip() == 'fcstMid'.lower(): # low clouds in forecast (layers possible); obs could be anything
               qcData = np.where( fcstMid >= cldfraThresh , qcData, missing_values)
            elif condition.lower().strip() == 'fcstHigh'.lower(): # low clouds in forecast (layers possible); obs could be anything
               qcData = np.where( fcstHigh >= cldfraThresh , qcData, missing_values)
            elif condition.lower().strip() == 'cloudEventLow'.lower():
               if dataSource == 1: this_var = np.where( fcstLow      >= cldfraThresh, yes, no ) # set cloudy points to 2, clear points to 0, use threshold of 1 in MET
               if dataSource == 2: this_var = np.where( thisGOESData >= PTOP_LOW, yes, no )
            elif condition.lower().strip() == 'cloudEventMid'.lower():
               if dataSource == 1: this_var = np.where( fcstMid      >= cldfraThresh, yes, no ) # set cloudy points to 2, clear points to 0, use threshold of 1 in MET
               if dataSource == 2: this_var = np.where( (thisGOESData <  PTOP_LOW) & (thisGOESData >= PTOP_MID), yes, no )
            elif condition.lower().strip() == 'cloudEventHigh'.lower():
               if dataSource == 1: this_var = np.where( fcstHigh     >= cldfraThresh, yes, no ) # set cloudy points to 2, clear points to 0, use threshold of 1 in MET
               if dataSource == 2: this_var = np.where( (thisGOESData <  PTOP_MID) & (thisGOESData >= PTOP_HIGH), yes, no )
            elif condition.lower().strip() == 'cloudEventTot'.lower():
               if dataSource == 1: this_var = np.where( fcstTotCldFra >= cldfraThresh, yes, no ) # set cloudy points to 2, clear points to 0, use threshold of 1 in MET
               if dataSource == 2: this_var = np.where( thisGOESData  > 0.0, yes, no ) 
            elif condition.lower().strip() == 'all':
               print("not doing any conditional verification or stratifying by event")
            else:
               print("condition = ",condition," not recognized.")
               sys.exit()
            #elif condition.lower().strip() == '4x4table'.lower():
              #if dataSource == 1:
	      #   this_var = np.where( fcstLow >= cldfraThresh, yesLow, no )
	      #   this_var = this_var + np.where( fcstMid >= cldfraThresh, yesMid, no )
	      #   this_var = this_var + np.where( fcstHigh >= cldfraThresh, yesHigh, no )
            print('number removed = ', (qcData==missing_values).sum())
           #print('number passed   = ', qcData.shape[0] - (qcData==missing_values).sum())
         else:
            print('shape mismatch')
            return -99999, -99999
	   
      # Append to arrays
      allData.append(this_var)
      allDataQC.append(qcData)

      nc_fid.close() # done with the file, so close it before going to next file in loop

   # We're now all done looping over the individul files

   # Get the indices with acceptable QC
   allQC = np.concatenate(allDataQC) # Put list of numpy arrays into a single long 1-D numpy array.  All QC data.
   idx = np.where(allQC==0) # returns indices

   # Now get all the forecast/observed brightness temperature data with acceptable QC
   this_var = np.concatenate(allData)[idx] # Put list of numpy arrays into a single long 1-D numpy array. This is all the forecast/obs data with good QC
   numObs = this_var.shape[0] # number of points with good QC for this channel
   print('Number of obs :',numObs)

   # Assume all the points actually fit into a square grid. Get the side of the square (use ceil to round up)
   if numObs > 0:
      l = np.ceil(np.sqrt(numObs)).astype('int') # Length of the side of the square

      # Make an array that can be reshaped into the square 
      raw_data1D = np.full(l*l,np.nan) # Initialize 1D array of length l**2 to np.nan
      raw_data1D[0:numObs] = this_var[:] # Fill data to the extent possible. There will be some np.nan values at the end
      raw_data = np.reshape(raw_data1D,(l,l)) # Reshape into "square grid"

      raw_data = np.where(np.isnan(raw_data), missing_values, raw_data) # replace np.nan to missing_values (for MET)

      met_data=raw_data.astype(float) # Give MET this info

      # Now need to tell MET the "grid" for the data
      # Make a fake lat/lon grid going from 0.0 to 50.0 degrees, with the interval determined by number of points
      griddedDatasets[source]['latDef'][0] = 0.0 # starting point
      griddedDatasets[source]['latDef'][1] = np.diff(np.linspace(0,50,l)).round(6)[0] # interval (degrees)
      griddedDatasets[source]['latDef'][2] = int(l) # number of points
      griddedDatasets[source]['lonDef'][0:3] = griddedDatasets[source]['latDef']

      gridInfo = getGridInfo(source, griddedDatasets[source]['gridType']) # 'LatLon' gridType
      return met_data, gridInfo

   else:
      return -99999, -99999

###########
def getGridInfo(source,gridType):

   if gridType == 'LatLon':
      latDef = griddedDatasets[source]['latDef']
      lonDef = griddedDatasets[source]['lonDef']
      gridInfo = {
         'type':      gridType,
         'name':      source,
         'lat_ll':    latDef[0], #-90.000,
         'lon_ll':    lonDef[0], #-180.000,
         'delta_lat': latDef[1], #0.5000,
         'delta_lon': lonDef[1], #0.625,
         'Nlat':      latDef[2], #361,
         'Nlon':      lonDef[2], #576,
      }
   elif gridType == 'Gaussian':
      gridInfo = {
        'type':     gridType,
        'name':     source,
        'nx':       griddedDatasets[source]['nx'],
        'ny':       griddedDatasets[source]['ny'],
        'lon_zero': griddedDatasets[source]['lon_zero'],
      }
 
   return gridInfo

def getAttrArray(source,variable,initTime,validTime):

   init = dt.datetime.strptime(initTime,"%Y%m%d%H")
   valid = dt.datetime.strptime(validTime,"%Y%m%d%H")
   lead, rem = divmod((valid-init).total_seconds(), 3600)

   attrs = {

      'valid': valid.strftime("%Y%m%d_%H%M%S"),
      'init':  init.strftime("%Y%m%d_%H%M%S"),
      'lead':  str(int(lead)),
      'accum': '000000',

      'name':      variable,  #'MERRA2_Cloud_Percentage'
      'long_name': variable,  #'Cloud Percentage Levels',
      'level':     'ALL',
      'units':     verifVariables[variable]['units'],

      'grid': getGridInfo(source,griddedDatasets[source]['gridType'])
   }

   #print(attrs)
   #print(griddedDatasets[source])

   return attrs

######## END FUNCTIONS   ##########


#if __name__ == "__main__":
dataFile, dataSource, variable, i_date, v_date, flag = sys.argv[1].split(":")
met_data = getDataArray(dataFile,dataSource,variable,flag)
attrs = getAttrArray(dataSource,variable,i_date,v_date)
print(attrs)
