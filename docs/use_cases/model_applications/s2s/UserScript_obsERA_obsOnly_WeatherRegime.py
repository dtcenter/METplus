"""
WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code
=====================================================================================

model_applications/
s2s/
UserScript_obsERA_obsOnly_WeatherRegime.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To perform a weather regime analysis using 500 mb height data.  There are 2 pre-
# processing steps, RegridDataPlane and PcpCombine, and 3 steps in the weather regime 
# analysis, elbow, EOFs, and K means.  The elbow and K means steps begin with K means
# clustering.  Elbow then computes the sum of squared distances for clusters 1 - 14 
# and draws a straight line from the sum of squared distance for the clusters.  This 
# helps determine the optimal cluster number by examining the largest difference between 
# the curve and the straight line.  The EOFs step is optional.  It computes an empirical 
# orthogonal function analysis.  The K means step uses clustering to compute the 
# frequency of occurrernce and anomalies for each cluster to give the most common
# weather regimes.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: None 
#  * Observation dataset: ERA Reanlaysis 500 mb height.

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed::
#
# * numpy
# * netCDF4
# * datetime
# * pylab
# * scipy
# * sklearn
# * eofs
#
# If the version of Python used to compile MET did not have these libraries at the time of compilation, you will need to add these packages or create a new Python environment with these packages.
#
# If this is the case, you will need to set the MET_PYTHON_EXE environment variable to the path of the version of Python you want to use. If you want this version of Python to only apply to this use case, set it in the [user_env_vars] section of a METplus configuration file.:
#
#    [user_env_vars]
#    MET_PYTHON_EXE = /path/to/python/with/required/packages/bin/python
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the weather regime driver script which runs the steps the user
# lists in STEPS_OBS.  The possible steps are regridding, time averaging, computing the 
# elbow (ELBOW), plotting the elbow (PLOTELBOW), computing EOFs (EOF), plotting EOFs 
# (PLOTEOF), computing K means (KMEANS), and plotting the K means (PLOTKMEANS).  Regridding 
# and time averaging are set up in the UserScript .conf file and are formatted as follows:
# PROCESS_LIST = RegridDataPlane(regrid_obs), PcpCombine(daily_mean_obs), UserScript(script_wr)
#
# The other steps are listed in the weather regime analsysis .conf file
# in the following format:
# OBS_STEPS = ELBOW+PLOTELBOW+EOF+PLOTEOF+KMEANS+PLOTKMEANS

##############################################################################
# METplus Workflow
# ----------------
#
# The weather regime python code is run for each time for the forecast and observations 
# data. This example loops by valid time.  This version is set to only process the weather 
# regime steps (ELBOW, PLOTELBOW, EOF, PLOTEOF, KMEANS, PLOTKMEANS), omitting the REGRID 
# and TIMEAVE pre-processing steps.  However, the configurations for pre-processing are
# available for user reference.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.py.  
# The file UserScript_obsERA_obsOnly_WeatherRegime.conf runs the python program, however
# UserScript_obsERA_obsOnly_Blocking/WeatherRegime_obsERA_obsOnly.conf sets the variables 
# for all steps of the Weather Regime use case including data paths.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane.py
# parm/use_cases/met_tool_wrapper/PCPCombine/PCPCOmbine_derive.py

##############################################################################
# Python Scripts
# ----------------
#
# This use case uses Python scripts to perform the blocking calculation
#
# parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime_driver.py:
# This script calls the requested steps in the blocking analysis for a forecast, observation, or both.  The possible
# steps are computing the elbow, computing EOFs, and computing weather regimes using k means clustering.
#
# parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime.py:
# This script runs the requested steps, containing the code for computing the bend in the elbow, computing EOFs, and
# computing weather regimes using k means clustering 
#
# parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/Blocking_WeatherRegime_util.py:
# This script contains functions used by both the blocking anwd weather regime analysis, including the code for
# determining which steps the user wants to run, and finding and reading the input files in the format from the output
# pre-processing steps
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime_driver.py
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/WeatherRegime.py
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime/Blocking_WeatherRegime_util.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in UserScript_obsERA_obsOnly_WeatherRegime.py then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.py -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_obsERA_obsOnly_WeatherRegime.py::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.py
#
# The following variables must be set correctly:
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

##############################################################################
# Expected Output
# ---------------
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in model_applications/s2s/WeatherRegime (relative to **OUTPUT_BASE**) and will contain output 
# for the steps requested.  This may include the regridded data, daily averaged files, and a weather regime output 
# file.  In addition, output elbow, EOF, and Kmeans weather regime plots can be generated.  The location
# of these output plots can be specified as WR_OUTPUT_DIR.  If it is not specified, plots will be sent 
# to model_applications/s2s/WeatherRegime/plots (relative to **OUTPUT_BASE**).

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/s2s-OBS_ERA_weather_regime.png'
#
# .. note:: `RegridDataPlaneUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneUseCase&check_keywords=yes&area=default>`_,
#  `PCPCombineUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineUseCase&check_keywords=yes&area=default>`_, 
#  `S2SAppUseCase <https://dtcenter.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_, 
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
