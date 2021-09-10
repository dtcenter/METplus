"""
Multi_Tool (MTD): Feature Relative by Lead (with lead groupings) 
==================================================================================================

model_applicaitons/medium_range/
MTD_SeriesAnalysis_fcstGFS
_obsGFS_FeatureRelative
_SeriesByLead.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# Demonstrate the capability in the Feature Relative use case but using output
# from the MET MODE Time Domain (MTD) tool.
#

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
#
#  * MODE Time Domain Forecast dataset: GFS
#  * Series-Analysis Forecast dataset: GFS
#  * MODE Time Domain Observation dataset: GFS Analysis
#  * Series-Analysis Observation dataset: GFS Analysis
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs MODE Time Domain and ExtractTiles wrappers to
# generate tiles of data centered on objects defined using MTD. The MET
# regrid-dataplane tool is used to regrid the data (GRIB1 or GRIB2 into netCDF).
# Next, a series analysis by lead time is performed on the results and plots
# (.ps and .png) are generated for all variable-level-stat combinations from
# the requested variables, levels, and requested statistics. The final results
# are aggregated into forecast hour groupings as specified by the start and end
# increment in the METplus configuration file, as well as labels to identify each
# forecast hour grouping.
#

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# MTD > RegridDataPlane (via ExtractTiles) > SeriesAnalysis
#
# This example loops by forecast/lead time (with begin, end, and increment as specified in the METplus
# MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf file). The following list
# of model initialization and forecast leads are processed in this use case:
#
# | **Init:** 20210712_00Z
# | **Forecast lead:** 6, 12, 18, 24, 30
# |
#
# | **Init:** 20210712_06Z
# | **Forecast lead:** 6, 12, 18, 24, 30
# |
#
# | **Init:** 20210712_12Z
# | **Forecast lead:** 6, 12, 18, 24, 30
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/medium_range/MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf

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
# **MTD_wrapped**
#
# .. note:: See the :ref:`MTD MET Configuration<mtd-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTD_wrapped
#
# **SeriesAnalysisConfig_wrapped**
#
# .. note:: See the :ref:`SeriesAnalysis MET Configuration<series-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf, then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/medium_range/MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of
#  NON-MET executables.  If the executable is in the user's path, METplus will find it from
#  the name. If the executable is not in the path, specify the full
#  path to the executable here (i.e. CONVERT = /usr/bin/convert)  The following executables are required
#  for performing series analysis use cases:
#
#  If the executables are in the path:
#
# * **CONVERT = convert**
#
# **NOTE:** All of these executable items must be located under the [exe] section.
#
#
# If the executables are not in the path, they need to be defined:
#
# * **CONVERT = /path/to/convert**
#
# **NOTE:** All of these executable items must be located under the [exe] section.
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
#   [exe]
#   CONVERT = /path/to/convert
#
# **NOTE:** The INPUT_BASE, OUTPUT_BASE, and MET_INSTALL_DIR must be located under the [dir] section, while the RM, CUT, TR, NCAP2, CONVERT, and NCDUMP must be located under the [exe] section.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in series_analysis_lead, relative to the **OUTPUT_BASE**, and in the following directories (relative to **OUTPUT_BASE**):
#
# * series_FHHH
# * series_animate
#
# | The *series_FHHH* subdirectory will contain files that have the following format:
#
#   ANLY_FILES_Fhhh_to_FHHH
#
#   FCST_ASCII_FILES_Fhhh_to_FHHH
#
#   series_<varname>_<level>_<stat>.png
#
#   series_<varname>_<level>_<stat>.ps
#
#   series_<varname>_<level>_<stat>.nc
#
#   Where:
#
#    **hhh** is the starting forecast hour/lead time in hours
#
#    **HHH** is the ending forecast hour/lead time in hours
#
#    **varname** is the variable of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **level**  is the level of interest, as specified in the METplus series_by_lead_all_fhrs config file
#
#    **stat** is the statistic of interest, as specified in the METplus series_by_lead_all_fhrs config file.
#
# | The series_animate directory contains the animations of the series analysis in .gif format for all variable, level, and statistics combinations:
#
#    series_animate_<varname>_<level>_<stat>.gif

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MediumRangeAppUseCase
#   * TCPairsToolUseCase
#   * SeriesByLeadUseCase
#   * MTDToolUseCase
#   * RegridDataPlaneToolUseCase
#   * SeriesAnalysisUseCase
#   * GRIB2FileUseCase
#   * FeatureRelativeUseCase
#   * SBUOrgUseCase
#   * DiagnosticsUseCase
#   * RuntimeFreqUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/medium_range-TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.png'
#
