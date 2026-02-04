# Script to read Point-Stat MPR files and Stat-Analysis -out_stat files and plot
# ME (bias) at station locations on a map

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import glob
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import pandas as pd
import sys

stat_analysis_file = sys.argv[1]
point_stat_output_dir = sys.argv[2]
obs_var = sys.argv[3]
obs_lev = sys.argv[4]
out_dir = sys.argv[5]

# Read the stat_analysis_file
sa_df = pd.read_csv(stat_analysis_file,sep='\\s+')

# Subset the stat_analysis file to only those lines with the requested variable
sa_df = sa_df[sa_df['OBS_VAR'].astype('str')==obs_var].reset_index()

# Sort the stat_analysis file by VX_MASK (OBS_SID)
sa_df = sa_df.sort_values(by='VX_MASK').reset_index()

# Read all available _mpr.txt files from point_stat at the point_stat_output_dir
# The VX_MASK column in the stat_analysis_file contains the OBS_SID values where there 
# are bias values. In order to get the OBS_LAT and OBS_LON values for plotting, we 
# need to collect all stations from all MPR files from PointStat. This is because if we pick
# only a single MPR file from a single time, all stations may not be present. So we must
# create a superset from all MPR files to ensure we get all the OBS_LAT/OBS_LON values
# for all stations in the stat_analysis output
point_stat_mpr_files = glob.glob(os.path.join(point_stat_output_dir,'*_mpr.txt'))
point_stat_mpr_files.sort()
df_list = [pd.read_csv(sf,sep='\\s+') for sf in point_stat_mpr_files]
sid_list = [df[['OBS_SID','OBS_LAT','OBS_LON','OBS_VAR']] for df in df_list]
all_sid = pd.concat(sid_list)
all_sid = all_sid[all_sid['OBS_VAR'].astype('str')==obs_var]
unique_sid = all_sid.drop_duplicates(subset=['OBS_SID']).sort_values(by='OBS_SID').reset_index()

# Ensure the list of stations from stat_analysis matches the unique list of stations from all MPR files
# and that they are in the same order
if (unique_sid['OBS_SID'].astype('str')==sa_df['VX_MASK'].astype('str')).all():
  sa_df['OBS_LAT'] = unique_sid['OBS_LAT']
  sa_df['OBS_LON'] = unique_sid['OBS_LON']
else:
  print("ERROR!")
  print("LIST OF STATIONS FROM MPR FILES DOES NOT MATCH STAT_ANALYSIS OUTPUT.")
  print("Error in UserScript: plot_point_stat_bias_map_ISMN.py")
  exit()

# Obtain some metadata to adorn the plot
fcst_valid_beg = sa_df['FCST_VALID_BEG'].astype('str').iloc[0]
fcst_valid_end = sa_df['FCST_VALID_END'].astype('str').iloc[0]
var_level = sa_df['FCST_LEV'].astype('str').iloc[0]
title_string_left = f"F-O (Mean Error, ME) for all forecasts valid \nfrom: {fcst_valid_beg}\nto: {fcst_valid_end}"
title_string_right = f"VAR_NAME: {obs_var}\nVAR_LEVEL: {var_level}"

# Now the sa_df dataframe contains OBS_LAT, OBS_LON, VX_MASK (OBS_SID), and ME, which we can plot on a map

# Create a figure with a map
fig = plt.figure(1,figsize=(22,15))
proj = ccrs.LambertConformal(central_longitude=-97.5,central_latitude=38.5)
ax1 = plt.subplot(111,projection=proj)
ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
ax1.add_feature(cfeature.STATES, linewidth=0.5)
ax1.add_feature(cfeature.BORDERS, linewidth=0.5)
ax1.set_extent([-125,-65,20,55])
ax1.set_title(title_string_left,loc='left',fontsize=18)
ax1.set_title(title_string_right,loc='right',fontsize=18)

# Create a color normalization to use for coloring the dots based on bias values
if obs_var=='SOILW':
  levels = np.arange(-0.1,0.11,0.01)
  units = 'fraction'
elif obs_var=='TSOIL':
  levels = np.arange(-10,11,1)
  units = 'K'

cmap = plt.get_cmap('RdBu_r')
norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N)
scatter = ax1.scatter(sa_df['OBS_LON'],sa_df['OBS_LAT'],c=sa_df['ME'],marker='.',s=500,cmap=cmap,norm=norm,transform=ccrs.PlateCarree())
cb = plt.colorbar(scatter,ax=ax1,orientation='vertical',extend='both',ticks=levels,shrink=0.75,pad=0.01)
cb.set_label(units,fontsize=18)
cb.ax.tick_params(labelsize=18)
plt.savefig(f"{out_dir}/{fcst_valid_beg}_{fcst_valid_end}_{obs_var}_{obs_lev}_ME_map.png")
