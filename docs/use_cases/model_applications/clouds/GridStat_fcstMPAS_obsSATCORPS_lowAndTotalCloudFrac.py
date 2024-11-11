"""
GridStat: Cloud Fractions Using MPAS and SatCORPS Data
======================================================

model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.conf

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
# This use case captures various statistical measures of two model comparisons
# for low and total cloud fraction with different neighborhood and probability
# settings for internal model metrics and to aid in future model updates.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** Model for Prediction Across Scales (MPAS)
#
# **Observation:** Satellite ClOud and Radiation Property retrieval System (SatCORPS)
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
#
# **Grid:** GPP 17km masking region

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes Python Embedding, which is called using the PYTHON_NUMPY keyword 
# in the forecast and observation input template settings. The same Python script processes both forecast and
# observation datasets. Two separate forecast fields are verified against two respective observation fields,
# with the Python script being passed the input file, the model name, the variable name being analyzed,
# the initialization and valid times, and a flag to indicate if the field passed is observation or forecast.
# This process is repeated with 3 instance names to GridStat, each with a different setting for regridding,
# neighborhood evaluation, thresholding, output line types, and output prefix names.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2020072300
#
# **End time (INIT_END):** 2020072300
#
# **Increment between beginning and end times (INIT_INCREMENT):** 12H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 36
#
# GridStat is the only MET tool called in this example.
# It processes the following run time:
#
# | **Init:** 2020-07-23 00Z
# | **Forecast lead:** 36 hour
#
# Because instance names are used, GridStat will run 3 times for this 1 initalization time.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.conf

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
# .. dropdown:: GridStatConfig_wrapped
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case utilizes 1 Python script to read and process both forecast and
# observation fields.
# parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac/read_input_data.py
#
# .. dropdown:: parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac/read_input_data.py
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac/read_input_data.py

##############################################################################
# User Scripting
# --------------
#
# [UPDATE_SECTION_CONTENT]

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.conf /path/to/user_system.conf
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
# Output for this use case will be found in {OUTPUT_BASE}/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac
# and will contain the following files::
#
# * grid_stat_MPAS_F36_CloudFracs_360000L_20200724_120000V_pairs.nc
# * grid_stat_MPAS_F36_CloudFracs_360000L_20200724_120000V.stat
# * grid_stat_MPAS_F36_CloudFracs_NBR_360000L_20200724_120000V_pairs.nc
# * grid_stat_MPAS_F36_CloudFracs_NBR_360000L_20200724_120000V.stat
# * grid_stat_MPAS_F36_CloudFracs_PROB_360000L_20200724_120000V_pairs.nc
# * grid_stat_MPAS_F36_CloudFracs_PROB_360000L_20200724_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * NetCDFFileUseCase
#   * CloudsAppUseCase
#   * PythonEmbeddingFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/clouds-GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.png'
