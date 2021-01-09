"""
Blocking Calculation: RegridDataPlane, PcpCombine, and Blocking python code
============================================================================

model_applications/
s2s/
Regrid_PCP_fcstGFS_obsERA_Blocking.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To compute the Central Blocking Latitude, Instantaneousy blocked latitudes,
# Group Instantaneousy blocked latitudes, and the frequency of atmospheric 
# blocking using the Pelly-Hoskins Method.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: GEFS Forecast 500 mb height. 
#  * Observation dataset: ERA Reanlaysis 500 mb height.

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the blocking driver script which runs the steps the user
# lists in STEPS_OBS.  The possible steps are regridding (REGRID), time averaging
# (TIMEAVE), computing a running mean (RMEAN), computing anomalies (ANOMALY), computing CBLs
# (CBL), plotting CBLs (PLOTCBL), computing IBLs (IBL), plotting IBL frequency (PLOTIBL), 
# computing GIBLs (GIBL), computing blocks (CALCBLOCKS), and plotting the blocking frequency
# (PLOTBLOCKS).  The steps are listed in a .conf file and are formatted as follows:
#
# FCST_STEPS = REGRID+TIMEAVE+CBL+IBL+PLOTIBL+GIBL+CALCBLOCKS+PLOTBLOCKS
# OBS_STEPS = REGRID+TIMEAVE+RUNMEAN+ANOMALY+CBL+PLOTCBL+IBL+PLOTIBL+GIBL+CALCBLOCKS+PLOTBLOCKS

##############################################################################
# METplus Workflow
# ----------------
#
# The regrid_data_plane, pcp_combine, and blocking python code are run for each
# time for the forecast and observations data. This example loops by valid time.  

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s/Regrid_PCP_fcstGFS_obsERA_Blocking.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/Regrid_PCP_fcstGFS_obsERA_Blocking.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane.py
# parm/use_cases/met_tool_wrapper/PCPCombine/PCPCOmbine_derive.py
# parm/use_cases/met_tool_wrapper/PCPCombine/PCPCOmbine_subtract.py

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in Regrid_PCP_fcstGFS_obsERA_Blocking.conf then a user-specific system configuration file::
#
#        master_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/Regrid_PCP_fcstGFS_obsERA_Blocking.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in Regrid_PCP_fcstGFS_obsERA_Blocking.conf::
#
#        master_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/Regrid_PCP_fcstGFS_obsERA_Blocking.conf
#
# The following variables must be set correctly:
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

##############################################################################
# Expected Output
# ---------------
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in model_applications/s2s/Blocking (relative to **OUTPUT_BASE**) and will contain output 
# for the steps requested.  This may include the regridded data, daily averaged files, running mean files, 
# anomaly files, the CBL , an IBL frequency plot, and blocking frequency plots.

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/s2s-IBL_frequency.png'
#
# .. note:: `RegridDataPlaneUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneUseCase&check_keywords=yes&area=default>`_,
#  `PCPCombineUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineUseCase&check_keywords=yes&area=default>`_, 
#  `S2SAppUseCase <https://dtcenter.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_, 
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
