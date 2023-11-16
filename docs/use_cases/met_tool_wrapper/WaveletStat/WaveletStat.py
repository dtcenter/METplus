"""
WaveletStat: Basic Use Case
===========================

met_tool_wrapper/WaveletStat/WaveletStat.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare 3 hour forecast precipitation accumulations to observations
# of 3 hour precipitation accumulation. Generate statistics of the results.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF 3 hour precipitation accumulation
# | **Observation:** MU 3 hour precipitation accumulation
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here for the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See the `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus WaveletStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool wavelet_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# WaveletStat is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 12 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line:
# parm/use_cases/met_tool_wrapper/WaveletStat/WaveletStat.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/WaveletStat/WaveletStat.conf

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
# .. note:: See the :ref:`WaveletStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/WaveletStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/WaveletStat/WaveletStat.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
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
# Output for this use case will be found in wavelet_stat/2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * wavelet_stat_120000L_20050807_120000V_isc.txt
# * wavelet_stat_120000L_20050807_120000V.nc
# * wavelet_stat_120000L_20050807_120000V.ps
# * wavelet_stat_120000L_20050807_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * WaveletStatToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-WaveletStat.png'
#
