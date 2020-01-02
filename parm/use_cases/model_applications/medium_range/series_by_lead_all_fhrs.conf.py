"""
Series by Lead (for all forecast hours)
========
This use case performs a series analysis on tropical cyclone
data, based on all lead times. This use case illustrates how one can "build" on an existing
configuration file by overriding configuration settings. In this case, we have
requested a series analysis based on forecast hours rather than by initialization times.
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
#  * Forecast dataset: ADeck non-ATCF tropical cyclone data
#  * Observation dataset: non-ATCF tropical cyclone "best track"(BDeck) cyclone data
#  * Sources of data (links, contacts, etc...)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TcPairs and ExtractTiles to generate matched
# tropical cyclone data and regrid them into appropriately-sized tiles
# along a storm track. The MET tc-stat tool is used to filter the
# track data, and the MET regrid-dataplane tool is used to regrid the
# data (GRIB1 or GRIB2 into netCDF). Next, a series analysis by init time is
# performed on the results and plots (.ps and ,png) are generated for all
# variable-level-stat combinations from the specified variables, levels, and
# requiested statistics.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#  TcPairs > RegridDataPlane, TcStat > SeriesAnalysis
#
# This example loops by initialization time. For each initialization time
#  it will process forecast leads 6, 12, 18, 24, 30, 36, and 40. Data is only
#  available for 20141214.  Therefore there is only one
#  initializtion time that is run, in spite of the requested 20141214 to 20141216 time range.
#  The following will be run:
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
# | **Forecast lead:** 40
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/feature_relative.conf
# -c parm/use_cases/model_applications/medium_range/series_by_init_12-14_to_12-16.conf
#
# .. highlight:: bash
# .. literalinclude:: feature_relative.conf
# .. literalinclude:: series_by_init_12-14_to_12-16.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../parm/use_cases/model_applications/medium_range/TCPairsETCConfig
# .. literalinclude:: ../../../parm/use_cases/model_applications/medium_range/TCStatConfig
# .. literalinclude:: ../../../parm/use_cases/model_applications/medium_range/SeriesAnalysisConfig
#
# See the following files for more information about the environment variables set in these configuration files.
#   parm/use_cases/met_tool_wrapper/TCPairs.py
#
#   parm/use_cases/met_tool_wrapper/SeriesByInit.py
#
##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in feature_relative.conf and series_by_init_12-14_to_12-16.conf, then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/feature_relative.conf
#        -c /path/to/METplus/parm/use_cases/model_applications/medium_range/series_by_init_12-14_to_12-16.conf
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in feature_relative.conf and series_by_init_12-14_to_12_16.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/feature_relative.conf
#                          -c /path/to/METplus/parm/use_cases/model_applications/medium_range/series_by_init_12-14_to_12-16.conf
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
# Output for this use case will be found in series_analysis_init/20141214_00 (relative to **OUTPUT_BASE**)
# and will contain the following subdirectories:
#
# * ML1200942014
# * ML1200972014
# * ML1200992014
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
#   ANLY_ASCII_FILES_<storm>
#
#   FCST_ASCII_FILES_<storm>
#
#   series_<varname>_<level>_<stat>.png
#
#   series_<varname>_<level>_<stat>.ps
#
#   series_<varname>_<level>_<stat>.nc
#



##############################################################################
# Keywords
# --------
#
# Choose from the following pool of keywords, and include them in a note directive below.
# Remove any keywords you don't use.
#
# FeatureRelativeUseCase, TcPairsUseCase, SeriesByInitUseCase
#
# Now include them like this:
#
# .. note:: FeatureRelativeUseCase, TcPairsUseCase, SeriesByInitUseCase
