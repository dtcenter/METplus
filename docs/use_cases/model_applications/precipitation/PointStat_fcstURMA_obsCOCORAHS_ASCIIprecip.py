"""
PointStat: Compare community observed precipitation to model forecasts
======================================================================

model_applications/precipitation/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# This use case ingests a CoCoRaHS csv file, a new dataset that utilizes community reporting of precipitation amounts.
# Numerous studies have shown that a community approach to weather observations not only covers areas that lack traditional verification datasets,
# but is also remarkably quality controlled. 
# Utilizing Python embedding, this use case taps into a new vital observation dataset and compares it to a 24 hour precipitation accumulation forecast. 

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** 24 URMA 1 hour precipitation accumulation files
#
# | **Observations:** CoCoRaHS, the Community Collaborative Rain, Hail, and Snow Network
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** EMC

##############################################################################
# METplus Components
# ------------------
#
# This use case calls a Python script in ASCII2NC for the observation dataset.
# PCPCombine is called for a user-defined summation of the forecast accumulation fields.
# Finally, PointStat processes the forecast and observation fields, and outputs the requested line types.

##############################################################################
# METplus Workflow
# ----------------
#
# 1 csv file of multiple valid observation times is passed to ASCII2NC via Python embedding, resulting in a netCDF output.
# 24 forecast files, each composed of 1 hour precipitation accumulation forecasts, is summarized via PCPCombine.
# The following boundary times are used for the forecast summation times:
#
# | **Valid Beg:** 2022-09-14 at 00z
# | **Valid End:** 2022-09-14 at 23z
# 
# The observation data point span the same times as the 24 hour forecast accumulation summation.
# Finally, PointStat is used to compare the two new fields (point data in netCDF and precipitation accumulation over 24 hours).
# Because the Valid Time used in configuration file is set to one time (2022-09-14 at 23z) and the precipitation accumulation valid time is set to this same time, 
# the observation window spans across the entire 2022-09-14 24 hour timeframe.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/precipitation/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
# .. literalinclide:: ../../../../parm/met_config/PointStatConfig_wrapped
# 

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/precipitation/PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [config]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
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
# Output for the use case will be found in 3 folders(relative to **OUTPUT_BASE**).
# Those folders are:
#
# * ASCII2NC
# * PCPCombine
# * PointStat
#
# The ASCII2NC folder will contain one file from the ASCII2NC tool call:
#
# * precip_20220914_summary.nc
#
# The PCPCombine folder will also contain one file, from the PCPCombine call:
#
# * fcst_24hr_precip.nc
#
# The final folder, PointStat, contains all of the following output from the PointStat call:
#
# * point_stat_000000L_20220914_230000V_cnt.txt
# * point_stat_000000L_20220914_230000V_ctc.txt
# * point_stat_000000L_20220914_230000V_cts.txt
# * point_stat_000000L_20220914_230000V_mcts.txt
# * point_stat_000000L_20220914_230000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * ASCII2NCToolUseCase
#   * PCPCombineToolUseCase
#   * PythonEmbeddingFileUseCase
#   * PrecipitationAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-PointStat_fcstURMA_obsCOCORAHS_ASCIIprecip.png'

