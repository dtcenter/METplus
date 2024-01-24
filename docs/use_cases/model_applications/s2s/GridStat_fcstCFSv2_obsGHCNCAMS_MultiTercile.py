"""
GridStat: Determine dominant ensemble members terciles and calculate categorical outputs
========================================================================================

model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# This use case ingests a CFSv2 Ensemble forecast, with all ensemble members in a single file for a given year. 
# 29 years of forecast ensembles are used to create probabilities for each tercile, which is accomplished by a Python script. 
# Of the terciles, each gridpoint is assigned a value corresponding to the tercile that is most likely to occur. This is compared to an observation set
# that contains the tercile data and MCTS line type is requested.
# This use case highlights the inclusion of tercile data for calculating HSS; in particular, how to utilize the hss_ec_value option to 
# preset the expected values rather than relying on categorical values.

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** 29 CFSv2 Ensemble files, 2m temperature fields
#
# | **Observations:** GHCNCAMS, 2m temperature field
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
# This use case calls a Python script 29 times, once for each year of data of the CFSv2 ensemble.
# Each time a successful call to the script is made, a grid of 1s, 2s, and 3s is returned, representing which tercile was dominant for the gridpoint.
# GridStat processes the forecast and observation fields, and outputs the requested line types.

##############################################################################
# METplus Workflow
# ----------------
#
# This use case utilizes 29 years of forecast data, with 24 members in each ensemble forecast.
# The following boundary times are used for the entire script:
#
# | **Init Beg:** 1982-01-01
# | **Init End:** 2010-01-02
# 
# Because the increment is 1 year, all January 1st from 1982 to 2010 are processed for a total of 29 years.
# 

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf
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
# 1) Passing in GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.conf
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
# Output for the use case will be found in 29 folders(relative to **OUTPUT_BASE**).
# The output will follow the time information of the run. Specifically:
#
# * YYYY01
#
# where YYYY will be replaced by values corresponding to each of the years (1982 through 2010).
# Each of those folders will have the following files:
#
# * grid_stat_000000L_19820101_000000V_pairs.nc
# * grid_stat_000000L_19820101_000000V_mctc.txt
# * grid_stat_000000L_19820101_000000V_mcts.txt
# * grid_stat_000000L_19820101_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * ProbabilityVerificationUseCase
#   * PythonEmbeddingFileUseCase
#   * S2SAppUseCase
#   * NETCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-GridStat_fcstCFSv2_obsGHCNCAMS_MultiTercile.png'

