"""
GridStat: Verifying Soil moisture of SFS-GSL output against ERA5-Land and compute categorical statistics
========================================================================================================

model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# This use case ingests 30 SFS-GSL Ensemble forecast of Soil Moisture, with all ensemble 
# members in a single file for a given year and month (here June).
# The python embedding script computes an ensemble mean for the given month.
# The ensemble mean is compared to ERA5-Land dataset.
# The ERA5-Land data contains 30 years of monthly Soil Moisture data at 1 degree resolution.
# This use case verifies soil moisture of SFS-GSL model against ERA5-Land soil moisture analysis.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# 
# **Forecast:** 30 SFS-GSL Ensemble files, 0-1m Soil Moisture fields Units: mm
#
# **Observation:** ERA5-Land, Monthly 0-1m Soil Moisture field Units: mm 
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
# This use case calls a GridStat 30 times, once for each year of data of the SFS-GSL ensemble.
# It also calls UserScript twice and makes one call to Series-Analysis.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 1991-06-00
#
# **End time (INIT_END):** 2020-06-00
#
# **Increment between beginning and end times (INIT_INCREMENT):** 12 months
#
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#
# With an increment of 12 months, all June from 1991 to 2020 are processed 
# for a total of 30 years, with 5 members in each ensemble forecast. This use case 
# initially reads the SFS GSL 5 member ensemble monthly forecast data,
# and compute ensemble means for each month. 
# The resulting 30 outputs and ERA5-Land monthly analysis are read in by GridStat
# to compute statistics for Global and over CONUS.
#
# Then, two UserScripts are each run once, one to reformat data and another to plot
# data.  Finally, Series-Analysis is run once to compute statistics for June over 
# the 30 year time period.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf

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
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This script reads output from the SFS-GSL model, which provides soil moisture forecasts
# in separate monthly NetCDF files. It accepts command-line arguments specifying the file path, 
# a valid forecast month, and year. The script loads forecast data (fcst) along with associated 
# latitude, longitude, and target time variables. It converts the model’s target time 
# values—representing months since January 1960—into actual calendar dates, then filters the 
# data to retain only forecasts matching the specified valid month. It computes the ensemble 
# mean over the 5-member ensemble and prepares the resulting data in a 
# format suitable for input into the MET (Model Evaluation Tools) verification system.
# The location of the code is 
# 
# .. dropdown:: parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture/sfs_gsl_model_wrapper.py 
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture/sfs_gsl_model_wrapper.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf /path/to/user_system.conf
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
# Output for the use case will be found in 30 folders(relative to **OUTPUT_BASE**).
# The output will follow the time information of the run. Specifically:
#
#  * YYYY060100
#
# where YYYY will be replaced by values corresponding to each of the years (1991 through 2020).
# Each of those folders will have the following files:
#
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_fho.txt
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_pairs.nc
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.
# For the netCDF file, five variable fields are present (not including the lat/lon fields). 
# Those variables are::
#
#  * FCST_Soil_moisture_0-1m_FULL(lat, lon) 
#  * FCST_Soil_moisture_0-1m_CONUS(lat, lon) 
#  * OBS_soilm1m_20200601_000000_all_all_FULL(lat, lon)
#  * OBS_soilm1m_20200601_000000_all_all_CONUS(lat, lon) 
#  * DIFF_Soil_moisture_0-1m_soilm1m_20200601_000000_all_all_FULL(lat, lon) 
#  * DIFF_Soil_moisture_0-1m_soilm1m_20200601_000000_all_all_CONUS(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * S2SAppUseCase
#   * S2SSoilMoistureAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_soil_moisture-GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.png'
