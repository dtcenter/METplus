"""
IODA2NC: Basic Use Case
=======================

met_tool_wrapper/IODA2NC/IODA2NC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Convert IODA NetCDF files to MET NetCDF format.

##############################################################################
# Datasets
# --------
#
# **Input:** IODA NetCDF observation
#
# **Location:** All of the input data required for this use case can be found
# in the met_test sample data tarball. Click here to the METplus releases
# page and download sample data for the appropriate release:
# https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will set the
# value of INPUT_BASE. See the `Running METplus`_ section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus IODA2NC wrapper to generate a command
# to run the MET tool ioda2nc if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# IODA2NC is the only tool called in this example.
# It processes the following run time(s):
#
# | **Valid:** 2020-03-10 12Z
#

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/IODA2NC/IODA2NC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/IODA2NC/IODA2NC.conf

##############################################################################
# MET Configuration
# ---------------------
#
# .. note::
#     See the :ref:`IODA2NC MET Configuration<ioda2nc-met-conf>`
#     section of the User's Guide for more information on the environment
#     variables used in the file below.
#
# parm/met_config/IODA2NCConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/IODA2NCConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Provide the use case .conf configuration file to the run_metplus.py script.
#
# /path/to/METplus/parm/use_cases/met_tool_wrapper/IODA2NC/IODA2NC.conf
#
# See the :ref:`running-metplus` section of the System Configuration chapter
# for more details.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following to the screen and the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data
# was generated. Output for this use case will be found in
# met_tool_wrapper/ioda2nc
# (relative to **OUTPUT_BASE**)
# and will contain the following file(s):
#
# * ioda.NC001007.2020031012.summary.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * IODA2NCToolUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-IODA2NC.png'
#
