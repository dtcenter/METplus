"""
Bias Plot on Zonal Mean Wind and Temperature: UserScript, Series-Analysis
==========================================================================

model_applications/
s2s/
UserScript_fcstGFS_obsERA_StratosphereBias.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# This use case calls functions in METcalcpy to create zonal and meridonial 
# means on U and T.  It then runs Series-Analysis on the output zonal means 
# and creates a contour plot of bias in latitude and pressure level.
#

##############################################################################
# Datasets
# --------
#
# GFS_2018_02_24h.nc
# ERA_2018_02.nc
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, zonal_mean_driver.py, runs Series-Analysis to compute the bias,
# and then runs another UserScript, bias_plot_driver.py, to create the bias plots.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots the entire time period of data
# 
# UserScript: Computes zonal and meridional means
# Series-Analysis: Computes the bias on zonal mean wind and temperature
# UserScript: Creates bias plots
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratosphereBias.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratosphereBias.conf
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
# **SeriesAnalysisConfig_wrapped**
#
# .. note:: See the :ref:`Series-Analysis MET Configuration<series-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read in the zonal mean data to Series-Analysis
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratosphereBias/read_met_axis_mean.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_StratosphereBias.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratosphereBias.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_StratosphereBias.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratosphereBias.conf
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

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * S2SAppUseCase
#   * SeriesAnalysisUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-UserScript_fcstGFS_obsERA_StratosphereBias.png'
