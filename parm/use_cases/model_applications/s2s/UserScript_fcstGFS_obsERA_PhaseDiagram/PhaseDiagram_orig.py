"""
Read in OMI or RMM indices and plot phase diagram for specified dates. OMI values
can be obtained from https://psl.noaa.gov/mjo/, RMM values can be obtained from 
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
"""

import numpy as np
import pandas as pd
import datetime

from plot_mjo_indices import phase_diagram

# which index are we plotting
indexname = 'RMM'  # 'RMM' or 'OMI'

# set dates to read and plot
datestrt = 20120101
datelast = 20120331

# read data from text file
if indexname=='OMI':
    data = pd.read_csv('omi.1x.txt', header=None, delim_whitespace=True, names=['yyyy','mm','dd','hh','pc1','pc2','amp'])
elif indexname=='RMM':
    data = pd.read_csv('rmm.1x.txt',  header=None, delim_whitespace=True, names=['yyyy','mm','dd', 'pc1','pc2','phase','amp','source'])

DATES = data.yyyy.values*10000 + data.mm.values*100 + data.dd.values
MONTHS = data.mm.values
DAYS = data.dd.values
#print(dates)

istrt = np.where(DATES==datestrt)[0][0]
ilast = np.where(DATES==datelast)[0][0]
print(DATES[istrt], DATES[ilast])
#print(istrt, ilast)

# subset data to only the dates we want to plot
dates = DATES[istrt:ilast+1]
months = MONTHS[istrt:ilast+1]
days = DAYS[istrt:ilast+1]
print(dates.min(), dates.max())
PC1 = data.pc1.values[istrt:ilast+1]
PC2 = data.pc2.values[istrt:ilast+1]

# plot the phase diagram
phase_diagram(indexname,PC1,PC2,dates,months,days,indexname+'_phase','png')
