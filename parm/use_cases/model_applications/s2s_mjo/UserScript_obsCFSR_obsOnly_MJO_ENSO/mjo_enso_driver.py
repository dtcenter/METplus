#!/usr/bin/env python3

import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import warnings

import metcalcpy.contributed.mjo_enso.compute_mjo_enso as mj
import metplotpy.contributed.mjo_enso.plot_mjo_enso_indices as plt
import METreadnc.util.read_netcdf as read_netcdf


def read_eofs(taux_eofs_file, tauy_eofs_file, meofs_file):
     
    taux_eofs=xr.open_dataset(taux_eofs_file).eof
    tauy_eofs=xr.open_dataset(tauy_eofs_file).eof
    meofs = xr.open_dataset(meofs_file).meofs

    return taux_eofs,tauy_eofs,meofs 

def read_filters(filtx1fil,filtx2fil,filty1fil,filty2fil):
    filtx1=np.loadtxt(filtx1fil, delimiter=',')
    filtx2=np.loadtxt(filtx2fil, delimiter=',')
    filty1=np.loadtxt(filty1fil, delimiter=',')
    filty2=np.loadtxt(filty2fil, delimiter=',')

    return filtx1,filtx2,filty1,filty2

def run_mjo_enso_steps(inlabel,spd,filtx1,filtx2,filty1,filty2,taux_eofs,tauy_eofs,meofs,oplot_dir):
    
    # Get TAUX, TAUY, SST, UCURRENT, VCURRENT file listings and variable names
    taux_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_TAUX_INPUT']
    tauy_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_TAUY_INPUT']
    sst_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_SST_INPUT']
    ucur_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_UCUR_INPUT']
    vcur_filetxt = os.environ['METPLUS_FILELIST_'+inlabel+'_VCUR_INPUT']

    taux_var = os.environ[inlabel+'_TAUX_VAR_NAME']
    tauy_var = os.environ[inlabel+'_TAUY_VAR_NAME']
    sst_var = os.environ[inlabel+'_SST_VAR_NAME']
    u_var = os.environ[inlabel+'_UCUR_VAR_NAME']
    v_var = os.environ[inlabel+'_VCUR_VAR_NAME']

    # Read the listing of TAUX, TAUY, SST, UCUR, VCUR files
    with open(taux_filetxt) as tx:
        taux_input_files = tx.read().splitlines()
    if (taux_input_files[0] == 'file_list'):
        taux_input_files = taux_input_files[1:]
    with open(tauy_filetxt) as ty:
        tauy_input_files = ty.read().splitlines()
    if (tauy_input_files[0] == 'file_list'):
        tauy_input_files = tauy_input_files[1:]
    with open(sst_filetxt) as ts:
        sst_input_files = ts.read().splitlines()
    if (sst_input_files[0] == 'file_list'):
        sst_input_files = sst_input_files[1:]
    with open(ucur_filetxt) as uc:
        ucur_input_files = uc.read().splitlines()
    if (ucur_input_files[0] == 'file_list'):
        ucur_input_files = ucur_input_files[1:]
    with open(vcur_filetxt) as vc:
        vcur_input_files = vc.read().splitlines()
    if (vcur_input_files[0] == 'file_list'):
        vcur_input_files = vcur_input_files[1:]

    # Check the input data to make sure it's not all missing
    taux_allmissing = all(elem == 'missing' for elem in taux_input_files)
    if taux_allmissing:
        raise IOError ('No input TAUX files were found, check file paths')
    tauy_allmissing = all(elem == 'missing' for elem in tauy_input_files)
    if tauy_allmissing:
        raise IOError('No input TUAY files were found, check file paths')
    sst_allmissing = all(elem == 'missing' for elem in sst_input_files)
    if sst_allmissing:
        raise IOError('No input SST files were found, check file paths')
    ucur_allmissing = all(elem == 'missing' for elem in ucur_input_files)
    if ucur_allmissing:
        raise IOError('No input UCUR files were found, check file paths')
    vcur_allmissing = all(elem == 'missing' for elem in vcur_input_files)
    if vcur_allmissing:
        raise IOError('No input VCUR files were found, check file paths')
 
    netcdf_reader_taux=read_netcdf.ReadNetCDF()
    ds_taux=netcdf_reader_taux.read_into_xarray(taux_input_files)

    netcdf_reader_tauy=read_netcdf.ReadNetCDF()
    ds_tauy=netcdf_reader_tauy.read_into_xarray(tauy_input_files)

    netcdf_reader_sst=read_netcdf.ReadNetCDF()
    ds_sst=netcdf_reader_sst.read_into_xarray(sst_input_files)

    netcdf_reader_ucur=read_netcdf.ReadNetCDF()
    ds_ucur=netcdf_reader_ucur.read_into_xarray(ucur_input_files)

    netcdf_reader_vcur=read_netcdf.ReadNetCDF()
    ds_vcur=netcdf_reader_vcur.read_into_xarray(vcur_input_files)

    time = []
    for din in range(len(ds_taux)):
        ctaux = ds_taux[din]
        #ctime =  datetime.datetime.strptime(ctaux[taux_var].valid_time,'%Y%m%d_%H%M%S')
        ctime =  datetime.datetime.strptime(str(ctaux['time'][0].values)[0:10],'%Y-%m-%d')
        time.append(ctime.strftime('%Y-%m-%d'))
        #ctaux = ctaux.assign_coords(time=ctime)
        #ds_taux[din] = ctaux.expand_dims("time")

        ctauy = ds_tauy[din]
        #ctauy = ctauy.assign_coords(time=ctime)
        #ds_tauy[din] = ctauy.expand_dims("time")

        csst = ds_sst[din]
        #csst = csst.assign_coords(time=ctime)
        #ds_sst[din] = csst.expand_dims("time")

        cucur = ds_ucur[din]
        #cucur = cucur.assign_coords(time=ctime)
        #ds_ucur[din] = cucur.expand_dims("time")

        cvcur = ds_vcur[din]
        #cvcur = cvcur.assign_coords(time=ctime)
        #ds_vcur[din] = cvcur.expand_dims("time")

    time = np.array(time,dtype='datetime64[D]')

    everything_taux = xr.concat(ds_taux,"time")
    uflxa = everything_taux[taux_var]

    everything_tauy = xr.concat(ds_tauy,"time")
    vflxa = everything_tauy[tauy_var]

    everything_sst = xr.concat(ds_sst,"time")
    sst = everything_sst[sst_var]

    everything_ucur = xr.concat(ds_ucur,"time")
    u = everything_ucur[u_var]

    everything_vcur = xr.concat(ds_vcur,"time")
    v = everything_vcur[v_var]
    print(v.shape)
  
    # get taux_mjo and tauy_mjo

    uflx_mjo=mj.calc_tau_MJO(uflxa,taux_eofs,filtx1,filtx2)
    vflx_mjo=mj.calc_tau_MJO(vflxa,tauy_eofs,filty1,filty2)
   
    wpower=mj.calc_wpower_MJO(u,v,uflx_mjo,vflx_mjo)

    #sst = ds.sst.sel(lat=slice(-5,5)).mean(dim='lat',skipna=True)
    sst = sst.sel(lat=slice(-5,5)).mean(dim='lat',skipna=True)

    wmjoks = wpower.sel(lat=slice(-5,5)).mean(dim='lat',skipna=True)

    make,maki=mj.make_maki(sst,wmjoks,meofs)

    #Get the index output file
    index_file = os.environ['MAKE_MAKI_OUTPUT_TEXT_FILE']
    import csv
    date_format = '%Y-%m-%d'
    strDate=datetime.datetime.strptime(str(sst['time'][0].values)[0:10],date_format)
    endDate=datetime.datetime.strptime(str(sst['time'][-1].values)[0:10],date_format) 
    time_mon = pd.date_range(strDate, endDate, freq='MS')#.to_pydatetime().tolist()
    with open(index_file+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "MaKE", "MaKI"])
        for i in range(len(make)):
            writer.writerow([time_mon[i], make[i].data, maki[i].data])
    
    #Get times for plotting MaKE and MaKI indices
    plot_time_format = os.environ['PLOT_TIME_FMT'] 
    plot_start_time = datetime.datetime.strptime(os.environ['PLOT_TIME_BEG'],plot_time_format)
    plot_end_time = datetime.datetime.strptime(os.environ['PLOT_TIME_END'],plot_time_format)    

    make_plot = make.sel(time=slice(plot_start_time,plot_end_time))
    maki_plot = maki.sel(time=slice(plot_start_time,plot_end_time))

    # Get the output name and format for the MaKE and MaKi plot
    plot_name = os.path.join(oplot_dir,os.environ.get(inlabel+'_PLOT_OUTPUT_NAME',inlabel+'_MAKE_MAKI_timeseries'))
    plot_format = os.environ.get(inlabel+'_PLOT_OUTPUT_FORMAT','png')

    #plot the MaKE-MaKI indices
    plt.plot_make_maki(make_plot,maki_plot,np.array(make_plot['time'].values),plot_name,plot_format)
    

def main():
    
    # Get the EOF files
    taux_eofs_file = os.environ['TAUX_EOF_INPUT_FILE'] 
    tauy_eofs_file = os.environ['TAUY_EOF_INPUT_FILE'] 
    meofs_file = os.environ['WMJOK_SST_EOF_INPUT_FILE'] 

    # Read in the EOFS
    print('Reading the EOFs')
    taux_eofs,tauy_eofs,meofs = read_eofs(taux_eofs_file, tauy_eofs_file, meofs_file)
    print('Done with reading EOFs')

    #Get the filter weights files
    filtx1fil = os.environ['TAUX_Filter1_TEXTFILE']
    filtx2fil = os.environ['TAUX_Filter2_TEXTFILE']
    filty1fil = os.environ['TAUY_Filter1_TEXTFILE']
    filty2fil = os.environ['TAUY_Filter2_TEXTFILE']
    
    # Read in the weights of the filters
    filtx1,filtx2,filty1,filty2 = read_filters(filtx1fil,filtx2fil,filtx2fil,filty2fil)

    # Get Number of Obs per day
    spd = os.environ.get('OBS_PER_DAY',1)

   # Check for an output plot directory
    oplot_dir = os.environ.get('PLOT_OUTPUT_DIR','')
    if not oplot_dir:
        obase = os.environ['SCRIPT_OUTPUT_BASE']
        oplot_dir = os.path.join(obase,'plots')
    if not os.path.exists(oplot_dir):
        os.makedirs(oplot_dir) 
     
   # Determine if doing forecast or obs
    run_obs_mjo_enso = os.environ.get('RUN_OBS', 'False').lower()
    run_fcst_mjo_enso = os.environ.get('RUN_FCST', 'False').lower()

    if (run_obs_mjo_enso == 'true'):
        run_mjo_enso_steps('OBS', spd, filtx1, filtx2, filty1, filty2, taux_eofs, tauy_eofs, meofs,oplot_dir)

    if (run_fcst_mjo_enso == 'true'):
        run_mjo_enso_steps('FCST', spd, filtx1, filtx2, filty1, filty2, taux_eofs, tauy_eofs, meofs,oplot_dir)

    # nothing selected
    if (run_obs_mjo_enso == 'false') and (run_fcst_mjo_enso == 'false'):
        warnings.warn('Forecast and Obs runs not selected, nothing will be calculated')
        warnings.warn('Set RUN_FCST or RUN_OBS in the [user_en_vars] section to generate output')

if __name__ == "__main__":
    main()
