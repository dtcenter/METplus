"""
MODE
========

This use case will run the MET MODE tool to compare gridded forecast data to
gridded observation data.

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
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. Click here to download: https://github.com/NCAR/METplus/releases/download/v2.2/sample_data-met_test-8.1.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

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
# | **Forecast lead:** 12

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/MODE.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/use_cases/met_tool_wrapper/MODE.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/met_config/MODEConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
# * QUILT - True/False to perform quilting. Corresponds to MODE_QUILT in the METplus configuration file.
# * FCST_CONV_RADIUS - Convolution radius used for forecast data. Corresponds to FCST_MODE_CONV_RADIUS in the METplus configuration files.
# * FCST_CONV_THRESH - List of convolution thresholds used for forecast data. Corresponds to FCST_MODE_CONV_THRESH in the METplus configuration files.
# * FCST_MERGE_THRESH - List of merge thresholds used for forecast data. Corresponds to FCST_MODE_MERGE_THRESH in the METplus configuration files.
# * FCST_MERGE_FLAG - True/False merge flag used for forecast data. Corresponds to FCST_MODE_MERGE_FLAG in the METplus configuration files.
# * OBS_CONV_RADIUS - Convolution radius used for observation data. Corresponds to OBS_MODE_CONV_RADIUS in the METplus configuration files.
# * OBS_CONV_THRESH - List of convolution thresholds used for observation data. Corresponds to OBS_MODE_CONV_THRESH in the METplus configuration files.
# * OBS_MERGE_THRESH - List of merge thresholds used for observation data. Corresponds to OBS_MODE_MERGE_THRESH in the METplus configuration files.
# * OBS_MERGE_FLAG - True/False merge flag used for forecast data. Corresponds to OBS_MODE_MERGE_FLAG in the METplus configuration files.
# * The following will be moved to a section that contains variables common to multiple tools (provide link)
# * MODEL
# * OBTYPE
# * FCST_VAR
# * OBS_VAR
# * LEVEL
# * FCST_FIELD
# * OBS_FIELD
# * VERIF_MASK
#
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MODE.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MODE.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MODE.conf
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
# .. note:: MODEUseCase
