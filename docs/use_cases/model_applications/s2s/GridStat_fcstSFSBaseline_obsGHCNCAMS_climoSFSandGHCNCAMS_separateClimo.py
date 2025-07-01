"""
GridStat: Apply separate climatologies for forecast and observations
====================================================================

model_applications/s2s/GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo.conf

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
# During forecast verification, it is important to keep perspective of the model's
# performance relative to a reference forecast. In most use cases, this is accomplished with
# a climatology comparison; however, the climatologies applied are often from the
# observational dataset and do not provide as much insight as a climatology
# based on the forecast itself. This use case shows a basic setup using 
# ensemble-specific climatology and applying that climatology to the forecast, as
# well as a separate climatology for the observational dataset. This use case will
# be an important template for those hoping to utilize forecast climatologies within
# METplus.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# 
# **Forecast:** Seasonal Forecast System (SFS), 2m temperature
#
# **Observation:** Global Historical Climatology Network version 2 and the Climate Anomaly Monitoring System (GHCN_CAMS), 2m temperature
#
# **Climatology:** Forecast is SFS-specific, Observation is GHCN_CAMS specific. Both made outside of METplus and provided via CPC
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
# This use case calls GenEnsProd, followed by GridStat. Within GenEnsProd, an ensemble
# mean is calculated and output. This output is then read in by GridStat for
# statistical analysis. 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 1994-11-01
#
# **End time (INIT_END):** 2023-12-01
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 year
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1 month
#
# With an increment of 1 year and a lead of 1 month, all December 1st’s from 1994 to 2023 are processed 
# for a total of 30 years. For each loop of GenEnsProd, a yearly ensemble mean output
# file is created. There are 11 ensemble members in total. Afterwards, GridStat will 
# repeat the time loop, using the ensemble mean from GenEnsProd as the forecast input for each year. 
# This use case utilizes separate climatologies for the forecast and observation 
# datasets during verification and outputs the netCDF output for the raw and 
# climatology fields, as well as the CNT line type.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s/GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo.conf

##############################################################################
# MET Configuration
# -----------------
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
# .. dropdown:: GenEnsProdConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GenEnsProdConfig_wrapped
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# There is no Python Embedding used in this use case. 

##############################################################################
# User Scripting
# --------------
#
# There is no User Scripting used in this use case. 

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo.conf /path/to/user_system.conf
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
# Output for this use case will be found in 
# {OUTPUT_BASE}/model_applications/s2s/GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo 
# and will contain two separate directories. The first directory is GEP and will contain 30 ensemble mean files
# from GenEnsProd output. They should have the following naming convention::
#
#  * gen_ens_prod_YYYY11_ens.nc
#
# where each date corresponds to the initialization year and month of the model. These files
# will contain the field info fcst_0_YYYY1201_000000_all_all_ENS_MEAN, where YYYY corresponds 
# to the valid year of the forecast.
# The second directory named GridStat will have 30 subdirectories corresponding to the 
# valid time for each year in the form of::
#
#  * YYYY1201
#
# Each directory will contain two files following the convention below::
#
#  * grid_stat_SFS_verfyingWith_GHCN_CAMS_000000L_YYYY1201_000000V.stat
#  * grid_stat_SFS_verfyingWith_GHCN_CAMS_000000L_YYYY1201_000000V_pairs.nc
#
# The stat file will only contain the CNT line type, while the netCDF file will have the following
# entries::
#
#  * FCST_fcst_0_YYYY1201_000000_all_all_FULL
#  * OBS_tmp2m_YYYY1201_000000_all_all_FULL
#  * DIFF_fcst_0_YYYY1201_000000_all_all_tmp2m_YYYY1201_000000_all_all_FULL
#  * FCST_CLIMO_MEAN_tmp2m_YYYY1201_000000_all_all_FULL
#  * FCST_CLIMO_STDEV_tmp2m_YYYY1201_000000_all_all_FULL
#  * OBS_CLIMO_MEAN_tmp2m_YYYY1201_000000_all_all_FULL
#  * OBS_CLIMO_STDEV_tmp2m_YYYY1201_000000_all_all_FULL
#  * OBS_CLIMO_CDF_tmp2m_YYYY1201_000000_all_all_FULL
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GenEnsProdToolUseCase
#   * GridStatToolUseCase
#   * ClimatologyUseCase
#   * S2SAppUseCase
#   * NetCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_fcstSFSBaseline_obsGHCNCAMS_climoSFSandGHCNCAMS_separateClimo.png'
