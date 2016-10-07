
#!/usr/bin/env python


#
# Logging
#

#Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR = "/d1/minnawin/SBU_out/logs"
LOG_FILENAME="init.log"


#
# Output Directories
# 
OUT_DIR = "/d1/minnawin/SBU_out/series_analysis"


#
# Tile constants
#

# These are used to create the latlon lon0:nlon:dlon lat0:nlat:dlat tile grid
# string that is part of the call to wgrib2 in the extract_tiles script
# If you have different values than what is currently in constants_pdef.parm, 
# then uncomment the following lines and replace the values  with 
# the new values. 
# constants_pdef.py
#LON_SUBTR = 15
#LAT_SUBTR = 15
#NLON = 60
#NLAT = 60
#DLAT = 0.5
#DLON = 0.5




