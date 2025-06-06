"""
GridStat: Use Python embedding to evaluate GeoTIFF imagery across multiple fields
=================================================================================

model_applications/marine_and_cryosphere/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# This use case provides an example for utilizing Python Embedding to read
# an unsupported file format into METplus and leverage the verification 
# capabilities. GeoTIFF format forecasts are read in via Python and verified against 
# the MRMS dataset, providing useful evaulation statistics for a numerical forecast that
# previously would not have been able to utilize METplus.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
# **Forecast:**  MIT-LL Global Synthetic Weather Radar (GSWR), ~0.045 degree global resolution
#
# **Observation:** MultiRadar/MultiSensor (MRMS) ~0.01 degree CONUS resolution
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
# The only tool this use case calls is GridStat, with six separate instances of GridStat used.
# Within GridStat a Python script is used for ingesting forecast data.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2024-10-15
#
# **End time (INIT_END):** 2024-10-15
#
# **Increment between beginning and end times (INIT_INCREMENT):** 15 minutes
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 60, 75, 90, 105, 120, 240, 300, 360, 420, and 480 minutes
#
# The use case runs six instances of GridStat; one for each of the three variable fields
# to be verified across the two different types of forecast files.  
# In the first GridStat call, the configuration options that will not
# change across the other instances are set, along with the initial five lead times 
# separated by 15 minute intervals. Due to the observation dataset having irregular 
# seconds attached to the valid time, the OBS_VAR1_OPTIONS sets the valid time
# equal to the valid time being verified. This will ensure that the forecast
# being evaluated is always the same valid time as the observation.
# The irregular valid time extends to the name of the observation files as well,
# so OBS_GRID_STAT_FILE_WINDOW has a +/- 120 seconds setting that will capture
# the file's slight irregular offset in seconds. Once the forecast python embedding is complete,
# the verification is completed with a regrid to the coarser forecast grid and the requested
# line type is created. The two GridStat instances containing "adv" keep the same timing information,
# changing only the observation file naming template and the corresponding
# forecast file passed to the Python script, as well as slight changes to the 
# thresholding and output location. The remaining three GridStat instances with "blend"
# need their own LEAD_SEQ, with five different lead times incremented by one hour. 
# These instances also update the observation input file templates, thresholding, and
# output location.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/short_range/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField.conf

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
# This script is necessary to read in the forecast file, which is in the unsupported
# GeoTIFF format. The only input required is a full path to the file to be evaluated,
# as each file only contains one field for analysis. After checking for exactly one input,
# two separate routines are used to extract the variable name from the filename, 
# as well as the timing information from the file name. The data from the file
# is extracted using another routine, followed by two final routines that extract the
# latitude and longitude information from the file contents and preparing the data
# to be passed back to GridStat. That final data routine also adjusts the data if 
# the variable field in the file is VIL, which requires additional steps to change
# the units to the expected kg/m^2. Any negative values are set to bad data (the negative values
# are the result of pixels with no data but bad pixel data could be seen as an actual value in MET
# if not thresholded) and finally the MET-required dictionary is constructed. 
# The location of the code is 
# 
# .. dropdown:: parm/use_cases/model_applications/short_range/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField/TIFF_readin.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField/TIFF_readin.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python Embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

##############################################################################
# User Scripting
# --------------
#
# There is no User Scripting in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in one of two directories:
#
# * advected
# * blended
#
# Under these two directories will be three subdirectories, corresponding to the 
# variable fields of interest:
#
# * echo_tops
# * vil
# * reflectivity
#
# Finally, each variable will have subdirectories corresponding to each of the leads that were
# evaluated. This should look like the following for advected:
#
# * 202410150200
# * 202410150215
# * 202410150230
# * 202410150245
# * 202410150300
#
# And for blended, the following subdirectories are present:
#
# * 202410150500
# * 202410150600
# * 202410150700
# * 202410150800
# * 202410150900
#
# Regardless of which directory is chosen, the lowest directory will contain a netCDF file 
# with the raw forecast and observation fields, and a stat file with CTS output.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * GRIB2FileUseCase
#   * ShortRangeAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-GridStat_fcstGSWR_obsMRMS_GeoTIFF_multiField.png'
