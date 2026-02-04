import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

outdir = sys.argv[1]

# Directories where point_stat MPR files are
ctp_dir = f'{outdir}/point_stat/CTP'
hmi_dir = f'{outdir}/point_stat/HI'

# Get a list of files for CIP and HI and sort them
ctp_files = glob.glob(os.path.join(ctp_dir,'*_mpr.txt'))
ctp_files.sort()
hmi_files = glob.glob(os.path.join(hmi_dir,'*_mpr.txt'))
hmi_files.sort()

# Determine the MPR column names and store them for later
ctp_cols = pd.read_csv(ctp_files[0],nrows=1,header=None)[0].str.split(expand=True).iloc[0].tolist()
hmi_cols = pd.read_csv(hmi_files[0],nrows=1,header=None)[0].str.split(expand=True).iloc[0].tolist()

# Read each MPR file into a dataframe without the header
ctp_list = [pd.read_csv(x,header=None,skiprows=1)[0].str.split(expand=True) for x in ctp_files]
hmi_list = [pd.read_csv(x,header=None,skiprows=1)[0].str.split(expand=True) for x in hmi_files]

# Concatenate all the MPR files into a single dataframe
ctp_df = pd.concat(ctp_list)
hmi_df = pd.concat(hmi_list)

# Add the columns
ctp_df.columns = ctp_cols
hmi_df.columns = hmi_cols

# Align the sites between CTP/HMI- sometimes the calculation will fail at some sites leading
# to an inconsistent match between sites with both, or only 1 of the two metrics
ctp_df = ctp_df[ctp_df['OBS_SID'].isin(hmi_df['OBS_SID'])]
hmi_df = hmi_df[hmi_df['OBS_SID'].isin(ctp_df['OBS_SID'])]

# Sort each subset based on some criteria. Note that there could be multiple forecast lead times
# at the same valid time, for each station.
ctp_sort = ctp_df.sort_values(['FCST_LEAD','FCST_VALID_BEG','OBS_SID'])
hmi_sort = hmi_df.sort_values(['FCST_LEAD','FCST_VALID_BEG','OBS_SID'])

fig, (ax1, ax2) = plt.subplots(2,1,figsize=(22,15))
fcst = ax1.scatter(hmi_sort['FCST'].astype('float'),ctp_sort['FCST'].astype('float'),c='k',s=50)
obs = ax1.scatter(hmi_sort['OBS'].astype('float'),ctp_sort['OBS'].astype('float'),c='b',s=50)
ax1.legend([fcst,obs],['FCST','OBS'],fontsize=18)
ax1.set_ylabel('CTP (J/kg)',fontsize=24)
ax1.set_xlabel('Humidity Index (C)',fontsize=24)
ax1.set_xlim([-10,100])
ax1.set_ylim([-1100,1000])
ax1.set_yticks([-1000,-750,-500,-250,0,250,500,750,1000])
ax1.set_xticks(ax1.get_xticks())
ax1.set_yticklabels(ax1.get_yticks(),fontsize=24)
ax1.set_xticklabels(ax1.get_xticks(),fontsize=24)
ax1.axhline(0.0,linewidth=2,c='k')
ax1.grid(which='both')
nsites = int(len(hmi_sort))
ax1.set_title(f'Convective Triggering Potential vs. Humidity Index for {nsites} Fcst/Obs Pairs',loc='center',fontsize=32)
ax2.scatter(hmi_sort['FCST'].astype('float')-hmi_sort['OBS'].astype('float'),ctp_sort['FCST'].astype('float')-ctp_sort['OBS'].astype('float'),c='r',s=50)
ax2.set_ylabel('CTP [FCST-OBS] (J/kg)',fontsize=24)
ax2.set_xlabel('Humidity Index [FCST-OBS] (C)',fontsize=24)
ax2.axhline(0.0,linewidth=2,c='k')
ax2.axvline(0.0,linewidth=2,c='k')
ax2.grid(which='both')
ax2.set_xlim([-50,50])
ax2.set_ylim([-1100,1000])
ax2.set_yticks([-1000,-750,-500,-250,0,250,500,750,1000])
ax2.set_xticks(ax2.get_xticks())
ax2.set_yticklabels(ax2.get_yticks(),fontsize=24)
ax2.set_xticklabels(ax2.get_xticks(),fontsize=24)
plt.savefig(f'{outdir}/compare_ctp_hi.png')
