"""
Grid-Stat: Surrogate Severe and Practically Perfect Probabilistic Evaluation 
============================================================================

model_applications/
convection_allowing_models/
GridStat_fcstHRRR_obsPracPerfect
_SurrogateSevereProb.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To evaluate the surrogate severe forecasts at predicting Severe weather
# using the (12Z - 12Z) practically perfect storm reports an obtain 
# probabilistic output statistics.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRR Surrogate Severe Data
#  * Observation dataset: Practically Perfect from Local Storm Reports
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs grid_stat to create probabilistic statistics on 
# surrogate severe from the HRRR model and Practially Perfect observations 
# computed from local storm reports.  

##############################################################################
# METplus Workflow
# ----------------
#
# The grid_stat tool is run for each time. This example loops by valid time.  It
# processes 1 valid time, listed below.
#
# | **Valid:** 2020-02-06_12Z
# | **Forecast lead:** 36

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevereProb.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/GridStatConfig_ss_prob
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/GridStat/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevereProb.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevereProb.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
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
# **NOTE:** All of these items must be found under the [dir] section.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in model_applications/convection_allowing_models/surrogate_severe_prac_perfect/grid_stat/prob (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# grid_stat_360000L_20200206_120000V_pct.txt
# grid_stat_360000L_20200206_120000V_pjc.txt
# grid_stat_360000L_20200206_120000V_prc.txt
# grid_stat_360000L_20200206_120000V_pstd.txt
# grid_stat_360000L_20200206_120000V.stat

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-SS_PP_prob.png'
#
# .. note:: `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_, 
#  `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_, 
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_, 
#  `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,  
#  `NCAROrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_
#  `NOAAHMTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,  
