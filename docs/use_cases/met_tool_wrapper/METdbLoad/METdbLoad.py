"""
METdbLoad: Basic Use Case
=========================

met_tool_wrapper/METdbLoad/METdbLoad.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Load MET data into a database using the met_db_load.py script
# found in dtcenter/METdatadb

##############################################################################
# Datasets
# --------
#
# | **Input:** Various MET .stat and .tcst files
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to see the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus METdbLoad wrapper to search for
# files ending with .stat or .tcst, substitute values into an XML load
# configuration file, and call met_db_load.py to load MET data into a
# database.

##############################################################################
# METplus Workflow
# ----------------
#
# METdbLoad is the only tool called in this example. It does not loop over
# multiple run times:
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoad.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoad.conf

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
# 1) Passing in METdbLoad.conf followed by a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoad.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config and then passing in METdbLoad.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoad.conf
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


##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-METdbLoad.png'
#
# .. note:: `METdbLoadUseCase <https://dtcenter.github.io/METplus/search.html?q=METdbLoadUseCase&check_keywords=yes&area=default>`_
