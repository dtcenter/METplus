"""
UserScript: Calculate Weather Regimes for ERA and possibly RegridDataPlane and PcpCombine
=========================================================================================

model_applications/
s2s_mid_lat/
UserScript_obsERA_obsOnly_WeatherRegime.py

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
# clustering for the ERA observations.  It also computes the frequency of occurrence of each
# weather regime over a 7 day period.  The code for computing weather regimes comes from Douglas Miller.
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
# **Forecast dataset:** None. 
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
# **Sequence of forecast leads to process (LEAD_SEQ):** 24
#
# This use case does not loop, but the UserScript that runs the weather regime driver script
# is run once over the entire time period.  The weather regime driver script performs the weather 
# regime calculation for the observations.  This calculation is divided up into steps, which the 
# user can select by setting STEPS_OBS in the [user_env_vars] section of the configuration.  More 
# information on the steps and how the calculation proceeds is given in the User Scripting section below.
#
# The two optional pre-processing steps loop by valid time when they are turned on, with different timing
# settings needed for the different steps.  These steps are turned off due to data size and processing 
# time.  The first optional step calls Regrid-Data-Plane to regrid the data to a 1 degree latitude/longitude
# grid.  The second calls PCP-Combine to compute daily means.  These omitted steps can be turned back on by 
# using the PROCESS_LIST that is commented out:
#
# PROCESS_LIST = RegridDataPlane(regrid_obs), PcpCombine(daily_mean_obs), UserScript(script_wr)
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
# parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherREgime.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.conf

##############################################################################
# MET Configuration
# ---------------------
#
# This case does not use MET configuration files.

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
# of the weather regime calculation that are specified in OBS_STEPS in the [user_env_vars] 
# section of the UserScript .conf file.  All steps are run for this use case, as specified 
# in the following format:
#
#  | OBS_STEPS = ELBOW+PLOTELBOW+EOF+PLOTEOF+KMEANS+PLOTKMEANS+TIMEFREQ+PLOTFREQ
#
# The possible steps are computing the elbow or optimal number of clusters (ELBOW), plotting the elbow 
# (PLOTELBOW), computing EOFs (EOF), plotting EOFs (PLOTEOF), computing the weather regimes using
# K means clustering (KMEANS), plotting the weather regimes (PLOTKMEANS), computing a user specified
# time frequency of weather regimes (TIMEFREQ) and plotting the time frequency (PLOTFREQ).  The 
# TIMEFREQ and PLOTFREQ steps require that the KMEANS step be run first, while all other steps 
# can be run individally. Input variables to the WeatherRegime driver are both set and described
# in the [user_env_vars] section of the configuration file. 
#
# Elbow computes the optimal number of clusters using the sum of squared distances for 
# clusters 1 - 14 and draws a straight line from the sum of squared distance for the 
# clusters.  This helps determine the optimal cluster number by examining the largest 
# difference between the curve and the straight line.  The EOFs step computes empirical orthogonal 
# functions.  The K means step uses clustering to compute the frequency of occurrence and anomalies 
# for each cluster to give the most common weather regimes.  Then, the time frequency computes the 
# frequency of each weather regime over a user specified time frame.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime_driver.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.conf /path/to/user_system.conf
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
# and will contain output for the steps requested.  The output includes 4 plots in the plots directory::
#
# * obs_elbow.png
# * obs_eof.png
# * obs_kmeans.png
# * obs_freq.png
#
# The output also includes a daily classification of weather regimes as a text file::
#
# * obs_weather_regime_class.txt
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
# sphinx_gallery_thumbnail_path = '_static/s2s_mid_lat-UserScript_obsERA_obsOnly_WeatherRegime.png'
