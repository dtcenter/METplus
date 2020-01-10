"""
Use Case: Sea Ice Validation and Verification
====================================================================================================

This use case will run both the MET GridStat and MODE tools to compare the National Ice Center (NIC) 
Interactive Multisensor Snow and Ice Mapping System (IMS; https://www.natice.noaa.gov/ims/index.html)
and the National Centers for Environmental Prediction (NCEP) sea ice analysis 
(https://polar.ncep.noaa.gov/seaice/Analyses.shtml). Future uses include comparing sea ice forecast 
models against sea ice observations. For now, it is limited to observation against observation.

"""
####################################################################################################
# Scientific Objective
# --------------------
#
# Compare IMS sea ice concentration analysis to NCEP sea ice concentration
# analysis. Generate statistics of the results.

####################################################################################################
# Datasets
# --------
#
# Both IMS and NCEP sea ice analyses are observation datasets. For the purposes
# of MET, IMS is referred to as "forecast" and NCEP is referred to as "observation".
#
#  * Forecast dataset: IMS Sea Ice Concentration
#    - Variable of interest: ICEC; ICEC is a binary field where "1" means a sea ice concentration of 
#      >=0.40 and "0" means a sea ice concentration of <0.40.
#    - Level: Z0 (surface)
#    - Dates: 20190201 - 20190228
#    - Valid time: 22 UTC
#    - Format: Grib2
#    - Projection: 4-km Polar Stereographic
#
#  * Observation dataset: NCEP Sea Ice Concentration
#    - Variable of interest: ICEC; ICEC is the sea ice concentration with values from 0.0 - 1.0. 
#      Values >1.0 && <=1.28 indicate flagged data to be included and should be set to ==1.0 when 
#      running MET. Values <1.28 should be ignored as that indicates an invalid observation.
#    - Level: Z0 (surface)
#    - Dates: 20190201 - 20190228
#    - Valid time: 00 UTC
#    - Format: Grib2
#    - Projection: 12.7-km Polar Stereographic
#    
#  * Data source: Received from Robert Grumbine at EMC. IMS data is originally from the NIC. NCEP 
#    data is originally from NCEP. 
#  
#  * Location: All input data is located on eyewall. 

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

###################################################################################################
# MET Configuration
# -----------------
# 
# METplus sets environment variables based on the values in the METplus configuration file. 
#
# These variables are referenced in the MET configuration files.
# ${MODEL} - Name of the forecast input. Corresponds to MODEL in the METplus configuration file.
# ${OBTYPE} - Name of the observation input. Corresponds to OBTYPE in the METplus configuration file.
# ${FCST_FIELD} - Formatted forecast field information. Generated from FCST_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] 
#                 in the METplus configuration file. 
# ${OBS_FIELD} - Formatted observation field information. Generated from OBS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS]
#                in the METplus configuration file. 
# ${FCST_VAR} - Field name of forecast data to process. Used in output_prefix to include input information in
#               the output filenames. Corresponds to FCST_VAR<n>_NAME in the METplus configuration file. 
# ${OBS_VAR} - Field name of observation data to process. Used in output_prefix to include input information in
#              the output filenames. Corresponds to OBS_VAR<n>_NAME in the METplus configuration file. 
# ${LEVEL} - Vertical level of the forecast input data. Used in output_prefix to include input information in
#            the output filenames. Corresponds to FCST_VAR<n>_LEVELS in the METplus configuration file.
# ${QUILT} - True/FAlse to perform quilting. Corresponds to MODE_QUILT in the METplus configuration file.
# ${FCST_CONV_RADIUS} - Convolution radius/radii used for forecast data. Corresponds to FCST_MODE_CONV_RADIUS in the
#                       METplus configuration file. 
# ${FCST_CONV_THRESH} - Convolution threshold(s) used for forecast data. Corresponds to FCST_CONV_THRESH in the
#                       METplus configuration file. 
# ${FCST_MERGE_THRESH} - Merge threshold(s) used for forecast data. Corresponds to FCST_MODE_CONV_THRESH in the
#                        METplus configuration file.
# ${FCST_MERGE_FLAG} - True/False merge flag used for forecast data. Corresponds to FCST_MODE_MERGE_FLAG in the
#                      METplus configuration file.
# ${OBS_CONV_RADIUS} - Convultion radius/radii used for observation data. Corresponds to OBS_CONV_RADIUS in the
#                      METplus configuration file.
# ${OBS_CONV_THRESH} - Convolution threshold(s) used for observation data. Corresponds to OBS_MODE_CONV_THRESH
#                      in the METplus configuration file.
# ${OBS_MERGE_THRESH} - Merge threshold(s) used for observation data. Corresponds to OBS_MODE_MERGE_FLAG in the
#                       METplus configuration file.
# ${OBS_MERGE_FLAG} - True/False merge flag used for observation data. Corresponds to OBS_MODE_MERGE_FLAG in the
#                     METplus configuration file.

###################################################################################################
# Running METplus
# ---------------
#
# The command to run this use case is: 
#       
#  master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/cryosphere/sea_ice.conf

####################################################################################################
# Expected Output
# ---------------
#
# A successful run of this use case will output the following to the screen and logfile:
#  
#   INFO: METplus has successfully finished runing.
#
# A successful run will have the following output files in the location defined by {OUTPUT_BASE}, which
# is located in the metplus_system.conf configuration file located in /path/to/METplus/parm/metplus_config.
# This list of files should be found for every time run through METplus. Using the output for 20190201 as
# and example.
#
# GridStat output:
# grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V_pairs.nc
# grid_stat_IMS_ICEC_vs_NCEP_ICEC_Z0_000000L_20190201_220000V.stat
#
# MODE output:
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_cts.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_obj.nc
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1_obj.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R1_T1.ps
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_cts.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_obj.nc 
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1_obj.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R2_T1.ps
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_cts.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_obj.nc
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1_obj.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R3_T1.ps
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_cts.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_obj.nc
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1_obj.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R4_T1.ps
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_cts.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_obj.nc
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1_obj.txt
# mode_IMS_ICEC_vs_NCEP_ICEC_000000L_20190201_220000V_000000A_R5_T1.ps 

###################################################################################################
# Keywords
# --------
#
# .. note:: GridStatUseCase, MODEUseCase
