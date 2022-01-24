import os
import numpy as np
from pylab import *
from sklearn.cluster import KMeans
import scipy
import netCDF4 as nc4
from scipy import stats,signal
from numpy import ones,vstack
from numpy.linalg import lstsq
from eofs.standard import Eof


class WeatherRegimeCalculation():
    """Contains the programs to perform a Weather Regime Analysis
    """
    def __init__(self,label):

        self.wrnum = int(os.environ.get(label+'_WR_NUMBER',6))
        self.numi = int(os.environ.get(label+'_NUM_CLUSTERS',20))
        self.NUMPCS = int(os.environ.get(label+'_NUM_PCS',10))
        self.wr_tstep = int(os.environ.get(label+'_WR_FREQ',7))
        self.wr_outfile_type = os.environ.get(label+'_WR_OUTPUT_FILE_TYPE','text')
        self.wr_outfile_dir = os.environ.get('WR_OUTPUT_FILE_DIR',os.environ['SCRIPT_OUTPUT_BASE'])
        self.wr_outfile = os.environ.get(label+'_WR_OUTPUT_FILE',label+'_WeatherRegime')


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

        k=KMeans(n_clusters=self.wrnum, random_state=0)  #Initilize cluster centers

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

        return a1


    def run_K_means(self,a1,timedict,arr_shape):

        arrdims = len(arr_shape)

        k=KMeans(n_clusters=self.wrnum, random_state=0)

        #fit the K-means algorithm to the data
        f=k.fit(a1)

        #Obtain the cluster anomalies
        y=f.cluster_centers_

        #Obtain cluster labels for each day [Reshape to Year,day]
        wr = f.labels_
        wr = np.reshape(wr,arr_shape[0:arrdims-2])

        yf = np.reshape(y,[self.wrnum,arr_shape[arrdims-2],arr_shape[arrdims-1]]) # reshape cluster anomalies to latlon

        #Get frequency of occurrence for each cluster
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
            wrc[wr==ii[i]] = i+1

        perc = perc[::-1]
        input = input[::-1]

        #Save Label data [YR,DAY]
        # Make some conversions first
        wrc_shape = wrc.shape
        len1d =  wrc.size
        valid_time_1d = np.reshape(timedict['valid'],len1d)
        yr_1d = []
        mth_1d = []
        day_1d = []
        for vt1 in valid_time_1d:
           yr_1d.append(vt1[0:4])
           mth_1d.append(vt1[4:6])
           day_1d.append(vt1[6:8])
        wrc_1d = np.reshape(wrc,len1d)

        # netcdf file
        if self.wr_outfile_type=='netcdf':
            wr_full_outfile = os.path.join(self.wr_outfile_dir,self.wr_outfile+'.nc')

            if os.path.isfile(wr_full_outfile):
                os.remove(wr_full_outfile)

            # Create CF compliant time unit
            rdate = datetime.datetime(int(yr_1d[0]),int(mth_1d[0]),int(day_1d[0]),0,0,0)
            cf_diffdays = np.zeros(len(yr_1d))
            ymd_arr = np.empty(len(yr_1d))
            for dd in range(len(yr_1d)):
                loopdate = datetime.datetime(int(yr_1d[dd]),int(mth_1d[dd]),int(day_1d[dd]),0,0,0)
                cf_diffdays[dd] = (loopdate - rdate).days
                ymd_arr[dd] = yr_1d[dd]+mth_1d[dd]+day_1d[dd]

            nc = nc4.Dataset(wr_full_outfile, 'w')
            nc.createDimension('time', len(mth_1d))
            nc.Conventions = "CF-1.7"
            nc.title = "Weather Regime Classification"
            nc.institution = "NCAR DTCenter"
            nc.source = "Weather Regime METplus use-case"

            ncti = nc.createVariable('time','d',('time'))
            nc.variables['time'].long_name = "time"
            nc.variables['time'].standard_name = "time"
            nc.variables['time'].units = "days since "+rdate.strftime('%Y-%m-%d %H:%M:%S')
            nc.variables['time'].calendar = "gregorian"

            ncdate = nc.createVariable('date','i',('time'))
            nc.variables['date'].long_name = "date YYYYMMDD"
       
            ncnum = nc.createVariable('wrnum','i',('time'),fill_value=-9999.0)
            nc.variables['wrnum'].long_name = "weather_regime_number"

            ncti[:] = cf_diffdays
            ncdate[:] = ymd_arr
            ncnum[:] = wrc_1d
            nc.close()

        # text file
        if self.wr_outfile_type=='text':
           wr_full_outfile = os.path.join(self.wr_outfile_dir,self.wr_outfile+'.txt')

           if os.path.isfile(wr_full_outfile):
                os.remove(wr_full_outfile)

           otdata = np.array([yr_1d, mth_1d, day_1d, wrc_1d])
           otdata = otdata.T

           with open(wr_full_outfile, 'w+') as datafile_id:
               np.savetxt(datafile_id, otdata, fmt=['%6s','%3s','%4s','%6s'], header='Year Month Day WeatherRegime')

        return input, self.wrnum, perc, wrc


    def compute_wr_freq(self, WR):

        ######## Simple Count ##########
        WRfreq = np.zeros((self.wrnum,len(WR[:,0]),len(WR[0,:])-self.wr_tstep+1))

        for yy in np.arange(0,len(WRfreq[0,:,0]),1):
            d1=0;d2=self.wr_tstep
            for dd in np.arange(len(WRfreq[0,0,:])):
                temp = WR[yy,d1:d2]
                for ww in np.arange(self.wrnum):
                    WRfreq[ww,yy,dd] = len(np.where(temp==ww+1)[0])
                d1=d1+1;d2=d2+1

        dlen_plot = len(WRfreq[0,0,:])

        return WRfreq, dlen_plot, self.wr_tstep
