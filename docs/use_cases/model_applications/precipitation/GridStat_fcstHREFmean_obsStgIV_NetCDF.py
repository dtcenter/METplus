"""
Grid-Stat: 6hr QPF in NetCDF format
===================================

model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Netcdf.conf

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
# Evaluate the skill of a high resolution multi-model ensemble mean
# at predicting 6 hour precipitation accumulation using the NCEP Stage IV
# gauge corrected analysis.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# Describe the datasets here. Relevant information about the datasets that would
# be beneficial include:
# 
#  * Forecast dataset: HREF mean forecasts in NetCDF
#  * Observation dataset: Stage IV GRIB 6 hour precipitation accumulation
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the forecast data to build a 6
# hour precipitation accumulation from 1 hour files or a single 6 hour file.
# Then the observation data is regridded to the model grid using the RegridDataPlane. Finally, the
# observation files are compared to the forecast data using GridStat.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# PCPCombine (observation) > RegridDataPlane (observation) > GridStat
#
# This example loops by initialization time.
# There is only one initalization time in this example so the following will be run:
#
# Run times:
#
# | **Init:** 2017-05-09_12Z
# | **Forecast lead:** 18
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_NetCDF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_NetCDF.conf
#


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
# .. dropdown:: GridStatConfig_wrapped
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_NetCDF.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_NetCDF/GridStat/201705091200 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_000000L_20170510_060000V_pairs.nc
# * grid_stat_000000L_20170510_060000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PrecipitationAppUseCase
#   * PCPCombineToolUseCase
#   * RegridDataPlaneToolUseCase
#   * NetCDFFileUseCase
#   * NOAAWPCOrgUseCase
#   * NOAAHMTOrgUseCase
#   * NOAAHWTOrgUseCase
#   * ConvectionAllowingModelsAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-GridStat_fcstHREFmean_obsStgIV_NetCDF.png'
#
