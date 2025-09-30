"""
Grid-Stat, Stat-Analysis, Data-Ingest: Credit and GFS statistics and Data Download
==================================================================================

model_applications/medium_range/GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.conf

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
# This use case is an example for verification within RAL to illustrate how to 
# compare 2 models and also how to download data automatically.  The use case was 
# originally designed to be run in real-time using the now keyword in VALID_BEG and 
# VALID_END.  However, a specified date is used in this example as for our automated 
# testing.  The case demonstrates how to run statistics for 2 models, Credit and GFS 
# for both the surface and upper air evaluation.  Surface and upper air statistics are 
# run separately since they are stored in separate observation files.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.2

##############################################################################
# Datasets
# --------
#
# **Forecast**: Credit ~0.28 degree model and GFS 0.25 degree model
#
# **Observation**: GFS Analysis
#
# **Climatology:** None
#
# **Location:** The Credit model data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#
# The GFS model data and GDAS observations are downloaded automatically.  Make sure you 
# have an internet connection.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls DataIngest once, GridStat 4 times and StatAnalysis once.  GridStat
# has 4 calls, 2 for the Credit model and 2 for the GFS for the surface and upper air
# evaluation respectively.


##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2025-09-24 00Z
#
# **End time (VALID_END):** 2025-09-24 06Z
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 6, 12
#
# The DataIngest and GridStat tools are run for each time, whereas StatAnalysis is
# run once.  This example loops by valid times. It processes 2 lead times for 2 valid times with 
# a total of 4 runs.  The times are listed below. 
#
# | **Init:** 2025-09-23_18Z
# | **Valid:** 2025-09-24_00Z
# | **Forecast lead:** 06
#
# | **Init:** 2025-09-23_12Z
# | **Valid:** 2025-09-24_00Z
# | **Forecast lead:** 12
#
# | **Init:** 2025-09-24_00Z
# | **Valid:** 2025-09-24_06Z
# | **Forecast lead:** 06
#
# | **Init:** 2025-09-23_18Z
# | **Valid:** 2025-09-24_06Z
# | **Forecast lead:** 12
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/medium_range/GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.conf


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
#
# .. dropdown:: StatAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# This user case does not call a user-defined script.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.conf /path/to/user_system.conf
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
# Output for this use case will be found in 
# {OUTPUT_BASE}/model_applications/medium_range/GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.conf.  There will 
# be 3 directories, data_ingest that contains the downloaded data, grid_stat which contains the output
# statistics, and StatAnalysis which contains the aggregated statistics.  The data_ingest directory 
# will contain 2 subdirectories, GFS and GFS_analysis, each with the downloaded data. The data inside 
# the GFS directory is sorted by model initialization time and contains both surface and upper air data.  
# These files have the format, where II is the model initialzation hours and HHH is the lead time in 
# hours::
#
# * gfs.tIIz.pgrb2.0p25.fHHH 
# * gfs.tIIz.sfluxgrbfHHH.grib2
#
# The GFS_analysis directory contains one subdirectory 20250924 with 4 files::
#
# * gfs.2025092400.pgrb2.0p25.anl
# * gfs.2025092406.pgrb2.0p25.anl
# * gfs_anal_2025092400.sfcanl.nc
# * gfs_anal_2025092406.sfcanl.nc
#
# Inside the grid_stat directory, there are also 2 subdirectories, Credit/6h and GFS.  The files output 
# to Credit/6h are also stored in subdirectories dated with model initialization time in the format of 
# YYYYMMDDHH.  These files have the following format, where the dates labeled are lead time, valid year, 
# month, and day, and valid hour, minute, and second::
#
# * grid_stat_Credit_surface_HHMMSSL_YYYYMMDD_HHMMSSV.stat
# * grid_stat_Credit_upper_air_HHMMSSL_YYYYMMDD_HHMMSSV.stat
#
# The files output to the GFS directory are also stored in subdirectories dated with model 
# initialization time in the format of YYYYMMDDHH.  These files have the same format as above where
# the dates labeled are lead time, valid year, month, and day, and valid hour, minute, and second::
#
# * grid_stat_GFS_surface_HHMMSSL_YYYYMMDD_HHMMSSV.stat
# * grid_stat_GFS_upper_air_HHMMSSL_YYYYMMDD_HHMMSSV.stat
#
# The StatAnalysis directory contains 1 subdirectory (6h).  Inside that directory are
# 4 output files::
#
# * Credit_GFS_2025092400_2025092406_allleads_allValidHours_CNT.stat
# * Credit_GFS_2025092400_2025092406_allleads_allValidHours_CTS.stat
# * GFS_GFS_2025092400_2025092406_allleads_allValidHours_CNT.stat
# * GFS_GFS_2025092400_2025092406_allleads_allValidHours_CTS.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * DataIngestToolUseCase
#   * GridStatToolUseCase
#   * StatAnalysisToolUseCase
#   * RALAppUseCase
#   * GRIB2FileUseCase
#   * NetCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-GridStat_fcstCredit_GFS_obsGFS_6hrRealtime.png'
