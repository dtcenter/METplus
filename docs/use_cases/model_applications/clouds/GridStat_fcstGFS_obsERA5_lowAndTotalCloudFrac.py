"""
GridStat: Cloud Fractions Using GFS and ERA5 Data
=================================================

model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.conf

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
# for low and total cloud fractions with different neighborhood
# settings for internal model metrics and to aid in future model updates



##############################################################################
# Version Added
# -------------
#
# METplus version 5.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** Global Forecast System (GFS)
#
# **Observation:** ECMWF Reanalysis, Version 5 (ERA5)
#
# **Climatology:** None
#
# **Grid:** GPP 17km masking region
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
# This use case utilizes Python Embedding, which is called using the PYTHON_NUMPY keyword 
# in the observation input template settings. The same Python script can processes both forecast and
# observation datasets, but only the observation dataset is not
# set up for native ingest by MET. Two separate forecast fields are verified against two respective observation fields,
# with the Python script being passed the input file, the model name, the variable name being analyzed,
# the initialization and valid times, and a flag to indicate if the field passed is observation or forecast.
# This process is repeated with 3 instance names to GridStat, each with a different setting for regridding,
# neighborhood evaluation, thresholding, output line types, and output prefix names.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only MET tool called in this example.
# It processes the following run time:
#
# **Init:** 2022-07-03 12Z
#
# **Forecast lead:** 36 hour
#
# Because instance names are used, GridStat will run 3 times for this 1 initalization time.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
#  i.e. parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.conf

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
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case utilizes 1 Python script to read and process the observation fields.
# parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac/read_input_data.py
# 
# .. dropdown:: parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac/read_input_data.py
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac/read_input_data.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 

##############################################################################
# User Scripting
# --------------
# [UPDATE_SECTION_CONTENT]
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.conf /path/to/user_system.conf
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
# Output for this use case will be found in {OUTPUT_BASE}/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac
# and will contain the following files::
#
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_360000L_20220705_000000V_pairs.nc
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_360000L_20220705_000000V.stat
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_NBR_360000L_20220705_000000V_pairs.nc
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_NBR_360000L_20220705_000000V.stat
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_PROB_360000L_20220705_000000V_pairs.nc
# * grid_stat_GFS_to_ERA5_F36_CloudFracs_PRB_360000L_20220705_000000V.stat


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
# sphinx_gallery_thumbnail_path = '_static/clouds-GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.png'
