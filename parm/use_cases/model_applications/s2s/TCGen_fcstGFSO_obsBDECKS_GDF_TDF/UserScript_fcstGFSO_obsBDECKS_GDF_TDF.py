#!/usr/bin/env python

import xarray as xr
import sys, datetime, multiprocessing

# Import METplotpy
from metplotpy.contributed.tc_s2s_panel import plot_tc_s2s_panel as tc_s2s_panel

# Enviromnment variables for use case
GDF_INPUT_FILENAME = "/home/dadriaan/projects/s2s/gdf/output801/met_tool_wrapper/TCGen/tc_gen_2016_pairs.nc"
GDF_LAT_HALF_DELTA = 5.0
GDF_LON_HALF_DELTA = 5.0
GDF_MODEL_STRING = 'GFSO' # use METplus "MODEL"
GDF_OBS_STRING = 'BEST'
GDF_DESC_STRING = 'GDF'
GDF_EARLY_STRING = 'GDF_EARLY'
GDF_LATE_STRING = 'GDF_LATE'
GDF_NORM_YEARS = 4.0 # --> use this to normalize the GDF?

# Compute the total number of model forecasts that could have forecasted a hypothetical genesis event
# within the user defined lead window
lead_step = 6 # how many hours between valid forecasts?
shortest_lead = 24 # what is the shortest forecast lead requested by user?
longest_lead = 120 # what is the longest forecast lead requested by user?
num_forecasts = float(len([shortest_lead + x for x in range(0,longest_lead,lead_step) if shortest_lead+x <= longest_lead]))

# Local variables
DEBUG = True

# Create some netCDF varname strings to use when referencing the data
fcstgenvarname = f"{GDF_DESC_STRING}_{GDF_MODEL_STRING}_GENESIS"
fcsthitvarname = f"{GDF_DESC_STRING}_{GDF_MODEL_STRING}_DEV_FY_OY"
fcstfalmvarname = f"{GDF_DESC_STRING}_{GDF_MODEL_STRING}_DEV_FY_ON"
obsmissvarname = f"{GDF_DESC_STRING}_{GDF_MODEL_STRING}_BEST_DEV_FN_OY"
obsgenvarname = f"{GDF_DESC_STRING}_BEST_GENESIS"
fcsttrackvarname = f"{GDF_DESC_STRING}_{GDF_MODEL_STRING}_TRACKS"
obstrackvarname = f"{GDF_DESC_STRING}_BEST_TRACKS"
fcstearlygenvarname = f"{GDF_EARLY_STRING}_{GDF_MODEL_STRING}_GENESIS"
fcstearlyhitvarname = f"{GDF_EARLY_STRING}_{GDF_MODEL_STRING}_DEV_FY_OY"
fcstlategenvarname = f"{GDF_LATE_STRING}_{GDF_MODEL_STRING}_GENESIS"
fcstlatehitvarname = f"{GDF_LATE_STRING}_{GDF_MODEL_STRING}_DEV_FY_OY"
if DEBUG:
  print("\nUSING VARIABLE NAMES:")
  print(f"Forecast genesis events varname: {fcstgenvarname}")
  print(f"Hits (fy_oy) varname::           {fcsthitvarname}")
  print(f"False alarms (fy_on) varname:    {fcstfalmvarname}")
  print(f"Miss (fn_oy) varname:            {obsmissvarname}")
  print(f"Observed genesis events varname: {obsgenvarname}")
  print(f"Forecast track points varname:   {fcsttrackvarname}")
  print(f"Observed track points varname:   {obstrackvarname}")
  print(f"Early genesis event varname:     {fcstearlygenvarname}")
  print(f"Early genesis hit varname:       {fcstearlyhitvarname}")
  print(f"Late genesis event varname:      {fcstlategenvarname}")
  print(f"Late genesis hit varname:        {fcstlatehitvarname}")

# Open the TCGen output file
tcgendata = xr.open_dataset(GDF_INPUT_FILENAME)

# Create 1D data to find locations of events
tcgendata1d = tcgendata.stack(adim=('lat','lon'))

# Get the lat/lon of EARLY FCST genesis events
earl_lat = tcgendata1d[fcstearlygenvarname].where(tcgendata1d[fcstearlygenvarname]>0.0,drop=True)['lat'].values
earl_lon = tcgendata1d[fcstearlygenvarname].where(tcgendata1d[fcstearlygenvarname]>0.0,drop=True)['lon'].values

# Get the lat/lon of LATE FCST genesis events
late_lat = tcgendata1d[fcstlategenvarname].where(tcgendata1d[fcstlategenvarname]>0.0,drop=True)['lat'].values
late_lon = tcgendata1d[fcstlategenvarname].where(tcgendata1d[fcstlategenvarname]>0.0,drop=True)['lon'].values

# Get the lat/lon of FCST genesis events
fcst_lat = tcgendata1d[fcstgenvarname].where(tcgendata1d[fcstgenvarname]>0.0,drop=True)['lat'].values
fcst_lon = tcgendata1d[fcstgenvarname].where(tcgendata1d[fcstgenvarname]>0.0,drop=True)['lon'].values

# Get the lat/lon of the OBS (BEST) genesis events
obs_lat = tcgendata1d[obsgenvarname].where(tcgendata1d[obsgenvarname]>0.0,drop=True)['lat'].values
obs_lon = tcgendata1d[obsgenvarname].where(tcgendata1d[obsgenvarname]>0.0,drop=True)['lon'].values

# Get the lat/lon of the FCST track points (based on genesis)
ftrk_lat = tcgendata1d[fcsttrackvarname].where(tcgendata1d[fcsttrackvarname]>0.0,drop=True)['lat'].values
ftrk_lon = tcgendata1d[fcsttrackvarname].where(tcgendata1d[fcsttrackvarname]>0.0,drop=True)['lon'].values

# Get the lat/lon of the OBS (BEST) track points (based on genesis)
otrk_lat = tcgendata1d[obstrackvarname].where(tcgendata1d[obstrackvarname]>0.0,drop=True)['lat'].values
otrk_lon = tcgendata1d[obstrackvarname].where(tcgendata1d[obstrackvarname]>0.0,drop=True)['lon'].values

# Function to take gridded counts of data and create a density plot given a lat/lon region defined by GDF_LAT/LON_HALF_DELTA around these counts.
# Input are the individual lats/lons of each location where there are any events, as well as the actual gridded variable of counts
def as_density(elats,elons,grid_var,fcst):

  # Create a DataArray that looks like the input grid_var
  dens_var = xr.zeros_like(grid_var,dtype='float32')

  # Try to re-write the while loop as a for loop
  #for clat,clon in tuple(zip(elats,elons)):
  llcnt = 0
  while llcnt < len(elats):

    clat = elats[llcnt]
    clon = elons[llcnt]

    # Latitude and longitude of subdomain around the point lat/lon
    glat = grid_var.lat[(grid_var.lat>=clat-GDF_LAT_HALF_DELTA) & (grid_var.lat<=clat+GDF_LAT_HALF_DELTA)]
    glon = grid_var.lon[(grid_var.lon>=clon-GDF_LON_HALF_DELTA) & (grid_var.lon<=clon+GDF_LON_HALF_DELTA)]

    # Get the number of events at the current point lat/lon
    nevent = grid_var.sel(lat=clat,lon=clon).values

    # Increment the dens_var where we want
    dens_var.loc[dict(lat=glat,lon=glon)] += nevent

    llcnt += 1

  # Return the dens_var
  if fcst:
    return(dens_var/(GDF_NORM_YEARS*num_forecasts))
  else:
    return(dens_var/(GDF_NORM_YEARS))

# Create some lists of function arguments to as_density() to run in parallel
varlist = [fcstgenvarname,fcsthitvarname,fcstfalmvarname,fcsttrackvarname,obsgenvarname,obsmissvarname,obstrackvarname,fcstlatehitvarname,fcstearlyhitvarname]
varlats = [fcst_lat,fcst_lat,fcst_lat,ftrk_lat,obs_lat,obs_lat,otrk_lat,late_lat,earl_lat]
varlons = [fcst_lon,fcst_lon,fcst_lon,ftrk_lon,obs_lon,obs_lon,otrk_lon,late_lon,earl_lon]
fcstobs = [True,True,True,True,False,True,False,True,True]
denvars = ['FCST_DENS','FYOY_DENS','FYON_DENS','FTRK_DENS','OBS_DENS','FNOY_DENS','OTRK_DENS','LHIT_DENS','EHIT_DENS']

# Use multiprocessing to run in parallel
# Results is a list of DataArray objects
mp = multiprocessing.Pool(multiprocessing.cpu_count()-2)
results = mp.starmap(as_density,[(x,y,tcgendata[z],f) for x,y,z,f  in tuple(zip(varlats,varlons,varlist,fcstobs))])

# Unpack the results
for r,n in tuple(zip(results,denvars)):
  tcgendata[n] = r

if DEBUG:
  print("\nOBS_DENS")
  print(tcgendata['OBS_DENS'].min().values)
  print(tcgendata['OBS_DENS'].max().values)
  print("\nFCST_DENS")
  print(tcgendata['FCST_DENS'].min().values)
  print(tcgendata['FCST_DENS'].max().values)
  print("\nFYOY_DENS")
  print(tcgendata['FYOY_DENS'].min().values)
  print(tcgendata['FYOY_DENS'].max().values)
  print("\nFYON_DENS")
  print(tcgendata['FYON_DENS'].min().values)
  print(tcgendata['FYON_DENS'].max().values)
  print("\nFNOY_DENS")
  print(tcgendata['FNOY_DENS'].min().values)
  print(tcgendata['FNOY_DENS'].max().values)
  print("\nFTRK_DENS")
  print(tcgendata['FTRK_DENS'].min().values)
  print(tcgendata['FTRK_DENS'].max().values)
  print("\nOTRK_DENS")
  print(tcgendata['OTRK_DENS'].min().values)
  print(tcgendata['OTRK_DENS'].max().values)
  print("\nEHIT_DENS")
  print(tcgendata['EHIT_DENS'].min().values)
  print(tcgendata['EHIT_DENS'].max().values)
  print("\nLHIT_DENS")
  print(tcgendata['LHIT_DENS'].min().values)
  print(tcgendata['LHIT_DENS'].max().values)

# Call plotting for GDF. tc_s2s_panel.plot_gdf() requires just the Xarray Dataset object
# Panel order for GDF is:
# 1. Total BEST (observed) genesis density
# 2. Total MODEL (forecast) genesis density
# 3. Difference 2-1
gdf_varlist = ['OBS_DENS','FCST_DENS']
tc_s2s_panel.plot_gdf(tcgendata[gdf_varlist])

# Call plotting for TDF. tc_s2s_panel.plot_tdf() requires just the Xarray Dataset object
# Panel order for TDF is:
# 1. Total BEST (observed) track points
# 2. Total FCST (hour 24-120) track points
# 3. FCST-BEST
tdf_varlist = ['FTRK_DENS','OTRK_DENS']
tc_s2s_panel.plot_tdf(tcgendata[tdf_varlist])

# Call plotting for GDF category. tc_s2s_panel.plot_gdf_cat() requires just the Xarray Dataset object
# Panel order for GDF category is:
# 1. Total HITS density
# 2. Total EARLY HITS density
# 3. Total LATE HITS density
# 4. Total FALSE_ALARMS density
gdf_cat_varlist = ['FYOY_DENS','EHIT_DENS','LHIT_DENS','FYON_DENS']
tc_s2s_panel.plot_gdf_cat(tcgendata[gdf_cat_varlist])

# Call plotting for GDF UFS. tc_s2s_panel.plot_gdf_ufs() requires just the Xarray Dataset object
# Panel order for GDF UFS is:
# 1. Total BEST (observed) genesis density (scatter is BEST genesis locations)
# 2. Total HITS density (scatter is BEST genesis locations)
# 3. Total FALSE_ALARMS density (scatter is FCST genesis locations, but only false?)
# 4. Total HITS+FALSE_ALARMS density (scatter is FCST genesis locations, but only hits+false?)
gdf_ufs_varlist = ['OBS_DENS','FYOY_DENS','FYON_DENS']
tc_s2s_panel.plot_gdf_ufs(tcgendata[gdf_ufs_varlist])
