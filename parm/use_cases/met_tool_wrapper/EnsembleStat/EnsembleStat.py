"""
EnsembleStat
============

This use case will run the MET EnsembleStat tool to compare gridded ensemble
forecast data to gridded AND point  observation data.

"""
##############################################################################
# Scientific Objective
# --------------------
#
# TODO Placeholder

##############################################################################
# Datasets
# --------
#
# TODO Placeholder
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus EnsembleStat wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool ensemble_stat if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# Ensemble is the only tool called in this example. It processes the following
# run times:
#
# TODO Placeholder

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/EnsembleStat.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/EnsembleStatConfig_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# TODO Placeholder
#



