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

if len(sys.argv) < 6:
    print("Must specify the following elements: rtofs_u, rtofs_v, cable_file, eightmile_file, valid_date, file_flag")
    sys.exit(1)

rtofsfile_u = os.path.expandvars(sys.argv[1]) 
rtofsfile_v = os.path.expandvars(sys.argv[2]) 
cablefile = os.path.expandvars(sys.argv[3]) 
eightmilefile = os.path.expandvars(sys.argv[4]) 
vDate=datetime.strptime(sys.argv[5],'%Y%m%d')
file_flag = sys.argv[6] 

print('Starting Cable V&V at',datetime.now(),'for',vDate, ' file_flag:',file_flag)



if not os.path.exists(cablefile):
        print('missing AOML Cable transport file for',vDate)

#-----------------------------------------------
# read cable transport data from AOML            
#-----------------------------------------------
cablefile='FC_cable_transport_2021.dat'
eightmilefile='eightmilecable.dat'
    
# read the AOML dataset
names=['year','month','day','transport']
cable=pd.read_csv(cablefile,comment='%',names=names,delimiter=' ',
    skipinitialspace=True,header=None,usecols=list(range(4)))
cable['date']=pd.to_datetime(cable[['year','month','day']])
cable.index=cable.date
cable['error']=2.0
del cable['year'], cable['month'], cable['day'], cable['date']
print(cable)

fcst=rtofsfile_u.split("_")[3].split("f")[1].strip("0")
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


want_date=datetime.strptime(sys.argv[1],'%Y%m%d')
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
both=both[both.index.max()-timedelta(3):]
fcst=both.dropna(inplace=True)
     


#Create the MET grids based on the file_flag
if file_flag == 'fcst':
    met_data = model[:,:]
    #trim the lat/lon grids so they match the data fields
    lat_met = model.lat
    lon_met = model3.lon
    print(" RTOFS Data shape: "+repr(met_data.shape))
    v_str = vDate.strftime("%Y%m%d")
    v_str = v_str + '_000000'
    lat_ll = float(lat_met.min())
    lon_ll = float(lon_met.min())
    n_lat = lat_met.shape[0]
    n_lon = lon_met.shape[0]
    delta_lat = (float(lat_met.max()) - float(lat_met.min()))/float(n_lat)
    delta_lon = (float(lon_met.max()) - float(lon_met.min()))/float(n_lon)
    print(f"variables:"
            f"lat_ll: {lat_ll} lon_ll: {lon_ll} n_lat: {n_lat} n_lon: {n_lon} delta_lat: {delta_lat} delta_lon: {delta_lon}")
    met_data.attrs = {
            'valid': v_str,
            'init': v_str,
            'lead': "00",
            'accum': "00",
            'name': 'ssh',
            'standard_name': 'zonal current',
            'long_name': 'sea_surface_elevation',
            'level': "SURFACE",
            'units': "meters",

            'grid': {
                'type': "LatLon",
                'name': "RTOFS Grid",
                'lat_ll': lat_ll,
                'lon_ll': lon_ll,
                'delta_lat': delta_lat,
                'delta_lon': delta_lon,
                'Nlat': n_lat,
                'Nlon': n_lon,
                }
            }
    attrs = met_data.attrs


if file_flag == 'obs':
# Empty object
    my_data = pd.DataFrame()
    my_data = my_data.append(pd.DataFrame(np.array([["ADUPA", transport]])))
