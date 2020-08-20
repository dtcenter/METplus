"""
PCPCombine: Custom String Looping Use Case
============================================================================

met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. This wrapper's purpose is to demonstrate the ability to read in a user-defined
# list of strings, processing each item in the list for the given run time.
#

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF-ARW precipitation 24h accumulation fields
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** WRF-AFW

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PCPCombine wrapper to run across a user-provided
# list of strings, executing each item in the list for each run time. In this example,
# the ADD mode of PCPCombine is used, but only a single file is processed for each run time.
# Because it is executed in this manner, the output will match the input.

##############################################################################
# METplus Workflow
# ----------------
#
# PCPCombine is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2009-12-31_12Z
# | **Forecast lead:** 24 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. PCPCombine does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PCPCombine_loop_custom.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PCPCombine_loop_custom.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf
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
# Output for this use case will be found in met_tool_wrapper/PCPCombine/PCPCombine_loop_custom (relative to **OUTPUT_BASE**)
# and will contain the following folders:
#
# * arw-fer-gep1
# * arw-fer-gep5
# * arw-sch-gep2
# * arw-sch-gep6
# * arw-tom-gep3
# * arw-tom-gep7
#
# and each of the folders will contain a single file titled:
#
# * d01_2009123112_02400.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#  `PCPCombineToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineToolUseCase&check_keywords=yes&area=default>`_,
#  `CustomStringLoopingUseCase <https://dtcenter.github.io/METplus/search.html?q=CustomStringLoopingUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PCPCombine.png'
