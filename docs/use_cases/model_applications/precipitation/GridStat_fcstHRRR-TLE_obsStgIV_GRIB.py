"""
Grid-Stat: 6hr PQPF Probability Verification
==========================================================================

model_applications/precipitation/GridStat_fcstHRRR-TLE
_obsStgIV_GRIB.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case demonstrates the evaluation of a probabilistic field.  The
# HRRR-Time Lag Ensemble (TLE) used in this example was used to demonstrate
# prototype ensemble post-processing techniques. A time-lagged ensemble can
# provide higher temporal resolution and be used to compute several different
# accumulation amounts based on
# what data is available for each run time. 6 hour and 1 hour observation data
# is available at 6Z, so the 6 hour accumulation data is used. However, at 7Z
# only a 1 hour accumulation field is available, so it uses the 1 hour field,
# then steps back in time trying to build a 6 hour accumulation with earlier
# data. METplus is configured to only allow 1 hour or 6 hour accumulations in
# the input files, so a set of six 1 hour accumulation fields are combined to
# create a 6 hour accumulation field. The result is compared to the 6 hour
# forecast data.
#

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
# 
#  * Forecast dataset: HRRR-TLE probabilistic forecasts in GRIB2
#  * Observation dataset: Stage IV GRIB 1 and 6 hour precipitation accumulation
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the observation data to build a 6
# hour precipitation accumulation from 1 hour files or a single 6 hour file.
# Then the observation data is regridded to the model grid using the RegridDataPlane. Finally, the
# observation files are compared to the forecast data using GridStat.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# PCPCombine (observation) > RegridDataPlane (observation) > GridStat
#
# This example loops by initialization time. For each initialization time
# it will process forecast leads 6 and 7. There is only one
# initialization time in this example, so the following will be run:
#
# Run times:
#
# | **Init:** 2016-09-04_12Z
# | **Forecast lead:** 6
# |
# | **Init:** 2016-09-04_12Z
# | **Forecast lead:** 7
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf

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
# .. note:: See the :ref:`GridStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf
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
# Output for this use case will be found in model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB/grid_stat/201609041200 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_180000V_pct.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_180000V_pjc.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_180000V_prc.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_180000V_pstd.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_180000V.stat
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_190000V_pct.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_190000V_pjc.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_190000V_prc.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_060000L_20160904_190000V_pstd.txt
# * grid_stat_PROB_PHPT_APCP_vs_STAGE4_GRIB_APCP_A06_070000L_20160904_190000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PrecipitationAppUseCase
#   * PCPCombineToolUseCase
#   * RegridDataPlaneToolUseCase
#   * GRIBFileUseCase
#   * GRIB2FileUseCase
#   * NetCDFFileUseCase
#   * NOAAWPCOrgUseCase
#   * NOAAHMTOrgUseCase
#   * NOAAHWTOrgUseCase
#   * ConvectionAllowingModelsAppUseCase
#   * ProbabilityVerificationUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-GridStat_fcstHRRR-TLE_obsStgIV_GRIB.png'
#
