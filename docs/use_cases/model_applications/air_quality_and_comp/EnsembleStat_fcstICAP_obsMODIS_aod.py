"""
EnsembleStat: Using Python Embedding for Aerosol Optical Depth
=============================================================================

model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS\
_aod.conf

"""
############################################################################
# Scientific Objective
# --------------------
#
# To provide useful statistical information on the relationship between
# observation data for aersol optical depth (AOD) to an ensemble forecast.
# These values can be used to help correct ensemble member deviations from observed values.


##############################################################################
# Datasets
# --------
#
# | **Forecast:** International Cooperative for Aerosol Prediction (ICAP) ensemble netCDF file, 7 members
# | **Observation:** Aggregate netCDF file with MODIS observed AOD field
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus EnsembleStat wrapper to read in files using Python Embedding
#

##############################################################################
# METplus Workflow
# ----------------
#
# EnsembleStat is the only tool called in this example. It processes a single run time with seven ensemble members. Three of the members do not have data for the AOD field, so EnsembleStat will only process four of the members for statistics.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${MODEL}** - Name of forecast input. Corresponds to MODEL in the METplus configuration file.
# * **${OBTYPE}** - Name of observation input. Corresponds to OBTYPE in the METplus configuration file.
# * **${ENS_THRESH}** - Threshold for ratio of valid files to expected files to allow application to run. Corresponds to ENSEMBLE_STAT_ENS_THRESH in the METplus configuration file.
# * **${ENS_VLD_THRESH}** - Threshold for ratio of valid data values for each grid point to number of ensemble mebers to allow application to run. Corresponds to ENSEMBLE_STAT_ENS_VLD_THRESH in the METplus configuration file.
# * **${ENS_FIELD}** - Formatted ensemble product fields information. Generated from ENS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_WINDOW_BEGIN}** - Corresponds to OBS_WINDOW_BEGIN or OBS_ENSEMBLE_STAT_WINDOW_BEGIN in the METplus configuration file.
# * **${OBS_WINDOW_END}** - Corresponds to OBS_WINDOW_END or OBS_ENSEMBLE_STAT_WINDOW_END in the METplus configuration file.
# * **${CLIMO_MEAN_FILE}** - Optional path to climatology mean file. Corresponds to ENSEMBLE_STAT_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${CLIMO_STDEV_FILE}** - Optional path to climatology standard deviation file. Corresponds to ENSEMBLE_STAT_CLIMO_STDEV_INPUT_[DIR/TEMPLATE] in the METplus configuration file.

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses two Python embedding scripts to read input data
#
# parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/forecast_embedded.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/forecast_embedded.py
#
# parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/analysis_embedded.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/analysis_embedded.py
#


##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in EnsembleStat_python_embedding.conf then a user-specific system configuration file::
#
#   master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf -c /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/air_quality/AOD  (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * ensemble_stat_aod_20160815_120000V_ecnt.txt
# * ensemble_stat_aod_20160815_120000V_ens.nc
# * ensemble_stat_aod_20160815_120000V_orank.nc
# * ensemble_stat_aod_20160815_120000V_phist.txt
# * ensemble_stat_aod_20160815_120000V_relp.txt
# * ensemble_stat_aod_20160815_120000V_rhist.txt
# * ensemble_stat_aod_20160815_120000V_ssvar.txt
# * ensemble_stat_aod_20160815_120000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#  `EnsembleStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleStatToolUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_,
#  `AirQualityandCompAppUseCase <https://dtcenter.github.io/METplus/search.html?q=AirQualityandCompAppUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/air_quality_and_comp-EnsembleStat_fcstICAP_obsMODIS_aod.png'
