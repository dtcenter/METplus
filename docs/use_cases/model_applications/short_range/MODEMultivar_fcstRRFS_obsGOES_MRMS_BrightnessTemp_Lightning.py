"""
MODEMultivar: Create objects of brightness temps and radar reflectivity  
=======================================================================

model_applications/
short_range/
MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning.conf

"""

##############################################################################
# .. contents::
#	:depth: 1
#	:local:
#	:backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# This use case identifies convective objects, which are defined by
# the intersection of: 1) satellite infrared brightness temperature < 235 K and 
# 2) radar reflectivity > 40 dBZ.
# Satellite brightness temperatures are used in conjunction with radar reflectivity 
# to capture both the cloud top (satellite) and in-cloud (radar) characteristics. 
# Convective objects are also defined as lightning thresholds exceeding the 10th percentile. 
# A percentile threshold is used for lightning data as RRFS lightning has units 
# which are “non-dimensional” and therefore cannot be directly compared to the
# Geostationary Lightning Mapper. 

##############################################################################
# Version Added
# -------------
#
# METplus Version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** Rapid Refresh Forecast System (RRFS) 3km resolution, 
# channel 13 brightness temperature,
# composite reflectivity, and lightning strike density
#
# **Observation:** Geostationary Operational Environmental Satellites (GOES) 3km resolution, 
# channel 13 brightness temperature; 
# Multi-radar Multi-sensor (MRMS) 3km resolution, composite reflectivity; 
# GOES Global Lightning Mapper (GLM) 3km resolution, flash_extent_density
# 
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be found in a sample data 
# tarball. Each use case category will have one or more sample data tarballs. It is only 
# necessary to download the tarball with the use case’s dataset and not the entire 
# collection of sample data. Click here to access the METplus releases page and download 
# sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will set the value of 
# INPUT_BASE. See :ref:`running-metplus` for more information.

##############################################################################
# METplus Components
# ------------------
#
# The only tool this use case calls is MODE, which will identify super-objects
# by intersection of the multiple variable fields.
# 

##############################################################################
# METplus Workflow
# ----------------
#
# | **Beginning Time (INIT_BEG):** 2024-01-09 05:00 UTC
# | **End Time (INIT_END):** 2024-01-09 05:00 UTC
# | **Increment between beginning and end times (VALID_INCREMENT):** 1 Hour
# | **Sequence of forecast leads to process (LEAD_SEQ):** 9,10
#
# This use case runs twice, once for each forecast lead time provided. It 
# creates objects valid at 14UTC and 15UTC from 09 January 2024 are compared to 
# the 9h and 10h forecasts initialized at 05UTC on 9 January 2024.
# Convective objects are identified with thresholds of
# satellite brightness temperature < 235 K and radar reflectivity > 40 dBZ, 
# or lightning > 10th percentile.
# In this use case, MODE super-object intensity statistics are output for both 
# radar reflectivity and lightning. Using the MODE_MULTIVAR_INTENSITY_FLAG, 
# users can control for which variables super object intensity statistics will be output. 
# If all are set to False, then no intensity information will be output
# and only statistics relative to the super-object geometry will be available.



##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, i.e.
# parm/use_cases/model_applications/short_range/MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning.conf

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
# .. dropdown:: MODEConfig_wrapped
#
#  .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use any Python Embedding.

##############################################################################
# Python Scripting
# ----------------
#
# This use case does not use any Python Scripting.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/short_range/MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning/f??,
# where the '??' characters will reflect the two forecast leads (09 and 10).
# Each of these directories will contain the following files with their appropriate
# verification times::
#
#  * mode_Fcst_LTNG_entireatmosphere_all_all_Obs_flash_extent_density_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_cts.txt
#  * mode_Fcst_LTNG_entireatmosphere_all_all_Obs_flash_extent_density_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_obj.nc
#  * mode_Fcst_LTNG_entireatmosphere_all_all_Obs_flash_extent_density_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_obj.txt
#  * mode_Fcst_LTNG_entireatmosphere_all_all_Obs_flash_extent_density_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A.ps
#  * mode_Fcst_REFC_entireatmosphere_consideredasinglelayer_all_all_Obs_MergedReflectivityQCComposite_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_cts.txt
#  * mode_Fcst_REFC_entireatmosphere_consideredasinglelayer_all_all_Obs_MergedReflectivityQCComposite_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_obj.nc
#  * mode_Fcst_REFC_entireatmosphere_consideredasinglelayer_all_all_Obs_MergedReflectivityQCComposite_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A_obj.txt
#  * mode_Fcst_REFC_entireatmosphere_consideredasinglelayer_all_all_Obs_MergedReflectivityQCComposite_all_all_RRFS_or_ANALYSIS_090000L_20240109_140000V_000000A.ps

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase 
#   * ShortRangeAppUseCase
#   * NetCDFFileUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.png'
#
