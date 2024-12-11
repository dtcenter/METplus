"""
MODE/Grid-Stat: Brightness Temperature Verification and Distance Maps
=====================================================================

model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTempObjs.conf

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
# To provide statistical inforation on regions of low brightness temperatures, 
# defined by creating objects, in the FV3 ensemble members compared to GOES satellite. 
# In addition, distance map information is computed for both the model and observation
# using object based brightness temperatures

##############################################################################
# Version Added
# -------------
#
# METplus version 4.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** FV3 Model member data
#
# **Observation:** GOES Brightness Temperature

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MODE to create object statistics on brightness temperatures 
# below 235 K. Then it runs grid_stat to compute neighborhood contingency table
# counts and distance maps for the forecast and observations. 

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2019052100
#
# **End time (INIT_END):** 2019052100
#
# **Increment between beginning and end times (INIT_INCREMENT):** 3600
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1,2
#
# The MODE and grid_stat tools are run for each of 2 ensemble members and for each
# time. This example loops by initialization time.  It processes 2 lead times, listed 
# below.
#
# | **Valid:** 2019-05-21_01Z
# | **Forecast lead:** 01
#
# | **Valid:** 2019-05-21_02Z
# | **Forecast lead:** 02

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTempObjs.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTempObjs.conf

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
# .. dropdown:: MODEConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/MODEConfig_wrapped
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
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTempObjs.conf /path/to/user_system.conf
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
# Output for this use case will be found in short_range/brightness_temperature
# (relative to **OUTPUT_BASE**) and will contain the following files:
#
# mode/mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_cts.txt
# mode/mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.nc
# mode/mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.txt
# mode/mode_FV3_core_lsm1_010000L_20190521_010000V_NAA.ps
# mode/mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_cts.txt
# mode/mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.nc
# mode/mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.txt
# mode/mode_FV3_core_lsm1_010000L_20190521_020000V_NAA.ps
# mode/mode_FV3_core_mp1_010000L_20190521_010000V_NAA_cts.txt
# mode/mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.nc
# mode/mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.txt
# mode/mode_FV3_core_mp1_010000L_20190521_010000V_NAA.ps
# mode/mode_FV3_core_mp1_010000L_20190521_020000V_NAA_cts.txt
# mode/mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.nc
# mode/mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.txt
# mode/mode_FV3_core_mp1_010000L_20190521_020000V_NAA.ps
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_010000V_dmap.txt
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_010000V_nbrctc.txt
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_010000V_pairs.nc
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_010000V.stat
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_020000V_dmap.txt
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_020000V_nbrctc.txt
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_020000V_pairs.nc
# grid_stat_obj/grid_stat_FV3_core_lsm1_000000L_20190521_020000V.stat
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_010000V_dmap.txt
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_010000V_nbrctc.txt
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_010000V_pairs.nc
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_010000V.stat
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_020000V_dmap.txt
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_020000V_nbrctc.txt
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_020000V_pairs.nc
# grid_stat_obj/grid_stat_FV3_core_mp1_000000L_20190521_020000V.stat


##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * MODEToolUseCase
#   * GridStatToolUseCase
#   * ShortRangeAppUseCase
#   * NetCDFFileUseCase
#   * NOAAEMCOrgUseCase 
#   * NOAAHWTOrgUseCase 
#   * ValidationUseCase 
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-MODE_fcstFV3_obsGOES_BrightnessTempObjs.png'
#
