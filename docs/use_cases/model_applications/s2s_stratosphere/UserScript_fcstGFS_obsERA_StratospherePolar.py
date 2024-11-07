"""
Bias Plot on Polar Cap Temperature and Polar Vortex U: UserScript, Stat-Analysis
================================================================================

model_applications/
s2s_stratosphere/
UserScript_fcstGFS_obsERA_StratospherePolar.py

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
# Many common modes of variability in the troposphere have stratospheric teloconnection 
# pathways. Thus, the stratosphere can be a source of predictability for surface weather.
#
# This use case calls functions in METcalcpy to create polar cap temperature 
# and polar vortex wind.  It then runs Stat-Analysis on the output zonal means 
# and creates a contour plot of bias in lead time and pressure level.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS Forecast U and T at multiple pressure levels
#
# **Observation:** ERA Reanlaysis U and T at multiple pressure levels
#
# **Climatology:** None
#
# **Location:** Data for this use case is not contained in the sample data tar files due to 
# its size. Rather, it is stored as additional data in a separate tar file, named 
# additional_data_UserScript_fcstGFS_obsERA_StratosphereQBO.tar.gz and can be
# downloaded at https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/v6.0/.

##############################################################################
# METplus Components
# ------------------
#
# This use case runs UserScript twice and Stat-Analysis once.  The UserScripts compute
# polar cap temperature and polar vortex wind and create plots.  METcalcpy, METplotpy,
# and METdataio are needed for this use case. The metcalcpy scripts accessed include 
# the following:
#
# * metcalcpy/pre_processing/directional_means.py
# 
# * metcalcpy/util/write_mpr.py
# 
# The METplotpy scripts accessed include the following:
#
# * metplotpy/contributed/stratosphere_diagnostics/stratosphere_plots.py
# 
# The METdataio scripts accessed include the following:
#
# * METreadnc/util/read_netcdf.py
 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2018-02-01
#
# **End time (VALID_END):** 2018-02-28
#
# **Increment between beginning and end times (VALID_INCREMENT):** 30 days
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0 - 384h at 24h intervals
#
# This use case loops over lead times for the first UserScript and Stat-Analysis,
# and the second UserScript runs once over the entire time period.  The first UserScript
# runs polar_t_u_driver.py which computes polar cap temperature and polar vortex wind
# and outputs that data to .stat files in MET's matched pair format.  Then, Stat-Analysis
# is run to compute bias and RMSE on the polar cap temperature and polar vortex wind.  
# Finally, the second UserScript runs the bias_rmse_plot_driver.py which creates plots
# of bias and RMSE over lead time and pressure level.
#
# METcalcpy 3.0.0 or higher, METplotpy 3.0.0 or higher, and METdataio 2.1 or higher are needed 
# for this use case

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf

#############################################################################
# MET Configuration
# ---------------------
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
# .. dropdown:: STATAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding

##############################################################################
# User Scripting
# --------------
#
# There are two python scripts in the is use case.  The first, polar_t_u_driver.py reads in netCDF files for the
# forecast and observations and computes zonal means for temperature and wind.  Then, polar cap temperature is 
# computed by taking the meridional mean between 60 and 90 latitude, while polar vortex u is computed by taking
# the meridional mean between 50 and 80 latitude.  This data is written to output files in MET's matched pair
# format.
#
# The second python script, bias_rmse_plot_driver reads in the output of Stat-Analysis and creates plots of bias
# and RMSE for polar cap temperature and polar vortex u.  Variables input to this script are given in the 
# [user_env_vars] section of the configuration file. 
#
# .. dropdown:: parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar/polar_t_u_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar/polar_t_u_driver.py
#
# .. dropdown:: parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar/bias_rmse_plot_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar/bias_rmse_plot_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar
# The output includes matched pair files, one for each lead time and valid time in mpr directory.
# The output files have the following format::
#
# * polar_cap_T_stat_GFS_HH0000L_YYYYMMDD_000000V.stat
# * polar_cap_T_stat_GFS_HHH0000L_YYYYMMDD_000000V.stat
#
# Additionally, CNT statistics will be output to the StatAnalysis directory with one file for each lead
# time and variable.  The files have the following format::
#
# * GFS_ERA_20180201_20180228_HH0000L_PolarCapT_CNT.stat
# * GFS_ERA_20180201_20180228_HH0000L_PolarVortexU_CNT.stat
#
# Four plot are also output to the plots directory::
# 
# * ME_2018_02_polar_cap_T.png
# * ME_2018_02_polar_vortex_U.png
# * RMSE_2018_02_polar_cap_T.png
# * RMSE_2018_02_polar_vortex_U.png

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * S2SAppUseCase
#   * S2SStratosphereAppUseCase
#   * StatAnalysisUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_stratosphere-UserScript_fcstGFS_obsERA_StratospherePolar.png'
