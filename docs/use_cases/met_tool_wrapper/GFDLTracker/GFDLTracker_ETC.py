"""
GFDLTracker: Extra Tropical Cyclone Use Case
============================================

met_tool_wrapper/GFDLTracker/GFDLTracker_ETC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Setup and run GFDL Tracker applications to track extra tropical cyclones.
# See :ref:`external-components-gfdl-tracker` for more information.
# A genesis vitals file is read into the tracker. This file contains
# information on storms that were tracked in the previous 2 runs so that
# additional data is attributed to the correct storm.
#

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GFDLTracker wrapper to generate a command
# to run the GFDL Tracker Fortran applications.

##############################################################################
# METplus Workflow
# ----------------
#
# GFDLTracker is the only tool called in this example.
# It processes the following run time:
#
# | **Init:** 2021-07-13 00Z
# | **Forecast lead**: All available leads (0 - 198 hour)
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GFDLTracker/GFDLTracker_ETC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GFDLTracker/GFDLTracker_ETC.conf

##############################################################################
# GFDL Tracker Configuration
# --------------------------
#
# METplus replaces values in the template configuration files read by the
# tracker based on user settings in the METplus configuration file.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GFDLTracker/template.nml

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run by passing in the conf file to the run script::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/GFDLTracker/GFDLTracker_ETC.conf
#
# See the :ref:`running-metplus` section of the User's Guide for more
# information on how to run use cases.
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
# Output for this use case will be found in gfdl_tracker/etc (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * gfs.2021071300.etc.txt
# * input.202107130000.nml

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GFDLTrackerToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
