"""
GridStat: GFS Cloud Pressure and Temperature Heights vs GOES
============================================================

model_applications/clouds/GridStat_fcstGFS_obsGOES_cloudTopPressAndTemp.conf

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
# This use case demonstrates using GOES-16 or GOES-18 level 2 cloud products 
# to verify forecasts of cloud top information.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# **Forecast:** Global Forecast System (GFS) global 0.25 degree grid
#               Cloud top temperature and cloud top pressure
#
# **Observation:** GOES-16 or GOES-18 level 2 cloud products 
#                  Cloud top temperature and cloud top pressure
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
# This use case uses Point2Grid to place the point observations from GOES onto the GFS grid, 
# then uses GridStat for evaluation.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2024-03-07 00:00
#
# **End time (INIT_END):** 2024-03-07 00:00
#
# **Increment between beginning and end times (INIT_INCREMENT):** None
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 6
#
# Instance names are used in this use case, so both Point2Grid and GridStat will run 
# twice for each initialization time. Each of the instance names refers to the temperature 
# observation variable (ACHTF) or the pressure observation variable (CTPC). 
# This use case first runs the ACHTF Point2Grid instance to put cloud top temperature point 
# observations on to a grid, then it runs the CTPC Point2Grid instance to put cloud top pressure 
# point observations on a grid. Then it runs the ACHTF GridStat instance to verify 
# cloud top temperature, and lastly, it runs the CTPC GridStat instance to verify cloud top pressure. 
# Various output line types are requested and placed in stat files, with a unique output prefix 
# indicating which output are from which GridStat instance.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGOES_cloudTopPressAndTemp.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGOES_cloudTopPressAndTemp.conf

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
# .. dropdown:: Point2GridConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/Point2GridConfig_wrapped
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case does not use additional scripts.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/clouds/GridStat_fcstGFS_obsGOES_cloudTopPressAndTemp.conf /path/to/user_system.conf
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
#
# Output from Point2Grid will be found in:
# {OUTPUT_BASE}/model_applications/clouds/Point2Grid/goes[16/18] and will contain the following files::
#
#  * OR_ABI-L2-ACHTF_s2024030706.nc
#  * OR_ABI-L2-CTPC_s2024030706.nc
#
# Output from GridStat will be found in:
# {OUTPUT_BASE}/model_applications/clouds/GridStat/goes[16/18] and will contain the following files::
#
#  * grid_stat_GFS_vs_ACHTF_060000L_20240307_060000V_ctc.txt
#  * grid_stat_GFS_vs_ACHTF_060000L_20240307_060000V_cts.txt
#  * grid_stat_GFS_vs_ACHTF_060000L_20240307_060000V_pairs.nc
#  * grid_stat_GFS_vs_ACHTF_060000L_20240307_060000V.stat
#  * grid_stat_GFS_vs_CTPC_060000L_20240307_060000V_ctc.txt
#  * grid_stat_GFS_vs_CTPC_060000L_20240307_060000V_cts.txt
#  * grid_stat_GFS_vs_CTPC_060000L_20240307_060000V_pairs.nc
#  * grid_stat_GFS_vs_CTPC_060000L_20240307_060000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * Point2GridToolUseCase
#   * CloudsAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#

# sphinx_gallery_thumbnail_path = '_static/clouds-GridStat_fcstGFS_obsGOES_cloudTopPressAndTemp.png'
