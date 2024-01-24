"""
SeriesAnalysis: Standardize ensemble members and calculate probabilistic outputs
================================================================================

model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# This use case ingests a CFSv2 Ensemble forecast, with all ensemble members in a single file for a given year. 
# 29 years of forecast ensembles are used to create climatologies for each ensemble member. These climatologies
# are then used to normalize each ensemble member via the Gen-Ens-Prod tool, allowing a meaningful comparison to
# the observation dataset, which is presented as normalized. The forecast to observation verification are completed across both the temporal and spatial.
# This use case highlights several important features within METplus; in particular, how to create climatologies for ensemble members using SeriesAnalysis,
# how those climatologies can be used by GenEnsProd to normalize each ensemble member to its corresponding climatology,
# and calculating probabilistic verfication on s2s data, which is a frequent request from climatological centers.

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
# This use case initially runs SeriesAnalysis 24 times, once for each member of the CFSv2 ensemble, across the entire 29 years for forecast data.
# The resulting 24 outputs are read in by GenEnsProd, which is called 29 times (once for each year). GenEnsProd uses the **normalize** option
# and the SeriesAnalysis outputs to normalize each of the ensemble members relative to its climatology (FBAR) and standard deviation (FSTDEV).
# The output from GenEnsProd are 29 files containing the uncalibrated probability forecasts for the lower tercile of January for each year.
# The final probability verification is done across the temporal scale in SeriesAnalysis, and the spatial scale in GridStat.

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
# i.e. -c parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_wrapped
# .. literalinclude:: ../../../../parm/met_config/GenEnsProdConfig_wrapped
# .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
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
# Output for use case will be found in 4 distinct folders (relative to **OUTPUT_BASE**).
# The output from the first SeriesAnalysis call goes to **SA_run1** will contain the following files:
#
# * mem??_output.nc
#
# where ?? will be replaced by values corresponding to each of the ensemble members (0 through 23).
# The output for GenEnsProd goes into **GEP** and contains the following files:
#
# * gen_ens_prod_YYYY01_ens.nc
#
# where YYYY will be replaced by each year of the forecast data being processed (1982 through 2010).
# The output from the second SeriesAnalysis call goes to **SA_run2** and contains the following files:
#
# * 198201to201002_CFSv2_SA.nc
#
# Finally, the output from GridStat will be in **GridStat** and will contain 29 folders of the following format:
#
# * ????01
#
# where ???? will correspond to each year of the forecast data being processed (1982 through 2010).
# Each of those folders will have the following files:
#
# * grid_stat_198201_000000L_19700101_000000V_pairs.nc
# * grid_stat_198201_000000L_19700101_000000V_pstd.txt
# * grid_stat_198201_000000L_19700101_000000V.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * SeriesAnalysisUseCase
#   * GenEnsProdUseCase
#   * GridStatUseCase
#   * ProbabilityVerificationUseCase
#   * S2SAppUseCase
#   * NETCDFFileUseCase
#   * ClimatologyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.png'

