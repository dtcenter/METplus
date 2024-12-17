"""
UserScript and SeriesAnalysis: Compute Zonal Mean Bias and Create Plots for Temperature and Wind
================================================================================================

model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias.py

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
# Many common modes of variability in the troposphere have stratospheric teleconnection
# pathways.  Thus, the stratosphere can be a source of predictability for surface weather.
# However, the predictive skill gained from the stratosphere can be limited by biases in 
# the representation of these stratospheric processes.  This use case investigates 
# stratospheric biases in temperature and wind.  Model biases are plotted for a month time
# period based on latitude and pressure between 100 and 1 hPa.
#
# In addition, this use case also demonstrates how to read semi-structured grids into
# MET.  Specifically zonal mean data (on a grid of latitude and pressure) is read into 
# Series-Analysis in the second step of this use case.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS 24 hour forecasts for February 2018
#
# **Observation:** ERA reanalysis for February 2018
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
# This use case calls UserScript first, Series-Analysis, and then UserScript
# a second time.  METcalcpy, METplotpy, and METdataio are needed for this use case to run.
# The metcalcpy scripts accessed include the following:
#
# * metcalcpy/pre_processing/directional_means.py
#
# The METplotpy scripts accessed include the following:
#
# * metplotpy/stratosphere_diagnostics/stratosphere_plots.py
#
# The METdataio scripts accessed include the following:
#
# * METreadnc/util/read_netcdf.py


##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 02-01-2018
#
# **End time (INIT_END):** 02-28-2018
#
# **Increment between beginning and end times (INIT_INCREMENT):** 30 days
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24
#
# This use case does not loop.  The two calls to UserScript are run once.  Series-
# Analysis is also run once.  The first call to UserScript runs zonal_mean_driver.py.  
# This script computes zonal and meridional mean data from the directional_means program in 
# METplotpy.  Then, Series-Analysis is run on the zonal mean output to compute
# continuous statistics.  Finally, the second call to UserScript runs bias_plot_driver.py
# which creates bias plots for temperature and wind.
#
# METcalcpy 3.0.0 or higher, METplotpy 3.0.0 or higher, and METdataio 2.1 or higher are needed 
# for this use case.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias.conf

#############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: SeriesAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read in the semi-structured zonal mean data to Series-Analysis.  Inputs to 
# this script include the filename to be read in, variable name, and the axis over which the mean is taken.  The script 
# returns a numpy array containing the zonal mean data (semi structured grid).
#
# .. dropdown:: read_met_axis_mean.py
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias/read_met_axis_mean.py

##############################################################################
# User Scripting
# --------------
#
# This use case runs both zonal_mean_driver.py and bias_plot_driver.py.  The zonal mean driver takes an input netCDF 
# file and the time variable.  Then it computes zonal and meridional means for u and T from directional_means.py in 
# METcalcpy.  It writes the zonal mean data to output netCDF files.
#
# The bias plot driver reads output netCDF files from Series-Analysis and creates plots of the bias over 
# latitude and pressure level.  Inputs to both of the python scripts can be found in the [user_env_vars]
# section of the UserScript_fcstGFS_obsERA_StratosphereBias.conf file
#
# .. dropdown:: parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias/zonal_mean_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias/zonal_mean_driver.py
#
# .. dropdown:: parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias/bias_plot_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias/bias_plot_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereBias.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar
# The output includes the netCDF zonal mean files for the forecast and observations, netCDF output 
# from Series-Analysis, and bias plots.  There are two bias plots output::
#
# * plots/GFS_ERA_ME_2018_02_zonal_mean_T.png
# * plots/GFS_ERA_ME_2018_02_zonal_mean_U.png
#
# The statistics output from Series-Analysis output is two netCDF files, one for temperature and one for wind::
#
# * SeriesAnalysis/zonal_mean_T_stats_2018_02.nc
# * SeriesAnalysis/zonal_mean_U_stats_2018_02.nc
#
# There are 7 variable fields present in the Series-Analysis output netCDF files (not 
# including the lat/lon fields).  Those variables are::
#
# * level(level)
# * n_series
# * series_cnt_TOTAL(lat, level)
# * series_cnt_ME(lat, level)
# * series_cnt_RMSE(lat, level)
# * series_cnt_FBAR(lat, level)
# * series_cnt_OBAR(lat, level)
#
# Text files with a listing of the files input to Series-Analysis are also output::
#
# * SeriesAnalysis/series_analysis_files_fcst_init_ALL_valid_ALL_lead_ALL.txt
# * SeriesAnalysis/series_analysis_files_obs_init_ALL_valid_ALL_lead_ALL.txt
#
# The zonal mean output includes 28 files for the forecast
# and observations, one for each day.  The file format for February 1 is::
#
# * FCST/FCST_zonal_mean_U_T_20180201_000000.nc
# * OBS/OBS_zonal_mean_U_T_20180201_000000.nc
#
# There are 4 variable fields present in the zonal mean netCDF file (not including the
# latitude and pressure fields). Those variables are::
#
# * time
# * u(pres, latitude)
# * T(pres, latitude)
# * lead_time

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * S2SAppUseCase
#   * S2SStratosphereAppUseCase
#   * SeriesAnalysisUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_stratosphere-UserScript_fcstGFS_obsERA_StratosphereBias.png'
