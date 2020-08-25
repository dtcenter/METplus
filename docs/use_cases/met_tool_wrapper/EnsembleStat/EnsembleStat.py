"""
EnsembleStat: Basic Use Case
=============================

met_tool_wrapper/EnsembleStat/EnsembleStat.conf

"""

###########################################
# Scientific Objective
# --------------------
#
# To provide useful statistical information on the relationship between
# observation data (in both grid and point formats) to an ensemble forecast.
# These values can be used to help correct ensemble member deviations from observed values.


##############################################################################
# Datasets
# --------
#
#
# | **Forecast:** WRF ARW 24 hour precipitation accumulation
# |     ...met_test/data/sample_fcst/2009123112/
# |         arw-fer-gep1/d01_2009123112_02400.grib
# |         arw-fer-gep5/d01_2009123112_02400.grib
# |         arw-sch-gep2/d01_2009123112_02400.grib
# |         arw-sch-gep6/d01_2009123112_02400.grib
# |         arw-tom-gep3/d01_2009123112_02400.grib
# |         arw-tom-gep7/d01_2009123112_02400.grib
# | **Gridded Observation:** ST4 24 hour precipitation accumulation
# |         met_test/data/sample_obs/ST4/sample_obs/ST4/ST4.2010010112.24h
# | **Point Observation:** 
# |         met_test/out/ascii2nc/precip24_2010010112.nc 
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus EnsembleStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool EnsembleStat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# EnsembleStat is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2009-12-31_12Z
# | **Forecast lead:** 24 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf
#

##############################################################################
# MET Configuration
# -----------------
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
# * **${REGRID_TO_GRID}** - Grid to remap data. Corresponds to ENSEMBLE_STAT_REGRID_TO_GRID in the METplus configuration file.
# * **${ENS_THRESH}** - Threshold for ratio of valid files to expected files to allow application to run. Corresponds to ENSEMBLE_STAT_ENS_THRESH in the METplus configuration file.
# * **${ENS_FIELD}** - Formatted ensemble product fields information. Generated from ENS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${FCST_FIELD}** - Formatted forecast field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_FIELD}** - Formatted observation field information. Generated from [OBS/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.
# * **${OBS_WINDOW_BEGIN}** - Corresponds to OBS_WINDOW_BEGIN or OBS_ENSEMBLE_STAT_WINDOW_BEGIN in the METplus configuration file.
# * **${OBS_WINDOW_END}** - Corresponds to OBS_WINDOW_END or OBS_ENSEMBLE_STAT_WINDOW_END in the METplus configuration file.
# * **${CLIMO_MEAN_FILE}** - Optional path to climatology mean file. Corresponds to ENSEMBLE_STAT_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${CLIMO_STDEV_FILE}** - Optional path to climatology standard deviation file. Corresponds to ENSEMBLE_STAT_CLIMO_STDEV_INPUT_[DIR/TEMPLATE] in the METplus configuration file.
# * **${OUTPUT_PREFIX}** - String to prepend to the output filenames. Corresponds to ENSEMBLE_STAT_OUTPUT_PREFIX in the METplus configuration file.
#

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in EnsembleStat.conf then a user-specific system configuration file::
#
#   master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf -c /path/to/user_system.conf
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
# Output for this use case will be found in ensemble/200912311200/ensemble_stat  (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * ensemble_stat_20100101_120000V.stat
# * ensemble_stat_20100101_120000V_ecnt.txt
# * ensemble_stat_20100101_120000V_rhist.txt
# * ensemble_stat_20100101_120000V_phist.txt
# * ensemble_stat_20100101_120000V_orank.txt
# * ensemble_stat_20100101_120000V_ssvar.txt
# * ensemble_stat_20100101_120000V_relp.txt
# * ensemble_stat_20100101_120000V_ens.nc
# * ensemble_stat_20100101_120000V_orank.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#  `EnsembleStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleStatToolUseCase&check_keywords=yes&area=default>`_,
#  `PythonEmbeddingFileUseCase <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_,
#  `EnsembleAppUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleAppUseCase&check_keywords=yes&area=default>`_,
#  `ProbabilityGenerationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ProbabilityGenerationAppUseCase&check_keywords=yes&area=default>`_
#  `GRIBFileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIBFileUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-EnsembleStat.png'
