"""
Grid-Stat: CESM and GFS Analysis CONUS Temp 
============================================================================
model_applications/climate/
GridStat_fcstCESM_obsGFS
_ConusTemp.conf
"""

##############################################################################
# Scientific Objective
# --------------------
#
# To evaluate the CESM model temperature against the GFS analysis across the
# the Continental United States to obtain categorical output statistics. This 
# was developed as part of the NCAR System for Integrated Modeling of the 
# Atmosphere (SIMA) project. 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: CESM Surface Temperature Data
#  * Observation dataset: GFS Analysis 2m Temperature
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs grid_stat to create continuous statistics on 
# tempeprature from the CESM model and observations from the GFS analysis. 

##############################################################################
# METplus Workflow
# ----------------
#
#  The grid_stat tool is run for each time. This example loops by initialization
#  time.  It processes 4 valid times, listed below.
#
# | **Valid:** 2014-08-01_06Z
# | **Forecast lead:** 06
# |
# | **Init:** 2014-08-01_12Z
# | **Forecast lead:** 12
# |
# | **Init:** 2014-08-02_06Z
# | **Forecast lead:** 06
# |
# | **Init:** 2014-08-02_12Z
# | **Forecast lead:** 12
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
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
# 1) Passing in GridStat_fcstCESM_obsGFS_ConusTemp.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstCESM_obsGFS_ConusTemp.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf
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

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in model_applications/climate/CESM_GridStat/grid_stat (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# grid_stat_CESM_TMP_vs_GFS_ANALYS_060000L_20140801_060000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_120000L_20140801_120000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_060000L_20140802_060000V.stat
# grid_stat_CESM_TMP_vs_GFS_ANALYS_120000L_20140802_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase 
#   * ClimateAppUseCase
#   * NetCDFFileUseCase 
#   * NCAROrgUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/climate-GridStat_fcstCESM_obsGFS_ConusTemp.png'
#
