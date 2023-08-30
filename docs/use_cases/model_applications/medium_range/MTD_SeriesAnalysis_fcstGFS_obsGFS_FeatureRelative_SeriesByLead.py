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
# regrid_data_plane tool is used to regrid the data (GRIB1 or GRIB2 into netCDF).
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
# then it loads any configuration files passed to METplus via the command line.
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
# **MTDConfig_wrapped**
#
# .. note:: See the :ref:`MTD MET Configuration<mtd-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped
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
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#        /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/medium_range/MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  If the 'convert' executable is not in the user's path, specify the full
#  path to the executable here
#
# * **CONVERT = /usr/bin/convert**
#
# Example User Configuration File::
#
#   [config]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#   CONVERT = /path/to/convert
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
# Output for this use case will be found in series_analysis_lead directory relative to the **OUTPUT_BASE**, 
# and in the following directories (relative to **OUTPUT_BASE**):
#
# * series_FHHH
# * series_animate
#
# | The *series_FHHH* subdirectory will contain files that have the following format:
#
#   OBS_FILES_FHHH
#
#   FCST_FILES_FHHH
#
#   series_Fhhh_to_FHHH_<varname>_<level>_<stat>.png
#
#   series_Fhhh_to_FHHH_<varname>_<level>_<stat>.ps
#
#   series_Fhhh_to_FHHH_<varname>_<level>_<stat>.nc
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
# sphinx_gallery_thumbnail_path = '_static/medium_range-MTD_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.png'
#
