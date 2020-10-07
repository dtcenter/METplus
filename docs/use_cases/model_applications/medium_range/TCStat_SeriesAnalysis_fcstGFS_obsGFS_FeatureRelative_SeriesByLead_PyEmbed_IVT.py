"""
Multi_Tool: Feature Relative by Lead using User-Defined Fields 
========================================================================

model_applications/medium_range/
TCStat_SeriesAnalysis_fcstGFS
_obsGFS_FeatureRelative
_SeriesByLead_PyEmbed_IVT.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case calls multiple tools to produce diagnostic plots of systematic erros relative to a
# feature (e.g. hurricane, MCS, etc...). This use case calls a user provided python script that
# calculates a diagnostic of interest (e.g. integrated vapor transport, potential vorticity, etc...).
# This user diagnostic is then used to define the systematic errors. This example calculates statistics
# over varying forecast leads with the ability to define lead groupings. This use case is very similar
# to the Multi_Tools: Feature Relative by Lead use case.
# (ADeck,GFS:BDeck,GFS:ATCF,Grib2)
#
# By maintaining focus of each evaluation time (or evaluation time series, in this case)
# on a user-defined area around a cyclone, the model statistical errors associated
# with cyclonic physical features (moisture flux, stability, strength of upper-level
# PV anomaly and jet, etc.) can be related directly to the model forecasts and provide
# improvement guidance by accurately depicting interactions with significant weather
# features around and within the cyclone. This is in contrast to the traditional
# method of regional averaging cyclone observations in a fixed grid, which
# "smooths out" system features and limits the meaningful metrics that can be gathered.
# Specifically, this use case creates bins of forecast lead times as specified by the
# given ranges which provides additional insight directly into forecast lead time accuracy.
#
# Additionally, the ability to calculate model statistical errors based on user provided diagnostics
# allows the user to customize the feature relative analysis to suit their needs.

##############################################################################
# Datasets
# --------
#
# This use case compares the Global Forecast System (GFS) forecast to the GFS analysis for
# hurricane Dorian. It is based on the user provided python script that calculates the diagnostic 
# integrated vaport transport (IVT). 
# 
#  - Variables required to calculate IVT:
#    Levels required: all pressure levels <= 100mb
#    #. Temperature
#    #. v- component of wind
#    #. u- component of wind
#    #. Geopotential height
#    #. Specific humidity OR Relative Humidity
#  - Forecast dataset: GFS Grid 4 Forecast
#    GFS Forecast data can be found at the following website: https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs
#    - Initialization date: 20190830
#    - Initialization hours: 00, 06, 12, 18 UTC
#    - Lead times: 90, 96, 102, 108, 114
#    - Format: Grib2
#    - Resolution: 0.5 degree
#  - Observation dataset: GFS Grid 4 Analysis
#    GFS Analysis data can be found at the following website: https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs
#    - Valid date/time range: 20190902_18 - 20190904_12 every 6 hours
#    - Format: Grib2
#    - Resolution: 0.5 degree
#  - Hurricane Track Data
#    Hurricane track data can be found at the following website: http://hurricanes.ral.ucar.edu/repository/data/
#    - ADeck Track File: aal052019.dat
#    - BDeck Track File: bal052019.dat
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PyEmbedIngest to run the user provided python scripts to calculate the
# desired diagnostic (in this example, IVT). PyEmbedIngest runs the RegridDataPlane tool to write 
# IVT to a MET readable netCDF file. Then TCPairs and ExtractTiles are run to generate matched
# tropical cyclone data and regrid them into appropriately-sized tiles along a storm track. 
# The MET tc-stat tool is used to filter the track data and the MET regrid-dataplane tool is used to 
# regrid the data (GRIB1 or GRIB2 into netCDF). Next, a series analysis by lead time is performed on 
# the results and plots (.ps and .png) are generated for all variable-level-stat combinations from 
# the specified variables, levels, and requested statistics. If lead grouping is turned on, the final
# results are aggregated into forecast hour groupings as specified by the start, end and increment in
# the METplus configuration file, as well as labels to identify each forecast hour grouping. If lead
# grouping is not turned out, the final results will be written out for each requested lead time.

##############################################################################
# METplus Workflow
# ----------------
#
# This use case loops by process which means that each tool is run for all times before moving to the
# next tool. The tool order is as follows:
# 
# PyEmbedIngest, TCPairs, ExtractTiles, SeriesByLead
#
# This example loops by forecast/lead time (with begin, end, and increment as specified in the METplus
# TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf file). 
#
# 4 initialization times will be run over 5 lead times:
#
# | **Init:** 20190830_00Z
# | **Forecast lead:** 90, 96, 102, 108, 114
#
# | **Init:** 20190830_06Z
# | **Forecast lead:** 90, 96, 102, 108, 114
#
# | **Init:** 20190830_12Z
# | **Forecast lead:** 90, 96, 102, 108, 114
#
# | **Init:** 20190830_18Z
# | **Forecast lead:** 90, 96, 102, 108, 114
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. 
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** 
# If there is a setting in the MET configuration file that is not controlled by an environment 
# variable, you can add additional environment variables to be set only within the METplus environmen
# using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config'
# section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCPairsETCConfig_IVT
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/TCStatConfig_IVT
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/SeriesAnalysisConfig_IVT
#
# See the following files for more information about the environment variables set in these configuration files.
#
# parm/use_cases/met_tool_wrapper/TCPairs/TCPairs.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf, 
# then a user-specific system configuration file::
#
#        master_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf \
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf::
#
#        master_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  If the executable is in the user's path, METplus will find it from the name. 
#  If the executable is not in the path, specify the full path to the executable here (i.e. RM = /bin/rm)  
#  The following executables are required for performing series analysis use cases:
#
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

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in subdirectories of the 'series_analysis_lead' directory (relative to **OUTPUT_BASE**):
# 
# * series_animate
# * series_F090
# * series_F096
# * series_F102
# * series_F108
# * series_F114
#
# | The series_animate directory contains the animations of the series analysis in .gif format for all variable, level, and statistics combinations:
#
#    series_animate_<varname>_<level>_<stat>.gif
#
# | The series_FHHH directories contains files that have the following format:
# 
#   ANLY_FILES_FHHH
#
#   FCST_ASCII_FILES_FHHH
#
#   series_FHHH_<varname>_<level>_<stat>.png
#
#   series_FHHH_<varname>_<level>_<stat>.ps
#
#   series_FHHH_<varname>_<level>_<stat>.nc
#
#   Where:
#
#    **HHH** is the forecast hour/lead time in hours
#
#    **varname** is the variable of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **level**  is the level of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **stat** is the statistic of interest, as specified in the METplus series_by_lead_all_fhrs config file.
#

##############################################################################
# Keywords
# --------
#
# .. note::
#  `TCPairsToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCPairsToolUseCase&check_keywords=yes&area=default>`_,
#  `SeriesByLeadUseCase <https://dtcenter.github.io/METplus/search.html?q=SeriesByLeadUseCase&check_keywords=yes&area=default>`_,
#  `TCStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCStatToolUseCase&check_keywords=yes&area=default>`_,
#  `RegridDataPlaneToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`_,
#  `PyEmbedIngestToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PyEmbedIngestToolUseCase&check_keywords=yes&area=default>`_,
#  `MediumRangeAppUseCase <https://dtcenter.github.io/METplus/search.html?q=MediumRangeAppUseCase&check_keywords=yes&area=default>`_,
#  `SeriesAnalysisUseCase <https://dtcenter.github.io/METplus/search.html?q=SeriesAnalysisUseCase&check_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#  `FeatureRelativeUseCase <https://dtcenter.github.io/METplus/search.html?q=FeatureRelativeUseCase&check_keywords=yes&area=default>`_,
#  `SBUOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=SBUOrgUseCase&check_keywords=yes&area=default>`_
#  `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_SBU_IVT.png'
