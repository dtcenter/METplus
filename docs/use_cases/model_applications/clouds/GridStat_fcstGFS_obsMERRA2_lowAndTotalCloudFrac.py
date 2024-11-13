"""
GridStat: Cloud Fractions Using GFS and MERRA2 Data
===================================================

model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.conf

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
# METplus version 5.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** Global Forecast System (GFS)
#
# **Observations:** Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA2)
#
# **Grid:** GPP 17km masking region
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
# GridStat is the only MET tool called in this use case. 
# This use case utilizes Python Embedding, which is called using the PYTHON_NUMPY keyword 
# in the observation input template settings. The Python script is passed an input file,
# model name, variable field name being analyzed, the initialization and valid times, 
# and a flag to indicate if the field passed is observation or forecast.
# After a successful call, a MET-readable gridded observation dataset is passed back to GridStat for evaluation. 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2021070312
#
# **End time (INIT_END):** 2021070312
#
# **Increment between beginning and end times (INIT_INCREMENT):** 12H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 36
#
# Because instance names are used, GridStat will run 3 times for this 1 initalization time. Each of the 
# instance names correspond to different regridding, neighborhood evaluations, thresholding, output line types, and output
# prefix names. For the first GridStat instance, total cloud cover fraction and low cloud cover fraction are verified 
# at 10 separate thresholds. The observation dataset is provided via Python Embedding. Various output line types are requested
# and placed in stat files, with a unique output prefix indicating which output are from which GridStat instance. All of the 
# evaluation takes place within the masked region, read in via a poly line file.
# For the nbr GridStat instance, the same variables are verified, but the thresholds are expanded to include forecast 
# and observation percentiles, ranging from 20 to 80. This instance also creates 4 neighborhoods of varying width using
# a circle definition. The related neighborhood line types are requested as output and a new ouput prefix is used.
# Finally, the prob GridStat instance updates the thresholds for the two variable fields to range from 0 to 1 and 
# changes the forecast field to probabilistic space via the FCST_IS_PROB setting. Neighborhoods using the same definitions
# from the nbr instance are used, and the respective line types are requested with a new output prefix for output files
# from this instance.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.conf

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
# This use case utilizes one Python script to read and process the observation fields to become 
# METplus usable. From the configuration file it collects an input file, model name, 
# variable field name being analyzed, the initialization and valid times, 
# and a flag to indicate if the field passed is observation or forecast. Once the script runs,
# it uses the model name to extract the correct grid definition from the griddedDatasets dictionary,
# and the variable field name is used to extract the correct file variable field name (in combination
# with the name of the model) from the verifVariables dictionary. These are combined into a dictionary 
# filled with values and keys used by the rest of the code, specifically set for the model and field
# being used. A total cloud fraction call results in the field being extracted and set to a 0-100 range
# with a similar behavior for low cloud fraction. The grid type associated with each model (determined by the
# griddedDatasets dictionary) helps the script create the grid's corresponding latitude and longitude arrays.
# Finally, the valid and initialization times that were passed at runtime are used to finalize the attrs dictionary
# and the dataset is passed back to METplus for evaluation.
#
# .. dropdown:: parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac/read_input_data.py
#
#   .. highlight:: bash
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac/read_input_data.py

##############################################################################
# User Scripting
# --------------
# 
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.conf /path/to/user_system.conf
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
# Output for this use case will be found in {OUTPUT_BASE}/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac
# and will contain the following files::
#
#  * grid_stat_GFS_TO_MERRA2_F36_CloudFracs_360000L_20210705_000000V_pairs.nc
#  * grid_stat_GFS_to_MERRA2_F36_CloudFracs_360000L_20210705_000000V.stat
#  * grid_stat_GFS_to_MERRA2_F36_CloudFracs_NBR_360000L_20210705_000000V_pairs.nc
#  * grid_stat_GFS_to_MERRA2_F36_CloudFracs_NBR_360000L_20210705_000000V.stat
#  * grid_stat_GFS_to_MERRA2_F36_CloudFracs_PROB_360000L_20210705_000000V_pairs.nc
#  * grid_stat_GFS_to_MERRA2_F36_CloudFracs_PROB_360000L_20210705_000000V.stat
#
# The netCDF files from the first GridStat instance and prob instance will contain 
# the raw fields, difference fields, and gradient fields using the supplied masking area.
# For the nbr instance, there will be additional fields for the fractional coverage 
# fields. Each of the instance's output can be identified by an additional tag in the file
# name (NBR for nbr, PROB for prob, and none for the first GridStat instance). For the
# accompanying stat files, the first GridStat instance contains FHO, CTC, CTS, CNT, SL1L2, and 
# GRAD line types. The nbr instance will contain only the neighborhood-related line types
# (NBRCTC, NBRCTS, and NBRCNT). Finally, the prob GridStat instance will contain probabilistic
# line types only (PCT, PSTD, PJC, and PRC).

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
# sphinx_gallery_thumbnail_path = '_static/clouds-GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.png'
