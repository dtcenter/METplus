"""
Grid-Stat: Analysis validation 
==============================================================================

GridStat_fcstGloTEC
_obsGloTEC_vx7.conf

"""
##############################################################################
# Overview
# --------
#
# This use case illustrates the use of grid_stat tool for the space weather domain.
# It compares Total Electron Content for a GloTEC model run initialized with COSMIC-1
# radio occultation (RO) data to a GloTEC model run without such data. 
#
# In this use case, the forecast is considered to be the run without COSMIC-1 RO data.
# The observations are considered to be the run with COSMIC-1 RO data.
#
# This use case runs grid_stat for the first two forecast times of a 
# space weather event known as the St. Patrick's Day Storm (Mar 17, 2015). 
#
# Novel aspects of this use case:
#
# * This is the first example use case to run grid_stat on a space weather model (GloTEC)
# * Example of how to run with NetCDF input data which do not strictly conform to the Climate Forecasts (CF) conventions
# * Example of using masks covering latitudinal bands of interest to the space weather community: equatorial region, mid-latitude region, and polar region
# * Example of masking using the values of a quality flag which vary at each time step and grid point

##############################################################################
# Scientific Objective
# --------------------
#
# Compare gridded forecast data from a run of the GloTEC model that includes 
# assimilation of COSMIC-1 radio occultation (RO) observations to gridded forecast 
# data from a GloTEC model run that does not include COSMIC-1 RO data. 

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GloTEC Total Electron Content (TEC) model run without assimilation of any COSMIC-1 RO data
# | **Observation:** GloTEC TEC model run that assimilates COSMIC-1 RO data
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. 
# | Click here to download: https://github.com/dtcenter/METplus/releases/download/v3.0/sample_data-space_weather-3.0.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data source:** NOAA Space Weather Prediction Center (SWPC)
# | **Data contact:** Dominic Fuller-Rowell (dominic.fuller-rowell@noaa.gov)
#

##############################################################################
# METplus Use Case Contact
# ------------------------
#
# | **Author:** Jonathan L. Vigh (National Center for Atmospheric Research / Research Applications Laboratory / Joint Numerical Testbed)
# | **Last modified:** 06 February 2020
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool grid_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2015-03-17 0005Z
# | **Forecast lead:** 0
#
# | **Init:** 2015-03-17 0015Z
# | **Forecast lead:** 0
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/space_weather/GridStat_fcstGloTEC_obsGloTEC_vx7.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/space_weather/GridStat_fcstGloTEC_obsGloTEC_vx7.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/space_weather/GridStatConfig_vx7
#
# Note the following variables are referenced in the MET configuration file.
# 
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from FCST_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from OBS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${FCST_VAR}** - Field name of forecast data to process. Used in output_prefix to include input information in the output filenames. Corresponds to FCST_VAR<n>_NAME in the METplus configuration file.
# * **${OBS_VAR}** - Field name of observation data to process. Used in output_prefix to include input information in the output filenames. Corresponds to OBS_VAR<n>_NAME in the METplus configuration file.
# * **${LEVEL}** - Vertical level of the forecast input data. Used in output_prefix to include input information in the output filenames. Corresponds to FCST_VAR<n>_LEVELS in the METplus configuration file.
# * **${VERIF_MASK}** - Optional verification mask file or list of files. Corresponds to GRID_STAT_VERIFICATION_MASK_TEMPLATE in the METplus configuration file.
# * **${NEIGHBORHOOD_SHAPE}** - Shape of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_SHAPE in the METplus configuration file. Default value is 1 if not set.
# * **${NEIGHBORHOOD_WIDTH}** - Width of the neighborhood method applied. Corresponds to GRID_STAT_NEIGHBORHOOD_WIDTH in the METplus configuration file. Default value is SQUARE if not set.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstGloTEC_obsGloTEC_vx7.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/space_weather/GridStat_fcstGloTEC_obsGloTEC_vx7.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstGloTEC_obsGloTEC_vx7.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/space_weather/GridStat_fcstGloTEC_obsGloTEC_vx7.conf
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
# Output for this use case will be found in space_weather/glotec_vs_glotec/output_data/2015_03_17 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_GloTEC_without_cosmic-vx7_TEC_vs_GloTEC_with_cosmic_000000L_20150317_000500V_pairs.nc  
# * grid_stat_GloTEC_without_cosmic-vx7_TEC_vs_GloTEC_with_cosmic_000000L_20150317_001500V_pairs.nc
# * grid_stat_GloTEC_without_cosmic-vx7_TEC_vs_GloTEC_with_cosmic_000000L_20150317_000500V.stat      
# * grid_stat_GloTEC_without_cosmic-vx7_TEC_vs_GloTEC_with_cosmic_000000L_20150317_001500V.stat


##############################################################################
# Keywords
# --------
#
# .. note::
#
#  `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#  `SpaceWeatherAppUseCase <https://dtcenter.github.io/METplus/search.html?q=SpaceWeatherAppUseCase&check_keywords=yes&area=default>`_,
#  `NOAASWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAASWPCOrgUseCase&check_keywords=yes&area=default>`_,
#  `CustomStringLoopingUseCase <https://dtcenter.github.io/METplus/search.html?q=CustomStringLoopingUseCase&check_keywords=yes&area=default>`_,
#  `MaskingFeatureUseCase  <https://dtcenter.github.io/METplus/search.html?q=MaskingFeatureUseCase&check_keywords=yes&area=default>`_,
#  `ValidationUseCase  <https://dtcenter.github.io/METplus/search.html?q=ValidationUseCase&check_keywords=yes&area=default>`_
    
# sphinx_gallery_thumbnail_path = '_static/space_weather-GridStat_fcstGloTEC_obsGloTEC_vx7.jpg'
