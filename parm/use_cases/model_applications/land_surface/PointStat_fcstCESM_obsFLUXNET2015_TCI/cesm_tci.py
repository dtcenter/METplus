"""
Code adapted from Meg Fowler,CGD,NCAR
The code computes the Terrestrial Coupling Index (TCI)
from latent Heat Flux and 10 cm Soil Moisture  
Designed to read Latent Heat Flux (from CAM) and Soil Temp (from CLM)
from two CESM files 
User needs to provide the season (DJF, MAM, JJA, or SON) in the METplus conf file
User can change the variables to compute TCI

Modified Nov 2023
"""
import metcalcpy.diagnostics.land_surface as land_sfc
import os
import pandas as pd
import sys
import xarray as xr

# The script expects five arguments:
# sfc_flux_file = Latent Heat Flux file (from CAM, CESM "community atmosphere model")
# sfc_flux_varname = Field name in sfc_flux_file to use when computing TCI
# soil_file = Soil Temperature file (from CLM, CESM "community land model")
# soil_varname = Field name in soil_file to use when computing TCI
# season = "DJF", "MAM", "JJA", or "SON"
if len(sys.argv) < 6:
  print("Must specify the following elements: ")
  print("sfc_flux_file")
  print("sfc_flux_varname")
  print("soil_file")
  print("soil_varname")
  print("season (DJF, MAM, JJA, or SON)")
  sys.exit(1)

# Store command line arguments
fileCAM = os.path.expandvars(sys.argv[1])
sfc_flux_varname = varCAM = sys.argv[2]
fileCLM = os.path.expandvars(sys.argv[3])
soil_varname = varCLM = sys.argv[4]
season = sys.argv[5]
if season not in ['DJF','MAM','JJA','SON']:
  print("ERROR: UNRECOGNIZED SEASON IN tci_from_cesm.py")
  sys.exit(1) 

print("Starting Terrestrial Coupling Index Calculation for: "+season)
dsCLM = xr.open_dataset(fileCLM, decode_times=False)
dsCAM = xr.open_dataset(fileCAM, decode_times=False)

# The same shape (dimensions/coordinates) are assumed between the CLM and CAM files
# However, some metadata differences prevent using Xarray functions to combine the fields.
# Thus, we extract the values from one Xarray object and attach it to the other.
dsCAM[soil_varname] = xr.DataArray(dsCLM[soil_varname].values,dims=['time','lat','lon'],coords=dsCAM.coords)
ds = dsCAM
print("Finished reading CAM and CLM files with Xarray.")

# Add a Pandas date range to subset by season
time_units, reference_date = ds.time.attrs['units'].split('since')
if time_units.strip() not in ['D','days','Days','DAYS']:
  print("ERROR: TIME UNITS EXPECTED TO BE DAYS IN tci_from_cesm.py")
  sys.exit(1)
else:
  ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='D')

# Group the dataset by season and subset to the season the user requested
szn = ds.groupby('time.season')[season]

# Use the shared coupling index function to compute the index
couplingIndex = land_sfc.calc_tci(szn[soil_varname],szn[sfc_flux_varname])

# Prepare for MET
# 1. Replace missing data with the MET missing data values
couplingIndex = xr.where(couplingIndex.isnull(),-9999.,couplingIndex)

# 2. Pull out the values into a NumPy object
met_data = couplingIndex.values

# 3. Reverse the ordering of met_data (flip the grid along the equator)
met_data = met_data[::-1]

# 4. Create a time variable formatted the way MET expects
time_var = ds.time.dt.strftime('%Y%m%d_%H%M%S').values[0]

# 5. Create  grid information. The CESM is on a lat/lon projection.
# lower left corner latitude
lat_ll = ds.lat.min().values
# lower left corner longitude
lon_ll = ds.lon.min().values
# number of latitude
n_lat = ds.sizes['lat']
# number of longitude
n_lon = ds.sizes['lon']
# latitude grid spacing
delta_lat = (ds.lat.max().values-lat_ll)/n_lat
# longitude grid spacing
delta_lon = (ds.lon.max().values-lon_ll)/n_lon

# 6. Create a dictionary for the LatLon grid and required attributes
grid_attrs = {'type': 'LatLon',
              'name': 'CESM Grid',
              'lat_ll': float(lat_ll),
              'lon_ll': float(lon_ll),
              'delta_lat': float(delta_lat),
              'delta_lon': float(delta_lon),
              'Nlat': int(n_lat),
              'Nlon': int(n_lon)}

# 7. Populate the attributes dictionary for MET
attrs = {'valid': time_var,
         'init': time_var,
         'lead': "000000",
         'accum': "000000",
         'name': 'TCI',
         'standard_name': 'terrestrial_coupling_index',
         'long_name': 'terrestrial_coupling_index',
         'level': '10cm_soil_depth',
         'units': 'W/m2',
         'grid': grid_attrs}

