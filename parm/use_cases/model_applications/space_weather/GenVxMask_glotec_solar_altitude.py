"""
GenVxMask: Solar Altitude
=========================

GenVxMask_fcstGloTEC_solar_altitude.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Creating masking region files to be used by other MET tools. This use case applies a solar altitude mask (solar altitude restriction) to the input grid.

##############################################################################
# Datasets
# --------
#
# | **Input Grid:** GloTEC
#
# | **Masks:** Solar altitude 
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. 
# | Click here to download: https://github.com/NCAR/METplus/releases/download/v3.0/sample_data-space_weather-3.0.tgz
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
# | **Last modified:** 20 April 2020
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
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask_multiple.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask_glotec_solar_altitude.conf

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
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask_multiple.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in the use case config file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask_multiple.conf
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
# Output for this use case will be found in met_tool_wrapper/GenVxMask (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * LAT_LON_mask.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#    `GenVxMaskToolUseCase <https://ncar.github.io/METplus/search.html?q=GenVxMaskToolUseCase&check_keywords=yes&area=default>`_,
#    `SpaceWeatherAppUseCase <https://ncar.github.io/METplus/search.html?q=SpaceWeatherAppUseCase&check_keywords=yes&area=default>`_,
#    `NOAASWPCOrgUseCase  <https://ncar.github.io/METplus/search.html?q=NOAASWPCOrgUseCase&check_keywords=yes&area=default>`_,
#    `MaskingFeatureUseCase  <https://ncar.github.io/METplus/search.html?q=MaskingFeatureUseCase&check_keywords=yes&area=default>`_,
#

# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GenVxMask.png'
