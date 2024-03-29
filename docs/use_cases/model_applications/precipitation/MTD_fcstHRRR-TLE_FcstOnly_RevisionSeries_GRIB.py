"""
MTD: Build Revision Series to Evaluate Forecast Consistency 
===========================================================================

model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly
_RevisionSeries_GRIB.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the use of the MTD tool to evaluate an updating
# forecast field and evaluate the forecast consistency.  The use case looks
# for all forecasts valid at a given time and passes them into MTD.  Objects
# are identified and tracked through time via the tool.  The output can then
# be loaded into METviewer to compute the revision series and assess the
# consistency either of one case or many.  See other HRRR-TLE use cases
# for a description of the Time Lagged Ensemble (TLE) field.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRR-TLE forecasts in GRIB2
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MTD (MODE Time Domain) over multiple forecast leads.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# MTD
#
# This example loops by valid time. For each valid time
# it will run once, processing forecast leads 12 through 0. There is only one
# valid time in this example, so the following will be run:
#
# Run times:
#
# | **Valid:** 2018-03-13_0Z
# | **Forecast leads:** 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf

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
# 1) Passing in MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf
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
# Output for this use case will be found in model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * mtd_20180313_000000V_2d.txt
# * mtd_20180313_000000V_3d_single_simple.txt
# * mtd_20180313_000000V_obj.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MTDToolUseCase
#   * PrecipitationAppUseCase
#   * NOAAHMTOrgUseCase
#   * GRIB2FileUseCase
#   * NOAAWPCOrgUseCase
#   * NOAAHMTOrgUseCase
#   * NOAAHWTOrgUseCase
#   * ConvectionAllowingModelsAppUseCase
#   * RevisionSeriesUseCase
#   * DiagnosticsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.png'
#
