#!/usr/bin/env python

from __future__ import (print_function)
from config_master import ConfigMaster

class Params(ConfigMaster):
  defaultParams = """

import os
import datetime

#
# Set up any environment variables 
# and commonly used directory "bases"
#

# Recently recompiled by John on 11/07, use this
#/d1/CODE/MET/MET_releases/met-5.2/bin/tc_stat
MET_BASE = "/d1/CODE/MET/MET_releases/met-5.2"

OUTPUT_BASE ="/d1/SBU_util/out"
PARM_BASE ="/d1/SBU_util/parm"


#
# Logging
#

#Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "DEBUG"
LOG_DIR = os.path.join(OUTPUT_BASE,"logs")
LOG_FILENAME = os.path.join(LOG_DIR, "master_met_plus." + datetime.datetime.now().strftime("%Y%m%d") + ".log")

#
# Master Script
#

# Processes to run in master script
PROCESS_LIST = ["run_tc_pairs.py", "extract_tiles.py", "series_by_lead.py"]

# Used by extract_tiles.py
# Define the records of interest from the grib2 file
# in the format :field:level:field1:level1:field2:level2:
# for specific level and field
# or :field:field1:field2: for all levels of
# specified fields,
# or :field:level:field1:field2:level2: for a combination of field
# and level.
GRIB2_RECORDS = ":TMP:2 m above|:HGT:500 mb|:PWAT:|:PRMSL:"
OVERWRITE_TRACK = False

#
# Executables
#


# Use this version:/d1/CODE/MET/MET_releases/met-5.2/bin/tc_stat
# it was recompiled by John on 11/07/2016
TC_STAT = os.path.join(MET_BASE, "bin/tc_stat")

WGRIB2 = "/d1/CODE/wgrib2"
SERIES_ANALYSIS = os.path.join(MET_BASE, "bin/series_analysis")
PLOT_DATA_PLANE = os.path.join(MET_BASE, "bin/plot_data_plane")
RM_EXE = "/bin/rm -rf"
CUT_EXE = "/usr/bin/cut"
TR_EXE = "/usr/bin/tr"
NCAP2_EXE = "/usr/local/nco/bin/ncap2"
CONVERT_EXE = "/usr/bin/convert"
TC_PAIRS = os.path.join(MET_BASE, "bin/tc_pairs")
RM_EXE = "/bin/rm -rf"
NCDUMP_EXE = "/usr/local/bin/ncdump"
EGREP_EXE = "/bin/egrep"

#
# Project Directories
#

PROJ_DIR = "/d1/SBU/GFS"
GFS_DIR = os.path.join(PROJ_DIR, "model_data")
TRACK_DATA_DIR = os.path.join(PROJ_DIR, "track_data")
TRACK_DATA_SUBDIR_MOD = os.path.join(PROJ_DIR, "track_data_atcf")
TC_PAIRS_DIR = os.path.join(PROJ_DIR, "tc_pairs")
TC_STAT_DIR = os.path.join(PROJ_DIR,"tc_stat")
TMP_DIR = "/tmp"

#
# Output Directories
# 
OUT_DIR = os.path.join(OUTPUT_BASE,"series_analysis")
# If you wish to keep the filtered tracks in the series analysis directory,
# and then run extract_tiles.py without re-running tc-stat,
# keep the following setting: 
# OVERWRITE_TRACK = False
# 
FILTER_OUT_DIR = OUT_DIR

# Use this setting if you want to separate the filtered track files from
# the series analysis directory.
#FILTER_OUT_DIR = os.path.join(OUTPUT_BASE, "filtered")


# 
# Configuration files required in performing the series analysis
#
CONFIG_FILE_LEAD = os.path.join(PARM_BASE,"SeriesAnalysisConfig_by_lead")
CONFIG_FILE_INIT = os.path.join(PARM_BASE, "SeriesAnalysisConfig")

#
# Lists
#

# Used for performing series analysis both for lead time and init time
VAR_LIST = ["HGT/P500", "PRMSL/Z0", "TMP/Z2", "PWAT/L0"]
STAT_LIST = ["FBAR", "OBAR", "ME", "MAE", "RMSE"]
INIT_LIST = ["20120131_00","20120131_06", "20120131_12", "20141203_06", "20141203_12", "20150126_00", "20150126_06", "20150126_12", "20150126_18", "20150127_00", "20150127_06", "20150127_12", "20150127_18"]
# Dates used for testing  filtering by basin
#INIT_LIST = ["20141203_06", "20141203_12"]

# Used for performing series analysis based on lead time
FHR_BEG = 0
FHR_END = 138 
FHR_INC = 6

#
# Filename templates
#
FCST_TILE_PREFIX = "FCST_TILE_F"
ANLY_TILE_PREFIX = "ANLY_TILE_F"
GFS_FCST_FILE_TMPL = "gfs_4_{init?fmt=%Y%m%d}_{init?fmt=%H}00_{lead?fmt=%HHH}.grb2"
GFS_ANLY_FILE_TMPL = "gfs_4_{valid?fmt=%Y%m%d}_{valid?fmt=%H}00_000.grb2"

#
# Constants used in creating the tile grid
#
NLAT = 60
NLON = 60

# Resolution of data in degrees
DLAT = 0.5
DLON = 0.5

# Degrees to subtract to get center of 30 x 30 grid
LON_SUBTR = 15
LAT_SUBTR = 15

# Regular expressions that are used in series analysis
# Forecast and Analysis tile files, and ASCII files
# created by the series analysis by init and lead time
FCST_TILE_REGEX = ".*FCST_TILE_F.*.grb2"
ANLY_TILE_REGEX = ".*ANLY_TILE_F.*.grb2"

FCST_ASCII_REGEX_INIT ="FCST_ASCII_FILE.*"
ANLY_ASCII_REGEX_INIT ="ANLY_ASCII_FILE.*"
FCST_ASCII_REGEX_LEAD ="FCST_FILE_F.*"
ANLY_ASCII_REGEX_LEAD ="ANLY_FILE_F.*"

#
# For tc pairs
#
TRACK_TYPE = "extra_tropical_cyclone"
TC_PAIRS_CONFIG_PATH = os.path.join(PARM_BASE, "TCPairsETCConfig")
ADECK_FILE_PREFIX = "amlq"
BDECK_FILE_PREFIX = "bmlq"
MISSING_VAL_TO_REPLACE = "-99"
MISSING_VAL = "-9999"
TRACK_DATA_MOD_FORCE_OVERWRITE = False
TC_PAIRS_FORCE_OVERWRITE = False

#
# TC-STAT filtering options
#
EXTRACT_TILES_FILTER_OPTS="  -basin ML -out_init_mask " + os.path.join(MET_BASE,"share/met/poly/CONUS.poly") 
#EXTRACT_TILES_FILTER_OPTS=" -basin ML "
SERIES_ANALYSIS_FILTER_OPTS="-init_beg 20140101 -init_end 20150101"

#
# Testing
#
TEST_DIR = "/tmp/python_test"
TEST_FILENAME="extract_tiles_test.txt"

"""    
 
