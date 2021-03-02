"""
Ensemble-Stat: Basic Post-Processing only  
================================================================

model_application/precipitation/EnsembleStat_fcstHRRRE
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
# This use case runs Ensemble-Stat on HRRRE data from 3 members after
# running it through pcp_combine to create a 3 hour precipitation accumulation

###############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
# EnsembleStat
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
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf

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
# .. note:: See the :ref:`EnsembleStat MET Configuration<ens-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf
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
# Output for this use case will be found in model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF/EnsembleStat (relative to **OUTPUT_BASE**)
# The following folder/file combination will be created:
#
# -201905191200
#
# * ensemble_stat_APCP_03_20190519_150000V_ens.nc
# * ensemble_stat_APCP_03_20190519_180000V_ens.nc
# * ensemble_stat_APCP_03_20190519_210000V_ens.nc
# * ensemble_stat_APCP_03_20190520_000000V_ens.nc
#
# -201905200000
#
# * ensemble_stat_APCP_03_20190520_030000V_ens.nc
# * ensemble_stat_APCP_03_20190520_060000V_ens.nc
# * ensemble_stat_APCP_03_20190520_090000V_ens.nc
# * ensemble_stat_APCP_03_20190520_120000V_ens.nc


##############################################################################
# Keywords
# --------
#
# .. note::
#    `EnsembleStatToolUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleStatToolUseCase&check_keywords=yes&area=default>`_,
#    `NOAAHWTOrgUseCase  <https://dtcenter.github.io/METplus/search.html?q=NOAAHWTOrgUseCase&check_keywords=yes&area=default>`_,
#    `PrecipitationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=PrecipitationAppUseCase&check_keywords=yes&area=default>`_,
#    `NetCDFFileUseCase  <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&check_keywords=yes&area=default>`_,
#    `EnsembleAppUseCase <https://dtcenter.github.io/METplus/search.html?q=EnsembleAppUseCase&check_keywords=yes&area=default>`_,
#    `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#    `ProbabilityGenerationAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ProbabilityGenerationAppUseCase&check_keywords=yes&area=default>`_,
#    `ListExpansionFeatureUseCase <https://dtcenter.github.io/METplus/search.html?q=ListExpansionFeatureUseCase&check_keywords=yes&area=default>`_

# sphinx_gallery_thumbnail_path = '_static/precipitation-EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.png'
