"""
UserScript: Python Script to compute cable transport
=======================================================

model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# The Florida Current flows northward along the eastern Florida coast and feeds to the Gulf Stream. More info can
# be obtained from: https://www.aoml.noaa.gov/phod/floridacurrent/index.php
#
# This use case utilizes a Python script to calculate transport (units Sv) variations of the Florida current
# using a submarine cable and snapshot estimates made by shipboard instruments. The code compares the transport 
# using RTOFS data and compare it with the AOML cable transport data and computes BIAS, RMSE, CORRELATION, and 
# Scatter Index. The operational code utilizes 21 days of data and computes 7 day statistics. 
# For the use case 3 days of data are utilized. The valid date is passed though an argument. The valid date 
# is the last processed day i.e. the code grabs 3 previous days of data.    

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** RTOFS u(3zuio) amd ,v(3zvio) files via Python Embedding script/file
#
# | **Observations:** AOML Florida Current data via Python Embedding script/file
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** NOMADS RTOFS Global + Daily mean transport (https://www.aoml.noaa.gov/phod/floridacurrent/data_access.php)+ Eightmilecable (static, provided with the use case)

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed:
#
# * scikit-learn
# * pyproj
#
# If the version of Python used to compile MET did not have these libraries at the time of compilation, you will need to add these packages or create a new Python environment with these packages.
#
# If this is the case, you will need to set the MET_PYTHON_EXE environment variable to the path of the version of Python you want to use. If you want this version of Python to only apply to this use case, set it in the [user_env_vars] section of a METplus configuration file.::
#
#    [user_env_vars]
#    MET_PYTHON_EXE = /path/to/python/with/required/packages/bin/python

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus UserScript wrapper to generate a
# command to run with Python Embedding for the specified valid time. 

##############################################################################
# METplus Workflow
# ----------------
#
# This use case uses UserScript. All the gridded data being pulled from the files via Python Embedding. 
# All of the desired statistics are in the log file.
# It processes the following run time:
#
# | **Valid:** 2021-10-28
# 
# The code grabs the 20211028, 20211027, and 20211026 24 hour RTOFS files. 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. All of the processing is completed in the UserScript
#

##############################################################################
# User Script
# ----------------
#
# This use case uses one Python script to read forecast and observation data
# as well as processing the desired statistics.
#
# parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport/read_aomlcable_rtofs_transport.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport/read_aomlcable_rtofs_transport.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstRTOFS_obsAOML_calcTransport.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstRTOFS_obsAOML_calcTransport.conf::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/UserScript_fcstRTOFS_obsAOML_calcTransport.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [config]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
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
# Output for use case will be found in calc_transport (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * calc_transport.log 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * PythonEmbeddingFileUseCase
#   * MarineAndCryosphereAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-UserScript_fcstRTOFS_obsAOML_calcTransport.png'

