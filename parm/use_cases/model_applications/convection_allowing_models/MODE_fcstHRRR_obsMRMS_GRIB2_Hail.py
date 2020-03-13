"""
HRRR Hail MODE Use Case
=======================

This use case builds hourly gridded fields for multiple variables,
comparing the resulting data to forecast data

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To provide statistical inforation on the forecast hail size compared to the 
# observed hail size from MRMS MESH data.

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
# from the HRRR version 4 model and the observed MRMS MESH hail size.  Using
# objects 

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
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MODEConfig_Hailcast
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
# 1) Passing in MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.conf
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
# Output for this use case will be found in model_applications/convection_allowing_models/MODE_fcstHRRRE_obsMRMS_GRIB2_Hail/20190529 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * TBD 


##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-MODE_fcstHRRRE_obsMRMS_GRIB2_Hail.png'
#
# .. note:: `MODEToolUseCase <https://ncar.github.io/METplus/search.html?q=ModeToolUseCase&check_keywords=yes&area=default>`_, `ConvectionAllowingModelsAppUseCase <https://ncar.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_, `GRIB2FileUseCase <https://ncar.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_, `HWTUseCase <https://ncar.github.io/METplus/search.html?q=HWTUseCase&check_keywords=yes&area=default>`_,  `ProbabilityGenerationAppUseCase <https://ncar.github.io/METplus/search.html?q=ProbabilityGenerationAppUseCase&check_keywords=yes&area=default>`_
