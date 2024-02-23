import os
import sys
import numpy as np
import datetime as dt
import netCDF4 as nc4


if len(sys.argv) != 4:
    print("Must specify exactly one input file, variable name, and summary axis (lat, lon, latlon).")
    sys.exit(1)

# Read the input file as the first argument
input_file = os.path.expandvars(sys.argv[1])
var_name   = sys.argv[2]
axis       = sys.argv[3]

# Read the data
f = nc4.Dataset(input_file, 'r')
data = np.float64(f.variables[var_name][:])
met_data = np.transpose(data).copy()

if axis == "lon":
   lats   = list()
   lons   = list(np.float64(f.variables["lon"][:]))
elif axis == "lat":
   lats   = list(np.float64(f.variables["lat"][:]))
   lons   = list()

pres = list(list(np.float64(f.variables["pres"][:])))
times  = list()

lead_ma = f.variables["lead_time"][:]
lead = lead_ma.__int__()
vtime = f.variables["time"]
cur_date = nc4.num2date(vtime[:], vtime.units, vtime.calendar)
init = cur_date - dt.timedelta(hours=lead)
accum     = "00"

attrs = {
   'valid': cur_date.strftime("%Y%m%d_%H%M%S"),
   'init':   init.strftime("%Y%m%d_%H%M%S"),
   'lead':   str(int(lead)).zfill(2),
   'accum':  accum,

   'name':      var_name,
   'long_name': str(getattr(f.variables[var_name], "long_name")),
   'level':     axis + "_mean",
   'units':     str(getattr(f.variables[var_name], "units")),

   'grid': {
     'type'   : "SemiLatLon",
     'name'   : axis + "_mean",
     'lats'   : lats,
     'lons'   : lons,
     'levels' : pres,
     'times'  : times
   }
}

print("Attributes: " + repr(attrs))
