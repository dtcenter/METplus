"""
TCRMW: Hurricane Gonzalo
========================

model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly
_gonzolo.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# The TC-RMW tool regrids tropical cyclone model data onto a moving range-azimuth grid centered on points along the storm track. This capability replicates the NOAA Hurricane Research Division DIA-Post module.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS GRIB2
# | **Track:** A Deck
#
# | **Location:** All of the input data required for this use case can be found in the tc_and_extra_tc sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCRMW wrapper to search for
# the desired ADECK file and forecast files that are correspond to the track.
# It generates a command to run the MET tool TC-RMW if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# TCRMW is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2014-10-13 12Z
# | **Forecast lead:** 0, 6, 12, 18, and 24 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly_gonzalo.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly_gonzalo.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCRMWConfig_wrapped
#
# See the Python Wrapper section of the User's Guide for more information on the environment variables set in this file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in the use case configuration file then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly_gonzalo.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in use case configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly_gonzalo.conf
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
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in model_applications/tc_and_extra_tc/TCRMW_gonzalo (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * tc_rmw_aal142016.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#   `TCRMWToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCRMWToolUseCase&check_keywords=yes&area=default>`_
#   `GRIB2FileUseCase  <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_
#

