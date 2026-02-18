
# Functions to pre-process data

def preprocess(path, model, init, variable, lead, clim_per, member):
    import numpy as np
    from netCDF4 import Dataset

    if clim_per == '1982_2010':
        years = np.arange(1982,2011,1)
    elif clim_per == '1991_2020':
        years = np.arange(1991,2020,1)
    else:
        print('ERROR: Check your climatology period')
        return None, None, None, None

    # Get the directory
    dir_name = path

    # Make an empty array to store the climatology and SD (just store for 1 lead, 1 member)
    full_fcst_array = np.zeros((len(years), 181, 360))
    anom = np.zeros((len(years), 181, 360))
    std_anom = np.zeros((len(years), 181, 360))

    for y in range(len(years)):
        year = years[y]    
        # Can comment out if this bothers you
        path = str(dir_name + model + '.' + variable + '.' + str(year) + str(init) + '.fcst.nc')
        #print('Opening ' + path)

        dataset  = Dataset(path)
        # Shape of array before subset (24, 10, 181, 360)
        fcst = dataset.variables['fcst'][member,lead,:,:]
        #print(fcst.shape)
        full_fcst_array[y,:,:] = fcst

    # Can comment out if this bothers you
    #print('Shape of fcst array with all times: ' + str(full_fcst_array.shape)) 

    # Define climatology for the lead and member of interest
    clim = np.nanmean(full_fcst_array,axis=0)
    
    # Define standard deviation for the lead and member of interest
    stddev = np.nanstd(full_fcst_array,axis=0)

    # Define anomalies and standardized anomalies (perhaps unnecessary)
    for y in range(len(years)):
        anom[y,:,:] = full_fcst_array[y,:,:] - clim
        std_anom[y,:,:] = anom[y,:,:]/stddev

    return clim, stddev, anom, std_anom
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
def dominant_tercile_fcst(path, model, init, variable, clim_per, lead):

    import numpy as np
    member = 0
    members = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

    n_ens = len(members)
 
    # Make climos, std anoms, etc. from function for 1 member (to get shapes for empty variables)
    _, _, _, std_anom = preprocess(path, model, init, variable, lead, clim_per, member)
    if std_anom is None:
        return None

    # Empty variables
    std_anom_all = np.zeros((std_anom.shape[0], std_anom.shape[1], std_anom.shape[2], n_ens))

    for i in range(len(members)):
        member = members[i]
        _, _, _, std_anom = preprocess(path, model, init, variable, lead, clim_per, member)
        std_anom_all[:, :, :, i] = std_anom

    ut_ones = np.where(std_anom_all[:,:,:,:] > 0.43,1,0)
    lt_ones = np.where(std_anom_all[:,:,:,:] < -0.43,1,0)
    mt_ones = np.where( (std_anom_all[:,:,:,:] > -0.43) & (std_anom_all[:,:,:,:] < 0.43),1,0)

    ut_prob = np.nansum(ut_ones,3)/len(members)
    lt_prob = np.nansum(lt_ones,3)/len(members)
    mt_prob = np.nansum(mt_ones,3)/len(members)

    # Put all in 1 array
    all_probs = np.zeros((3, ut_prob.shape[0], ut_prob.shape[1], ut_prob.shape[2]))

    all_probs[0,:,:,:] = lt_prob
    all_probs[1,:,:,:] = mt_prob
    all_probs[2,:,:,:] = ut_prob

    dominant_tercile = np.argmax(all_probs, axis=0)

    temp = np.where(dominant_tercile == 2, 3., dominant_tercile)
    temp = np.where(dominant_tercile == 1, 2., temp)
    temp = np.where(dominant_tercile == 0, 1., temp)

    # Swap lats to match obs (will swap back later)
    temp = temp[:,::-1,0:360]
    # Mask according to obs:
    # Note, will need to change path name here:
    data_mask = mask(path)

    temp_masked = np.zeros((temp.shape[0], temp.shape[1], temp.shape[2]))
    for i in range(0,temp.shape[0]):
        #MODIFIED BY JOHN O, CHANGE NANS TO -9999s
        temp_masked[i,:,:] = np.where(data_mask[:,0:360] == -9.99000000e+08, -9999, temp[i,:,:])

    cat_thresh_fcst = temp_masked[:,::-1,:]  # MET function swaps lats to normal, putting this back into abnormal

    return cat_thresh_fcst
# --------------------------------------------------------------------------------------------------




# --------------------------------------------------------------------------------------------------
def dominant_tercile_obs(path_obs):
    from netCDF4 import Dataset
    import numpy as np

    # Read in obs data
    obs_data = Dataset(path_obs + "ghcn_cams.1x1.1982-2020.mon.nc")
    obs_clim_data = Dataset(path_obs + "ghcn_cams.1x1.1982-2010.mon.clim.nc")
    obs_stddev_data = Dataset(path_obs + "ghcn_cams.1x1.1982-2010.mon.stddev.nc")


    print('Note this function for obs is ONLY meant to be used for January monthly verification with a 1982-2010 base period')
    obs_full = obs_data.variables['tmp2m'][:,:,:]
    obs_clim = obs_clim_data.variables['clim'][0,:,:]
    obs_stddev = obs_stddev_data.variables['stddev'][0,:,:]

    # Grab only Januaries
    obs_jan_full = obs_full[::12,:,:]

    # For 1982-2010
    obs_jan = obs_jan_full[0:29,:,:]

    # Make std anoms
    obs_std_anom = np.zeros((obs_jan.shape[0], obs_jan.shape[1], obs_jan.shape[2]))

    for t in range(0,obs_jan.shape[0]):
        obs_std_anom[t,:,:] = (obs_jan[t,:,:] - obs_clim) / obs_stddev

    ut_obs_ones = np.where(obs_std_anom[:,:,:] > 0.43,3,0)
    lt_obs_ones = np.where(obs_std_anom[:,:,:] < -0.43,1,0)
    mt_obs_ones = np.where( (obs_std_anom[:,:,:] > -0.43) & (obs_std_anom[:,:,:] < 0.43),2,0)

    # Put all in 1 array
    all_probs = np.zeros((3, ut_obs_ones.shape[0], ut_obs_ones.shape[1], ut_obs_ones.shape[2]))

    all_probs[0,:,:,:] = lt_obs_ones
    all_probs[1,:,:,:] = mt_obs_ones
    all_probs[2,:,:,:] = ut_obs_ones

    # Mask according to obs:
    # Note, will need to change path name here:
    data_mask = mask(path_obs)

    temp1 = np.nansum(all_probs,axis=0)
    temp  = temp1[:,:,0:360]

    temp_masked = np.zeros((temp.shape[0], temp.shape[1], temp.shape[2]))
    for i in range(0,temp.shape[0]):
        #MODIFIED BY JOHN O, CHANGE NANS TO -9999s
        temp_masked[i,:,:] = np.where(data_mask[:,0:360] == -9.99000000e+08, -9999, temp[i,:,:])

    cat_thresh_obs = temp_masked

    return cat_thresh_obs
# --------------------------------------------------------------------------------------------------






# --------------------------------------------------------------------------------------------------
def plot_bs(var_obs, plot_type):
    import numpy as np
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
    from matplotlib import ticker

    lats = np.arange(-90, 90, 1)
    lons = np.arange(0, 360, 1)

    if plot_type == 'BS':
        clevs = np.arange(0.025, 0.425, 0.025)
    elif plot_type == 'BS_clim':
        clevs = np.arange(0.025, 0.425, 0.025)
    elif plot_type == 'bs_py_min_met':
        clevs = np.arange(-0.1, 0.1, 0.01)
    elif plot_type == 'bsc_py_min_met':
        clevs = np.arange(-0.1, 0.1, 0.01)
    else:
        clevs = np.arange(-0.4, 0.4, 0.025)        
    if var_obs == 'tmp2m':
        my_blues = ['#5a00d2', '#3e9dff', '#30c6f3', '#00ffff', '#c7eab9']
        my_reds = ['#f9e3b4', '#eeff41', '#ffc31b', '#e69138', '#c43307']
    else:
        my_blues = ['#995005', '#da751f', '#e0a420', '#f9cb9c', '#f9e3b4']
        my_reds = ['#5affd1', '#b3eaac', '#75e478', '#4db159', '#2e8065']
    my_colors = my_blues+['white']+my_reds
    cmap = ListedColormap(my_colors, 'mycmap', N = len(clevs)-1)
    norm = BoundaryNorm(clevs, cmap.N)
    m = Basemap(projection='mill', resolution='l', llcrnrlon=0, llcrnrlat= -90,
                urcrnrlon=360, urcrnrlat = 90)
    fig = plt.figure(figsize=(10,10))

    return lats, lons, clevs, my_blues, my_reds, my_colors, cmap, norm, m, fig
# --------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------
def get_init_year(year):

    # There is absolutely a better way to do this...

    if year == '198201':
        idx = 0
    if year == '198301':
        idx = 1
    if year == '198401':
        idx = 2
    if year == '198501':
        idx = 3
    if year == '198601':
        idx = 4
    if year == '198701':
        idx = 5
    if year == '198801':
        idx = 6
    if year == '198901':
        idx = 7
    if year == '199001':
        idx = 8
    if year == '199101':
        idx = 9
    if year == '199201':
        idx = 10
    if year == '199301':
        idx = 11
    if year == '199401':
        idx = 12
    if year == '199501':
        idx = 13
    if year == '199601':
        idx = 14
    if year == '199701':
        idx = 15
    if year == '199801':
        idx = 16
    if year == '199901':
        idx = 17
    if year == '200001':
        idx = 18
    if year == '200101':
        idx = 19
    if year == '200201':
        idx = 20
    if year == '200301':
        idx = 21
    if year == '200401':
        idx = 22
    if year == '200501':
        idx = 23
    if year == '200601':
        idx = 24
    if year == '200701':
        idx = 25
    if year == '200801':
        idx = 26
    if year == '200901':
        idx = 27
    if year == '201001':
        idx = 28

    return idx
# --------------------------------------------------------------------------------------------------




# --------------------------------------------------------------------------------------------------
def mask(path_obs):  
    import numpy as np
    from netCDF4 import Dataset
    obs_data = Dataset(path_obs + "ghcn_cams.1x1.1982-2020.mon.nc")
    obs_mask_all = obs_data.variables['tmp2m'][::12,:,:]
    obs_mask = obs_mask_all[0,:,0:360]
    #print(obs_mask[:,100])
    obs_mask = np.where(obs_mask.all == '--', np.nan, obs_mask)
    #print(obs_mask[:,100])
    return obs_mask
# --------------------------------------------------------------------------------------------------
