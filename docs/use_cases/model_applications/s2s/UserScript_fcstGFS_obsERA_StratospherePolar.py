"""
Bias Plot on Zonal Mean Wind and Temperature: UserScript, Stat-Analysis
========================================================================

model_applications/
s2s/
UserScript_fcstGFS_obsERA_StratospherePolar.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# This use case calls functions in METcalcpy to create polar cap temperature 
# and polar vortex wind.  It then runs Stat-Analysis on the output zonal means 
# and creates a contour plot of bias in lead time and pressure level.
#

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: GFS Forecast U and T at multiple pressure levels
#  * Observation dataset: ERA Reanlaysis U and T at multiple pressure levels
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, polar_t_u_driver.py which output data into MET's matched pair format.  
# It then runs Stat-Analysis to compute the bias and RMSE, and another UserScript, 
# bias_rmse_plot_driver.py, to create the plots.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case loops over lead times for the first UserScript and Stat-Analysis,
# and the plotting proceeds over the entire time period
# 
# UserScript: Computes polar cap temperature and polar vortex U
# Stat-Analysis: Computes ME and RMSE on polar cap temperature and polar vortex U
# UserScript: Creates ME and RMSE plots
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratospherePolar.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratospherePolar.conf
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
# **STATAnalysisConfig_wrapped**
#
# .. note:: See the :ref:`Series-Analysis MET Configuration<series-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_StratospherePolar.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratospherePolar.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_StratospherePolar.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_StratospherePolar.conf
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
#   * StatAnalysisUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-UserScript_fcstGFS_obsERA_StratospherePolar.png'
