"""
BMKG APIK Seasonal Forecast
===========================

Brief summary of this use case...

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
# Time variable
# Commonly, MET and METplus use the time variable with units such as seconds, minutes
# and possibly hours. With limited number of digits available to express the time,
# durations of months is hitting limits of this format. It is therefore imperative that
# MET and METplus expand their ability to offer time variable capabilities that deal
# with days, months, and years. A change in year is common when a 6 months forecast is
# initiated after July 1. The lead time of 6 months then invariably runs into the
# following calendar year. The development requirements for MET and METplus thus include
# the ability to provide time-stepping of days and months rather than seconds and minutes,
# and the treatment of forecast leads needs to cover days, months and years.
#
# Input data
# The input data from seasonal forecasts is generally based on daily, weekly, decadal
# (10-day), monthly or seasonal time integrated intervals. The time variable therefore is
# often no longer a simple snapshot of the system but rather representing an average, a
# sum (precipitation), or a particular statistic (maximum wind, minimum temperature, wind
# variability) over the integration time period. This requires some adjustment from the
# traditional approach in forecast verification where forecast time ("valid-time") is
# simply a snapshot out of a continuous run.
#
# Hindcasts
# The objective of seasonal forecasts is no longer the exact location and intensity
# of one particular weather event, such as a storm, a frontal passage, or high wind
# conditions. Rather, seasonal forecasting focuses more on the statistical properties
# over a period of time, be it a 10-day interval, a month, or even a three month season.
# The verification of a new, forward looking seasonal forecast requires assessments of
# the forecast systems ability to appropriately forecast that longrange behavior of the
# weather (here, only atmospheric verification is considered, but the same concept would
# apply ocean or any other longrange forecast system). Because weather properties
# commonly change significantly over the course of the season, samples to verify the
# prognostic system can not be taken from the immediate days, weeks of months before the
# forecast. Hindcasting in the seasonal context requires a complete set of forecasts
# based on the same season but during past years. A current July-1 2019 forecast, therefore
# requires many July-1 forecasts for as many years in the past as possible, given that
# the forecast system is the same as the one used for the current forecast cycle into the
# future. Operational centers offer hindcasts, also sometimes called "re-forecasts", with
# the current, most up-to-date forecast system. MET and METplus therefore need to be able
# to extract the appropriate collection of past forecasts. This includes the identification
# of the same Julian-day-of-Year init-dates from forecasts cycles from past years, and then
# identify the different lead-times of interest generally ranging from one to 6 or more
# months.
#
# Verification
# The verification steps can then utilize the existing collection of verification tools.
# In comparison to weather forecasts, the only difference is that the data, as stated
# above, are not snapshots but time-integrated values (averages, sums, statistics) that
# are representing a whole period of time. The verification then focuses on comparisons
# of these derivatives of the forecast simulations. In practice, a further step might be
# added prior to, or as a key step during verification: the formation of anomalies of the
# forecasts compared to long-term expected averages. A rainfall forecasts can therefore
# be verified in both absolute as well as anomaly context where some analyses might focus
# on extreme rainfall threshold exeedance of, for example, 500mm per month. At the same
# time, the same forecast might be verified for the 3 months rainfall average in comparison
# with the long-term expected mean. The verification might then assess how well the system
# can foresee the occurrence of below average rainfall over the season, and possibly some
# selected thresholds there (e.g., ability to forecast mean seasonal rainfall below
# the 10-th percentile of seasonal rainfall). Finally, flexibility in formulating forecast
# verification strategies is important as forecast skill might vary by location, the timing
# within the seasonal cycle, or the state of the evolving coupled system (the rapid onset
# of a strong El Nino will lead to significantly different forecast skill compared to a
# neutral state in the Pacific). Memory from past months, for example when considering
# accumulated soil moisture, might also influence the forecast skills. Seasonal forecast
# verification therefore requires understanding of the climate system; MET and METplus
# then need to offer the flexibility to tailor verification strategies and to potentially
# craft conditional approaches.
#
# Overall, seasonal forecasts don't require a new verification approach. It does however
# put demands on the flexibility of dealing with a significantly exapanded range of the
# time variable as well as logistic infrastructure to select appropriate hindcast samples
# from long hindcast or re-forecast archives. Scientifically, the challenges are mostly
# restricted in the appropriate formulation of verificaation questions that address
# specific forecast objectives. Compared to weather forecastsing, seasonal forecasts need
# to draw their skill from slowly changing components in the coupled Earth system while
# acknowledging the high-frequency noise of weather superposed on these 'climatologically'
# evolving background conditions. In many regions of the world, the noise might dominate
# that background climate and forecast skill is low. It is therefore the task of seasonal
# forecast verification to identify where there is actually skill for particular properties
# of the forecasts over a wide range of lead-times. The skill might be dependent on
# location, on the timing within the seasonal cycle, or even on the evolving state of the
# coupled system.

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
#

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#  GridStat
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
# Because not all of MET has been wrapped with python into METplus, the application of
# seasonal forecast verification is split into two steps:
#
# 1.	work with ~30-years of hindcasts to determine how well forecasting mechanisms worked
# 	in the past. This is done using the python-wrapped tools of METplus that are ready
# 	for automated processing using the GridStat tool.
# 2.	select one or more verification criteria and investigate these in context of the
# 	hindcast archive to generate a mask that then is applied to the actual forecast.
# 	This step users StatAnalysis, an element of MET that has not yet been wrapped in
# 	python (METplus), and thus it needs to be run directly under MET.
#
# Step 1: GridStat using METplus
# In order to run the python-based METplus packages, the user needs to issue a command to
# activate the appropriate version of python on the system. In the virtual machine delivered
# to BMKG, this is done with the following command:
#
# 		conda activate py3.6.3
#
# The GridStat tool is driven by the following ASCII configuration and run-scripts:
# •	METplus: run_grid_stat_metplus.bash sets key variables and executes the
# 	master_metplus.py with configurations. Look for …/ush/master_metplus.py call:
# •	user-config: “apik.conf”: defines which met version is used, where input data is to
# 	be found, and where output. It also provides the filters for the formats of both input
# 	and output.
# •	met_config: contains “GridStatConfig_APIK_S2S_use_case_1” where it sets all the
# 	GridStat parameters for data handling as well as types of statistics to be computed.
# •	use-case config: points to the specific configuration file, in this case
# 	“grid_to_grid_s2s_use_case_1_August-December.conf”, though a separate configuration
# 	file for the 6th month of the example is needed because the forecast for January is
# 	located in a file with a year parameter that is advanced over August through December.
# 	In future versions this separation will not be necessary.
#
# Step 2: SeriesAnalysis and StatAnalysis using MET
# The SeriesAnalysis and StatAnalysis tools are core MET tools that offer analysis
# capabilities based on prior processing and calculation steps. Series Analysis can
# generate initial products, but it can also pickup secondary products and analyze
# them in a time-series context. For the purpose of the use case, two sequential
# calculations are necessary. First, a summary of each statistical quantity has to be
# computed across the different hindcast cases (each of which had been processed separately
# before). This includes the application of thresholds and counting of occurrences above or
# below these thresholds. Then second, based on these climatologies, the full statistics
# can now be computed across the collection to provide the overall skill computation
# within the hindcast context.
#
# The following scripts define the process:
# 	MET run script: run_sereis_analysis.bash sets all key configurations determining
# 	input and output data, provides templates for reading variables inside the statistics
# 	files. Because this part of MET has not yet been “python-wrapped”, the run-script has
# 	to cover many aspects of the configuration that in METplus are better generalized.
# 	SeriesAnalysis Climatology: ”config/SeriesAnalysisConfig_APIK_S2S_use_case_ 1_climo”
# 	contains the parameters that calculate the climatological mean difference between the
# 	hindcast experiments and their associated observations.
# 	SeriesAnalysis 2: “config/SeriesAnalsyisConfig_APIK_S2S_use_case_1_full_stats”
# 	contains all necessary configurations to compute the skill statistics. The options for
# 	these statistics are listed in the MET-Users Guide. There are many options, and
# 	turning them on is done in the context of the different groups or “packages”.



##############################################################################
# METplus Configuration
# ---------------------
#
# .. highlight:: none
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/seasonal_forecast.conf

##############################################################################
# Running METplus
# ---------------
# This use case can be run two ways:
#
# 1) Passing in seasonal_forecast.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/seasonal_forecast.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in seasonal_forecast.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/seasonal_forecast.conf
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
#  ------  METplus is run via a bash script -------
#
#

#PROJECT="APIK"
# Set the path to the version of METplus you will run
#
# METPLUS_BASE_DIR="/opt/utilities/METplus_feature_281_py_embed" 	# development version
# The repository that contains the stand-alone use case
#
#PROJECT_CODE_DIR=${PROJECT_BASE_DIR}/${PROJECT}/"METplus-for-Indonesia-APIK"
# inside the repository, here is the preliminary-release specific user configuration:
#
#USER_CONFIG_DIR=${PROJECT_BASE_DIR}/${PROJECT}/"METplus-for-Indonesia-APIK/METplus_feature_281_py_embed_parm/user_config"
#  ... and the
#USE_CASE_CONFIG_PATH=${PROJECT_CODE_DIR}/"METplus_feature_281_py_embed_parm/examples"
# -------  METplus Execution --------- #
#
# Now the execution of METplus following a specified use case config file and user config files
#
# point to configuration file
# USE_CASE_CONFIG_FILENAME="grid_to_grid_s2s_use_case_1_August-December.conf"
# now launch the METplus python master script
#
# echo "${METPLUS_BASE_DIR}/ush/master_metplus.py -c ${USER_CONFIG_DIR}/apik.conf -c ${USE_CASE_CONFIG_PATH}/${USE_CASE_CONFIG_FILENAME}"
#${METPLUS_BASE_DIR}/ush/master_metplus.py -c ${USER_CONFIG_DIR}/apik.conf -c ${USE_CASE_CONFIG_PATH}/${USE_CASE_CONFIG_FILENAME}
#



##############################################################################
# Expected Output
# ---------------
#
# For each month and year there will be two files written::
#
# * grid_stat_NMME-hindcast_precip_vs_CPC_IC{%Y}{%N}01_2301360000L_20081001_000000V.stat
# * grid_stat_NMME-hindcast_precip_vs_CPC_IC{%Y}{%N}01_2301360000L_20081001_000000V_pairs.nc


##############################################################################
# Keywords
# --------
#
# .. note:: `GridStatUseCase <https://ncar.github.io/METplus/search.html?q=GridStatUseCase&check_keywords=yes&area=default>`_

