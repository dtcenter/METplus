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
# This use case calls functions in METcalcpy to create zonal and meridonial 
# means on U from -10 S to 10N latitude between 100 and 10 hpa.  It then runs 
# creates 2 phase plots, phase circuits which gives one plot for each start date
# listed in the configuration file for model and observations, and another phase plot 
# for the whole time period 
#

##############################################################################
# Datasets
# --------
#
# GFS 0-24 hour forecasts for TIME PERIOD
# ERA for TIME PERIOD
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, stratosphere_qbo_driver.py to compute the zonal and meridional
# mean, compute anomalies and create phase plots.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots the entire time period of data
# 
# UserScript: Computes zonal and meridional means, anomalies, EOFs and creates phase plots
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf
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
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_StratosphereQBO.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_StratosphereQBO.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratosphereQBO.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  No executables are required for performing this use case.
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
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
# There should be 2 graphics output, ERA_GFS_QBO_circuits.png and ERA5_QBO_PhaseSpace.png
# These graphics will be output to the path specified in PLOT_PHASE_CIRCUITS_OUTPUT_NAME
# and PLOT_PHASE_SPACE_OUTPUT_NAME in the [user_env_vars] section. 
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
