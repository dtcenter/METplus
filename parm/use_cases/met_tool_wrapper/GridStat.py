"""
GridStat
========

This use case will run the MET GridStat tool to compare gridded forecast data to
gridded observation data.

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Compare 3 hour forecast precipitation accumulations to observations
#  of 3 hour precipitation accumulation. Generate statistics of the results.

##############################################################################
# Datasets
# --------
#
# Forecast: WRF 3 hour precipitation accumulation
# Observation: MU 3 hour precipitation accumulation

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool grid_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GridStat is the only tool called in this example. It processes the following
# run times:
#
# Init: 2005-08-07_0Z Forecast lead: 12

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/GridStat.conf
#
# .. highlight:: none
# .. literalinclude:: ../../../parm/use_cases/met_tool_wrapper/GridStat.conf

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat.conf then a user-specific system configuration file
#
#   master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat.conf
#     -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat.conf
#
#   master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat.conf
#
# The former method is recommended.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile:
#
# INFO: METplus has successfully finished running.
#
# Refer to the value set for OUTPUT_BASE to find where the output data was generated.
# Output for this use case will be found in grid_stat/2005080700 (relative to OUTPUT_BASE)
# and will contain the following files:
#
#   grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V_eclv.txt
#   grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V_grad.txt
#   grid_stat_QPF_APCP_vs_QPE_APCP_03_120000L_20050807_120000V.stat

##############################################################################
# Keywords
# --------
#
# .. note:: GridStatUseCase
