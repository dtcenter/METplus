import sys
import numpy as np
import pandas as pd
from met.point_nc import nc_point_obs
from metcalcpy.diagnostics import land_surface
from metpy.units import units

pd.set_option('display.max_rows', None)

# Get the input PB2NC output filename as the input to this script
pb2nc = sys.argv[1]

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

# Array to hold the CTP values for each station
ctp = np.array([])

# Process each group, which is defined as a single site
# Each site will have the MET 11-column data.
for name,group in groups:

  print("PROCESSING FOR SITE: %s" % (name))
  
  # First, make sure there is only one valid time
  timegrp = group.groupby('vld')
  if timegrp.ngroups>1:
    print("WARNING! FOUND MULTIPLE SOUNDINGS FOR THIS SITE.")
    print("USING THE FIRST")
    timegrp_name = [sg_name for sg_name,sg_df in timegrp]
    prof = timegrp.get_group(timegrp_name[0])
  else:
    prof = group

  # Filter out stations that we don't want to process
  if name not in point_data['sid'].values.tolist():
    continue

  # In each group here, there are rows for each variable at each pressure level.
  # Thus, we can subset based on TMP and just use the pressure data for TMP.
  sub = prof[prof['var']=='TMP']

  # Ensure the temperature subset has data
  if len(sub)==0:
    print("NO DATA!")
    ctp = np.append(ctp,-9999.)
    continue

  # Subset out the data for this site into individual arrays
  # and add units using MetPy
  tmpsub = sub['obs'].astype('float').values*units('degK')
  prssub = sub['lvl'].astype('float').values*units('hPa')
  qcsub = sub['qc'].astype('int').values

  # The pressures must exceed 300 hPa above the lowest in the sounding
  if max(prssub.m)<= min(prssub.m+300.0):
    print("")
    print("WARNING! SOUNDING TOP PRESSURE DOES NOT EXCEED 300 hPa ABOVE THE LOWEST PRESSURE.")
    print("UNABLE TO COMPUTE CTP FOR SID: %s" % (name))
    ctp = np.append(ctp,-9999.)
  else:
    # Append the CTP value
    thisctp = land_surface.calc_ctp(prssub,tmpsub)
    ctp = np.append(ctp,thisctp.m)

# After each station is processed, add in the missing 11-column data
# lvl --> set to 1000.0
# hgt --> set to 0
# qc --> set to 'NA' for now
# var --> set to "CTP"
# typ --> reset from ADPUPA to ADPSFC
point_data['obs'] = ctp
point_data['lvl'] = [1000.0]*len(point_data)
point_data['hgt'] = [0]*len(point_data)
point_data['qc'] = ['NA']*len(point_data)
point_data['var'] = ['CTP']*len(point_data)
point_data['typ'] = ['ADPSFC']*len(point_data)

# Assign proper dtypes
met_col_dtypes = {'typ':'string',
                  'sid':'string',
                  'vld':'string',
                  'lat':'float64',
                  'lon':'float64',
                  'elv':'float64',
                  'var':'string',
                  'lvl':'float64',
                  'hgt':'float64',
                  'qc':'string',
                  'obs':'float64'}
point_data = point_data.astype(met_col_dtypes)

# Reorder the columns to be correct
point_data = point_data[['typ','sid','vld','lat','lon','elv','var','lvl','hgt','qc','obs']]

print(point_data)

# Convert to MET object
point_data = point_data.values.tolist()
