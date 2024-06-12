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
point_data = point_data[point_data['site_digit']=='7']
point_data = point_data.drop(['site_digit'],axis=1)

# Array to hold the HI values for each station
hi = np.array([])

# Notes from development:
# 1. For some soundings, there are "-9999" for HGT values but not others. Why?
# 2. Some stations have clearly duplicate soundings, but different valid times.
#    I think because we are using a +/- 30 min window, and using soundings, it's
#    safe to just process one sounding for each site and assume the other is
#    a duplicate.
# 3. Some soundings only have a few levels. There are many ways to handle this:
#    a) require a pressure delta between lowest and highest level
#    b) require a minimum number of levels with good data
#    c) Ensure the uppermost pressure is at least 300 hPa above the lowest pressure (current)
# 4. The "QC" value from PB2NC appears to not be useful (it is almost always 2 from things I inspected
#    a) I changed the value to include values as high as 10 from PB2NC
# 5. I am using searchsorted in the calculator for CTP, which assumes the pressure array is sorted.
#    We should consider checking for duplicate, repeat, or improperly ordered pressure values somehow.
# 6. Why is dewpoint a different length than temperature? I guess this is because SPFH data are bad to derive
#    DPT, but, even if I set to "level 9" BUFR, there are still some levels missing...
# 7. The issue seems to be with the geopotential height data at significant thermodynamic levels (TTBB). It
#    appears to be missing, whilst the significant wind levels (PPBB) seem to have the geopotential height.
#    Also, the mandatory levels only show geopotential height whilst the wind data at mandatory levels
#    have a missing HGT, so get it from the TTAA levels if you need it.

# Each group should have temperature, dewpoint, and geopotential height. Pressure is a separate column already.
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

  # Filter out data where HGT = -9999.
  #prof = prof[(prof['hgt']!=-9999.)&(prof['lvl']>300.0)]

  # Filter out stations that we don't want to process
  if name not in point_data['sid'].values.tolist():
  #if name not in ['71908']:
    continue

  # TODO: REMOVE DEBUG
  #print("")
  #print("11 COLUMN INFO")
  #print("")
  #print(prof[['hgt','var','lvl','obs','qc','sid']])

  # We need to build in some sanity checking here. The 11-column data cannot
  # be gaurunteed to have each var at each pressure level. So we need only the
  # levels where the variables we are interested in occur.
  # But really CTP just needs temperature, which the 11-column data should have.

  # In each group here, there are rows for each variable at each pressure level.
  # Thus, we can subset based on TMP and just use the pressure for TMP.
  # Add units using MetPy
  tmpsub = prof[prof['var']=='TMP']
  dewsub = prof[prof['var']=='DPT']
  hgtsub = prof[prof['var']=='HGT']
  spfsub = prof[prof['var']=='SPFH']
  print(dewsub[['sid','lvl','hgt','obs','vld','var']])
  print(tmpsub[['sid','lvl','hgt','obs','vld','var']])
  print(hgtsub[['sid','lvl','hgt','obs','vld','var']])
  print(spfsub[['sid','lvl','hgt','obs','vld','var']])
  
  # Filter the data where hgt is not -9999.
  #tmpsub = tmpsub[tmpsub['hgt']!=-9999.]
  #dewsub = dewsub[dewsub['hgt']!=-9999.]

  print("")
  ntmp = len(tmpsub)
  ndew = len(dewsub)
  nhgt = len(hgtsub)
  nspf = len(spfsub)
  print("SITECOUNTS %s" % (name))
  print("FOUND %04d TMP OBS" % (ntmp))
  print("FOUND %04d DEW OBS" % (ndew))
  #print("FOUND %04d HGT OBS" % (nhgt))
  print("FOUND %04d SPFH OBS" % (nspf))

  #if ntmp!=ndew:
  #  print("WARNING! DIFFERENT NUMBER OF TMP AND DEW OBS.")
  #  hi = np.append(hi,-9999.)
  #  continue

  if ntmp == 0:
    print("NO DATA!")
    hi = np.append(hi,-9999.)
    continue

  # TODO: REMOVE DEBUG
  #print("")
  #print("11 COLUMN INFO TEMPERATURE ONLY")
  #print("")
  #print(tmpsub[['sid','lvl','hgt','obs','vld']])

  # Subset out the data for this site into individual arrays
  tmparr = tmpsub['obs'].astype('float').values*units('degK')
  dewarr = dewsub['obs'].astype('float').values*units('degK')
  prsarr = tmpsub['lvl'].astype('float').values*units('hPa')
  hgtarr = tmpsub['hgt'].astype('float').values*units('m')
  spfharr = spfsub['obs'].astype('float').values*units('kg/kg')
  tmpqc = tmpsub['qc'].astype('int').values
  dewqc = dewsub['qc'].astype('int').values
  spfqc = spfsub['qc'].astype('int').values
  print(tmpqc)
  print(dewqc)
  print(spfqc)
  
  # Find a site that has equivalent number of TMP/DEW/HGT
  if ntmp==ndew==nhgt:
    print("EQUAL")
    outdf = pd.DataFrame(columns=['pressure','height','temperature','dewpoint'])
    #outdf.columns=['pressure','height','temperature','dewpoint']
    outdf['pressure'] = prsarr.m
    #outdf['height'] = np.sort(hgtsub['obs'].astype('float').values)
    #outdf['height'] = hgtsub['obs'].astype('float').values
    outdf['height'] = hgtarr.m
    outdf['temperature'] = tmparr.m
    outdf['dewpoint'] = dewarr.m

    print("")
    print("PRESSURES/HGT FOR ZOB:")
    print(hgtsub['lvl'].astype('float').values*units('hPa'))
    print(hgtsub['hgt'].astype('float').values*units('m'))

    print("PRESSURES/HGT FOR TOB:")
    print(tmpsub['lvl'].astype('float').values*units('hPa'))
    print(tmpsub['hgt'].astype('float').values*units('m'))
    
    print("PRESSURES/HGT FOR D_DPT:")
    print(dewsub['lvl'].astype('float').values*units('hPa'))
    print(dewsub['hgt'].astype('float').values*units('m'))
    print(outdf)
    outdf.to_csv('2023031512_GDAS_Sounding_%s.csv' % (name),index=False)
  
  # Do some QC of the data here. We should probably check the min/max pressure?
  # Maybe the number of obs?
  ##print("NUMBER TEMPERATURE: %04d" % (len(tmpsub)))
  ##print("NUMBER PRESSURE: %04d" % (len(prssub)))
  ##print("MIN PRESSURE: %4.1f" % (min(prssub.m)))
  ##print("MAX PRESSURE: %4.1f" % (max(prssub.m)))
  # For now, let's just eliminate any sites with any "-9999." values in either:
  # 1. hgt, 2. lvl, or 3. obs
  #hgtmiss = sub[sub['hgt'].astype('float')==-9999.]
  #prsmiss = sub[sub['lvl'].astype('float')==-9999.]
  #obsmiss = sub[sub['obs'].astype('float')==-9999.]
  #if any(hgtmiss+prsmiss+obsmiss):
  #  ctp = np.append(ctp,-9999.)
  #else:
  # # Append the CTP value
  #  ctp = np.append(ctp,land_surface.calc_ctp(prssub,tmpsub).m)

  # The pressures must exceed 300 hPa above the lowest in the sounding
  if max(prsarr.m)<= min(prsarr.m+300.0):
    print("")
    print("WARNING! SOUNDING TOP PRESSURE DOES NOT EXCEED 300 hPa ABOVE THE LOWEST PRESSURE.")
    print("UNABLE TO COMPUTE HI FOR SID: %s" % (name))
    hi = np.append(hi,-9999.)
  elif not len(prsarr)==len(tmparr)==len(dewarr):
    print("")
    print("WARNING! UNEQUAL LENGTH DATA.")
    print("UNABLE TO COMPUTE HI FOR SID: %s" % (name))
    hi = np.append(hi,-9999.)
  elif np.max(prsarr.m) < 950.0:
    print(np.max(prsarr.m))
    print("")
    print("WARNING! LOWEST PRESSURE IS ABOVE 950 hPa!")
    print("UNABLE TO COMPUTE HI FOR SID: %s" % (name))
    hi = np.append(hi,-9999.)
  else:
    # Append the HI value
    thishi = land_surface.calc_humidity_index(prsarr,tmparr,dewarr,bot_pressure_hpa=950.,top_pressure_hpa=850.,interp=True)
    hi = np.append(hi,thishi.m)

# After each station is processed, add in the missing 11-column data
# lvl --> set to 1000.0
# hgt --> set to 0
# qc --> set to 'NA' for now
# var --> set to "CTP"
# typ --> reset from ADPUPA to ADPSFC
point_data['obs'] = hi
point_data['lvl'] = [1000.0]*len(point_data)
point_data['hgt'] = [0]*len(point_data)
point_data['qc'] = ['NA']*len(point_data)
point_data['var'] = ['HI']*len(point_data)
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
