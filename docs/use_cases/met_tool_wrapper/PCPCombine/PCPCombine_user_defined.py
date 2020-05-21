"""
PCPCombine: User-defined Command Use Case
=============================================================================

PCPCombine_user_defined.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Derive statistics (sum, minimum, maximum, range, mean, standard deviation, and valid count) using six 3 hour
# precipitation accumulation fields. This use case builds the same command as pcp_derive.conf, but the command
# is defined completely by the user in the METplus configuration file.
#

##############################################################################
# Datasets
# --------
#
# | **Forecast:** WRF precipitation accumulation fields (24, 21, 18, 15, 12, and 9 hour forecast leads)
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/NCAR/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** WRF

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PCPCombine wrapper to generate a command to run PCPCombine to derive
# statistics from the fields. FCST_PCP_COMBINE_COMMAND is used to define all arguments to the call to the MET tool
# pcp_combine. This variable uses filename template notation using the 'shift' keyword to define filenames that
# are valid at a time slightly shifted from the run time, i.e. wrfprs_ruc13_{lead?fmt=%HH?shift=-3H}.tm00_G212.
# It also references other configuration variables in the METplus
# configuration file, such as FCST_PCP_COMBINE_INPUT_NAMES and FCST_PCP_COMBINE_INPUT_LEVELS, and FCST_PCP_COMBINE_INPUT_DIR.

##############################################################################
# METplus Workflow
# ----------------
#
# PCPCombine is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2005-08-07_00Z
# | **Forecast lead:** 24 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_user_defined.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_user_defined.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. PCPCombine does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PCPCombine_user_defined.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_user_defined.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PCPCombine_user_defined.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/PCPCombine/PCPCombine_user_defined.conf
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
# Output for this use case will be found in met_tool_wrapper/PCPCombine/PCPCombine_user_defined (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * wrfprs_ruc13_2005080700_f24_A24.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#  `PCPCombineToolUseCase <https://ncar.github.io/METplus/search.html?q=PCPCombineToolUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PCPCombine.png'
