"""
TCGen: Basic Use Case
==========================================================================

met_tool_wrapper/TCGen/TCGen.conf

"""
###########################################
# Scientific Objective
# --------------------
#
# The TC-Gen tool provides verification of tropical cyclone genesis forecasts in ATCF file format.
#

##############################################################################
# Datasets
# --------
#
#
# | **Track:** A Deck or B Deck (Best)
# | **Genesis:** Genesis Forecast
#
# | **Location:** All of the input data required for this use case can be found in the met_tool_wrapper sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCGen wrapper to search for
# files that match wildcard expressions and generate a command to run
# the MET tool tc_gen.

##############################################################################
# METplus Workflow
# ----------------
#
# TCGen is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2016

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c /path/to/TCGen.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/TCGen/TCGen.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCGenConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${INIT_FREQ}** - Corresponds to TC_GEN_INIT_FREQUENCY in the METplus configuration file.
# * **${LEAD_WINDOW_DICT}** - Corresponds to TC_GEN_LEAD_WINDOW_[BEGIN/END] in the METplus configuration file.
# * **${MIN_DURATION}** - Corresponds to TC_GEN_MIN_DURATION in the METplus configuration file.
# * **${FCST_GENESIS_DICT}** - Corresponds to TC_GEN_FCST_GENESIS_[VMAX_THRESH/MSLP_THRESH] in the METplus configuration file.
# * **${BEST_GENESIS_DICT}** - Corresponds to TC_GEN_FCST_GENESIS_[TECHNIQUE/CATEGORY/VMAX_THRESH/MSLP_THRESH] in the METplus configuration file.
# * **${OPER_GENESIS_DICT}** - Corresponds to TC_GEN_OPER_GENESIS_[TECHNIQUE/CATEGORY/VMAX_THRESH/MSLP_THRESH] in the METplus configuration file.
# * **${FILTER}** - Corresponds to TC_GEN_FILTER_<n> in the METplus configuration file.
# * **${MODEL}** - Corresponds to MODEL in the METplus configuration file.
# * **${STORM_ID}** - Corresponds to TC_GEN_STORM_ID in the METplus configuration file.
# * **${STORM_NAME}** - Corresponds to TC_GEN_STORM_NAME in the METplus configuration file.
# * **${INIT_BEG}** -  Corresponds to TC_GEN_INIT_BEG in the METplus configuration file.
# * **${INIT_END** - Corresponds to TC_GEN_INIT_END in the METplus configuration file.
# * **${VALID_BEG}** -  Corresponds to TC_GEN_VALID_BEG in the METplus configuration file.
# * **${VALID_END** - Corresponds to TC_GEN_VALID_END in the METplus configuration file.
# * **${INIT_HOUR_LIST}** - Corresponds to TC_GEN_INIT_HOUR_LIST in the METplus configuration file.
# * **${LEAD_LIST}** - Corresponds to LEAD_SEQ in the METplus configuration file.
# * **${GENESIS_WINDOW_DICT}** - Corresponds to TC_GEN_GENESIS_WINDOW_[BEGIN/END] in the METplus configuration file.
# * **${GENESIS_RADIUS}** - Corresponds to TC_GEN_GENESIS_RADIUS in the METplus configuration file.
# * **${DLAND_FILE}** - Corresponds to TC_GEN_DLAND_FILE in the METplus configuration file.

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
# 1) Passing in TCGen.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/TCGen/TCGen.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCGen.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/TCGen/TCGen.conf
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
# Output for this use case will be found in met_tool_wrapper/TCGen
# and will contain the following files:
#
# * tc_gen_2016_ctc.txt
# * tc_gen_2016_cts.txt
# * tc_gen_2016.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#  `TCGenToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCGenToolUseCase&check_keywords=yes&area=default>`_,
#  `DTCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=DTCOrgUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-TCGen.png'
