"""
Anomoly
=======

This use case will run the MET GridStat and StatAnalysis tools to compare gridded forecast data to gridded observation data over a few valid times and generate statistics over time.

"""
##############################################################################
# Scientific Objective
# --------------------
#
# 

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS
# | **Observation:** GFS
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. Click here to download: https://github.com/NCAR/METplus/releases/download/v3.0/sample_data-medium_range-3.0.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool grid_stat if all required files are found. Then StatAnalysis
# is run on the GridStat output.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat and StatAnalysis are the tools called in this example. It processes the following
# run times:
#
# | **Valid:** 2017-06-13 0Z
# | **Forecast lead:** 24 hour
#
# | **Valid:** 2017-06-13 0Z
# | **Forecast lead:** 48 hour
#
# | **Valid:** 2017-06-13 6Z
# | **Forecast lead:** 24 hour
#
# | **Valid:** 2017-06-13 6Z
# | **Forecast lead:** 48 hour
#
##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/anom.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/anom.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStatConfig_anom
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to GRID_STAT_REGRID_TO_GRID in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to GRID_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
# * **${CLIMO_FILE}** - Optional path to climatology file. Corresponds to CLIMO_GRID_STAT_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${NEIGHBORHOOD_SHAPE}** - Shape of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_SHAPE in the METplus configuration file. Default value is 1 if not set.
# * **${NEIGHBORHOOD_WIDTH}** - Width of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_WIDTH in the METplus configuration file. Default value is SQUARE if not set.
#
# TODO: Add StatAnalysis environment variables

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in anom.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/anom.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in anom.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/anom.conf
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
# Output for this use case will be found in gather_by_date/stat_analysis/grid2grid/anom (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * 00Z/GFS/GFS_20170613.stat
# * 06Z/GFS/GFS_20170613.stat

##############################################################################
# Keywords
# --------
#
# .. note:: `GridStatUseCase <https://ncar.github.io/METplus/search.html?q=GridStatUseCase&check_keywords=yes&area=default>, StatAnalysisUseCase <https://ncar.github.io/METplus/search.html?q=StatAnalysisUseCase&check_keywords=yes&area=default>`_
