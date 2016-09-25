#!/usr/bin/env pythonzz

from __future__ import (print_function)
from ConfigMaster import ConfigMaster

class Params(ConfigMaster):
  defaultParams = """

import os

#
# Logging
#

#Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "DEBUG"
LOG_DIR = "/d1/SBU_util/out/logs"
LOG_FILENAME = "extract_tiles.log"

#
# Executables
#

TC_STAT = "/d1/CODE/MET/MET_releases/met-5.2_beta2/bin/tc_stat"
WGRIB2 = "/d1/CODE/wgrib2"
SERIES_ANALYSIS = "/d1/CODE/MET/MET_releases/met-5.2_beta2/bin/series_analysis"
PLOT_DATA_PLANE = "/d1/CODE/MET/MET_releases/met-5.2_beta2/bin/plot_data_plane"
RM_EXE = "/bin/rm -rf"
CUT_EXE = "/usr/bin/cut"
TR_EXE = "/usr/bin/tr"
NCAP2_EXE = "/usr/local/nco/bin/ncap2"
CONVERT_EXE = "/usr/bin/convert"
TC_PAIRS = "/d1/CODE/MET/MET_releases/met-5.2_beta2/bin/tc_pairs"
RM_EXE = "/bin/rm -rf"
NCDUMP_EXE = "/usr/local/bin/ncdump"

#
# Project Directories
#

PROJ_DIR = "/d1/SBU/GFS"
GFS_DIR = os.path.join(PROJ_DIR, "model_data")
TRACK_DATA_DIR = os.path.join(PROJ_DIR, "track_data")
TC_PAIRS_DIR = os.path.join(PROJ_DIR, "tc_pairs")

#
# Output Directories
# 
OUT_DIR = "/d1/SBU_util/out/series_analysis"

# 
# Configuration files required in performing the series analysis
#
CONFIG_FILE_LEAD = "/d1/SBU_util/parm/SeriesAnalysisConfig_by_lead"
CONFIG_FILE_INIT = "/d1/SBU_util/parm/SeriesAnalysisConfig"

#
# Lists
#

# Used for performing series analysis both for lead time and init time
VAR_LIST = ["HGT/P500", "PRMSL/Z0", "TMP/Z2", "PWAT/L0"]
STAT_LIST = ["FBAR", "OBAR", "ME", "MAE", "RMSE"]
INIT_LIST = ["20150126_00", "20150126_06", "20150126_12", "20150126_18", "20150127_00", "20150127_06", "20150127_12", "20150127_18"]

# Used for performing series analysis based on lead time
FHR_BEG = 0
FHR_END = 138 
FHR_INC = 6

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

# For tc pairs
TRACK_TYPE = "extra_tropical_cyclone"
TC_PAIRS_CONFIG_PATH = "TCPairsETCConfig"
ADECK_FILE_PREFIX = "amlq"
BDECK_FILE_PREFIX = "bmlq"
TRACK_DATA_SUBDIR_MOD = "track_data_atcf"
MISSING_VAL_TO_REPLACE = "-99"
MISSING_VAL = "-9999"

#
# Testing
#
TEST_DIR = "/tmp/python_test"
TEST_FILENAME="extract_tiles_test.txt"

"""    
 
