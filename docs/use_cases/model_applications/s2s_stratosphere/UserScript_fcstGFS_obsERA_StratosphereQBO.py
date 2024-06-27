"""
QBO Phase plots and QBO Index: UserScript, Stat-Analysis
==========================================================================

model_applications/
s2s_stratosphere/
UserScript_fcstGFS_obsERA_StratosphereQBO.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# Stratpheric evaluation is important because many common modes of variability in
# the troposphere have stratospheric teloconnection pathways.  This use case performs
# evaluation of the Quasi-biennial Oscillation (QBO) using several different calculations 
# and plots.  Specifically, phase diagrams can be used to compare the phase progression 
# between the model and observations.
#

##############################################################################
# Datasets
# --------
#
#  * GFS: 0-24 hour forecasts for 10/2017 - 2/2018
#  * ERA: 30 year climatology for EOFs and 10/2017 - 2/2018  
#

##############################################################################
# METplus Components
# ------------------
#
# This use case requires METcalcpy 3.0.0, METplotpy 3.0.0, and METdataio 2.1.
# Specifically, the case runs the UserScript wrapper tool to run a user provided script,
# stratosphere_qbo_driver.py.  The driver first computes zonal and meridional means
# using directional_means.py in METcalcpy on U from -10 S to 10N latitude.  Then, 
# an EOF analysis is performed on this zonal and meridional mean data, and two phase 
# diagrams of QBO are created using the plot_qbo_phase_circuits and plot_qbo_phase_space
# functions from stratosphere_plots.py in METplotpy.  Additionally the zonal and meridional 
# mean at 30 and 50mb are output as time series to matched pair (MPR) files using write_mpr.py 
# in METcalcpy and are also plotted as timeseries using the plot_u_timeseries function from 
# stratosphere_plots.py in METplotpy.  Finally StatAnalysis is run on the 30 and 50mb U mpr 
# files to compute the bias (ME).
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots the entire time period of data.  The 
# following tools are run once: UserScript, StatAnalysis
# 

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
#

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
# **StatAnalysisConfig_wrapped**
#
# .. note:: See the :ref:`Stat-Analysis MET Configuration<series-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding.
#

##############################################################################
# Python Scripting
# ----------------
#
# This use case runs the stratospher_qbo_driver.py python script.  The calculations
# performed in the script are detailed in the METplus Components section.
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any 
# user-specific system configuration files if desired:
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf /path/to/user_system.conf
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
# There should be 4 graphics output, ERA_GFS_QBO_circuits.png, ERA5_QBO_PhaseSpace.png,
# ERA_GFS_timeseries_30mb_u_201710_201802.png, and ERA_GFS_timeseries_30mb_u_201710_201802.png.
# These graphics will be output to the path specified as OUTPUT_DIR/plots, using 
# PLOT_PHASE_CIRCUITS_OUTPUT_NAME, PLOT_PHASE_SPACE_OUTPUT_NAME, PLOT_TIME_SERIES_OUTPUT_NAME_30,
# and PLOT_TIME_SERIES_OUTPUT_NAME_50 in the [user_env_vars] section.  Additionally matched pair
# .stat files will be output to OUTPUT_DIR/mpr, and the computed bias will be output to 
# OUTPUT_DIR/StatAnalysis.
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * S2SAppUseCase
#   * S2SStratosphereAppUseCase
#   * StatAnalysisUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_stratosphere-UserScript_fcstGFS_obsERA_StratosphereQBO.png'
