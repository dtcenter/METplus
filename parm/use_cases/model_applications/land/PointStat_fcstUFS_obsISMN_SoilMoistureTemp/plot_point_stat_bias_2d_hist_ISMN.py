# Script to read Point-Stat MPR files and Stat-Analysis -out_stat files and plot
# ME (bias) against the forecast (FCST) values in a 2D histogram

import glob
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import pandas as pd
import sys
from matplotlib.colors import BoundaryNorm

point_stat_output_dir = sys.argv[1]
obs_var = sys.argv[2]
obs_lev = sys.argv[3]
out_dir = sys.argv[4]

# Read all available _mpr.txt files from point_stat at the point_stat_output_dir
point_stat_mpr_files = glob.glob(os.path.join(point_stat_output_dir,'*_mpr.txt'))
point_stat_mpr_files.sort()
df_list = [pd.read_csv(sf,sep='\\s+') for sf in point_stat_mpr_files]
df = pd.concat(df_list)
df = df[df['OBS_VAR'].astype('str')==obs_var]

# Obtain some metadata to adorn the plot
fcst_valid_beg = df['FCST_VALID_BEG'].astype('str').iloc[0]
fcst_valid_end = df['FCST_VALID_END'].astype('str').iloc[0]
var_level = df['FCST_LEV'].astype('str').iloc[0]
title_string_left = f"F-O (Mean Error, ME) for all forecasts valid \nfrom: {fcst_valid_beg}\nto: {fcst_valid_end}"
title_string_right = f"VAR_NAME: {obs_var}\nVAR_LEVEL: {var_level}"

# Create a F-O column
df['FCST_MINUS_OBS'] = df['FCST'].astype('float32')-df['OBS'].astype('float32')

# Create a 2D histogram of F-O vs F
fig = plt.figure(1,figsize=(22,15))
ax1 = plt.subplot(111)
if obs_var=='SOILW':
  ymin = -0.1
  ymax = 0.1
  yincr = 0.01
  xmin = 0
  xmax = 1.0
  xincr = 0.05
  units = 'fraction'
elif obs_var=='TSOIL':
  ymin = -10
  ymax = 10
  yincr = 1
  xmin = df['FCST'].min().round()
  xmax = df['FCST'].max().round()
  xmin = xmin-2
  xmax = xmax+2
  xincr = 1
  units = 'K'

cmap = 'inferno'
bias_bins = np.arange(ymin,ymax+yincr,yincr)
fcst_bins = np.arange(xmin,xmax+xincr,xincr)
h1 = ax1.hist2d(np.clip(df['FCST'],fcst_bins[0],fcst_bins[-1]),np.clip(df['FCST_MINUS_OBS'],bias_bins[0],bias_bins[-1]),bins=[fcst_bins,bias_bins],cmap=cmap)
ax1.set_xlim(xmin,xmax)
ax1.set_ylim(ymin,ymax)
ax1.set_xticks(fcst_bins[::2])
ax1.set_yticks(bias_bins)
ax1.tick_params(axis='x',labelsize=18,rotation=45.0)
ax1.tick_params(axis='y',labelsize=18)
ax1.set_ylabel(obs_var+' (FCST-OBS), '+units,fontsize=18)
ax1.set_xlabel(obs_var+' FCST ('+units+')',fontsize=18)
title_string_left = f"F-O vs. F for all forecasts valid \nfrom: {fcst_valid_beg}\nto: {fcst_valid_end}"
title_string_right = f"VAR_NAME: {obs_var}\nVAR_LEVEL: {var_level}"
ax1.set_title(title_string_left,loc='left',fontsize=20)
ax1.set_title(title_string_right,loc='right',fontsize=20)
cb = plt.colorbar(h1[3],ax=ax1,orientation='vertical',extend='max',shrink=0.9,pad=0.01)
cb.set_label('count',fontsize=18)
cb.ax.tick_params(labelsize=18)
plt.savefig(f"{out_dir}/{fcst_valid_beg}_{fcst_valid_end}_{obs_var}_{obs_lev}_2D_hist.png")
