"""
GridStat: Temporal and spatial verification of soil moisture
============================================================

model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python.conf

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
# Comparison between prototype forecast models and existing observational data
# is critical to ensuring that model upgrades are completed with minimal 
# downsides or degradation in verification statistics. This use case compares
# a GFS HR run to SMOPS, a combination dataset of satellite measurements concerning
# soil characteristics. By completing temporal and spatial verification measurements,
# this use case serves as an excellent baseline for evaluating near surface model soil moisture

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0

##############################################################################
# Datasets
# --------
# **Forecast:** Global Forecast System (GFS) v17 prototype version (tag HR1) 12km resolution, 0-0.1 meter soil temperature
#
# **Observation:** NOAA Soil Moisture Products System (SMOPS) 0.25 degree resolution, blended soil temperature
# **NOTE:** Retrieving observation data from CLASS requires user account
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
# The two MET tools used in this use case are GridStat and SeriesAnalysis. 
# Both tools require Python Embedding to ingest observation data. 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2020-06-07
#
# **End time (INIT_END):** 2020-06-07
#
# **Increment between beginning and end times (INIT_INCREMENT):** 12 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24 hours
#
# With an increment of 12 hours and no difference between the INIT_BEG and INIT_END,
# only one time is run in this use case: a 24 hour lead from 2020-06-07.
# Both GridStat and SeriesAnalysis are used over this time frame, requesting CNT line
# type output. Because both tools are run using the same input data,
# much of SeriesAnalysis' settings reference GridStat's settings, which is the first
# tool used. The forecast and observation grid resolutions differ, so regridding is
# used to interpolate the higher resolution forecast data to the lower resolution 
# observation data for verification, using a bilinear method. A poly masking
# for CONUS is used, with the mask being available from the MET installation.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# e.g. parm/use_cases/model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python.conf

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
# .. dropdown:: SeriesAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls the read_SMOPS_data.py script to read and pass to GridStat
# and SeriesAnalysis a MET-usable dataset for the observation data. In its current form,
# the SMOPS data is read in by MET upside down, and is not CF-compliant. Using
# a simplified Python script, the input file and variable field are passed at runtime
# and the associated data is extracted. This is passed in memory to MET and
# verification proceeds normally.
# 
# .. dropdown:: parm/use_cases/model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python/read_SMOPS_data.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python/read_SMOPS_data.py
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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land/GridStat_fcstGFS_obsSMOPS_soilMoisture_Python.conf /path/to/user_system.conf
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
# Output will be in two subfolders relative to **OUTPUT_BASE**:
#
#  * GridStat
#  * SeriesAnalysis
#
# Each of these directories will hold the output from their respectively named tools.
# The GridStat folder will contain two files, one STAT file with the CNT line type output
# and one netCDF file, which contains 3 fields (not including the lat/lon fields). Those fields
# are:
#
#  * FCST_SOILW_Z0.1-0_CONUS(lat, lon)
#  * OBS_Blended_SM_UNKNOWN_CONUS(lat, lon)
#  * DIFF_SOILW_Z0.1-0_Blended_SM_UNKNOWN_CONUS(lat, lon)
#
# For the SeriesAnalysis folder, only one netCDF output is created.
# Six variable fields are present (not including the lat/lon and series fields). 
# Those variables are:
#
#  * series_cnt_ME(lat, lon)
#  * series_cnt_MAE(lat, lon)
#  * series_cnt_RMSE(lat, lon)
#  * series_cnt_MBIAS(lat, lon)
#  * series_cnt_FBAR(lat, lon)
#  * series_cnt_OBAR(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * LandAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/land-GridStat_fcstGFS_obsSMOPS_soilMoisture_Python.png'
