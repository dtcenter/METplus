"""
PointStat: Use Python embedding and METcalcpy to calculate and verify CTP/HI
============================================================================

model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI.conf

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
# This use case examines short-term land-atmosphere coupling within the UFS global forecast system (GFS).
# The specific configuration is a GFSv17 pre-release version (HR1).  Land-atmosphere coupling is 
# important for many processes, such as prediction of convection, convective clouds, as well as near surface 
# sensible weather (e.g. winds, humidity, temperature).  Here the CTP-HI process diagnostic uses morning 
# surface and lower atmosphere conditions to assess the convective coupling in wet or dry coupling phases.
# This permits further assessment of the model near surface and lower atmosphere biases in an integrated 
# phase space, using CTP versus HI.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** Global Forecast System (GFS) version 17 prototype.
# Global 1-degree grid including temperature, specific humidity, and pressure.
#
# **Observation:** Upper air radiosonde observations from the 
# Global Data Assimilation System (GDAS) in PREPBUFR format.
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
# This use cases uses PB2NC, GenVxMask, and PointStat along with Python embedding
# and user scripting. For each call to PointStat, Python embedding is used to calculate 
# the CTP and Humidity Index diagnostics and pass those diagnostics to PointStat 
# for verification.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2020-08-05 12:00
#
# **End time (VALID_END):** 2020-08-05 12:00
#
# **Increment between beginning and end times (VALID_INCREMENT):** 12 Hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 60
#
# Only a single time is used to demonstrate the workflow for this use case.
# For each time, PB2NC is used to convert the upper-air radiosonde observations from
# PREPBUFR format to NetCDF. Then, a Python user script is used to create a text file
# with the locations of upper-air sites to use for verification. This text file
# is used by GenVxMask to mask out any points in the forecast outside of a user-defined
# radius around each upper-air site. Then, PointStat is called which uses Python embedding
# to compute diagnostics using METcalcpy to use for verification. Point stat is used
# to produce matched pairs (forecast/observation pairs) of both diagnostics for
# downstream land-atmosphere process evaluation.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s/SeriesAnalysis_fcstCFSv2_obsGHCNCAMS_climoStandardized_MultiStatisticTool.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI.conf

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
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case has four Python embedding scripts, one for each diagnostic (CTP/HI)
# for both the forecast and observations
#
# * pyembed_fcst_HR1.py
# * pyembed_obs_gdas.py
#
# In addition to the `basic package requirements for Python embedding <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/appendixF.html#compiling-met-for-python-embedding>`_, these Python scripts also require
#
# * `MetPy <https://unidata.github.io/MetPy/latest/>`_
# * `METcalcpy version 3.1+ <https://metplus.readthedocs.io/projects/metcalcpy/en/latest/index.html>`_
#
# The forecast Python embedding scripts require the data variable names and the path
# to the mask file created with GenVxMask, while the observation Python embedding scripts
# only require the output file from PB2NC.
# 
# .. dropdown:: parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_fcst_HR1.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_fcst_HR1.py
#
# .. dropdown:: parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_obs_gdas.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/pyembed_obs_gdas.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus,
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.

##############################################################################
# User Scripting
# --------------
#
# This use case uses a Python script to create an input file for GenVxMask to use
# based on the upper-air sites the user wishes to include. In the METplus configuration file,
# a user can set the USER_SCRIPT_SITES_TO_INCLUDE configuration item. This is a comma-separated
# string of integers representing the first digit in the WMO station ID of upper-air sites to
# include. For example, in the United States many of the upper-air sites begin with "7". If a 
# user wants to use only U.S. sites, they would set this just to 7. To include other countries,
# include more digits. By default, this is set to only 7 in order to decrease the total run time of
# the use case for testing and demonstration.
#
# A second user script is used to plot matched forecast and observation pairs (MPR) from PointStat MPR
# text files in order to visualize the two metrics in the same space.
#
# In addition to the `basic package requirements for Python embedding <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/appendixF.html#compiling-met-for-python-embedding>`_, the **plot_2panel_ctp_hi.py** Python script also requires
#
# * `Matplotlib <https://matplotlib.org/stable/>`_
#
# .. dropdown:: parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/create_raob_mask_file.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/create_raob_mask_file.py
#
# .. dropdown:: parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/plot_2panel_ctp_hi.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI/plot_2panel_ctp_hi.py

##############################################################################
# Running METplus
# ---------------
#
# .. note::
#
#   Prior to running this use case, the user should ensure that the version of Python in their environment meets the requirements
#   for the Python UserScripts. These requirements are noted earlier in this documentation. Additionally, if the user is using a version
#   of MET that was not compiled against a Python installation meeting the requirements for Python embedding (also described earlier), then
#   the user should set the MET_PYTHON_EXE configuration variable under the [user_env_var] section of their local METplus configuration file 
#   to "python3". When a user runs the Linux command "which python3", it should return the path to the Python installation that meets the 
#   requirements for either the Python UserScripts, and if needed, Python embedding scripts. This will ensure the correct Python is used for
#   Python embedding (if needed), and the Python UserScripts.
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI.conf /path/to/user_system.conf
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
# Output for this use case will be found in 
# {OUTPUT_BASE}/model_applications/land/PointStat_fcstUFS_obsGDAS_CTP_HI
# and will contain the following files::
#
#  * point_stat/CTP/point_stat_600000L_20200805_120000V_mpr.txt
#  * point_stat/CTP/point_stat_600000L_20200805_120000V.stat
#  * point_stat/HI/point_stat_600000L_20200805_120000V_mpr.txt
#  * point_stat/HI/point_stat_600000L_20200805_120000V.stat
#  * compare_ctp_hi.png
#  * gen_vx_mask/pb2nc_adpupa_latlon.txt
#  * gen_vx_mask/raob_masks.nc
#  * obs/netcdf/prepbufr.gdas.2020080512.nc
 
#
# Each file should contain corresponding statistics for the line type(s) requested.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PointStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * METcalcpyUseCase
#   * LandAppUseCase
#   * UserScriptUseCase
#   * VxDataGDASPREP
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/land-PointStat_fcstUFS_obsGDAS_CTP_HI.png'
