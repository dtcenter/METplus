"""
ExtractTiles: MTD Input
=======================

met_tool_wrapper/ExtractTiles/ExtractTiles_mtd.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Read a MODE Time Domain (MTD) output file and use the centroid latitude
# and longitude values of the MTD cluster object pairs to
# create a cutout of forecast and observation data valid at each time.
#

##############################################################################
# Datasets
# --------
#
# | **Track Data:** Output from MODE Time Domain (MTD)
# | **Forecast:** WRF
# | **Observation:** Stage 2 NetCDF 3-hour Precipitation Accumulation
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ExtractTiles wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool regrid_data_plane if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# ExtractTiles is the only tool called in this example.
# It processes the following run time:
#
# | **Init:** 2005-08-07 0Z
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/ExtractTiles/ExtractTiles_mtd.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/ExtractTiles/ExtractTiles_mtd.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. RegridDataPlane does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in ExtractTiles_mtd.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ExtractTiles/ExtractTiles_mtd.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in ExtractTiles_mtd.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ExtractTiles/ExtractTiles_mtd.conf
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
# Output for this use case will be found in met_tool_wrapper/ExtractTiles/20050807_00 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * FCST_TILE_F006_wrfprs_20050807_0000_006.nc
# * FCST_TILE_F009_wrfprs_20050807_0000_009.nc
# * FCST_TILE_F012_wrfprs_20050807_0000_012.nc
# * OBS_TILE_F006_wrfprs_20050807_0600_000.nc
# * OBS_TILE_F009_wrfprs_20050807_0900_000.nc
# * OBS_TILE_F012_wrfprs_20050807_1200_000.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * RegridDataPlaneToolUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-ExtractTiles.png'
#
