"""
Point2Grid: Calculate Practically Perfect Probabilities
=======================================================

model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf

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
# To use storm reports as observations to calculate 
# Practically Perfect probabilities.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** [UPDATE_SECTION_CONTENT]
#
# **Observation:** Local Storm Reports
#
# **Climatology:** [UPDATE_SECTION_CONTENT]
#
# **Location:** [UPDATE_SECTION_CONTENT]

##############################################################################
# METplus Components
# ------------------
#
# This use case runs ASCII2NC to get the storm reports in netcdf format, runs
# Point2Grid to get those netcdf observations onto a grid, runs RegridDataPlane
# to use that gridded data as a mask to calculate probabilities 
#

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2020020500
#
# **End time (INIT_END):** 2020020500
#
# **Increment between beginning and end times (INIT_INCREMENT):** 24H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24H
#
# The following tools are used for each run time:
#
# ASCII2NC > Point2Grid > RegridDataPlane 
#
# This example runs on a single time/file at a time. Each storm report is 
# assumed to have no more than 24 hours of data inside 
#
# Run times:
#
# 2020-02-05

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf
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
# .. dropdown:: Ascii2NcConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read input data.
#
#  .. dropdown:: parm/use_cases/model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect/read_ascii_storm.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect/read_ascii_storm.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on
# `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/short_range/practically_perfect/ (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * StormReps_211_Probs.20200205.nc 
#


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * ASCII2NCToolUseCase
#   * Point2GridToolUseCase
#   * RegridDataPlaneToolUseCase 
#   * RegriddingInToolUseCase 
#   * NetCDFFileUseCase
#   * PythonEmbeddingFileUseCase 
#   * ShortRangeAppUseCase
#   * NCAROrgUseCase 
#   * ProbabilityGenerationUseCase
#   * MaskingFeatureUseCase 
#   * HMTOrgUseCase 
#   * HWTOrgUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.png'
