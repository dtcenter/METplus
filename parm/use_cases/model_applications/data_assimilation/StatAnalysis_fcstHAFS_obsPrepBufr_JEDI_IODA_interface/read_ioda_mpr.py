from __future__ import print_function

import pandas as pd
import os
from glob import glob
import sys
import xarray as xr
import datetime as dt

########################################################################

def read_netcdfs(files, dim):
    paths = sorted(glob(files))
    datasets = [xr.open_dataset(p) for p in paths]
    combined = xr.concat(datasets, dim)
    return combined

########################################################################
print('Python Script:\t', sys.argv[0])

# Input is directory of .nc or .nc4 files

if len(sys.argv) == 2:
    # Read the input file as the first argument
    input_dir = os.path.expandvars(sys.argv[1])
    try:
        print("Input File:\t" + repr(input_dir))
       
        # Read all from a directory 
        ioda_data = read_netcdfs(input_dir+'/*.nc*', dim='nlocs')
        
        # Grab variables list
        var_list = ioda_data['variable_names@VarMetaData'].isel(nlocs=[0]).str.decode('utf-8').values
        var_list = [i.strip() for i in var_list[0] if i]

        # Use only nlocs dimension to ensure a table
        ioda_data = ioda_data.drop_dims('nvars')
        ioda_df = ioda_data.to_dataframe()
           
        nlocs = len(ioda_df.index)
        print('Number of locations in set: ' + str(nlocs)) 

        # Decode strings
        ioda_df.loc[:,'datetime@MetaData'] = ioda_df.loc[:,'datetime@MetaData'].str.decode('utf-8') 
        ioda_df.loc[:,'station_id@MetaData'] = ioda_df.loc[:,'station_id@MetaData'].str.decode('utf-8')

        # Datetime format. Need YYYYMMD_HHMMSS from YYYY-MM-DDTHH:MM:SSZ.           
        time = ioda_df.loc[:,'datetime@MetaData'].values.tolist()

        for i in range(0,nlocs):        
            temp = dt.datetime.strptime(time[i], '%Y-%m-%dT%H:%M:%SZ')
            time[i] = temp.strftime('%Y%m%d_%H%M%S')
            
        ioda_df.loc[:,'datetime@MetaData'] = time

        mpr_data = []
        var_list = [i for i in var_list if i+'@hofx' in ioda_df.columns]

        for var_name in var_list:
            
            # Subset the needed columns
            ioda_df_var = ioda_df[['datetime@MetaData','station_id@MetaData',var_name+'@ObsType',
                                'latitude@MetaData','longitude@MetaData','air_pressure@MetaData',
                                var_name+'@hofx',var_name+'@ObsValue',
                                var_name+'@PreQC']]
            
            # Find locations with ObsValues
            ioda_df_var = ioda_df_var[ioda_df_var[var_name+'@ObsValue'] < 1e9] 
            nlocs = len(ioda_df_var.index)
            print(var_name+' has '+str(nlocs)+' obs.')
            
            # Add additional columns
            ioda_df_var['lead'] = '000000'
            ioda_df_var['MPR'] = 'MPR'
            ioda_df_var['nobs'] = nlocs
            ioda_df_var['index'] = range(0,nlocs)
            ioda_df_var['varname'] = var_name
            ioda_df_var['na'] = 'NA'

            # Arrange columns in MPR format
            cols = ['na','na','lead','datetime@MetaData','datetime@MetaData','lead','datetime@MetaData',
                    'datetime@MetaData','varname','na','lead','varname','na','na',
                    var_name+'@ObsType','na','na','lead','na','na','na','na','MPR',
                    'nobs','index','station_id@MetaData','latitude@MetaData','longitude@MetaData',
                    'air_pressure@MetaData','na',var_name+'@hofx',var_name+'@ObsValue',
                    var_name+'@PreQC','na','na']
            
            ioda_df_var = ioda_df_var[cols]

            # Into a list and all to strings
            mpr_data = mpr_data + [list( map(str,i) ) for i in ioda_df_var.values.tolist() ]
            
            print("Total Length:\t" + repr(len(mpr_data)))

    except NameError: 
        print("Can't find the input files or the variables.")
        print("Variables in this file:\t" + repr(var_list))
else:
    print("ERROR: read_ioda_mpr.py -> Must specify directory of files.\n")
    sys.exit(1)

########################################################################

