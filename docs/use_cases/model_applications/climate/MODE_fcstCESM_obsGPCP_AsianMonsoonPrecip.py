"""
MODE: CESM and GPCP Asian Monsoon Precipitation 
============================================================================
model_applications/climate/\
MODE_fcstCESM_obsGPCP_\
AsianMonsoonPrecip.conf
"""

##############################################################################
# Scientific Objective
# --------------------
#
# To evaluate the CESM model daily precipitation against the GPCP daily 
# precipitation over the Indian Monsoon region to obtain object based
# output statistics. This was developed as part of the NCAR System for
# Integrated Modeling of the Atmosphere (SIMA) project. 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: CESM Daily Precipitation
#  * Observation dataset: GPCP Daily Precipitation
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs mode to create object based statistics on daily 
# precipitation data from the CESM model and observations from the GPCP. 

##############################################################################
# METplus Workflow
# ----------------
#
# The mode tool is run for each time. This example loops by model 
# initialization time.  It processes 4 valid times, listed below.
#
# | **Valid:** 2014-08-02
# | **Forecast lead:** 24
# |
#
# | **Init:** 2014-08-03
# | **Forecast lead:** 48
# |
#
# | **Init:** 2014-08-03
# | **Forecast lead:** 24
# |
#
# | **Init:** 2014-08-04
# | **Forecast lead:** 48
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/climate/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/climate/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf

##############################################################################
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
# .. note:: See the :ref:`MODE MET Configuration<mode-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MODE_fcstCESM_obsGPCP_ConusPrecip.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/climate/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/climate/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf
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
# Output for this use case will be found in model_applications/climate/CESM_MODE (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T1_cts.txt
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T1_obj.nc
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T1_obj.txt
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T1.ps
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T2_cts.txt
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T2_obj.nc
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T2_obj.txt
# 2014_06_01_000000/mode_000000L_20140602_000000V_000000A_R1_T2.ps
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T1_cts.txt
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T1_obj.nc
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T1_obj.txt
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T1.ps
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T2_cts.txt
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T2_obj.nc
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T2_obj.txt
# 2014_06_01_000000/mode_000000L_20140603_000000V_000000A_R1_T2.ps
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T1_cts.txt
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T1_obj.nc
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T1_obj.txt
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T1.ps
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T2_cts.txt
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T2_obj.nc
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T2_obj.txt
# 2014_06_02_000000/mode_000000L_20140603_000000V_000000A_R1_T2.ps
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T1_cts.txt
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T1_obj.nc
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T1_obj.txt
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T1.ps
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T2_cts.txt
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T2_obj.nc
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T2_obj.txt
# 2014_06_02_000000/mode_000000L_20140604_000000V_000000A_R1_T2.ps

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/climate-MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.png'
#
# .. note:: `MODEToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_, 
#  `ClimateAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ClimateAppUseCase&check_keywords=yes&area=default>`_, 
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_, 
#  `NCAROrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_
