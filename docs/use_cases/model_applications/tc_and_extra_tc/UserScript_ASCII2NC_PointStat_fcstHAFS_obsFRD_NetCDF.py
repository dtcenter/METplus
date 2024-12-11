"""
Point-Stat: Standard Verification for CONUS Surface 
===================================================

model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between observation data
# in point format to a gridded forecast. These values can be used to assess the skill 
# of the prediction. Statistics are store as partial sums to save space and Stat-Analysis
# must be used to compute Continuous statistics.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** HAFS temperature
#
# **Observation:** HRD Dropsonde data 
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#
# **Dropsonde Data Source:** `Hurricane Research Division Sonde Archive  <https://www.aoml.noaa.gov/hrd/data_sub/dropsonde.html>`_

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ASCII2NC wrapper to convert full-resolution data (frd) dopsonde point observations to NetCDF format and then compare them to gridded forecast data using PointStat.


##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2019082912
#
# **End time (VALID_END):** 2019082912
#
# **Increment between beginning and end times (VALID_INCREMENT):** 21600
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0,6,12,18
#
# The use case runs the UserScript wrapper (untar the dropsonde file and extract the files to a directory),
# ASCII2NC (convert the ascii files to NetCDF format), and PointStat (compute statistics against
# HAFS model output), which are the tools called in this example. It processes the following run times:
#
# **Valid:** 2019-08-29 12Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf
#
# Notes for USER_SCRIPT* METplus conf items for this use case:
#
# * **${USER_SCRIPT_RUNTIME_FREQ}** - Corresponds to USER_SCRIPT_RUNTIME_FREQ in the METplus configuration file.
# * **${USER_SCRIPT_INPUT_DIR}** - Corresponds to USER_SCRIPT_INPUT_DIR in the METplus configuration file.
# * **${USER_SCRIPT_OUTPUT_DIR}** - Corresponds to USER_SCRIPT_OUTPUT_DIR in the METplus configuration file.
# * **${USER_SCRIPT_COMMAND}** - Arguments needed to hrd_frd_sonde_find_tar.py corresponds to USER_SCRIPT_INPUT_TEMPLATE.
# * **${USER_SCRIPT_INPUT_TEMPLATE}** - Input template to hrd_frd_sonde_find_tar.py: USER_SCRIPT_INPUT_DIR, valid date (%Y%m%d), and USER_SCRIPT_OUTPUT_DIR.

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
# .. dropdown:: Ascii2NcConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses two Python embedding scripts: one to download the data (hrd_frd_sonde_find_tar.py) and the other to process it (hrd_frd_sonde_for_ascii2nc.py).
#
# .. dropdown:: parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_find_tar.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_find_tar.py
#
# .. dropdown:: parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_for_ascii2nc.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_for_ascii2nc.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications//tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf /path/to/user_system.conf
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
# Output for this use case will be found in nam (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_180000L_20190829_120000V.stat
# * point_stat_180000L_20190829_120000V_fho.txt
# * point_stat_180000L_20190829_120000V_eclv.txt
# * point_stat_180000L_20190829_120000V_ctc.txt
# * point_stat_180000L_20190829_120000V_cnt.txt
# * point_stat_180000L_20190829_120000V_mpr.txt

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCandExtraTCAppUseCase
#   * UserScriptUseCase
#   * PointStatToolUseCase
#   * ASCII2NCToolUseCase
#   * TropicalCycloneUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.png'
#
