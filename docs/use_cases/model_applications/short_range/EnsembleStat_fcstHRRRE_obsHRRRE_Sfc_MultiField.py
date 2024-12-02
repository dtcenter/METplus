"""
Ensemble-Stat: Ensemble Statistics using Obs Uncertainty 
========================================================

model_applications/short_range/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf

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
# To provide useful statistical information about the ensemble characteristics
# such as how dispersive it is and the relationship between spread and skill.
# This example also shows how to compute simple probability fields called
# ensemble relative frequency.

##############################################################################
# Version Added
# -------------
#
# METplus version 3.0

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
# 
#  * Forecast dataset: HRRRE data
#  * Observation dataset: HRRRE data
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs PB2NC on the prepBUFR observation data to convert it into
# NetCDF format so it can be read by MET. Then EnsembleStat is run.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# PB2NC > EnsembleStat
#
# This example loops by initialization time. For each initialization time
# it will process forecast leads 0, 1, and 2. There is only one
# initialization time in this example, so the following will be run:
#
# Run times:
#
# | **Init:** 2018-07-09_12Z
# | **Forecast lead:** 0
#
# | **Init:** 2018-07-09_12Z
# | **Forecast lead:** 1
#
# | **Init:** 2018-07-09_12Z
# | **Forecast lead:** 2
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/short_range/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf

##############################################################################
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
# .. dropdown:: EnsembleStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/short_range/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField/EnsembleStat/201807091200 (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_ecnt.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_ens.nc
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_orank.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_phist.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_relp.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_rhist.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V_ssvar.txt
# * ensemble_stat_HRRRE_F000_ADPSFC_20180709_120000V.stat
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_ecnt.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_ens.nc
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_orank.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_phist.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_relp.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_rhist.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V_ssvar.txt
# * ensemble_stat_HRRRE_F001_ADPSFC_20180709_130000V.stat
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_ecnt.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_ens.nc
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_orank.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_phist.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_relp.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_rhist.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V_ssvar.txt
# * ensemble_stat_HRRRE_F002_ADPSFC_20180709_140000V.stat
#


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * EnsembleStatToolUseCase 
#   * ShortRangeAppUseCase
#   * PB2NCToolUseCase
#   * prepBUFRFileUseCase
#   * GRIB2FileUseCase
#   * NCAROrgUseCase 
#   * EnsembleAppUseCase
#   * ProbabilityGenerationUseCase
#   * NOAAGSLOrgUseCase 
#   * DTCOrgUseCase 
#   * ObsUncertaintyUseCase
#   * MaskingFeatureUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.png'
