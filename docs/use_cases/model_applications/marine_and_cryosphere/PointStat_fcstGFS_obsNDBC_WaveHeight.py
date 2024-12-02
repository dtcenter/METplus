"""
PointStat: read in buoy ASCII files to compare to model wave heights
====================================================================

model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsNDBC_WaveHeight.conf

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
# This use case utilizes the new ASCII2NC method to natively read in NDBC ASCII files, a common source of sea surface data
# for operational entities. These values are then compared to GFS' new wave height output, which it incorporated from Wave Watch III.

##############################################################################
# Version Added
# -------------
#
# METplus version 5.1

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFSv16 forecast data from WAVE file category 
#
# | **Observations:** ASCII buoy files from NDBC
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls ASCII2NC to read in ASCII buoy files and
# then PointStat for verification against GFS model data

##############################################################################
# METplus Workflow
# ----------------
#
# ASCII2NC is the first tool called. It pulls in all files with a .txt type, which is 
# the ASCII buoy data saved format. These observations are converted into a netCDF, which is then called by PointStat
# as the observation dataset. PointStat also pulls in a 3 hour forecast from the GFS for wave heights, which is included
# in the range of available buoy observation times. A +/- 30 minute window is allowed for the observational data. 
# Thresholds are set that correspond to operational usage, and the CTC and CTS line types are requested.
# It processes the following run time:
#
# | **Valid:** 2022-10-16 09Z
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsNDBC_WaveHeight.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsNDBC_WaveHeight.conf

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
# .. dropdown:: Ascii2NcConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# .. dropdown:: PointStatConfig_wrapped
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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsNDBC_WaveHeight.conf /path/to/user_system.conf
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
# Output for this use case will be found in  PointStat and buoy_ASCII directories (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_030000L_20221016_090000V_ctc.txt
# * point_stat_030000L_20221016_090000V_cts.txt
# * point_stat_030000L_20221016_090000V.stat
# * buoy_2022101609.nc 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * ASCII2NCToolUseCase
#   * GRIB2FileUseCase
#   * MarineAndCryosphereAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-PointStat_fcstGFS_obsNDBC_WaveHeight.png'

