"""
PointStat: read in directory of ASCAT files over user-specified time 
====================================================================

model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To evaluate wind characteristics (direction, speed, and u/v components) from ASCAT data over water bodies, 
# Python embedding is utilized to pull user-selected variables and time frames from a runtime directory. 
# Those point values are then compared to GFS data over two masked regions over ocean regions.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** GFS forecast data for 10-m winds 
#
# | **Observations:** ASCAT METOP-B data provided by OPC
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
# PointStat kicks off a Python script execution, which reads in the entire directory passed as an arguement. 
# In the script, the directory's files are included only if they are between the times that are also passed as an arguement.
# After these points are passed back to PointStat as the point observation dataset, they are compared to gridded forecast data
# in pre-created masking regions. MCTC and MCTS line types are output, using thresholds of relevant wind speeds.
# The use case processes the following run time:
#
# | **Init:** 2023-07-06 00Z 6hr lead
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf

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
# .. note:: See the :ref:`GridStat MET Configuration<grid-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case calls the read_ASCAT_data.py script to read and pass to PointStat the user-requested variable.
# The script needs 5 inputs in the following order: a path to a directory that contains only ASCAT data of the "ascat_YYYYMMDDHHMMSS_*" string, a start time in YYYYMMDDHHMMSS,
# an end time in the same format, a message type to code the variables as (currently set for SATWND), and
# a variable name to read in. Currently the script puts the same station ID to each observation, but there is space
# in the code describing an alternate method that may be improved upon to allow different sattellites to have their own station IDs.
# The location of the code is parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds/read_ASCAT_data.py


##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds.conf /path/to/user_system.conf
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
# Output for this use case will be found in use_cases/model_applications/marine_and_cryosphere/PointStat_fcstGFS_obsASCAT_satelliteWinds (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_030000L_20221016_090000V_ctc.txt
# * point_stat_030000L_20221016_090000V_cts.txt
# * point_stat_030000L_20221016_090000V.stat
# * buoy_2022101609.nc 

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
# sphinx_gallery_thumbnail_path = '_static/marine_and_cryosphere-PointStat_fcstGFS_obsASCAT_satelliteWinds.png'

