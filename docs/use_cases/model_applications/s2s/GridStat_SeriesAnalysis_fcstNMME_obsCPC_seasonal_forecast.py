"""
Grid-Stat and Series-Analysis: BMKG APIK Seasonal Forecast 
=============================================================================

model_applications/s2s/GridStat_SeriesAnalysis
_fcstNMME_obsCPC
_seasonal_forecast.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# The process of seasonal forecasting with a time horizon of one to many months
# (typically 6 to 9 months) poses new challenges to tools primarily developed for
# weather forecasting that cover a few days. These challenges include two aspects
# in particular: (1) a dramatically expanded time variable, and (2) a verification
# that is by design backward oriented using extensive hindcasts over past decades
# rather than the rapid verification possible in short-range weather forecasting.
# Therefore, the scientific objective of the seasonal forecast usecase involves
# the expansion of options to describe time as well as the strategic selection
# of hindcasts.
#
# Time:
#  Commonly METplus expresses time intervals in the minutes, hours, and days. 
#  Month and year intervals were not supported since there is not a constant length for these units.
#  Therefore, modifications to METplus were made to support these intervals by determining the offset
#  relative to a given time.
#
# Input data:
#  The input data from seasonal forecasts is generally based on daily, weekly, decadal
#  (10-day), monthly or seasonal time integrated intervals. The time variable therefore is
#  often no longer a simple snapshot of the system but rather representing an average, a
#  sum (precipitation), or a particular statistic (maximum wind, minimum temperature, wind
#  variability) over the integration time period. This requires some adjustment from the
#  traditional approach in forecast verification where forecast time ("valid-time") is
#  simply a snapshot out of a continuous run.
#
# Hindcasts:
#  The objective of seasonal forecasts is no longer the exact location and intensity
#  of one particular weather event, such as a storm, a frontal passage, or high wind
#  conditions. Rather, seasonal forecasting focuses more on the statistical properties
#  over a period of time, be it a 10-day interval, a month, or even a three month season.
#  The verification of a new, forward looking seasonal forecast requires assessments of
#  the forecast systems ability to appropriately forecast that longrange behavior of the
#  weather (here, only atmospheric verification is considered, but the same concept would
#  apply ocean or any other longrange forecast system). Because weather properties
#  commonly change significantly over the course of the season, samples to verify the
#  prognostic system can not be taken from the immediate days, weeks of months before the
#  forecast. Hindcasting in the seasonal context requires a complete set of forecasts
#  based on the same season but during past years. A current July-1 2019 forecast, therefore
#  requires many July-1 forecasts for as many years in the past as possible, given that
#  the forecast system is the same as the one used for the current forecast cycle into the
#  future. Operational centers offer hindcasts, also sometimes called "re-forecasts", with
#  the current, most up-to-date forecast system. MET and METplus therefore need to be able
#  to extract the appropriate collection of past forecasts. This includes the identification
#  of the same Julian-day-of-Year init-dates from forecasts cycles from past years, and then
#  identify the different lead-times of interest generally ranging from one to 6 or more
#  months.
#
# Verification:
#  The verification steps can then utilize the existing collection of verification tools.
#  In comparison to weather forecasts, the only difference is that the data, as stated
#  above, are not snapshots but time-integrated values (averages, sums, statistics) that
#  are representing a whole period of time. The verification then focuses on comparisons
#  of these derivatives of the forecast simulations. In practice, a further step might be
#  added prior to, or as a key step during verification: the formation of anomalies of the
#  forecasts compared to long-term expected averages. A rainfall forecasts can therefore
#  be verified in both absolute as well as anomaly context where some analyses might focus
#  on extreme rainfall threshold exeedance of, for example, 500mm per month. At the same
#  time, the same forecast might be verified for the 3 months rainfall average in comparison
#  with the long-term expected mean. The verification might then assess how well the system
#  can foresee the occurrence of below average rainfall over the season, and possibly some
#  selected thresholds there (e.g., ability to forecast mean seasonal rainfall below
#  the 10-th percentile of seasonal rainfall). Finally, flexibility in formulating forecast
#  verification strategies is important as forecast skill might vary by location, the timing
#  within the seasonal cycle, or the state of the evolving coupled system (the rapid onset
#  of a strong El Nino will lead to significantly different forecast skill compared to a
#  neutral state in the Pacific). Memory from past months, for example when considering
#  accumulated soil moisture, might also influence the forecast skills. Seasonal forecast
#  verification therefore requires understanding of the climate system; MET and METplus
#  then need to offer the flexibility to tailor verification strategies and to potentially
#  craft conditional approaches.
#
#  Overall, seasonal forecasts don't require a new verification approach. It does however
#  put demands on the flexibility of dealing with a significantly exapanded range of the
#  time variable as well as logistic infrastructure to select appropriate hindcast samples
#  from long hindcast or re-forecast archives. Scientifically, the challenges are mostly
#  restricted in the appropriate formulation of verificaation questions that address
#  specific forecast objectives. Compared to weather forecastsing, seasonal forecasts need
#  to draw their skill from slowly changing components in the coupled Earth system while
#  acknowledging the high-frequency noise of weather superposed on these 'climatologically'
#  evolving background conditions. In many regions of the world, the noise might dominate
#  that background climate and forecast skill is low. It is therefore the task of seasonal
#  forecast verification to identify where there is actually skill for particular properties
#  of the forecasts over a wide range of lead-times. The skill might be dependent on
#  location, on the timing within the seasonal cycle, or even on the evolving state of the
#  coupled system.

##############################################################################
# Datasets
# --------
#
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
#
# | **Init:** 1983-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
#
# | **Init:** 1984-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
#
# | **Init:** 1985-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
#
# ...
#
# | **Init:** 2009-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
#
# | **Init:** 2010-07
# | **Forecast leads:** 1 month, 2 months, 3 months, 4 months, 5 months
#

##############################################################################
# METplus Configuration
# ---------------------
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# **GridStatConfig_seasonal_forecast**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStatConfig_seasonal_forecast
#
# See the following file for more information about the environment variables set in this configuration file::
#   parm/use_cases/met_tool_wrapper/GridStat/GridStat.py
#
# **SeriesAnalysisConfig_seasonal_forecast_climo**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/SeriesAnalysisConfig_seasonal_forecast_climo
#
# **SeriesAnalysisConfig_seasonal_forecast_full_stats**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/SeriesAnalysisConfig_seasonal_forecast_full_stats
#
# See the following file for more information about the environment variables set in these configuration files::
#   parm/use_cases/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis.conf
#

##############################################################################
# Running METplus
# ---------------
# This use case can be run two ways:
#
# 1) Passing in GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf
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
#    `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#    `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&check_keywords=yes&area=default>`_,
#    `LoopByMonthFeatureUseCase  <https://dtcenter.github.io/METplus/search.html?q=LoopByMonthFeatureUseCase&check_keywords=yes&area=default>`_,
#    `NCAROrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_
#    `CustomStringLoopingUseCase  <https://dtcenter.github.io/METplus/search.html?q=CustomStringLoopingUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.png'
#
