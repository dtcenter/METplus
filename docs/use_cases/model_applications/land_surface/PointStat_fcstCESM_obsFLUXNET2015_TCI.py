"""
PointStat: CESM and FLUXNET2015 Terrestrial Coupling Index (TCI) 
======================================================================

model_applications/precipitation/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# This use case ingests two CESM (CAM and CLM) files and a new FLUX2015 dataset (NETCDF) that Paul Dirmeyer, GMU prepared from FLUXNET2015 ASCII dataset.
# The use case will calculate Terrestrial Coupling Index (TCI) from CESM datasets.
# Utilizing Python embedding, this use case taps into a new vital observation dataset and compares it to CESM simulations TCI forecast. 

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** CESM 1979-1983 Simulations a. Community Land Model (CLM) and b. Community Atmosphere Model (CAM) 
#
# | **Observations:** FLUXNET2015 post processed and converted to NETCDF. This data includes data collected from multiple regional flux towers.
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** CESM - CGD; FLUXNET2015 - Paul Dirmeyer

##############################################################################
# METplus Components
# ------------------
#
# PointStat processes the forecast and observation fields, and outputs the requested line types.

##############################################################################
# METplus Workflow
# ----------------
#
# 2 CESM files containing Soil Moisture and Sensible Heat Flux, each composed of daily forecasts from 1979 to 1983 is read by Python Embedding.
# 1 FLUXNET2015 NETCDF files containing station observations of several variables including Coupling Index of Soil Moisture and Sensible Heat Flux is read by Python Embedding.
#
# | **Valid Beg:** 1979-01-01 at 00z
# | **Valid End:** 2023-01-01 at 23z
# 
# Finally, PointStat is used to compare the two new fields (TCI calculated from CESM dataset and FLUXNET2015).
# The Valid Beg and End times are set to large range to incorporate any data available during the time frame.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/precipitation/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/precipitation/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped
# 

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in PointStat_fcstCESM_obsFLUXNET2015_TCI.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in PointStat_fcstCESM_obsFLUXNET2015_TCI::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf
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
# * PointStat
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
#   * PythonEmbeddingFileUseCase
#   * LandSurfaceAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/precipitation-PointStat_fcstCESM_obsFLUXNET2015_TCI.png'

