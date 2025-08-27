"""
GridStat: Times from Template
=============================

met_tool_wrapper/GridStat/GridStat_times_from_template.conf

"""
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
# ---------------------
#
# .. note::
#     See the :ref:`GridStat MET Configuration<grid-stat-met-conf>`
#     section of the User's Guide for more information on the environment
#     variables used in the file below.
#
# parm/met_config/GridStatConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Provide the use case .conf configuration file to the run_metplus.py script.
#
# /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat_times_from_template.conf
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
