"""
PointStat: read in satellite data and verify wind speeds or wave heights 
========================================================================

model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Satellite data provides a wealth of information, especially over vast water bodies (eg. oceans)
# where traditional observation methods are sparse or unavailable. This use case shows how a satellite
# dataset can be used as observations to verify against a model forecast. While the use case is set
# up to verify using JASON-3 data, the Python script called on via Python Embedding is capabile
# of processing SARAL and Sentinel-6a datasets as well.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS forecast data (wind speed and sig. wave hgt)
#
# | **Observations:** JASON-3 satellite data
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls Python Embedding during PointStat, which is the only tool used. 
#

##############################################################################
# METplus Workflow
# ----------------
#
# PointStat kicks off a Python script execution, which reads in the file name, variable field of interest, and type of file (JASON, SARAL, or SENTINEL). 
# After these points are passed back to PointStat as the point observation dataset, they are compared to gridded forecast data. 
# CTC and CTS line types are output, which can be adjusted for additional wind speeds/ wave heights.
# The use case processes the following run time:
#
# | **Valid:** 2024-01-02 12Z 12hr lead
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. note:: See the :ref:`PointStat MET Configuration<point-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls the read_satData.py script to read and pass to PointStat the user-requested variable.
# The script needs 3 inputs in the following order: an input file, a variable field to extract,
# and where the data came from, passed as JASON (JASON-3), SARAL, or SENTINEL (Sentinel-6a).
# The location of the code is parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry/read_satData.py
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry/read_satData.py


##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsJASON3_satelliteAltimetry (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_swh_120000L_20240102_120000V.stat
# * point_stat_wind_120000L_20240102_120000V.stat

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
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-PointStat_fcstGFS_obsJASON3_satelliteAltimetry.png'

