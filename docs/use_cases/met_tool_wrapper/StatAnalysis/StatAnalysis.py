"""
StatAnalysis: Basic Use Case
===========================================================================

met_tool_wrapper/StatAnalysis/StatAnalysis.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# This demonstrates how the Stat-Analysis tool can tie together results from other
# MET tools (including PointStat, GridStat, EnsembleStat, and WaveletStat)
# and provide summary statistical information.


##############################################################################
# Datasets
# --------
#
#
# | **WRF ARW grid_stat output STAT files:**
# |     ...met_test/out/grid_stat/
# |         grid_stat_120000L_20050807_120000V.stat
# |         grid_stat_APCP_12_120000L_20050807_120000V.stat
# |         grid_stat_APCP_24_240000L_20050808_000000V.stat
# |         grid_stat_POP_12_1080000L_20050808_000000V.stat
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# | **Data Source:** WRF
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus StatAnalysis wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool stat_analysis.

##############################################################################
# METplus Workflow
# ----------------
#
# StatAnalysis is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2005-08-07_00Z  
# | **Forecast lead:** 12 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/StatAnalysis/StatAnalysis.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/StatAnalysis/StatAnalysis.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`StatAnalysis MET Configuration<stat-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in StatAnalysis.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/StatAnalysis.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
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
# Output for this use case will be found in stat_analysis/12Z/WRF  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * WRF_2005080712.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#  `StatAnalysisToolUseCase <https://dtcenter.github.io/METplus/search.html?q=StatAnalysisToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-StatAnalysis.png'
