"""
Grid-Stat: Surrogate Severe and Practically Perfect Evaluation
==============================================================

model_applications/short_range/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# To evaluate the surrogate severe forecasts at predicting Severe weather
# using the (12Z - 12Z) practically perfect storm reports.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** HRRR Surrogate Severe Data
#
# **Observation:** Practically Perfect from Local Storm Reports.
#
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case runs grid_stat to create categorical statistics for 
# Surrogate Severe derived from the HRRR model and Practially Perfect
# Analysis derived from local storm reports.  

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2020020612
#
# **End time (VALID_END):** 2020020612
#
# **Increment between beginning and end times (VALID_INCREMENT):** 86400
#
# **Sequence of forecast leads to process (INIT_SEQ):** 0
#
# The grid_stat tool is run for each time. This example loops by valid time.  It
# processes 1 valid time, listed below.
#
# | **Valid:** 2020-02-06_12Z
# | **Forecast lead:** 36

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/short_range/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/short_range/surrogate_severe_prac_perfect/grid_stat (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# grid_stat_360000L_20200206_120000V_ctc.txt
# grid_stat_360000L_20200206_120000V_cts.txt
# grid_stat_360000L_20200206_120000V.stat

##############################################################################
# Keywords
# --------
#
#
#
# .. note::
#
#   * GridStatToolUseCase
#   * ShortRangeAppUseCase
#   * NetCDFFileUseCase 
#   * NOAAHWTOrgUseCase  
#   * NCAROrgUseCase 
#   * NOAAHMTOrgUseCase  
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-SS_PP_prob.png'
