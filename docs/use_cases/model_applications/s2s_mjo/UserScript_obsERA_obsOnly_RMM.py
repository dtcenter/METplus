"""
UserScript: Make ERA RMM plots from calculated MJO indices
==========================================================

model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.py

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
# The Madden-Julian Oscillation (MJO) is the largest element of intraseasonal variability in the 
# tropics and is characterized by eastward moving regions of enhanced and suppressed rainfall.  These
# phases are typically grouped into numbers 1 - 8 based on the geographic location of the enhanced and 
# suppressed rainfall.  The MJO affects global weather including summer monsoons, tropical cyclone 
# development, and sudden stratospheric warming events, and has teleconnections to mid latitude weather
# systems.  
# 
# This use case uses anomalies of outgoing longwave radiation (OLR), 850 hPa wind (U850), and 200 hPa 
# wind (U200) to compute the Real-time Multivariate MJO Index (RMM).  In contrast to OMI, which is a 
# convective index of MJO, RMM is a dynamical index.  The code for computing RMM came from Maria
# Gehne at the NOAA Physical Sciences Laboratory (PSL).

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1.0

##############################################################################
# Datasets
# --------
#
# **Forecast:**  None
#
# **Observation:** ERA Reanlaysis Outgoing Longwave Radiation, 850 hPa wind and 200 hPa wind, 2000 - 2002
# 
# **EOFs:** EOF patterns for OLR, U850, and U200 from Matthew Wheeler
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
# This use case calls UserScript 5 times and Regrid-Data-Plane three times.  The UserScript calls run
# the harmonic pre-processing on all three variables, create a filelist, and run the RMM calculation.
# There are four optional pre-processing steps.
#
# This use case requires METcalcpy, METplotpy, and METdataio to run. The METcalcpy scripts accessed include the following:
#
# * metcalcpy/contributed/rmm_omi/compute_mjo_indices.py
#
# The METplotpy scripts accessed include the following:
#
# * metplotpy/contributed/mjo_rmm_omi/plot_mjo_indioces.py
#
# The METdataio scripts accessed include the following:
#
# * METreadnc/util/read_netcdf.py

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 01-01-2000
#
# **End time (VALID_END):** 12-30-2002
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# # The UserScript calls do not loop, but are each run once.  The first call creates a list of 
# the mean daily annual data files for OLR, U850, and U200. It is done separately since the mean 
# daily annual files span across all years whereas the RMM calculation can proceed on a different 
# time frame.  The second, third, and fourth calls to UserScript run the pre-processing to compute
# anomalies OLR, U850, and U200 using a harmonic analysis program in python.  Then, RegridDataPlane is 
# run for all valid times for the 3 variables.  This step cuts the grid to only include -15 to 15 latitude.  
# Finally, the last (fifth) call to UserScript runs the RMM calculation once on the observations.
#
# There are four optional pre-processing steps loop by valid time with different timing settings needed for 
# the different steps.  These steps are turned off due to data size and processing time.  Two of the steps are 
# calls to Pcp-Combine to compute the mean daily annual data for OLR, wind (U850 and U200).  The other two steps 
# also call Pcp-Combine but these compute daily means for OLR and wind.  These omitted steps can be turned back 
# on by using the PROCESS_LIST that is commented out in the file:
#
# PROCESS_LIST = PcpCombine(mean_daily_annual_cycle_obs_wind), PcpCombine(mean_daily_annual_cycle_obs_olr), PcpCombine(daily_mean_obs_wind), PcpCombine(daily_mean_obs_olr), UserScript(create_mda_filelist), UserScript(harmonic_anomalies_olr), UserScript(harmonic_anomalies_u850), UserScript(harmonic_anomalies_u200), RegridDataPlane(regrid_obs_olr), RegridDataPlane(regrid_obs_u850), RegridDataPlane(regrid_obs_u200), UserScript(script_rmm)
#
# Settings for the optional pre-processing steps can be found in the respective sections of the configuration, 
# mean_daily_annual_cycle_obs_wind, mean_daily_annual_cycle_obs_olr, daily_mean_obs_wind, and daily_mean_obs_olr.  
# Data is not provided in the tarball to run these steps, but the configurations is provided for reference on how 
# to set up these calculations.
#
# The Phase diagram and timeseries plots are created over a different time frame, 01-01-2002 
# to 12-30-2002 for both plots.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.conf.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.conf

##############################################################################
# MET Configuration
# -----------------
#
# There are no MET configuration files used in this use case.

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# There are two Python scripts used in this use case.  The RMM driver script (RMM_driver.py) 
# orchestrates the calculation of the MJO indices and the generation of three RMM plots.  The 
# calculation proceeds using OLR, U850, and U200 data between 15N and 15S.  The 120 day mean is first 
# removed and the data are normalized by normalization factors (generally the square root of the 
# average variance).  The anomalies are projected onto Empirical Orthogonal Function (EOF) data.  The 
# OLR is then filtered for 20 - 96 days, and regressed onto the daily EOFs.  Finally, it's normalized 
# and these normalized components are plotted on a phase diagram and timeseries plot.
#
# The anomalies are created using a harmonic analysis for OLR, U850, and U200 with the python script
# compute_harmonic_anomalies.py.  Input to the harmonic analysis script include a text file containing the
# list of input files, the daily mean variable name, mean daily average varable name, output directory and output file 
# basename.  These are defined in the [harmonic_anomalies_olr], [harmonic_anomalies_u850], and harmonic_anomalies_u200] 
# sections of the configuration file.  Additional variables for the RMM calculation and harmonic analysis are set in the 
# [user_env_vars] section of the .conf file.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/RMM_driver.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/RMM_driver.py
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/compute_harmonic_anomalies.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/compute_harmonic_anomalies.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_obsERA_obsOnly_RMM.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in {OUTPUT_BASE}/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/plots.  The
# output may include the regridded data and daily averaged files if those steps are turned on.  Three output
# plots will be generated, a phase diagram, time series, and EOF plot::
#
#  * obs_RMM_comp_phase.png
#  * obs_RMM_time_series.png
#  * RMM_EOFs.png
#
# Output from the Harmonic analysis pre-processing includes multiple files, one for each variable and day in the 
# following format::
#
# * ERA_OLR_anom_000000L_YYYYMMDD_000000V.nc
# * ERA_U200_anom_000000L_YYYYMMDD_000000V.nc
# * ERA_U850_anom_000000L_YYYYMMDD_000000V.nc
#
# One variabe is output in each of the above files (not including the lat/lon fields). Those variables are::
#
# * olr_anom(lat, lon)
# * U_P200_mean_anom(lat, lon)
# * U_P850_mean_anom(lat, lon)
#
# Output from the regridding also includes one file for each day and variable with the following format::
#
# * ERA_OLR_YYYYMMDD.nc
# * ERA_U200_YYYYMMDD.nc
# * ERA_U850_YYYYMMDD.nc
#
# One variabe is output in each of the regriddwed files (not including the lat/lon fields). Those variables 
# are::
#
# * OLR_anom(lat, lon)
# * U_P200_anom(lat, lon)
# * U_P850_anom(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SMJOAppUseCase
#   * NetCDFFileUseCase
#   * RegridDataPlaneUseCase
#   * PCPCombineUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_obsERA_obsOnly_RMM.png'
