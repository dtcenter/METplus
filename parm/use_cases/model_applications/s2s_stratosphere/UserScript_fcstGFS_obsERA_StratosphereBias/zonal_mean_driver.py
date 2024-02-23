#!/usr/bin/env python3

"""
Create meridonial mean statistics

"""
import os
import sys
import logging
import yaml
import xarray as xr  # http://xarray.pydata.org/
import metcalcpy.util.read_env_vars_in_config as readconfig
import metcalcpy.pre_processing.directional_means as directional_means
import METreadnc.util.read_netcdf as read_netcdf


def main():
    """
    Read arguments
    """
    inlabel = sys.argv[1].upper()
    timevar = sys.argv[2]

    """
    Read METplus environment variables
    """
    print('Reading Input Environment Variables')
    input_file = [os.environ[inlabel+'_INPUT_FILE_NAME']]
    output_dir = os.environ['OUTPUT_DIR']
    full_output_dir = os.path.join(output_dir,inlabel)

    """
    Setup logging
    """
    #logfile = "meridonial_mean.log"
    #logging_level = os.environ.get("LOG_LEVEL","logging.INFO")
    #logging.basicConfig(stream=logfile, level=logging_level)

    """
    Read dataset
    """
    print('Reading input data')
    file_reader = read_netcdf.ReadNetCDF()
    ds = file_reader.read_into_xarray(input_file)[0]
    ds = ds.rename({'lat':'latitude',
                    'lon':'longitude'})

    print('Computing Zonal means')
    uzm = directional_means.zonal_mean(ds.u)
    uzm = uzm.assign_coords(lat=("latitude",ds.latitude.values[:,0]))
    Tzm = directional_means.zonal_mean(ds.T)
    Tzm = Tzm.assign_coords(lat=("latitude",ds.latitude.values[:,0]))

    """
    Write output files if desired, by first creating a directory
    """
    print('Writing output zonal mean files')
    if not os.path.exists(full_output_dir):
        os.makedirs(full_output_dir)

    datetimeindex = ds.indexes[timevar].to_datetimeindex()
    out_ds = uzm.to_dataset()
    out_ds.u.attrs = ds.u.attrs
    out_ds['T'] = Tzm
    out_ds.T.attrs = ds.T.attrs
    for i in range(len(datetimeindex)):
        cur_date = datetimeindex[i]
        output_file = os.path.join(full_output_dir,inlabel+'_zonal_mean_U_T_'+cur_date.strftime('%Y%m%d_%H%M%S')+'.nc')
        out_write = out_ds.isel(time=i)
        # Add lead time as a variable
        if inlabel == 'OBS':
            out_write = out_write.assign(lead_time=[0.0])
        elif inlabel == 'FCST':
            #Grab Forecast Lead
            out_write = out_write.assign(lead_time=ds.lead_time[i])
        out_write.to_netcdf(output_file, 'w')



if __name__ == '__main__':
    main()
