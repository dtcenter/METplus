"""
Gen-Ens-Prod: Basic Post-Processing only
========================================

model_application/precipitation/GenEnsProd_fcstHRRRE
_FcstOnly_NetCDF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Post-process ensemble members to derive simple (non-bias-corrected) mean,
# standard deviation (spread), minimum, maximum, and range fields for use in
# other MET tools.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HRRRE 3 member ensemble netcdf 3 hour precipitation accumulation
#

###############################################################################
# METplus Components
# ------------------
#
# This use case runs gen_ens_prod on HRRRE data from 3 members after
# running it through pcp_combine to create a 3 hour precipitation accumulation

###############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# GenEnsProd
#
# This example loops by initialization time. For each initialization time
# it will process forecast leads 3, 6, 9 and 12
#
# Run times:
#
# | **Init:** 2019-05-19_12Z
# | **Forecast lead:** 3
#
# | **Init:** 2019-05-19_12Z
# | **Forecast lead:** 6
#
# | **Init:** 2019-05-19_12Z
# | **Forecast lead:** 9
#
# | **Init:** 2019-05-19_12Z
# | **Forecast lead:** 12
#
# | **Init:** 2019-05-20_00Z
# | **Forecast lead:** 3
#
# | **Init:** 2019-05-20_00Z
# | **Forecast lead:** 6
#
# | **Init:** 2019-05-20_00Z
# | **Forecast lead:** 9
#
# | **Init:** 2019-05-20_00Z
# | **Forecast lead:** 12
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configurations found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/GenEnsProd_fcstHRRRE_FcstOnly_NetCDF.conf

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
# .. note:: See the :ref:`GenEnsProd MET Configuration<gen-ens-prod-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GenEnsProdConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# The command to run this use case is::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/GenEnsProd_fcstHRRRE_FcstOnly_NetCDF.conf
#
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
# Output for this use case will be found in model_applications/precipitation/GenEnsProd_fcstHRRRE_FcstOnly_NetCDF/GenEnsProd (relative to **OUTPUT_BASE**)
# The following folder/file combination will be created:
#
# -201905191200
#
# * gen_ens_prod_APCP_03_20190519_150000V_ens.nc
# * gen_ens_prod_APCP_03_20190519_180000V_ens.nc
# * gen_ens_prod_APCP_03_20190519_210000V_ens.nc
# * gen_ens_prod_APCP_03_20190520_000000V_ens.nc
#
# -201905200000
#
# * gen_ens_prod_APCP_03_20190520_030000V_ens.nc
# * gen_ens_prod_APCP_03_20190520_060000V_ens.nc
# * gen_ens_prod_APCP_03_20190520_090000V_ens.nc
# * gen_ens_prod_APCP_03_20190520_120000V_ens.nc


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GenEnsProdToolUseCase
#   * NOAAHWTOrgUseCase
#   * PrecipitationAppUseCase
#   * NetCDFFileUseCase
#   * EnsembleAppUseCase
#   * ConvectionAllowingModelsAppUseCase
#   * ProbabilityGenerationAppUseCase
#   * ListExpansionFeatureUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-GenEnsProd_fcstHRRRE_FcstOnly_NetCDF.png'
#
