"""
PointStat: Python embedding for ASOS/METAR cloud obs to verify GFS
==================================================================

model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight.conf

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
# This use case is intended to demonstrate using readily available ASOS/METAR
# cloud observations of cloud fraction and cloud base height (ceiling) to verify
# GFS forecasts of low cloud height and multiple cloud layer fractions. Python 
# embedding is used to serve the observations from their NetCDF file format to 
# PointStat. The use case also demonstrates interpolating the pressure of the
# low cloud altitude from GFS to a height value using the geopotential height
# field in order to compare with the observations.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# **Forecast:** Global Forecast System (GFS) 0.25 degree global grid
#               Low cloud fraction
#               Middle cloud fraction
#               High cloud fraction
#               Low cloud altitude (pressure)
#               Geopotential height
#
# **Observation:** Global METAR reports from NCAR RDA
#                  Low cloud area fraction
#                  Middle cloud area fraction
#                  High cloud area fraction
#                  Low cloud base altitude
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
# The only tool this use case calls is PointStat. Within PointStat a Python 
# script is used for ingesting forecast data only for verifying the low cloud altitude, and
# also for ingesting the observations for all variables once for each valid time requested.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2024-03-07 00:00 UTC
#
# **End time (INIT_END):** 2024-03-07 00:00 UTC
#
# **Increment between beginning and end times (INIT_INCREMENT):** None
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 6
#
# Only the 6-h forecast from the 00 UTC forecast on 20240307 is verified.
# PointStat computes contingency table counts (CTC), 
# contingency table statistics (CTS), and continuous statistics (CNT)
# for the data variables being verified.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight.conf

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
# This use case calls a Python embedding script to read the observations for all variables,
# and a Python embedding script to read the forecast only when verifying the low cloud
# base altitude (ceiling) forecasts. The observation Python script is read_asos_ceil.py,
# which reads NetCDF formatted METAR observations and prepares the data in a format that MET
# expects. The forecast Python script for low cloud base altitude is read_interp_gfs_025.py.
# This script opens a GRIB2 formatted GFS file and reads in the 3D geopotential height field,
# the 2D low cloud base altitude (pressure) field, and the 2D orography (surface topography)
# field. It uses 1-D logarithmic interpolation from MetPy to interpolate the geopotential height
# field (converted to meters AGL from meters MSL using the orography field) to the height
# pressure altitude of the low cloud base altitude field from the model. This interpolation is done
# by a function contained in a third Python embedding file, gfs_025_interp_funcs.py. Because the Python
# multiprocessing module is used to parallelize the interpolation at each grid cell, this function
# had to exist in a separate file that read_interp_gfs_025.py imports from. The gridded low cloud
# base altitude field in meters AGL is passed back to PointStat for comparison with the obs.
# The location of each script is
#
# .. dropdown:: parm/use_cases/model_applications/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight/read_asos_ceil.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight/read_asos_ceil.py
#
# .. dropdown:: parm/use_cases/model_applications/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight/read_interp_gfs_025.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight/read_interp_gfs_025.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

##############################################################################
# User Scripting
# --------------
#
# This use case does not use additional scripts.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/clouds/PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight 
# and will contain the following files::
#
#  * point_stat_060000L_20240307_060000V.stat
#
# organized in directories for each variable being verified::
#
#  * high_cloud_area_fraction
#  * low_cloud_area_fraction
#  * middle_cloud_area_fraction
#  * low_cloud_base_altitude
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
#   * GRIB2FileUseCase
#   * CloudsAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/clouds-PointStat_fcstGFS_obsASOS_cloudFraction_cloudBaseHeight.png'
