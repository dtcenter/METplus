"""
ASCII2NC:Basic Use Case
========================

met_tool_wrapper/ASCII2NC/ASCII2NC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. Simply converting file formats so point observations can be read by the MET tools.

##############################################################################
# Datasets
# --------
#
# | **Observations:** Precipitation accumulation observations in ASCII text files
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ASCII2NC wrapper to generate a command to run the MET tool ASCII2NC if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# ASCII2NC is the only tool called in this example. It processes the following
# run time:
#
# | **Valid:** 2010-01-01_12Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC.conf

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
# Note the following variables are referenced in the MET configuration file. Please see the MET User's Guide section regarding ASCII2NC time summary options for more information.
#
# * **${TIME_SUMMARY_FLAG}** - True/False option to compute time summary statistics. Corresponds to ASCII2NC_TIME_SUMMARY_FLAG in the METplus configuration file.
# * **${TIME_SUMMARY_RAW_DATA}** - Corresponds to ASCII2NC_TIME_SUMMARY_RAW_DATA in the METplus configuration file.
# * **${TIME_SUMMARY_BEG}** - Corresponds to ASCII2NC_TIME_SUMMARY_BEG in the METplus configuration file.
# * **${TIME_SUMMARY_END}** - Corresponds to ASCII2NC_TIME_SUMMARY_END in the METplus configuration file.
# * **${TIME_SUMMARY_STEP}** - Corresponds to ASCII2NC_TIME_SUMMARY_STEP in the METplus configuration file.
# * **${TIME_SUMMARY_WIDTH}** - Corresponds to ASCII2NC_TIME_SUMMARY_WIDTH in the METplus configuration file.
# * **${TIME_SUMMARY_GRIB_CODES}** - Corresponds to ASCII2NC_TIME_SUMMARY_GRIB_CODES in the METplus configuration file.
# * **${TIME_SUMMARY_VAR_NAMES}** - Corresponds to ASCII2NC_TIME_SUMMARY_VAR_NAMES in the METplus configuration file.
# * **${TIME_SUMMARY_TYPES}** - Corresponds to ASCII2NC_TIME_SUMMARY_TYPES in the METplus configuration file.
# * **${TIME_SUMMARY_VALID_FREQ}** - Corresponds to ASCII2NC_TIME_SUMMARY_VALID_FREQ in the METplus configuration file.
# * **${TIME_SUMMARY_VALID_THRESH}** - Corresponds to ASCII2NC_TIME_SUMMARY_VALID_THRESH in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in ASCII2NC.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in ASCII2NC.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC.conf
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
# Output for this use case will be found in ascii2nc (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * precip24_2010010112.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#    `ASCII2NCToolUseCase <https://dtcenter.github.io/METplus/search.html?q=ASCII2NCToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-ASCII2NC.png'
#
