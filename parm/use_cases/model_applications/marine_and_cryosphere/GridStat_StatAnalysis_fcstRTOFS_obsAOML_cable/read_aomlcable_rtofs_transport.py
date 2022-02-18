"""
Florida Cable Transport Class-4 Validation System
Adapted from Todd Spindler's code
"""

from netCDF4 import Dataset
import numpy as np
from pyproj import Geod
import math
from datetime import datetime, timedelta
import pandas as pd
import sys, os

# global subdirectories (will be env vars in next release)
refDir='/d1/biswas/feature_cable'
DCOMDir='/d1/biswas/feature_cable'
archDir='/d1/biswas/feature_cable/rtofs-cable'

if len(sys.argv) < 5:
    print("Must specify the following elements: rtofs_u, rtofs_v, cable_file, eightmile_file, valid_date")
    sys.exit(1)

rtofsfile_u = os.path.expandvars(sys.argv[1]) 
rtofsfile_v = os.path.expandvars(sys.argv[2]) 
cablefile = os.path.expandvars(sys.argv[3]) 
eightmilefile = os.path.expandvars(sys.argv[4]) 
vDate=datetime.strptime(sys.argv[5],'%Y%m%d')

print('Starting Cable V&V at',datetime.now(),'for',vDate)



if not os.path.exists(cablefile):
        print('missing AOML Cable transport file for',vDate)

#-----------------------------------------------
# read cable transport data from AOML            
#-----------------------------------------------
#cablefile='FC_cable_transport_2021.dat'
#eightmilefile='eightmilecable.dat'
    
# read the AOML dataset
names=['year','month','day','transport']
cable=pd.read_csv(cablefile,comment='%',names=names,delimiter=' ',
    skipinitialspace=True,header=None,usecols=list(range(4)))
cable['date']=pd.to_datetime(cable[['year','month','day']])
cable.index=cable.date
cable['error']=2.0
del cable['year'], cable['month'], cable['day'], cable['date']
print(cable)

print(rtofsfile_u)
fcst=rtofsfile_u.split('/')[-1].split("_")[3].split("f")[1].strip("0")
fcst=int(fcst)

#-----------------------------------------------
# full cross-section transport calculation
#-----------------------------------------------
def calc_transport(dates,fcst):
    """
    Calculate the transport of water across the Florida Straits
    This extracts the section and integrates the flow through it.
    """
    transport=[]
#MKB    if fcst==0:
#MKB        fcst_str='n024'
#MKB    else:
#MKB        fcst_str='f{:03d}'.format(fcst)
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
#MKB Does this means it needs files from -24 hr?
        rundate=date-timedelta(fcst/24.)  # calc rundate from fcst and date
#MKB        ufile=archDir+'/'+rundate.strftime('%Y%m%d')+'/rtofs_glo_3dz_'+fcst_str+'_daily_3zuio.nc'
#MKB        vfile=archDir+'/'+rundate.strftime('%Y%m%d')+'/rtofs_glo_3dz_'+fcst_str+'_daily_3zvio.nc'
#MKB        ufile='rtofsfile_u'
#MKB        vfile='rtofsfile_v'

#MKB        print(ufile)
#MKB        print(vfile)

#MKB        try:
        udata=Dataset(rtofsfile_u)
        vdata=Dataset(rtofsfile_v)
#MKB        except:
#MKB            print(rundate,fcst,'not found -- continuing')
#MKB            transport.append(np.nan)
#MKB            continue

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
    #model['validDates']=model.dates+timedelta(fcst/24.)
    #model.index=model.validDates
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

#-------------------------------------------------------------------------
def rms(both,fcst):
    print('Code call rmse')
    fcst=both[fcst]
    obs=both['transport']
    B = fcst.mean() - obs.mean()
    B2 = B**2
    D = fcst-obs
    S=D.std()
    S2=S**2
    return np.sqrt(S2 + B2)

#-------------------------------------------------------------------------
def bias(both,fcst):
    print('Code call bias')
    fcst=both[fcst]
    obs=both['transport']
    return fcst.mean() - obs.mean()




want_date=datetime.strptime(sys.argv[5],'%Y%m%d')
print('WANT DATE :', want_date)
DateSet=True

fcsts=list(range(fcst,fcst+1,24))

start_date=want_date
stop_date=want_date
cable=cable[:stop_date]

for end_date in pd.date_range(start_date,stop_date):
    dates=pd.date_range(end=end_date,periods=3)
    model=get_model(dates,fcsts)

both=pd.merge(cable,model,left_index=True,right_index=True,how='inner')
print("both :", both)
both=both[both.index.max()-timedelta(3):]
fcst=both.dropna(inplace=True)
     
print('BOTH :',both)
print('BOTH(FCST) :',both[fcst])
print('BOTH.TRANSPORT :',both.transport)
diff=both[fcst] - both.transport
print('DIFF :',diff)
bias=diff.mean()
rmse=mean_squared_error(both.transport,both[fcst])**0.5
if both[fcst].mean() != 0.0:
    scatter_index=100.0*(((diff**2).mean())**0.5 - bias**2)/both.transport.mean()
else:
    scatter_index=np.nan

corr=both[fcst].corr(both.transport)

print("BIAS :",bias, "RMSE :",rmse, "CORR :",corr, "SCATTER INDEX :",scatter_index)
