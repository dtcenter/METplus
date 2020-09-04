"""
GridStat: Multiple Config Files Use Case
========================================

met_tool_wrapper/GridStat/GridStat_multiple_config
_files.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare 3 hour forecast precipitation accumulations to observations
# of 3 hour precipitation accumulation. Generate statistics of the results.
# Separate configuration files containing information about the forecast and
# observation data are passed into the METplus wrappers to demonstrate how users
# can create configuration files specific to their data sets to mix and match.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF 3 hour precipitation accumulation
# | **Observation:** MU 3 hour precipitation accumulation
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool GridStat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 12 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf
#
# **GridStat.conf**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf
#
# **GridStat_forecast.conf**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GridStat/GridStat_forecast.conf
#
# **GridStat_observation.conf**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to GRID_STAT_REGRID_TO_GRID in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to GRID_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
# * **${CLIMO_MEAN_FILE}** - Optional path to climatology mean file. Corresponds to GRID_STAT_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${CLIMO_STDEV_FILE}** - Optional path to climatology standard deviation file. Corresponds to GRID_STAT_CLIMO_STDEV_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${NEIGHBORHOOD_SHAPE}** - Shape of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_SHAPE in the METplus configuration file. Default value is 1 if not set.
# * **${NEIGHBORHOOD_WIDTH}** - Width of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_WIDTH in the METplus configuration file. Default value is SQUARE if not set.
# * **${OUTPUT_PREFIX}** - String to prepend to the output filenames. Corresponds to GRID_STAT_OUTPUT_PREFIX in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat.conf, GridStat_forecast.conf, GridStat_observation.conf, an explicit override of the output directory, then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf
#        -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_forecast.conf
#        -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf
#        -c dir.GRID_STAT_OUTPUT_DIR={OUTPUT_BASE}/met_tool_wrapper/GridStat/GridStat_multiple_config
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, passing in GridStat.conf, GridStat_forecast.conf, GridStat_observation.conf, and an explicit override of the output directory::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf
#        -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_forecast.conf
#        -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf
#        -c dir.GRID_STAT_OUTPUT_DIR={OUTPUT_BASE}/met_tool_wrapper/GridStat/GridStat_multiple_config
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
# .. note::
#    The order that the configurations files are supplied on the command line is very important. If the same variables are found in multiple configuration files, then each subsequent configuration file will override the values of the previous files.
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
# Output for this use case will be found in met_tool_wrapper/GridStat/GridStat_multiple_config//2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V_eclv.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V_grad.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#  `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#  `MultiConfUseCase <https://dtcenter.github.io/METplus/search.html?q=MultiConfUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GridStat.png'
