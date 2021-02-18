"""
UserScript: Calculate the Difficulty Index
========================================================================

model_applications/medium_range/
UserScript_fcstGEFS
_Difficulty_Index.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# This use case calls the UserScript wrapper to run a user provided script that calculates 
# the difficulty index for windspeed. This use case allows for the user to change a variety 
# of variables needed to run the difficulty index (i.e. threshold start and units) so that
# user can run the script at different thresholds without needing to alter the code. This 
# script run by the use case uses METcalcpy to provide the difficulty index calculation and
# METplotpy to provide the plotting capability. 
#
# The difficulty index was developed by the Naval Research Lab (NRL). The overall aim of the
# difficulty index is to graphically represent the expected difficulty of a decision based on 
# a set of forecasts (ensemble) of, e.g., significant wave height as a function of space and 
# time. There are two basic factors that can make a decision difficult. The first factor is the 
# proximity of the ensemble mean forecast to a decision threshold, e.g. 12 ft seas. If the 
# ensemble mean is either much lower or much higher than the threshold, the decision is easier; 
# if it is closer to the threshold, the decision is harder. The second factor is the forecast 
# precision, or ensemble spread. The greater the spread around the ensemble mean, the more likely 
# it is that there will be ensemble members both above and below the decision threshold, making 
# the decision harder. (A third factor that we will not address here is undiagnosed systematic 
# error, which adds uncertainty in a similar way to ensemble spread.) The challenge is combining 
# these factors into a continuous function that allows the user to assess relative risk. 

##############################################################################
# Datasets
# --------
#
# This use case calculates the difficulty index for windspeed using NCEP 
# GEFS ensemble data. The data is composed of 30 ensemble members that 
# have been compiled and compressed into one .npz file. 
# 
#  - Variables required to calculate the difficulty index:
#    Levels required: 10-m
#    #. v- component of wind
#    #. u- component of wind
#    #. Windspeed
#    #. Latitude
#    #. Longitude
#  - Forecast dataset: NCEP GEFS 30 member Ensemble
#    - Initialization date: 20191208
#    - Initialization hours: 12 UTC
#    - Lead times: 60
#    - Format: Grib2
#    - Resolution: 0.5 degree
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, wind_difficulty_index.py.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case loops by process which means that each tool is run for all times before moving to the
# next tool. The tool order is as follows:
# 
# UserScript
#
# This example loops by initialization time (with begin, end, and increment as specified in the 
# METplus UserScript_fcstGEFS_Difficulty_Index.conf file). 
#
# 1 initialization time will be run over 1 lead time:
#
# | **Init:** 20201208_12Z
# | **Forecast lead:** 60
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# There are no MET tools used in this use case.
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read input data
#
# parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index/wind_difficulty_index.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index/wind_difficulty_index.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstGEFS_Difficulty_Index.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.conf \
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGEFS_Difficulty_Index.conf::
#
#        run_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  If the executable is in the user's path, METplus will find it from the name. 
#  If the executable is not in the path, specify the full path to the executable here (i.e. RM = /bin/rm)  
#  The following executables are required for performing series analysis use cases:
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
#   [exe]
#   RM = /path/to/rm
#   CUT = /path/to/cut
#   TR = /path/to/tr
#   NCAP2 = /path/to/ncap2
#   CONVERT = /path/to/convert
#   NCDUMP = /path/to/ncdump
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in a directory relative to **OUTPUT_BASE**. There
# should be a list of files that have the following format:
#
# wndspd_GEFS_NorthPac_5dy_30mem_difficulty_indexTHRESH_00_kn.png
# 
# Where THRESH isa number between DIFF_INDEX_SAVE_THRESH_START and 
# DIFF_INDEX_SAVE_THRESH_STOP which are defined in UserScript_fcstGEFS_Difficulty_Index.conf.
# 

##############################################################################
# Keywords
# --------
#
# .. note::
#  `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_,
#  `MediumRangeAppUseCase <https://dtcenter.github.io/METplus/search.html?q=MediumRangeAppUseCase&check_keywords=yes&area=default>`_,
#  `NRLOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NRLOrgUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-UserScript_fcstGEFS_Difficulty_Index.png'
