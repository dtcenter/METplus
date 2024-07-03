"""
Blocking Calculation: ERA Blocking Python Code and possibly RegridDataPlane and PcpCombine
==========================================================================================

model_applications/
s2s_mid_lat/
UserScript_obsERA_obsOnly_Blocking.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# Atmospheric blocking is associated with extreme weather events.  This use case computes
# atmospheric blocking events using the methodology in Miller & Wang (2019, 2022), which
# identifies blocsk from 500 mb height.  Various studies (Masato et al. 2013; Kitano and 
# Yamada 2016) have suggested that using 500 mb height produces a similar climatology as when 
# blocks are identified using potential temperature on a 2-PVU surface.
#
# The methodology in Miller & Wang (2019, 2022) first computes the Central Blocking Latitude 
# (CBL) or storm track.  Allowing for an offset north and south of the storm track, reversals 
# in geopotential height are identified as Instantaneously Blocked longitudes (IBLs).  These 
# IBLs are grouped when consective longitudes are blocked (GIBLs) and then blocks are identified 
# by applying thresholds to ensure the large-scale, quasi-stationary characteristics of blocking 
# anticyclones are met.
#
# This use case is a simplified version of the UserScript_fcstGFS_obs_ERA_Blocking use case.  While 
# that use case evaluates a model versus observation, this case shows how to run the blocking
# calculation on observations only, for simplicity.
#
#  * Miller, D. E., and Z. Wang, 2019a: Skillful seasonal prediction of Eurasian winter blocking and extreme temperature frequency. Geophys. Res. Lett., 46, 11 530–11 538, https://doi.org/10.1029/2019GL085035.
#  * Miller, D. E., and Z. Wang, 2022: Northern Hemisphere Winter Blocking: Differing Onset Mechanisms across regions. J. Atmos. Sci., 79, 1291-1309, https://doi.org/10.1175/JAS-D-21-0104.1.
#  * Masato, G., B. J. Hoskins, and T. J. Woollings, 2013: Winter and summer Northern Hemisphere blocking in CMIP5 models. J. Climate, 26, 7044–7059, https://doi.org/10.1175/JCLI-D-12-00466.1.
#  * Kitano, Y., and T. J. Yamada, 2016: Relationship between atmospheric blocking and cold day extremes in current and RCP8.5 future climate conditions over Japan and the surrounding area. Atmos. Sci. Lett., 17, 616–622, https://doi.org/10.1002/asl.711.
#

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: None
#  * Observation dataset: ERA Reanlaysis 500 mb height for DJF 2000 - 2017 for the blocking evaluation and 1979 - 2018 for the CBL calculation
#

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed::
#
# * numpy
# * netCDF4
# * datetime
# * bisect
# * scipy
#

##############################################################################
# METplus Components
# ------------------
#
# This use case calls UserScript once to run the driver which performs the blocking 
# calculation.  There are 4 optional pre-processing steps that are not run in the example 
# to save time and disk space.  These include RegridDataPlane to regrid the observations to 
# degree.  Then, there are 3 calls to PcpCombine.  These compute daily average 500 mb height,  
# a 5 day running mean and daily anomalies.  These omitted steps can be turned back on by using 
# the PROCESS_LIST that is commented out.
#
#PROCESS_LIST = RegridDataPlane(regrid_obs), PcpCombine(daily_mean_obs), PcpCombine(running_mean_obs), PcpCombine(anomaly_obs), UserScript(script_blocking)
#
# Settings for the optional pre-processing steps can be found in the respective sections of 
# the configuration, regrid_obs, daily_mean_obs, running_mean_obs, and anomaly_obs.  Data is not 
# provided in the tarball to run these steps, but the configurations are provided for reference 
# on how to set up these steps.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop.  It runs UserScript once for the blocking calculation.
# The optional pre-processing steps do loop by valid time with different timing settings 
#needed used for the different steps.
# 
# The UserScript runs the blocking calculation which performs multiple steps from METcalcpy
# or METplotpy.  These include computing CBLs (CBL), plotting CBLs (PLOTCBL), computing IBLs 
# (IBL), plotting IBL frequency (PLOTIBL), computing GIBLs (GIBL), computing blocks (CALCBLOCKS), 
# plotting the blocking frequency (PLOTBLOCKS).  This use case runs all steps although not all of 
# them are required to be run.  They must be run in the above order and control over which steps 
# to run is controlled in the [user_env_vars] section of the configuration and are formatted as 
# follows:
# 
# OBS_STEPS = CBL+PLOTCBL+IBL+PLOTIBL+GILB+CALCBLOCKS+PLOTBLOCKS
#
# The metcalcpy scripts accessed include the following:
# metcalcpy/contributed/blocking_weather_regime/Blocking.py, which runs the calculation steps, CBL, IBL, GIBL, and CALcBLOCKS.  See the METcalcpy `Blocking Calculation Script <https://github.com/dtcenter/METcalcpy/blob/develop/metcalcpy/contributed/blocking_weather_regime/Blocking.py>`_ for more information.
#
# metcalcpy/contributed/blocking_weather_regime/Blocking_WeatherRegime_util.py, which contains functions used by both the blocking anwd weather regime analysis, including the code for determining which steps the user wants to run, and reading the input files in the format required for the calculation.  See the METcalcpy `Utility script <https://github.com/dtcenter/METcalcpy/blob/develop/metcalcpy/contributed/blocking_weather_regime/Blocking_WeatherRegime_util.py>`_ for more information.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.py.
# The file UserScript_obsERA_obsOnly_Blocking.conf runs the python program, and the
# variables for all steps of the Blocking calculation are given in the [user_env_vars]
# section of the .conf file.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# This case does not use MET configuration files.
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding
#

##############################################################################
# Python Scripting
# ----------------
#
# This use case runs the blocking_driver.py python script located in the UserScript_obsERA_obsOnly_Blocking directory.  The steps this driver script runs are described in the METplus workflow section above.  There are many input variables to the driver script, which can be modified in the [user_env_vars] section of the UserScript_obsERA_obsOnly_Blocking.conf file.  A description of each of these variables is also provided with each variable in the .conf file.
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking/Blocking_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired:
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_obsERA_obsOnly_Blocking.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Warnings of missing files will also be output to the log file.  In this case, the warnings are a result of
# the 5 day running mean calculation, and should be present for 12/01, 12/02, 02/27, and 02/28 for each year
# the calculation runs.  Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in model_applications/s2s_mid_lat/Blocking (relative to **OUTPUT_BASE**).  
# There should be 3 different graphics output to the plot directory in the above location, but each will have png 
# and pdf versions to make for 6 output plots:
#
#  * ERA_CBL_avg.png
#  * ERA_CBL_avg.pdf
#  * ERA_IBL_Freq_DJF.png
#  * ERA_IBL_Freq_DJF.pdf
#  * obs_Block_Freq_DJF.png
#  * obs_Block_Freq_DJF.pdf
# 
# If the pre-processing steps are turned on, regridded data, daily averaged files, running mean files, 
# and anomaly files will also be output to Regrid, Daily,Rmean5d, and Anomaly in the ERA directory.
#

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
