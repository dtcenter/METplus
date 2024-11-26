"""
Grid-Stat: 6hr QPF in GEMPAK format
===================================

model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf

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
# Evaluate the skill of a high resolution multi-model ensemble mean
# at predicting 6 hour precipitation accumulation using the NCEP Stage IV
# gauge corrected analysis.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** HREF mean forecasts in Gempak
#
# **Observation:** Stage IV GRIB 6 hour precipitation accumulation
#
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

# Sources of data (links, contacts, etc...)

##############################################################################
#External Dependencies
#---------------------
#
# GempakToCF.jar
#
# GempakToCF is an external tool that utilizes the Unidata NetCDF-Java package. The jar file that can be used to run the utility is available here: https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
#
#To enable Gempak support, you must set [exe] GEMPAKTOCF_JAR in your user METplus configuration file:
#
# [exe] GEMPAKTOCF_JAR = /path/to/GempakToCF.jar
#
# See the GempakToCF use case for more information:
#
# parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.conf
#
# More information on the package used to create the file is here: https://www.unidata.ucar.edu/software/netcdf-java
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs PCPCombine on the forecast data to build a 6
# hour precipitation accumulation from 1 hour files or a single 6 hour file.
# Then the observation data is regridded to the model grid using the RegridDataPlane. Finally, the
# observation files are compared to the forecast data using GridStat.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2017050912
#
# **End time (INIT_END):** 2017050912
#
# **Increment between beginning and end times (INIT_INCREMENT):** 43200
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 18
#
# The following tools are used for each run time:
#
# PCPCombine (observation) > RegridDataPlane (observation) > GridStat
#
# This example loops by initialization time.
# There is only one initalization time in this example so the following will be run:
#
# Run times:
#
# | **Init:** 2017-05-09_12Z
# | **Forecast lead:** 18

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf
#

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
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak/GridStat/201705091200 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * grid_stat_000000L_20170510_060000V_eclv.txt
# * grid_stat_000000L_20170510_060000V_grad.txt
# * grid_stat_000000L_20170510_060000V.stat
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
#   * GEMPAKFileUseCase
#   * NetCDFFileUseCase
#   * NOAAWPCOrgUseCase
#   * NOAAHMTOrgUseCase
#   * NOAAHWTOrgUseCase
#   * ConvectionAllowingModelsAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-GridStat_fcstHREFmean_obsStgIV_Gempak.png'
#
