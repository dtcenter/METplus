“””
    PointStat: Use Python embedding to calculate temperature terciles
    =================================================================

    model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf

“””
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# To provide statistical information on the forecast hail size compared to
# the observed hail size from MRMS MESH data. Using objects to verify hail size
# avoids the “unfair penalty” issue, where a CAM must first generate convection
# to have any chance of accurately predicting the hail size. In addition, studies
# have shown that MRMS MESH observed hail sizes do not correlate one-to-one with
# observed sizes but can only be used to group storms into general categories.
# Running MODE allows a user to do this.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
# **Forecast:** Global Forecast System (GFS) 25km resolution, 2m temperature
#
# **Observation:** ECMWF Reanalysis v5 (ERA5) 5 degree resolution, 2m temperature
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
# The only tool this use case calls is GridStat. Within GridStat a Python 
# script is used for ingesting forecast data, once for each year of data of 
# the CFSv2 ensemble.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 1982-01-01
# **End time (INIT_END):** 2010-01-02
# **Increment between beginning and end times (INIT_INCREMENT):** 1 year
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#
# With an increment of 1 year, all January 1st’s from 1982 to 2010 are processed 
# for a total of 29 years, with 24 members in each ensemble forecast. This use case 
# initially runs SeriesAnalysis 24 times, once for each member of the CFSv2 ensemble 
# across the 29 years of data. The resulting 24 outputs are read in by GenEnsProd 
# which uses the normalize option to normalize each of the ensemble members 
# relative to its climatology (FBAR) and standard deviation (FSTDEV). The output from 
# GenEnsProd are 29 files containing the uncalibrated probability forecasts for 
# the lower tercile of January for each year. The final probability verification 
# is done across the temporal scale in SeriesAnalysis, and the spatial scale in GridStat.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#

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
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls the read_ASCAT_data.py script to read and pass to PointStat 
# the user-requested variable. The script needs 5 inputs in the following order: 
# a path to a directory that contains only ASCAT data of the “ascat_YYYYMMDDHHMMSS_*” 
# string, a start time in YYYYMMDDHHMMSS, an end time in the same format, 
# a message type to code the variables as, and a variable name to read in. 
# Currently the script puts the same station ID to each observation, but there is 
# space in the code describing an alternate method that may be improved upon to 
# allow different satellites to have their own station IDs. 
# This code currently ingests all files it finds in the directory, pulls out the 
# requested variable, and arranges the data in a list of lists following the 
# 11-column format for point data. This list of lists is passed back 
# to PointStat for evaluation and the requested statistical output. The location 
# of the code is 
# parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_ 
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py

##############################################################################
# Python Scripting
# ----------------
#
# This use case uses a Python script to perform plotting, which at the time of 
# this use case creation was not an ability METplus had. Additionally some of 
# the plotting features used in this script are not currently slated for METplus 
# analysis suite development.
# In order to create the plots, the script reads in a yaml file and sets up 
# the correct environment. Plot parameters (which are hard coded in the script) are set, 
# and the datasets are read in from the input file. The desired variable fields 
# are placed into arrays, which are then treated for bad data and squeezed to the 
# appropriate dimensions. Additional basic math is completed on the resulting arrays 
# to create the cross spectra values with the results being graphed.
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired:
#
# run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in 
# {OUPUT_BASE}/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds 
# and will contain the following files::
#
#  * grid_stat_198201_000000L_19700101_000000V_pairs.nc
#  * grid_stat_198201_000000L_19700101_000000V_pstd.txt
#  * grid_stat_198201_000000L_19700101_000000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.
# For the netCDF file, five variable fields are present (not including the lat/lon fields). 
# Those variables are::
#
#  * FCST_fcst_ENS_FREQ_lt-0.43_0_0_all_all_FULL(lat, lon)
#  * OBS_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_MEAN_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_STDEV_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_CDF_tmp2m_20100101_000000_all_all_FULL(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * GRIB2FileUseCase
#   * MarineAndCryosphereAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = ‘_static/short-range-MODEMultivar_fcstRRFS_obsGOES_MRMS_BrightnessTemp_Lightning.png’
