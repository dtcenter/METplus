"""
UserScript: Make GFS and ERA OMI plot from calculated MJO indices
=================================================================

model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.py

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
# came from Maria Gehne at PSL.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS Model Outgoing Longwave Radiation, 2017 - 2018.
#
# **Observation:** ERA Reanlaysis Outgoing Longwave Radiation, 2017 - 2018.
#
# **EOFs:** Observed OMI EOF1 and EOF2 patterns from the PSL Website (https://psl.noaa.gov/mjo/mjoindex/)
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
# This use case requires METcalcpy, METplotpy, and METdataio to run. The metcalcpy scripts accessed include the following:
# 
# * metcalcpy/contributed/rmm_omi/compute_mjo_indices.py
#
# The METplotpy scripts accessed include the following:
# 
# * metplotpy/contributed/mjo_rmm_omi/plot_mjo_indioces.py
#
# The METdataio scripts accessed include the following:
#
# * METreadnc/util/read_netcdf.py

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 20170101
#
# **End time (VALID_END):** 20181231
#
# **Increment between beginning and end times (VALID_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# This use case does not loop, but the UserScript to create and EOF filelist is run once and the OMI driver script is 
# run once for both the model and observations across the entire time period.  The 3 optional pre-processing steps 
# loop by valid time. The Phase diagram plots are created over a different time frame than the calculation, 01-01-2017
# to 03-31-2017 for both plots.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.conf.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.conf

##############################################################################
# MET Configuration
# ---------------------
#
# There are no MET configuration files used in this use case.

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding.

##############################################################################
# Python Scripting
# ----------------
#
# This use case runs the OMI driver which computes OMI and creates a phase diagram. Inputs to the 
# OMI driver include netCDF files formatted in MET's netCDF version.  In addition, a txt file containing 
# the listing of these input netCDF files is required, as well as text file listings of the EOF1 and 
# EOF2 files.  These text files can be generated using the USER_SCRIPT_INPUT_TEMPLATES in the 
# [create_eof_filelist] and [script_omi] sections.  Variables for the OMI calculation are set in the 
# [user_env_vars] section of the .conf file. 
#
# For the OMI calculation, the OLR data are projected onto Empirical Orthogonal Function (EOF) 
# data that is computed for each day of the year, latitude, and longitude.  The OLR is then filtered 
# for 20 - 96 days, and regressed onto the daily EOFs.  Finally, it's normalized and these normalized 
# components are plotted on a phase diagram.  The OMI driver script orchestrates the calculation of the 
# MJO indices and the generation of a phase diagram OMI plot.  Separate phase diagrams are created for 
# the model and observations.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI/OMI_driver.py
#
#   .. highlight:: python 
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI/OMI_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along with any
# user-specific system configuration files if desired::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_OMI.conf /path/to/user_system.conf
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
# case will be found in model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI/plots (relative to **OUTPUT_BASE**).  
# Phase diagram plots will be generated and will include 2 files::
#
#  * fcst_OMI_comp_phase.png
#  * obs_OMI_comp_phase.png
#
# If the pre-processing steps are turned on, the output will include the regridded data and daily averaged files.

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
