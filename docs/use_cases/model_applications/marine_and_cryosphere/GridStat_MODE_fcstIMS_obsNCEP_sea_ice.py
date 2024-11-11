"""
Grid-Stat and MODE: Sea Ice Validation   
======================================

model_applications/marine_and_cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

################################################################################
# Scientific Objective
# --------------------
#
# Run Grid-Stat and MODE to compare the National Ice Center (NIC) Interactive Multisensor Snow
# and Ice Mapping System (IMS) and the National Centers for Environmental Prediction (NCEP)
# sea ice analysis.  This is a validation and diagnostics use case because it is limited to a
# comparison between IMS analysis to NCEP analysis.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

#################################################################################
# Datasets
# --------
#
# Both IMS and NCEP sea ice analyses are observation datasets. For the purposes
# of MET, IMS is referred to as "forecast" and NCEP is referred to as "observation".
#
# | **Forecast:** IMS Sea Ice Concentration
# |     - Variable of interest: ICEC; ICEC is a binary field where "1" means a sea ice concentration of >=0.40 and "0" means a sea ice concentration of <0.40.
# |     - Level: Z0 (surface)
# |     - Dates: 20190201 - 20190228
# |     - Valid time: 22 UTC
# |     - Format: Grib2
# |     - Projection: 4-km Polar Stereographic
#
#  | **Observation:** NCEP Sea Ice Concentration
#  |    - Variable of interest: ICEC; ICEC is the sea ice concentration with values from 
#        0.0 - 1.0. Values >1.0 && <=1.28 indicate flagged data to be included and should be set to ==1.0 when running MET. 
#        Values >1.28 should be ignored as that indicates an invalid observation.
#  |    - Level: Z0 (surface)
#  |    - Dates: 20190201 - 20190228
#  |    - Valid time: 00 UTC
#  |    - Format: Grib2
#  |    - Projection: 12.7-km Polar Stereographic
#
# **Climatology:** None
#    
#  **Data source:** Received from Robert Grumbine at EMC. IMS data is originally from the NIC. NCEP data is originally from NCEP.
#  
#  **Location:** IMS: https://www.natice.noaa.gov/ims/index.html; IMS - (https://polar.ncep.noaa.gov/seaice/Analyses.shtml)
# 
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

###################################################################################
# METplus Components
# ------------------
#
# This use case runs the MET GridStat and MODE tools.

###################################################################################
# METplus Workflow
# ----------------
# 
# **Beginning time (VALID_BEG):** 20190201
#
# **End time (VALID_END):** 20190201
#
# **Increment between beginning and end times (VALID_INCREMENT):** 86400
#
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#
# The workflow processes the data by valid time, meaning that each tool will be run for each time 
# before moving onto the next valid time. The GridStat tool is called first followed by the MODE
# tool. It processes analysis times from 2019-02-01 to 2019-02-05. The valid times for each analysis
# are different from one another (please see `Datasets`_ section for more information).

##################################################################################
# METplus Configuration
# ---------------------
# 
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/marine_and_cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf

##################################################################################
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
# .. dropdown:: GridStatConfig_wrapped
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#
# .. dropdown:: MODEConfig_wrapped
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# None

################################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#       
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

####################################################################################################
# Expected Output
# ---------------
#
# A successful run of this use case will output the following to the screen and logfile::
#  
#    INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in two locations:
# GridStat output will be in {OUTPUT_BASE}/model_applications/marine_and_cryosphere/sea_ice/GridStat.
# MODE output will be in {OUTPUT_BASE}/model_applications/marine_and_cryosphere/sea_ice/MODE.
# Using the output for 20190201 as an example:
#
# **GridStat output**::
#
# * grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V_pairs.nc
# * grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V.stat
#
# **MODE output**::
#
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_cts.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_obj.nc
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_obj.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1.ps
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_cts.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_obj.nc 
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_obj.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1.ps
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_cts.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_obj.nc
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_obj.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1.ps
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_cts.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_obj.nc
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_obj.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1.ps
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_cts.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_obj.nc
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_obj.txt
# * mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1.ps 

###################################################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * MODEToolUseCase
#   * MarineAndCryosphereAppUseCase
#   * ValidationUseCase
#   * S2SAppUseCase
#   * NOAAEMCOrgUseCase
#   * DiagnosticsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere_GridStat_MODE_fcstIMS_obsNCEP_Sea_Ice.png'
