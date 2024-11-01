"""

EnsembleStat: Using Python Embedding for Aerosol Optical Depth
==============================================================

model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

############################################################################
# Scientific Objective
# --------------------
#
# To provide useful statistical information on the relationship between
# observation data for aersol optical depth (AOD) to an ensemble forecast.
# These values can be used to help correct ensemble member deviations from observed values.

##############################################################################
# Version Added
# -------------
# [UPDATE_SECTION_CONTENT]
#
# METplus version 4.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** International Cooperative for Aerosol Prediction (ICAP) ensemble netCDF file, 7 members
#
# **Observation:** Aggregate netCDF file with MODIS observed AOD field
#
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus EnsembleStat wrapper to read in files using Python Embedding.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 201608150000 
# **End time (INIT_END):** 201608150000
# **Increment between beginning and end times (INIT_INCREMENT):** 06H
# **Sequence of forecast leads to process (LEAD_SEQ):** 12H
#
# EnsembleStat is the only tool called in this example. It processes a single run time with seven ensemble members.
# Three of the members do not have data for the AOD field, so EnsembleStat will only process four of the members for statistics.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: EnsembleStatConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses two Python embedding scripts to read input data.
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 
#
#
# parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/forecast_embedded.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/forecast_embedded.py
#
# parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/analysis_embedded.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod/analysis_embedded.py

##############################################################################
# User Scripting
# --------------
# [UPDATE_SECTION_CONTENT]

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired:
#
# run_metplus.py /path/to/METplus/parm/use_cases/model_applications/air_quality_and_comp/EnsembleStat_fcstICAP_obsMODIS_aod.conf -c /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in 
# {OUTPUT_BASE}/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds 
# and will contain the following files::
#
# * ensemble_stat_aod_20160815_120000V_ecnt.txt
# * ensemble_stat_aod_20160815_120000V_ens.nc
# * ensemble_stat_aod_20160815_120000V_orank.nc
# * ensemble_stat_aod_20160815_120000V_phist.txt
# * ensemble_stat_aod_20160815_120000V_relp.txt
# * ensemble_stat_aod_20160815_120000V_rhist.txt
# * ensemble_stat_aod_20160815_120000V_ssvar.txt
# * ensemble_stat_aod_20160815_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * EnsembleStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * AirQualityAndCompAppUseCase
#   * PythonEmbeddingFileUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/air_quality_and_comp-EnsembleStat_fcstICAP_obsMODIS_aod.png'
