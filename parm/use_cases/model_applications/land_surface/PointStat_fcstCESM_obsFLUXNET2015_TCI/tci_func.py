from xarray.core.dataarray import DataArray
from pandas.core.series import Series

#def calc_tci_cesm(soil_data,sfc_flux_data):
def calc_tci(soil_data,sfc_flux_data):

  # For Xarray objects, compute the mean 
  if isinstance(soil_data,DataArray) and isinstance(sfc_flux_data,DataArray):
    soil_mean = soil_data.mean(dim='time')
    soil_count = soil_data.count(dim='time')
    sfc_flux_mean = sfc_flux_data.mean(dim='time')
    soil_std = soil_data.std(dim='time')
    print(((soil_data-soil_mean) * (sfc_flux_data-sfc_flux_mean)))
    numer = ((soil_data-soil_mean) * (sfc_flux_data-sfc_flux_mean)).sum(dim='time')
  # For Pandas objects, compute the mean
  elif isinstance(soil_data,Series) and isinstance(sfc_flux_data,Series):
    soil_mean = soil_data.mean()
    soil_count = soil_data.count()
    sfc_flux_mean = sfc_flux_data.mean()
    soil_std = soil_data.std()
    numer = ((soil_data-soil_mean) * (sfc_flux_data-sfc_flux_mean)).sum()
  # No other object types are supported
  else:
    print("ERROR: Unrecognized Object Type in calc_tci.py")
    print(type(soil_data))
    print(type(sfc_flux_data))
    exit(1)

  covarTerm = numer / soil_count

  return covarTerm/soil_std

