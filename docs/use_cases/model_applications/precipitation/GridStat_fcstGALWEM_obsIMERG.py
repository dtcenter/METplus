"""
Multi_Tool: Comparing GALWEM and IMERG 
====================================

model_applications/precipitation/
GridStat_fcstGALWEM_obsIMERG.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare GALWEM forecast accumulated 3 hour precipitation to observed IMERG
# 3 hour precipitation. 

##############################################################################
# Datasets
# --------
#
# This use case compares the Global Air-Land Weather Exploitation Model (GALWEM)
# precipitation forecast to the Integrated Multi-satellitE Retrievals for GPM
# (IMERG) observed precipitation. 
#
# - Forecast Datataset: GALWEM
#   - Initialization Date: 20180102
#   - Initialization Time: 00 UTC
#   - Lead Times: 0 - 36 hours
#   - Format: Grib2
#   - Resolution: 1.5km
#
# - Observation Dataset: IMERG
#   - Valid Date/Time Range: 20180102_00 - 20180103_12 every half hour
#   - Format: NETCDF4
#   - Resolution: 0.10 degrees
#
##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PCPCombine wrapper to create 3 hourly 
# accumulated precipitation values. It also utilizies the GridStat wrapper to 
# search for files that are valid at a given run time and generate a command 
# to run the MET tool grid_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PCPCombine is run first. PCPCombine is called to run over the forecast GALWEM
# data and create 3 hourly accumulated precipitation values. These values are then
# written out in a new netCDF file. PCPCombine is then run on the observation IMERG
# data to create 3 hourly accumulated precipitation values. This is done by calling
# a python embedding script to read the IMERG data and pass that data to PCPCobmine.
# Finally, GridStat is called. It processes all lead times from 3 - 36 hours every
# 3 hours. 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/GridStat_fcstGALWEM_obsIMERG.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation.GridStat_fcstGALWEM_obsIMERG.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_APCP_03h
#
# See the following files for more information about the environment variables set in these configuration files.
#
# parm/use_cases/met_tool_wrapper/GridStat/GridStat.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstGALWEM_obsIMERG.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstGALWEM_obsIMERG.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstGALWEM_obsIMERG.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstGALWEM_obsIMERG.conf

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
# Output for this use case will be found in AF/ (relative to **OUTPUT_BASE**)
# and will contain the following directories and files:
#
# * 1P5KM_APCP3: This is where the PCPCombine output for GALWEM will be. There should be
# 12 output files, one for each lead time between 3 and 36 hours. The files have the 
# following format:
# 
#   * DI.C_GP.GALWEM-RD-REGRID_GR_KOREA.C1P5KM_REGRID_20180102_f03_APCP_03.nc
#
# * IMERG_APCP3: This is where the PCPCombine output for IMERG will be. There should be
# 12 output files, one for each lead time between 3 and 36 hours. The files have the 
# following format:
# 
#   * IMERG_3H_00.00_20180103-060000.nc
#
# * 20180102/grid_stat: This is where the GridStat output will be. There should be
# 24 output files, two for each lead time between 3 and 36 hours. The files have the 
# following format:
#
#   * grid_stat_GALWEM_vs_IMERG_180000L_20180102_180000V_pairs.nc
#   * grid_stat_GALWEM_vs_IMERG_180000L_20180102_180000V.stat

##############################################################################
