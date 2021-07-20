import os
import numpy as np
import datetime
import bisect
from scipy import stats
from scipy.signal import argrelextrema
#from metplus.util import config_metplus, get_start_end_interval_times, get_lead_sequence
#from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate
from Blocking_WeatherRegime_util import read_nc_met

class BlockingCalculation():
    """Contains the programs to calculate Blocking via the Pelly-Hoskins Method
    """
    def __init__(self,label):

        self.blocking_anomaly_var = os.environ.get(label+'_BLOCKING_ANOMALY_VAR','Z500_ANA')
        self.blocking_var = os.environ.get(label+'_BLOCKING_VAR','Z500')
        self.smoothing_pts = int(os.environ.get(label+'_SMOOTHING_PTS',9))
        lat_delta_in = os.environ.get(label+'_LAT_DELTA','-5,0,5')
        self.lat_delta = list(map(int,lat_delta_in.split(",")))
        self.n_s_limits = int(os.environ.get(label+'_NORTH_SOUTH_LIMITS',30))
        self.ibl_dist = int(os.environ.get(label+'_IBL_DIST',7))
        self.ibl_in_gibl = int(os.environ.get(label+'_IBL_IN_GIBL',15))
        self.gibl_overlap = int(os.environ.get(label+'_GIBL_OVERLAP',10))
        self.block_time = int(os.environ.get(label+'_BLOCK_TIME',5))  ###Should fix so it supports other times"
        self.block_travel = int(os.environ.get(label+'_BLOCK_TRAVEL',45))
        self.block_method = os.environ.get(label+'_BLOCK_METHOD','PH')

        # Check data requirements
        if self.smoothing_pts % 2 == 0:
            print('ERROR: Smoothing Radius must be an odd number given in grid points, Exiting...')
            exit()


    def run_CBL(self,cblinfiles,nseasons,dseasons):

        z500_anom_4d,lats,lons,timedict = read_nc_met(cblinfiles,self.blocking_anomaly_var,nseasons,dseasons)

        #Create Latitude Weight based for NH
        cos = lats
        cos = cos * np.pi / 180.0
        way = np.cos(cos)
        way = np.sqrt(way)
        weightf = np.repeat(way[:,np.newaxis],360,axis=1)

        ####Find latitude of maximum high-pass STD (CBL)
        yrlen = len(z500_anom_4d[:,0,0,0])
        mstd = np.nanstd(z500_anom_4d,axis=1)
        mhweight = mstd * weightf
        cbli = np.argmax(mhweight,axis=1)
        CBL = np.zeros((yrlen,len(lons)))
        for j in np.arange(0,yrlen,1):
            CBL[j,:] = lats[cbli[j,:]]

        ###Apply Moving Average to Smooth CBL Profiles
        lt = len(lons)
        CBLf = np.zeros((yrlen,len(lons)))
        m=int((self.smoothing_pts-1)/2.0)
        for i in np.arange(0,len(CBL[0,:]),1):
            ma_indices = np.arange(i-m,i+m+1)
            ma_indices = np.where(ma_indices >= lt,ma_indices-lt,ma_indices)
            CBLf[:,i] = np.nanmean(CBL[:,ma_indices],axis=1).astype(int)
        
        return CBLf,lats,lons,mhweight,timedict


    def run_mod_blocking1d(self,a,cbl,lat,lon,meth):
        lat_d = self.lat_delta
        dc = (90 - cbl).astype(int)
        db = self.n_s_limits
        BI = np.zeros((len(a[:,0,0]),len(lon)))
        blon = np.zeros((len(a[:,0,0]),len(lon)))
        if meth=='PH':
            # loop through days
            for k in np.arange(0,len(a[:,0,0]),1):
                blontemp=0
                q=0
                BI1=np.zeros((len(lat_d),len(lon)))
                for l in lat_d:
                    blon1 = np.zeros(len(lon))
                    d0 = dc-l
                    dn = ((dc - 1*db/2) - l).astype(np.int64)
                    ds = ((dc + 1*db/2) - l).astype(np.int64)
                    GHGS = np.zeros(len(cbl))
                    GHGN = np.zeros(len(cbl))
                    for jj in np.arange(0,len(cbl),1):
                        GHGN[jj] = np.mean(a[k,dn[jj]:d0[jj]+1,jj])
                        GHGS[jj] = np.mean(a[k,d0[jj]:ds[jj]+1,jj])
                    BI1[q,:] = GHGN-GHGS
                    q = q +1
                BI1 = np.max(BI1,axis=0)
                block = np.where((BI1>0))[0]
                blon1[block]=1
                blontemp = blontemp + blon1
                BI[k,:] = BI1
                blon[k,:] = blontemp

        return blon,BI


    def run_Calc_IBL(self,cbl,iblinfiles,nseasons, dseasons):

        z500_daily,lats,lons,timedict = read_nc_met(iblinfiles,self.blocking_var,nseasons,dseasons)

        #Initilize arrays for IBLs and the blocking index
        # yr, day, lon
        yrlen = len(z500_daily[:,0,0,0])
        blonlong = np.zeros((yrlen,len(z500_daily[0,:,0,0]),len(lons)))
        BI = np.zeros((yrlen,len(z500_daily[0,:,0,0]),len(lons)))

        #Using long-term mean CBL and acsessing module of mod.py
        cbl = np.nanmean(cbl,axis=0)
        for i in np.arange(0,yrlen,1):
            blon,BI[i,:,:] = self.run_mod_blocking1d(z500_daily[i,:,:,:],cbl,lats,lons,self.block_method)
            blonlong[i,:,:] = blon

        return blonlong,timedict


    def run_Calc_GIBL(self,ibl,lons):

        #Initilize GIBL Array
        GIBL = np.zeros(np.shape(ibl))

        #####Loop finds IBLs within 7 degree of each other creating one group. Finally
        ##### A GIBL exist if it has more than 15 IBLs
        crit = self.ibl_in_gibl

        for i in np.arange(0,len(GIBL[:,0,0]),1):
            for k in np.arange(0,len(GIBL[0,:,0]),1):
                gibli = np.zeros(len(GIBL[0,0,:]))
                thresh = crit/2.0
                a = ibl[i,k,:]
                db = self.ibl_dist
                ibli = np.where(a==1)[0]
                if len(ibli)==0:
                    continue
                idiff = ibli[1:] - ibli[:-1]
                bt=0
                btlon = ibli[0]
                ct = 1
                btfin = []
                block = ibli
                block = np.append(block,block+360)
                for ll in np.arange(1,len(block),1):
                    diff = np.abs(block[ll] - block[ll-1])
                    if diff == 1:
                        bt = [block[ll]]
                        btlon = np.append(btlon,bt)
                        ct = ct + diff
                    if diff <= thresh and diff != 1:
                        bt = np.arange(block[ll-1]+1,block[ll]+1,1)
                        btlon = np.append(btlon,bt)
                        ct = ct + diff
                    if diff > thresh or ll==(len(block)-1):
                        if ct >= crit:
                            btfin = np.append(btfin,btlon)
                            ct=1
                        ct = 1
                        btlon = block[ll]
                if len(btfin)/2 < crit :
                    btfin = []
                if len(btfin)==0:
                    continue
                gibl1 = btfin
                temp = np.where(gibl1>=360)[0]
                gibl1[temp] = gibl1[temp] - 360
                gibli[gibl1.astype(int)] = 1
                GIBL[i,k,:] = gibli

        return GIBL


    def Remove(self,duplicate):
        final_list = []
        for num in duplicate:
            if num not in final_list:
                final_list.append(num)
        return final_list


    def run_Calc_Blocks(self,ibl,GIBL,lon,tsin):

        crit = self.ibl_in_gibl

        ##Count up the blocked longitudes for each GIBL
        c = np.zeros((GIBL.shape))
        lonlen = len(lon)
        sz = []
        mx = []
        min = []

        for y in np.arange(0,len(GIBL[:,0,0]),1):
            for k in np.arange(0,len(GIBL[0,:,0]),1):
                a = GIBL[y,k] # Array of lons for each year,day
                ct=1
                ai = np.where(a==1)[0]
                ai = np.append(ai,ai+360)
                temp = np.where(ai>=360)[0]
                bi=list(ai)
                bi = np.array(bi)
                bi[temp] = bi[temp]-360
                # Loop through the lons that are part of the GIBL
                for i in np.arange(0,len(ai)-1,1):
                    diff = ai[i+1] - ai[i]
                    c[y,k,bi[i]] = ct
                    if diff==1:
                        ct=ct+1
                    else:
                        sz = np.append(sz,ct)
                        ct=1

        ########## - finding where the left and right limits of the block are - ################
        for i in np.arange(0,len(c[:,0,0]),1):
            for k in np.arange(0,len(c[0,:,0]),1):
                maxi = argrelextrema(c[i,k],np.greater,mode='wrap')[0]
                mini = np.where(c[i,k]==1)[0]
                if c[i,k,lonlen-1]!=0 and c[i,k,0]!=0:
                    mm1 = mini[-1]
                    mm2 = mini[:-1]
                    mini = np.append(mm1,mm2)
                mx = np.append(mx,maxi)
                min = np.append(min,mini)

        locy, locd, locl = np.where(c==crit)

        A = np.zeros(lonlen)
        A = np.expand_dims(A,axis=0)

        ################# - Splitting up each GIBL into its own array - ###################

        for i in np.arange(0,len(locy),1):
            m = locy[i]   #year
            n = locd[i]   #day
            o = locl[i]   #long where 15
            mm = int(mx[i])
            mn = min[i]
            temp1 = GIBL[m,n]
            temp2 = np.zeros(lonlen)
            if mn>mm:
                diff = int(mm - c[m,n,mm] + 1)
                lons = lon[diff]
                place1 = np.arange(lons,lonlen,1)
                place2 = np.arange(0,mm+1,1)
                bl = np.append(place2,place1).astype(int)
            if temp1[lonlen-1] ==1 and mm>200:
                lons = lon[mm]
                beg = mm - c[m,n,mm] + 1
                bl = np.arange(beg,mm+1,1).astype(int)
            if mm>mn: #temp1[359] ==0:
                lons = lon[mm]
                beg = mm - c[m,n,mm] + 1
                bl = np.arange(beg,mm+1,1).astype(int)
            temp2[bl] = 1
            temp2 = np.expand_dims(temp2,axis=0)
            A = np.concatenate((A,temp2),axis=0)

        A = A[1:]

        ######### - Getting rid of non-consectutve Time steps which would prevent blocking - #################
        dd=[]
        dy = []
        dA = A[0]
        dA = np.expand_dims(dA,axis=0)
        ct=0
        for i in np.arange(1,len(locy),1):
            dd1 = locd[i-1]
            dd2 = locd[i]
            if dd2-dd1 > 2:
                ct = 0
                continue
            if ct == 0:
                dd = np.append(dd,locd[i-1])
                dy = np.append(dy,locy[i-1])
                temp2 = np.expand_dims(A[i-1],axis=0)
                dA = np.concatenate((dA,temp2),axis=0)
                ct = ct + 1
            if dd2-dd1<=2:
                dd=np.append(dd,locd[i])
                dy = np.append(dy,locy[i])
                temp2 = np.expand_dims(A[i],axis=0)
                dA = np.concatenate((dA,temp2),axis=0)
                ct = ct + 1

        dA=dA[1:]
        dAfin = dA

        ############ - Finding center longitude of block - ##############
        middle=[]
        for l in np.arange(0,len(dAfin),1):
            temp = np.where(dAfin[l]==1)[0]
            if len(temp) % 2 == 0:
                temp = np.append(temp,0)
            midtemp = np.median(temp)
            middle = np.append(middle,midtemp)


        #####Track blocks. Makes sure that blocks overlap with at least 10 longitude points on consecutive
        overlap = self.gibl_overlap
        btime = self.block_time
        fin = [[]]
        finloc = [[]]
        ddcopy=dd*1.0
        noloc=[]
        failloc = [[]]
        for i in np.arange(0,len(c[:,0,0]),1):
            yri = np.where(dy==i)[0]
            B = [[]]
            ddil =1.0 * ddcopy[yri]
            dyy = np.where(dy==i)[0]
            rem = []
            for dk in ddil:
                if len(ddil) < btime:
                    continue
                ddil = np.append(ddil[0]-1,ddil)
                diff = np.diff(ddil)
                diffB=[]
                dB =1
                cnt = 1
                while dB<=2:
                    diffB = np.append(diffB,ddil[cnt])
                    dB = diff[cnt-1]
                    if ddil[cnt]==ddil[-1]:
                        dB=5
                    cnt=cnt+1
                diffB = np.array(self.Remove(diffB))
                locb = []
                for ll in diffB:
                    locb = np.append(locb,np.where((dy==i) & (dd==ll))[0])
                ddil=ddil[1:]
                locbtemp = 1.0*locb
                ree=np.empty(0,dtype=int)
                for hh in np.arange(0,len(noloc),1):
                    ree = np.append(ree,np.where(locb == noloc[hh])[0])
                ree.astype(int)
                locbtemp = np.delete(locbtemp,ree)
                locb=locbtemp * 1.0
                datemp = dAfin[locb.astype(int)]
                blocktemp = [[datemp[0]]]
                locbi = np.array([locb[0]])
                ll1=0
                pass1 = 0
                ai=[0]
                add=0
                for ll in np.arange(0,len(locb)-1,1):
                    if ((dd[locb[ll+1].astype(int)] - dd[locb[ll1].astype(int)]) >=1) & ((dd[locb[ll+1].astype(int)] - dd[locb[ll1].astype(int)]) <=2):
                        add = datemp[ll1] + datemp[ll+1]
                    ai = np.where(add==2)[0]
                    if len(ai)>overlap:
                        locbi=np.append(locbi,locb[ll+1])
                        ll1=ll+1
                        add=0
                    if (len(ai)<overlap):
                        add=0
                        continue
                if len(locbi)>4:
                    noloc = np.append(noloc,locbi)
                    finloc = finloc + [locbi]
                    for jj in locbi:
                        rem = np.append(rem,np.where(dyy==jj)[0])
                    ddil = np.delete(ddcopy[yri],rem.astype(int))
                if len(locbi)<=4:
                    noloc = np.append(noloc,locbi)
                    if len(locbi)<=2:
                        failloc=failloc+[locbi]
                    for jj in locbi:
                        rem = np.append(rem,np.where(dyy==jj)[0])
                    ddil = np.delete(ddcopy[yri],rem.astype(int))

        blocks = finloc[1:]
        noblock = failloc[1:]

        ############Get rid of blocks that travel downstream##########
        ######If center of blocks travel downstream further than 45 degrees longitude, 
        ######cancel block moment it travels out of this limit
        newblock = [[]]
        newnoblock=[[]]
        distthresh = self.block_travel
        for bb in blocks:
            diffb = []
            start = middle[bb[0].astype(int)]
            for bbs in bb:
                diffb = np.append(diffb, start - middle[bbs.astype(int)])
            loc = np.where(np.abs(diffb) > distthresh)[0]
            if len(loc)==0:
                newblock = newblock +[bb]
            if len(loc)>0:
                if len(bb[:loc[0]]) >4:
                    newblock = newblock + [bb[:loc[0]]]
                if len(bb[:loc[0]]) <=2:
                    noblock = noblock + [bb]

        blocks = newblock[1:]

        #Create a final array with blocking longitudes. Similar to IBL/GIBL, but those that pass the duration threshold
        blockfreq = np.zeros((len(ibl[:,0,0]),len(ibl[0,:,0]),360))
        savecbl=[]
        savemiddle = []
        saveyr=[]
        numblock=0
        for i in np.arange(0,len(blocks),1):
            temp = blocks[i]
            numblock=numblock+1
            for j in temp:
                j=int(j)
                daycomp = int(dd[j])
                yearcomp = int(dy[j])
                saveyr = np.append(saveyr,dy[j])
                middlecomp = middle[j].astype(int)
                mc1 = int(round(middlecomp / 2.5))
                blockfreq[yearcomp,daycomp] = blockfreq[yearcomp,daycomp] + dAfin[j]
                ct = ct + 1

        return blockfreq
