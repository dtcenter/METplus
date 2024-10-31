"""
Grid-Stat: CESM and GFS Analysis CONUS Temp 
============================================================================
model_applications/climate/
GridStat_fcstCESM_obsGFS
_ConusTemp.conf
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
# To evaluate the CESM model temperature against the GFS analysis across the
# the Continental United States to obtain categorical output statistics. This 
# was developed as part of the NCAR System for Integrated Modeling of the 
# Atmosphere (SIMA) project. 

##############################################################################
# Version Added
# -------------
# [UPDATE_SECTION_CONTENT]
#
# METplus version 3.1

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: CESM Surface Temperature Data

#  * Observation dataset: GFS Analysis 2m Temperature
#
# **Climatology:** None
#
# **Location:** 

##############################################################################
# METplus Components
# ------------------
#
# This use case runs grid_stat to create continuous statistics on 
# tempeprature from the CESM model and observations from the GFS analysis. 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2014080100
# **End time (INIT_END):** 2014080200
# **Increment between beginning and end times (INIT_INCREMENT):** 86400
# **Sequence of forecast leads to process (LEAD_SEQ):** 6, 12
#
#  The grid_stat tool is run for each time. This example loops by initialization
#  time.  It processes 4 valid times, listed below.
#
#  **Valid:** 2014-08-01_06Z
#  **Forecast lead:** 06
# 
#  **Init:** 2014-08-01_12Z
#  **Forecast lead:** 12
# 
#  **Init:** 2014-08-02_06Z
#  **Forecast lead:** 06
# 
#  **Init:** 2014-08-02_12Z
#  **Forecast lead:** 12

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GridStatConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
# [UPDATE_SECTION_CONTENT]
#
# This use case calls the read_ASCAT_data.py script to read and pass to PointStat 
# the user-requested variable. The script needs 5 inputs in the following order: 
# a path to a directory that contains only ASCAT data of the “ascat_YYYYMMDDHHMMSS_*” 
# string, a start time in YYYYMMDDHHMMSS, an end time in the same format, 
# a message type to code the variables as, and a variable name to read in. 
# Currently the script puts the same station ID to each observation, but there is 
# space in the code describing an alternate method that may be improved upon to 
# allow different satellites to have their own station IDs. 
# This code currently ingests all files it finds in the directory, pulls out the 
# requested variable, and arranges the data in a list of lists following the 
# 11-column format for point data. This list of lists is passed back 
# to PointStat for evaluation and the requested statistical output. The location 
# of the code is 
# parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py

##############################################################################
# User Scripting
# --------------
# [UPDATE_SECTION_CONTENT]
#
# This use case uses a Python script to perform plotting, which at the time of 
# this use case creation was not an ability METplus had. Additionally some of 
# the plotting features used in this script are not currently slated for METplus 
# analysis suite development.
# In order to create the plots, the script reads in a yaml file and sets up 
# the correct environment. Plot parameters (which are hard coded in the script) are set, 
# and the datasets are read in from the input file. The desired variable fields 
# are placed into arrays, which are then treated for bad data and squeezed to the 
# appropriate dimensions. Additional basic math is completed on the resulting arrays 
# to create the cross spectra values with the results being graphed.
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired:
#
#run_metplus.py /path/to/METplus/parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf /path/to/user_system.conf
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
# Output for this use case will be found in {OUPUT_BASE}/model_applications/climate/CESM_GridStat/grid_stat
# and will contain the following files:
#
# grid_stat_CESM_TMP_vs_GFS_ANALYS_060000L_20140801_060000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_120000L_20140801_120000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_060000L_20140802_060000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_120000L_20140802_120000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.
# Those variables are::
#
#  * UPDATE_FILES

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase 
#   * ClimateAppUseCase
#   * NetCDFFileUseCase 
#   * NCAROrgUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/climate-GridStat_fcstCESM_obsGFS_ConusTemp.png'
#
