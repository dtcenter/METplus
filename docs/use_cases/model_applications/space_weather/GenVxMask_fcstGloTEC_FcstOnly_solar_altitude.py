"""
GenVxMask: Solar Altitude
=========================

model_applications/space_weather/GenVxMask_fcstGloTEC_solar
_altitude.conf

"""
##############################################################################
# Overview
# --------
#
# This use case illustrates the use of the gen_vx_mask tool for the space weather domain.
# It creates a mask for region where the solar altitude angle is less than 45 degrees
# (low sun angle or sun below the horizon), only letting data through for the region
# where the sun is high in the sky (i.e., solar altitude angle greater than 45 degrees).
#
# In this use case, the input data is the GloTEC model run assimilated with COSMIC-1 RO data.
#
# This use case runs gen_vx_mask for a couple forecast times from a
# space weather event known as the St. Patrick's Day Storm (Mar 17, 2015).
#
# Novel aspects of this use case:
#   - First example use case to run gen_vx_mask on a space weather model (GloTEC)
#   - Example of how to run gen_vx_mask on NetCDF input data which do not strictly conform to the
#     Climate Forecasts (CF) conventions
#   - Example of constructing a mask based on the solar altitude angle.
#   - Changing the mask condition to solar alt <= 0 will mask out the night region.
#   - Changing the mask condition to solar alt > 0 will mask the day region.
#
# Background: The solar altitude angle is the angle of the sun relative to the Earth's horizon,
# and is measured in degrees. The altitude is zero at sunrise and sunset, and can reach a
# maximum of 90 degrees (directly overhead) at noon at latitudes near the equator.
# [Source: https://sciencing.com/solar-altitude-23364.html]


##############################################################################
# Scientific Objective
# --------------------
#
# Creating masking region files to be used by other MET tools.
# This use case applies a solar altitude mask (solar altitude restriction) to the
# input grid, creating a separate masked output file for each time level of the input file.


##############################################################################
# Datasets
# --------
#
# | **Input Grid:** GloTEC
#
# | **Masks:** Solar altitude 
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
# | **Last modified:** 26 May 2020
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GenVxMask wrapper to generate a command to run the MET tool GenVxMask if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GenVxMask is the only tool called in this example. It processes the following
# run time:
#
# | **Init:** 2015-03-17 0005Z
# | **Forecast lead:** 0
#
# | **Init:** 2015-03-17 0015Z
# | **Forecast lead:** 0
#
# The input file is read to define the output grid. Then the solar altitude angle specified with the -thresh argument is applied to the input file, creating the output file.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/space_weather/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/space_weather/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. GenVxMask does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in the use case config file then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/space_weather/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in the use case config file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/space_weather/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf
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
# Output for this use case will be found in model_applications/space_weather/GenVxMask_fcstGloTEC_solar_altitude (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * GloTEC_TEC_solar_altitude_le_45_masked_2015_03_17_0005.nc
# * GloTEC_TEC_solar_altitude_le_45_masked_2015_03_17_0015.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#    `GenVxMaskToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GenVxMaskToolUseCase&check_keywords=yes&area=default>`_,
#    `SpaceWeatherAppUseCase <https://dtcenter.github.io/METplus/search.html?q=SpaceWeatherAppUseCase&check_keywords=yes&area=default>`_,
#    `NOAASWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAASWPCOrgUseCase&check_keywords=yes&area=default>`_,
#    `MaskingFeatureUseCase  <https://dtcenter.github.io/METplus/search.html?q=MaskingFeatureUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GenVxMask.png'
