"""
GridStat: Times from Template
=============================

met_tool_wrapper/GridStat/GridStat_times_from_template.conf

"""

##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# Compare 3 hour forecast precipitation accumulations to observations
# of 3 hour precipitation accumulation. Generate statistics of the results.
#
# This use case is similar to the basic GridStat use case,
# but it uses filename templates to build the list
# of run times to process based on existing files on disk.
# The basic use case only processes a single forecast lead, but this use case
# processes 4 forecast leads because the input data are available.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.2

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
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool grid_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 3, 6, 9, 12 hours
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/GridStat/GridStat_times_from_template.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GridStat/GridStat_times_from_template.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not call a Python Embedding script.
#

##############################################################################
# User Scripting
# --------------
#
# This user case does not call a user-defined script.
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_times_from_template.conf /path/to/user_system.conf
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
# Output for this use case will be found in met_tool_wrapper/GridStat/GridStat/2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_030000L_20050807_030000V_eclv.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_030000L_20050807_030000V_grad.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_030000L_20050807_030000V.stat
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_060000L_20050807_060000V_eclv.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_060000L_20050807_060000V_grad.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_060000L_20050807_060000V.stat
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_090000L_20050807_090000V_eclv.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_090000L_20050807_090000V_grad.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_090000L_20050807_090000V.stat
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V_eclv.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V_grad.txt
# * grid_stat_WRF_APCP_vs_MC_PCP_APCP_03_120000L_20050807_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * TimesFromTemplateUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GridStat.png'
#
