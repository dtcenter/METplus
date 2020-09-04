"""
Multi_Tool: Feature Relative by Init 
===================================================================================

model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS
_obsGFS_FeatureRelative
_SeriesByInit.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# By maintaining focus of each evaluation time (or evaluation time series, in this case)
# on a user-defined area around a cyclone, the model statistical errors associated
# with cyclonic physical features (moisture flux, stability, strength of upper-level PV
# anomaly and jet, etc.) can be related directly to the model forecasts and provide
# improvement guidance by accurately depicting interactions with significant weather
# features around and within the cyclone. This is in contrast to the traditional
# method of regional averaging cyclone observations in a fixed grid, which "smooths out"
# system features and limits the meaningful metrics that can be gathered.

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
#
#  * TC-Pairs/TC-Stat Forecast dataset: ADeck modified-ATCF tropical cyclone data
#  * Series-Analysis Forecast dataset: GFS
#  * TC-Pairs/TC-Stat Observation dataset: BDeck modified-ATCF tropical cyclone data
#  * Series-Analysis Observation dataset: GFS Analysis
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TCPairs and ExtractTiles to generate matched
# tropical cyclone data and regrid them into appropriately-sized tiles
# along a storm track. The MET tc-stat tool is used to filter the
# track data, and the MET regrid-dataplane tool is used to regrid the
# data (GRIB1 or GRIB2 into netCDF). Next, a series analysis by init time is
# performed on the results and plots (.ps and .png) are generated for all
# variable-level-stat combinations from the specified variables, levels, and
# requested statistics.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# TCPairs > RegridDataPlane, TCStat > SeriesAnalysis
#
# This example loops by initialization time. For each initialization time
# it will process forecast leads 6, 12, 18, 24, 30, 36, and 40. There is only one
# initialization time in this example, so the following will be run:
#
# Run times:
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 6
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 12
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 18
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 24
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 30
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 36
#
# | **Init:** 20141214_0Z
# | **Forecast lead:** 42
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCPairsETCConfig
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCStatConfig
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/SeriesAnalysisConfig
#
# See the following files for more information about the environment variables set in these configuration files.
# 
# parm/use_cases/met_tool_wrapper/TCPairs/TCPairs.py
# parm/use_cases/met_tool_wrapper/SeriesByInit/SeriesByInit.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#
#  and for the [exe] section, you will need to define the location of
#  NON-MET executables.  If the executable is in the user's path, METplus will find it from
#  the name. If the executable is not in the path, specify the full
#  path to the executable here (i.e. RM = /bin/rm)  The following executables are required
#  for performing series analysis use cases:
#
#  If the executables are in the path:
#
# * **RM = rm**
# * **CUT = cut**
# * **TR = tr**
# * **NCAP2 = ncap2**
# * **CONVERT = convert**
# * **NCDUMP = ncdump**
#
# **NOTE:** All of these executable items must be located under the [exe] section.
#
#
# If the executables are not in the path, they need to be defined:
#
# * **RM = /path/to/rm**
# * **CUT = /path/to/cut**
# * **TR = /path/to/tr**
# * **NCAP2 = /path/to/ncap2**
# * **CONVERT = /path/to/convert**
# * **NCDUMP= /path/to/ncdump**
#
# **NOTE:** All of these executable items must be located under the [exe] section.
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
#   [exe]
#   RM = /path/to/rm
#   CUT = /path/to/cut
#   TR = /path/to/tr
#   NCAP2 = /path/to/ncap2
#   CONVERT = /path/to/convert
#   NCDUMP = /path/to/ncdump
#
# **NOTE:** The INPUT_BASE, OUTPUT_BASE, and MET_INSTALL_DIR must be located under the [dir] section, while the RM, CUT, TR, NCAP2, CONVERT, and NCDUMP must be located under the [exe] section.




##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in series_analysis_init/20141214_00 (relative to **OUTPUT_BASE**)
# and will contain the following subdirectories:
#
# * ML1200942014
# * ML1200942014
# * ML1200942014
# * ML1201002014
# * ML1201032014
# * ML1201042014
# * ML1201052014
# * ML1201062014
# * ML1201072014
# * ML1201082014
# * ML1201092014
# * ML1201102014
#
# Each subdirectory will contain files that have the following format:
# 
# ANLY_ASCII_FILES_<storm>
#
# FCST_ASCII_FILES_<storm>
#
# series_<varname>_<level>_<stat>.png
#
# series_<varname>_<level>_<stat>.ps
#
# series_<varname>_<level>_<stat>.nc
#



##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.png'
#
# .. note:: `TCStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCStatToolUseCase&check_keywords=yes&area=default>`_, `SeriesByInitUseCase <https://dtcenter.github.io/METplus/search.html?q=SeriesByInitUseCase&check_keywords=yes&area=default>`_, `RegridDataPlaneToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`_, `MediumRangeAppUseCase <https://dtcenter.github.io/METplus/search.html?q=MediumRangeAppUseCase&check_keywords=yes&area=default>`_,  `SeriesAnalysisUseCase <https://dtcenter.github.io/METplus/search.html?q=SeriesAnalysisUseCase&check_keywords=yes&area=default>`_, `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_, `TCPairsToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCPairsToolUseCase&check_keywords=yes&area=default>`_, `FeatureRelativeUseCase <https://dtcenter.github.io/METplus/search.html?q=FeatureRelativeUseCase&check_keywords=yes&area=default>`_, `SBUOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=SBUOrgUseCase&check_keywords=yes&area=default>`_, `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
