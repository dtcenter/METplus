"""
METdbLoad: Brightness Temperature
=================================

model_applications/
convection_allowing_model/
METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Load MET data into a database using the met_db_load.py 
# script found in dtcenter/METdatadb.

##############################################################################
# Datasets
# --------
#
# | **Input:** MET .stat files and MODE text files
#
# ********FIX ME...  Need to figure out where the .stat files are stored.  Are they already in the tarball or do I need to add??********** 
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
# into a METviewer database for the following use cases, 
# MODE_fcstFV3_obsGOES_BrightnessTemp, MODE_fcstFV3_obsGOES_BrightnessTempObjs,
# and GridStat_fcstFV3_obsGOES_BrightnessTempDmap.  It loads the data into a database
# called mv_brightness_temp

##############################################################################
# METplus Workflow
# ----------------
# The METdbload is run once and loads data for two ensemble members, one model initialization
# time and 2 forecast lead times, listed below.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf

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
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoadConfig.xml

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf followed by a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config and then passing in METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/METdbLoad_fcstFV3_obsGoes_BrightnessTemp.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path to directory where METplus output will be written. This must be in a location where you have write permissions
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
#   * ConvectionAllowingModelsAppUseCase 
#   * NOAAEMCOrgUseCase
#   * NOAAHWTOrgUseCase  
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-METdbLoad_fcstFV3_obsGoes_BrightnessTemp.png'
#
