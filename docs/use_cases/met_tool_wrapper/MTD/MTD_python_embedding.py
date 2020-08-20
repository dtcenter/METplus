"""
MTD using Python Embedding
==========================

met_tool_wrapper/MTD/MTD_python_embedding.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare forecast and observation 3 hour precipitation accumulation spatially and temporally over the 6 hour, 9 hour, and 12 hour forecast leads.
#

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
# This use case utilizes the METplus MTD wrapper to read in files using Python Embedding to demonstrate how to read in data this way.
#

##############################################################################
# METplus Workflow
# ----------------
#
# MTD is the only tool called in this example. It processes a single run time with three forecast leads. The input data are simple text files with no timing information, so the list of forecast leads simply duplicates the same file multiple times to demonstrate how data is read in via Python Embedding.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/MTD/MTD_python_embedding.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/MTD/MTD_python_embedding.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MIN_VOLUME}** - Minimum volume to be considered valid data. Corresponds to MTD_MIN_VOLUME in the METplus configuration file.
# * **${FCST_CONV_RADIUS}** - Convolution radius used for forecast data. Corresponds to FCST_MODE_CONV_RADIUS in the METplus configuration files.
# * **${FCST_CONV_THRESH}** - List of convolution thresholds used for forecast data. Corresponds to FCST_MODE_CONV_THRESH in the METplus configuration files.
# * **${OBS_CONV_RADIUS}** - Convolution radius used for observation data. Corresponds to OBS_MODE_CONV_RADIUS in the METplus configuration files.
# * **${OBS_CONV_THRESH}** - List of convolution thresholds used for observation data. Corresponds to OBS_MODE_CONV_THRESH in the METplus configuration files.
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${LEVEL}** - Vertical level of the forecast input data. Used in output_prefix to include input information in the output filenames. Corresponds to [FCST/BOTH]_VAR<n>_LEVELS in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${FCST_VAR}** - Field name of forecast data to process. Used in output_prefix to include input information in the output filenames. Corresponds to [FCST/BOTH]_VAR<n>_NAME in the METplus configuration file.
# * **${OBS_VAR}** - Field name of observation data to process. Used in output_prefix to include input information in the output filenames. Corresponds to [OBS/BOTH]_VAR<n>_NAME in the METplus configuration file.
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to MTD_REGRID_TO_GRID in the METplus configuration file.
# * **${OUTPUT_PREFIX}** - String to prepend to the output filenames. Corresponds to MTD_OUTPUT_PREFIX in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_python_embedding.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MTD/MTD_python_embedding.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_python_embedding.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/MTD/MTD_python_embedding.conf
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
# Output for this use case will be found in met_tool_wrapper/MTD/mtd_python_embedding (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * mtd_PYTHON_20050807_120000V_2d.txt
# * mtd_PYTHON_20050807_120000V_3d_pair_cluster.txt
# * mtd_PYTHON_20050807_120000V_3d_pair_simple.txt
# * mtd_PYTHON_20050807_120000V_3d_single_cluster.txt
# * mtd_PYTHON_20050807_120000V_3d_single_simple.txt
# * mtd_PYTHON_20050807_120000V_obj.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#  `MTDToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MTDToolUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#  `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-MTD.png'
