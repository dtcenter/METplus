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
# objects from two or more fields, defined by a logical expression. This use
# case identifies blizzard-like objects defined by: 1) the presence of snow
# precipitation type, 2) 10-m winds > 20 mph, and  3) visibility < 1/2 mile.
# The use of multivariate MODE is well-suited to assess the structure and
# placement of complex high-impact events such as blizzard conditions and heavy
# snow bands. Output from this use-case consists of the MODE forecast and observation
# super objects and the MODE ASCII, NetCDF, and PostScript files.
#

##############################################################################
# Datasets
# --------
#
# | **Forecast dataset:** 1-hour HRRR in grib2
# | **Observation dataset:** MRMS and HRRR analysis in grib2
# 
# The forecast and observation fields are only a subset of the full domain in
# order for a faster run-time of Multivariate MODE. An example command using
# wgrib2 to create the HRRR subdomain is::
#
#   wgrib2 infile.grib2 -new_grid_winds earth -new_grid lambert:262.5:38.5:38.5:38.5 -83.0:400:3000 37.0:400:3000 outfile.grib2 
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MODE using multiple variables to output the super objects
# based on a user-defined logical expression. Currently, the initial multivariate
# MODE run only outputs the super objects and additional steps are required to
# produce the statistical output. GenVxMask is run on a field(s) of interest
# using the super objects to mask the field(s). Finally, MODE is run a second
# time on the super-object-masked field(s) to output attribute statistics for
# the field(s).
#
# **Note:** The second MODE run can also be run directly on the super objects if
# field-specific statistics, such as intensity, is not desired.
# 

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# MODE(mv), GenVxMask(fcst_super), GenVxMask(obs_super), MODE (super)
# 
# Where the first instance of MODE runs over multiple variables to identify
# super objects for the forecast and observation, GenVxMask masks the raw input
# field(s) using the super objects, and the second instance of MODE is run
# traditionally to compare the masked forecast and observed super objects and
# and provide statistics.
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
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf
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
# This use case can be run two ways:
#
# 1) Passing in MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in OUTPUT_BASE for the various MET tools
# and will contain the following files:
#
# **mode/2021020100/f21**
#
# Multivariate output - first instance
#
# Precipitation type = snow
#
# * 00/mode_210000L_20210201_210000V_000000A_cts.txt
# * 00/mode_210000L_20210201_210000V_000000A_obj.nc
# * 00/mode_210000L_20210201_210000V_000000A_obj.txt
# * 00/mode_210000L_20210201_210000V_000000A.ps
#
# Visibility
#
# * 01/mode_210000L_20210201_210000V_000000A_cts.txt
# * 01/mode_210000L_20210201_210000V_000000A_obj.nc
# * 01/mode_210000L_20210201_210000V_000000A_obj.txt
# * 01/mode_210000L_20210201_210000V_000000A.ps
#
# 10-m Winds
#
# * 02/mode_210000L_20210201_210000V_000000A_cts.txt
# * 02/mode_210000L_20210201_210000V_000000A_obj.nc
# * 02/mode_210000L_20210201_210000V_000000A_obj.txt
# * 02/mode_210000L_20210201_210000V_000000A.ps
#
# Super Objects
#
# * f_super.nc
# * o_super.nc
#
# MODE 10-m wind super object output - second instance
#
# * mode_HRRR_vs_ANALYSIS_WIND_super_Z10_210000L_20210201_210000V_000000A_cts.txt
# * mode_HRRR_vs_ANALYSIS_WIND_super_Z10_210000L_20210201_210000V_000000A_obj.nc
# * mode_HRRR_vs_ANALYSIS_WIND_super_Z10_210000L_20210201_210000V_000000A_obj.txt
# * mode_HRRR_vs_ANALYSIS_WIND_super_Z10_210000L_20210201_210000V_000000A.ps
#
# **gen_vx_mask/2021020100**
#
# * fcst_wind_super_2021020100_f21.nc
# * obs_wind_super_2021020121.nc

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase 
#   * GenVxMaskToolUseCase 
#   * ShortRangeAppUseCase
#   * GRIB2FileUseCase 
#   * RegriddingInToolUseCase 
#   * NOAAWPCOrgUseCase
#   * NCAROrgUseCase 
#   * DiagnosticsUseCase
#
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-MODEMultivar_fcstHRRR_obsMRMS_HRRRanl.png'
#
