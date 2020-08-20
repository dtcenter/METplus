"""
CyclonePlotter: Basic Use Case
============================================================================

met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf

"""


##############################################################################
# Scientific Objective
# --------------------
#
#
# Provide visualization of cyclone tracks on a global map (PlateCaree projection)

##############################################################################
# Datasets
# --------
#
#  No datasets are required for running this use case.  Only output from
#  running the MET Tool tc-pairs or the METplus tc pairs wrapper is required.

##############################################################################
# METplus Components
# ------------------
#
# This use case does not utilize any MET tools

##############################################################################
# METplus Workflow
# ----------------
#
# CyclonePlotter is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2015-03-01_12Z


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf

##############################################################################
# MET Configuration
# ---------------------
#
# No MET configuration is needed to run the cyclone plotter wrapper.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run as follows:
#
# 1) Passing in CyclonePlotter.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf \
#                          -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in CyclonePlotter.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf
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
# A successful run will generate output to both the screen and to the logfile:
#
#    INFO: METplus has successfully finished running.
#
# Additionally, two output files are created.  Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# TCPairs output for this use case will be found in cyclone/201503 (relative to **OUTPUT_BASE**)
# and will contain files with the following format:
#
# * 20150301.txt
# * 20150301.png

##############################################################################
# Keywords
# --------
#
# .. note:: `CyclonePlotterUseCase <https://dtcenter.github.io/METplus/search.html?q=CyclonePlotterUseCase&check_keywords=yes&area=default>`_

