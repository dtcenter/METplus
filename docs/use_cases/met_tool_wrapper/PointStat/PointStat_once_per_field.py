"""
PointStat: Once Per Field
=============================================================================

met_tool_wrapper/PointStat/PointStat_once_per_field.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare 3 hour forecast precipitation accumulations to observations
# of 3 hour precipitation accumulation. Generate statistics of the results.
#

##############################################################################
# Datasets
# --------
#
# | **Forecast:** NAM temperature, u-wind component, and v-wind component
# | **Observation:** prepBURF data that has been converted to NetCDF format via PB2NC
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PointStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool point_stat if all required files are found.
# This use case processes each field name/level separately to generate
# output files for each. POINT_STAT_OUTPUT_PREFIX is used to control
# the names of the output fields, referencing {CURRENT_FCST_NAME} and
# {CURRENT_FCST_LEVEL} to get information for each field.
#

##############################################################################
# METplus Workflow
# ----------------
#
# PointStat is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2007-03-30_0Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/PointStat/PointStat_once_per_field.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PointStat/PointStat_once_per_field.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
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
# * **${CLIMO_MEAN_FILE}** - Optional path to climatology mean file. Corresponds to POINT_STAT_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${CLIMO_STDEV_FILE}** - Optional path to climatology standard deviation file. Corresponds to POINT_STAT_CLIMO_STDEV_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${OUTPUT_PREFIX}** - String to prepend to the output filenames. Corresponds to POINT_STAT_OUTPUT_PREFIX in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PointStat.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PointStat/PointStat_once_per_field.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PointStat_once_per_field.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PointStat/PointStat_once_per_field.conf
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
# Output for this use case will be found in point_stat (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_TMP_P750-900_360000L_20070331_120000V.stat
# * point_stat_UGRD_Z10_360000L_20070331_120000V.stat
# * point_stat_VGRD_Z10_360000L_20070331_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#  `PointStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PointStatToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PointStat.png'
