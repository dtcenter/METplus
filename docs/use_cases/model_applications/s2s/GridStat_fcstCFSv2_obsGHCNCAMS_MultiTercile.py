"""
GridStat: Determine dominant ensemble members terciles and calculate categorical outputs
========================================================================================

model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# This use case ingests a CFSv2 Ensemble forecast, with all ensemble members in a single file for a given year. 
# 29 years of forecast ensembles are used to create probabilities for each tercile, which is accomplished by a Python script. 
# Of the terciles, each gridpoint is assigned a value corresponding to the tercile that is most likely to occur. This is compared to an observation set
# that contains the tercile data and MCTS line type is requested.
# This use case highlights the inclusion of tercile data for calculating HSS; in particular, how to utilize the hss_ec_value option to 
# preset the expected values rather than relying on categorical values.

##############################################################################
# Version Added
# -------------
#
# METplus version 5.0

##############################################################################
# Datasets
# --------
#
# | **Forecast:** 29 CFSv2 Ensemble files, 2m temperature fields
#
# | **Observations:** GHCNCAMS, 2m temperature field
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
# This use case calls a Python script 29 times, once for each year of data of the CFSv2 ensemble.
# Each time a successful call to the script is made, a grid of 1s, 2s, and 3s is returned, representing which tercile was dominant for the gridpoint.
# GridStat processes the forecast and observation fields, and outputs the requested line types.

##############################################################################
# METplus Workflow
# ----------------
#
# This use case utilizes 29 years of forecast data, with 24 members in each ensemble forecast.
# The following boundary times are used for the entire script:
#
# | **Init Beg:** 1982-01-01
# | **Init End:** 2010-01-02
# 
# Because the increment is 1 year, all January 1st from 1982 to 2010 are processed for a total of 29 years.
# 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf
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
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile /path/to/user_system.conf
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
# Output for the use case will be found in 29 folders(relative to **OUTPUT_BASE**).
# The output will follow the time information of the run. Specifically:
#
# * YYYY01
#
# where YYYY will be replaced by values corresponding to each of the years (1982 through 2010).
# Each of those folders will have the following files:
#
# * grid_stat_000000L_19820101_000000V_pairs.nc
# * grid_stat_000000L_19820101_000000V_mctc.txt
# * grid_stat_000000L_19820101_000000V_mcts.txt
# * grid_stat_000000L_19820101_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * ProbabilityVerificationUseCase
#   * PythonEmbeddingFileUseCase
#   * S2SAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.png'

