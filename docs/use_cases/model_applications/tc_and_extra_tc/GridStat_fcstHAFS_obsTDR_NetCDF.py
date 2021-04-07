"""
Grid-Stat: Verification of TC forecasts against merged TDR data 
==============================================================================

model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR
_NetCDF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between merged 
# Tail Doppler Radar (TDR) data in NetCDF format to a gridded forecast. These 
# values can be used to assess the skill of the prediction. The TDR data is 
# available every 0.5 km AGL. So, the TC forecasts need to be in height coordinates
# to compare with the TDR data. 

##############################################################################
# Datasets
# --------
#
# | **Forecast:** HAFS zonal wind
# | **Observation:** HRD TDR data 
#
# | **Location of Model forecast and Dropsonde files:** All of the input data required for this use case can be found in the sample data tarball. Click `here <https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data>`_ to download.
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **TDR Data Source:** `Hurricane Research Division:  https://seb.noaa.gov/pub/flight/hrd/radar/20190829H1/ `_
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ASCII2NC wrapper to convert full-resolution data (frd) dopsonde point observations to NetCDF format and then compare them to gridded forecast data using PointStat.


##############################################################################
# METplus Workflow
# ----------------
#
# The use case runs the python embedding scripts (GridStat_fcstHAFS_obsTDR_NetCDF/read_tdr.py: to read the TDR data) and run Grid-Stat (compute statistics against HAFS model output, in height coordinates), called in this example. It processes the following run times:
#
# | **Valid:** 2019-08-29 12Z
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications//tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstHAFS_obsTDR_NetCDF.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.conf
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

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in nam (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_180000L_20190829_120000V.stat

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.png'
#
# .. note:: `TCandExtraTCAppUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=TCandExtraTCAppUseCase&check_keywords=yes&area=default>`_, `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_
