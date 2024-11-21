"""
METdbLoad: Brightness Temperature
=================================

model_applications/short_range/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# Load MET data into a database using the met_db_load.py script found in 
# dtcenter/METdataio.  Specifically, this use case loads distance map output
# from grid_stat and mode output into a database.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# | **Input:** MET .stat files and MODE text files
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to see the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus METdbLoad wrapper to search for
# files ending with .stat or .txt, substitute values into an XML load
# configuration file, and call met_db_load.py.  It then loads data
# into a METviewer database for the following use cases:
# MODE_fcstFV3_obsGOES_BrightnessTemp, MODE_fcstFV3_obsGOES_BrightnessTempObjs,
# and GridStat_fcstFV3_obsGOES_BrightnessTempDmap.

##############################################################################
# METplus Workflow
# ----------------
# The METdbload is run once and loads data for two ensemble members, one model initialization
# time and 2 forecast lead times, listed below.
#
# | **Valid:** 2019-05-21_01Z
# | **Forecast lead:** 01
# |
#
# | **Valid:** 2019-05-21_02Z
# | **Forecast lead:** 02
# |


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/short_range/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf

##############################################################################
# MET Configuration
# -----------------
# [UPDATE_SECTION_CONTENT]
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`

##############################################################################
# XML Configuration
# -----------------
#
# METplus substitutes values in the template XML configuration file based on
# user settings in the METplus configuration file. While the XML template may
# appear to reference environment variables, this is not actually the case.
# These strings are used as a reference for the wrapper to substitute values.
#
# .. note::
#     See the :ref:`METdbLoad XML Configuration<met_db_load-xml-conf>`
#     section of the User's Guide for more information on the values
#     substituted in the file below:
#
# .. dropdown:: METdbLoadConfig.xml
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoadConfig.xml

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Output files are not generated.  Rather, data should be available in the METviewer database.
# The data in the database should include Stat data for two variables and two model ensembles,
# and mode data.
#


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * METdbLoadUseCase
#   * ShortRangeAppUseCase
#   * NOAAEMCOrgUseCase
#   * NOAAHWTOrgUseCase  
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-METdbLoad_fcstFV3_obsGoes_BrightnessTemp.png'
#
