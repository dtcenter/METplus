"""
StatAnalysis: Using Python Embedding
===========================================================================

met_tool_wrapper/StatAnalysis/StatAnalysis_python_embedding.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# This demonstrates how the Stat-Analysis tool can tie together results from other
# MET tools (including PointStat, GridStat, EnsembleStat, and WaveletStat)
# and provide summary statistical information. Matched pair records are passed into
# Stat-Analysis using python embedding.


##############################################################################
# Datasets
# --------
#
#
# | **WRF ARW point_stat output STAT files:**
# |     ...met_test/new
# |         point_stat_120000L_20050807_120000V.stat
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
# | **Data Source:** WRF

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus StatAnalysis wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool stat_analysis.

##############################################################################
# METplus Workflow
# ----------------
#
# StatAnalysis is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2005-08-07_00Z  
# | **Forecast lead:** 12 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/StatAnalysis/StatAnalysis.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/StatAnalysis/StatAnalysis_python_embedding.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped
#
# Note the following variables can be referenced in the MET configuration file.
# Refer to the MET Stat-Analysis Tool users guide for a further description of
# these MET configuration file settings.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL_LIST = {MODEL<n>} in the METplus configuration file.
# * **${DESC}** - User specified Description field. Corresponds to DESC_LIST in the METplus configuration file.
# * **${FCST_LEAD}** - Forecast lead time.  Corresponds to FCST_LEAD_LIST in the METplus configuration file.
# * **${OBS_LEAD}** -  Observation lead time.  Corresponds to OBS_LEAD_LIST in the METplus configuration file.
# * **${FCST_VALID_BEG}** - Forecast valid begin time. Corresponds to VALID_BEG in the METplus configuration file.
# * **${FCST_VALID_END}** - Forecast valid end time. Corresponds to VALID_END in the METplus configuration file.
# * **${FCST_VALID_HOUR}** - Forecast valid hour. Corresponds to FCST_VALID_HOUR_LIST in the METplus configuration file.
# * **${OBS_VALID_BEG}** - Observation valid begin time. Corresponds to VALID_BEG in the METplus configuration file.
# * **${OBS_VALID_END}** - Observation valid end time. Corresponds to VALID_END in the METplus configuration file.
# * **${OBS_VALID_HOUR}** - Observation valid hour. Corresponds to OBS_VALID_HOUR_LIST in the METplus configuration file.
# * **${FCST_INIT_BEG}** - Forecast initialization begin time. Corresponds to INIT_BEG in the METplus configuration file.
# * **${FCST_INIT_END}** - Forecast initialization end time. Corresponds to INIT_END in the METplus configuration file.
# * **${FCST_INIT_HOUR}** - Forecast initialization hour time. Corresponds to FCST_INIT_HOUR_LIST in the METplus configuration file.
# * **${OBS_INIT_BEG}** - Observation initialization begin time. Corresponds to INIT_BEG in the METplus configuration file.
# * **${OBS_INIT_END}** - Observation initialization end time. Corresponds to INIT_END in the METplus configuration file.
# * **${OBS_INIT_HOUR}** - Observation initialization hour time. Corresponds to OBS_INIT_HOUR_LIST in the METplus configuration file.
# * **${FCST_VAR}** - Forecast variable type. Corresponds to FCST_VAR_LIST in the METplus configuration file.
# * **${OBS_VAR}** -  Observation variable type. Corresponds to OBS_VAR_LIST in the METplus configuration file.
# * **${FCST_UNITS}** - Forecast units. Corresponds to FCST_UNITS_LIST in the METplus configuration file.
# * **${OBS_UNITS}** - Observation units. Corresponds to OBS_UNITS_LIST in the METplus configuration file.
# * **${FCST_LEVEL}** - Forecast level type. Corresponds to FCST_LEVEL_LIST in the METplus configuration file.
# * **${OBS_LEVEL}** - Observation level type. Corresponds to OBS_LEVEL_LIST in the METplus configuration file.
# * **${OBTYPE}** -  Observation type. Corresponds to a MODEL<n>_OBTYPE  in the METplus configuration file.
# * **${VX_MASK}** - Verification masking regions. Corresponds to VX_MASK_LIST in the METplus configuration file.
# * **${INTERP_MTHD}** - Interpolation methods. Corresponds to INTERP_MTHD_LIST in the METplus configuration file.
# * **${INTERP_PNTS}** - Interpolation points. Corresponds to INTERP_PNTS_LIST in the METplus configuration file.
# * **${FCST_THRESH}** - Forecast threshold. Corresponds to FCST_THRESH_LIST in the METplus configuration file.
# * **${OBS_THRESH}** - Observation threshold. Corresponds to OBS_THRESH_LIST in the METplus configuration file.
# * **${COV_THRESH}** - Coverage threshold. Corresponds to COV_THRESH_LIST in the METplus configuration file.
# * **${ALPHA}** - Alpha confidence values. Corresponds to ALPHA_LIST in the METplus configuration file.
# * **${LINE_TYPE}** - Line types used for all analysis. Corresponds to LINE_TYPE_LIST in the METplus configuration file.
# * **${JOB}** - Analysis jobs to be performed. Corresponds to STAT_ANALYSIS_JOB_NAME, STAT_ANALYSIS_JOB_ARGS and MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE in the METplus configuration file.


##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in StatAnalysis_python_embedding.conf then a user-specific system configuration file::
#
#   master_metplus.py -c /path/to/StatAnalysis_python_embedding.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs).
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
# Output for this use case will be found in met_tool_wrapper/StatAnalysis_python_embedding  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * WRF_ADPSFC_valid20050807_fcstvalidhour120000Z_out_stat.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#  `StatAnalysisToolUseCase <https://dtcenter.github.io/METplus/search.html?q=StatAnalysisToolUseCase&check_keywords=yes&area=default>`_
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#

# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-StatAnalysis.png'
