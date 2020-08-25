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
#

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
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/MTD/MTD.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf
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
#     `MTDToolUseCase <https://dtcenter.github.io/METplus/search.html?q=MTDToolUseCase&check_keywords=yes&area=default>`_,
#     `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#     `NOAAHMTOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#     `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#     `NOAAWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_,
#     `NOAAHMTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#     `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#     `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#     `RevisionSeriesUseCase  <https://dtcenter.github.io/METplus/search.html?q=RevisionSeriesUseCase&check_keywords=yes&area=default>`_,
#     `DiagnosticsUseCase <https://dtcenter.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.png'
