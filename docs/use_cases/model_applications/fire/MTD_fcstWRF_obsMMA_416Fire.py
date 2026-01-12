"""
MTD: Use MTD to compute fire area and spread
============================================

model_applications/fire/MTD_fcstWRF_obsMMA_416Fire.conf

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
# This case uses MODE-Time-Domain to create objects using fire area and 
# Multimission Aircraft fire perimeters for the 416 Fire.  MTD is used specifically 
# to create objects over time that provide information on fire area and spread over 
# time. 

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** WRF Fire
#
# **Observation:** Multimission Aircraft Fire Perimeter
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
# This use case calls Gen-Vx-Mask and MODE-Time-Domain once.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2018-06-01 16 UTC
#
# **End time (INIT_END):** 2018-06-01 16 UTC
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 hour
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1 - 33 hours with hourly increments
#
# With an increment of 1 hour, one forecast initialization time is processed to result in 32
# runs of Gen-Vx-Mask, once for each lead time.  The runs of Gen-Vx-Mask create netCDF files 
# from the interpolated fire perimeters that are used as input observations to Mode-Time-Domain.
# Then, Mode-Time-Domain is run once which uses all model and observation times as input.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416Fire.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416Fire.conf

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
#   .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416Fire.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/fire/MTD_fcstWRF_obsMMA_416Fire.  The output from 
# Gen-Vx-Mask will be in the GenVxMask/Interpolated_perimeters directory and will 
# contain one mask for each time in the following format::
#
#  * 416_Fire_Interpolated_YYYYMMDDHH.nc
#
# Here, YYYYMMDDHH is the year, month, day, and hour of the interpolated permiters.  The 
# output from MTD and will contain the following files::
#
#  * mtd_WRF_Fire_416_20180601_170000V_2d.txt
#  * mtd_WRF_Fire_416_20180601_170000V_3d_pair_cluster.txt
#  * mtd_WRF_Fire_416_20180601_170000V_3d_pair_simple.txt
#  * mtd_WRF_Fire_416_20180601_170000V_3d_single_cluster.txt
#  * mtd_WRF_Fire_416_20180601_170000V_3d_single_simple.txt
#  * mtd_WRF_Fire_416_20180601_170000V_obj.nc
#
# The 2d file contains object-based statistics for the objects at different time steps.  
# The 3d files contains the object based statistics over time for single and paired, simple and 
# cluster objects.  For the netCDF file, six variable fields are present (not including the 
# lat/lon fields). Those variables are::
#
#  * fcst_raw(time, lat, lon)
#  * obs_raw(time, lat, lon)
#  * fcst_object_id(time, lat, lon)
#  * obs_object_id(time, lat, lon)
#  * fcst_cluster_id(time, lat, lon)
#  * obs_cluster_id(time, lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MTDToolUseCase
#   * GenVxMaskToolUseCase
#   * NetCDFFileUseCase
#   * FireAppUseCase
#   * WRFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-MTD_fcstWRF_obsMMA_416Fire.png'
