"""
GempakToCF: Basic Use Case
=============================================================================

met_tool_wrapper/GempakToCF/GempakToCF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. Simply converting data to a format that MET can read.
#

##############################################################################
# Datasets
# --------
#
# | **Observations:** MRMS QPE
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# External Dependencies
# ---------------------
#
# **GempakToCF.jar**
#
# GempakToCF is an external tool that utilizes the Unidata NetCDF-Java package. The jar file that can be used to run the utility is available here: https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
#
# See the METplus Configuration section below for information on how to configure METplus to find the jar file.
#
# More information on the package used to create the file is here:  https://www.unidata.ucar.edu/software/netcdf-java
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GempakToCF wrapper to generate a command to run GempakToCF (external)  if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GempakToCF is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2017-06-22 0Z
#
# | **Init:** 2017-06-22 12Z
#
#

##############################################################################
# METplus Configuration
# ---------------------
#
# To enable Gempak support, you must set [exe] :term:`GEMPAKTOCF_JAR` in your user METplus configuration file.:
#
#    [exe]
#    :term:`GEMPAKTOCF_JAR` = /path/to/GempakToCF.jar
#
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf
#


##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GempakToCF.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GempakToCF.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf
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
# Output for this use case will be found in met_tool_wrapper/GempakToCF (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * 20170622/mrms_qpe_2017062200.nc
# * 20170622/mrms_qpe_2017062212.nc


##############################################################################
# Keywords
# --------
#
# .. note::
#  `GempakToCFToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GempakToCFToolUseCase&check_keywords=yes&area=default>`_,
#  `GEMPAKFileUseCase <https://dtcenter.github.io/METplus/search.html?q=GEMPAKFileUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHMTOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#  `NOAAWPCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GempakToCF.png'
