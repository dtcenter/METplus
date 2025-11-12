"""
MODEMultivar: Create objects of Relative Humidity and Wind Speed using the Red Flag Criteria 
============================================================================================

model_applications/fire/MODEMultivar_fcstHRRR_fcstOnly_CreekFire.conf

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
# This use case runs Multivatiate MODE using relative humidity, wind speed, and wind
# gusts to identify areas that meet the Red Flag criteria for fire weather.  The
# specfic thresholds are:
#
# - relative humidity <= 10% and wind speed >= 15 mph or wind gusts >= 25 mph
# - relative humidity <= 15% and wind speed >= 25 mph or wind gusts >= 35 mph
#
# The purpose is to identify objects in the model that meet the Red Flag Criteria for 
# fire weather forecasting.  Observations are not used.  Rather, the model is used as 
# input for both the forecast and observations (since Multivariate MODE requires both 
# to run).  As such, matched object statistics are not useful for this use case.  Instead, 
#simple and cluster object statistics on the area meeting the Red Flag Criteria are the 
# goal.

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** High Resolution Rapid Refresh (HRRR) model relative humidity, wind speed, and wind gusts
#
# **Observation:** HRRR (same as forecast)
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
# This use case calls GenVxMask once and Multivariate MODE (MvMODE) twice.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2020-09-03 0000 UTC
#
# **End time (VALID_END):** 2020-09-06 0000 UTC
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (INIT_SEQ):** 0, 6, 12, 18
#
# **Forecast lead min and max to process:** 6 to 24 hours
#
# GenVxMask is run once to create a mask over the Hanford CWA.  Then, with an 
# increment of 6 hours for the 0, 6, 12, and 18 hour model initializations MvMODE is run
# using lead times between 6 and 24 hours.  This makes a total of 52 runs for each call
# of MvMODE.  The first run uses relative humidity and wind speed thresholds to identify
# objects while the second uses relative humidity and wind gust threshold to identify
# objects.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/fire/MODEMultivar_fcstHRRR_fcstOnly_CreekFire.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/MODEMultivar_fcstHRRR_fcstOnly_CreekFire.conf

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
# .. dropdown:: MODEConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case does not use any Python Scripting.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/MODEMultivar_fcstHRRR_fcstOnly_CreekFire.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/fire/MODEMultivar_fcstHRRR_fcstOnly_CreekFire.  There will
# be 3 output directories, VxMasks, mv_mode_rh_wind, and mv_mode_rh_gust.  The VxMasks 
# directory will contain one file::
#
#  * Hanford_CWA_mask.nc
# 
# The mv_mode_rh_wind directory will contain 16 output files for each timestep, 8 for relative
# humidity and 8 for wind.  The files fill have the following format::
#
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_cts.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_obj.nc
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_obj.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1.ps
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_cts.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_obj.nc
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_obj.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2.ps
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_cts.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_obj.nc
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_obj.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1.ps
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_cts.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_obj.nc
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_obj.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_Fire_Creek_rh_wind_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2.ps
#
# Here, HHMMSSL is the hour, minute, and second of the forecast lead time, YYYYMMDD is the year, month
# and day of the valid time, and HHMMSSV is the hour, minute, and second of the valid time.  R1_T1
# indicates the first convolution radius and threshold (radius of 3, threshold of <=10% for relative 
# humidity and >=15 miles per hour for wind speed).  R2_T2 is the second radius and threhsold (radius 
# of 3, threshold of <=15% for relative humidity and >=25 miles per hour for wind speed).
#
# The mv_mode_rh_gust directory also contains 16 output fiels for each timestep, 8 for relative humidity
# and 8 for wind gust.  The files have the same format as above, but the thresholds for wind gusts are
# >=25 miles per hour for R1 and >=35 miles per hour for R2.  These files have the following format::
#
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_cts.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_obj.nc
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1_obj.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R1_T1.ps
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_cts.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_obj.nc
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2_obj.txt
#  * mode_Fcst_RH_Z2_Obs_RH_Z2_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_000000A_R2_T2.ps
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_cts.txt
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_obj.nc
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1_obj.txt
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R1_T1.ps
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_cts.txt
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_obj.nc
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2_obj.txt
#  * mode_Fcst_GUST_Z10_Obs_GUST_Z10_HRRR_Fire_Creek_rh_gust_HHMMSSL_YYYYMMDD_HHMMSSV_010000A_R2_T2.ps
#
# For both directories, the cts files contain contingency table statistics while the obj.txt files contain 
# the object attributes.  The postscript output shows images of the objects.  For the netCDF file, 18 
# variable fields are present (not including the lat/lon fields). Those variables are::
#
#  * fcst_raw(lat, lon)
#  * fcst_obj_raw(lat, lon)
#  * fcst_obj_id(lat, lon)
#  * fcst_clus_id(lat, lon)
#  * obs_raw(lat, lon)
#  * obs_obj_raw(lat, lon)
#  * obs_obj_id(lat, lon)
#  * obs_clus_id(lat, lon)
#  * int fcst_conv_radius
#  * obs_conv_radius
#  * fcst_conv_threshold(fcst_thresh_length)
#  * obs_conv_threshold(obs_thresh_length)
#  * fcst_variable(fcst_variable_length)
#  * obs_variable(obs_variable_length)
#  * fcst_level(fcst_level_length)
#  * obs_level(obs_level_length)
#  * fcst_units(fcst_units_length)
#  * obs_units(obs_units_length)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase
#   * FireAppUseCase
#   * HRRRFileUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-MODEMultivar_fcstHRRR_fcstOnly_CreekFire.png'
