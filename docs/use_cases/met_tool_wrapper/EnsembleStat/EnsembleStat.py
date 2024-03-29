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
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
# | **Data Source:** Unknown
# |

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
# |

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
# .. note:: See the :ref:`EnsembleStat MET Configuration<ens-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in EnsembleStat.conf then a user-specific system configuration file::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf /path/to/user_system.conf
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
#
#   * EnsembleStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * EnsembleAppUseCase
#   * ProbabilityGenerationAppUseCase
#   * GRIBFileUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-EnsembleStat.png'
#
