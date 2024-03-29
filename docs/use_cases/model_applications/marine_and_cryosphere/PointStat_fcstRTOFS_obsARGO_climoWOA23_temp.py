"""
PointStat: Python embedding to read Argo netCDF files to verify ocean temperature forecast at 50 m depth
========================================================================================================

model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case utilizes the ASCII2NC tool with python embedding to natively read in Argo
# netCDF files, a common source of ocean profile data for operational entities. These
# values are then used by the PointStat tool to verify RTOFS ocean temperature forecast at 50 m depth.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** RTOFSv2.3 forecast data pre-processed into 0.1 degree lat-lon grid
#
# | **Observations:** three netCDF files from Argo
#
# | **Climatology:** two monthly climatology files from WOA23
#
# | **Sea Ice Mask:** a mask file to exclude forecast grid points with sea ice concentration > 15%
#
# | **Location:** All of the input data required for this use case can be found in the
#   marine_and_cryosphere sample data tarball. Click here to the METplus releases page and download sample
#   data for the appropriate release: https://github.com/dtcenter/METplus/releases
#   This tarball should be unpacked into the directory that you will set the value of
#   INPUT_BASE. See `Running METplus`_ section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls ASCII2NC to read in Argo netCDF files and then PointStat for
# verification against RTOFS model data.

##############################################################################
# METplus Workflow
# ----------------
#
# ASCII2NC is the first tool called. It pulls in three Argo files for the Atlantic,
# Pacific, and Indian Oceans, respectively using a Python script. These observations are converted into a netCDF
# file, which is then called by PointStat as the observation dataset. PointStat also pulls
# in a forecast from the RTOFS for ocean temperature at 50 m depth, which is included in
# the range of available observation times, and two monthly climatology files from the
# WOA23 to calculate daily climatology for the valid date. A 24-hour (18Z to 18Z) window is
# allowed for the observational data, and a “UNIQUE” flag is set to only use the
# observational data closest to the forecast valid time at a given location. Temperature
# thresholds are set to correspond to operational usage, and the CTC, CTS, CNT, SL1L2, and
# SAL1L2 line types are requested.
# It processes the following run time:
#
# | **Valid:** 2023-03-18 00Z
#
# | **Forecast lead:** 24 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the default configuration files found in parm/metplus_config, then it loads any configuration files passed to METplus via the command line with the -c option, i.e. -c parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp.conf

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
# .. note:: See the :ref:`PointStat MET Configuration<point-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses one Python script to read observation data.
#
# parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp/read_argo_metplus.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp/read_argo_metplus.py

##############################################################################
# Running METplus
# ---------------
#
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstRTOFS_obsARGO_climoWOA23_temp.conf /path/to/user_system.conf
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
# Output for this use case will be found in prep and stats/rtofs.20230318 directories (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * argo.20230318.nc
# * point_stat_RTOFS_ARGO_temp_Z50_240000L_20230318_000000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * ASCII2NCToolUseCase
#   * PythonEmbeddingFileUseCase
#   * ClimatologyUseCase
#   * MarineAndCryosphereAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-PointStat_fcstRTOFS_obsARGO_climoWOA23_temp.png'
