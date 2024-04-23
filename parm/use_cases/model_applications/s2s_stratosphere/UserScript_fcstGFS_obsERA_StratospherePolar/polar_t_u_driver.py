#!/usr/bin/env python3

"""
Create Polar Cap Temperatures and Polar Vortex Winds

"""
import os
import sys
import datetime
import numpy as np
import metcalcpy.pre_processing.directional_means as directional_means
import METreadnc.util.read_netcdf as read_netcdf
from metcalcpy.util.write_mpr import write_mpr_file


def main():
    """
    Read arguments
    """
    timevar = sys.argv[1]
    leadvar = sys.argv[2]

    """
    Read METplus filename lists
    """
    obs_filetxt = os.environ.get('METPLUS_FILELIST_OBS_INPUT','')
    fcst_filetxt = os.environ.get('METPLUS_FILELIST_FCST_INPUT','')

    with open(obs_filetxt) as ol:
        obs_infiles = ol.read().splitlines()
        # Remove the first line if it's there
        if (obs_infiles[0] == 'file_list'):
            obs_infiles = obs_infiles[1:]
    with open(fcst_filetxt) as fl:
        fcst_infiles = fl.read().splitlines()
        # Remove the first line if it's there
        if (fcst_infiles[0] == 'file_list'):
            fcst_infiles = fcst_infiles[1:]

    output_dir = os.environ['OUTPUT_DIR']
    full_output_dir = os.path.join(output_dir,'mpr')

    """
    Read dataset
    """
    file_reader = read_netcdf.ReadNetCDF()
    dsO = file_reader.read_into_xarray(obs_infiles)[0]
    dsO = dsO.rename({'lat':'latitude',
                    'lon':'longitude'})
    file_reader2 = read_netcdf.ReadNetCDF()
    dsF = file_reader2.read_into_xarray(fcst_infiles)[0]
    dsF = dsF.rename({'lat':'latitude',
                    'lon':'longitude'})

    """
    Limit Dataset to 100 - 1 hPa
    """
    dsO = dsO.sel(pres=slice(1,100))
    dsF = dsF.sel(pres=slice(1,100))


    """
    Create Polar Cap Temparatures for Forecast and Obs
    """
    TzmO = directional_means.zonal_mean(dsO.T)
    TzmO.assign_coords(lat=("latitude",dsO.latitude.values[:,0]))
    TO_6090 = directional_means.meridional_mean(TzmO, 60, 90)
    TzmF = directional_means.zonal_mean(dsF.T)
    TzmF.assign_coords(lat=("latitude",dsF.latitude.values[:,0]))
    TF_6090 = directional_means.meridional_mean(TzmF, 60, 90)

    """
    Create Polar Vortex Winds
    """
    UzmO = directional_means.zonal_mean(dsO.u)
    UzmO.assign_coords(lat=("latitude",dsO.latitude.values[:,0]))
    UO_6090 = directional_means.meridional_mean(UzmO, 50, 80)
    UzmF = directional_means.zonal_mean(dsF.u)
    UzmF.assign_coords(lat=("latitude",dsF.latitude.values[:,0]))
    UF_6090 = directional_means.meridional_mean(UzmF, 50, 80)


    """
    Add P to the levels since they are pressure levels
    """
    obs_lvls = ['P'+str(int(op)) for op in dsO.pres.values]
    obs_lvls2 = [str(int(op)) for op in dsO.pres.values]
    fcst_lvls = ['P'+str(int(fp)) for fp in dsF.pres.values]

    """
    Write output MPR files
    """
    dlength1 = len(TO_6090[0,:])
    dlength = dlength1*2 
    modname = os.environ.get('MODEL_NAME','GFS')
    maskname = os.environ.get('MASK_NAME','FULL')
    datetimeindex = dsF.indexes[timevar].to_datetimeindex()
    for i in range(len(datetimeindex)):
        valid_str = datetimeindex[i].strftime('%Y%m%d_%H%M%S')
        leadstr = str(int(leadvar)).zfill(2)+'0000'
        outobs = np.concatenate((TO_6090[i,:].values,UO_6090[i,:].values))
        outfcst = np.concatenate((TF_6090[i,:].values,UF_6090[i,:].values))
        write_mpr_file(outfcst,outobs,[0.0]*dlength,[0.0]*dlength,[leadstr]*dlength,[valid_str]*dlength,
            ['000000']*dlength,[valid_str]*dlength,modname,'NA',['PolarCapT']*dlength1+['PolarVortexU']*dlength1,
            ['K']*dlength1+['m/s']*dlength1,fcst_lvls*2,['PolarCapT']*dlength1+['PolarVortexU']*dlength1,
            ['K']*dlength1+['m/s']*dlength1,obs_lvls*2,maskname,obs_lvls2*2,full_output_dir,'polar_cap_T_stat_'+modname)




if __name__ == '__main__':
    main()
