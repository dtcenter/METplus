"""
Surrogate Severe Calculation: PCPCombine, EnsembleStat, and RegridDataPlane 
===================================================================================================

model_applications/\
convection_allowing_model/\
EnsembleStat_fcstHRRR_fcstOnly_\
SurrogateSevere.conf

"""
###################################################################################################
# Scientific Objective
# --------------------
#
# Run PCPCombine, EnsembleStat, and RegridDataPlane tools to create surrogate severe probability 
# forecasts (SSPFs) for a given date. SSPFs are a severe weather forecasting tool and is a techniqu
# used by the Storm Prediction Center (SPC) as well as others. SSPFs are based on updraft helicity 
# (UH; UH = ∫z0 to zt (ω * ζ) dz) since certain thresholds of UH have been shown as good proxies for# severe weather. SSPFs can be thought of as the perfect model forecast. They are derived as follows:
#
#    1. Regrid the maximum UH value over the 2-5km layer at each grid point to the NCEP 211 grid (dx = ~80km).
#    2. Create a binary mask of points that meet a given threshold of UH)
#    3. Convert the binary mask into a probability field by applying a Gaussian filter.
# 
# For more information, please reference Sobash et al. 2011 (https://journals.ametsoc.org/doi/full/10.1175/WAF-D-10-05046.1).

###################################################################################################
# Datasets
# --------
#
# There are two dates that can be used as input data for this use case 20190518 or 20200205.
# 
# * Input Data: HRRR data
#   - There should 24 grib2 files.
#   - Variable of interest: MXUPHL; the maximum updraft helicity
#   - Level: Z2000-5000; from 2 - 5km
#   - Format: grib2
#   - Projection: Lambert Conformal
#
# * Location: kiowa:/d1/projects/METplus/METplus_Data/model_applications/convection_allowing_models/surrogate_severe_calc/
#
# * Data Source: Originally received from Burkely Gallo at the Storm Prediction Center. 

###################################################################################################
# METplus Components
# ------------------
#
# This use case runs the PCPCombine, EnsembleStat, and RegridDataPlane MET tools.

###################################################################################################
# METplus Workflow
# ----------------
#
# This workflow loops over the data by process, meaning that each MET tool will run over all times
# before moving onto the tool. PCPCombine is called first, followed by EnsembleStat,
# and then, finally, RegridDataPlane.

###################################################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config. Then, it loads
# any configuration files passed to METplus by the command line with the -c option.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/EnsembleStat_fcstHRRR_fcstOnly_SurrogateSevere.conf

###################################################################################################
# MET Configuration
# -----------------
# 
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# **EnsembleStatConfig_Surrogate_severe**
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/EnsembleStatConfig_Surrogate_severe 
#
# See the following file for more information about the environment variables set in this configuration file:
#   parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.py

###################################################################################################
# Running METplus
# ---------------
#
# The command to run this use case is::
#
#    master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/EnsembleStat_fcstHRRR_fcstOnly_SurrogateSevere.conf

###################################################################################################
# Expected Output
# ---------------

# A successful run of this use case will output the following to the screen and logfile::
#  
#    INFO: METplus has successfully finished runing.
#
# A successful run will have the following output files in the location defined by {OUTPUT_BASE}, which
# is located in the metplus_system.conf configuration file located in /path/to/METplus/parm/metplus_config.
# This list of files should be found for every time run through METplus. Using the output for 20190518 as an example.
#
# **PCPCombine output**:
#
# * 20190518/hrrr_ncep_2019051800f036.nc
#
# **EnsembleStat output**:
#
# * ensemble_stat_20190519_120000V_ens.nc
#
# **RegridDataPlane output**:
# 
# * surrogate_severe_20190518_036V_regrid.nc
#

###################################################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-EnsembleStat_fcstHRRR_fcstOnly_SurrogateSevere.png'
#
# .. note:: PCPCombineUseCase, EnsembleStatUseCase, RegridDataPlaneUseCase
