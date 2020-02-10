"""
Track and Intensity Use case (filter TC Pairs output)
==================================================================
This use case generates TC-pairs .tcst output files
via MET TC-pairs, then performs further filtering on the output
based on a specific cyclone of interest.
"""

##############################################################################
# Scientific Objective
# --------------------
#
# Describe the scientific objective of the use case here. This can be fairly
# simple, or complex depending on the task.

##############################################################################
# Datasets
# --------
#
#
#  * Forecast dataset: ADeck non-ATCF tropical cyclone data
#  * Observation dataset: non-ATCF tropical cyclone "best track"(BDeck) cyclone data
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TcPairs and then filters out results specific to
# a cyclone.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#  TcPairs > TcStat
#
# To generate TcPairs output, this example loops by initialization time for every 6 hour period that is available
# in the data set for 20141214. The output is then filtered using TcStat to produce output for the specified
# cyclone of interest as specified in the TC_STAT_JOBS_LIST in the METplus config file.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/tc_and_extra_tc/tcmpr_mean_median_box.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/tc_stat_filter.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/TCStatConfig
#
#
# See the following files for more information about the environment variables set in these configuration files.
#   parm/use_cases/met_tool_wrapper/TCPairs.py
#
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in tcmpr_mean_median_box.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/tc_stat_filter.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in tc_stat_filter.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/tc_stat_filter.conf
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
# TCPairs output for this use case will be found in tc_pairs/201412 (relative to **OUTPUT_BASE**)
# and will contain files with the following format:
#
# |    * mlq2014121400.gfso.<*nnnn*>.tcst
# |
# | where nnnn is a zero-padded 4-digit number.
# |
# | The filtered result is a .tcst file (relative to **OUTPUT_BASE**), which was specified in the TC_STAT_JOBS_LIST value in the METplus config file:
# |    * tc_stat_filter_config.tcst
#




##############################################################################
# Keywords
# --------
#
#
#
#
# .. note:: TcPairsUseCase,TcStatUseCase
