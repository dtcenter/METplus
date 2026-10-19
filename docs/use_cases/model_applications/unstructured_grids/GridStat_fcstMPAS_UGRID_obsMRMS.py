"""
GridStat: MPAS UGRID
====================================

model_applications/unstructured_grids/GridStat_fcstMPAS_UGRID_obsMRMS.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

###########################################
# Scientific Objective
# --------------------
#
# This use case demonstrates verification on an unstructured grid MPAS grid.
# This foregoes the need for multiple interpolations: to a regular grid for
# model post-processeing, and then either the forecast, the observations,
# or both to a common grid. Instead, this use case uses a single interpolation,
# yielding the forecast data on the observation grid. This avoids any additional
# incurred interpolation errors.
#
# In particular, this use case ingests a MPAS diag forecast file in
# NetCDF format, which follows the UGRID format and containing a regional
# hexagonal grid. The demonstrated case is a small 12km domain over Oklahoma.
# Observations used are MRMS files, allowing for verification of reflectivity
# data in the MPAS forecast. In this use case, the MRMS files were reduced 
# using wgrib2 from the complete MRMS domain to one immediately surrounding 
# the forecast domain to facilitate shorter runtimes.

##############################################################################
# Version Added
# -------------
#
# METplus version 13.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** MPAS diag files containing hexagonal gridded data in NetCDF format
#
# **Observation:** MRMS Reflectivity data in grib2 format
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
# This use case utilizes the METplus GridStat wrapper to search for
# files that are valid for the given case and generate a command to run
# the MET tool grid_stat.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2025051900
#
# **End time (VALID_END):** 2025051906
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0,1,2,3,4,5,6
#
# GridStat is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2025-05-19_00Z to  2025-05-19_06Z 
# | **Forecast lead:** 00 to 06 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/unstructured_grids/GridStat_fcstMPAS_UGRID_obsMRMS.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/unstructured_grids/GridStat_fcstMPAS_UGRID_obsMRMS.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GridStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/GridStat_fcstMPAS_UGRID_obsMRMS.conf /path/to/user_system.conf
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
# Output for this use case will be found in OK_12km_ugrid/grid_stat  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * grid_stat_0H0000L_20250519_0H0000V_pairs.nc
# * grid_stat_0H0000L_20250519_0H0000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridStatToolUseCase 
#   * UnstructuredGridUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/unstructured_grids-GridStat_fcstMPAS_UGRID_obsMRMS.png'
