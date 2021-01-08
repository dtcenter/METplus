"""
UserScript: Run Once Per Lead Use Case
======================================

met_tool_wrapper/UserScript/UserScript_run_once_per_lead.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Demonstrate how to run a user-defined script that should be executed once
# for each forecast lead time.
# This use case runs a simple ls command to list the contents of a directory.
# A wildcard character (*) is used to replace filename template tags for
# valid and init to find all files that match any of the times available.
#

##############################################################################
# Datasets
# --------
#
# | **Input:** Empty test files from the METplus repository
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus UserScript wrapper to generate a command
# that is specified by the user.

##############################################################################
# METplus Workflow
# ----------------
#
# UserScript is the only tool called in this example. It processes the following
# run times:
#
# | **Forecast Lead:** 0 hour
# | **Forecast Lead:** 12 hour
# | **Forecast Lead:** 24 hour
# | **Forecast Lead:** 120 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_lead.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_lead.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. UserScript does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_run_once_per_lead.conf_run_once then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_lead.conf_run_once -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_run_once_per_lead.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/UserScript_run_once_per_lead.conf
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
# No output files are generated from this use case, but the logfile will
# contain the results of the directory listing command(s)
#
# Forecast Lead: 0 hour
#
# * init_20141031093015_valid_20141031093015_lead_000.nc
# * init_20141031213015_valid_20141031213015_lead_000.nc
# * init_20141101093015_valid_20141101093015_lead_000.nc
#
# Forecast Lead: 12 hour
#
# * init_20141030213015_valid_20141031093015_lead_012.nc
# * init_20141031093015_valid_20141031213015_lead_012.nc
# * init_20141031213015_valid_20141101093015_lead_012.nc
# * init_20141101093015_valid_20141101213015_lead_012.nc
#
# Forecast Lead: 24 hour
#
# * init_20141030093015_valid_20141031093015_lead_024.nc
# * init_20141030213015_valid_20141031213015_lead_024.nc
# * init_20141031093015_valid_20141101093015_lead_024.nc
# * init_20141031213015_valid_20141101213015_lead_024.nc
# * init_20141101093015_valid_20141102093015_lead_024.nc
#
# Forecast Lead: 120 hour
#
# * init_20141026093015_valid_20141031093015_lead_120.nc
# * init_20141026213015_valid_20141031213015_lead_120.nc
# * init_20141027093015_valid_20141101093015_lead_120.nc
# * init_20141031093015_valid_20141105093015_lead_120.nc
# * init_20141031213015_valid_20141105213015_lead_120.nc
# * init_20141101093015_valid_20141106093015_lead_120.nc
#

##############################################################################
# Keywords
# --------
#
# .. note:: `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_,
#  `RuntimeFreqUseCase <https://dtcenter.github.io/METplus/search.html?q=RuntimeFreqUseCase&check_keywords=yes&area=default>`_
#
