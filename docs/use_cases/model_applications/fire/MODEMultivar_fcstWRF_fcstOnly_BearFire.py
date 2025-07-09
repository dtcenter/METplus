"""
MODEMultivar: Create objects of Relative Humidity and Wind Speed using the Red Flag Criteria 
============================================================================================

model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire.conf

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
# This use case runs Multivatiate MODE using the red flag criteria for fire weather 
# (relative humidity less than 15% and wind speed greater than 25 miles per hour).
# The purpose is to identify areas in the model that meet the red flag criteria for
# fire weather forecasting.  Observations are not used in this use case.  Rather, the 
# model is used as both the forecast and observations (since Multivariate MODE requires 
# both to run).  As such, matched pair output is not useful for this use case.  Rather
# simple and cluster object statistics on the area meeting the Red Flag criteria are 
# the goal of this use case.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.2

##############################################################################
# Datasets
# --------
#
# **Forecast:** WRF Fire
#
# **Observation:** None
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
# This use case calls Multivariate MODE once.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2020-09-08 2000 UTC
#
# **End time (VALID_END):** 2020-09-08 2045 UTC
#
# **Increment between beginning and end times (VALID_INCREMENT):** 900 seconds (15 min)
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# With an increment of 15 minutes, one forecast initialization time is processed for 3
# different valid times resulting in 3 runs of Multivariate MODE.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire.conf

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
# .. dropdown:: MTDConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case reads the input model data usoing a python embedding script.  Although
# the WRF subgrid files are able to be read directly in MET, here we use the Python
# embedding script to compute Relative Humidity from Specific Humidity, and wind 
# speed from the U and V wind components.
#
# .. dropdown:: read_wrfout_fire_rh_wind.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire/read_wrfout_fire_rh_wind.py

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/fire/MODEMultivar_fcstWRF_fcstOnly_BearFire
# and will contain the following files::
#
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_010000L_20200908_200000V_000000A_cts.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_010000L_20200908_200000V_000000A_obj.nc
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_010000L_20200908_200000V_000000A_obj.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_010000L_20200908_200000V_000000A.ps
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_011500L_20200908_201500V_000000A_cts.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_011500L_20200908_201500V_000000A_obj.nc
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_011500L_20200908_201500V_000000A_obj.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_011500L_20200908_201500V_000000A.ps
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_013000L_20200908_203000V_000000A_cts.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_013000L_20200908_203000V_000000A_obj.nc
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_013000L_20200908_203000V_000000A_obj.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_013000L_20200908_203000V_000000A.ps
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_014500L_20200908_204500V_000000A_cts.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_014500L_20200908_204500V_000000A_obj.nc
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_014500L_20200908_204500V_000000A_obj.txt
#  * mode_Fcst_Super_LO_Obs_Super_LO_WRF_Fire_Bear_014500L_20200908_204500V_000000A.ps
#
# The cts files contain contingency table statistics while the obj.txt files contain the object 
# attributes.  The postscript output shows images of the objects.  For the netCDF file, 18 variable 
# fields are present (not including the lat/lon fields). Those variables are::
#
#  * fcst_raw(lat, lon)
#  * fcst_obj_raw(lat, lon)
#  * fcst_obj_id(lat, lon)
#  * fcst_clus_id(lat, lon)
#  * obs_raw(lat, lon)
#  * obs_obj_raw(lat, lon)
#  * obs_obj_id(lat, lon)
#  * obs_clus_id(lat, lon)
#  * int fcst_conv_radius ;
#  * obs_conv_radius ;
#  * fcst_conv_threshold(fcst_thresh_length) ;
#  * obs_conv_threshold(obs_thresh_length) ;
#  * fcst_variable(fcst_variable_length) ;
#  * obs_variable(obs_variable_length) ;
#  * fcst_level(fcst_level_length) ;
#  * obs_level(obs_level_length) ;
#  * fcst_units(fcst_units_length) ;
#  * obs_units(obs_units_length)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase
#   * PythonEmbeddingFileUseCase
#   * FireAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-MODEMultivar_fcstWRF_fcstOnly_BearFire.png'
