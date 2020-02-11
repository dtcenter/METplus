"""
GFS to CCPA GRIB Use Case
===============================
This use case compares gridded forecast precipitation accumulation data to
gridded 24 hour observation precipitation accumulation data.
"""
##############################################################################
# Scientific Objective
# --------------------
#
# To provide useful statistical information on the relationship between observation
# data in gridded format to a gridded forecast. These values can be used to help correct
# model deviations from observed values.

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
# 
#  * Forecast dataset: GFS
#  * Observation dataset: Climatologically Calibrated Precipitation Analysis (CCPA)
#  * Sources of data (links, contacts, etc...)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the observation data to build a 24
# hour precipitation accumulation file.
# Then the observation data are compared to the forecast data using GridStat.


##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#  PCPCombine (observation) > GridStat
#
# This example loops by valid time. There is only one
#  initialization time in this example, so the following will be run:
#
# Run times:
#
# | **Init:** 2017-06-13_00Z
# | **Forecast lead:** 24
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStatConfig_precip
#
# See the following files for more information about the environment variables set in this configuration file.
#   parm/use_cases/met_tool_wrapper/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstGFS_obsCCPA_GRIB.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstGFS_obsCCPA_GRIB::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#

#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB/grid_stat/20170613 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
#

##############################################################################
# Keywords
# --------
#
# .. note:: GridStatUseCase, PrecipitationUseCase, PCPCombineUseCase
