import os
import numpy as np
import pandas as pd
import sys
from metcalcpy.diagnostics import land_surface
from metpy.units import units

# Append the MET Python module directory to the path to import the functions
sys.path.append(os.environ.get('MET_PYTHON_DIR'))
from met.point_nc import nc_point_obs

pd.set_option('display.max_rows', None)

# Get the input PB2NC output filename as the input to this script
pb2nc = sys.argv[1]

# Get the output filename for this script
outfile = sys.argv[2]

# Make the output directory if it doesn't exist
if not os.path.exists(os.path.dirname(outfile)):
  os.makedirs(os.path.dirname(outfile))

# Get the Pandas dataframe of the PB2NC data
df = nc_point_obs(pb2nc).to_pandas()

# Group the 11-column data by station. This will effectively create "soundings" for each site
groups = df.groupby('sid')
print("FOUND %04d SITES TO PROCESS" % (int(groups.ngroups)))

# The first row of each group contains the metadata we want to retain
point_data = groups.first().reset_index()[['sid','typ','vld','lat','lon','elv']]

# Filter out stations to not process here
point_data['site_digit'] = point_data['sid'].astype('str').str[0]
point_data = point_data[point_data['site_digit'].isin(['7'])]
point_data = point_data.drop(['site_digit'],axis=1)

# Subset to only sid/lat/lon for unique sid's
point_data = point_data[point_data['sid'].isin(point_data['sid'].unique())]
print("TOTAL OF %04d UNIQUE SITES" % (int(len(point_data))))

# Join the lat/lon as another column
point_data['latlon'] = point_data['lat'].astype('str')+' '+point_data['lon'].astype('str')

# Write out the text file that GenVxMask needs
point_data['latlon'].astype('object').to_csv(outfile,index=False,sep=' ',header=['RAOB_SITES'],quoting=3,escapechar=' ')

