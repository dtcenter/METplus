"""
SeriesAnalysis: Using Python Embedding
============================================================================

met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python
_embedding.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. This is a demonstration of using python embedding to pass and read in external files,
# which have a data format that MET would not otherwise be able to parse.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** Dummy text files found in the MET shared directory
# | **Observation:** Dummy text files found in the MET shared directory
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus SeriesAnalysis wrapper to search for
# files as determined by the Python script. 

##############################################################################
# METplus Workflow
# ----------------
#
# SeriesAnalysis is the only tool called in this example. It processes simple text files
# with no timining or meteorological information to demonstrate how SeriesAnalysis can be 
# run utilizing Python Embedding.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python_embedding.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python_embedding.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to SERIES_ANALYSIS_REGRID_TO_GRID in the METplus configuration file.
# * **${CLIMO_MEAN_FILE}** - Optional path to climatology mean file. Corresponds to SERIES_ANALYSIS_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${CLIMO_STDEV_FILE}** - Optional path to climatology standard deviation file. Corresponds to SERIES_ANALYSIS_CLIMO_STDEV_INPUT_[DIR/TEMPLATE] in the METplus configuration file.

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in SeriesAnalysis_python_embedding.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python_embedding.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in SeriesAnalysis_python_embedding.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python_embedding.conf
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
# Output for this use case will be found in met_tool_wrapper/SeriesAnalysis (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * python_sa.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#  `SeriesAnalysisUseCase <https://dtcenter.github.io/METplus/search.html?q=SeriesAnalysisUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#  `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-SeriesAnalysis.png'
