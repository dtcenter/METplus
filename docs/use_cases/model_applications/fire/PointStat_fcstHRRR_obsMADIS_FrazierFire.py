"""
PointStat: Use Point-Stat to Verify Points that meet the Red Flag Criteria
==========================================================================

model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire.py

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
# This use case evaluates the HRRR model using the Red Flag Criteria for Fire 
# weather.  The purpose is to identify points that meet the Red Flag Criteria.
# The evaluation is done two ways.  The first is to identify areas that match the
# relative humidity, wind speed, and wind gust criteria separately.  The second
# way takes a relative humidity mask and finds the points that meet the wind 
# criteria inside each mask.  This way we can identify the points that meet
# both the relative humidity and wind speed/wind gust criteria.

##############################################################################
# Version Added
# -------------
#
# METplus version 13.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** HRRR
#
# **Observation:** MADIS
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
#
# The MADIS observations are downloaded automatically. Make sure you have an internet 
# connection.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls Data-Ingest once and Gen-Vx-Mask, Point-Stat, and Stat-Analysis 
# 3 times.  It also calls User-Script twice.  Additionally, METcalcpy, METplotpy, and 
# METdataio are required to run this use case.  The METcalcpy scripts accessed include 
# the following:
#
# * metcalcpy/util/read_env_vars_in_config.py
#
# The METplopty scrips accessed include the following:
#
# * metplotpy/plots/performance_diagram/performance_diagram.py
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
# **Beginning time (VALID_BEG):** 2025-05-28 18 UTC
#
# **End time (VALID_END):** 2025-05-29 18 UTC
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (INIT_SEQ):** 0, 6, 12, 18
#
# **Forecast lead min and max to process:** 6 to 24 hours
#
# The call to DataIngest, the second 2 calls to Gen-Vx-Mask, and the 3 calls to Point-Stat 
# are processed at 6 hourly increments for the 0, 6, 12, and 18 hour model initializations 
# using lead times between 6 and 24 hours, for a total of 20 runs.  The first call to 
# Gen-Vx-Mask is run once to create the mask for the Hanford CWA domain.
#
# The first call of Point-Stat processes statistics for each variable (relative humidity,
# wind speed, and wind gusts) individually.  The second call uses a data mask of relative 
# humidity less than 15% and calculates statistics for wind speed and wind gusts.  This
# enables the identification of points that meet both the wind and relative humidity threshold
# for fire weather.  Similarly, the third call to Point-Stat uses a data mask of relative 
# humidity less than 10% and calculates statistics for wind speed and wind gusts.
#
# Stat-Analysis is called once for the entire time period for each of the 3 calls.  Each of the 
# 3 runs aggregates statistics for the different runs of Point-Stat above.  Additionally, both
# of the 2 User-Scripts are also called once.  The first User-Script reformats data, while the 
# second creates the performance diagrams.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire.conf

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
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped
#
# .. dropdown:: StatAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls a Python embedding script to read the MADIS data.  While
# the MADIS data would run through MET after calling madis2nc, in this case, 
# the Python embedding script is used to calculate relative humidity, which is 
# needed for the Red Flag Criteria but didn't exist in the MADIS data.  The script
# is /parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire/convert_madis_sfc_rh_wind.py
#
# .. dropdown:: convert_madis_sfc_rh_wind.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire/convert_madis_sfc_rh_wind.py

##############################################################################
# User Scripting
# --------------
#
# There are two Python scripts used in this use case, called using the "UserScript" keyword
# in the METplus wrappers PROCESS_LIST configuration item.  These scripts provide an
# interface to the functions in the METdataio, METcalcpy, and METplotpy Python modules
# of METplus.  The functions used in these scripts demonstrate reformatting
# aggregated StatAnalysis output to meet the format required by METcalcpy and METplotpy,
# and then plotting that reformatted output using functions from METcalcpy and METplotpy.  
# 
# The first Python script is called reformat_CTS_linetype.py.  This script takes the aggregated 
# output CTS linetype from Stat Analysis and reformats it so that the data can be plotted.  
# The script takes an input .yaml file, reformat_CTS.yaml.  Environment variables in the yaml
# file are specified in the [user_env_vars] section of the 
# PointStat_fcstHRRR_obsMADIS_FrazierFire.conf METplus configuration file.
#
# The second Python script is plot_performance_diagram.py.  This script creates performance
# diagrams for wind and relative humidity.  Some input variables to the script are set in the
# [user_env_vars] section of the PointStat_fcstHRRR_obsMADIS_FrazierFire.conf METplus 
# configuration file.
#
# For more information about YAML configuration options for the Performance Diagram plots, see the METplotpy
# `Performance Diagram plot documentation <https://metplus.readthedocs.io/projects/metplotpy/en/latest/Users_Guide/performance_diagram.html>`_.
#
# Both Python scripts are located at::
#
#   parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire
#
# .. dropdown:: reformat_linetype.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire/reformat_linetype.py
#
# .. dropdown:: plot_performance_diagram.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire/plot_performance_diagram.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/fire/PointStat_fcstHRRR_obsMADIS_FrazierFire.  There will be
# 6 directories of output, data_ingest, VxMasks, PointStat, StatAnalysis, reformatted, and plots.  
# The data_ingest directory contains the observation data that has been downloaded and will 
# contain one subdirectory, MADIS/metar. That directory will contain a number of files::
#
#  * 20250528_1800.nc
#  * 20250529_0000.nc
#  * 20250529_0600.nc
#  * 20250529_1200.nc
#  * 20250529_1800.nc
#  * 20250530_0000.nc
#  * 20250530_0600.nc
#  * 20250530_1200.nc
#  * 20250530_1800.nc 
#
# The output from Gen-Vx-Mask will be in the VxMasks directory.  The VxMasks directory contains 
# the Hanford CWA mask::
#
#  * Hanford_CWA_mask.nc
#
# It also contains the relative humidity masks using thresholds of 10% and 15% these are in directories
# RH_10 and RH_15.  There is one mask for each time run, with the following format::
# 
#  * RH_mask_YYYYMMDDHH_fHHH.nc
# 
# Where the YYYYMMDDHH is the year, month, day, and hour of the model initialization time, and HHH is the 
# forecast lead time.  There should be 20 files in both the RH_10 and RH_15 directories.
#
# The output from Point-Stat will contain 3 directories, Individual_Variables, RH_10, and RH_16.  Each 
# of these directories will contain sub-directories labeled with the model initializaiton time in 
# YYYYMMDDHH.  There should be 20 files total output for each Point-Stat directory.  The files have 
# the following format::
#
#  * point_stat_HHMMSSL_YYYYMMDD_HHMMSSV.stat
#
# Where HHMMSSL is the hour, minute, and second of the forecast lead time, YYYYMMDD is the valid year, month,
# and day, and HHMMSSV is the hour, minute, and second of the valid time.
#
# The output from Stat-Analysis has the same three directories as are output from Point-Stat, 
# Individual_Variables, RH_10, and RH_15.  The Individual_Variables directory contains 1 file::
#
#  * HRRR_MADIS_2025052818_2025052918_separate_leads_allValidHours_CTS.stat
#
# The RH_10 directory contains 3 files::
#
#  * HRRR_MADIS_RH10_wind15_gust25_2025052818_2025052918_all_leads_allValidHours_CTS.stat
#  * HRRR_MADIS_RH10_wind15_gust25_2025052818_2025052918_all_leads_separateValidHours_CTS.stat
#  * HRRR_MADIS_RH10_wind15_gust25_2025052818_2025052918_separate_leads_allValidHours_CTS.stat
#
# The RH_15 directory also contains 3 files::
#
#  * HRRR_MADIS_RH15_wind25_gust35_2025052818_2025052918_all_leads_allValidHours_CTS.stat
#  * HRRR_MADIS_RH15_wind25_gust35_2025052818_2025052918_all_leads_separateValidHours_CTS.stat
#  * HRRR_MADIS_RH15_wind25_gust35_2025052818_2025052918_separate_leads_allValidHours_CTS.stat
#
# Output from the 2 UserScripts are in 2 directories, reformatted and plots.  The reformatted 
# directory contains 1 file::
#
#  * reformat_CTS_leads.data
# 
# The plots directory contains 2 plots::
#
#  * performance_diagram_rh_lead.png
#  * performance_diagram_wind_lead.png


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * FireAppUseCase
#   * DataIngestUseCase
#   * PointStatToolUseCase
#   * GenVxMaskToolUseCase
#   * StatAnalysisToolUseCase
#   * UserScriptUseCase
#   * METdataioUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-PointStat_fcstHRRR_obsMADIS_FrazierFire.png'
