"""
TCGen: Genesis Density Function (GDF) and Track Density Function (TDF) 
=============================================================================

model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#

##############################################################################
# Datasets
# --------
#
# All datasets are traditionally in netCDF format. Grids are either regular gaussian
# Latitude/Longitude grids or they are Lambert-conformal WRF grids.
#
# The forecast datasets contain weekly, monthly or seasonally integrated data. Here, the
# time format of the use-case is monthly. Since the verification is done on the hindcasts
# rather than the forecast (would require another 6 months of waiting), the key
# identification here is the month of initialization and then the lead-time of the forecast
# of interest.
#
# The hindcast data, the 'observational' data that is to be compared to the forecast,
# is a collection of datasets formatted in equivalent format to the forecast. The
# hindcast ensemble is identified through the year in the filename (as well as in the
# time variable inside the netCDF file).
#
# Forecast Datasets:
# 
# NMME
# * variable of interest: pr (precipitation: cumulative monthly sum)
# * format of precipitation variable: time,lat,lon (here dimensions: 29,181,361) with time variable representing 29 samples of same Julian Init-Time of hindcasts over past 29 years.
#
# Hindcast Datasets:
#
# Observational Dataset:
#
# * CPC precipitation reference data (same format and grid)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case loops over initialization years and processes forecast lead months with GridStat
# It also processes the output of GridStat using two calls to SeriesAnalysis.
#

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time: GridStat
#
# This example loops by initialization time. Each initialization time is July of each year from 1982 to 2010. For each init time it will run once, processing forecast leads 1 month through 5 months. The following times are processed:
#
# Run times:
#
# | **Init:** 1982-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
# | **Init:** 1983-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
# | **Init:** 1984-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
# | **Init:** 1985-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
# | ...
# |
# | **Init:** 2009-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
# | **Init:** 2010-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf
#

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
# **TCGenConfig_wrapped**
#
# .. note:: See the :ref:`TCGen MET Configuration<tc-gen-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCGenConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to create output graphics
#
# parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF/UserScript_fcstGFSO_obsBDECKS_GDF_TDF.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF/UserScript_fcstGFSO_obsBDECKS_GDF_TDF.py
#

##############################################################################
# Running METplus
# ---------------
# This use case can be run two ways:
#
# 1) Passing in GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
# **NOTE:** All of these items must be found under the [dir] section.
#
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast/GridStat (relative to **OUTPUT_BASE**)
#
# For each month and year there will be two files written::
#
# * grid_stat_NMME-hindcast_precip_vs_CPC_IC{%Y%b}01_2301360000L_20081001_000000V.stat
# * grid_stat_NMME-hindcast_precip_vs_CPC_IC{%Y%b}01_2301360000L_20081001_000000V_pairs.nc
#
# Output from SeriesAnalysis will be found in model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast/SeriesAnalysis (relative to **OUTPUT_BASE**)
#
# For each month there will be two files written::
#
# * series_analysis_NMME_CPC_stats_ICJul_{%m}_climo.nc
# * series_analysis_NMME_CPC_stats_ICJul_{%m}_full_stats.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#    `TCGenToolUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=TCGenToolUseCase&check_keywords=yes&area=default>`_
#    `S2SAppUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_
#    `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.png'
#
