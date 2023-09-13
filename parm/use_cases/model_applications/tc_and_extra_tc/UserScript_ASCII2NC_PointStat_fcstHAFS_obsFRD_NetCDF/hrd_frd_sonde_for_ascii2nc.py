########################################################################
#
# Description:
#   Prepare HRD FRD (full-resolution data) dropsonde files for further
#   processing by the ascii2nc tool in MET.
#   Source: https://www.aoml.noaa.gov/hrd/data_sub/dropsonde.html
#
# Date:
#   December 2020
#
########################################################################

import re
import os
import sys
import numpy as np
import itertools
import datetime as dt
from datetime import datetime, timedelta
import pandas as pd

# Check arguments
if len(sys.argv) == 2:
  input_dir = os.path.expandvars(sys.argv[1])
  print("Input Dir:\t" + repr(input_dir))
else:
  print("ERROR:", sys.argv[0],
        "-> Must specify exactly one input file.")
  sys.exit(1)

# Empty object
my_data = pd.DataFrame()

for filename in sorted(os.listdir(input_dir)):
   input_file = os.path.join(input_dir, filename)

   # Open file
   with open(input_file, 'r') as file_handle:
      lines = file_handle.read().splitlines()
   readdata = False
   for idx, line in enumerate(lines):

    # Extract date, time and sonde info
       match_date = re.match(r'^ Date:(.*)', line)
       match_time = re.match(r'^ Time:(.*)', line)
       match_sonde = re.match(r'^ SID:(.*)', line)

       if match_date:
         date_items = match_date.group(1).split()[:1]
         lat = match_date.group(1).split()[:4]
       if match_time:
         time_items = match_time.group(1).split()[:1]
         lon = match_time.group(1).split()[:4]
       if match_sonde:
         sonde = match_sonde.group(1).split()[0]

         # Format the date and time
         date_formatted = \
           f"{date_items[0][:2]}{date_items[0][2:4]}{date_items[0][4:6]}_" +\
           f"{time_items[0][:2]}:{time_items[0][2:4]}:{time_items[0][4:6]}"
         valid_time = \
           dt.datetime.strptime(date_formatted, "%y%m%d_%H:%M:%S")
         print(f"Valid Time:\t{valid_time}")
       if line.startswith("IX"):
           readdata = True
           continue
       if not readdata:
           continue
       line    = line.strip()
       columns = line.split()
       dsec    = str(columns[1])     # time elasp (s)
       pres    = float(columns[2])   # pressure (mb)
       temp    = float(columns[3])   # temperature (C)
       temp    = temp + 273.15        # convert deg C to K
       relh    = float(columns[4])   # relative humidity (%)
       geop    = int(columns[5])     # geopotential mass height (m)
       wind_dir = int(columns[6])    # wind direction (E)
       wind_spd = float(columns[7])  # wind speed (m/s)
       wind_z   = float(columns[8])  # zonal wind (m/s)
       wind_m   = float(columns[9])  # meridional wind (m/s)
       wind_w   = float(columns[11]) # vertical velocity (m/s)
       zw       = int(columns[12])   # geopotential wind height (m)
       lat      = float(columns[17]) # lat (N)
       lon      = float(columns[18]) # lon (E)
       vld      = valid_time + dt.timedelta(seconds=float(dsec))

       # Skip line if dsec, lat, or lon are missing.
       # Or if pres and geop are missing.
       if dsec == -999.0 or lat == -999.0 or lon == -999.0 or +\
           (pres == -999.0 and geop == -999):
          continue

       # Store valid time in YYYYMMDD_HHMMSS format
       t_vld = vld.strftime('%Y%m%d_%H%M%S')

       # Flag values for the station elevation and qc
       elv = "-9999"
       qc  = "-9999"

       # Append observations for this line
       # Name variable using GRIB conventions:
       #   https://www.nco.ncep.noaa.gov/pmb/docs/on388/table2.html
       if temp != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "TMP", pres, geop, qc, temp]]))])

       if relh != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "RH", pres, geop, qc, relh]]))])

       if geop != -999.0 and pres != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "HGT", pres, geop, qc, geop]]))])

       if wind_dir != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "WDIR", pres, zw, qc, wind_dir]]))])

       if wind_spd != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "WIND", pres, zw, qc, wind_spd]]))])

       if wind_z != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "UGRD", pres, zw, qc, wind_z]]))])

       if wind_m != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "VGRD", pres, zw, qc, wind_m]]))])

       if wind_w != -999.0:
          my_data = pd.concat([my_data, pd.DataFrame(np.array(
            [["ADPUPA", str(sonde), t_vld, lat, lon, elv,
              "DZDT", pres, zw, qc, wind_w]]))])

# Prepare point_data object for ascii2nc
point_data = my_data.values.tolist()
print("Data Length:\t" + repr(len(point_data)))
print("Data Type:\t" + repr(type(point_data)))
