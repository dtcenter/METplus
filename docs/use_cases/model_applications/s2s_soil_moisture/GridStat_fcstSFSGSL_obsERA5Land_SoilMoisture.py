"""
GridStat: Verifying Soil moisture of SFS-GSL output against ERA5-Land, continuous and categorical statistics
============================================================================================================

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
# This use case verifies 30 years of Soil Moisture data from an ensemble for a given
# year and month (here June).  The purpose is to evaluate the Soil Moisture ensemble
# mean at a 1 degree resolution against ERA5-Land data.  The use case demonstrates how 
# to compute categorical, continuous, and anomaly statistics over the globe and CONUS 
# with Grid-Stat, and also select continuous statistics at each grid point over the globe 
# statistics with Series-Analysus.  It also illustrates how to read in NMME data and 
# compute an emsemble mean from NMME data as input to Grid-Stat and Series-Analysis, and 
# how to plot example statistics from the command line.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# 
# **Forecast:** 30 SFS-GSL Ensemble files, 0-1m Soil Moisture fields in mm
#
# **Observation:** ERA5-Land, Monthly 0-1m Soil Moisture field in mm 
#
# **Climatology Forecast:** SFS-GSL 30 year Enemble Mean Soil Moisture mean and standard deviation
#
# **Climatology Observation:** ERA5-Land, 30 year Monthly 0-1m Soil Moisture mean and standard deviation
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
# It also calls Series-Analysis once and UserScript twice.  METcalcpy, METplotpy, and METdataio 
# are required to run the tow UserScripts.  These steps could be turned off if graphics are not
# desires.  The METcalcpy scripts accessed include the following:
#
# * metcalcpy/util/read_env_vars_in_config.py
#
# The METplopty scrips accessed include the following:
#
# * metplotpy/plots/line/line.py
#
# The METdataio scripts accessed include the following:
#
# * METdbLoad/ush/read_data_files.py
#
# * METdbLoad/ush/read_load_xml.py
#
# * METreformat/write_stat_ascii.py

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
# This use case initially computes statiscs with Grid-Stat using ensemble means from
# the SFS-GSL 5 member ensemble monthly forecast data.  With an increment of 12 months, 
# all Junes from 1991 to 2020 are processed for a total of 30 years over the globe and
# CONUS.
#
# Then, Series-Analysis is run once to compute 2D statistics over the entire 30 year time
# period.  Finally, the two UserScripts are each run once, one to reformat data and 
# another to create a plot of ME and RMSE for June over the 30 year time period.

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
# .. dropdown:: SeriesAnalysisConfig_wrapped
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
# mean over the 5-member ensemble and prepares the resulting data in a format suitable for input 
# into the MET (Model Evaluation Tools) verification system.  The code is located in::
#
#  * parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture
# 
# .. dropdown:: sfs_gsl_model_wrapper.py 
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture/sfs_gsl_model_wrapper.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 

##############################################################################
# User Scripting
# --------------
#
# There are two Python scripts used in this use case, called using the "UserScript" keyword
# in the METplus wrappers PROCESS_LIST configuration item.  These scripts provide an
# interface to the functions in the METdataio, METcalcpy, and METplotpy Python modules
# of METplus.  The functions used in these scripts demonstrate reformatting of the GridStat
# output to meet the format required by METcalcpy and METplotpy, and then plotting that 
# reformatted output using functions from METcalcpy and METplotpy.  
# 
# The first Python script is called reformat_CNT_linetype.py.  This script takes the
# output CNT linetype from Grid Stat and reformats it so that the data can be plotted.  
# The script takes an input .yaml file, reformat_CNT.yaml.  Environment variables in the yaml
# file are specified in the [user_env_vars] section of the 
# GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf METplus configuration file.
#
# The second Python script is plot_line_stats.py.  This script creates line plots for ME and RMSE
# over time, using the YAML files custom_line_ME.yaml, and custom_line_RMSE.yaml  Input variables 
# to both scripts are set in the [user_env_vars] section of the 
# GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.conf file.
#
# For more information about YAML configuration options for the line plots shown here, see the METplotpy
# `line plot documentation <https://metplus.readthedocs.io/projects/metplotpy/en/latest/Users_Guide/line.html>`_.
#
# Both Python scripts are located in the following directory::
#
#   parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture
#
# .. dropdown:: reformat_CNT_linetype.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture/reformat_CNT_linetype.py
#
# .. dropdown:: plot_line_stats.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_soil_moisture/GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture/plot_line_stats.py

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
# Output for the GridStat run will be found in the grid_stat directory (relative to **OUTPUT_BASE**) 
# and will have the following files::
#
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_fho.txt
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_pairs.nc
#  * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.
# For the netCDF file output from Grid Stat, 16 variable fields are present (not including 
# the lat/lon fields). Those variables are::
#
#  * FCST_Soil_moisture_0-1m_FULL(lat, lon) 
#  * FCST_Soil_moisture_0-1m_CONUS(lat, lon) 
#  * OBS_soilm1m_20200601_000000_all_all_FULL(lat, lon)
#  * OBS_soilm1m_20200601_000000_all_all_CONUS(lat, lon) 
#  * DIFF_Soil_moisture_0-1m_soilm1m_20200601_000000_all_all_FULL(lat, lon) 
#  * DIFF_Soil_moisture_0-1m_soilm1m_20200601_000000_all_all_CONUS(lat, lon)
#  * FCST_CLIMO_MEAN_soilm1m_20190601_000000_all_all_FULL(lat, lon)
#  * FCST_CLIMO_MEAN_soilm1m_20190601_000000_all_all_CONUS(lat, lon)
#  * FCST_CLIMO_STDEV_soilm1m_20190601_000000_all_all_FULL(lat, lon)
#  * FCST_CLIMO_STDEV_soilm1m_20190601_000000_all_all_CONUS(lat, lon)
#  * OBS_CLIMO_MEAN_soilm1m_20190601_000000_all_all_FULL(lat, lon)
#  * OBS_CLIMO_MEAN_soilm1m_20190601_000000_all_all_CONUS(lat, lon)
#  * OBS_CLIMO_STDEV_soilm1m_20190601_000000_all_all_FULL(lat, lon)
#  * OBS_CLIMO_STDEV_soilm1m_20190601_000000_all_all_CONUS(lat, lon)
#  * OBS_CLIMO_CDF_soilm1m_20190601_000000_all_all_FULL(lat, lon)
#  * OBS_CLIMO_CDF_soilm1m_20190601_000000_all_all_CONUS(lat, lon)
#
# The output from SeriesAnalysis will be in the series_analysis directory (relative to
# **OUTPUT_BASE**) and will contain 3 files::
#
#  * series_analysis_files_fcst_init_ALL_valid_ALL_lead_ALL.txt
#  * series_analysis_files_obs_init_ALL_valid_ALL_lead_ALL.txt
#  * SFS-GSL-SA_vs_ERA5_June.nc
#
# The netCDF output from SeriesAnalysis contains 5 variable fields (not including the lat/lon
# fields).  Those variables are::
#
#  * series_cnt_TOTAL(lat, lon)
#  * series_cnt_ME(lat, lon)
#  * series_cnt_RMSE(lat, lon)
#  * series_cnt_FBAR(lat, lon)
#  * series_cnt_OBAR(lat, lon)
#
# The output from the first UserScript can be found in the reformatted directory 
# (relative to **OUTPUT_BASE**) and will contain 1 file::
#
#  * reformat_CNT.data
#
# The output from the second UserScript will be 2 plots found in the plots directory
# (relative to **OUTPUT_BASE**)::
#
#  * SoilMoisture_ME.png
#  * SoilMoisture_RMSE.png

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * SeriesAnalysisUseCase
#   * UserScriptUseCase
#   * PythonEmbeddingFileUseCase
#   * S2SAppUseCase
#   * S2SSoilMoistureAppUseCase
#   * NETCDFFileUseCase
#   * METdataioUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_soil_moisture-GridStat_fcstSFSGSL_obsERA5Land_SoilMoisture.png'
