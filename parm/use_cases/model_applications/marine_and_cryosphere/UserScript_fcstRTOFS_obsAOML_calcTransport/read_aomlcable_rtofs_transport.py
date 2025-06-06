#! /usr/bin/env python3
"""
Florida Cable Transport Class-4 Validation System
Adapted from Todd Spindler's code
"""

from netCDF4 import Dataset
import numpy as np
from pyproj import Geod
import math
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pandas as pd
import sys, os
import logging

vDate=datetime.strptime(sys.argv[1],'%Y%m%d')
rtofsdir = os.environ.get('CALC_TRANSPORT_RTOFS_DIRNAME') 
cablefile = os.environ.get('CALC_TRANSPORT_CABLE_FILENAME') 
eightmilefile = os.environ.get('CALC_TRANSPORT_EIGHTMILE_FILENAME') 

print('Starting Cable V&V at',datetime.now(),'for',vDate)



if not os.path.exists(cablefile):
        print('missing AOML Cable transport file for',vDate)

#-----------------------------------------------
# read cable transport data from AOML            
#-----------------------------------------------
    
# read the AOML dataset
names=['year','month','day','transport']
cable=pd.read_csv(cablefile,comment='%',names=names,delimiter=' ',
    skipinitialspace=True,header=None,usecols=list(range(4)))
cable['date']=pd.to_datetime(cable[['year','month','day']])
cable.index=cable.date
cable['error']=2.0
del cable['year'], cable['month'], cable['day'], cable['date']
print(cable)

#-----------------------------------------------
# full cross-section transport calculation
#-----------------------------------------------
def calc_transport(dates,fcst):
    """
    Calculate the transport of water across the Florida Straits
    This extracts the section and integrates the flow through it.
    """
    transport=[]
    fcst_str='f{:03d}'.format(fcst)
    cable_loc=np.loadtxt(eightmilefile,dtype='int',usecols=(0,1))
    eightmile_lat = 26.5167
    eightmile_lon = -78.7833%360
    wpb_lat = 26.7153425
    wpb_lon = -80.0533746%360
    cable_angle = math.atan((eightmile_lat-wpb_lat)/(eightmile_lon-wpb_lon))
    g=Geod(ellps='WGS84')

    for date in dates:
        print('DATE :', date, ' DATES :',dates)
        print('processing',date.strftime('%Y%m%d'),'fcst',fcst)
        rundate=date-timedelta(fcst/24.)  # calc rundate from fcst and date
        ufile=rtofsdir+'/'+rundate.strftime('%Y%m%d')+'/rtofs_glo_3dz_'+fcst_str+'_daily_3zuio.nc'
        vfile=rtofsdir+'/'+rundate.strftime('%Y%m%d')+'/rtofs_glo_3dz_'+fcst_str+'_daily_3zvio.nc'

        print(ufile)
        print(vfile)

        udata=Dataset(ufile)
        vdata=Dataset(vfile)

        lon=udata['Longitude'][:]
        lat=udata['Latitude'][:]
        depth=udata['Depth'][:]

        usection=np.zeros((depth.shape[0],cable_loc.shape[0]))
        vsection=np.zeros((depth.shape[0],cable_loc.shape[0]))

        udata=udata['u'][:].squeeze()
        vdata=vdata['v'][:].squeeze()

        for ncol,(row,col) in enumerate(cable_loc):
            usection[:,ncol]=udata[:,row,col].filled(fill_value=0.0)
            vsection[:,ncol]=vdata[:,row,col].filled(fill_value=0.0)

        lon=lon[cable_loc[:,0],cable_loc[:,1]]
        lat=lat[cable_loc[:,0],cable_loc[:,1]]

        # compute the distances along the track
        _,_,dist=g.inv(lon[0:-1],lat[0:-1],lon[1:],lat[1:])
        depth=np.diff(depth)
        usection=usection[:-1,:-1]
        vsection=vsection[:-1,:-1]

        dist,depth=np.meshgrid(dist,depth)
        u,v=rotate(usection,vsection,cable_angle)
        trans1=(v*dist*depth).sum()/1e6
        #print(date.strftime('%Y-%m-%d'),' transport:',transport,'Sv')
        transport.append(trans1)

    return transport

#-----------------------------------------------
# retrieve model data
#-----------------------------------------------
def get_model(dates,fcsts):

    transport={'dates':dates}


    for fcst in fcsts:
            transport[fcst]=calc_transport(dates,fcst)

    model=pd.DataFrame(transport)
    model.index=model.dates
    del model['dates']
    #del model['validDates']

    print(model)
    return model
#-----------------------------------------------
# coordinate rotation
#-----------------------------------------------
def rotate(u,v,phi):
    # phi is in radians
    u2 =  u*math.cos(phi) + v*math.sin(phi)
    v2 = -u*math.sin(phi) + v*math.cos(phi)
    return u2,v2

#-----------------------------------------------
if __name__ == "__main__":

    want_date=vDate
    DateSet=True

    fcst = int(os.environ.get('CALC_TRANSPORT_LEAD_TIME'))
    no_of_fcst_stat_days = int(os.environ.get('CALC_TRANSPORT_STATS_DAY'))

    fcsts=list(range(fcst,fcst+1,24))

    start_date=want_date
    stop_date=want_date
    cable=cable[:stop_date]

    # Count the number in the subdirs RTOFS dir
    path, dirs, files = next(os.walk(rtofsdir))
    dir_count = len(dirs)

    """
    Setup logging
    """
    logfile = os.environ.get('CALC_TRANSPORT_LOG_FILE')


    for end_date in pd.date_range(start_date,stop_date):
        dates=pd.date_range(end=end_date,periods=dir_count)
        model=get_model(dates,fcsts)

    both=pd.merge(cable,model,left_index=True,right_index=True,how='inner')
    print("both :", both)
    both=both[both.index.max()-timedelta(no_of_fcst_stat_days):]
     
    diff=both[fcst] - both.transport
    bias=diff.mean()
    rmse=mean_squared_error(both.transport,both[fcst])**0.5
    if both[fcst].mean() != 0.0:
        scatter_index=100.0*(((diff**2).mean())**0.5 - bias**2)/both.transport.mean()
    else:
        scatter_index=np.nan

    corr=both[fcst].corr(both.transport)

#    print("BIAS :",bias, "RMSE :",rmse, "CORR :",corr, "SCATTER INDEX :",scatter_index)

    outdir = os.environ.get('OUTPUT_DIR')

    if not os.path.exists(outdir):
        print(f"Creating output directory: {outdir}")
        os.makedirs(outdir)

    expected_file = os.path.join(outdir,logfile)
    print(expected_file)

    with open(expected_file, 'w') as f:
       print("BIAS :",bias, "RMSE :",rmse, "CORR :",corr, "SCATTER INDEX :",scatter_index, file=f)
