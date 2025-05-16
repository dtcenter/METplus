"""
PointStat: Use Python embedding and METcalcpy to calculate and verify CTP/HI
============================================================================

model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# [UPDATE_SECTION_CONTENT]
#
# To provide statistical information on the forecast hail size compared to
# the observed hail size from MRMS MESH data. Using objects to verify hail size
# avoids the “unfair penalty” issue, where a CAM must first generate convection
# to have any chance of accurately predicting the hail size. In addition, studies
# have shown that MRMS MESH observed hail sizes do not correlate one-to-one with
# observed sizes but can only be used to group storms into general categories.
# Running MODE allows a user to do this.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# [UPDATE_SECTION_CONTENT]
# **Forecast:** Global Forecast System (GFS) 25km resolution, 2m temperature
#
# **Observation:** Upper air radiosonde observations from the 
# Global Data Assimilation System (GDAS) in PREPBUFR format.
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
# This use cases uses PB2NC, GenVxMask, and PointStat along with Python embedding
# and user scripting. For each call to PointStat, Python embedding is used to calculate 
# the CTP and Humidity Index diagnostics and pass those diagnostics to PointStat 
# for verification.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2020-08-05 12:00
#
# **End time (VALID_END):** 2020-08-05 12:00
#
# **Increment between beginning and end times (VALID_INCREMENT):** 12 Hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 60
#
# Only a single time is used to demonstrate the workflow for this use case.
# For each time, PB2NC is used to convert the upper-air radiosonde observations from
# PREPBUFR format to NetCDF. Then, a Python user script is used to create a text file
# with the locations of upper-air sites to use for verification. This text file
# is used by GenVxMask to mask out any points in the forecast outside of a user-defined
# radius around each upper-air site. Then, PointStat is called which uses Python embedding
# to compute diagnostics using METcalcpy to use for verification. Point stat is used
# to produce matched pairs (forecast/observation pairs) of both diagnostics for
# downstream land-atmosphere process evaluation.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI.conf

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

##############################################################################
# Python Embedding
# ----------------
#
# This use case has four Python embedding scripts, one for each diagnostic (CTP/HI)
# for both the forecast and observations
#
# * pyembed_ctp_fcst_HR1.py
# * pyembed_ctp_obs_gdas.py
# * pyembed_hi_fcst_HR1.py
# * pyembed_hi_obs_gdas.py
#
# The forecast Python embedding scripts require the data variable names and the path
# to the mask file created with GenVxMask, while the observation Python embedding scripts
# only require the output file from PB2NC.
# 
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_ctp_fcst_HR1.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_ctp_fcst_HR1.py
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_ctp_obs_gdas.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_ctp_obs_gdas.py
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_hi_fcst_HR1.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_hi_fcst_HR1.py
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_hi_obs_gdas.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_hi_obs_gdas.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus,
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

##############################################################################
# User Scripting
# --------------
#
# This use case uses a Python script to create an input file for GenVxMask to use
# based on the upper-air sites the user wishes to include. In the METplus configuration file,
# a user can set the USER_SCRIPT_SITES_TO_INCLUDE configuration item. This is a comma-separated
# string of integers representing the first digit in the WMO station ID of upper-air sites to
# include. For example, in the United States many of the upper-air sites begin with "7". If a 
# user wants to use only U.S. sites, they would set this just to 7. To include other countries,
# include more digits. By default, this is set to only 7 in order to decrease the total run time of
# the use case for testing and demonstration.
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/create_raob_mask_file.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI/create_raob_mask_file.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/land_surface/PointStat_fcstUFS_obsGDAS_CTP_HI 
# and will contain the following files::
#
#  * CTP/point_stat_600000L_20200805_120000V_mpr.txt
#  * CTP/point_stat_600000L_20200805_120000V.stat
#  * HI/point_stat_600000L_20200805_120000V_mpr.txt
#  * HI/point_stat_600000L_20200805_120000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * METcalcpyUseCase
#   * LandSurfaceAppUseCase
#   * UserScriptUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/land_surface-PointStat_fcstUFS_obsGDAS_CTP_HI.png'
