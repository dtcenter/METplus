"""
GridStat: Verifying Soil moisture of SFS-GSL output against ERA5 and compute categorical statistics
========================================================================================

model_applications/s2s/GridStat_fcstSFSGSL_obsERA_SoilMoisture.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# This use case ingests 30 SFS-GSL Ensemble forecast of Soil Moisture, with all ensemble members in a single file for a given year and month (here June). 
# The python embedding script computes an ensemble mean for the given month. 
# The ensemble mean is compared to ERA5 dataset.
# The post-processed ERA5 data contains 30 years of monthly Soil Moisture data at 1 degree resolution.
# This use case verifies soil moisture of SFS-GSL model against ERA5 analysis. 

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** 30 SFS-GSL Ensemble files, 0-1m Soil Moisture fields Units: mm
#
# | **Observations:** post processed ERA5, 0-1m Soil Moisture field Units: mm
#
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** CPC

##############################################################################
# METplus Components
# ------------------
#
# This use case calls a Python script 30 times, once for each year of data of the SFS-GSL ensemble.
# GridStat processes the forecast and observation fields, and outputs the requested line types.

##############################################################################
# METplus Workflow
# ----------------
#
# This use case utilizes 30 years of forecast data, with 5 members in each ensemble forecast.
# The following boundary times are used for the entire script:
#
# | **Init Beg:** 1991-06-00
# | **Init End:** 2020-06-00
# 
# Because the increment is 1 year, all June 1st from 1991 to 2020 are processed for a total of 30 years.
# 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/s2s/GridStat_fcstSFSGSL_obsERA_SoilMoisture.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStat_fcstSFSGSL_obsERA_SoilMoisture.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in GridStat_fcstSFSGSL_obsERA_SoilMoisture.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstSFSGSL_obsERA_SoilMoisture /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstSFSGSL_obsERA_SoilMoisture::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstSFSGSL_obsERA_SoilMoisture.conf
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
# Output for the use case will be found in 30 folders(relative to **OUTPUT_BASE**).
# The output will follow the time information of the run. Specifically:
#
# * YYYY060100
#
# where YYYY will be replaced by values corresponding to each of the years (1991 through 2020).
# Each of those folders will have the following files:
#
# * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_fho.txt
# * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V_pairs.nc 
# * grid_stat_SFS-GSL_vs_ERA5_060000L_YYYY0601_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * S2SAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_fcstSFSGSL_obsERA_SoilMoisture.png'

