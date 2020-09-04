"""
TCPairs: Basic Use Case for Tropical Cyclones
==========================================================================

met_tool_wrapper/TCPairs/TCPairs_tropical.conf

"""
###########################################
# Scientific Objective
# --------------------
#
# Once this method is complete, a forecast and reference track analysis file
# will have been paired up, allowing statistical information to be extracted.

##############################################################################
# Datasets
# --------
#
#
# | **Forecast:** A Deck 
# |     /path/to/hwrf/adeck
# | **Observation:** Best Track - B Deck
# |     /path/to/hwrf/bdeck
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** HWRF

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCPairs wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool tc_pairs.

##############################################################################
# METplus Workflow
# ----------------
#
# TCPairs is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2018-08-30_06Z, 2018-08-30_12Z, 2018-08-30_18Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c /path/to/TCPairs_tropical.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/TCPairs/TCPairs_tropical.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCPairsConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Corresponds to MODEL in the METplus configuration file.
# * **${STORM_ID}** - Corresponds to TC_PAIRS_STORM_ID in the METplus configuration file.
# * **${BASIN}** - Corresponds to TC_PAIRS_BASIN in the METplus configuration file.
# * **${CYCLONE}** - Corresponds to TC_PAIRS_CYCLONE in the METplus configuration file.
# * **${STORM_NAME}** - Corresponds to TC_PAIRS_STORM_NAME in the METplus configuration file.
# * **${INIT_BEG}** -  Corresponds to INIT_BEG in the METplus configuration file. 
# * **${INIT_END** - Corresponds to INIT_END in the METplus configuration file. 
# * **${INIT_INCLUDE}** - Corresponds to INIT_INCLUDE in the METplus configuration file.
# * **${INIT_EXCLUDE}** - Corresponds to INIT_EXCLUDE in the METplus configuration file.
# * **${VALID_BEG}** - Corresponds to VALID_BEG in the METplus configuration file.
# * **${VALID_END}** - Corresponds to VALID_END in the METplus configuration file.
# * **${DLAND_FILE}** - Corresponds to TC_PAIRS_DLAND_FILE in the METplus configuration file.

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in TCPairs_tropical.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/TCPairs_tropical.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCPairs_tropical.conf::
#        master_metplus.py -c /path/to/TCPairs_tropical.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs).
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
# Output for this use case will be found in tc_pairs
# and will contain the following files:
#
# * tc_pairs_al2018083006.dat.tcst
# * tc_pairs_al2018083012.dat.tcst
# * tc_pairs_al2018083018.dat.tcst

##############################################################################
# Keywords
# --------
#
# .. note::
#  `TCPairsToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCPairsToolUseCase&check_keywords=yes&area=default>`_,
#  `DTCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=DTCOrgUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-TCPairs.png'
