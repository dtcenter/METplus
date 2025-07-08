"""
PointStat: Verify UFS Soil Moisture and Temperature with ISMN Observations
==========================================================================

model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp.conf

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
# This use case examines soil moisture and temperature biases in the UFS global forecast system (GFS).
# The specific configuration is a GFSv17 pre-release version (HR1). Correct representation of land states 
# are important for many processes, such as prediction of convection, near surface sensible weather 
# (e.g. winds, humidity, temperature), and subsequent hydrological forecasting applications such as 
# snowpack evolution and runoff generation. Here we use the International Soil Moisture Network (ISMN) 
# soil moisture and temperature data to assess UFS forecast errors across CONUS for an example summer 
# 60 hour forecast. We plot spatial differences (forecast-observation) to diagnose regional variations 
# as well as a 2D probability density plot of forecast difference versus forecast value to assess the 
# frequency of conditional differences. These diagnostics are useful for process understanding and may 
# aid in land model development and forecast error improvement.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** Global Forecast System (GFS) version 17 prototype.
# Global 1-degree grid including soil moisture content and soil temperature.
#
# **Observation:** International Soil Moisture Network (ISMN) observations
# of soil moisture content and soil temperature.
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

##############################################################################
# METplus Components
# ------------------
#
# This use case uses ASCII2NC to process ISMN observations from their raw
# format and then calls PointStat to verify the forecast data using those
# observations. After PointStat, StatAnalysis is called to compute an aggregate
# mean error (ME, Bias) across all times and forecast leads. Then METplus UserScripts
# are used to create various graphics from the output.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2020-08-05 12:00
#
# **End time (INIT_END):** 2020-08-05 12:00
#
# **Increment between beginning and end times (INIT_INCREMENT):** 12 Hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 60
#
# Only a single time is used to demonstrate the workflow for this use case.
# For each time, ASCII2NC is used to convert the ISMN observations to NetCDF.
# Then PointStat is called to create matched forecast and observation pairs for each
# variable and level defined by the user. After PointStat, StatAnalysis is used to
# compute an aggregate mean error (ME, bias) for all forecast/observation pairs across
# all valid times and forecast leads. This bias value is used to create a plot of the ME
# at each ISMN site on a map, color-coded by the bias value. In addition, 2-D histogram
# plots are created showing the relationship between the forecast minus observation values and
# the forecast values.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: Ascii2NcConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# .. dropdown:: STATAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case uses two Python UserScripts to perform plotting of the output.
# These scripts are called via the METplus configuration file, and produce a map
# plot of the mean error (ME, bias) at each observation location from PointStat 
# for both variables analyzed, as well as a 2D histogram plotting the frequency of
# each forecast minus observation and forecast value combination.
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp/plot_point_stat_bias_map_ISMN.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp/plot_point_stat_bias_map_ISMN.py
#
# .. dropdown:: parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp/plot_point_stat_bias_2d_hist_ISMN.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp/plot_point_stat_bias_map_ISMN.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp.conf /path/to/user_system.conf
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
# Output for this use case will be found in 
# {OUTPUT_BASE}/model_applications/land_surface/PointStat_fcstUFS_obsISMN_SoilMoistureTemp 
# and will contain the following files::
#
#  * ascii2nc/2020080512_ismn.nc
#  * point_stat/point_stat_600000L_20200805_120000V_mpr.txt
#  * point_stat/point_stat_600000L_20200805_120000V.stat
#  * stat_analysis/2020080512_2020080512_OBS_SID_CNT.stat
#  * 20200805_120000_20200805_120000_SOILW_0-0.1_2D_hist.png
#  * 20200805_120000_20200805_120000_SOILW_0-0.1_ME_map.png
#  * 20200805_120000_20200805_120000_TSOIL_0-0.1_2D_hist.png
#  * 20200805_120000_20200805_120000_TSOIL_0-0.1_ME_map.png

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * ASCII2NCToolUseCase
#   * PointStatToolUseCase
#   * StatAnalysisToolUseCase
#   * UserScriptUseCase
#   * LandSurfaceAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/land_surface-PointStat_fcstUFS_obsISMN_SoilMoistureTemp.png'
