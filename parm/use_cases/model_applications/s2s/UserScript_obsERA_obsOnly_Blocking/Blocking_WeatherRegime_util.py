import os
import netCDF4
import numpy as np
import pandas as pd
import datetime
from metplus.util import pre_run_setup, config_metplus
#, get_start_end_interval_times, get_lead_sequence
#from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub

def parse_steps(config_list):

    steps_config_part_fcst = [s for s in config_list if "FCST_STEPS" in s]
    steps_list_fcst = []

    steps_config_part_obs = [s for s in config_list if "OBS_STEPS" in s]
    steps_list_obs = []

    # Setup the Steps
    if steps_config_part_fcst:
        steps_param_fcst = steps_config_part_fcst[0].split("=")[1]
        steps_list_fcst = steps_param_fcst.split("+")
        config_list.remove(steps_config_part_fcst[0])
    if steps_config_part_obs:
        steps_param_obs = steps_config_part_obs[0].split("=")[1]
        steps_list_obs = steps_param_obs.split("+")
        config_list.remove(steps_config_part_obs[0])

    config = pre_run_setup(config_list)
    if not steps_config_part_fcst:
        steps_param_fcst = config.getstr('config','FCST_STEPS','')
        steps_list_fcst = steps_param_fcst.split("+")
    if not steps_config_part_obs:
        steps_param_obs = config.getstr('config','OBS_STEPS','')
        steps_list_obs = steps_param_obs.split("+")

    return steps_list_fcst, steps_list_obs, config_list 


def write_mpr_file(data_obs,data_fcst,lats_in,lons_in,time_obs,time_fcst,mname,fvar,flev,ovar,olev,maskname,obslev,outfile):

    dlength = len(lons_in)
    bdims = data_obs.shape

    na_array = ['NA']*dlength
    for y in range(bdims[0]):
        for dd in range(bdims[1]):
            #clat = lats_in[dd]
            # Create a pandas array to write to a file
            if time_fcst['valid'][y][dd]:
                mpr_dict = {'VERSION':['V9.1']*dlength,'MODEL':[mname]*dlength,'DESC':na_array,
                    'FCST_LEAD':[time_fcst['lead'][y][dd]]*dlength,'FCST_VALID_BEG':[time_fcst['valid'][y][dd]]*dlength,
                    'FCST_VALID_END':[time_fcst['valid'][y][dd]]*dlength,'OBS_LEAD':[time_obs['lead'][y][dd]]*dlength,
                    'OBS_VALID_BEG':[time_obs['valid'][y][dd]]*dlength,'OBS_VALID_END':[time_obs['valid'][y][dd]]*dlength,
                    'FCST_VAR':[fvar]*dlength,'FCST_LEV':[flev]*dlength,'OBS_VAR':[ovar]*dlength,'OBS_LEV':[olev]*dlength,
                    'OBTYPE':['ADPUPA']*dlength,'VX_MASK':[maskname]*dlength,'INTERP_MTHD':['NEAREST']*dlength,
                    'INTERP_PNTS':[1]*dlength,'FCST_THRESH':na_array,'OBS_THRESH':na_array,'COV_THRESH':na_array,
                    'ALPHA':na_array,'LINE_TYPE':['MPR']*dlength,'':[dlength]*dlength,'':np.arange(0,dlength,1)+1,
                    '':na_array,'':lats_in,'':lons_in,'':[obslev]*dlength,'':na_array,'':data_fcst[y,0,:],
                    '':data_obs[y,0,:],'':na_array,'':na_array,'':na_array,'':na_array}
                mpr_df = pd.DataFrame(data=mpr_dict)
                ft_stamp = time_fcst['lead'][y][dd]+'L_'+time_fcst['valid'][y][dd][0:8]+'_'+time_fcst['valid'][y][dd][9:15]+'V'
                mpr_outfile_name = outfile+'_'+ft_stamp+'.stat'
                mpr_df.to_csv(mpr_outfile_name,sep='\t', index=False, header=True)


def read_nc_met(infiles,invar,nseasons,dseasons):

    print("Reading in Data")

    #Find the first non empty file name so I can get the variable sizes
    locin = next(sub for sub in infiles if sub)
    indata = netCDF4.Dataset(locin)
    lats = indata.variables['lat'][:]
    lons = indata.variables['lon'][:]
    invar_arr = indata.variables[invar][:]
    indata.close()

    var_3d = np.empty([len(infiles),len(invar_arr[:,0]),len(invar_arr[0,:])])
    init_list = []
    valid_list = []
    lead_list = []

    for i in range(0,len(infiles)):

        #Read in the data
        if infiles[i]:
            indata = netCDF4.Dataset(infiles[i])
            new_invar = indata.variables[invar][:]

            init_time_str = indata.variables[invar].getncattr('init_time')
            valid_time_str = indata.variables[invar].getncattr('valid_time')
            lead_dt = datetime.datetime.strptime(valid_time_str,'%Y%m%d_%H%M%S') - datetime.datetime.strptime(init_time_str,'%Y%m%d_%H%M%S')
            leadmin,leadsec = divmod(lead_dt.total_seconds(), 60)
            leadhr,leadmin = divmod(leadmin,60)
            lead_str = str(int(leadhr)).zfill(2)+str(int(leadmin)).zfill(2)+str(int(leadsec)).zfill(2)
            indata.close()
        else:
            new_invar = np.empty((1,len(var_3d[0,:,0]),len(var_3d[0,0,:])),dtype=np.float)
            init_time_str = ''
            valid_time_str = ''
            lead_str = ''
            new_invar[:] = np.nan
        init_list.append(init_time_str)
        valid_list.append(valid_time_str)
        lead_list.append(lead_str)
        var_3d[i,:,:] = new_invar

    #yr = np.array(yrlist)
    #if len(var_3d[:,0,0])%float(len(yrlist)) != 0:
    #    lowval = int(len(var_3d[:,0,0])/float(len(yrlist)))
    #    newarrlen = (lowval+1) * float(len(yrlist))
    #    arrexp = int(newarrlen - len(var_3d[:,0,0]))
    #    arrfill = np.empty((arrexp,len(var_3d[0,:,0]),len(var_3d[0,0,:])),dtype=np.float)
    #    arrfill[:] = np.nan
    #    var_3d = np.append(var_3d,arrfill,axis=0)
    #    print(var_3d.shape)
    #sdim = len(var_3d[:,0,0])/float(num_seasons)
    var_4d = np.reshape(var_3d,[nseasons,dseasons,len(var_3d[0,:,0]),len(var_3d[0,0,:])])

    # Reshape time arrays and store them in a dictionary
    init_list_2d = np.reshape(init_list,[nseasons,dseasons])
    valid_list_2d = np.reshape(valid_list,[nseasons,dseasons])
    lead_list_2d = np.reshape(lead_list,[nseasons,dseasons])
    time_dict = {'init':init_list_2d,'valid':valid_list_2d,'lead':lead_list_2d}

    return var_4d,lats,lons,time_dict
