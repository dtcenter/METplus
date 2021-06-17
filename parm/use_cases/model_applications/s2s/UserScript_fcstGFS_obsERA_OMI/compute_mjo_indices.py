import numpy as np
import xarray as xr
import datetime
import pandas as pd
from scipy.fftpack import rfft, irfft, fftfreq
from scipy.signal import detrend

def rmm(olr, u850, u200, time, spd, eofpath):
    """
    Compute RMM index for given olr, u850 and u200 averaged from 15S - 15N. Use observed RMM EOFs 
    to project the data onto. To match the observed RMM index use ERA Interim wind and observed OLR 
    anomalies from 1979-2001 climatology. The normalization factors are the original ones from Wheeler 
    and Hendon (2004).
    :param olr: OLR data (time, lon) DataArray
    :param u850: zonal wind at 850hPa (time, lon) DataArray
    :param u200: zonal wind at 200hPa (time, lon) DataArray
    :param time: time datetime64 array
    :param spd: number of obs per day
    :param eofpath: file path to eof data files
    :return: RMM PCs
    """

    EOF1, EOF2 = read_rmm_eofs(eofpath)
    rmm_norm = [15.11623, 1.81355, 4.80978] # normalization factors for OLR, U850, U200  from 1979 - 2001
    pc_norm = [8.618352504159244, 8.40736449709697] # normalization factors for the PCs from 1979 - 2001

    # test that the input data has the same longitude values as the EOFs
    eoflon = EOF1['lon']
    lon = olr['lon']
    if not np.all(lon == eoflon):
        raise ValueError("Longitude grid of EOFs and OLR is not equal.  Longitudes should be 0 to 375.5 by 2.5 degrees.")
    lon = u850['lon']
    if not np.all(lon == eoflon):
        raise ValueError("Longitude grid of EOFs and U850 is not equal.  Longitudes should be 0 to 375.5 by 2.5 degrees.")
    lon = u200['lon']
    if not np.all(lon == eoflon):
        raise ValueError("Longitude grid of EOFs and U200 is not equal.  Longitudes should be 0 to 375.5 by 2.5 degrees.")

    # remove previous 120 day mean from data
    olr = rem_120day_mean(olr,time)
    u850 = rem_120day_mean(u850,time)
    u200 = rem_120day_mean(u200,time)

    # normalize by the square root of the average variance from 1979-2001
    olr.values   = olr/rmm_norm[0] 
    u850.values  = u850/rmm_norm[1]
    u200.values  = u200/rmm_norm[2]

    # add all variables to a single array (append in longitude)
    dims = olr.shape
    ntim = dims[0]
    nlon = dims[1]

    data = xr.DataArray(np.empty([ntim,3*nlon]), dims=('time','lon_ext'))
    data[:,0:nlon] = olr
    data[:,nlon:2*nlon] = u850 
    data[:,2*nlon::] = u200

    # add EOFs to single array for all variables
    eof1 = xr.DataArray(np.empty([3*nlon]), dims=('lon_ext'))
    eof2 = xr.DataArray(np.empty([3*nlon]), dims=('lon_ext'))
    for i in np.arange(0,3):
        eof1[nlon*(i):nlon*(i+1)] = EOF1[i,:]
        eof2[nlon*(i):nlon*(i+1)] = EOF2[i,:]

    # project data onto the EOF patterns
    raw_pc1, raw_pc2 = regress_2dim_data_onto_eofs(data, time, eof1, eof2)

    # normalize PCs by their std from 1979 - 2001
    normalization_factor = 1 / pc_norm[0]
    #normalization_factor = 1 / np.std(raw_pc1)
    pc1 = np.multiply(raw_pc1, normalization_factor)
    normalization_factor = 1 / pc_norm[1]
    #normalization_factor = 1 / np.std(raw_pc2)
    pc2 = np.multiply(raw_pc2, normalization_factor)

    pc1 = xr.DataArray(pc1,dims=['time'],coords={'time':time})
    pc2 = xr.DataArray(pc2,dims=['time'],coords={'time':time})

    return pc1, pc2


def omi(olr, time, spd, eof1_files, eof2_files):
    """
    Compute OMI index for given input OLR. Use observed OMI EOFs to project the data onto. To reproduce
    the observed OMI use daily OLR from PSL/NOAA at https://psl.noaa.gov/data/gridded/data.interp_OLR.html
    and the filtering method perform_3dim_spectral_filtering. This is slower than using the bandpass_filter_3D
    filter method, but it matches the observed OMI values closely. 
    :param olr: OLR data  (time, lat, lon) DataArray
    :param time: datetime64 time array
    :param spd: number of obs per day
    :param eofpath: filepath to the location of the eof files
    :return: OMI PCs
    """
    EOF1, EOF2 = read_omi_eofs(eof1_files, eof2_files)

    # check that all latitudes and longitudes match between EOFs and OLR
    eoflon = EOF1['lon']
    lon = olr['lon']
    eoflat = EOF1['lat']
    lat = olr['lat']
    if not np.all(lat == eoflat):
        raise ValueError("Latitude grid of EOFs and OLR is not equal. Latitudes should be -20 to 20 by 2.5 degrees.")
    if not np.all(lon == eoflon):
        raise ValueError("Longitude grid of EOFs and OLR is not equal. Longitudes should be 0 to 375.5 by 2.5 degrees.")

    # filter OLR for 20-96 days
    #filtered_olr_data  = bandpass_filter_3D(olr, time, 20, 96)
    time_spacing = (time[1] - time[0]).astype('timedelta64[s]') / np.timedelta64(1, 'D')  # time spacing in days
    filtered_olr_data = perform_3dim_spectral_filtering(olr, time_spacing, 20, 96, -720, 720)

    # regress OLR onto daily EOFs
    raw_pc1, raw_pc2 = regress_3dim_data_onto_eofs(filtered_olr_data, time, EOF1, EOF2)

    # normalize PCs
    normalization_factor = 1 / np.nanstd(raw_pc1)
    pc1 = np.multiply(raw_pc1, normalization_factor)
    pc2 = np.multiply(raw_pc2, normalization_factor)

    pc1 = xr.DataArray(pc1,dims=['time'],coords={'time':time})
    pc2 = xr.DataArray(pc2,dims=['time'],coords={'time':time})

    return pc1, pc2


def read_omi_eofs(eof1_files, eof2_files):
    """
    Read the OMI EOFs from file and into a xarray DataArray.
    :param eofpath: filepath to the location of the eof files
    :return: EOF1 and EOF2 3D DataArrays
    """
    #eof1path = eofpath+'eof1/'
    #eof2path = eofpath+'eof2/'

    # observed EOFs from NOAA PSL are saved in individual text files for each doy
    # horizontal resolution of EOFs is 2.5 degree

    EOF1 = xr.DataArray(np.empty([366,17,144]),dims=['doy','lat','lon'],
    coords={'doy':np.arange(1,367,1), 'lat':np.arange(-20,22.5,2.5), 'lon':np.arange(0,360,2.5)})
    EOF2 = xr.DataArray(np.empty([366,17,144]),dims=['doy','lat','lon'],
    coords={'doy':np.arange(1,367,1), 'lat':np.arange(-20,22.5,2.5), 'lon':np.arange(0,360,2.5)})
    nlat = len(EOF1['lat'])
    nlon = len(EOF1['lon'])

    for doy in range(len(eof1_files)):
        doystr = str(doy).zfill(3)  
        tmp1 = pd.read_csv(eof1_files[doy], header=None, delim_whitespace=True, names=['eof1'])
        tmp2 = pd.read_csv(eof2_files[doy], header=None, delim_whitespace=True, names=['eof2'])
        eof1 = xr.DataArray(np.reshape(tmp1.eof1.values,(nlat, nlon)),dims=['lat','lon'])
        eof2 = xr.DataArray(np.reshape(tmp2.eof2.values,(nlat, nlon)),dims=['lat','lon'])
        EOF1[doy,:,:] = eof1.values
        EOF2[doy,:,:] = eof2.values

    return EOF1, EOF2  


def read_rmm_eofs(eofpath='UserScript_fcstGFS_obsERA_RMM/'):
    """
    Read the OMI EOFs from file and into a xarray DataArray.
    :param eofpath: filepath to the location of the eof files
    :return: EOF1 and EOF2 2D DataArrays
    """
    olrfile = eofpath+'rmm_olr_eofs.txt'
    u850file = eofpath+'rmm_u850_eofs.txt'
    u200file = eofpath+'rmm_u200_eofs.txt'


    # observed EOFs from BOM Australia are saved in individual text files for each variable
    # horizontal resolution of EOFs is 2.5 degree and longitudes go from 0 - 375.5, column1 is eof1
    # column 2 is eof2 in each file

    EOF1 = xr.DataArray(np.empty([3,144]),dims=['var','lon'],
    coords={'var':['olr','u850','u200'], 'lon':np.arange(0,360,2.5)})
    EOF2 = xr.DataArray(np.empty([3,144]),dims=['var','lon'],
    coords={'var':['olr','u850','u200'], 'lon':np.arange(0,360,2.5)})
    nlon = len(EOF1['lon'])

    tmp = pd.read_csv(olrfile, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[0,:] = tmp.eof1.values
    EOF2[0,:] = tmp.eof2.values
    tmp = pd.read_csv(u850file, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[1,:] = tmp.eof1.values
    EOF2[1,:] = tmp.eof2.values
    tmp = pd.read_csv(u200file, header=None, delim_whitespace=True, names=['eof1','eof2'])
    EOF1[2,:] = tmp.eof1.values
    EOF2[2,:] = tmp.eof2.values

    return EOF1, EOF2               


def regress_3dim_data_onto_eofs(data, time, EOF1, EOF2):
    """
    Finds time-dependent coefficients w.r.t the DOY-dependent EOF basis for time-dependent spatially 
    resolved data.
    I.e. it finds the PCs for temporally resolved OLR data.
    :param data: data DataArray to project onto the EOFs
    :param time: datetime64 time array
    :param EOF1: the day of year dependent EOF1
    :param EOF2: the day of year dependent EOF2
    :return: PCs
    """
    if not np.all(data.lat == EOF1.lat):
        raise ValueError("Latitude grid of EOFs and OLR is not equal.")
    if not np.all(data.lon == EOF1.lon):
        raise ValueError("Longitude grid of EOFs and OLR is not equal.")
    pc1 = np.empty(data.time.size)
    pc2 = np.empty(data.time.size)
    nlat = len(data.lat)
    nlon = len(data.lon)

    for idx, val in enumerate(time):
        olr_singleday = data.sel(time=val)
        # get doy, only works of day is datetime or date object
        doy = pd.to_datetime(val).timetuple().tm_yday
        
        (pc1_single, pc2_single) = regress_vector_onto_eofs(
            np.reshape(olr_singleday.values,(nlat*nlon)), np.reshape(EOF1[doy-1,:,:].values,(nlat*nlon)), 
            np.reshape(EOF2[doy-1,:,:].values,(nlat*nlon)) )
        
        pc1[idx] = pc1_single
        pc2[idx] = pc2_single

    return pc1, pc2


def regress_2dim_data_onto_eofs(data, time, EOF1, EOF2):
    """
    Finds time-dependent coefficients w.r.t the 2D EOF basis for time-dependent longitudinally 
    resolved data.
    I.e. it finds the PCs for temporally resolved OLR data.
    :param data: data DataArray to project onto the EOFs
    :param time: datetime64 time array
    :param EOF1: the day of year dependent EOF1
    :param EOF2: the day of year dependent EOF2
    :return: PCs
    """
    pc1 = np.empty(time.size)
    pc2 = np.empty(time.size)
    nlon = len(data.lon_ext)

    for idx, val in enumerate(time):
        olr_singleday = data[idx,:]
        
        (pc1_single, pc2_single) = regress_vector_onto_eofs(
            np.reshape(olr_singleday.values,(nlon)), np.reshape(EOF1.values,(nlon)), 
            np.reshape(EOF2.values,(nlon)) )

        pc1[idx] = pc1_single
        pc2[idx] = pc2_single

    return pc1, pc2    


def regress_vector_onto_eofs(vector: np.ndarray, eof1: np.ndarray, eof2: np.ndarray):
    """
    Helper method that finds the coefficients of the given vector with respect to the given basis of 
    2 EOFs. The computed coefficients are the PCs in the terminology of the EOF analysis.
    :param vector: The vector for which the coefficients in the EOF basis should be found.
    :param eof1: EOF basis vector 1.
    :param eof2: EOF basis vector 2.
    :return: The two PCs.
    """
    eof_mat = np.array([eof1, eof2]).T

    # Alternative implementation 1:
    x = np.linalg.lstsq(eof_mat, vector, rcond=None)
    pc1, pc2 = x[0]

    return pc1, pc2


def bandpass_filter_3D(data, time, a, b):
    """
    Filter 3D data in time. Bandpass filter limits are given in units of days. Assumes filter dimension 
    is the first dimension of the array (time x lat x lon). This method is much faster than the spectral
    filter in perform_3dim_spectral_filtering below. However, it does not give the same answer! If speed
    is of importance this routine can be used, but for accurancy  perform_3dim_spectral_filtering is
    reccomended.
    :param data: input DataArray to be filtered in time (time, lat, lon)
    :param time: datetime64 time array
    :param a: short period limit in days
    :param b: long period limit in days
    :return: filtered DataArray the same size as the input array
    """
    filtered_data = data.copy()

    dt = (time[1] - time[0]).astype('timedelta64[s]') / np.timedelta64(1, 'D')

    # remove linear trend from data in time
    data = detrend(data,axis=0,type='linear',overwrite_data=True)

    # taper time window and pad with zeros
    orig_data = data
    orig_nt, nm, nl = orig_data.shape
    
    nt = 2 ** 17  # Zero padding for performance and resolution optimization, as well as consistency with origininal Kiladis code

    if orig_nt > nt:
        raise ValueError('Time series is longer than hard-coded value for zero-padding!')

    data = np.zeros([nt, nm, nl])
    data[0:orig_nt, :, :] = orig_data

    # 10 days tapering according ot Kiladis Code
    # only relevant at beginning of time series as it is zero-padded in the end
    for idx_l in range(0, nl):
        for idx_m in range(0, nm):
            data[:, idx_m, idx_l] = taper_vector_to_zero(data[:, idx_m, idx_l], int(10 / dt))

    # set up frequency array for masking

    W = fftfreq(data[:,0,0].size, dt)
    W = np.tile(W,(nm,nl,1))
    W = np.moveaxis(W,2,0)
    P = 1 / W

    # run fft
    data_fft = rfft(data,axis=0)
        
    data_fft = np.where(P<a, 0, data_fft)
    data_fft = np.where(P>b, 0, data_fft)

    filter = irfft(data_fft,axis=0)
    filtered_data.values = filter[0:orig_nt, :, :]

    return filtered_data  


def rem_120day_mean(data, time):
    """
    Filter 3D data in time. Bandpass filter limits are given in units of days. Assumes filter dimension 
    is the first dimension of the array (time x lat x lon)
    :param data: input DataArray to remove previous 120 day time mean from
    :param time: datetime64 time array
    :return: DataArray containing the data with the previous 120day mean removed from each time step
    """
    filtered_data = data.copy()
    dt = (time[1] - time[0]).astype('timedelta64[s]') / np.timedelta64(1, 'D')
    ntim_mean = int(120/dt)

    for idx, val in enumerate(time):
        if idx>ntim_mean:
            filtered_data[idx,:] = filtered_data[idx,:].values - np.nanmean(data[idx-ntim_mean:idx+1,:].values, axis=0)
        else:
            filtered_data[idx,:] = filtered_data[idx,:].values - np.nanmean(data[0:idx+1,:].values, axis=0)   

    return filtered_data       


def zon_avg_variance(data):
    """
    Compute zonally averaged temporal variance for 2D data.
    :param data:  DataArray (time x lon) 
    :return: numpy array (1)
    """
    # compute temporal variance at each longitude
    var = np.nanvar(data,axis=0)

    # compute zonal mean of the temporal variance
    zavg_var  = np.nanmean(var)     

    return zavg_var     


def taper_vector_to_zero(data, window_length):
    """
    Taper the data in the given vector to zero at both the beginning and the ending.
    :param data: The data to taper.
    :param window_length: The length of the window (measured in vector indices),
        in which the tapering is applied for the beginning and the ending independently
    :return: The tapered data.
    """
    startinds = np.arange(0, window_length, 1)
    endinds = np.arange(-window_length - 1, -1, 1) + 2

    result = data
    result[0:window_length] = result[0:window_length] * 0.5 * (1 - np.cos(startinds * np.pi / window_length))
    result[data.size - window_length:data.size] = \
        result[data.size - window_length:data.size] * 0.5 * (1 - np.cos(endinds * np.pi / window_length))
    return result


def perform_3dim_spectral_filtering(data, time_spacing, period_min, period_max, 
    wn_min: float, wn_max: float):
        """
        Bandpass-filters OLR data in time- and longitude-direction according to
        the original Kiladis algorithm.
        Note that the temporal and longitudinal dimension have in principle
        different characteristics, so that they are in detail treated a bit
        differently:
        While the time is evolving into infinity (so that the number of data
        points and the time_spacing variable are needed to calculate the
        full temporal coverage), the longitude is periodic with the periodicity
        of one globe (so that it is assumed that the data covers exactly one
        globe and only passing the number of longitudes provides already the complete information).
        :param data: The OLR data as 2-dim array: first dimension time, second
            dimension longitude, both equally spaced.
            The longitudinal dimension has to cover the full globe.
            The time dimension is further described by the variable
            `time_spacing`.
        :param time_spacing: Temporal resolution of the data in days (often 1 or 0.5 (if two
            data points exist per day)).
        :param period_min: Minimal period (in days) that remains in the dataset.
        :param period_max: Maximal period (in days) that remains in the dataset.
        :param wn_min: Minimal wavenumber (in cycles per globe) that remains in the dataset.
        :param wn_max: Maximal wavenumber (in cycles per globe) that remains in the dataset.
        :param do_plot: If True, diagnosis plots will be generated.
        :param save_debug: If true, some variables will be filled with values of intermediate processing steps
            for debugging purposes.
        :return: The filtered data.
        """

        # ###################### Process input data #######################
        dataperday = 1 / time_spacing
        freq_min = 1 / period_max
        freq_max = 1 / period_min

        # ######################## Detrend #################################
        # "orig" refers to the original size in the time dimension in the following, i.e. not the zero-padded version.
        filtered_data = data.copy()
        orig_data = data
        orig_nt, nm, nl = orig_data.shape
        lat = orig_data['lat']

        print('detrending in time')
        orig_data = detrend(orig_data, axis=0, type='linear', overwrite_data=True)

        # ######################## Zero Padding ############################
        nt_max = 2 ** 17  # Zero padding for performance and resolution optimization, as well as consistency with origininal Kiladis code
        #nt = nt_max
        nt = orig_nt+1000 # this is a much faster option, but has slight differences to the original OMI

        if orig_nt > nt_max:
            raise ValueError('Time series is longer than hard-coded value for zero-padding!')

        data = np.zeros([nt, nm, nl])
        data[0:orig_nt, :, :] = orig_data

        # ######################## Tapering to zero ########################
        # 10 days tapering according ot Kiladis Code
        # only relevant at beginning of time series as it is zero-padded in the end
        print('taper beginning of time series to zero')
        for idx_l in range(0, nl):
            for idx_m in range(0, nm):
                data[:, idx_m, idx_l] = taper_vector_to_zero(data[:, idx_m, idx_l], int(10 * dataperday))

        # ########################## Forward Fourier transform ############
        

        # ## Calculation of the frequency grid in accordance with Kiladis code
        freq_axis = np.zeros(nt)
        for i_f in range(0, nt):
            if (i_f <= nt / 2):
                freq_axis[i_f] = i_f * dataperday / nt
            else:
                freq_axis[i_f] = -1 * (nt - i_f) * dataperday / nt
        # the following code based on scipy function produces qualitatively the same grid.
        # However, numerical differences seem to have larger effect for the filtering step.
        # freq_axis = np.fft.fftfreq(nt, d=time_spacing)
        # freq_axis = np.fft.fftshift(freq_axis)
        # freq_axis = np.roll(freq_axis, int(nt/2))

        # ## Calculation of the wavenumber grid in accordance with Kiladis code
        wn_axis = np.zeros(nl)
        for i_wn in range(0, nl):
            if i_wn <= nl / 2:
                wn_axis[i_wn] = -1 * i_wn
                # note: to have this consistent with the time-dimension, one could write wn_axis[i_wn]= -1*i_wn*dataperglobe/nl
                # However, since data is required to cover always one globe nl will always be equal to dataperglobe
                # The sign is not consistent with the time dimension, which is for reasons of consitency with the original Kiladis implementation
            else:
                wn_axis[i_wn] = nl - i_wn
        # the following code based on scipy function produces qualitatively the same grid.
        # However, numerical differences seem to have larger effect for the filtering step.
        # wn_axis = np.fft.fftfreq(nl, d=dy)
        # wn_axis = np.fft.fftshift(wn_axis)  #identical with  wn_axis=np.arange(-int(nlong/2), int(nlong/2),1.)
        # wn_axis = -1 *wn_axis
        # wn_axis = np.roll(wn_axis, int(nl/2))

        # ################### Filtering of the Fourier Spectrum #############
        # ## name filter boundaries like in Kiladis Fortran Code
        f1 = freq_min
        f2 = freq_min
        f3 = freq_max
        f4 = freq_max
        s1 = wn_min
        s2 = wn_max
        s3 = wn_min
        s4 = wn_max

        for idx_m, ilat in enumerate(lat):
            print('filtering latitude: '+str(ilat))
            fourier_fft = np.fft.fft2(np.squeeze(data[:,idx_m,:]))
            # reordering of spectrum is done to be consistent with the original kiladis ordering.
            fourier_fft = np.fft.fftshift(fourier_fft, axes=(0, 1))
            fourier_fft = np.roll(fourier_fft, int(nt / 2), axis=0)
            fourier_fft = np.roll(fourier_fft, int(nl / 2), axis=1)

            # ### Very similar to original Kiladis Code
            fourier_fft_filtered = fourier_fft
            count = 0
            for i_f in range(0, int(nt / 2) + 1):
                for i_wn in range(0, nl):
                    ff = freq_axis[i_f]
                    ss = wn_axis[i_wn]
                    if ((ff >= ((ss * (f1 - f2) + f2 * s1 - f1 * s2) / (s1 - s2))) and
                            (ff <= ((ss * (f3 - f4) + f4 * s3 - f3 * s4) / (s3 - s4))) and
                            (ss >= ((ff * (s3 - s1) - f1 * s3 + f3 * s1) / (f3 - f1))) and
                            (ss <= ((ff * (s4 - s2) - f2 * s4 + f4 * s2) / (f4 - f2)))):
                        count = count + 1
                    else:
                        fourier_fft_filtered[i_f, i_wn] = 0
                        if i_wn == 0 and i_f == 0:
                            pass
                        elif i_wn == 0:
                            ind_f = nt - i_f
                            if (ind_f < nt):
                                fourier_fft_filtered[ind_f, i_wn] = 0
                        elif i_f == 0:
                            ind_wn = nl - i_wn
                            if ind_wn < nl:
                                fourier_fft_filtered[i_f, ind_wn] = 0
                        else:
                            ind_f = nt - i_f
                            ind_wn = nl - i_wn
                            if ind_f < nt and ind_wn < nl:
                                fourier_fft_filtered[ind_f, ind_wn] = 0

            # ############################ FFT Backward transformation ############
            # #reorder spectrum back from kiladis ordering to python ordering
            fourier_fft_filtered = np.roll(fourier_fft_filtered, -int(nt / 2), axis=0)
            fourier_fft_filtered = np.roll(fourier_fft_filtered, -int(nl / 2), axis=1)
            fourier_fft_filtered = np.fft.ifftshift(fourier_fft_filtered, axes=(0, 1))
            filtered_olr = np.fft.ifft2(fourier_fft_filtered)
            filtered_olr = np.real(filtered_olr)

            # ############################# remove zero padding elements ##########
            filtered_data[:, idx_m, :] = filtered_olr[0:orig_nt, :] 

        # ToDo: Make sure that result is real
        return filtered_data
