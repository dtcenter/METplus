"""
CyclonePlotter
==============

Generates a plot of cyclone tracks.  No MET tool is invoked for this example.

"""

##############################################################################
# Scientific Objective
# --------------------
#
#
# Provide visualization of cyclone tracks on a global map (PlateCaree projection)

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF 3 hour precipitation accumulation
# | **Observation:** MU 3 hour precipitation accumulation
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. Click here to download: https://github.com/NCAR/METplus/releases/download/v2.2/sample_data-met_test-8.1.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case does not utilize any MET tools

##############################################################################
# METplus Workflow
# ----------------
#
# CyclonePlotter is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2015-03-01_0Z


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GridStat.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/use_cases/met_tool_wrapper/GridStat.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/use_cases/met_tool_wrapper/GridStat.met
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from FCST_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from OBS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${CLIMO_FILE}** - Optional path to climatology file. Corresponds to CLIMO_GRID_STAT_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${FCST_VAR}** - Field name of forecast data to process. Used in output_prefix to include input information in the output filenames. Corresponds to FCST_VAR<n>_NAME in the METplus configuration file.
# * **${OBS_VAR}** - Field name of observation data to process. Used in output_prefix to include input information in the output filenames. Corresponds to OBS_VAR<n>_NAME in the METplus configuration file.
# * **${LEVEL}** - Vertical level of the forecast input data. Used in output_prefix to include input information in the output filenames. Corresponds to FCST_VAR<n>_LEVELS in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to GRID_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
# * **${NEIGHBORHOOD_SHAPE}** - Shape of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_SHAPE in the METplus configuration file. Default value is 1 if not set.
# * **${NEIGHBORHOOD_WIDTH}** - Width of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_WIDTH in the METplus configuration file. Default value is SQUARE if not set.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run as follows:
#
# 1) Passing in CyclonePlotter.conf then a user-specific system configuration file and user-specific data
#    configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/CyclonePlotter.conf
#                          -c /path/to/user_system.conf
#                          -c /path/to/user_data.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in CyclonePlotter.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/CyclonePlotter.conf
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
# Output for this use case will be found in grid_stat/2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V_eclv.txt
# * grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V_grad.txt
# * grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note:: GridStatUseCase

