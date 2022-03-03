"""
CycloneVerification: TC Verification Compare ADECK vs BDECK
===========================================================

model_applications/tc_and_extra_tc/TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample.conf

"""
###########################################
# Scientific Objective
# --------------------
#
# This use case run TC-Pairs to produce produce matched pairs of forecast model 
# output and an observation dataset. TC-Pairs produces matched pairs for position 
# errors, as well as wind, sea level pressure, and distance to land values for 
# each input dataset. Then TC-stat will filter TC-pairs output based on user criteria.

##############################################################################
# Datasets
# --------
#
#
# | **Forecast:** Adeck
# |     /path/to/TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample/a{basin}{cyclone}{init?fmt=%Y}.dat
# | **Observation:** Bdeck
# |     /path/to/{TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample/b{basin}{cyclone}{init?fmt=%Y}.dat
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** NHC ftp.noaa.gov/atcf
# |

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# TCPairs
# TCStat
#
# To generate TCPairs output, this example loops by initialization time for every 6 hour period that is available
# in the data set between 2021082500 and 2021083000. Then TCStat filters the TCPairs output based on user criteria
# (e.g. storm characteristics in this use case).
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TC-Pairs to produce matched pairs of Adeck and Bdeck files.
# The TC-Pairs output (tcst files) is then read by the TC-Stat tool to further filter the tcst files
# as well as summarize the statistical information. 

##############################################################################
# METplus Workflow
# ----------------
#
# TCPairs is the first tool called in this example. It processes the following
# run times for each storm file (e.g. aal092021.dat, aal102021.dat) against the corresponding 
# Bdeck files (e.g. bal092021.dat, bal102021.dat):
#
# | **Init/Valid:** 2021082500
# | **End/Valid:** 2021083000
#
# TC-Stat is the second (and final) tool called in this example. It processes the output
# from TCPairs. In this example the TC-Stat filters the TC-Pairs output based on the 
# characteristics of the storm (HU, SD, SS, TS, TD). The output from the TC-Stat can be used to 
# aggregate verification statistics (e.g. Track, Intensity, MSLP, wind radii errors etc.).
# 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c /path/to/TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`TCPairs MET Configuration<tc-pairs-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCPairsConfig_wrapped
# .. literalinclude:: ../../../../parm/met_config/TCStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/TCPairs_TCStat_fcstADECK_obsBDECK_ATCF_BasicExample.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where Adeck and Bdeck ATCF format files are read (See Datasets section to obtain tarballs).
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
# Output for this use case will be found in tc_pairs/ tc_stat/ (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * tc_pairs/tc_pairs.al092021.tcst
# * tc_pairs/tc_pairs.al102021.tcst
# * tc_stat/tc_stat_summary.tcst
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCPairsToolUseCase
#   * TCStatToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#




