"""
Grid-Stat: Standard Verification of Surface Fields
==================================================

model_applications/medium_range/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between observation
# data in gridded format to a gridded forecast. These values can be used to assess 
# the skill of the prediction.  Statistics stored only as partial sums to save space.
# Stat-Analysis must be used to compute Continuous Statistics.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS
#
# **Observation:** GFS
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
#
# **Data Source:** GFS

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool grid_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2017061300
#
# **End time (VALID_END):** 2017061306
#
# **Increment between beginning and end times (VALID_INCREMENT):** 21600
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24
#
# GridStat is the only tool called in this example. It processes the following run times:
#
# | **Valid:** 2017-06-13 0Z
# | **Forecast lead:** 24 hour
# |
# | **Valid:** 2017-06-13 6Z
# | **Forecast lead:** 24 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf

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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf /path/to/user_system.conf
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
# Output for this use case will be found in met_out/{MODEL}/sfc (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * 00Z/GFS/GFS_20170613.stat
# * 06Z/GFS/GFS_20170613.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * MediumRangeAppUseCase
#   * GRIBFileUseCase
#   * NOAAEMCOrgUseCase
#   * ClimatologyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-GridStat_fcstGFS_obsGFS_Sfc_MultiField.png'
#
