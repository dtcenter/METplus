"""
PointStat: Hurricane Matthew I-WRF
==================================

model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf

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
# Perform verification of WRF data generated over Hurricane Matthew from 2016
# using MADIS RAOB and METAR observations.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** WRF, temperature and wind
#
# **Observation:** MADIS RAOB and METAR
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
# This use case calls 2 instances of MADIS2NC to convert the RAOB and METAR
# observations to NetCDF.
# Then 2 instances of PointStat are called to process surface and
# upper air fields.
# Next, UserScript is used to call a python script to plot the WRF data.
# Finally, another UserScript instance calls a METdataio script to reformat
# the PointStat output and a METplotpy script to produce a line plot.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2016-10-06 00Z
#
# **End time (INIT_END):** 2016-10-06 00Z
#
# **Increment between beginning and end times (INIT_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48
#
# The MADIS2NC instances process every forecast lead from 0-48.
# The RAOB MADIS2NC instance has missing data for a few of the leads,
# so a missing data threshold of 87.5% is set to prevent errors.
# The surface instance of PointStat allows a +/- 30 minute window for observations and
# includes files from the previous hour.
# The upper air instance of PointStat allows +/- 90 minute window for observations and
# includes files from +/- 2 hours around the valid time.


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line:
# parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf

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
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python Embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case calls files from METdataio and METcalcpy to generate a line
# plot of the point_stat output.
# It also calls a Python script to perform plotting of WRF data.
#
# .. dropdown:: parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew/plot_wrf.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew/plot_wrf.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf /path/to/user_system.conf
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
# Output for this use case will be found in {OUTPUT_BASE}
# and will contain the following files:
#
# * met_plot/cnt_reformatted.data
# * met_plot/line_T2_RMSE_BCMSE.png
# * point_stat/point_stat_surface_000000L_20161006_000000V.stat
# * point_stat/point_stat_surface_000000L_20161006_000000V_cnt.txt
# * point_stat/point_stat_surface_000000L_20161006_000000V_vcnt.txt
# * point_stat/point_stat_surface_030000L_20161006_030000V.stat
# * point_stat/point_stat_surface_030000L_20161006_030000V_cnt.txt
# * point_stat/point_stat_surface_030000L_20161006_030000V_vcnt.txt
# * point_stat/point_stat_surface_060000L_20161006_060000V.stat
# * point_stat/point_stat_surface_060000L_20161006_060000V_cnt.txt
# * point_stat/point_stat_surface_060000L_20161006_060000V_vcnt.txt
# * point_stat/point_stat_surface_090000L_20161006_090000V.stat
# * point_stat/point_stat_surface_090000L_20161006_090000V_cnt.txt
# * point_stat/point_stat_surface_090000L_20161006_090000V_vcnt.txt
# * point_stat/point_stat_surface_120000L_20161006_120000V.stat
# * point_stat/point_stat_surface_120000L_20161006_120000V_cnt.txt
# * point_stat/point_stat_surface_120000L_20161006_120000V_vcnt.txt
# * point_stat/point_stat_surface_150000L_20161006_150000V.stat
# * point_stat/point_stat_surface_150000L_20161006_150000V_cnt.txt
# * point_stat/point_stat_surface_150000L_20161006_150000V_vcnt.txt
# * point_stat/point_stat_surface_180000L_20161006_180000V.stat
# * point_stat/point_stat_surface_180000L_20161006_180000V_cnt.txt
# * point_stat/point_stat_surface_180000L_20161006_180000V_vcnt.txt
# * point_stat/point_stat_surface_210000L_20161006_210000V.stat
# * point_stat/point_stat_surface_210000L_20161006_210000V_cnt.txt
# * point_stat/point_stat_surface_210000L_20161006_210000V_vcnt.txt
# * point_stat/point_stat_surface_240000L_20161007_000000V.stat
# * point_stat/point_stat_surface_240000L_20161007_000000V_cnt.txt
# * point_stat/point_stat_surface_240000L_20161007_000000V_vcnt.txt
# * point_stat/point_stat_surface_270000L_20161007_030000V.stat
# * point_stat/point_stat_surface_270000L_20161007_030000V_cnt.txt
# * point_stat/point_stat_surface_270000L_20161007_030000V_vcnt.txt
# * point_stat/point_stat_surface_300000L_20161007_060000V.stat
# * point_stat/point_stat_surface_300000L_20161007_060000V_cnt.txt
# * point_stat/point_stat_surface_300000L_20161007_060000V_vcnt.txt
# * point_stat/point_stat_surface_330000L_20161007_090000V.stat
# * point_stat/point_stat_surface_330000L_20161007_090000V_cnt.txt
# * point_stat/point_stat_surface_330000L_20161007_090000V_vcnt.txt
# * point_stat/point_stat_surface_360000L_20161007_120000V.stat
# * point_stat/point_stat_surface_360000L_20161007_120000V_cnt.txt
# * point_stat/point_stat_surface_360000L_20161007_120000V_vcnt.txt
# * point_stat/point_stat_surface_390000L_20161007_150000V.stat
# * point_stat/point_stat_surface_390000L_20161007_150000V_cnt.txt
# * point_stat/point_stat_surface_390000L_20161007_150000V_vcnt.txt
# * point_stat/point_stat_surface_420000L_20161007_180000V.stat
# * point_stat/point_stat_surface_420000L_20161007_180000V_cnt.txt
# * point_stat/point_stat_surface_420000L_20161007_180000V_vcnt.txt
# * point_stat/point_stat_surface_450000L_20161007_210000V.stat
# * point_stat/point_stat_surface_450000L_20161007_210000V_cnt.txt
# * point_stat/point_stat_surface_450000L_20161007_210000V_vcnt.txt
# * point_stat/point_stat_surface_480000L_20161008_000000V.stat
# * point_stat/point_stat_surface_480000L_20161008_000000V_cnt.txt
# * point_stat/point_stat_surface_480000L_20161008_000000V_vcnt.txt
# * point_stat/point_stat_upper_air_000000L_20161006_000000V.stat
# * point_stat/point_stat_upper_air_000000L_20161006_000000V_cnt.txt
# * point_stat/point_stat_upper_air_000000L_20161006_000000V_vcnt.txt
# * point_stat/point_stat_upper_air_030000L_20161006_030000V.stat
# * point_stat/point_stat_upper_air_030000L_20161006_030000V_cnt.txt
# * point_stat/point_stat_upper_air_030000L_20161006_030000V_vcnt.txt
# * point_stat/point_stat_upper_air_060000L_20161006_060000V.stat
# * point_stat/point_stat_upper_air_060000L_20161006_060000V_cnt.txt
# * point_stat/point_stat_upper_air_060000L_20161006_060000V_vcnt.txt
# * point_stat/point_stat_upper_air_090000L_20161006_090000V.stat
# * point_stat/point_stat_upper_air_090000L_20161006_090000V_cnt.txt
# * point_stat/point_stat_upper_air_090000L_20161006_090000V_vcnt.txt
# * point_stat/point_stat_upper_air_120000L_20161006_120000V.stat
# * point_stat/point_stat_upper_air_120000L_20161006_120000V_cnt.txt
# * point_stat/point_stat_upper_air_120000L_20161006_120000V_vcnt.txt
# * point_stat/point_stat_upper_air_150000L_20161006_150000V.stat
# * point_stat/point_stat_upper_air_150000L_20161006_150000V_cnt.txt
# * point_stat/point_stat_upper_air_150000L_20161006_150000V_vcnt.txt
# * point_stat/point_stat_upper_air_180000L_20161006_180000V.stat
# * point_stat/point_stat_upper_air_180000L_20161006_180000V_cnt.txt
# * point_stat/point_stat_upper_air_180000L_20161006_180000V_vcnt.txt
# * point_stat/point_stat_upper_air_210000L_20161006_210000V.stat
# * point_stat/point_stat_upper_air_210000L_20161006_210000V_cnt.txt
# * point_stat/point_stat_upper_air_210000L_20161006_210000V_vcnt.txt
# * point_stat/point_stat_upper_air_240000L_20161007_000000V.stat
# * point_stat/point_stat_upper_air_240000L_20161007_000000V_cnt.txt
# * point_stat/point_stat_upper_air_240000L_20161007_000000V_vcnt.txt
# * point_stat/point_stat_upper_air_270000L_20161007_030000V.stat
# * point_stat/point_stat_upper_air_270000L_20161007_030000V_cnt.txt
# * point_stat/point_stat_upper_air_270000L_20161007_030000V_vcnt.txt
# * point_stat/point_stat_upper_air_300000L_20161007_060000V.stat
# * point_stat/point_stat_upper_air_300000L_20161007_060000V_cnt.txt
# * point_stat/point_stat_upper_air_300000L_20161007_060000V_vcnt.txt
# * point_stat/point_stat_upper_air_330000L_20161007_090000V.stat
# * point_stat/point_stat_upper_air_330000L_20161007_090000V_cnt.txt
# * point_stat/point_stat_upper_air_330000L_20161007_090000V_vcnt.txt
# * point_stat/point_stat_upper_air_360000L_20161007_120000V.stat
# * point_stat/point_stat_upper_air_360000L_20161007_120000V_cnt.txt
# * point_stat/point_stat_upper_air_360000L_20161007_120000V_vcnt.txt
# * point_stat/point_stat_upper_air_390000L_20161007_150000V.stat
# * point_stat/point_stat_upper_air_390000L_20161007_150000V_cnt.txt
# * point_stat/point_stat_upper_air_390000L_20161007_150000V_vcnt.txt
# * point_stat/point_stat_upper_air_420000L_20161007_180000V.stat
# * point_stat/point_stat_upper_air_420000L_20161007_180000V_cnt.txt
# * point_stat/point_stat_upper_air_420000L_20161007_180000V_vcnt.txt
# * point_stat/point_stat_upper_air_450000L_20161007_210000V.stat
# * point_stat/point_stat_upper_air_450000L_20161007_210000V_cnt.txt
# * point_stat/point_stat_upper_air_450000L_20161007_210000V_vcnt.txt
# * point_stat/point_stat_upper_air_480000L_20161008_000000V.stat
# * point_stat/point_stat_upper_air_480000L_20161008_000000V_cnt.txt
# * point_stat/point_stat_upper_air_480000L_20161008_000000V_vcnt.txt
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RAIN+barbs_20161008_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_REFL+barbs_20161008_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_RH2+barbs_20161008_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_SLP+barbs_20161008_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_T2+barbs_20161008_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_TERRAIN.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161006_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_0000.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_0300.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_0600.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_0900.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_1200.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_1500.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_1800.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161007_2100.png
# * wrf_plot/20161006_00/plots/map_wrf_d01_WS10+barbs_20161008_0000.png
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCandExtraTCAppUseCase
#   * PointStatToolUseCase
#   * METplotpyUseCase
#   * UserScriptUseCase
#   * WRFFileUseCase
#   * MADIS2NCToolUseCase
#   * GRIB2FileUseCase
#   * MADISFileUseCase
#
# Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-PointStat_fcstWRF_obsMADIS_hurricane_matthew.png'
