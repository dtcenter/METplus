"""
GenVxMask: Basic Use Case
=========================

GenVxMask.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Creating masking region files to be used by other MET tools.

##############################################################################
# Datasets
# --------
#
# | **Input Grid:** GFS
#
# | **Mask:** CONUS polyline file
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/NCAR/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
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
# | **Initialization:** 2012-04-09_0Z
# | **Forecast Lead:** 12 hour
#
# The input file is read to define the output grid and the CONUS polyline file is applied to create the mask.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask.conf

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
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in the use case config file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GenVxMask/GenVxMask.conf
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
# * POLY_GFS_LATLON_CONUS_mask.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#    `GenVxMaskToolUseCase <https://ncar.github.io/METplus/search.html?q=GenVxMaskToolUseCase&check_keywords=yes&area=default>`_,
#    `GRIBFileUseCase  <https://ncar.github.io/METplus/search.html?q=GRIBFileUseCase&check_keywords=yes&area=default>`_
#

# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GenVxMask.png'

