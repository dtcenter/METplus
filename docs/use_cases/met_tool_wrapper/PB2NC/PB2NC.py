"""
PB2NC: Basic Use Case
=====================

met_tool_wrapper/PB2NC/PB2NC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Simply converting file formats so point observations can be read by the MET tools.

##############################################################################
# Datasets
# --------
#
# | **Observations:** Various fields in prepBUFR file
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** Unknown
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PB2NC wrapper to generate a command to run the MET tool PB2NC if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PB2NC is the only tool called in this example. It processes the following
# run time:
#
# | **Valid:** 2007-03-31_12Z
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`PB2NC MET Configuration<pb2nc-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PB2NCConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PB2NC.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PB2NC.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PB2NC/PB2NC.conf
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
# Output for this use case will be found in pb2nc (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * sample_pb.nc

##############################################################################
# Keywords
# --------
#
# .. note:: `PB2NCToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PB2NCToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PB2NC.png'
