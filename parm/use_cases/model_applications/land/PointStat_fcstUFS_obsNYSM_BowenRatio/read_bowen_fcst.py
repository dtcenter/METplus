import os
import sys
import datetime as dt
import numpy as np
import xarray as xr
from pathlib import Path

# Accept command line arguments from METplus (valid time, lead time, and forecast directory)
arg_cnt = len(sys.argv)
if arg_cnt < 8:
    print("ERROR: read_bowen_fcst.py -> Missing command line argument(s).")
    print("Usage: read_bowen_fcst.py VALID_TIME LEAD_TIME FCST_DIR")
    sys.exit(1)

last_index = 8
if last_index < arg_cnt:
    print(" INFO: read_bowen_fcst.py -> Too many arguments, ignored {o}.".format(
        o=' '.join(sys.argv[last_index:])))
    print("Usage: read_bowen_fcst.py VALID_TIME LEAD_TIME FCST_DIR")

valid_time = sys.argv[1]
lead_time = sys.argv[2]
fcst_dir = sys.argv[3]
output_dir = sys.argv[4]
sens_heat_flux_shortName = sys.argv[5]
latent_heat_flux_shortName = sys.argv[6]
min_latent_heat_flux = float(sys.argv[7])

# Ensure output directory exists
os.makedirs(output_dir, exist_ok='True')

# Calculate datetime information
valid_dt = dt.datetime.strptime(valid_time, '%Y%m%d%H')
lead_td = dt.timedelta(hours=int(lead_time))
init_dt = valid_dt - lead_td

# Set the forecast file name
fcst_file_grib = '{0}/{1}/{1}.f{2}.grib2'.format(fcst_dir, init_dt.strftime('%Y%m%d%H'), lead_time.zfill(3))
print(f"\nINFO: read_bowen_fcst.py opening file: {fcst_file_grib}")
path_obj = Path(fcst_file_grib)
if not path_obj.exists():
  print(f"NO SUCH FILE OR DIRECTORY")
  exit(1)

# Read sensible heat flux
shtfl = xr.open_dataset(fcst_file_grib,engine='cfgrib',backend_kwargs={'indexpath':'','filter_by_keys':{'shortName':sens_heat_flux_shortName}}).squeeze()
##shtfl.to_netcdf('shtfl.nc')

# Read latent heat flux
lhtfl = xr.open_dataset(fcst_file_grib,engine='cfgrib',backend_kwargs={'indexpath':'','filter_by_keys':{'shortName':latent_heat_flux_shortName}}).squeeze()
##lhtfl.to_netcdf('lhtfl.nc')

# Get lat/lon info
lat = shtfl.latitude
lon = shtfl.longitude

nx = shtfl.sizes['longitude']
ny = shtfl.sizes['latitude']

# Calculate bowen ratio
# bowen ratio = sensible heat flux / latent heat flux
bowen = shtfl[sens_heat_flux_shortName] / lhtfl[latent_heat_flux_shortName]
cond = ((lhtfl[latent_heat_flux_shortName]>min_latent_heat_flux) | (lhtfl[latent_heat_flux_shortName]<(-1.0*min_latent_heat_flux)))
bowen = xr.where(cond,bowen,0.0)
##bowen.to_netcdf('bowen.nc')
bowen = bowen.values 

# Convert data into a format METplus can read
met_data = bowen.copy()[::-1].astype(np.float64)

# Create the attrs dictionary
attrs = {
   'valid': valid_dt.strftime('%Y%m%d_%H%M%S'),
   'init': init_dt.strftime('%Y%m%d_%H%M%S'),
   'lead': lead_time,
   'accum': '00',
   'name': 'BOWEN',
   'long_name': 'Bowen Ratio',
   'level': 'L0',
   'units': 'none',
   'grid': {
       'name': 'hr1.conus',
       'type': 'Gaussian',
       'lon_zero': 0.,
       'nx': nx,
       'ny': ny,
    }
}
