"""
Point-Stat, Stat-Analysis, UserScript, DataIngest: Credit and GFS point statistics, Data Download, Plots
========================================================================================================

model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf

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
# compare two models and also how to download data automatically.  The use case was 
# originally set up to be run in real-time using the now keyword in VALID_BEG and 
# VALID_END.  However, a specified date is provided used here for our automated 
# testing.  The case demonstrates how to run statistics for two models, Credit and 
# GFS and how to make plots of continuous statistics ME, MAE and RMSE and categorical
# statistics CSI and FBIAS  on some of the variables.  In contrast to the 
# GridStat_fcstCredit_GFS_obsGFS_6hrRealtime use case, this case uses point observations 
# whereas that one used gridded observations.  Also, that use case shows how to process 
# multiple valid times while this one uses only a single valid time.

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
# **Observation**: GDAS
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
# This use case calls DataIngest once, PointStat 3 times, StatAnalysis once, and UserScript
# 4 times.  One of the PointStat calls is for the Credit model and 2 are for the GFS model 
# (one for the surface data and one for the upper air data).  The 4 UserScripts require 
# METcalcpy, METplotpy, and METdataio are required to run this use case.  The METcalcpy 
# scripts accessed include the following:
#
# * metcalcpy/util/read_env_vars_in_config.py
#
# The METplopty scrips accessed include the following:
#
# * metplotpy/plots/line/line.py
#
# The METdataio scripts accessed include the following:
#
# * METdbLoad/ush/read_data_files.py
#
# * METdbLoad/ush/read_load_xml.py
#
# * METreformat/write_stat_ascii.py


##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2025-09-24 00Z
#
# **End time (VALID_END):** 2025-09-24 00Z
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0 - 120 in 6 hour intervals
#
# DataIngest, PointStat, and StatAnalysis tools are run for each time, whereas StatAnalysis is
# run once.  This example loops by valid times. It processes 20 lead times for 1 valid
# time for a total of 20 runs.  All 4 UserScripts are each run once.  The first UserScript reformats
# the PointStat CNT output while the second reformats the PointStat CTS output so that they can be 
# used for plotting.  The third and fourth UserScript calls creates plots, one for the CNT output
# and the other for the CTS output.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# e.g. parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf

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
# There are three Python scripts used in this use case, called using the "UserScript" keyword
# in the METplus wrappers PROCESS_LIST configuration item.  These scripts provide an
# interface to the functions in the METdataio, METcalcpy, and METplotpy Python modules
# of METplus.  The functions used in these scripts demonstrate reformatting
# aggregated StatAnalysis output to meet the format required by METcalcpy and METplotpy,
# and then plotting that reformatted output using functions from METcalcpy and METplotpy.  
# 
# The first Python scripts is called reformat_linetype.py.  This script takes the aggregated 
# output linetype from Stat Analysis and reformats it so that the data can be plotted.  
# The script takes an input .yaml file of which there are 2, reformat_CNT.yaml and reformat_CTS.yaml.  
# Environment variables in the yaml file are specified in the [user_env_vars] section of the 
# PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf METplus configuration file.
#
# The second Python script is plot_line_stats.py.  This script creates line plots for Credit and GFS
# of MAE, ME and RMSE with lead time, using the YAML file custom_2line_6h.yaml.  Input variables to this 
# script are also specified in the [user_env_vars] section of the
# PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf METplus configuration file.
#
# The third Python script is plot_line_stats_CTS.py.  This script creates line plots for Credit and GFS
# of CSI and Frequency Bias with lead time, using the YAML file custom_2line_cat_6h.yaml.  Input variables 
# to this script are also specified in the [user_env_vars] section of the 
# PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf METplus configuration file.
#
# For more information about YAML configuration options for the line plots shown here, see the METplotpy
# `line plot documentation <https://metplus.readthedocs.io/projects/metplotpy/en/latest/Users_Guide/line.html>`_.
#
# Both Python scripts are located at::
#
#   parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime
#
# .. dropdown:: reformat_linetype.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime/reformat_linetype.py
#
# .. dropdown:: plot_line_stats.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime/plot_line_stats.py
#
# .. dropdown:: plot_line_stats_CTS.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime/plot_line_stats_CTS.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/medium_range/PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.  There will
# be 6 directories, data_ingest, GDAS, plots, point_stat, reformatted, and StatAnalaysis.  The 
# data_ingest directory contains the observation dat that has been downloaded
# and contains 2 subdirectories, GDAS and GFS.  The GDAS directory contains 1 subdirectory, 20250924, 
# with 2 files:
#
# * 20250924_0000.prepbufr.nr
# * 20250924_0600.prepbufr.nr
#
# The data inside the GFS directory is sorted by model initialization time and contains both surface 
# and upper air data.  These files have the format, where II is the model initialzation hours and HHH 
# is the lead time in hours:
#
# * gfs.tIIz.pgrb2.0p25.fHHH 
# * gfs.tIIz.sfluxgrbfHHH.grib2
#
# Inside the GDAS directory contains the GDAS observations that have been converted from prepbufr to
# netCDF.  The directory contains 2 files:
#
# * prepbufr.gdas.2025092400.nc
# * prepbufr.gdas.2025092406.nc 
# 
# The plots directory contains one subdirectory, 6h, that has 11 plots:
#
# * T500_FULL_MAE.png
# * T500_FULL_ME.png
# * T500_FULL_RMSE.png
# * TMP_FULL_CSI.png
# * TMP_FULL_FBIAS.png
# * TMP_FULL_MAE.png
# * TMP_FULL_ME.png
# * TMP_FULL_RMSE.png
# * Z500_FULL_MAE.png
# * Z500_FULL_ME.png
# * Z500_FULL_RMSE.png
#
# The point_stat directory also has 2 subdirectories, Credit/6h and GFS.  The files output to Credit/6h are 
# also stored in subdirectories dated with model initialization time in the format of YYYYMMDDHH.  These files 
# have the following format, where the dates labeled are lead time, valid year, month, and day, and valid hour, 
# minute, and second:
#
# * point_stat_Credit_surface_HHMMSSL_YYYYMMDD_HHMMSSV.stat
#
# The files output to the GFS directory are also stored in subdirectories dated with model 
# initialization time in the format of YYYYMMDDHH.  These files have the same format as above where
# the dates labeled are lead time, valid year, month, and day, and valid hour, minute, and second:
#
# * point_stat_GFS_surface_HHMMSSL_YYYYMMDD_HHMMSSV.stat
# * point_stat_GFS_upper_air_HHMMSSL_YYYYMMDD_HHMMSSV.stat
#
# The reformatted directory contains the reformatted output from StatAnalysis that is used in plotting.
# There is one subdirectory (6h) that contains 2 files:
#
# * reformat_CNT_6h.data
# * reformat_CTS_6h.data
#
# The StatAnalysis directory contains 1 subdirectory (6h).  Inside that directory are
# 6 output files:
#
# * Credit_GDAS_2025092400_2025092406_allleads_all_stations_allValidHours_CNT.stat
# * Credit_GDAS_2025092400_2025092406_allleads_all_stations_allValidHours_CTS.stat
# * Credit_GDAS_2025092400_2025092406_allleads_all_stations_hourly_VCNT.stat
# * GFS_GDAS_2025092400_2025092406_allleads_all_stations_allValidHours_CNT.stat
# * GFS_GDAS_2025092400_2025092406_allleads_all_stations_allValidHours_CTS.stat
# * GFS_GDAS_2025092400_2025092406_allleads_all_stations_hourly_VCNT.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * DataIngestToolUseCase
#   * PointStatToolUseCase
#   * StatAnalysisToolUseCase
#   * RALAppUseCase
#   * GRIB2FileUseCase
#   * NetCDFFileUseCase
#   * METdataioUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-PointStat_fcstCredit_GFS_obsGDAS_6hrRealtime.png'
