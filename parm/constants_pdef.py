#!/usr/bin/env python

from __future__ import (print_function)
from config_master import ConfigMaster

class Params(ConfigMaster):
  defaultParams = """

import os
import datetime

#
#    NON-MET EXECUTABLES 
#

WGRIB2 = "/d1/CODE/wgrib2"
RM_EXE = "/bin/rm -rf"
CUT_EXE = "/usr/bin/cut"
TR_EXE = "/usr/bin/tr"
NCAP2_EXE = "/usr/local/nco/bin/ncap2"
CONVERT_EXE = "/usr/bin/convert"
RM_EXE = "/bin/rm -rf"
NCDUMP_EXE = "/usr/local/bin/ncdump"
EGREP_EXE = "/bin/egrep"

#
#    COMMONLY USED BASE VARIABLES
#

MET_BUILD_BASE = "/d1/CODE/MET/MET_releases/met-5.2"
MET_BASE = os.path.join(MET_BUILD_BASE, "share/met/")
os.environ["MET_BASE"] = MET_BASE

OUTPUT_BASE ="/d1/SBU_util/out"
PARM_BASE ="/d1/SBU_util/parm"

#
#    OUTPUT DIRECTORIES (uses previously set variables)
#

LOG_DIR = os.path.join(OUTPUT_BASE,"logs")
OUT_DIR = os.path.join(OUTPUT_BASE,"series_analysis")
TMP_DIR = "/tmp"

#
#     Use this setting to separate the filtered track files from
#     the series analysis directory.
#

EXTRACT_OUT_DIR = os.path.join(OUTPUT_BASE, "extract_tiles")
SERIES_LEAD_FILTERED_OUT_DIR = os.path.join(OUTPUT_BASE, "series_lead_filtered")
SERIES_INIT_FILTERED_OUT_DIR = os.path.join(OUTPUT_BASE, "series_init_filtered")

#
#     Define the output directories for Series analysis by lead and init
#

SERIES_LEAD_OUT_DIR=os.path.join(OUTPUT_BASE, "series_analysis_lead")
SERIES_INIT_OUT_DIR=os.path.join(OUTPUT_BASE, "series_analysis_init")

#
#     MET EXECUTABLES (uses previously set variables)
#

TC_STAT = os.path.join(MET_BUILD_BASE, "bin/tc_stat")
SERIES_ANALYSIS = os.path.join(MET_BUILD_BASE, "bin/series_analysis")
PLOT_DATA_PLANE = os.path.join(MET_BUILD_BASE, "bin/plot_data_plane")
TC_PAIRS = os.path.join(MET_BUILD_BASE, "bin/tc_pairs")
REGRID_DATA_PLANE_EXE = os.path.join(MET_BUILD_BASE, "bin/regrid_data_plane")

#
#     PROJECT DATA DIRECTORIES (uses previously set variables)
#

PROJ_DIR = "/d1/SBU/GFS"
GFS_DIR = os.path.join(PROJ_DIR, "model_data")
TRACK_DATA_DIR = os.path.join(PROJ_DIR, "track_data")
TRACK_DATA_SUBDIR_MOD = os.path.join(PROJ_DIR, "track_data_atcf")
TC_PAIRS_DIR = os.path.join(PROJ_DIR, "tc_pairs")
TC_STAT_DIR = os.path.join(PROJ_DIR,"tc_stat")

#
#     CONFIGURATION FILES (uses previously set variables)
#

TC_PAIRS_CONFIG_PATH = os.path.join(PARM_BASE, "TCPairsETCConfig")

# 
#     Configuration files required in performing the series analysis
#
CONFIG_FILE_LEAD = os.path.join(PARM_BASE,"SeriesAnalysisConfig_by_lead")
CONFIG_FILE_INIT = os.path.join(PARM_BASE, "SeriesAnalysisConfig")

#
#     LOGGING
#

#
#     Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
#

LOG_LEVEL = "DEBUG"
LOG_FILENAME = os.path.join(LOG_DIR, "master_met_plus." + datetime.datetime.now().strftime("%Y%m%d") + ".log")

#
#     FILENAME TEMPLATES
#

FCST_TILE_PREFIX = "FCST_TILE_F"
ANLY_TILE_PREFIX = "ANLY_TILE_F"
GFS_FCST_FILE_TMPL = "gfs_4_{init?fmt=%Y%m%d}_{init?fmt=%H}00_{lead?fmt=%HHH}.grb2"
GFS_FCST_NC_FILE_TMPL = "gfs_4_{init?fmt=%Y%m%d}_{init?fmt=%H}00_{lead?fmt=%HHH}.nc"
GFS_ANLY_FILE_TMPL = "gfs_4_{valid?fmt=%Y%m%d}_{valid?fmt=%H}00_000.grb2"
GFS_ANLY_NC_FILE_TMPL = "gfs_4_{valid?fmt=%Y%m%d}_{valid?fmt=%H}00_000.nc"

#
#     LISTS AND SETTINGS
#

#
#     Processes to run in master script (master_met_plus.py)
#

PROCESS_LIST = ["run_tc_pairs.py", "extract_tiles.py"]


STAT_LIST = ["FBAR", "OBAR", "ME", "MAE", "RMSE"]
INIT_LIST = ["20141203_06", "20141203_12", "20150126_00", "20150126_06", "20150126_12", "20150126_18", "20150127_00", "20150127_06", "20150127_12", "20150127_18"]

#
#     Used by extract_tiles.py to define the records of interest from the grib2 file
#

VAR_LIST = ["HGT/P500", "PRMSL/Z0", "TMP/Z2"]
EXTRACT_TILES_VAR_LIST = ["PWAT/L0"]

#
#     Used for performing series analysis based on lead time
#

FHR_BEG = 0
FHR_END = 138 
FHR_INC = 6

#
#     Constants used in creating the tile grid
#

NLAT = 60
NLON = 60

#
#     Resolution of data in degrees
#

DLAT = 0.5
DLON = 0.5

#
#     Degrees to subtract from the center lat and lon to 
#     calculate the lower left lat (lat_ll) and lower
#     left lon (lon_ll) for a grid that is 2n X 2m, 
#     where n = LAT_ADJ degrees and m = LON_ADJ degrees.
#     For this case, where n=15 and m=15, this results
#     in a 30 deg X 30 deg grid.
#

LON_ADJ = 15
LAT_ADJ = 15

#
#     Regular expressions that are used in series analysis
#     Forecast and Analysis tile files, and ASCII files
#     created by the series analysis by init and lead time
#

FCST_TILE_REGEX = ".*FCST_TILE_F.*.grb2"
ANLY_TILE_REGEX = ".*ANLY_TILE_F.*.grb2"

FCST_ASCII_REGEX_INIT ="FCST_ASCII_FILE.*"
ANLY_ASCII_REGEX_INIT ="ANLY_ASCII_FILE.*"
FCST_ASCII_REGEX_LEAD ="FCST_FILE_F.*"
ANLY_ASCII_REGEX_LEAD ="ANLY_FILE_F.*"



#
#     TC PAIRS filtering options
#

TRACK_TYPE = "extra_tropical_cyclone"
ADECK_FILE_PREFIX = "amlq"
BDECK_FILE_PREFIX = "bmlq"
MISSING_VAL_TO_REPLACE = "-99"
MISSING_VAL = "-9999"

#
#     TC-STAT filtering options
#

EXTRACT_TILES_FILTER_OPTS="-basin ML"
SERIES_ANALYSIS_FILTER_OPTS="-init_beg 20140101 -init_end 20141231"


#
#     OVERWRITE OPTIONS
#

#
#     Don't overwrite filter files if they already exist.
#

OVERWRITE_TRACK = False 
TRACK_DATA_MOD_FORCE_OVERWRITE = False
TC_PAIRS_FORCE_OVERWRITE = False

#
#     PLOTTING
#

#
#     By default, background map is turned off. Set 
#     to False to turn of plotting of background map.
#

BACKGROUND_MAP = False


#
#     TESTING
#

TEST_DIR = "/tmp/python_test"
TEST_FILENAME="extract_tiles_test.txt"

"""    
 
