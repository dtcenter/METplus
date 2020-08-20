"""
Grid-Stat: 6hr QPF in GEMPAK format
===============================================================================

model_applications/precipitation/GridStat_fcstHREFmean
_obsStgIV_Gempak.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Evaluate the skill of a high resolution multi-model ensemble mean
# at predicting 6 hour precipitation accumulation using the NCEP Stage IV
# gauge corrected analysis.
#

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
# 
#  * Forecast dataset: HREF mean forecasts in Gempak
#  * Observation dataset: Stage IV GRIB 6 hour precipitation accumulation
#  * Sources of data (links, contacts, etc...)
#

##############################################################################
#External Dependencies
#---------------------
#
# GempakToCF.jar
#
# GempakToCF is an external tool that utilizes the Unidata NetCDF-Java package. The jar file that can be used to run the utility is available here: https://dtcenter.org/sites/default/files/community-code/utilities/GempakToCF.jar
#
#To enable Gempak support, you must set [exe] GEMPAKTOCF_JAR in your user METplus configuration file:
#
# [exe] GEMPAKTOCF_JAR = /path/to/GempakToCF.jar
#
# See the GempakToCF use case for more information:
#
# parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf
#
# More information on the package used to create the file is here: https://www.unidata.ucar.edu/software/netcdf-java
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the forecast data to build a 6
# hour precipitation accumulation from 1 hour files or a single 6 hour file.
# Then the observation data is regridded to the model grid using the RegridDataPlane. Finally, the
# observation files are compared to the forecast data using GridStat.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# PCPCombine (observation) > RegridDataPlane (observation) > GridStat
#
# This example loops by initialization time.
# There is only one initalization time in this example so the following will be run:
#
# Run times:
#
# | **Init:** 2017-05-09_12Z
# | **Forecast lead:** 18
#
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStatConfig_MEAN
#
# See the following files for more information about the environment variables set in this configuration file.
#   parm/use_cases/met_tool_wrapper/GridStat/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstHREFmean_obsStgIV_Gempak.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstHREFmean_obsStgIV_Gempak.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf
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
# Output for this use case will be found in model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak/GridStat/201705091200 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_000000L_20170510_060000V_eclv.txt
# * grid_stat_000000L_20170510_060000V_grad.txt
# * grid_stat_000000L_20170510_060000V.stat
#

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-GridStat_fcstHREFmean_obsStgIV_Gempak.png'
#
# .. note::
#     `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#     `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#     `PCPCombineToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineToolUseCase&check_keywords=yes&area=default>`_,
#     `RegridDataPlaneToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`_,
#     `GEMPAKFileUseCase <https://dtcenter.github.io/METplus/search.html?q=GEMPAKFileUseCase&check_keywords=yes&area=default>`_,
#     `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_,
#     `NOAAWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_,
#     `NOAAHMTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#     `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#     `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_
