"""
StatAnalysis: IODAv2
===========================================================================

model_applications/data_assimilation/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the Stat-Analysis tool and ingestion of HofX NetCDF files 
# that have been output from the Joint Effort for Data assimilation Integration (JEDI)
# data assimilation system. JEDI uses IODA version 2 formatted files, which are NetCDF files
# with certain requirements of variables and naming conventions. These files
# hold observations to be assimilated into forecasts, in this case taken from the JEDI software 
# test data, which contained a small number of Global observation-forecast pairs
# derived from the hofx application.
#
# UFO is a component of HofX, which maps the background forecast to observation space
# to form O minus B pairs. The HofX application of JEDI takes the input IODAv2 files and
# adds an additional variable which is the forecast value as interpolated to the 
# observation location. These HofX files are used as input to form Matched Pair (MPR) 
# formatted lists via Python embedding. In this case, Stat-Analysis then performs an aggregate_stat
# job and outputs statistics in an ascii file.
#
# This use case adopts the IODAv2 formatted NetCDF files, which replace the previous variable
# formatting scheme to make use of NetCDF groups.

##############################################################################
# Datasets
# --------
#
#
# | **Data source:** JEDI HofX output files in IODAv2 format
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# |

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus StatAnalysis wrapper to search for
# files that are valid for the given case and generate a command to run
# the MET tool stat_analysis.

##############################################################################
# METplus Workflow
# ----------------
#
# StatAnalysis is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2018-04-15_00Z  
# | **Forecast lead:** 0 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`StatAnalysis MET Configuration<stat-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read input data
#
# parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed/read_iodav2_mpr.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed/read_iodav2_mpr.py
#

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs).
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
# Output for this use case will be found in StatAnalysis_IODAv2  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * dump.out

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * StatAnalysisToolUseCase 
#   * PythonEmbeddingFileUseCase 
#   * DataAssimilationUseCase
#   * IODA2NCToolUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/data_assimilation-StatAnalysis_fcstGFS_HofX_obsIODAv2_PyEmbed.png'
