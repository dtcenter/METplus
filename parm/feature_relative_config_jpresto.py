
#!/usr/bin/env python


import os
import datetime


#
# Logging
#

#Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR = "/d1/jpresto/my_sbu_wip/logs"
LOG_LEVEL = "DEBUG"
LOG_FILENAME = os.path.join(LOG_DIR, "feature_relative_config_jpresto." + datetime.datetime.now().strftime("%Y%m%d") + ".log")

#
# Output Directories
# 
OUT_DIR = ""

#
# Project Directories
#

PROJ_DIR = "/d1/jpresto/my_sbu_wip/data"
GFS_DIR = os.path.join(PROJ_DIR, "model_data")
TRACK_DATA_DIR = os.path.join(PROJ_DIR, "track_data")
TC_PAIRS_DIR = os.path.join(PROJ_DIR, "tc_pairs")

# For tc pairs
TC_PAIRS_CONFIG_PATH = "/d1/jpresto/my_sbu_wip/parm/TCPairsETCConfig"
