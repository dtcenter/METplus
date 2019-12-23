"""
RUC vs. Stage II GRIB Use Case
========

This use case builds a 3 hour gridded precipitation accumulation using 1 hour accumulation fields,
then compares the resulting data set to gridded 3 hour accumulation forecast data

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Describe the scientific objective of the use case here. This can be fairly
# simple, or complex depending on the task.

##############################################################################
# Datasets
# --------
#
# Describe the datasets here. Relevant information about the datasets that would
# be beneficial include:
# 
#  * Forecast dataset: RUC GRIB 3 hour precipitation accumulation
#  * Observation dataset: Stage II GRIB 1 hour precipitation accumulation
#  * Sources of data (links, contacts, etc...)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the observation data to build a 3
# hour precipitation accumulation from 1 hour files. Then the observation data
# is regridded to the model grid using the RegridDataPlane. Finally, the
# observation files are compared to the forecast data using GridStat.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#  PCPCombine (observation) > RegridDataPlane (observation) > GridStat
#
# This example loops by initialization time. For each initialization time
#  it will process forecast leads 3, 6, 9, and 12. There is only one
#  initialization time in this example, so the following will be run:
#
# Run times:
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 3
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 6
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 9
#
# | **Init:** 2005-08-07_0Z
# | **Forecast lead:** 12
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/ruc-vs-s2grib.conf
#
# .. highlight:: bash
# .. literalinclude:: ruc-vs-s2grib.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/use_cases/model_applications/precipitation/GridStatConfig_MEAN
#
# See the following files for more information about the environment variables set in this configuration file.
#   parm/use_cases/met_tool_wrapper/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in ruc-vs-s2grib.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/ruc-vs-s2grib.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in ruc-vs-s2grib.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/ruc-vs-s2grib.conf
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
# Output for this use case will be found in grid_stat/ruc-vs-s2grib/2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_030000L_20050807_030000V_eclv.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_030000L_20050807_030000V_grad.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_030000L_20050807_030000V.stat
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_060000L_20050807_060000V_eclv.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_060000L_20050807_060000V_grad.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_060000L_20050807_060000V.stat
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_090000L_20050807_090000V_eclv.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_090000L_20050807_090000V_grad.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_090000L_20050807_090000V.stat
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_120000L_20050807_120000V_eclv.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_120000L_20050807_120000V_grad.txt
# *grid_stat_MEAN_QPF_APCP_vs_QPE_APCP_A03_120000L_20050807_120000V.stat
#

##############################################################################
# Keywords
# --------
#
# Choose from the following pool of keywords, and include them in a note directive below.
# Remove any keywords you don't use.
#
# GridStatUseCase, PB2NCUseCase, PrecipitationUseCase
#
# Now include them like this:
#
# .. note:: GridStatUseCase, PrecipitationUseCase, PCPCombineUseCase, RegridDataPlaneUseCase
