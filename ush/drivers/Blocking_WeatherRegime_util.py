import os
import netCDF4
import numpy as np
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub

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


def find_input_files(inconfig, use_init, intemplate, secondtemplate=''):
    loop_time, end_time, time_interval = get_start_end_interval_times(inconfig)
    skip_times = get_skip_times(inconfig)

    start_mth = loop_time.strftime('%m')
    template = inconfig.getraw('config',intemplate)
    if secondtemplate:
        template2 = inconfig.getraw('config',secondtemplate)
        file_list2 = []

    file_list = []
    yr_list = []
    if use_init:
        timname = 'init'
    else:
        timname = 'valid'
    input_dict = {}
    input_dict['loop_by'] = timname
    pmth = start_mth
    while loop_time <= end_time:
        lead_seq = get_lead_sequence(inconfig)
        for ls in lead_seq:
            new_time = loop_time + ls
            input_dict[timname] = loop_time
            input_dict['lead'] = ls

            outtimestuff = ti_calculate(input_dict)
            if skip_time(outtimestuff, skip_times):
                continue
            cmth = outtimestuff['valid'].strftime('%m')
            filepath = do_string_sub(template, **outtimestuff)
            if secondtemplate:
                filepath2 = do_string_sub(template2, **outtimestuff)
                if os.path.exists(filepath) and os.path.exists(filepath2):
                    file_list.append(filepath)
                    file_list2.append(filepath2)
                else:
                    file_list.append('')
                    file_list2.append('')
            else:
                if os.path.exists(filepath):
                    file_list.append(filepath)
                else:
                    file_list.append('')

            if (int(cmth) == int(start_mth)) and (int(pmth) != int(start_mth)):
                yr_list.append(int(outtimestuff['valid'].strftime('%Y')))
            pmth = cmth

        loop_time += time_interval

    if secondtemplate:
        file_list = [file_list,file_list2]
    yr_list.append(int(outtimestuff['valid'].strftime('%Y')))

    return file_list, yr_list

def read_nc_met(infiles,yrlist,invar):

    print("Reading in Data")

    #Find the first non empty file name so I can get the variable sizes
    locin = next(sub for sub in infiles if sub)
    indata = netCDF4.Dataset(locin)
    lats = indata.variables['lat'][:]
    lons = indata.variables['lon'][:]
    invar_arr = indata.variables[invar][:]
    indata.close()

    var_3d = np.empty([len(infiles),len(invar_arr[:,0]),len(invar_arr[0,:])])

    for i in range(0,len(infiles)):

        #Read in the data
        if infiles[i]:
            indata = netCDF4.Dataset(infiles[i])
            new_invar = indata.variables[invar][:]
            #new_invar = np.expand_dims(new_invar,axis=0)
            init_time_str = indata.variables[invar].getncattr('init_time')
            valid_time_str = indata.variables[invar].getncattr('valid_time')
            indata.close()
        else:
            new_invar = np.empty((1,len(var_3d[0,:,0]),len(var_3d[0,0,:])),dtype=np.float)
            new_invar[:] = np.nan
        var_3d[i,:,:] = new_invar

    yr = np.array(yrlist)
    sdim = len(var_3d[:,0,0])/float(len(yrlist))
    var_4d = np.reshape(var_3d,[len(yrlist),int(sdim),len(var_3d[0,:,0]),len(var_3d[0,0,:])])

    return var_4d,lats,lons,yr
