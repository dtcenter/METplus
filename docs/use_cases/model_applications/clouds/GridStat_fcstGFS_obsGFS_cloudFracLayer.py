"""
Grid-Stat, MODE, Stat-Analysis, UserScript, Gen-Vx-Mask: GFS Cloud Statistics by Type
=====================================================================================

model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer.conf

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
# This use case evaluates clouds classified into low, mid, and high levels.  The
# evaluation covers multiple types of statistics including contingency table
# statistics, neighborhood statistics, distance maps, and an object based evaluation.
# Additionally, plots are created to demonstrate how to reformat and visualize GSS
# CSI and frequency bias from the command line.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast**: GFS 0.25 degree model
#
# **Observation**: GFS Analysis
#
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls GenVxMask once, GridStat once, MODE three times, StatAnalysis
# once, and UserScript twice.  Additionally, METcalcpy, METplotpy, and METdataio are 
# required to run this use case.  The METcalcpy scripts accessed include the following:
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
# **Beginning time (INIT_BEG):** 2024030700
#
# **End time (INIT_END):** 2024030700
#
# **Increment between beginning and end times (INIT_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0, 6, 12, 18
#
# GenVxMask is run once.  The Grid-Stat, MODE, and Stat-Analysis tools run for each time. 
# This example loops by model initialization time.  It processes one initialization time and 
# three lead times for each for a total of 3 valid times, listed below.
#
# | **Valid:** 2024-03-07_00Z
# | **Forecast lead:** 00
#
# | **Valid:** 2024-03-07_06Z
# | **Forecast lead:** 06
#
# | **Init:** 2024-03-07_12Z
# | **Forecast lead:** 12
#
# | **Init:** 2024-03-07_18Z
# | **Forecast lead:** 18
#
# Both UserScripts are each run once.  The first UserScript reformats the GridStat CTS
# output so that it can be used to create a plot.  The second UserScript creates three
# plots.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer.conf

##############################################################################
# MET Configuration
# ---------------------
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
# .. dropdown:: MODEConfig_wrapped
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped
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
# There are two python scripts used in this use case.  The first is 
# reformat_CTS_linetype.py.  This script takes the aggregated output CTS linetype
# from Stat Analysis and reformats it so that the data can be plotted.  The script
# takes an input .yaml file, reformat_CTS.yaml.  Environment variables in the yaml
# file are specified in the [user_env_vars] section of the GridStat_fcstGFS_obsGFS_clouds.conf
# configuration file.
#
# The second python script is plot_line_stats.py.  This script creates line plots for low
# and high clouds for GSS, CSI, and Frequency bias with lead time.  Input variables to both 
# scripts are set in the [user_env_vars] section of the .conf file.
#
# .. dropdown:: parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer/reformat_CTS_linetype.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer/reformat_CTS_linetype.py
#
# .. dropdown:: parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer/plot_line_stats.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer/plot_line_stats.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/clouds/GridStat_fcstGFS_obsGFS_cloudFracLayer.  There will 
# be 6 directories with output data, masks, grid_stat, mode, stat_analysis, reformatted, and 
# plots.  The mask directory will contain an input mask and the following output mask file::
#
# * West_Pacific.nc
#
# The grid_stat directory will contain 4 .stat file sand 4 .nc files::
#
# * grid_stat_GFS_cloud_000000L_20240307_000000V_pairs.nc
# * grid_stat_GFS_cloud_000000L_20240307_000000V.stat
# * grid_stat_GFS_cloud_060000L_20240307_060000V_pairs.nc
# * grid_stat_GFS_cloud_060000L_20240307_060000V.stat
# * grid_stat_GFS_cloud_120000L_20240307_120000V_pairs.nc
# * grid_stat_GFS_cloud_120000L_20240307_120000V.stat
# * grid_stat_GFS_cloud_180000L_20240307_180000V_pairs.nc
# * grid_stat_GFS_cloud_180000L_20240307_180000V.stat
#
# The mode directory will contain the following files::
#
# * mode_GFS_high_cloud_000000L_20240307_000000V_000000A_cts.txt
# * mode_GFS_high_cloud_000000L_20240307_000000V_000000A_obj.nc
# * mode_GFS_high_cloud_000000L_20240307_000000V_000000A_obj.txt
# * mode_GFS_high_cloud_000000L_20240307_000000V_000000A.ps
# * mode_GFS_high_cloud_060000L_20240307_060000V_000000A_cts.txt
# * mode_GFS_high_cloud_060000L_20240307_060000V_000000A_obj.nc
# * mode_GFS_high_cloud_060000L_20240307_060000V_000000A_obj.txt
# * mode_GFS_high_cloud_060000L_20240307_060000V_000000A.ps
# * mode_GFS_high_cloud_120000L_20240307_120000V_000000A_cts.txt
# * mode_GFS_high_cloud_120000L_20240307_120000V_000000A_obj.nc
# * mode_GFS_high_cloud_120000L_20240307_120000V_000000A_obj.txt
# * mode_GFS_high_cloud_120000L_20240307_120000V_000000A.ps
# * mode_GFS_high_cloud_180000L_20240307_180000V_000000A_cts.txt
# * mode_GFS_high_cloud_180000L_20240307_180000V_000000A_obj.nc
# * mode_GFS_high_cloud_180000L_20240307_180000V_000000A_obj.txt
# * mode_GFS_high_cloud_180000L_20240307_180000V_000000A.ps
# * mode_GFS_low_cloud_000000L_20240307_000000V_000000A_cts.txt
# * mode_GFS_low_cloud_000000L_20240307_000000V_000000A_obj.nc
# * mode_GFS_low_cloud_000000L_20240307_000000V_000000A_obj.txt
# * mode_GFS_low_cloud_000000L_20240307_000000V_000000A.ps
# * mode_GFS_low_cloud_060000L_20240307_060000V_000000A_cts.txt
# * mode_GFS_low_cloud_060000L_20240307_060000V_000000A_obj.nc
# * mode_GFS_low_cloud_060000L_20240307_060000V_000000A_obj.txt
# * mode_GFS_low_cloud_060000L_20240307_060000V_000000A.ps
# * mode_GFS_low_cloud_120000L_20240307_120000V_000000A_cts.txt
# * mode_GFS_low_cloud_120000L_20240307_120000V_000000A_obj.nc
# * mode_GFS_low_cloud_120000L_20240307_120000V_000000A_obj.txt
# * mode_GFS_low_cloud_120000L_20240307_120000V_000000A.ps
# * mode_GFS_low_cloud_180000L_20240307_180000V_000000A_cts.txt
# * mode_GFS_low_cloud_180000L_20240307_180000V_000000A_obj.nc
# * mode_GFS_low_cloud_180000L_20240307_180000V_000000A_obj.txt
# * mode_GFS_low_cloud_180000L_20240307_180000V_000000A.ps
# * mode_GFS_mid_cloud_000000L_20240307_000000V_000000A_cts.txt
# * mode_GFS_mid_cloud_000000L_20240307_000000V_000000A_obj.nc
# * mode_GFS_mid_cloud_000000L_20240307_000000V_000000A_obj.txt
# * mode_GFS_mid_cloud_000000L_20240307_000000V_000000A.ps
# * mode_GFS_mid_cloud_060000L_20240307_060000V_000000A_cts.txt
# * mode_GFS_mid_cloud_060000L_20240307_060000V_000000A_obj.nc
# * mode_GFS_mid_cloud_060000L_20240307_060000V_000000A_obj.txt
# * mode_GFS_mid_cloud_060000L_20240307_060000V_000000A.ps
# * mode_GFS_mid_cloud_120000L_20240307_120000V_000000A_cts.txt
# * mode_GFS_mid_cloud_120000L_20240307_120000V_000000A_obj.nc
# * mode_GFS_mid_cloud_120000L_20240307_120000V_000000A_obj.txt
# * mode_GFS_mid_cloud_120000L_20240307_120000V_000000A.ps
# * mode_GFS_mid_cloud_180000L_20240307_180000V_000000A_cts.txt
# * mode_GFS_mid_cloud_180000L_20240307_180000V_000000A_obj.nc
# * mode_GFS_mid_cloud_180000L_20240307_180000V_000000A_obj.txt
# * mode_GFS_mid_cloud_180000L_20240307_180000V_000000A.ps
#
# The stat_analysis directory will contain the following files::
#
# * stat_analysis_GFS_ANAL_West_Pacific_000000L_CTS.stat
# * stat_analysis_GFS_ANAL_West_Pacific_060000L_CTS.stat
# * stat_analysis_GFS_ANAL_West_Pacific_120000L_CTS.stat
# * stat_analysis_GFS_ANAL_West_Pacific_180000L_CTS.stat
#
# The reformatted directory will contain the following files::
#
# * reformat_CTS.data
#
# The plots directory will contain the following files::
#
# * High_low_cloud_CSI.png
# * High_low_cloud_FBIAS.png
# * High_low_cloud_GSS.png
#
# For the Grid-Stat netCDF files, 6 variable fields are present (not including the lat/lon 
# fields).  Those variables are::
#
# * FCST_DMAP_ge50_LCDC_L0_FULL(lat, lon)
# * OBS_DMAP_ge50_LCDC_L0_FULL(lat, lon)
# * FCST_DMAP_ge50_MCDC_L0_FULL(lat, lon)
# * OBS_DMAP_ge50_MCDC_L0_FULL(lat, lon)
# * FCST_DMAP_ge50_HCDC_L0_FULL(lat, lon)
# * OBS_DMAP_ge50_HCDC_L0_FULL(lat, lon)
#
# For the MODE netCDF files, 18 variable fields are present (not including the lat/lon fields). 
# Those variables are::
#
# * fcst_raw(lat, lon)
# * fcst_obj_raw(lat, lon)
# * fcst_obj_id(lat, lon)
# * fcst_clus_id(lat, lon)
# * obs_raw(lat, lon)
# * obs_obj_raw(lat, lon)
# * obs_obj_id(lat, lon)
# * obs_clus_id(lat, lon)
# * fcst_conv_radius
# * obs_conv_radius
# * fcst_conv_threshold(fcst_thresh_length)
# * obs_conv_threshold(obs_thresh_length)
# * fcst_variable(fcst_variable_length)
# * obs_variable(obs_variable_length)
# * fcst_level(fcst_level_length)
# * obs_level(obs_level_length)
# * fcst_units(fcst_units_length)
# * obs_units(obs_units_length)

##############################################################################
# Keywords
# ---------
#
# .. note::
#
#   * GridStatToolUseCase
#   * MODEToolUseCase
#   * StatAnalysisToolUseCase
#   * UserScriptUseCase
#   * ShortRangeAppUseCase
#   * METdataioUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/clouds-GridStat_fcstGFS_obsGFS_cloudFracLayer.png'
