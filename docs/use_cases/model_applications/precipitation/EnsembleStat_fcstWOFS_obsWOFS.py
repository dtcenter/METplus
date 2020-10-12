"""
Ensemble-Stat: WoFS
================================================================

model_application/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Comparing the Warn on Forecast System (WoFS) ensemble to the MRMS observed
# variable field to understand its forecasting abilities. Specifically focusing on
# accumulated precipitation at different neighborhood distances and accumulation
# thresholds to provide meaningful analysis output that can provide direction to future WoFS improvement.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: WoFS Ensemble
#

###############################################################################
# METplus Components
# ------------------
#
# This use case runs PCP-Combine on each ensemble member, then runs
# Ensemble-Stat on the output. Finally, it runs Grid-Stat on the output from
# Ensemble-Stat

###############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# PCPCombine, EnsembleStat, GridStat
#
# This example loops by initialization time. For each initialization time
# it will process the 1 hour forecast lead
#
# Run times:
#
# | **Init:** 2020-06-15_17Z
# | **Forecast lead:** 1 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/EnsembleStatConfig_WOFS
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/EnsembleStat.py
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStatConfig_WOFS_PCP_1H
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in EnsembleStat_fcstWOFS_obsWOFS.py then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in EnsembleStat_fcstWOFS_obsWOFS.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf
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
# Output for this use case will be found in WOFS/grid_stat (relative to **OUTPUT_BASE**)
# The following folder/file combination will be created:
#
# * 20200615/1700/grid_stat_WOFS_PCP_1700_A1_000000L_20200615_180000V_pairs.nc
# * 20200615/1700/grid_stat_WOFS_PCP_1700_A1_000000L_20200615_180000V.stat


##############################################################################
# Keywords
# --------
#
# .. note::
#    `EnsembleStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleStatToolUseCase&check_keywords=yes&area=default>`_,
#    `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#    `GRIB2FileUseCase  <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#    `EnsembleAppUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleAppUseCase&check_keywords=yes&area=default>`_,

# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-EnsembleStat.png'
