"""
MTD: 6hr QPF Use Case
==================================

model_applications/precipitation/MTD_fcstHRRR-TLE
_obsMRMS.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the evaluation of an ensemble mean field from a
# prototype ensemble post-processing technique for time-lagged ensembles
# (HRRR-TLE). MTD is used to provide useful object attributes and diagnostics on
# aggregated over a time series. This non-traditional
# approach provides alternative information and diagnostics to inform model development.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRR-TLE forecasts in GRIB2
#  * Observation dataset: Multi Radar Multi Sensor (MRMS)
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MTD (MODE Time Domain) over multiple forecast leads and 
# compares them to the observational data set.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# MTD
#
# This example loops by valid time. For each valid time
# it will run once, processing forecast leads 1, 2, and 3. There is only one
# valid time in this example, so the following will be run:
#
# Run times:
#
# | **Valid:** 2017-05-10_03Z
# | **Forecast leads:** 1, 2, 3
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`MTD MET Configuration<mtd-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_fcstHRRR-TLE_obsMRMS.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_fcstHRRR-TLE_obsMRMS.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
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
# Output for this use case will be found in model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * mtd_20170510_040000V_2d.txt
# * mtd_20170510_040000V_3d_single_simple.txt
# * mtd_20170510_040000V_obj.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MTDToolUseCase
#   * PrecipitationAppUseCase
#   * GRIB2FileUseCase
#   * NetCDFFileUseCase
#   * NOAAWPCOrgUseCase
#   * NOAAHMTOrgUseCase
#   * NOAAHWTOrgUseCase
#   * ConvectionAllowingModelsAppUseCase
#   * ProbabilityVerificationUseCase
#   * DiagnosticsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-MTD_fcstHRRR-TLE_obsMRMS.png'
#
