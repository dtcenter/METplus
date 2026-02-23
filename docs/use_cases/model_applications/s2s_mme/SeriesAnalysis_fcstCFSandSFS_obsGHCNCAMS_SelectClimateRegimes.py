"""
SeriesAnalysis: Verifying seasonal models across conditional times
==================================================================

model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCN_SelectClimateRegimes.conf

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
# This use case uses conditional time periods for verification, relying on METplus tool
# instances and valid listing to create specific verifiction windows. Instead of aggregating 
# statistics over the entire hindcast period, this configuration allows users 
# to assess model skill during specific climate regimes, such as El Niño, La Niña,
# or Neutral years. 

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0

##############################################################################
# Datasets
# --------
# **Forecast:** Climate Forecast System ver 2 (CFSv2) and Seasonal Forecast System (SFS) Baseline, 1 degree resolution, 2m temperature
#
# **Observation:** Global Historical Climatology Network ver. 2, Climatology Anomaly Monitoring System (GHCNCAMS) 1 degree resolution, 2m temperature
#
# **Climatology:** None
#
# Note that this use case ingests the same dataset used in two other use cases in the this category,
# and in an effort to mimize data duplication, paths to the data may reference another use case name
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
# The only tool this use case calls is SeriesAnalysis, but there are
# four instances of SeriesAnalysis. A Python script is used for ingesting 
# forecast and observation data, once for each year  of data in the CFSv2 and SFS ensembles.

##############################################################################
# METplus Workflow
# ----------------
#
# For the initial instance of SeriesAnalysis, the timing info is:
#
# **Beginning time (INIT_BEG):** 1994-11-01
#
# **End time (INIT_END):** 2020-11-01
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 year
#
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#
# For the remaining instances of SeriesAnalysis, the VALID_LIST setting is 
# utilized. The following details what each instance has for each VALID_LIST.
#
# ElNino instance:
#
# **VALID_LIST :** 1997110100,2002110100,2004110100,2006110100,2009110100,2014110100,2015110100,2018110100
#
# LaNina instance:
#
# **VALID_LIST :** 1995110100,1998110100,1999110100,2000110100,2005110100,2007110100,2008110100,2010110100,2011110100,2016110100,2017110100,2020110100
#
# Neutral instance:
#
# **VALID_LIST :** 199610100,2001110100,2003110100,2012110100,2013110100,2019110100

# With an increment of 1 year, all November 1st’s from 1994 to 2020 are processed 
# for a total of 27 years for the first instance of SeriesAnalysis. In the following
# three instances, the VALID_LIST controls how many years are read in, ranging from
# six to twelve years. This use case utilizes Python Embedding to process the 
# forecast and observation inputs, reading user-set variables like TIME_PERIOD and 
# CLIM to fine-tune what temporal size the means are calcuated over and what climatology
# period is available, respectively. Outputs of ME, MAE, and RMSE, among others, provide
# climate-useful statistical output. Instead of utilizing LEAD_SEQ, this use case
# uses the CUSTOM_LOOP_LIST for 1, 2, and 3 month leads. This is done so that the Python script can
# access an actual number rather than a date for processing. 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# e.g. parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes.conf

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
# .. dropdown:: SeriesAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case utilizes two Python scripts. The first, function_library.py,
# serves the purpose of data handling. It open and reads in NMME and observational data,
# while also calculating climatologies, anomalies, and tercile probabilities using CPC methodologies 
# (including non-normal assumption for precipitation terciles, or other variables as needed).
# For more simple changes, users can add additional models under MODEL_SPECS 
# (in the format 'model_name': nMembers); and additional model groupings can 
# be added under MODEL_GROUPS, in the format  'short_name’: ['list', 'of', 'models']. 
# Both of these are near the top of the function library. Additional observed datasets 
# can be added under the file_map and var_map, under create_obs_anomalies. 
# The second script, wrapper_combined.py, serves as the interface between python logic and METplus.
# Based on options in the METplus config file, it formats model and observational 
# data (e.g., standardizing to lat x lon grids) and holds it in memory for METplus 
# to ingest. It also feature options for flags (FLIP_OBS, FLIP_MODELS) to handle 
# latitude orientation mismatches, ensuring data is geometrically correct before MET sees it.
# 
# .. dropdown:: parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes/function_library.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes/function_library.py
# 
# .. dropdown:: parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes/wrapper_combined.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes/wrapper_combined.py

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes.conf /path/to/user_system.conf
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
# Output will be in a directory named SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes
# relative to **OUTPUT BASE** and will contain 12 files. These can be grouped into three
# lead times (1, 2, and 3 month) and follow this naming scheme:
#
#  * Bias_SeriesAnalysis_tmp2m_raw_CFSandSFS_IC11_Lead0xseasonal_1994_2020_ElNino.nc 
#  * Bias_SeriesAnalysis_tmp2m_raw_CFSandSFS_IC11_Lead0xseasonal_1994_2020_LaNina.nc 
#  * Bias_SeriesAnalysis_tmp2m_raw_CFSandSFS_IC11_Lead0xseasonal_1994_2020.nc 
#  * Bias_SeriesAnalysis_tmp2m_raw_CFSandSFS_IC11_Lead0xseasonal_1994_2020_Neutral.nc 
#
# Where x is the lead time value.
# In each netCDF file, six variable fields are present (not including the lat/lon fields). 
# These correspond to the statistics that were requested in the configuration file,
# and are as follows:
#
#  * series_cnt_ME(lat, lon)
#  * series_cnt_MAE(lat, lon)
#  * series_cnt_RMSE(lat, lon)
#  * series_cnt_TOTAL(lat, lon)
#  * series_cnt_FBAR(lat, lon)
#  * series_cnt_OBAR(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * SeriesAnalysisUseCase
#   * PythonEmbeddingFileUseCase
#   * CustomStringLoopingUseCase
#   * S2SMMEAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mme-SeriesAnalysis_fcstCFSandSFS_obsGHCNCAMS_SelectClimateRegimes.png'
