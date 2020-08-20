"""
TCMPRPlotter: Basic Use Case
=======================================================

met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Generate plots of tropical cyclone tracks.

##############################################################################
# Datasets
# --------
#
# No datasets are used in this use case, the tc-pairs output from the MET tc-pairs tool
# is used as input.
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCMPRPlotter wrapper to invoke the
# the MET script tcmpr_plotter.R.

##############################################################################
# METplus Workflow
# ----------------
#
# tcmpr_plotter.R is the only tool (script) called in this example.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf

##############################################################################
# MET Configuration
# ---------------------
#
# A MET configuration is not needed to run this single wrapper use case.

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in TCMPRPlotter.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCMPRPlotter.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf
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
# Output for this use case will be found in tcmpr_plots/2005080700 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * AMAX_WIND-BMAX_WIND_mean.png
# * AMAX_WIND-BMAX_WIND_mean.png
# * AMSLP-BMSLP_mean.png
# * AMSLP-BMSLP_median.png
# * TK_ERR_mean.png
# * TK_ERR_median.png

##############################################################################
# Keywords
# --------
#
# .. note::
#  `TCMPRPlotterUseCase <https://dtcenter.github.io/METplus/search.html?q=TCMPRPlotterUseCase&check_keywords=yes&area=default>`_
