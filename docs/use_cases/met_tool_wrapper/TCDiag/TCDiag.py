"""
TCDiag: Basic Use Case
======================

met_tool_wrapper/TCDiag/TCDiag.conf

"""
##############################################################################
# Overview
# --------------------
#
# This use case illustrates the use of tc_diag tool, which is currently
# considered a beta-level release that lacks full functionality.
# The use case illustrates running the
# tc_diag tool for a tropical cyclone forecast case and generating
# intermediate NetCDF output files of the input model's data transformed
# onto an azimuth-range grid. When the full functionality of the
# tc_diag tool is released in MET v12.0.0, this use case will be also
# output environmental diagnostics computed from callable Python scripts.
#
# The diagnostics are computed on a range-azimuth grid that follows the
# projected storm track. For inputs, it uses 0.25 deg gridded GRIB files from the
# a retrospective reforecast of the Global Forecast System Finite Volume (GFS-FV3). For the track, it uses the
# GFS-FV3's predicted track to ensure that the model's simulated storm doesn't
# contaminate the diagnostics result as a result of the model's simulated
# storm being mistaken for environmental factors. (Note:
# a future version of the tc_diag tool will include removal of the model's vortex,
# allowing diagnostics to be computed along any arbitrarily defined track.)
#

# Novel aspects of this use case:
#
# This is the first example use case to run the tc_diag tool.
# Example of running for a single tropical cyclone forecast case from
# Hurricane Matthew (2016) using GFS-FV3 data.

##############################################################################
# Scientific Objective
# --------------------
#
# Generate intermediate data files, in which the input model's data have been
# transformed to a range-azimuth grid, in preparation for further diagnostic
# calculations using Python-based routines.

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS grib files
#
# **Track:** a-deck file (Automated Tropical Cyclone Forecast System format)
#
# **Location:** All of the input data required for this use case can be found
# in the met_test sample data tarball. Click here to the METplus releases page
# and download sample data for the appropriate release:
# https://github.com/dtcenter/METplus/releases
#
# This tarball should be unpacked into the directory that you will set the
# value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# **Data source:** Users may obtain real-time data from the deterministic GFS-FV3 runs from
# NOAA's NOMADS server:
# https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.YYYYMMDD/ZZ/atmos/
# where YYYYMMDD is the date (4-digit year, 2-digit month, 2-digit day),
# ZZ is the initialization hour of the desired model cycle (00, 06, 12, 18).

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCDiag wrapper to search for
# the desired ADECK file and forecast files that are correspond to the track.
# It generates a command to run tc_diag if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# TCDiag is the only tool called in this example. It processes the following
# run times:
#
# **Init:** 2016-09-29 0000Z
# **Forecast lead:** 141, 144, and 147 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf

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
# .. note:: See the :ref:`TCDiag MET Configuration<tc-rmw-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCDiagConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf /path/to/user_system.conf
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
# Output for this use case will be found in met_tool_wrapper/TCDiag (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * tc_diag_aal142016.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCDiagToolUseCase
#   * GRIB2FileUseCase
#   * TCandExtraTCAppUseCase
#   * FeatureRelativeUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-TCDiag.png'
#
