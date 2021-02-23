"""
MODE: Brightness Temperature Verification  
=========================================================================

model_applications/
convection_allowing_model/
MODE_fcstFV3_obsGOES_BrightnessTemp.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To provide statistical inforation on regions of low brightness temperatures, 
# defined by creating objects, in the FV3 model compared to GOES satellite.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: FV3 Model member data
#  * Observation dataset: GOES Brightness Temperature
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MODE to create object statistics on brightness temperatures 
# below 235 K.  

##############################################################################
# METplus Workflow
# ----------------
#
# The MODE tool is run for each of 2 ensemble members and for eachtime. This 
# example loops by initialization time.  It processes 2 lead times, listed below.
#
# | **Valid:** 2019-05-21_01Z
# | **Forecast lead:** 01
#
# | **Valid:** 2019-05-21_02Z
# | **Forecast lead:** 02

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/MODE_fcstFV3_obsGOES_BrightnessTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODE_fcstFV3_obsGOES_BrightnessTemp.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODE_fcstFV3_obsGOES_BrightnessTemp/MODEConfig_BrightnessTemp
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/MODE/MODE.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MODE_fcstFV3_obsGOES_BrightnessTemp.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstFV3_obsGOES_BrightnessTemp.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE_fcstFV3_obsGOES_BrightnessTemp.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstFV3_obsGOES_BrightnessTemp.conf
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
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in convection_allowing_models/brightness_temperature 
# (relative to **OUTPUT_BASE**) and will contain the following files:
#
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_cts.txt
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.nc
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.txt
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA.ps
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_cts.txt
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.nc
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.txt
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA.ps
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_cts.txt
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.nc
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.txt
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA.ps
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_cts.txt
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.nc
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.txt
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA.ps


##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-MODE_fcstFV3_obsGOES_BrightnessTemp.png'
#
# .. note:: `MODEToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_,
#  `MODEToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_,
#  `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_,
#  `NCAROrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_,
