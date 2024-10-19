"""
UserScript: Make GFS and ERA OMI plot from calculated MJO indices
=================================================================

model_applications/
s2s_mjo/
UserScript_fcstGFS_obsERA_OMI.py

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
# This use case uses outgoing longwave radiation (OLR) to compute the OLR based MJO Index (OMI), which is
# a convective index of the MJO.  OMI is computed separately for the model and observations and then displayed
# on phase diagrams to evaluate the model reprentation of this important oscillation.  The code for computing OMI
# comes from Maria Gehne at PSL.
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: GFS Model Outgoing Longwave Radiation, 2017 - 2018.
#  * Observation dataset: ERA Reanlaysis Outgoing Longwave Radiation, 2017 - 2018.
#  * EOFs: Observed OMI EOF1 and EOF2 patterns from the PSL Website (https://psl.noaa.gov/mjo/mjoindex/)

##############################################################################
# METplus Components
# ------------------
#
# This use case calls UserScript twice.  The first UserScript creates a list of the EOF files 
# needed for the calculation.  It is done separately since the EOF files are needed for each day
# of the year while the OMI calculation is on a separate time frame.  The second UserScript runs the
# OMI calculation.
#
# There are three optional pre-processing steps for the OMI calculation.  These include using PcpCombine to
# compute daily averages for the forecast, and using RegridDataPlane for both the model and observations
# to cut the grid to only include -20 to 20 latitude.  These omitted steps can be turned back on by using the 
# PROCESS_LIST that is commented out:
#
# PROCESS_LIST = PcpCombine(daily_mean_fcst), RegridDataPlane(regrid_obs_olr), RegridDataPlane(regrid_fcst_olr), UserScript(create_eof_filelist), UserScript(script_omi) 
#
# Settings for the optional pre-processing steps can be found in the respective sections of the configuration, 
# daily_mean_fcst, regrid_obs_olr, and regrid_fcst_olr.  Data is not provided in the tarball to run these steps, 
# but the configurations are provided for reference on how to set up these calculations.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop, but the UserScript to create and EOF filelist is run once and the OMI driver script is 
# run once for both the model and observations.  The OMI script has the ability to loop over lead time, although only 
# one lead time is provided here. The 3 optional pre-processing steps loop by valid time.  
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.conf.
# The file UserScript_fcstGFS_obsERA_OMI/OMI_driver.py runs the python program and the
# variables for the OMI calculation are set in the [user_env_vars] section of the .conf 
# file. 
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.conf

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
# This use case runs the OMI driver which computes OMI and creates a phase diagram. Inputs to the 
# OMI driver include netCDF files formatted in MET's netCDF version.  In addition, a txt file containing 
# the listing of these input netCDF files is required, as well as text file listings of the EOF1 and 
# EOF2 files.  These text files can be generated using the USER_SCRIPT_INPUT_TEMPLATES in the 
# [create_eof_filelist] and [script_omi] sections.  Some optional pre-processing steps include using 
# regrid_data_plane to either regrid your data or cut the domain to 20N - 20S.
#
# For the OMI calculation, the OLR data are then projected onto Empirical Orthogonal Function (EOF) 
# data that is computed for each day of the year, latitude, and longitude.  The OLR is then filtered 
# for 20 - 96 days, and regressed onto the daily EOFs.  Finally, it's normalized and these normalized 
# components are plotted on a phase diagram.  The OMI driver script orchestrates the calculation of the 
# MJO indices and the generation of a phase diagram OMI plot.  Separate phase diagrams are created for 
# the model and observations.
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI/OMI_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
#Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired:
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_OMI.conf /path/to/user_system.conf
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
# case will be found in model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI/plots (relative to **OUTPUT_BASE**).  
# The output may include the regridded data and daily averaged files if those steps are turned on.  Phase diagram 
# plots will be generated and will include 2 files:
#
#  * fcst_OMI_comp_phase.png
#  * obs_OMI_comp_phase.png
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
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_fcstGFS_obsERA_OMI.png'
#
