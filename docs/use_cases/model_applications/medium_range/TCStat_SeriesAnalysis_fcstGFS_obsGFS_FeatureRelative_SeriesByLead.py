"""
Multi_Tool: Feature Relative by Lead (with lead groupings) 
==========================================================

model_applicaitons/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf

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
# By maintaining focus of each evaluation time (or evaluation time series, in this case)
# on a user-defined area around a cyclone, the model statistical errors associated
# with cyclonic physical features (moisture flux, stability, strength of upper-level
# PV anomaly and jet, etc.) can be related directly to the model forecasts and provide
# improvement guidance by accurately depicting interactions with significant weather
# features around and within the cyclone. This is in contrast to the traditional
# method of regional averaging cyclone observations in a fixed grid, which
# "smooths out" system features and limits the meaningful metrics that can be gathered.
# Specifically, this use case creates bins of forecast lead times as specified by the
# given ranges which provides additional insight directly into forecast lead time accuracy.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
#
#  * TC-Pairs/TC-Stat Forecast dataset: ADeck modified-ATCF tropical cyclone data
#  * Series-Analysis Forecast dataset: GFS
#  * TC-Pairs/TC-Stat Observation  dataset: BDeck modified-ATCF tropical cyclone data
#  * Series-Analysis Observation dataset: GFS Analysis

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed::
#
# * netCDF4

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TCPairs and ExtractTiles wrappers to generate matched
# tropical cyclone data and regrid them into appropriately-sized tiles
# along a storm track. The MET tc-stat tool is used to filter the
# track data, and the MET regrid-dataplane tool is used to regrid the
# data (GRIB1 or GRIB2 into netCDF). Next, a series analysis by lead time is
# performed on the results and plots (.ps and .png) are generated for all
# variable-level-stat combinations from the specified variables, levels, and
# requested statistics. The final results are aggregated into forecast hour
# groupings as specified by the start, end and increment in the METplus
# configuration file, as well as labels to identify each forecast hour grouping.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 20141214
#
# **End time (INIT_END):** 20141214
#
# **Increment between beginning and end times (INIT_INCREMENT):** None
#
# **Sequence of forecast leads to process:**
#
# | LEAD_SEQ_1 = begin_end_incr(0,18,6)
# | LEAD_SEQ_1_LABEL = Day1
# |
# | LEAD_SEQ_2 = begin_end_incr(24,42,6)
# | LEAD_SEQ_2_LABEL = Day2
#
# The following tools are used for each run time:
#
# TCPairs > RegridDataPlane, TCStat > SeriesAnalysis
#
# This example loops by forecast/lead time (with begin, end, and increment as specified in the METplus
# TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf file).
# The following will be run based on the availability of data corresponding to the initialization time
# (in this example, we only have 20141214 as our initialization time) and the requested forecast leads, resulting
# in the run times below.
#
# Run times:
#
# **Init:** 20141214_0Z
#
# **Forecast lead:** 6, 12, 18, 24, 30, 36, 42

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf

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
# .. dropdown:: TCPairsConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/TCPairsConfig_wrapped
#
# .. dropdown:: TCStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/TCStatConfig_wrapped
#
# .. dropdown:: SeriesAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in series_analysis_lead, relative to the **OUTPUT_BASE**, and in the following directories (relative to **OUTPUT_BASE**):
#
# * Day1
# * Day2
# * series_animate
#
# The *Day1* subdirectory will contain files that have the following format:
#
#   ANLY_FILES_Fhhh_to_FHHH
#
#   FCST_ASCII_FILES_Fhhh_to_FHHH
#
#   series_<varname>_<level>_<stat>.png
#
#   series_<varname>_<level>_<stat>.ps
#
#   series_<varname>_<level>_<stat>.nc
#
#   Where:
#
#    **hhh** is the starting forecast hour/lead time in hours
#
#    **HHH** is the ending forecast hour/lead time in hours
#
#    **varname** is the variable of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **level**  is the level of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **stat** is the statistic of interest, as specified in the METplus series_by_lead_all_fhrs config file.
#
# The *Day2* subdirectory will contain files that have the same formatting as *Day1*, but for those forecast hours within 24 to 42 hours.
#
# | The series_animate directory contains the animations of the series analysis in .gif format for all variable, level, and statistics combinations:
#
#    series_animate_<varname>_<level>_<stat>.gif




##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MediumRangeAppUseCase
#   * TCPairsToolUseCase
#   * SeriesByLeadUseCase
#   * TCStatToolUseCase
#   * RegridDataPlaneToolUseCase
#   * MediumRangeAppUseCase
#   * SeriesAnalysisUseCase
#   * GRIB2FileUseCase
#   * FeatureRelativeUseCase
#   * SBUOrgUseCase
#   * DiagnosticsUseCase
#   * RuntimeFreqUseCase
#   * TropicalCycloneUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.png'
#
