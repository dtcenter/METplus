"""
PointStat: Met Office LFRic UGRID
====================================

model_applications/unstructured_grids/PointStat_fcstMPAS_UGRID_obsMESONET.conf

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
# This use case demonstrates the use of python embedding to ingest and perform
# verification on an MPAS unstructured grid. This foregoes the need to interpolate
# to a regular grid as a step in the verification process, thereby avoiding
# any incurred interpolation error in the process.
#
# In particular, this use case ingests a MPAS diag forecast file in
# NetCDF format, which contains data on an unstructured hexagonal mesh. The
# MET ugrid capability was designed to perform verification directly on 
# unstructured grid formats, and is employed here to ingest the file and perform
# a direct, nearest-neighbor interpolation from the native forecast grid to 
# observation locations, thereby forming matched pairs to pass to point_stat. 
#
# Observations of MESONET data are given in ASCII format, and are ingested
# using the provided python embedding script.

##############################################################################
# Version Added
# -------------
#
# METplus version 13.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** MPAS forecast files in NetCDF format
#
# **Observation:** MESONET observations in ASCII format
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
# This use case utilizes the METplus PointStat wrapper to search for
# files that are valid for the given case and generate a command to run
# the MET tool point_stat.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2025051700
#
# **End time (VALID_END):** 2025051700
#
# **Increment between beginning and end times (VALID_INCREMENT):** 6H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# PointStat is the only tool called in this example. It processes the following
# run times:
#
# | **Valid:** 2025-05-17_00Z  
# | **Forecast lead:** 06 hour

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/unstructured_grids/PointStat_fcstMPAS_UGRID_obsMESONET.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/unstructured_grids/PointStat_fcstMPAS_UGRID_obsMESONET.conf

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
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read input data.
#
# .. dropdown:: parm/use_cases/model_applications/unstructured_grids/PointStat_fcstMPAS_UGRID_obsMESONET/read_OK_mesonet.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/unstructured_grids/PointStat_fcstMPAS_UGRID_obsMESONET/read_OK_mesonet.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on
# `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/PointStat_fcstMPAS_UGRID_obsMESONET.conf /path/to/user_system.conf
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
# Output for this use case will be found in PointStat_UGRID  (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * dump.out

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase 
#   * PythonEmbeddingFileUseCase 
#   * UnstructureGridsUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/unstructured_grids-PointStat_fcstMPAS_UGRID_obsMESONET.png'
