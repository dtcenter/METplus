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
# |
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
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# **EnsembleStatConfig_wrapped**
#
# .. note:: See the :ref:`EnsembleStat MET Configuration<ens-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped
#
# **GridStatConfig_wrapped**
#
# .. note:: See the :ref:`GridStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in EnsembleStat_fcstWOFS_obsWOFS.py then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in EnsembleStat_fcstWOFS_obsWOFS.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf
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
#
#   * EnsembleStatToolUseCase
#   * PrecipitationAppUseCase
#   * GRIB2FileUseCase
#   * EnsembleAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-EnsembleStat_fcstWOFS_obsWOFS.png'
