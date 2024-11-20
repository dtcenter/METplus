"""
Point-Stat: Investigating Preciptitation Types
==============================================

model_application/precipitation/PointStat_fcstMULTI_obsMETAR_PtypeComparisons.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# During a storm that produces mulitiple precipitation types, the validation
# process becomes critical to investigating how well a model does during these
# situations. Using METplus' PointStat tool in this use case creates an opportunity
# to compare three separate model outputs for a multi-precipitation type storm
# across several valid times and create statistical output that can help modelers
# fine-tune curent numerical models to perform better in this forecast situation.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: operational GFS, GFSv16, NAM
#  * Observation dataset: METARs (via NAM prepbufr reanalysis)
#

###############################################################################
# METplus Components
# ------------------
#
# This use case runs PB2NC on each NAM prepbufr file, extracts the METAR data within a 30-minute window
# of the valid time, then runs Point-Stat on the model forecasts, comparing each valid time 
# to the newly created netCDFs.
# 

###############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# PB2NC, PointStat
#
# This example loops by initialization time. For each initialization time
# it will process the listed lead hours (12 hour steps from 12 to 84 hours)
#
# Run times:
#
# | **Init:** 2021-02-15_12Z
# | **Forecast leads:** 12, 24, 36, 48, 60, 72, 84 hour
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/precipitation/PointStat_fcstMULTI_obsMETAR_PtypeComparisons.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/PointStat_fcstMULTI_obsMETAR_PtypeComparisons.conf

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
# **PB2NCConfig_wrapped**
#
# .. note:: See the :ref:`PB2NC MET Configuration<pb2nc-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PB2NCConfig_wrapped
#
# **PointStatConfig_wrapped**
#
# .. note:: See the :ref:`PointStat MET Configuration<point-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/PointStat_fcstMULTI_obsMETAR_PtypeComparisons.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/precipitation (relative to **OUTPUT_BASE**)
# The following PB2NC output files will be created:
#
# * nam.obsfile_sfc_prwe.02[dd]2021_[hh].nc
# 
# Where [dd] and [hh] corespond to each valid time run (total of 7 files).
#
# The following PointStat output files will also be created in model_applications/precipitation (relative to **OUTPUT_BASE**):
#
# * point_stat_[model]_[lead]0000L_[valid_YYMMDD_time]_[valid_HH_time].stat
#
# Where [model] is gfs, gfsx (for gfsv16), or nam, and valid times correspond to the 7 valid times being processed (total of 21 files).


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * PB2NCToolUseCase
#   * PrecipitationAppUseCase
#   * GRIB2FileUseCase
#   * prepBUFRFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-PointStat_fcstMULTI_obsMETAR_PtypeComparisons.png'
