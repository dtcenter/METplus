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
#    - Format: Grib2
#    - Projection: 4-km Polar Stereographic
#
#  * Observation dataset: NCEP Sea Ice Concentration
#    - Variable of interest: ICEC; ICEC is the sea ice concentration with values from 0.0 - 1.0. Values
#      >1.0 && <=1.28 indicate flagged data to be included and should be set to ==1.0 when running MET.
#      Values <1.28 should be ignored as that indicates an invalid observation.
#    - Level: Z0 (surface)
#    - Dates: 20190201 - 20190228
#    - Format: Grib2
#    - Projection: 12.7-km Polar Stereographic
#    
#  * Data source: Received from Robert Grumbine at EMC. IMS data is originally from the NIC. NCEP data
#                 is originally from NCEP. 
#  
#  * Location: All input data is located on eyewall. 

####################################################################################################
# METplus Components
# ------------------
#
# This use case utilizes the MET GridStat and MET Mode tools. 

    ##############################################################################
    # METplus Workflow
    # ----------------
    # 
    # 
    # A general description of the workflow will be useful to the user. For example,
    # the order in which tools are called (e.g. PcpCombine then grid_stat) or the way 
    # in which data are processed (e.g. looping over valid times) with an example
    # of how the looping will work would be helpful for the user.

###################################################################################################
# METplus Configuration
# ---------------------
# 
# METplus sets environment variables based on the values in the METplus configuration file. 
#
# These variables are referenced in the MET configuration files.
#  1. ${MODEL} - Name of the forecast input. Corresponds to MODEL in the METplus configuration file.
#  2. ${OBTYPE} - Name of the observation input. Corresponds to OBTYPE in the METplus config. file.
#  3. ${FCST_FIELD} - Formatted forecast field information. Generated from FCST_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] 
#                    in the METplus config file. 
#  4. ${OBS_FIELD} - Formatted observation field information. Generated from OBS_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS]
#                   in the METplus config file. 
#  5. ${FCST_VAR} - Field name of forecast data to process. Used in output_prefix to include input information in
#                  the output filenames. Corresponds to FCST_VAR<n>_NAME in the METplus config. file. 
#  6. ${OBS_VAR} - Field name of observation data to process. Used in output_prefix to include input information in
#                 the output filenames. Corresponds to OBS_VAR<n>_NAME in the METplus config. file. 
#  7. ${LEVEL} - Vertical level of the forecast input data. Used in output_prefix to include input information in
#               the output filenames. Corresponds to FCST_VAR<n>_LEVELS in the METplus config. file.
#  8. ${QUILT} - True/FAlse to perform quilting. Corresponds to MODE_QUILT in the METplus config. file.
#  9. ${FCST_CONV_RADIUS} - Convolution radius/radii used for forecast data. Corresponds to FCST_MODE_CONV_RADIUS in the
#                          METplus config. file. 
# 10. ${FCST_CONV_THRESH} - Convolution threshold(s) used for forecast data. Corresponds to FCST_CONV_THRESH in the
#                           METplus config. file. 
#
                    #
                    #    [dir]
                    #    OUTPUT_BASE=/path/to
                    #
                    # Or if you want to suck in the entire conf file automatically, provide the relative
                    # path to the conf file from the gallery_dirs directory for this use case specified in the
                    # conf.py file (this is recommended since it will keep in sync with the conf file automatically):
                    #
                    # .. highlight:: none
                    # .. literalinclude:: ../../../../parm/use_cases/template/use_case_application/use-case-application.conf

###################################################################################################
# Running METplus
# ---------------
#
# It will be helpful to include an example command of running METplus.

####################################################################################################
                    # Expected Output
                    # ---------------
                    #
                    # Spend some time detailing how the user will know if the use case succeeded or not. This
                    # could include anything from where expected output files will be, what those filenames will be,
                    # what METplus will print to the command line, images from METplotpy, or something else.
                    # If the expected output is just files, include some information for the user on how they can
                    # know if what is in the files is what is expected.
                    #
                    # Using static images is allowed but must use a path relative to the gallery_dirs directory for
                    # this use case (found in the conf.py file). This relative path allows images to be stored with the
                    # use case files under parm/use_cases:
                    #
                    # .. image:: ../../../../parm/use_cases/template/use_case_application/METplus_logo.png
                    #

                    ##############################################################################
                    # Keywords
                    # --------
                    #
                    # Choose from the following pool of keywords, and include them in a note directive below.
                    # Remove any keywords you don't use.
                    #
                    # GridStatUseCase, PB2NCUseCase, PrecipitationUseCase
                    #
                    # Now include them like this:
                    #
                    # .. note:: GridStatUseCase, PB2NCUseCase
