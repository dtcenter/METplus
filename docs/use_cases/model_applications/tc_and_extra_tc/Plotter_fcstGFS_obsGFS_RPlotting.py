"""
Track and Intensity Plotter: Generate mean, median and box plots 
======================================================================================

model_applications/tc_and_extra_tc/Plotter_fcstGFS
_obsGFS_RPlotting.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# By maintaining focus of each evaluation time on a user-defined area around a cyclone,
# the model statistical errors associated with cyclonic physical features (moisture
# flux, stability, strength of upper-level PV anomaly and jet, etc.) can be related
# directly to the model forecasts and provide improvement guidance by accurately
# depicting interactions with significant weather features around and within the cyclone.
# This is in contrast to the traditional method of regional averaging cyclone observations
# in a fixed grid, which “smooths out" system features and limits the meaningful metrics
# that can be gathered. This use case relays the mean and median of forecast lead
# times for cyclone position compared to a reference dataset via boxplot.


##############################################################################
# Datasets
# --------
#
#
#  * Forecast dataset: ADeck ATCF tropical cyclone data 
#  * Observation dataset: BDeck ATCF tropical cyclone "best track" cyclone data
#

##############################################################################
# METplus Components
# ------------------
#
# This use case first runs TCPairs and then generates the requested
# plot types for statistics of interest. The TCMPRPlotterConfig_customize configuration
# file is used by the plot_tcmpr.R script to select things such as the size of
# the plot window that appears on your screen, etc.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# TCPairs > plot_tcmpr.R
#
# To generate TCPairs output, this example loops by initialization time for every 6 hour period that is available
# in the data set for 20141214. The output is then used to generate the mean, median, and box plot for the following:
# the difference between the MSLP of the Adeck and Bdeck tracks (AMSLP-BMSLP), the difference between the max wind of the Adeck and
# Bdeck tracks (AMAX_WIND-BMSLP), and the track err (TK_ERR).
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_RPlotting.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_RPlotting.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/TCPairsETCConfig
#
#
# See the following files for more information about the environment variables set in these configuration files.
#
# parm/use_cases/met_tool_wrapper/TCPairs/TCPairs.py
#
#

##############################################################################
# Running METplus
# ---------------
#
# **NOTE** - In order for this example to run successfully, ensure that your output folder ({OUTPUT_BASE}/tc_pairs/201412) is
# empty. If there are any files in this directory, the program will fail out and not produce the output for {OUTPUT_BASE}/tcmpr_plots.
#
# This use case can be run two ways:
#
# 1) Passing in Plotter_fcstGFS_obsGFS_RPlotting.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_RPlotting.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in Plotter_fcstGFS_obsGFS_RPlotting.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_RPlotting.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# TCPairs output for this use case will be found in tc_pairs/201412 (relative to **OUTPUT_BASE**)
# and will contain files with the following format:
#
# * mlq2014121400.gfso.<*nnnn*>.tcst
#
# where *nnnn* is a zero-padded 4-digit number
#
#
# Plots (in .png format) will be found in tcmpr_plots (relative to **OUTPUT_BASE**):
# * AMAX_WIND-BMAX_WIND_boxplot.png
# * AMAX_WIND-BMAX_WIND_boxplot.png
# * AMAX_WIND-BMAX_WIND_boxplot.png
# * AMSLP-BMSLP_boxplot.png
# * AMSLP-BMSLP_boxplot.png
# * AMSLP-BMSLP_boxplot.png
# * TK_ERR_boxplot.png
# * TK_ERR_mean.png
# * TK_ERR_median.png



##############################################################################
# Keywords
# --------
#
#
# .. note::
#  `TCPairsToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCPairsUseCase&check_keywords=yes&area=default>`_,
#  `TCandExtraTCAppUseCase <https://dtcenter.github.io/METplus/search.html?q=TCandExtraTCAppUseCase&check_keywords=yes&area=default>`_,
#  `FeatureRelativeUseCase  <https://dtcenter.github.io/METplus/search.html?q=FeatureRelativeUseCase&check_keywords=yes&area=default>`_,
#  `MediumRangeAppUseCase <https://dtcenter.github.io/METplus/search.html?q=MediumRangeAppUseCase&check_keywords=yes&area=default>`_,
#  `SBUOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=SBUOrgUseCase&check_keywords=yes&area=default>`_,
#  `DTCOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=DTCOrgUseCase&check_keywords=yes&area=default>`_

# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-Plotter_fcstGFS_obsGFS_RPlotting.png'
