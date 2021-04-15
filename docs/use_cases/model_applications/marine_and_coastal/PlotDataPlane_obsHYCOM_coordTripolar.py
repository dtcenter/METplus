"""
PlotDataPlane: Python Embedding of tripolar coordinate file
===========================================================

model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# By producing a postscript image from a file that utilizes a tripolar coordinate system, this use case shows METplus can utilize
# python embedding to ingest and utilize file structures on the same coordinate system.

##############################################################################
# Datasets
# --------
#
# | **Input:** Python Embedding script/file, HYCOM observation file, coordinate system weight files (optional)
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** HYCOM model
# |

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed:
#
# * xesmf
#
# If the version of Python used to compile MET did not have these libraries at the time of compilation, you will need to add these packages or create a new Python environment with these packages.
#
# If this is the case, you will need to set the MET_PYTHON_EXE environment variable to the path of the version of Python you want to use. If you want this version of Python to only apply to this use case, set it in the [user_env_vars] section of a METplus configuration file.:
#
#    [user_env_vars]
#    MET_PYTHON_EXE = /path/to/python/with/required/packages/bin/python

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PlotDataPlane wrapper to generate a
# command to run the MET tool PlotDataPlane with Python Embedding if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PlotDataPlane is the only tool called in this example.
# It processes the following run time:
#
# | **Valid:** 2020-01-27 0Z
# |

#
# As it is currently set, the configuration file will pass in the path to the observation data,
# as well as a path to the weights for the coordinate system. This is done in an effort to speed up running the use case.
# These weight files are not required to run at the time of executing the use case, but will be made via Python Embedding
# if they are not found/passed in at run time. Additional user configurations, including the lat/lon spacing, can be found in the
# python script.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar.conf

##############################################################################
# MET Configuration
# ---------------------
#
# This tool does not use a MET configuration file.
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses one Python script to read input data, passed through two times
#
# parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar/read_tripolar_grid.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar/read_tripolar_grid.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PlotDataPlane_obsHYCOM_coordTripolar.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PlotDataPlane_obsHYCOM_coordTripolar.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/marine_and_coastal/PlotDataPlane_obsHYCOM_coordTripolar.conf
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
# Output for thisIce use case will be found in model_applications/PlotDataPlane_obsHYCOM_coordTripolar
# (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * HYCOM_iceCoverage_north.ps
# * HYCOM_iceCoverage_south.ps 

##############################################################################
# Keywords
# --------
#
# .. note::
#    `PlotDataPlaneToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PlotDataPlaneToolUseCase&check_keywords=yes&area=default>`_
#    `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/model_applications-PlotDataPlane_obsHYCOM_coordTripolar.png'
#
