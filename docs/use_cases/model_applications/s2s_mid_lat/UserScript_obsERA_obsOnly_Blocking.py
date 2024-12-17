"""
UserScript: Calculate Blocking for the ERA and possibly RegridDataPlane and PcpCombine
======================================================================================

model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.py

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
# in geopotential height are then identified as Instantaneously Blocked Longitudes (IBLs).  These 
# IBLs are grouped when consective longitudes are blocked (GIBLs) and then blocks are identified 
# by applying thresholds to ensure the large-scale, quasi-stationary characteristics of blocking 
# anticyclones are met.
#
# This use case is a simplified version of the UserScript_fcstGFS_obs_ERA_Blocking use case.  While 
# that use case evaluates blocking for both the model and observations, this case shows how to run 
# the blocking calculation on observations only.  The setup is simpler and requires fewer MET runs 
# than the UserScript_fcstGFS_obs_ERA_Blocking use case.  The original code for computing blocking 
# came from Douglas Miller.
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
# **Forecast dataset:** None.
#
# **Observation dataset:** ERA Reanlaysis 500 mb height for DJF 1979 - 2017
#
# **Climatology:** None.
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
# This use case calls UserScript once.  There are 4 optional pre-processing steps, 
# RegridDataPlane and 3 calls to PcpCombine.  METcalcpy and METplotpy are also 
# required to run this use case.  The METcalcpy scripts accessed include the 
# following:
#
# * metcalcpy/contributed/blocking_weather_regime/Blocking.py
#
# * metcalcpy/contributed/blocking_weather_regime/Blocking_WeatherRegime_util.py
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
# **Beginning time (VALID_BEG):** 12-01-1979
#
# **End time (VALID_END):** 02-28-2017
#
# **Increment between beginning and end times (VALID_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# This use case does not loop.  It runs UserScript once over the entire time period.  The 
# UserScript runs the blocking driver script which performs the blocking calculation.  This
# calculation is divided up into steps, which the user can select by setting STEPS_OBS in 
# the [user_env_vars] section of the configuration.  More information on the steps and 
# how the calculation proceeds is given in the User Scripting section below.
#
# The four optional pre-processings steps loop by valid time with different timing settings 
# needed used for the different steps.  These steps are turned off due to data size and processing 
# time.  The first optional step calls Regrid-Data-Plane to regrid the data to a 1 degree 
# latitude/longitude grid.  The second calls PCP-Combine to compute daily means of 500 mb height. 
# The third calls PCP-Combine to compute a 5 day running mean, while the last uses PCP-Combine
# to compute anomalies by subtracting the 5 day running mean from the daily mean.  These omitted steps 
# can be turned on by using the PROCESS_LIST that is commented out:
#
# PROCESS_LIST = RegridDataPlane(regrid_obs), PcpCombine(daily_mean_obs), PcpCombine(running_mean_obs), PcpCombine(anomaly_obs), UserScript(script_blocking)
#
# Settings for the optional pre-processing steps can be found in the respective sections of 
# the configuration, regrid_obs, daily_mean_obs, running_mean_obs, and anomaly_obs.  Data is not 
# provided in the tarball to run these steps, but the configurations are provided as an example 
# of how to set up these steps.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line, i.e
# parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.conf

#############################################################################
# MET Configuration
# ---------------------
#
# This case does not use MET configuration files.

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding

##############################################################################
# User Scripting
# --------------
#
# This use case runs the blocking driver.  The blocking driver runs the user selected steps
# of the blocking calculation.  These steps are specified in OBS_STEPS in the [user_env_vars]
# section fo the configuration file in the following format:
#
#  | OBS_STEPS = CBL+PLOTCBL+IBL+PLOTIBL+GILB+CALCBLOCKS+PLOTBLOCKS
#
# The possible steps are computing the CBLs or central blocking latitude (CBL), plotting CBLs 
# (PLOTCBL), computing Instantaneously Blocked Longitudes (IBL), plotting IBL frequency (PLOTIBL), 
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
# .. dropdown:: parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking/Blocking_driver.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking/Blocking_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.conf /path/to/user_system.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in {OUTPUT_BASE}/model_applications/s2s_mid_lat/Blocking.  There should be 
# 3 different graphics output to the plot directory in the above location.  Each will have png and pdf 
# versions to make for 6 output plots::
#
#  * ERA_CBL_avg.png
#  * ERA_CBL_avg.pdf
#  * ERA_IBL_Freq_DJF.png
#  * ERA_IBL_Freq_DJF.pdf
#  * obs_Block_Freq_DJF.png
#  * obs_Block_Freq_DJF.pdf
# 
# If the pre-processing steps are turned on, regridded data, daily averaged files, running mean files, 
# and anomaly files will also be output to Regrid, Daily,Rmean5d, and Anomaly directories in the 
# ERA directory.

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
# sphinx_gallery_thumbnail_path = '_static/s2s_mid_lat-UserScript_obsERA_obsOnly_Blocking.png'
