"""
MODE: Basic Use Case
====================

met_tool_wrapper/MODE/MODE.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare relative humidity 12 hour forecast to 0 hour observations.
# Generate statistics of the results.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF Relative Humidity
# | **Observation:** WRF Relative Humidity
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus MODE wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool mode if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# MODE is the only tool called in this example. It processes the following
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
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/MODE/MODE.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/MODE/MODE.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **QUILT** - True/False to perform quilting. Corresponds to MODE_QUILT in the METplus configuration file.
# * **${FCST_CONV_RADIUS}** - Convolution radius used for forecast data. Corresponds to FCST_MODE_CONV_RADIUS in the METplus configuration files.
# * **${FCST_CONV_THRESH}** - List of convolution thresholds used for forecast data. Corresponds to FCST_MODE_CONV_THRESH in the METplus configuration files.
# * **${FCST_MERGE_THRESH}** - List of merge thresholds used for forecast data. Corresponds to FCST_MODE_MERGE_THRESH in the METplus configuration files.
# * **${FCST_MERGE_FLAG}** - True/False merge flag used for forecast data. Corresponds to FCST_MODE_MERGE_FLAG in the METplus configuration files.
# * **${OBS_CONV_RADIUS}** - Convolution radius used for observation data. Corresponds to OBS_MODE_CONV_RADIUS in the METplus configuration files.
# * **${OBS_CONV_THRESH}** - List of convolution thresholds used for observation data. Corresponds to OBS_MODE_CONV_THRESH in the METplus configuration files.
# * **${OBS_MERGE_THRESH}** - List of merge thresholds used for observation data. Corresponds to OBS_MODE_MERGE_THRESH in the METplus configuration files.
# * **${OBS_MERGE_FLAG}** - True/False merge flag used for forecast data. Corresponds to OBS_MODE_MERGE_FLAG in the METplus configuration files.
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from FCST_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from OBS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to MODE_REGRID_TO_GRID in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to GRID_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
# * **${OUTPUT_PREFIX}** - String to prepend to the output filenames. Corresponds to MODE_OUTPUT_PREFIX in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MODE.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MODE/MODE.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MODE/MODE.conf
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
# Output for this use case will be found in mode/2005080712 (relative to **OUTPUT_BASE**)
# and will contain the following files:

# * mode_WRF_RH_vs_WRF_RH_P500_120000L_20050807_120000V_000000A_cts.txt
# * mode_WRF_RH_vs_WRF_RH_P500_120000L_20050807_120000V_000000A_obj.nc
# * mode_WRF_RH_vs_WRF_RH_P500_120000L_20050807_120000V_000000A_obj.txt
# * mode_WRF_RH_vs_WRF_RH_P500_120000L_20050807_120000V_000000A.ps


##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-MODE.png'
#
# .. note:: `MODEToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_, `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
