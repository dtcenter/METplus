"""
MADIS2NC: Basic Use Case
========================

met_tool_wrapper/MADIS2NC/MADIS2NC.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Converting file formats so point observations can be read by the MET tools.

##############################################################################
# Datasets
# --------
#
# | **Observations:** METAR observations in MADIS NetCDF files
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** MADIS
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus MADIS2NC wrapper to generate a command to run the MET tool madis2nc if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# MADIS2NC is the only tool called in this example. It processes the following
# run time:
#
# | **Valid:** 2012-04-09_12Z
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/MADIS2NC/MADIS2NC.conf

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
# .. note:: See the :ref:`MADIS2NC MET Configuration<madis2nc-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Madis2NcConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the path to MADIS2NC.conf as an argument to run_metplus.py::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/MADIS2NC/MADIS2NC.conf
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
# Output for this use case will be found in madis2nc (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * met_metar_2012040912_F000.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MADIS2NCToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-MADIS2NC.png'
#
