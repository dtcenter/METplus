"""
UserScript: Make ERA RMM plot from calculated MJO indices
=========================================================

model_applications/
s2s_mjo/
UserScript_obsERA_obsOnly_RMM.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# The Madden-Julian Oscillation (MJO) is the largest element of intraseasonal variability in the 
# tropics and is characterized by eastward moving regions of enhanced and suppressed rainfall.  These
# phases are typically grouped into numbers 1 - 8 based on the geographic location of the enhanced and 
# suppressed rainfall.  The MJO affects global weather including summer monsoons, tropical cyclone 
# development, and sudden stratospheric warming events, and has teloconnections to mid latitude weather
# systems.  
# 
# This use case uses anomalies of outgoing longwave radiation (OLR), 850 hPa wind (U850), and 200 hPa 
# wind (U200) to compute the Real-time Multivariate MJO Index (RMM).  In contrast to OMI, which is a 
# convective index of MJO, RMM is a dynamical index.  The code for computing RMM comes from Maria
# Gehne at PSL.
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset:  None
#  * Observation dataset: ERA Reanlaysis Outgoing Longwave Radiation, 850 hPa wind and 200 hPa wind, 2000 - 2002.
#  * EOFs: NEED TO FILL IN
#

##############################################################################
# METplus Components
# ------------------
#
# This use case calls UserScript 5 times.  The first call creates a list of the mean daily annual data 
# files for OLR, U850, and U200. It is done separately since the mean daily annual files are span across
# all years whereas the RMM calculation can proceed on a different time frame.  The second, third, and 
# fourth calls to UserScript run the pre-processing on OLR, U850, and U200 using a harmonic analysis 
# program in python.  Then, there are 3 calls to RegridDataPlane, which cuts the grid to only include 
# -15 to 15 latitude.  The last (fifth) call to UserScript runs the RMM calculation.
#
# There are four optional pre-processing steps.  These steps are turned off due to data size and processing
# time.  Two of the steps are calls to PcP-Combine to compute the mean daily annual data for OLR, wind 
# (U850 and U200).  The other two steps also call Pcp-Combine but these compute daily means for OLR and wind.  
# These omitted steps can be turned back on by using the PROCESS_LIST that is commented out:
#
# PROCESS_LIST = PROCESS_LIST = PcpCombine(mean_daily_annual_cycle_obs_wind), PcpCombine(mean_daily_annual_cycle_obs_olr), PcpCombine(daily_mean_obs_wind), PcpCombine(daily_mean_obs_olr), UserScript(create_mda_filelist), UserScript(harmonic_anomalies_olr), UserScript(harmonic_anomalies_u850), UserScript(harmonic_anomalies_u200), RegridDataPlane(regrid_obs_olr), RegridDataPlane(regrid_obs_u850), RegridDataPlane(regrid_obs_u200), UserScript(script_rmm)
#
# Settings for the optional pre-processing steps can be found in the respective sections of the configuration, 
# mean_daily_annual_cycle_obs_wind, mean_daily_annual_cycle_obs_olr, daily_mean_obs_wind, and daily_mean_obs_olr.  
# Data is not provided in the tarball to run these steps, but the configurations is provided for reference on how 
# to set up these calculations.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop, but the UserScript to create and EOF filelist is run once and the RMM driver script is 
# run once.  The RMM script has the ability to loop over lead time, although only one lead time is provided here.  The 
# optional pre-processing step loops by valid time.  
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.conf.
# The file UserScript_obsERA_obsOnly_RMM/RMM_driver.py runs the python program and the
# variables for the RMM calculation are set in the [user_env_vars] section of the .conf 
# file. 
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.conf

##############################################################################
# MET Configuration
# ---------------------
#
# There are no MET configuration files used in this use case.
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
# This use case runs the RMM driver which computes RMM and creates a phase diagram. Inputs to the 
# RMM driver include netCDF files formatted in MET's netCDF version.  In addition, a txt file containing 
# the listing of these input netCDF files is required, as well as text file listings of the EOF1 and 
# EOF2 files.  These text files can be generated using the USER_SCRIPT_INPUT_TEMPLATES in the 
# [create_eof_filelist] and [script_omi] sections.  Some optional pre-processing steps include using 
# regrid_data_plane to either regrid your data or cut the domain to 20N - 20S.
#
# For the RMM calculation, the OLR data are then projected onto Empirical Orthogonal Function (EOF) 
# data that is computed for each day of the year, latitude, and longitude.  The OLR is then filtered 
# for 20 - 96 days, and regressed onto the daily EOFs.  Finally, it's normalized and these normalized 
# components are plotted on a phase diagram.  The RMM driver script orchestrates the calculation of the 
# MJO indices and the generation of a phase diagram RMM plot.
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM/RMM_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired:
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_obsERA_obsOnly_RMM.conf /path/to/user_system.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use 
# case will be found in model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_RMM/plots (relative to **OUTPUT_BASE**).  
# The output may include the regridded data and daily averaged files if those steps are turned on.  A Phase diagram 
# plots will be generated:
#
#  * obs_RMM_comp_phase.png
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SMJOAppUseCase
#   * RegridDataPlaneUseCase
#   * PCPCombineUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_obsERA_obsOnly_RMM.png'
#
