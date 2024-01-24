"""
GridStat: Use binary observation field to verify percentile forecast
====================================================================

model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# Evaluation of a Probability of Exceedence (POE) field presents several difficulties. Some of these include a fitting verification statistic to report on,
# choosing a meaningful percentile field, and more. This use case was the culmination of attempting to verify a POE field for extreme temperature (defined
# as the 85th percentile) in METplus. In order to provide a streamlined process that didn't require vast reworkings of the MET tools, the observation
# field was converted to binary: 0s indicating a non-85th percentile temperature was observed, and a 1 indicating the opposite.
# Those observations are compared to the chosen forecast percentile and the HSS_EC becomes the main statistical focus, as the new hss_ec_value feature
# allowed the use case to more closely replicate in-house verificaiton that already existed.
# A final note that because the POE forecast file is a non-standard netCDF, Python Embedding was used to extract the desired field

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** 85th percentile of Temperature maximum, from GEFS
#
# | **Observations:** Climate Assessment Data Base (CADB), converted into a binary field relative to the 85th percentile
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** CPC

##############################################################################
# METplus Components
# ------------------
#
# This use case calls a Python script to extract the user-defined percentile forecast. METplus then verifies it against a binary observation field
# in GridStat and returns the requested line type outputs.

##############################################################################
# METplus Workflow
# ----------------
#
# The following boundary time is used for the entire script:
#
# | **Init Beg:** 2022-05-22
# | **Init End:** 2022-05-22
# 
# There is only one time processed for the use case.
# 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls a Python script to parse the user-requested percentile from the forecast dataset.
# This is controlled in the forecast VAR1 variable setting and is provided in
# parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE/Tmax_fcst_embedded.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE/Tmax_fcst_embedded.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstGEFS_obsCADB_BinaryObsPOE::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf
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
# Output for the use case will be found in model_applications/POE_tmax (relative to **OUTPUT_BASE**).
# The following files should exist:
#
# * grid_stat_1920000L_20220530_000000V_ctc.txt
# * grid_stat_1920000L_20220530_000000V_cts.txt
# * grid_stat_1920000L_20220530_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatUseCase
#   * PythonEmbeddingFileUseCase
#   * MediumRangeAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-GridStat_fcstGEFS_obsCADB_BinaryObsPOE.png'

