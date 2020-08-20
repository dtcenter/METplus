"""
Grid-Stat: 6hr PQPF Probability Verification
==========================================================================

model_applications/precipitation/GridStat_fcstHRRR
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
#
# | **Init:** 2016-09-04_12Z
# | **Forecast lead:** 7
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
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStatConfig_PROB
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/GridStat/GridStat.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf
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
#  `GridStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#  `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#  `PCPCombineToolUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineToolUseCase&check_keywords=yes&area=default>`_,
#  `RegridDataPlaneToolUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`_,
#  `GRIBFileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIBFileUseCase&check_keywords=yes&area=default>`_,
#  `GRIB2FileUseCase <https://dtcenter.github.io/METplus/search.html?q=GRIB2FileUseCase&check_keywords=yes&area=default>`_,
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`_,
#  `NOAAWPCOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHMTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#  `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#  `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#  `ProbabilityVerificationUseCase  <https://dtcenter.github.io/METplus/search.html?q=ProbabilityVerificationUseCase&check_keywords=yes&area=default>`_

# sphinx_gallery_thumbnail_path = '_static/precipitation-GridStat_fcstHRRR-TLE_obsStgIV_GRIB.png'
