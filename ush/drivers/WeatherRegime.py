import os
import numpy as np
from pylab import *
from sklearn.cluster import KMeans
import scipy
from scipy import stats,signal
from numpy import ones,vstack
from numpy.linalg import lstsq
from eofs.standard import Eof
from metplus.util import config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate


class WeatherRegimeCalculation():
    """Contains the programs to perform a Weather Regime Analysis
    """
    def __init__(self,config,label):

        self.wrnum = config.getint('WeatherRegime',label+'_WR_NUMBER',6)
        self.numi = config.getint('WeatherRegime',label+'_NUM_CLUSTERS',20)
        self.NUMPCS = config.getint('WeatherRegime',label+'_NUM_PCS',10)


    def get_cluster_fraction(self, m, label):
        return (m.labels_==label).sum()/(m.labels_.size*1.0)


    def weights_detrend(self,lats,lons,indata):

        arr_shape = indata.shape

        ##Set up weight array
        cos = lats * np.pi / 180.0
        way = np.cos(cos)
        if len(lats.shape) == 1:
            weightf = np.repeat(way[:,np.newaxis],len(lons),axis=1)
        else:
            weightf = way

        #Remove trend and seasonal cycle
        atemp = np.zeros(arr_shape)
        for i in np.arange(0,len(indata[0,:,0,0]),1):
            atemp[:,i] = signal.detrend(atemp[:,i],axis=0)
            atemp[:,i] = (indata[:,i] - np.nanmean(indata[:,i],axis=0)) * weightf

        a = atemp
        atemp=0

        #Reshape into time X space
        a1 = np.reshape(a,[len(a[:,0,0,0])*len(a[0,:,0,0]),len(lons)*len(lats)])

        return a,a1


    def run_elbow(self,a1):

        k=KMeans(n_clusters=self.wrnum, random_state=0, n_jobs=-1)  #Initilize cluster centers

        #Calculate sum of squared distances for clusters 1-15
        kind = np.arange(1,self.numi,1)
        Sum_of_squared_distances = []
        K = range(1,self.numi)
        for k in K:
            km = KMeans(n_clusters=k)
            km = km.fit(a1)
            Sum_of_squared_distances.append(km.inertia_)

        # Calculate the bend of elbow
        points = [(K[0],Sum_of_squared_distances[0]),(K[-1],Sum_of_squared_distances[-1])]
        x_coords, y_coords = zip(*points)
        A = vstack([x_coords,ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords,rcond=None)[0]
        line = m*kind + c
        curve = Sum_of_squared_distances
        curve=np.array(curve)*10**-10
        line = line*10**-10

        d=[]
        for i in np.arange(0,self.numi-1,1):
            p1=np.array([K[0],curve[0]])
            p2=np.array([K[-1],curve[-1]])
            p3=np.array([K[i],curve[i]])
            d=np.append(d,np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))

        mi = np.where(d==d.min())[0]
        print('Optimal Cluster # = '+str(mi+1)+'')

        return K,d,mi,line,curve


    def Calc_EOF(self,eofin):

        #Remove trend and seasonal cycle
        for d in np.arange(0,len(eofin[0,:,0,0]),1):
            eofin[:,d] = signal.detrend(eofin[:,d],axis=0)
            eofin[:,d] = eofin[:,d] - np.nanmean(eofin[:,d],axis=0)

        #Reshape into time X space
        arr_shape = eofin.shape
        arrdims = len(arr_shape)
        eofin = np.reshape(eofin,(np.prod(arr_shape[0:arrdims-2]),arr_shape[arrdims-2]*arr_shape[arrdims-1]))

        # Use EOF solver and get PCs and EOFs
        solver = Eof(eofin,center=False)
        pc = solver.pcs(npcs=self.NUMPCS,pcscaling=1)
        eof = solver.eofsAsCovariance(neofs=self.NUMPCS,pcscaling=1)
        eof = np.reshape(eof,(self.NUMPCS,arr_shape[arrdims-2],arr_shape[arrdims-1]))

        #Get variance fractions
        variance_fractions = solver.varianceFraction(neigs=self.NUMPCS) * 100
        print(variance_fractions)

        return eof, pc, self.wrnum, variance_fractions


    def reconstruct_heights(self,eof,pc,reshape_arr):

        rssize = len(reshape_arr)
        eofshape = eof.shape
        eosize = len(eofshape)

        #reconstruction. If NUMPCS=nt, then a1=a0
        eofs=np.reshape(eof,(self.NUMPCS,eofshape[eosize-2]*eofshape[eosize-1]))
        a1=np.matmul(pc,eofs)
        #a1 = np.reshape(a1,reshape_arr)

        return a1


    def run_K_means(self,a1,yr,arr_shape):

        arrdims = len(arr_shape)

        k=KMeans(n_clusters=self.wrnum, random_state=0, n_jobs=-1)

        #fit the K-means algorithm to the data
        f=k.fit(a1)

        #Obtain the cluster anomalies
        y=f.cluster_centers_

        #Obtain cluster labels for each day [Reshape to Year,day]
        wr = f.labels_
        wr = np.reshape(wr,arr_shape[0:arrdims-2])

        yf = np.reshape(y,[self.wrnum,arr_shape[arrdims-2],arr_shape[arrdims-1]]) # reshape cluster anomalies to latlon

        #Get frequency of occurence for each cluster
        perc=np.zeros(self.wrnum)
        for ii in np.arange(0,self.wrnum,1):
            perc[ii] = self.get_cluster_fraction(f,ii)

        #Sort % from low to high
        ii = np.argsort(perc)
        print(perc[ii])

        #Reorder
        perc = perc[ii]
        input=yf[ii]
        ii = ii[::-1]

        #Reorder from max to min and relabel
        wrc = wr*1.0/1.0
        for i in np.arange(0,self.wrnum,1):
            wrc[wr==ii[i]] = i

        perc = perc[::-1]
        input = input[::-1]

        #Save Label data [YR,DAY]
        #if os.path.isfile(outfile+'.nc'):
        #   os.remove(outfile+'.nc')
        #nc = nc4.Dataset(outfile, 'w')
        #nc.createDimension('year', arr_shape[0])
        #nc.createDimension('day', arr_shape[1])

        #ncyr = nc.createVariable('time','i',('year'))
        #nc.variables['time'].long_name = "time"
        #nc.variables['time'].standard_name = "time"
        #nc.variables['time'].units = "years"
       
        #ncnum = nc.createVariable('wrnum','i',('year','day'),fill_value=-9999.0)
        #nc.variables['wrnum'].long_name = "weather_regime_number"
        #nc.variables['wrnum'].standard_name = "weather_regime_number"
        #nc.variables['wrnum'].units = "unitless"

        #ncyr[:,:] = yr
        #ncnum[:,:] = wrc
        #nc.close()

        #np.save('WR_LABELS',wrc)

        return input, self.wrnum, perc

