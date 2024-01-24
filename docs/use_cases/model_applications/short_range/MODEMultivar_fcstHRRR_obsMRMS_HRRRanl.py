"""
MODE: Multivariate  
=========================================================================

model_applications/
short_range/
MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case demonstrates how to run Multivariate MODE to identify complex
# objects from two or more fields defined by a logical expression. This use
# case identifies blizzard-like objects defined by the intersection of : 1) the
# presence of snow precipitation type, 2) 10-m winds > 20 mph, and  3) visibility
# < 1/2 mile. The use of multivariate MODE is well-suited to assess the structure and
# placement of complex high-impact events such as blizzard conditions and heavy
# snow bands. Output from this use-case consists of the MODE ASCII, NetCDF, and
# PostScript files for the MODE forecast and observation super objects.
#
# In this case, MODE super object intensity statistics were ouput for both 10-m
# wind and visibility. Using the the MODE_MULTIVAR_INTENSITY_FLAG, the user can
# control for which variables super object intensity statistics will be output.
# If all are set to False, then no intensity information will be output and only
# statistics relative to the super-object geometry will be available. In the case
# no requested intesities, the parameters MODE_FCST/OBS_MULTIVAR_NAME and/or
# MODE_FCST/OBS_MULTIVAR_LEVEL may be used as identifiers for the super-object.

##############################################################################
# Datasets
# --------
#
# **Forecast dataset:** 1-hour HRRR in grib2
#
# **Observation dataset:** MRMS and HRRR analysis in grib2
# 
# The forecast and observation fields are only a subset of the full domain in
# order for a faster run-time of Multivariate MODE. An example command using
# wgrib2 to create the HRRR subdomain is::
#
#   wgrib2 infile.grib2 -new_grid_winds earth -new_grid lambert:262.5:38.5:38.5:38.5 -83.0:400:3000 37.0:400:3000 outfile.grib2 
#
# **Location:** All of the input data required for this use case can be found
# in the *short_range* sample data tarball.
# Navigate to `METplus Releases <https://github.com/dtcenter/METplus/releases>`_
# and download sample data for the appropriate release.
#
# This tarball should be unpacked into the directory that you will set the
# value of INPUT_BASE. See :ref:`running-metplus` for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus MODE wrapper, ingesting multiple variables
# to output complex super objects based on a user-defined logical expression. 
# 

##############################################################################
# METplus Workflow
# ----------------
#
# MODE is the only tool called and ingests multiple fields to create a complex
# super object.
#
# This example runs a single forecast hour.
#
# | **Initialization:** 2021020100
# | **Forecast lead:** 21
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line:
# parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`MODE MET Configuration<mode-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf /path/to/user_system.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in OUTPUT_BASE and will contain the following
# files in the directory mode/2021020100/f21:
#
#  * mode_Fcst_VIS_L0_Obs_VIS_L0_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_cts.txt
#  * mode_Fcst_VIS_L0_Obs_VIS_L0_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_obj.nc
#  * mode_Fcst_VIS_L0_Obs_VIS_L0_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_obj.txt
#  * mode_Fcst_VIS_L0_Obs_VIS_L0_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A.ps
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_cts.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_obj.nc
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A_obj.txt
#  * mode_Fcst_WIND_Z10_Obs_WIND_Z10_HRRR_vs_ANALYSIS_210000L_20210201_210000V_000000A.ps

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase 
#   * ShortRangeAppUseCase
#   * GRIB2FileUseCase 
#   * RegriddingInToolUseCase 
#   * NOAAWPCOrgUseCase
#   * NCAROrgUseCase 
#   * DiagnosticsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.png'
#
