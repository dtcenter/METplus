"""
PointStat: CESM and FLUXNET2015 Terrestrial Coupling Index (TCI) 
======================================================================

model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf

"""
##############################################################################
# .. contents::
#    :depth: 1
#    :local:
#    :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# This use case ingests two CESM (CAM and CLM) files and raw FLUXNET2015 data.
# The use case calculates the Terrestrial Coupling Index (TCI) from the CESM forecasts and FLUXNET observations.
# Utilizing Python embedding, this use case taps into a new vital observation dataset and compares it to CESM forecasts of TCI. 
# Finally, it will generate plots of model forecast TCI overlaid with TCI observations at FLUXNET sites.
#
# The reference for the Terrestrial Coupling Index calculation is as follows:
#
# Dirmeyer, P. A., 2011: The terrestrial segment of soil moisture-climate coupling. *Geophys. Res. Lett.*, **38**, L16702, doi: 10.1029/2011GL048268.
#

##############################################################################
# Datasets
# ---------------------
#
# | **Forecast:** CESM 1979-1983 Simulations 
# | * Community Land Model (CLM) file
# | * Community Atmosphere Model (CAM) file
#
# | **Observations:** Raw FLUXNET2015 observations
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** CESM - NSF NCAR Climate & Global Dynamics (CGD); FLUXNET2015 "SUBSET" Data Product: https://fluxnet.org/data/fluxnet2015-dataset/subset-data-product/
#

##############################################################################
# Python Dependencies
# ---------------------
#
# This use case requires the following Python dependencies::
#
# * Xarray
# * Pandas
# * METcalcpy 3.0.0+
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PyEmbedIngest to read the CESM files and calculate TCI using python embedding and a NETCDF file of the TCI is generated. 
# The METplus PointStat processes the output of PyEmbedIngest and FLUXNET2015 dataset (using Python embedding), and outputs the requested line types.
# Then the METplus PlotPointObs tool reads the output of PyEmbedIngest and FLUXNET2015 dataset and produce plots of TCI from CESM and point observations.
# A custom loop runs through all the pre-defined seasons (DJF, MAM, JJA, SON) and runs PyEmbedIngest, PointStat, and PlotPointObs.
#

##############################################################################
# METplus Workflow
# ----------------
#
# The PyEmbedIngest tool reads 2 CESM files containing Soil Moisture (CLM file) and Sensible Heat Flux (CAM file), each composed of daily forecasts from
# 1979 to 1983 and calculates TCI and generates a NETCDF file of the TCI. Raw CSV files containing FLUXNET station observations of latent heat flux (LE_F_MDS)
# and soil water content at the shallowest level (SWC_F_MDS_1) are read using Python embedding, and TCI is computed.
# 
# | **Valid Beg:** 1979-01-01 at 00z
# | **Valid End:** 1979-01-01 at 00z
#
# PointStat is used to compare the two new fields (TCI calculated from CESM dataset and FLUXNET2015).
# Finally, PlotPointObs is run to plot the CESM TCI overlaying the FLUXNET2015 point observations.
#
# .. note::
# 
#   The CESM forecasts cover a time period prior to the availability of FLUXNET observations. Thus,
#   this use case should be considered a demonstration of the capability to read CESM forecast data, 
#   raw FLUXNET observation data, and compute TCI, rather than a bonafide scientific application.
#   The use case is designed to enforce seasonal alignment, but it is not designed to enforce date/time alignment. 
#   In this case, the CESM data cover 1979-1983, whereas the sample FLUXNET observations cover varying time ranges depending on the site.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. -c parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf
#

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on the values in the METplus configuration file. These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the ‘User Defined Config’ section on the ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read both the forecast and observation data, in order to compute TCI,
# which is the diagnostic that is being verified by MET using PointStat. The CESM forecast data is read using:
#
# parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI/cesm_tci.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI/cesm_tci.py
#
# The user can control all arguments to this script via the METplus use case configuration file using the following config entries:
#
# .. glossary::
# 
#    CESM_CAM_VAR
#      The CESM Community Atmosphere Model variable to use for computing TCI
#
#      | *Default:* LHFLX
#
#    CESM_CLM_VAR
#      The CESM Community Land Model variable to use for computing TCI
#
#      | *Default:* SOILWATER_10CM
#
#    CESM_CAM_FILE_PATH
#      The absolute path to the CESM Community Atmosphere Model netcdf file
#
#      | *Default:*
#
#    CESM_CLM_FILE_PATH
#      The absolute path to the CESM Community Land Model netcdf file
#
#      | *Default:*
#
# The raw FLUXNET2015 SUBSET data are read using:
#
# parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI/fluxnet2015_tci.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI/fluxnet2015_tci.py
#
# The user can control all command line arguments to this script via METplus config entries:
#
# .. glossary::
#
#    FLUXNET_DATA_DIR
#      The directory containing raw FLUXNET CSV files
#
#      | *Default:*
#
#    FLUXNET_LAT_HEAT_VAR
#      The FLUXNET surface latent heat flux variable name to use for computing TCI
#
#      | *Default:* LE_F_MDS
#
#    FLUXNET_SOIL_MOIST_VAR
#      The FLUXNET soil moisture variable name to use for computing TCI
#
#      | *Default:* SWC_F_MDS_1
#
#    FLUXNET_OBS_METADATA_FILE
#      The absolute path to the fluxnetstations.csv metadata file included with the use case
#
#      | *Default:*
#
# and for data filtering options, via METplus config entries:
#
# .. glossary::
#
#    FLUXNET_SKIP_LEAP_DAYS
#      Skip FLUXNET observations from 29 February days
#
#      | *Default:* True
#
#    FLUXNET_HIGHRES_QC_THRESH
#      The fraction of higher temporal resolution FLUXNET data required to have
#      passed quality control in order to use the daily data.
#
#      | *Default:* 0.8
#
#    FLUXNET_MIN_DAYS_PER_SEASON
#      The minimum number of days to include in individual seasons at each site
#
#      | *Default:* 1
#
#    FLUXNET_MIN_DAYS_PER_SITE
#      The minimum number of days for all seasons at each site
#
#      | *Default:* 10
#
#    FLUXNET_RAW_FILENAME_PATTERN
#      A filename pattern matching the template of the raw FLUXNET CSV files
#
#      | *Default:* FLX_*_DD_*.csv
#
#    FLUXNET_DEBUG
#      Turn on additional print statements from the Python embedding script
#
#      | *Default:* False
#
# Both of the above Python embedding scripts compute TCI using the ``calc_tci()`` function in METcalcpy. See the METcalcpy 
# documentation for more information: https://metcalcpy.readthedocs.io/en/latest/index.html.
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land_surface/PointStat_fcstCESM_obsFLUXNET2015_TCI.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
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
# * PyEmbedIngest
#
# The **OUTPUT_BASE** folder contains all of the TCI output calculated using CESM files in NETCDF format:
#
# * regrid_data_plane_DJF.nc
# * regrid_data_plane_JJA.nc
# * regrid_data_plane_MAM.nc
# * regrid_data_plane_SON.nc
#
# * PointStat
#
# The final folder, PointStat, contains all of the following output from the PointStat call:
#
# * point_stat_DJF_000000L_19790101_000000V_cnt.txt
# * point_stat_DJF_000000L_19790101_000000V_ctc.txt
# * point_stat_DJF_000000L_19790101_000000V_mpr.txt
# * point_stat_DJF_000000L_19790101_000000V.stat
# * point_stat_JJA_000000L_19790101_000000V_cnt.txt
# * point_stat_JJA_000000L_19790101_000000V_ctc.txt
# * point_stat_JJA_000000L_19790101_000000V_mpr.txt
# * point_stat_JJA_000000L_19790101_000000V.stat
# * point_stat_MAM_000000L_19790101_000000V_cnt.txt
# * point_stat_MAM_000000L_19790101_000000V_ctc.txt
# * point_stat_MAM_000000L_19790101_000000V_mpr.txt
# * point_stat_MAM_000000L_19790101_000000V.stat
# * point_stat_SON_000000L_19790101_000000V_cnt.txt
# * point_stat_SON_000000L_19790101_000000V_ctc.txt
# * point_stat_SON_000000L_19790101_000000V_mpr.txt
# * point_stat_SON_000000L_19790101_000000V.stat
#
# * PlotPointObs
#
# The final folder plot_point_obs, contains all of the plots from the PlotPointObs call:
#
# * cesm_fluxnet2015_DJF.ps
# * cesm_fluxnet2015_JJA.ps
# * cesm_fluxnet2015_MAM.ps
# * cesm_fluxnet2015_SON.ps
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PyEmbedIngestToolUseCase
#   * PointStatToolUseCase
#   * PlotPointObsToolUseCase
#   * PythonEmbeddingFileUseCase
#   * NETCDFFileUseCase
#   * LandSurfaceAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/land_surface-PointStat_fcstCESM_obsFLUXNET2015_TCI.png'

