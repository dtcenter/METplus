"""
GridStat: Python Embedding for sea surface salinity using level 3, 1 day composite obs
======================================================================================

model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case utilizes Python embedding to extract several statistics from the sea surface salinity data over the globe, 
# which was already being done in a closed system. By producing the same output via METplus, this use case
# provides standardization and reproducible results.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** RTOFS sss file via Python Embedding script/file
#
# | **Observations:** SMOS sss file via Python Embedding script/file
#
# | **Sea Ice Masking:** RTOFS ice cover file via Python Embedding script/file
#
# | **Climatology:** WOA sss file via Python Embedding script/file
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** JPL's PODAAC and NCEP's FTPPRD data servers
# |

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed:
#
# * scikit-learn
# * pyresample
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
# This use case utilizes the METplus GridStat wrapper to generate a
# command to run the MET tool GridStat with Python Embedding for the specified user hemispheres

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only tool called in this example. This use case will pass in both the observation, forecast, 
# and climatology gridded data being pulled from the files via Python Embedding. All of the desired statistics 
# reside in the CNT line type, so that is the only output requested.
# It processes the following run time:
#
# | **Valid:** 2021-05-03 0Z
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`GridStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses one Python script to read forecast and observation data
#
# parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss/read_rtofs_smos_woa.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss/read_rtofs_smos_woa.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.conf
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
# Output for thisIce use case will be found in 20210503 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_SSS_000000L_20210503_000000V.stat 
# * grid_stat_SSS_000000L_20210503_000000V_cnt.txt 
# * grid_stat_SSS_000000L_20210503_000000V_pairs.nc 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * MarineAndCryosphereAppUseCase
#   * ClimatologyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-GridStat_fcstRTOFS_obsSMOS_climWOA_sss.png'

