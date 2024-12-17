"""
UserScript and StatAnalysis: Calculate and evaluate Blocking for the GFS and ERA
================================================================================

model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.py

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
# Atmospheric blocking is associated with extreme weather events.  This use case computes
# atmospheric blocking events using the methodology in Miller & Wang (2019, 2022), which
# identifies blocks from 500 mb height.  Various studies (Masato et al. 2013; Kitano and 
# Yamada 2016) have suggested that 500 mb height produces a similar blocking climatology as 
# results from potential temperature on a 2-PVU surface.
#
# The methodology in Miller & Wang (2019, 2022) first computes the Central Blocking Latitude 
# (CBL) or storm track.  Allowing for an offset north and south of the storm track, reversals 
# in geopotential height are then identified as Instantaneously Blocked longitudes (IBLs).  These 
# IBLs are grouped when consective longitudes are blocked (GIBLs) and then blocks are identified 
# by applying thresholds to ensure the large-scale, quasi-stationary characteristics of blocking 
# anticyclones are met.  The IBLs, GIBLs, and blocks are computed separately for the model and 
# observations, and contingency table statistics are computed to compare model performance at 
# identifying IBLs and blocks.  The original code for computing blocking came from Douglas Miller.
#
#  * Miller, D. E., and Z. Wang, 2019a: Skillful seasonal prediction of Eurasian winter blocking and extreme temperature frequency. Geophys. Res. Lett., 46, 11 530–11 538, https://doi.org/10.1029/2019GL085035.
#  * Miller, D. E., and Z. Wang, 2022: Northern Hemisphere Winter Blocking: Differing Onset Mechanisms across regions. J. Atmos. Sci., 79, 1291-1309, https://doi.org/10.1175/JAS-D-21-0104.1.
#  * Masato, G., B. J. Hoskins, and T. J. Woollings, 2013: Winter and summer Northern Hemisphere blocking in CMIP5 models. J. Climate, 26, 7044–7059, https://doi.org/10.1175/JCLI-D-12-00466.1.
#  * Kitano, Y., and T. J. Yamada, 2016: Relationship between atmospheric blocking and cold day extremes in current and RCP8.5 future climate conditions over Japan and the surrounding area. Atmos. Sci. Lett., 17, 616–622, https://doi.org/10.1002/asl.711.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.0.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS Forecast 500 mb height for DJF 2000 - 2017 
#
# **Observation:** ERA Reanlaysis 500 mb height for DJF 2000 - 2017 for the blocking evaluation and 1979 - 2017 for the CBL calculation
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
# This use case calls UserScript twice and StatAnalysis twice.  The first StatAnalysis
# run computes contingency table statistics on the IBLs, while the second computes contintency 
# table statistics on the computed blocks. There are 6 optional pre-processing steps, 2 calls to 
# RegridDataPlane and 4 calls to PCP-Combine.  Additionally, METcalcpy and METplotpy are 
# required to run this use case.  The METcalcpy scripts accessed include the following:
#
# * metcalcpy/contributed/blocking_weather_regime/Blocking.py
#
# * metcalcpy/contributed/blocking_weather_regime/Blocking_WeatherRegime_util.py
#
# * metcalcpy/util/write_mpr.py
#
# The METplopty scrips accessed include the following:
#
# * metplotpy/contributed/blocking_s2s/CBL_plot.py
#
# * metplotpy/contributed/blocking_s2s/plot_blocking.py

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 12-01-2000
#
# **End time (VALID_END):** 02-28-2017
#
# **Increment between beginning and end times (VALID_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 24H
#
# This use case does not loop, but the 2 UserScripts calls are run once for 
# all valid times of the forecast and observations.  The first UserScript creates a file list
# with the observed ERA data to use for the storm track climatology.  This is done separately 
# because it's a different (longer) time frame from the data used in the other steps of the blocking
# calculation.  The second UserScript runs the blocking driver which calls the code to perform the 
# blocking calculation.  The blocking calculation is divided up into steps, which the user can select 
# by setting STEPS_OBS and STEPS_FCST in the [user_env_vars] section of the configuration.  More 
# information on the steps and how the calculation proceeds is given in the User Scripting section 
# below.
#
# The two calls to StatAnalysis also don't loop but are run once for all valid times.  The first 
# StatAnalysis run computes contingency table statistics on the IBLs, while the second computes 
# contintency table statistics on the computed blocks.
#
# The 6 optional pre-processing steps loop by loop by valid time with different timing settings 
# needed used for the different steps.  These include 2 runs of RegridDataPlane to regrid both
# the model and observations to a 1 degree grid.  Then, there are 2 calls to PcpCombine.  These 
# compute daily average 500 mb height for the model and observations.  The next two calls to 
# PcpCombine compute a 5 day running mean and daily anomalies on the observations, which are used 
# to compute the storm track climatology.  These omitted steps can be turned back on by using the 
# PROCESS_LIST that is commented out:
#
# PROCESS_LIST = RegridDataPlane(regrid_fcst), RegridDataPlane(regrid_obs), PcpCombine(daily_mean_fcst), PcpCombine(daily_mean_obs), PcpCombine(running_mean_obs), PcpCombine(anomaly_obs), UserScript(create_cbl_filelist), UserScript(script_blocking), StatAnalysis(sanal_ibls), StatAnalysis(sanal_blocks)
#
# Settings for the optional pre-processing steps can be found in the respective sections of 
# the configuration, regrid_fcst, regrid_obs, daily_mean_fcst, daily_mean_obs, running_mean_obs, 
# and anomaly_obs.  Data is not provided in the tarball to run these steps, but the configurations 
# are provided for reference on how to set up these calculations.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, i.e
# parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.conf

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
# .. dropdown:: StatAnalysisConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case runs the blocking driver.  The blocking driver runs the user selected steps
# of the blocking calculation for both the forecast and observation.  These steps are specified 
# in FCST_STEPS and OBS_STEPS in the [user_env_vars] section fo the configuration file in the 
# following format:
#
#  | FCST_STEPS = CBL+IBL+PLOTIBL+GILB+CALCBLOCKS+PLOTBLOCKS
#  | OBS_STEPS = CBL+PLOTCBL+IBL+PLOTIBL+GILB+CALCBLOCKS+PLOTBLOCKS
#
# The possible steps are computing the CBLs or central blocking latitude (CBL), plotting CBLs 
# (PLOTCBL), computing instantaneously blocked longitudes (IBL), plotting IBL frequency (PLOTIBL), 
# computing grouped instantaneously blocked longitudes (GIBL), computing blocks (CALCBLOCKS), and
# plotting the blocking frequency (PLOTBLOCKS).  This use case runs all steps although not all of 
# them are required to be run.  The CBL, IBL, GIBL, and CALCBLOCKS steps must be run in order as the
# IBL step requires previously computed CBLs, and GIBLs requires previously computed IBLs.  Plotting
# also requires the associated step to be run (e.g. PLOTCBL requires CBL to be run first).  The 
# methodology used in these calculations is described in Miller & Wang (2019, 2022) listed in the 
# Scientific Objective section.
#
# There are many input variables that can be changed for the driver script and blocking calculation.  
# These can be changed and are described in the [user_env_vars] section of the configuration file.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking/Blocking_driver.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking/Blocking_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.conf /path/to/user_system.conf
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
# Warnings of missing files will also be output to the log file.  In this case, the warnings are a result of
# the 5 day running mean calculation.  They should alert the user about missing data fir 12/01, 12/02, 02/27,
# and 02/28 of each year the calculation runs.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in {OUTPUT_BASE}/model_applications/s2s_mid_lat/Blocking.  There should be 4 different 
# graphics output to the plot directory in the location above, but each will have png and pdf version to make 
# for 8 output plots:: 
#
#  * ERA_CBL_avg.png
#  * ERA_CBL_avg.pdf
#  * GFS_ERA_IBL_Freq_DJF.png
#  * GFS_ERA_IBL_Freq_DJF.pdf
#  * obs_Block_Freq.png
#  * obs_Block_Freq.pdf
#  * fcst_Block_Freq.png
#  * fcst_Block_Freq.pdf
# 
# There are numerous matched pair files output in two subdirectories of the mpr directory.  These contain
# output computed IBLs and blocks.  For the IBLs, one file is written for each day to the IBL subdirectory
# in the format below for 12-02-2000::
#
# * IBL_stat_GFS_240000L_20001202_000000V.stat
#
# For the blocks .stat files, one file is also written for each day to the Blocks subdirectory in the format
# below for 12-02-2000::
#
# * blocking_stat_GFS_240000L_20001202_000000V.stat
#
# There are also 2 files output from the StatAnalysis runs containing contingency table statistics:: 
#
#  * GFS_ERA_IBLS_240000L_CTS_CNT.stat
#  * GFS_ERA_Blocks_240000L_CTS.stat
#
# If the pre-processing steps are turned on, regridded data, daily averaged files, running mean files, 
# and anomaly files will also be output to Regrid, Daily,Rmean5d, and Anomaly directories in the ERA 
# directory and Regrid and Daily directories in the GFS directory. 

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * RegridDataPlaneToolUseCase
#   * PCPCombineToolUseCase
#   * StatAnalysisToolUseCase
#   * S2SAppUseCase
#   * S2SMidLatAppUseCase
#   * NetCDFFileUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mid_lat-UserScript_fcstGFS_obsERA_Blocking.png'
