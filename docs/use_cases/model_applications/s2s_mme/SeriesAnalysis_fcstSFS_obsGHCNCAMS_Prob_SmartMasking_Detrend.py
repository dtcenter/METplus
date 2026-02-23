"""
SeriesAnalysis: Probabilistic verification across tercile climatology
=====================================================================

model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend.conf

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
# When verifying climatology data, it is sometimes more advantageous to calculate
# the climatology fields across the data itself, rather than ingesting another
# dataset. This use case expands on this concept, with a static probability field 
# of 0.33 being read in as the climatology mean file and acting as the tercile
# that the data can be measured against. The forecast is calculated in probabilistic
# space with the aid of Python Embedding and demonstrates how S2S verification space can be
# more easily accessed in METplus.

##############################################################################
# Version Added
# -------------
#
# METplus version 7.0

##############################################################################
# Datasets
# --------
# **Forecast:** Seasonal Forecast System (SFS) Baseline, 1 degree resolution, 2m temperature
#
# **Observation:** Global Historical Climatology Network ver. 2, Climatology Anomaly Monitoring System (GHCNCAMS) 1 degree resolution, 2m temperature
#
# **Climatology:** A self-created constant field of 0.33
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
# **Beginning time (INIT_BEG):** 1994-11-01
#
# **End time (INIT_END):** 2020-11-01
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 year
#
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#

# With an increment of 1 year, all November 1st’s from 1994 to 2020 are processed 
# for a total of 27 years in SeriesAnalysis. This use case utilizes Python Embedding
# which moves the input into probabilistic space when it is returned to SeriesAnalysis,
# so all thresholds are unitless. To focus on instances where the lower tercile (0.33) is met,
# the observation categorical threshold is set to >=0.5, where the observation field 
# that is preprocessed by Python Embedding is already set to 0 or 1, to indicate an observed
# lower tercile event occurred or not. Additionally, the lower tercile is set
# using the climatology mean input file.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# e.g. parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend.conf

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
# This use case utilizes two Python scripts. The first, function_library_withDetrend.py,
# serves the purpose of data handling. It open and reads in NMME and observational data,
# while also calculating the tercile probabilities evaluated in METplus using CPC methodologies 
# (including non-normal assumption for precipitation terciles, or other variables as needed).
# For more simple changes, users can add additional models under MODEL_SPECS 
# (in the format 'model_name': nMembers); and additional model groupings can 
# be added under MODEL_GROUPS, in the format  'short_name’: ['list', 'of', 'models']. 
# Both of these are near the top of the function library. Additional observed datasets 
# can be added under the file_map and var_map, under create_obs_anomalies. 
# This python has the addiitonal enhancement of a dynamic "smart masking" logic. 
# This procedure identifies the valid domain of any input variable (e.g., Land for 
# temperature, Ocean for SST) and converts NaN values within that domain to 
# zeros to ensuring non-events are statistically counted as "misses." It also 
# re-applies the original data mask to the invalid regions (e.g., oceans for 
# land-only data), preventing invalid verification over undefined areas regardless of the variable type.
# The second script, wrapper_combined_withDetrend.py, serves as the interface between python logic and METplus.
# Based on options in the METplus config file, it formats model and observational 
# data (e.g., standardizing to lat x lon grids) and holds it in memory for METplus 
# to ingest. It also feature options for flags (FLIP_OBS, FLIP_MODELS) to handle 
# latitude orientation mismatches, ensuring data is geometrically correct before MET sees it.
# This use case could also be made to detrend the data, by updating the DETREND_DATA 
#setting in function_library_withDetrend.py to TRUE.
# 
# .. dropdown:: parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend/function_library_withDetrend.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend/function_library_withDetrend.py
# 
# .. dropdown:: parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend/wrapper_combined_withDetrend.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend/wrapper_combined_withDetrend.py

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mme/SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend.conf /path/to/user_system.conf
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
# Output will be in a directory named SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend
# relative to **OUTPUT BASE** and will contain one file. The netCDF file
# will contain eight variable fields (not including the lat/lon fields). 
# These correspond to the statistics that were requested in the configuration file,
# and are as follows:
#
#  * series_pstd_BRIER_obsge0.5(lat, lon)
#  * series_pstd_RELIABILITY_obsge0.5(lat, lon)
#  * series_pstd_RESOLUTION_obsge0.5(lat, lon)
#  * series_pstd_UNCERTAINTY_obsge0.5(lat, lon)
#  * series_pstd_ROC_AUC_obsge0.5(lat, lon)
#  * series_pstd_BSS_obsge0.5(lat, lon)
#  * series_pstd_BRIERCL_obsge0.5(lat, lon)
#  * series_pstd_TOTAL_obsge0.5(lat, lon)

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
# sphinx_gallery_thumbnail_path = '_static/s2s_mme-SeriesAnalysis_fcstSFS_obsGHCNCAMS_Prob_SmartMasking_Detrend.png'
