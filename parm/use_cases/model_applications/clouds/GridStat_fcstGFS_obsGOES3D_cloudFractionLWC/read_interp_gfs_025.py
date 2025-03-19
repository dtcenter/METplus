import datetime
import numpy as np
import sys
import xarray as xr
from metpy.interpolate import log_interpolate_1d
from metpy.units import units

# Command line input arguments
model_file = sys.argv[1]
level = sys.argv[2]
valid = sys.argv[3]
leadhours = sys.argv[4]
varname = sys.argv[5]

# Process reuested level
if level!='L0':
  level = np.array(float(level)*1000.0)*units('m')

# Process time information
valid = datetime.datetime.strptime(valid,'%Y%m%d_%H%M%S')
init = valid-datetime.timedelta(hours=int(leadhours))

# For total cloud coverage
if varname=='TCC':
  tcc_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'tcc'},indexpath='')
  gph_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'gh'},indexpath='')
  tcc_var['tcc'].attrs['units'] = '%'
  gph_var['gh'].attrs['units'] = 'm'
  gph_var = gph_var.sel(isobaricInhPa=tcc_var.isobaricInhPa.values)
  tcc_lev = log_interpolate_1d(level,gph_var['gh'],tcc_var['tcc'],axis=0)

  met_data = tcc_lev.m[0,:,:]
  long_name = "Total Cloud Cover"
  units = "%"
  level = 'Z%d' % (int(level.m))

# For cloud water mixing ratio (content)
elif varname=='CLWC':
  gph_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'gh'},indexpath='')
  tmp_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'t'},indexpath='')
  clw_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'clwmr'},indexpath='')
  
  # CLWMR is only available at isobaric levels >= 100 hPa
  prs_lev = clw_var.isobaricInhPa[clw_var.isobaricInhPa>=100.0]
  prs_var = prs_lev.broadcast_like(gph_var)
  prs_var.attrs['units'] = 'hPa'
  prs_var = prs_var*100.0
  prs_var.attrs['units'] = 'Pa'
  tmp_var['t'].attrs['units'] = 'degK'
  clw_var['clwmr'].attrs['units'] = 'kg/kg'
  gph_var['gh'].attrs['units'] = 'm'

  # Subset the three fields to available pressure levels
  tmp_var = tmp_var.sel(isobaricInhPa=prs_lev)
  clw_var = clw_var.sel(isobaricInhPa=prs_lev)
  gph_var = gph_var.sel(isobaricInhPa=prs_lev)

  # Convert units from kg/kg to g/m3
  clw_var = ((clw_var['clwmr']*prs_var)*1000.0/(287.05*tmp_var['t']))
  
  clw_lev = log_interpolate_1d(level,gph_var['gh'],clw_var,axis=0)
  
  met_data = clw_lev.m[0,:,:]
  long_name = "Cloud Liquid Water Content"
  units = 'g/m3'
  level = 'Z%d' % (int(level.m))

# For the total atmospheric cloud water content
elif varname=='CLWP':

  gph_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'gh'},indexpath='')
  tmp_var = xr.open_dataset(model_file,engine='cfgrib',filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'t'},indexpath='')
  clw_var = xr.open_dataset(model_file,filter_by_keys={'typeOfLevel':'isobaricInhPa','shortName':'clwmr'},indexpath='')

  # CLWMR is only available at isobaric levels >= 100 hPa
  prs_lev = clw_var.isobaricInhPa[clw_var.isobaricInhPa>=100.0]
  prs_var = prs_lev.broadcast_like(gph_var)
  prs_var.attrs['units'] = 'hPa'
  prs_var = prs_var*100.0
  prs_var.attrs['units'] = 'Pa'
  tmp_var['t'].attrs['units'] = 'degK'
  clw_var['clwmr'].attrs['units'] = 'dimensionless'
  gph_var['gh'].attrs['units'] = 'm'

  # Subset the three fields to available pressure levels
  tmp_var = tmp_var.sel(isobaricInhPa=prs_lev)
  clw_var = clw_var.sel(isobaricInhPa=prs_lev)
  gph_var = gph_var.sel(isobaricInhPa=prs_lev)

  # Convert units from kg/kg to g/m3 to compare with obs
  clw_var = ((clw_var['clwmr']*prs_var)*1000.0/(287.05*tmp_var['t']))
  
  met_data = clw_var.sum(dim='isobaricInhPa').squeeze().values
  long_name = "Cloud Liquid Water Path"
  units = "g/m3"
  level = level

else:
  print("UNSUPPORTED varname IN SCRIPT")
  exit(1)

# Set the grid and data attributes as MET expects
attrs = {}
attrs['valid'] = valid.strftime('%Y%m%d_%H%M%S')
attrs['init'] = init.strftime('%Y%m%d_%H%M%S')
attrs['lead'] = '%02d0000' % (int(leadhours))
attrs['accum'] = '000000'
attrs['name'] = varname
attrs['long_name'] = long_name
attrs['level'] = level
attrs['units'] = units
attrs['grid'] = 'G193'
