"""
UserScript: Run Once Per Init Use Case
======================================

met_tool_wrapper/UserScript/UserScript_run_once_per_init.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Demonstrate how to run a user-defined script that should be executed once
# for each initialization time.
# This use case runs a simple ls command to list the contents of a directory.
# A wildcard character (*) is used to replace filename template tags for
# valid and lead to find all files that match any of the times available.
#

##############################################################################
# Datasets
# --------
#
# | **Input:** Empty test files from the METplus repository
# |
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
# | **Init:** 2014-10-31 09:30:15
# | **Init:** 2014-10-31 21:30:15
# | **Init:** 2014-11-01 09:30:15
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_init.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_init.conf

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
# 1) Passing in UserScript_run_once_per_init.conf_run_once then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/UserScript/UserScript_run_once_per_init.conf_run_once -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_run_once_per_init.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/UserScript_run_once_per_init.conf
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
# Init time: 2014-10-31 09:30:15
#
# * init_20141031093015_valid_20141031093015_lead_000.nc
# * init_20141031093015_valid_20141031213015_lead_012.nc
# * init_20141031093015_valid_20141101093015_lead_024.nc
# * init_20141031093015_valid_20141102093015_lead_048.nc
# * init_20141031093015_valid_20141103093015_lead_072.nc
# * init_20141031093015_valid_20141104093015_lead_096.nc
# * init_20141031093015_valid_20141105093015_lead_120.nc
# * init_20141031093015_valid_20141106093015_lead_144.nc
# * init_20141031093015_valid_20141107093015_lead_168.nc
#
# Init time: 2014-10-31 21:30:15
#
# * init_20141031213015_valid_20141031213015_lead_000.nc
# * init_20141031213015_valid_20141101093015_lead_012.nc
# * init_20141031213015_valid_20141101213015_lead_024.nc
# * init_20141031213015_valid_20141102213015_lead_048.nc
# * init_20141031213015_valid_20141103213015_lead_072.nc
# * init_20141031213015_valid_20141104213015_lead_096.nc
# * init_20141031213015_valid_20141105213015_lead_120.nc
# * init_20141031213015_valid_20141106213015_lead_144.nc
# * init_20141031213015_valid_20141107213015_lead_168.nc
#
# Init time: 2014-11-01 09:30:15
#
# * init_20141101093015_valid_20141101093015_lead_000.nc
# * init_20141101093015_valid_20141101213015_lead_012.nc
# * init_20141101093015_valid_20141102093015_lead_024.nc
# * init_20141101093015_valid_20141103093015_lead_048.nc
# * init_20141101093015_valid_20141104093015_lead_072.nc
# * init_20141101093015_valid_20141105093015_lead_096.nc
# * init_20141101093015_valid_20141106093015_lead_120.nc
# * init_20141101093015_valid_20141107093015_lead_144.nc
# * init_20141101093015_valid_20141108093015_lead_168.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * RuntimeFreqUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#

