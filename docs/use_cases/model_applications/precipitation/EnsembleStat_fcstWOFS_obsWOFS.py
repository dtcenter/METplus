"""
Ensemble-Stat: WoFS
===================

model_application/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf

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
# Comparing the Warn on Forecast System (WoFS) ensemble to the MRMS observed
# variable field to understand its forecasting abilities. Specifically focusing on
# accumulated precipitation at different neighborhood distances and accumulation
# thresholds to provide meaningful analysis output that can provide direction to future WoFS improvement.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** WoFS Ensemble
#
# **Observation:** [UPDATE_SECTION_CONTENT]
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

###############################################################################
# METplus Components
# ------------------
#
# This use case runs PCP-Combine on each ensemble member, then runs
# Ensemble-Stat on the output. Finally, it runs Grid-Stat on the output from
# Ensemble-Stat.

###############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 202006151700
#
# **End time (INIT_END):** 202006151700
#
# **Increment between beginning and end times (INIT_INCREMENT):** 3600
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1
#
# The following tools are used for each run time:
# PCPCombine, EnsembleStat, GridStat
#
# This example loops by initialization time. For each initialization time
# it will process the 1 hour forecast lead
#
# Run times:
#
# | **Init:** 2020-06-15_17Z
# | **Forecast lead:** 1 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: EnsembleStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped
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
#  run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf /path/to/user_system.conf
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
# Output for this use case will be found in WOFS/grid_stat (relative to **OUTPUT_BASE**)
# The following folder/file combination will be created::
#
# * 20200615/1700/grid_stat_WOFS_PCP_1700_A1_000000L_20200615_180000V_pairs.nc
# * 20200615/1700/grid_stat_WOFS_PCP_1700_A1_000000L_20200615_180000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * EnsembleStatToolUseCase
#   * PrecipitationAppUseCase
#   * GRIB2FileUseCase
#   * EnsembleAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-EnsembleStat_fcstWOFS_obsWOFS.png'
