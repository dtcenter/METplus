"""
Point-Stat: Standard Verification of Global Upper Air  
=====================================================

model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf

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
# To provide useful statistical information on the relationship between observation
# data in point format to a gridded forecast. These values can be used to assess  
# the skill of the prediction.  Statistics are stored as partial sums to save
# space and Stat-Analysis must be used to compute the Continuous Statistics.


##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS temperature, u-wind component, v-wind component, and height
# | **Observation:** GDAS prepBURF data
#
# | **Location:** Click here for the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PB2NC wrapper to convert PrepBUFR point observations to NetCDF format and then compare them to gridded forecast data using PointStat.


##############################################################################
# METplus Workflow
# ----------------
#
# PB2NC and PointStat are the tools called in this example. It processes the following run times:
#
# | **Valid:** 2017-06-01 0Z
# | **Valid:** 2017-06-02 0Z
# | **Valid:** 2017-06-03 0Z
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf
#

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
# .. dropdown:: PB2NCConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PB2NCConfig_wrapped
#
# .. dropdown:: PointStatConfig_wrapped**
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf /path/to/user_system.conf
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
# Output for this use case will be found in gdas (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_000000L_20170601_000000V.stat
# * point_stat_000000L_20170602_000000V.stat
# * point_stat_000000L_20170603_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PB2NCToolUseCase
#   * PointStatToolUseCase
#   * MediumRangeAppUseCase
#   * GRIBFileUseCase
#   * prepBUFRFileUseCase
#   * NOAAEMCOrgUseCase
#   * RegriddinginToolUseCase
#   * ObsTimeSummaryUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.png'
#
