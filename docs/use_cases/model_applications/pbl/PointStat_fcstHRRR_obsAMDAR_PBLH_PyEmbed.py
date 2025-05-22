"""
Point-Stat: Computing PBLH from AMDAR data using two methods: Theta-increase, Critical Bulk Richardson Number
======================================================================================

model_applications/pbl/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.conf

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
# The Planetary Boundary Layer Height (PBLH) arises from a complex interaction of 
# lower atmosphere and surface processes, and is therefore a useful metric to
# evaluate models. This PointStat use case computes PBLH from AMDAR aircraft data
# for 71 airports specified in a csv file using two methods: 1) "Theta-increase" 
# method (Nielsen-Gammon et al., 2008, J. App. Met. Clim.), which computes PBLH 
# by finding the lowest altitude in an aircraft profile that exceeds a specified 
# increase in potential temperature from a base value. This theta-increase (pt_delta)
# value is set to 1.25 K, which is the same as the HRRR model. 2) "Critical Bulk 
# Richardson Number" method (Seidel et al., 2012, JGR), which computes PBLH by finding
# the lowest altitude in an aircraft profile which exceeds a Critical Bulk Richardson
# Number. The name of the airport list csv file and the sounding are specified in the
# configuration script.
# 

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** NOAA High Resolution Rapid Refresh (HRRR)
#
# **Observation:** AMDAR hourly 1-d netcdf files
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
# This use case utilizes the METplus PointStat tool to compare PBLH 
# from AMDAR data to model output. The python embedding script "calc_amdar_pblh.py" 
# computes PBLH and sends data MET via python embedding. 
 
##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2022070108
#
# **End time (INIT_END):** 2022070108
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1H
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 12
#
# PointStat is called in this example. The following run times are processed:
#
# | **Valid:** 2022-07-01_20Z
# | **Forecast lead:** 12 hour
#
# PointStat is run with Python embedding (calc_amdar_pblh.py).
# The Python embedding script calls an airport csv file.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/pbl/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/pbl/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.conf

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
# .. dropdown:: parm/use_cases/model_applications/pbl/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed/calc_amdar_pblh.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/pbl/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed/calc_amdar_pblh.py
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
#   run_metplus.py /path/to/PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.conf /path/to/user_system.conf
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
# Output for this use case will be found in point_stat_pblh  (relative to **OUTPUT_BASE**)
# with subdirectories for valid time (YYYYMMDD) and will contain .stat files with the following naming convention:
#
# convention: point_stat_{SOUNDING_FLAG}_{LEADTIME}L_{VALIDTIME}.stat
#    example: point_stat_ALL_120000L_20220701_200000V.stat

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase 
#   * PythonEmbeddingFileUseCase 
#   * PBLAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/pbl-PointStat_fcstHRRR_obsAMDAR_PBLH_PyEmbed.png'
