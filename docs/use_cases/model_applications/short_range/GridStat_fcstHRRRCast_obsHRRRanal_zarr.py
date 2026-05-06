"""
GridStat: Read Zarr Files and Compute Statistics
=================================================================

model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr.conf

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
# This use case demonstrates how to read Zarr format data from the HRRRCast
# model.  This data is read into the Grid-Stat tool, and continuous, categorical,
# and vector statistics are computed for temperature, reflectivity, and wind. 
# The purpose of this use case is to demonstrate how to use the Zarr format for
# AI models.

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0?

##############################################################################
# Datasets
# --------
#
# **Forecast:** HRRRCast
#
# **Observation:** HRRR Analysis
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
# This use case call Grid-Stat once.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2024-05-01 00 UTC
#
# **End time (INIT_END):** 2024-05-02 03 UTC
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 hour
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1 - 18 using 1 hour increments
#
# Starting with the 00 UTC initialization on 2024-05-01, 28 model initializations are 
# processed ending with the run initialized at 03 UTC on 2024-05-02.  For each 
# initialization, 18 lead times are processed, for a total of 504 Grid-Stat runs. 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# e.g. parm/use_cases/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr.conf

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

##############################################################################
# Python Embedding
# ----------------
# [UPDATE_SECTION_CONTENT]
#
# This use case calls a Python Embedding script to read ZARR.  But since we are
# changing this, I am waiting to update this documentation.
# 
# .. dropdown:: parm/use_cases/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr/read_zarr_HRRRCast.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr/read_zarr_HRRRCast.py
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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr.conf /path/to/user_system.conf
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
# Output for this use case can be found in 
# {OUTPUT_BASE}/model_applications/short_range/GridStat_fcstHRRRCast_obsHRRRanal_zarr/grid_stat
# and will contain 28 directories, one for each model initialization.  The directories will 
# have the following format::
#
#  * YYYYmmddHH
#
# Inside each directory, there will be 12 .stat files of the format 
# grid_stat_HRRRCast_vs_HRRR_HHMMSSL_YYYYMMDD_HHMMSSV.stat, where HHMMSSL is the hour, 
# minute, and second of the lead time, YYYYMMDD is the year, month, and day of the valid 
# time, and HHMMSSV is the hour, minute, and second of the valid time.  For example, the
# directory contains the following files::
#
#  * grid_stat_HRRRCast_vs_HRRR_010000L_20240501_010000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_020000L_20240501_020000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_030000L_20240501_030000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_040000L_20240501_040000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_050000L_20240501_050000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_060000L_20240501_060000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_070000L_20240501_070000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_080000L_20240501_080000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_090000L_20240501_090000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_120000L_20240501_120000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_150000L_20240501_150000V.stat
#  * grid_stat_HRRRCast_vs_HRRR_180000L_20240501_180000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * AIUseCase
#   * PythonEmbeddingFileUseCase
#   * ZarrFileUseCase
#   * GRIB2FileUseCase
#   * ShortRangeAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-GridStat_fcstHRRRCast_obsHRRRanal_zarr.png'
