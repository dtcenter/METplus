from __future__ import print_function

import pandas as pd
import os
from glob import glob
import sys
import xarray as xr
import datetime as dt

########################################################################

print('Python Script:\t', sys.argv[0])

# Input is .nc or .nc4 file

if len(sys.argv) == 2:
    # Read the input file as the first argument
    input_path = os.path.expandvars(sys.argv[1])
    try:
        print("Input File:\t" + repr(input_path))
       
        # Read all the needed groups 
        ioda_data = xr.open_dataset(input_path, group = 'MetaData')
        ioda_hofx_data = xr.open_dataset(input_path, group = 'hofx')

        hofx_vars = list(ioda_hofx_data.keys())
        
        # use dataframes 
        ioda_df = ioda_data.to_dataframe()
        ioda_data.close()        

        for var_name in hofx_vars:
            ioda_df[var_name + '@hofx'] = ioda_hofx_data[var_name]

        # Add columns for needed attributes, for each variable present for hofx
        for attribute in ['ObsValue', 'ObsType', 'EffectiveQC']:
            ioda_attr_data = xr.open_dataset(input_path, group = attribute)
            for var_name in hofx_vars:
                ioda_df[var_name + '@' + attribute] = ioda_attr_data[var_name]

        ioda_attr_data.close()        
        ioda_hofx_data.close()        

        nlocs = len(ioda_df.index)
        print('Number of locations in set: ' + str(nlocs)) 

        # Decode strings
        time = list(ioda_df['datetime'])

        for i in range(0,nlocs):        
            temp = dt.datetime.strptime(time[i], '%Y-%m-%dT%H:%M:%SZ')
            time[i] = temp.strftime('%Y%m%d_%H%M%S')
            
        ioda_df['datetime'] = time

        #set up MPR data
        mpr_data = []

        for var_name in hofx_vars:
            
            # Set up the needed columns
            ioda_df_var = ioda_df[['datetime','station_id',var_name+'@ObsType',
                                'latitude','longitude','air_pressure',
                                var_name+'@hofx',var_name+'@ObsValue',
                                var_name+'@EffectiveQC']]
            
            # Cute down to locations with valid ObsValues
            ioda_df_var = ioda_df_var[abs(ioda_df_var[var_name+'@ObsValue']) < 1e6] 
            nlocs = len(ioda_df_var.index)
            print(var_name+' has '+str(nlocs)+' valid obs.')
            
            # Add additional columns
            ioda_df_var['lead'] = '000000'
            ioda_df_var['MPR'] = 'MPR'
            ioda_df_var['nobs'] = nlocs
            ioda_df_var['index'] = range(0,nlocs)
            ioda_df_var['varname'] = var_name
            ioda_df_var['na'] = 'NA'

            # Arrange columns in MPR format
            cols = ['na','na','lead','datetime','datetime','lead','datetime',
                    'datetime','varname','na','lead','varname','na','na',
                    var_name+'@ObsType','na','na','lead','na','na','na','na','MPR',
                    'nobs','index','station_id','latitude','longitude',
                    'air_pressure','na',var_name+'@hofx',var_name+'@ObsValue',
                    var_name+'@EffectiveQC','na','na']
            
            ioda_df_var = ioda_df_var[cols]

            # Into a list and all to strings
            mpr_data = mpr_data + [list( map(str,i) ) for i in ioda_df_var.values.tolist() ]
                
            print("Total Length:\t" + repr(len(mpr_data)))
    
    except NameError: 
        print("Can't find the input file.")
        print("HofX variables in this file:\t" + repr(hofx_vars))
else:
    print("ERROR: read_iodav2_mpr.py -> Must specify input file.\n")
    sys.exit(1)

########################################################################

