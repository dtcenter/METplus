"""
MTD: 6hr QPF Use Case
==================================

model_applications/precipitation/MTD_fcstHRRR-TLE
_obsMRMS.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the evaluation of an ensemble mean field from a
# prototype ensemble post-processing technique for time-lagged ensembles
# (HRRR-TLE). MTD is used to provide useful object attributes and diagnostics on
# aggregated over a time series. This non-traditional
# approach provides alternative information and diagnostics to inform model development.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRR-TLE forecasts in GRIB2
#  * Observation dataset: Multi Radar Multi Sensor (MRMS)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MTD (MODE Time Domain) over multiple forecast leads and 
# compares them to the observational data set.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# MTD
#
# This example loops by valid time. For each valid time
# it will run once, processing forecast leads 1, 2, and 3. There is only one
# valid time in this example, so the following will be run:
#
# Run times:
#
# | **Valid:** 2017-05-10_03Z
# | **Forecast leads:** 1, 2, 3
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/MTD/MTD.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_fcstHRRR-TLE_obsMRMS.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_fcstHRRR-TLE_obsMRMS.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf
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
# Output for this use case will be found in model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * mtd_20170510_040000V_2d.txt
# * mtd_20170510_040000V_3d_single_simple.txt
# * mtd_20170510_040000V_obj.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#  `MTDToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MTDToolUseCase&check_keywords=yes&area=default>`_,
#  `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&check_keywords=yes&area=default>`_,
#  `NOAAWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHMTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#  `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#  `ProbabilityVerificationUseCase  <https://dtcenter.github.io/METplus/search.html?q=ProbabilityVerificationUseCase&check_keywords=yes&area=default>`_,
#  `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-MTD_fcstHRRR-TLE_obsMRMS.png'
