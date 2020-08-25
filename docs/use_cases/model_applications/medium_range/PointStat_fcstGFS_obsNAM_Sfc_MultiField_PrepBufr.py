"""
Point-Stat: Standard Verification for CONUS Surface 
==============================================================================

model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc
_MultiField_PrepBufr.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between observation data
# in point format to a gridded forecast. These values can be used to assess the skill 
# of the prediction. Statistics are store as partial sums to save space and Stat-Analysis
# must be used to compute Continuous statistics.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS temperature, u-wind component, v-wind component, and height
# | **Observation:** NAM prepBURF data
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. Click here to download: https://github.com/dtcenter/METplus/releases/download/v3.0/sample_data-medium_range-3.0.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PB2NC wrapper to convert PrepBUFR point observations to NetCDF format and then compare them to gridded forecast data using PointStat.


##############################################################################
# METplus Workflow
# ----------------
#
# PB2NC and PointStat are the tools called in this example. It processes the following run times:
#
# | **Valid:** 2017-06-01 0Z
#
# | **Valid:** 2017-06-02 0Z
#
# | **Valid:** 2017-06-03 0Z
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PB2NCConfig_wrapped
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# PB2NC:
#
# * **${PB2NC_MESSAGE_TYPE}** - Corresponds to PB2NC_MESSAGE_TYPE in the METplus configuration file.
# * **${PB2NC_STATION_ID}** - Corresponds to PB2NC_STATION_ID in the METplus configuration file.
# * **${PB2NC_GRID}** - Corresponds to PB2NC_GRID in the METplus configuration file.
# * **${PB2NC_POLY}** - Corresponds to PB2NC_POLY in the METplus configuration file.
# * **${OBS_WINDOW_BEGIN}** - Corresponds to OBS_WINDOW_BEGIN or PB2NC_WINDOW_BEGIN in the METplus configuration file.
# * **${OBS_WINDOW_END}** - Corresponds to OBS_WINDOW_END or PB2NC_WINDOW_END in the METplus configuration file.
# * **${OBS_BUFR_VAR_LIST}** - Corresponds to PB2NC_OBS_BUFR_VAR_LIST in the METplus configuration file.
# * **${TIME_SUMMARY_FLAG}** - True/False option to compute time summary statistics. Corresponds to PB2NC_TIME_SUMMARY_FLAG in the METplus configuration file.
# * **${TIME_SUMMARY_BEG}** - Corresponds to PB2NC_TIME_SUMMARY_BEG in the METplus configuration file.
# * **${TIME_SUMMARY_END}** - Corresponds to PB2NC_TIME_SUMMARY_END in the METplus configuration file.
# * **${TIME_SUMMARY_VAR_NAMES}** - Corresponds to PB2NC_TIME_SUMMARY_VAR_NAMES in the METplus configuration file.
# * **${TIME_SUMMARY_TYPES}** - Corresponds to PB2NC_TIME_SUMMARY_TYPES in the METplus configuration file.
#
# PointStat:
#
# * **${POINT_STAT_MESSAGE_TYPE}** - Corresponds to POINT_STAT_MESSAGE_TYPE in the METplus configuration file.
# * **${POINT_STAT_STATION_ID}** - Corresponds to POINT_STAT_STATION_ID in the METplus configuration file.
# * **${POINT_STAT_GRID}** - Corresponds to POINT_STAT_GRID in the METplus configuration file.
# * **${POINT_STAT_POLY}** - Corresponds to POINT_STAT_POLY in the METplus configuration file.
# * **${OBS_WINDOW_BEGIN}** - Corresponds to OBS_WINDOW_BEGIN or OBS_POINT_STAT_WINDOW_BEGIN in the METplus configuration file.
# * **${OBS_WINDOW_END}** - Corresponds to OBS_WINDOW_END or OBS_POINT_STAT_WINDOW_END in the METplus configuration file.
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to POINT_STAT_REGRID_TO_GRID in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to POINT_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf
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
# * point_stat_000000L_20170601_000000V.stat
# * point_stat_000000L_20170602_000000V.stat
# * point_stat_000000L_20170603_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.png'
#
# .. note:: `PB2NCToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PB2NCToolUseCase&check_keywords=yes&area=default>`_, `MediumRangeAppUseCase <https://dtcenter.github.io/METplus/search.html?q=MediumRangeAppUseCase&check_keywords=yes&area=default>`_, `PointStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PointStatToolUseCase&check_keywords=yes&area=default>`_, `GRIBFileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIBFileUseCase&check_keywords=yes&area=default>`_, `prepBUFRFileUseCase <https://dtcenter.github.io/METplus/search.html?q=prepBUFRFileUseCase&check_keywords=yes&area=default>`_, `NOAAEMCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NOAAEMCOrgUseCase&check_keywords=yes&area=default>`_, `RegriddinginToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegriddingInToolUseCase&check_keywords=yes&area=default>`_  , `ObsTimeSummaryUseCase <https://dtcenter.github.io/METplus/search.html?q=ObsTimeSummaryUseCase&check_keywords=yes&area=default>`_
