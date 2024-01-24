"""
StatAnalysis: Met Office LFRic UGRID
====================================

model_applications/unstructured_grids/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the use of python embedding to ingest and perform
# verification on an unstructured grid. This foregoes the need to interpolate
# to a regular grid as a step in the verification process, thereby avoiding
# any incurred interpolation error in the process.
#
# In particular, this use case ingests a UK MET Office LFRic forecast file in
# NetCDF format, which resides in the UGRID format of the cubed-sphere. The python
# library Iris was developed to perform analysis on various UGRID formats, and is
# employed here to ingest the file as well as perform direct interpolation 
# from the native forecast grid to observation locations, thereby forming matched
# pairs to pass to stat_analysis. In order to perform the interpolation using a 
# nearest-neighbors approach, the geovista python package is also used to form a 
# KD tree to be used in identifying the interpolation points to be used. This
# package is located at https://github.com/bjlittle/geovista/ and can be installed
# from a development version. It is also required to install the pyvista python 
# package. ASCII files containing observations are also ingested.
#
# The python embedding script itself performs the interpolation in time, and
# for this use case thins the observation data in order to reduce the run time.
# It is also noted that the observations for this use case were fabricated and
# correlated observation-forecast pairs are not expected.
#

##############################################################################
# Datasets
# --------
#
#
# | **Data source:** UK MET Office LFRic forecast files in UGRID NetCDF format and observations in ASCII format
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
# | **Valid:** 2021-05-05_00Z  
# | **Forecast lead:** 12 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/unstructured_grids/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/unstructured_grids/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.conf

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
# parm/use_cases/model_applications/unstructured_grids/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed/ugrid_lfric_mpr.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/unstructured_grids/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed/ugrid_lfric_mpr.py
#

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.conf -c /path/to/user_system.conf
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
# Output for this use case will be found in StatAnalysis_UGRID  (relative to **OUTPUT_BASE**)
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
#   * UnstructureGridsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/unstructured_grids-StatAnalysis_fcstLFRIC_UGRID_obsASCII_PyEmbed.png'
