"""
PB2NC: Basic Use Case
=====================

met_tool_wrapper/PB2NC/PB2NC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Simply converting file formats so point observations can be read by the MET tools.

##############################################################################
# Datasets
# --------
#
# | **Observations:** Various fields in prepBUFR file
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PB2NC wrapper to generate a command to run the MET tool PB2NC if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PB2NC is the only tool called in this example. It processes the following
# run time:
#
# | **Valid:** 2007-03-31_12Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PB2NCConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file. Please see the MET User's Guide section regarding PB2NC options for more information.
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

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PB2NC.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PB2NC.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf
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
# Output for this use case will be found in pb2nc (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * sample_pb.nc

##############################################################################
# Keywords
# --------
#
# .. note:: `PB2NCToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PB2NCToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PB2NC.png'
