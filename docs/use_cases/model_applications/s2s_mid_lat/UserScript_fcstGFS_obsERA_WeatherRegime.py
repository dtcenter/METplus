"""
UserScript and StatAnalysis: Calculate and evaluate Weather Regimes for GFS and ERA
===================================================================================

model_applications/
s2s_mid_lat/
UserScript_fcstGFS_obsERA_WeatherRegime.py

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
# Weather regimes are defined as atmospheric patterns with high likelihoods of recurrence.
# They can modulate many atmospheric phenomena including tornado and severe weather 
# occurrence.  This use case computes the top 6 most frequent weather regimes using K-means
# clustering for the forecast and observations, and computes multi-category contingency table
# statistics on these regimes.  It also computes the frequency of occurrence of each
# weather regime over a 7 day period for the forecast and observation and continuous
# statistics are computed comparing these two frequencies.
#
# The code for computing weather regimes comes from Douglas Miller.
#
# * Miller, D. E., Wang, Z., Trapp, R. J., &Harnos, D. S., 2020: Hybrid prediction of weekly tornado activity out to Week 3: Utilizing weather regimes. Geophysical Research Letters, 47, https://doi.org/10.1029/2020GL087253. 

##############################################################################
# Version Added
# -------------
#
# METplus version 4.0.0 

##############################################################################
# Datasets
# --------
#
# **Forecast dataset:** GFS Forecast 500 mb height. 
#
# **Observation dataset:** ERA Reanlaysis 500 mb height.
#
# **Climatology:** None.
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
# This use case calles UserScript once and Stat-Analysis twice.  There are two optional
# pre-processing steps, Regrid-Data-Plane and PCP-Combine.  Additionally, METcalcpy
# and METplotpy are required to run this use case.  The METcalcpy scripts accessed include
# the following:
#
# * metcalcpy/contributed/blocking_weather_regime/WeatherRegime.py
#
# * metcalcpy/contributed/blocking_weather_regime/Blocking_WeatherRegime_util.py
#
# * metcalcpy/util/write_mpr.py
#
# The METplopty scrips accessed include the following:
#
# * metplotpy/contributed/weather_regime/plot_weather_regime.py

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 12-01-2000
#
# **End time (VALID_END):** 02-28-2017
#
# **Increment between beginning and end times (VALID_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24H
#
# This use case does not loop, but the UserScript and both calls to Stat-Analysis are
# each run once.  The UserScript runs the weather regime driver script.  The weather regime
# driver script performs the weather regime calculation for the forecast and observation.  This 
# calculation is divided up into steps, which the user can select by setting STEPS_FCST and 
# STEPS_OBS in the [user_env_vars] section of the configuration.  More information on the steps and 
# how the calculation proceeds is given in the User Scripting section below.
#
# The two optional pre-processing steps loop by valid time when they are turned on, with different timing
# settings needed for the different steps.  These steps are turned off due to data size and processing 
# time.  The first optional step calls Regrid-Data-Plane to regrid the data to a 1 degree latitude/longitude
# grid.  The second calls PCP-Combine to compute daily means.  These omitted steps can be turned back on by 
# using the PROCESS_LIST that is commented out:
#
# PROCESS_LIST = RegridDataPlane(regrid_obs), PcpCombine(daily_mean_obs), UserScript(script_wr), StatAnalysis(sanal_wrclass), StatAnalysis(sanal_wrfreq)
#
# Settings for the optional pre-processing steps can be found in the respective sections of the configuration,
# regrid_obs and daily_mean_obs.  Data is not provided in the tarball to run these steps, but the 
# configurations are provided for reference on how to set up these calculations.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, i.e
# parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: StatAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding

##############################################################################
# User Scripting
# --------------
#
# This use case runs WeatherRegime_driver.py.  This driver script runs the selected steps
# of the weather regime calculation that are specified in FCST_STEPS and OBS_STEPS in the
# [user_env_vars] section of the UserScript .conf file.  All steps are run for this use
# case, as specified in the following format:
#
#  | OBS_STEPS = ELBOW+PLOTELBOW+EOF+PLOTEOF+KMEANS+PLOTKMEANS+TIMEFREQ+PLOTFREQ
#  | FCST_STEPS = ELBOW+PLOTELBOW+EOF+PLOTEOF+KMEANS+PLOTKMEANS+TIMEFREQ+PLOTFREQ
#
# The possible steps are computing the elbow or optimal number of clusters (ELBOW), plotting the elbow 
# (PLOTELBOW), computing EOFs (EOF), plotting EOFs (PLOTEOF), computing the weather regimes using
# K means clustering (KMEANS), plotting the weather regimes (PLOTKMEANS), computing a user specified
# time frequency of weather regimes (TIMEFREQ) and plotting the time frequency (PLOTFREQ).  The 
# TIMEFREQ and PLOTFREQ steps require that the KMEANS step be run first, while the ELBOW, EOF, and 
# KMEANS steps can be run individally. Input variables to the WeatherRegime driver are set and 
# described in the [user_env_vars] section of the configuration file. 
#
# Elbow computes the optimal number of clusters using the sum of squared distances for 
# clusters 1 - 14 and draws a straight line from the sum of squared distance for the 
# clusters.  This helps determine the optimal cluster number by examining the largest 
# difference between the curve and the straight line.  The EOFs step computes empirical orthogonal 
# functions.  These EOFs are used to reconstruct the height field, with this reconstructed data used 
# in the K means calculation.  If EOFs are not compted, the original height field is used in the K means 
# calculation.  The K means step uses clustering to compute the frequency of occurrence and anomalies 
# for each cluster to give the most common weather regimes.  Then, the time frequency computes the 
# frequency of each weather regime over a user specified time frame.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime/WeatherRegime_driver.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime/WeatherRegime_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.conf /path/to/user_system.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output 
# for this use case will be found in {OUTPUT_BASE}/model_applications/s2s_mid_lat/WeatherRegime
# and will contain output for the steps requested.  The output includes 8 plots in the plots directory::
#
# * fcst_elbow.png
# * obs_elbow.png
# * fcst_eof.png
# * obs_eof.png
# * fcst_kmeans.png
# * obs_kmeans.png
# * fcst_freq.png
# * obs_freq.png
#
# The output also includes a daily classification of weather regimes as text files for both
# the forecast and observation::
#
# * fcst_weather_regime_class.txt
# * obs_weather_regime_class.txt
#
# There are numerous matched pair files output in two subdirectories of the mpr directory.  These contain
# output classified weather regimes and also the frequency for each weather regime.  For the classified 
# weather regimes, one file is written for each day to the WeatherRegime subdirectory (1513 files total)
# in the format below for 12-02-2000::
#
# * weather_regime_stat_GFS_240000L_20001202_000000V.stat
#
# for the frequency matched pair files, one file is written for each day and each weather regime (8466 files 
# total) to the freq subdirectory in the format below for 12-02-2000, weather regime 1::
#
# * weather_regime01_freq_stat_GFS_240000L_20001202_000000V.stat
#
# Stat-Analysis Output::
#
# * GFS_ERA_WRClass_240000L_MCTS.stat
# * GFS_ERA_WR_freq_240000L_CNT.stat
#
# If the pre-processing steps are turned on, the output will include the regridded data and daily averaged files. 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * RegridDataPlaneToolUseCase
#   * PCPCombineToolUseCase
#   * StatAnalysisToolUseCase
#   * S2SAppUseCase
#   * S2SMidLatAppUseCase
#   * NetCDFFileUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mid_lat-UserScript_fcstGFS_obsERA_WeatherRegime.png'
