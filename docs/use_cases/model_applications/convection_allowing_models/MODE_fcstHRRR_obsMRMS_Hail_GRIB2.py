"""
MODE: Hail Verification  
=========================================================================

model_applications/
convection_allowing_model/
MODE_fcstHRRR_obsMRMS_Hail_GRIB2.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To provide statistical inforation on the forecast hail size compared to the 
# observed hail size from MRMS MESH data.  Using objects to verify hail size
# avoids the "unfair penalty" issue, where a CAM must first generate convection
# to have any chance of accurately predicting the hail size.  In addition,
# studies have shown that MRMS MESH observed hail sizes do not correlate one-
# to-one with observed sizes but can only be used to group storms into general
# categories.  Running MODE allows a user to do this.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRRv4 data
#  * Observation dataset: MRMS 
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MODE to create object statistics on forecast hail size 
# from the HRRR version 4 model and the observed MRMS MESH hail size.  

##############################################################################
# METplus Workflow
# ----------------
#
# The MODE tool is run for each time. This example loops by valid time.  It
# processes 2 valid times, listed below.
#
# | **Valid:** 2019-05-29_02Z
# | **Forecast lead:** 26
#
# | **Valid:** 2019-05-29_03Z
# | **Forecast lead:** 27

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRR_obsMRMS_Hail_GRIB2.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRR_obsMRMS_Hail_GRIB2.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODEConfig_hailcast
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
# 1) Passing in MODE_fcstHRRRE_obsMRMS_Hail_GRIB2.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_Hail_GRIB2.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE_fcstHRRRE_obsMRMS_Hail_GRIB2.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_Hail_GRIB2.conf
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
# Output for this use case will be found in hailtest (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# mode_260000L_20190529_020000V_010000A_cts.txt
# mode_260000L_20190529_020000V_010000A_obj.nc
# mode_260000L_20190529_020000V_010000A_obj.txt
# mode_260000L_20190529_020000V_010000A.ps
# mode_270000L_20190529_030000V_010000A_cts.txt
# mode_270000L_20190529_030000V_010000A_obj.nc
# mode_270000L_20190529_030000V_010000A_obj.txt
# mode_270000L_20190529_030000V_010000A.ps



##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-MODE_fcstHRRRE_obsMRMS_Hail_GRIB2.png'
#
# .. note:: `MODEToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_,
#  `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#  `RegriddingInToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegriddingInToolUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#  `NCAROrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_,
#  `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
