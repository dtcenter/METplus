"""
Grid-Stat and MODE: Sea Ice Validation   
====================================================================================================

Runs bot GridStat and MODE tools to compare two ice concentration analyses 
and generate statistics and diagnostics. (IMS:NCEPAnalysis:Grib2) 

"""
####################################################################################################
# Scientific Objective
# --------------------
#
# Run Grid-Stat and MODE to compare the National Ice Center (NIC) Interactive Multisensor Snow
# and Ice Mapping System (IMS) and the National Centers for Environmental Prediction (NCEP)
# sea ice analysis.  This is a validation and diagnostics use case because it is limited to a
# comparison between IMS analysis to NCEP analysis.

####################################################################################################
# Datasets
# --------
#
# Both IMS and NCEP sea ice analyses are observation datasets. For the purposes
# of MET, IMS is referred to as "forecast" and NCEP is referred to as "observation".
#
#  * Forecast dataset: IMS Sea Ice Concentration
#      - Variable of interest: ICEC; ICEC is a binary field where "1" means a sea ice concentration of >=0.40 and "0" means a sea ice concentration of <0.40.
#      - Level: Z0 (surface)
#      - Dates: 20190201 - 20190228
#      - Valid time: 22 UTC
#      - Format: Grib2
#      - Projection: 4-km Polar Stereographic
#
#  * Observation dataset: NCEP Sea Ice Concentration
#      - Variable of interest: ICEC; ICEC is the sea ice concentration with values from 0.0 - 1.0. Values >1.0 && <=1.28 indicate flagged data to be included and should be set to ==1.0 when running MET. Values <1.28 should be ignored as that indicates an invalid observation.
#      - Level: Z0 (surface)
#      - Dates: 20190201 - 20190228
#      - Valid time: 00 UTC
#      - Format: Grib2
#      - Projection: 12.7-km Polar Stereographic
#    
#  * Data source: Received from Robert Grumbine at EMC. IMS data is originally from the NIC. NCEP data is originally from NCEP.
#  
#  * Location: IMS: https://www.natice.noaa.gov/ims/index.html; IMS - (https://polar.ncep.noaa.gov/seaice/Analyses.shtml) 

###################################################################################################
# METplus Components
# ------------------
#
# This use case runs the MET GridStat and MODE tools.

###################################################################################################
# METplus Workflow
# ----------------
# 
# The workflow processes the data by valid time, meaning that each tool will be run for each time 
# before moving onto the next valid time. The GridStat tool is called first followed by the MODE
# tool. It processes analysis times from 2019-02-01 to 2019-02-05. The valid times for each analysis
# are different from one another (please see 'Dataset' section for more information).

###################################################################################################
# METplus Configuration
# ---------------------
# 
# METplus first loads all of the configuration files found in parm/metplus_config. Then, it loads
# any configuration files passed to METplus by the command line with the -c option.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf
#

###################################################################################################
# MET Configuration
# -----------------
# 
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# **GridStatConfig_sea_ice**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/cryosphere/GridStatConfig_sea_ice
#
# See the following file for more information about the environment variables set in this configuration file:
#   parm/use_cases/met_tool_wrapper/GridStat/GridStat.py
#
# **MODEConfig_sea_ice**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/cryosphere/MODEConfig_sea_ice
#
# See the following file for more information about the environment variables set in this configuration file:
#   parm/use_cases/met_tool_wrapper/MODE/MODE.py
#


###################################################################################################
# Running METplus
# ---------------
#
# The command to run this use case is::
#       
#  master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf

####################################################################################################
# Expected Output
# ---------------
#
# A successful run of this use case will output the following to the screen and logfile::
#  
#    INFO: METplus has successfully finished runing.
#
# A successful run will have the following output files in the location defined by {OUTPUT_BASE}, which
# is located in the metplus_system.conf configuration file located in /path/to/METplus/parm/metplus_config.
# This list of files should be found for every time run through METplus. Using the output for 20190201 as
# and example.
#
# **GridStat output**:
#
# * grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V_pairs.nc
# * grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V.stat
#
# **MODE output**:
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
#

###################################################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/cryosphere_GridStat_MODE_fcstIMS_obsNCEP_Sea_Ice.png'
#
# .. note::
#    `GridStatToolUseCase <https://ncar.github.io/METplus/search.html?q=GridStatToolUseCase&check_keywords=yes&area=default>`_,
#    `MODEToolUseCase <https://ncar.github.io/METplus/search.html?q=MODEToolUseCase&check_keywords=yes&area=default>`_,
#    `MarineAndCryoAppUseCase <https://ncar.github.io/METplus/search.html?q=MarineAndCryoAppUseCase&check_keywords=yes&area=default>`_,
#    `ValidationUseCase  <https://ncar.github.io/METplus/search.html?q=ValidationUseCase&check_keywords=yes&area=default>`_,
#    `S2SAppUseCase <https://ncar.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_, 
#    `NOAAEMCOrgUseCase <https://ncar.github.io/METplus/search.html?q=NOAAEMCOrgUseCase&check_keywords=yes&area=default>`_
#    `DiagnosticsUseCase <https://ncar.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
