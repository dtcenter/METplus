"""
UserScript and StatAnalysis: Compute QBO Phase Plots and QBO Index
==================================================================

model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.py

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
# pathways.  This use case performs evaluation of the Quasi-biennial Oscillation (QBO),
# one of the key players of stratospheric variability, using several different calculations
# and plots.  Specifically, phase diagrams can be used to compare the QBO phase progression
# between the model and observations.  Additionally, timeseries of U at 30 and 50mb are also
# plotted to compare the speed of propagation of QBO in the model versus observations.  
# Continuous statistics (ME, RMSE, etc.) are calculated for U at 30 and 50mb and are also
# computed separately to evaluate QBO in the easterly phase versus the westerly phase.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS 0-24 hour forecasts for 10/2017 - 2/2018
#
# **Observation:** ERA 30 year climatology for EOFs and 10/2017 - 2/2018
#
# **EOFs:** EOFs computed for 10/1991 - 12/2020
#
# **Location:** Data for this use case is not contained in the sample data tar files 
# due to its size.  Rather, it is stored as additional data in a separate tar file,
# named additional_data_UserScript_fcstGFS_obsERA_StratosphereQBO.tar.gz and can be
# downloaded at https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/v6.0/.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls UserScript once and StatAnalysis once.  Additionally, METcalcpy,
# METplotpy, and METdataio are required to run.  The METcalcpy scripts accessed include 
# the following:
#
# * metcalcpy/pre_processing/directional_means.py
# 
# * metcalcpy/util/write_mpr.py
# 
# The METplotpy scripts accessed include the following:
#
# * metplotpy/contributed/stratosphere_diagnostics/stratosphere_plots.py
# 
# The METdataio scripts accessed include the following:
#
# * METreadnc/util/read_netcdf.py

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2018-02-01
#
# **End time (INIT_END):** 2018-02-28
#
# **Increment between beginning and end times (INIT_INCREMENT):** 30 days
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0, 3, 6, 9, 12, 15, 18, 21 hours
#
# This use case does not loop but UserScript and StatAnalysis are each run once using data
# from the entire time period.  The UserScript call runs stratosphere_qbo_driver.py to compute 
# a QBO index.  The output QBO index is run through Stat-Analysis to compute the continuous
# statistics.
#
# There is an optional step to calculate EOFs rather than providing an input file.  This 
# calculation is performed inside qbo_driver.py, but requires building a list of input 
# files to use to create EOFs using a call to UserScript.  This step is turned off due to 
# the length of time it needs to run, but can be turned back on using the PROCESS_LIST that 
# is commented out.  
#
# PROCESS_LIST = UserScript(create_obs_eofs_filelist), UserScript(compute_plot_qbo), StatAnalysis(qbo_bias)
#
# Other changes needed to calculate EOFs are described in the User Scripting section below.  Data is not 
# provided for the EOF calculation.
#
# METcalcpy 3.0.0 or higher, METplotpy 3.0.0 or higher, and METdataio 2.1 or higher are needed 
# for this use case.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, i.e
# parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf

#############################################################################
# MET Configuration
# ---------------------
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
# This use case runs the stratosphere_qbo_driver.py Python script, which first 
# computes zonal and meridional means using directional_means.py in METcalcpy on U from 
# -10 S to 10N latitude.  Then, an EOF analysis is performed on this zonal and meridional 
# mean data, and two phase diagrams of QBO are created using the plot_qbo_phase_circuits and 
# plot_qbo_phase_space functions from stratosphere_plots.py in METplotpy.  Additionally, the 
# zonal and meridional mean at 30 and 50mb are output as time series in MET's matched pair
# (MPR) format using write_mpr.py in METcalcpy.  They are also plotted as timeseries using the 
# plot_u_timeseries function from stratosphere_plots.py in METplotpy.  Finally, StatAnalysis is 
# run on the 30 and 50mb U mpr files to compute the bias (ME).
#
# Variables input to this script are given in the [user_env_vars] section of the configuration
# file.  As mentioned above, the option exists to compute EOFs inside the script.  To do this, 
# the COMPUTE_EOF_ZONAL_MERIDIONAL_MEAN variable should be set to true, and an input file list
# provided by turning on the UserScipt call for [create_eof_filelist].
#
# .. dropdown:: parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO/stratosphere_qbo_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO/stratosphere_qbo_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO
# There should be 4 graphics output to the plot directory::
#
#  * ERA_GFS_QBO_circuits.png
#  * ERA5_QBO_PhaseSpace.png
#  * ERA_GFS_timeseries_30mb_u_201710_201802.png
#  * ERA_GFS_timeseries_50mb_u_201710_201802.png
#
# Additionally matched pair .stat files for each day will be output to the mpr directory.  These 
# files have the following format::
#
# * qbo_u_GFS_210000L_YYYYMMDD_000000V.stat
#
# Two computed continuous statistics will be output to the StatAnalysis directory::
#
#  * GFS_ERA_20171001_20180228_210000L_zonal_wind_byphase_CNT.stat
#  * GFS_ERA_20171001_20180228_210000L_zonal_wind_CNT.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SStratosphereAppUseCase
#   * UserScriptUseCase
#   * StatAnalysisUseCase
#   * METdataioUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_stratosphere-UserScript_fcstGFS_obsERA_StratosphereQBO.png'
