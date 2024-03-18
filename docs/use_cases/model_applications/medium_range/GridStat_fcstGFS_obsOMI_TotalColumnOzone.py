"""
Grid-Stat: Using Python Embedding for Total Column Ozone
================================================================================

model_applications/medium_range/GridStat_fcstGFS_obsOMI
_TotalColumnOzone.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between observation
# data in gridded format to a gridded forecast. The Ozone Monitoring Instrument (OMI)
# data covers a 36 hour period and is compared to the average of the gridded forecast
# files (all from the same initialization time). 

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS (1 degree Lat/Lon grid)
# | **Observation:** NASA's Level-3 Aura/OMI Global Total Ozone Mapping Spectrometer-Like (TOMS-Like) Total Column Ozone gridded product OMTO3e (0.25deg Lat/Lon grid)
# | **Location:** Click here for the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the forecast data to build a
# 36-hour Total Colum Ozone mean/average file. Then the forecast data
# are compared to the observation data using GridStat. This use case utilizes 
# the METplus GridStat wrapper to read in the observation file using Python Embedding.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# PCPCombine (forecast) > GridStat
#
# It processes the following run times:
#
# | **Valid:** 2023-12-05 06Z (36 hour period covering 2023-12-03 18Z - 2023-12-05 06Z)
# | **Init:** 2023-12-03 06Z
# | **Forecast lead:** 48

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone.conf

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
# .. note:: See the :ref:`GridStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses one Python embedding script with GridStat to read the input observation data
#
# parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone/read_omi-aura_l3-omto3e.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone/read_omi-aura_l3-omto3e.py


##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone.conf /path/to/user_system.conf
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
# Output for this use case will be found in /model_applications/medium_range/GridStat_fcstGFS_obsOMI_TotalColumnOzone
# (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * PCPCombine/pcp_combine.tozone_l0.mean.f048.init2023120306.nc
# * GridStat/grid_stat_GFS_vs_OMI_480000L_20231205_060000V.stat 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PCPCombineToolUseCase
#   * GridStatToolUseCase
#   * MediumRangeAppUseCase
#   * GRIBFileUseCase
#   * PythonEmbeddingFileUseCase
#   * RegriddingInToolUseCase
#   * NOAAEMCOrgUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-GridStat_fcstGFS_obsOMI_TotalColumnOzone.png'
#
