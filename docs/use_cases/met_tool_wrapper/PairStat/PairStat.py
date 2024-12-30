"""
PairStat: Basic Use Case
========================

met_tool_wrapper/PairStat/PairStat.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare hourly forecasts for temperature, u-, and v-wind components to observations
# in a 3-hour observation window. Generate statistics of the results.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** NAM temperature, u-wind component, and v-wind component
# | **Observation:** prepBUFR data that has been converted to NetCDF format via PB2NC
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** Unknown
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PairStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool pair_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PairStat is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2007-03-30_0Z
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/PairStat/PairStat.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PairStat/PairStat.conf

##############################################################################
# MET Configuration
# ---------------------
#
# .. note::
#     See the :ref:`PairStat MET Configuration<pair-stat-met-conf>`
#     section of the User's Guide for more information on the environment
#     variables used in the file below.
#
# parm/met_config/PairStatConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PairStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Provide the use case .conf configuration file to the run_metplus.py script.
#
# /path/to/METplus/parm/use_cases/met_tool_wrapper/PairStat/PairStat.conf
#
# See the :ref:`running-metplus` section of the System Configuration chapter
# for more details.
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
# Output for this use case will be found in pair_stat (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * pair_stat_360000L_20070331_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PairStatToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PairStat.png'
#
