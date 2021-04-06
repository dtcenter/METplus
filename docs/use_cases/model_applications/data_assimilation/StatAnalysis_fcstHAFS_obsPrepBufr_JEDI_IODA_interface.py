"""
StatAnalysis: JEDI
===========================================================================

model_applications/data_assimilation/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the Stat-Analysis tool and ingestion of HofX netCDF files 
# that have been output from the Joint Effort for Data assimilation Integration (JEDI)
# data assimilation system. JEDI uses "IODA" formatted files, which are netCDF files
# with certain requirements of variables and naming conventions. These files
# hold observations to be assimilated into forecasts, in this case the FV3-based
# Hurricane Analysis and Forecast System (HAFS). HAFS performs tc initialization 
# by using synthetic observations of conventional variables to relocate a 
# tropical cyclone as informed by a vortex tracker, in this case Tropical Storm Dorian. 
#
# In this case 100224 observations from 2019082418 are used. These were converted
# from perpbufr files via a fortran ioda-converter provided by the Joint Center for
# Satellite Data Assimilation, which oversees the development of JEDI. The variables
# used are t, q, u, and v.
#
# The first component of JEDI to be incorporated into operational systems will be
# the Unified Forward Operator (UFO) to replace the GSI observer in global EnKF forecasts.
# UFO is a component of HofX, which maps the background forecast to observation space
# to form O minus B pairs. The HofX application of JEDI takes the input IODA files and
# adds an additional variable, <variable_name>@hofx that is to be paired with 
# <variable_name>@ObsValue. These HofX files are used as input to form Matched Pair (MPR) 
# formatted lists via Python embedding. In this case, Stat-Analysis then performs a filter job and
# outputs the filtered MPR formatted columns in an ascii file.
#

##############################################################################
# Datasets
# --------
#
#
# | **Data source:** JEDI HofX output files in IODA format
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
# | **Valid:** 2019-08-24_18Z  
# | **Forecast lead:** 6 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf

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
# parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface/read_ioda_mpr.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/data_assimilation/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface/read_ioda_mpr.py
#

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf -c /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/data_assimilation/StatAnalysis_HofX  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * dump.out

##############################################################################
# Keywords
# --------
#
# .. note::
#  `StatAnalysisToolUseCase <https://dtcenter.github.io/METplus/search.html?q=StatAnalysisToolUseCase&check_keywords=yes&area=default>`_
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#  `TCandExtraTCAppUseCase <https://dtcenter.github.io/METplus/search.html?q=TCandExtraTCAppUseCase&check_keywords=yes&area=default>`_
#  `NOAAEMCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NOAAEMCOrgUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/data_assimilation-StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.png'
