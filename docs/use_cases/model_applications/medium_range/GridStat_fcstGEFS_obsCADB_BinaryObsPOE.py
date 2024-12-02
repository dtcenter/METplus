"""
GridStat: Use binary observation field to verify percentile forecast
====================================================================

model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

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
# Version Added
# -------------
#
# METplus version 5.1

##############################################################################
# Datasets
# --------
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
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf
#

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls a Python script to parse the user-requested percentile from the forecast dataset.
# This is controlled in the forecast VAR1 variable setting and is provided in the below file.
#
# .. dropdown:: parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE/Tmax_fcst_embedded.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE/Tmax_fcst_embedded.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/GridStat_fcstGEFS_obsCADB_BinaryObsPOE.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

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

