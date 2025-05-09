"""
MTD: Use MTD to compute fire area and spread
============================================

model_applications/fire/MTD_fcstWRF_obsMMA_416fire.conf

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
# Multimission Aircraft fire perimiters for the 416 Fire.  MTD is used specifically 
# to create objects over time that provide information on fire area and spread over 
# time. 

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** WRF Fire
#
# **Observation:** Multimission Aircraft Fire Perimiter
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
# This use case calls MODE-Time-Domain once.

##############################################################################
# METplus Workflow
# ----------------
# [UPDATE_SECTION_CONTENT]
#
# **Beginning time (INIT_BEG):** 2018-06-01 16 UTC
#
# **End time (INIT_END):** 2018-06-01 16 UTC
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 hour
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1 - 35 hours with hourly increments
#
# With an increment of 1 hour, one forecast initialization time is processed to produce
#
# for a total of 29 years, with 24 members in each ensemble forecast. This use case 
# initially runs SeriesAnalysis 24 times, once for each member of the CFSv2 ensemble 
# across the 29 years of data. The resulting 24 outputs are read in by GenEnsProd 
# which uses the normalize option to normalize each of the ensemble members 
# relative to its climatology (FBAR) and standard deviation (FSTDEV). The output from 
# GenEnsProd are 29 files containing the uncalibrated probability forecasts for 
# the lower tercile of January for each year. The final probability verification 
# is done across the temporal scale in SeriesAnalysis, and the spatial scale in GridStat.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416fire.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416fire.conf

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
# .. dropdown:: parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/MTD_fcstWRF_obsMMA_416fire.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/fire/MTD_fcstWRF_obsMMA_416fire
# and will contain the following files::
#
#  * mtd_WRF_Fire_416_20180601_170000V_2d.txt
#  * mtd_WRF_Fire_416_20180601_170000V_3d_single_simple.txt
#  * mtd_WRF_Fire_416_20180601_170000V_obj.nc
#
# The 2d file contains object based statistics for the objects at different time steps.  
# The 3d file contains the object based statistics over time.  For the netCDF file, five 
# variable fields are present (not including the lat/lon fields). Those variables are::
#
#  * fcst_raw(time, lat, lon)
#  * fcst_object_id(time, lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MTDToolUseCase
#   * NetCDFFileUseCase
#   * FireAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-MTD_fcstWRF_obsMMA_416fire.png'
