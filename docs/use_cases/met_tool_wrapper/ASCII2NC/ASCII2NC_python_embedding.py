"""
ASCII2NC: Using Python Embedding
=============================================================================

met_tool_wrapper/ASCII2NC/ASCII2NC_python
_embedding.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. Simply converting file formats so point observations can be read by the MET tools.

##############################################################################
# Datasets
# --------
#
# | **Observations:** Precipitation accumulation observations in ASCII text files
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ASCII2NC wrapper to generate a command to run the MET tool ASCII2NC.

##############################################################################
# METplus Workflow
# ----------------
#
# ASCII2NC is the only tool called in this example. It has one run time, but the time is not relevant because the files processed do not have any time information in the names.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. No MET configuration file for ASCII2NC is used in this case.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in ASCII2NC_python_embedding.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in ASCII2NC_python_embedding.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf
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
# Output for this use case will be found in met_tool_wrapper/ASCII2NC (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * ascii2nc_python.nc

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-ASCII2NC.png'
#
# .. note::
#  `ASCII2NCToolUseCase <https://dtcenter.github.io/METplus/search.html?q=ASCII2NCToolUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
