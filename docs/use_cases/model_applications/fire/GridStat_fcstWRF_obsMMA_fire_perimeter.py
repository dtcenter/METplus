"""
GridStat: WRF and MMA Fire Perimeter
====================================

model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter.conf

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
# This use case demonstrates the use of GridStat to evaluate the performance of the 
# fire spread forecast from the WRF-Fire model for the 416 fire in Colorado in 2018. 
# Using available fire perimeter observations and WRF-Fire forecasts, 
# contingency statistics are produced to evaluate the forecast performance 
# relative to the observed fire.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.0

##############################################################################
# Datasets
# --------
#
#
# **Forecast:** WRF Fire
#
# **Observations:** Multimission Aircraft (MMA)
#
# **Location:** All of the input data required for this use case can be
# found in a sample data tarball. Each use case category will have
# one or more sample data tarballs. It is only necessary to download
# the tarball with the use case’s dataset and not the entire collection
# of sample data. Click here to access the METplus releases page and download sample data
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#


##############################################################################
# METplus Components
# ------------------
#
# This use case uses the UserScript wrapper to run a Python script to that
# converts KML fire perimeter files to the poly line format that can be read by
# MET. Then it runs GenVxMask to create gridded MET NetCDF files from the poly
# files. Then it runs GridStat to process the WRF fire forecast files and the
# observation mask files.
#

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2018-06-01 at 16Z
#
# **End time (INIT_END):** 2018-06-01 at 16Z
#
# **Increment between beginning and end times (INIT_INCREMENT):** None
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 4 hour, 23 hour, 32 hour
#
# This use case processes 3 forecast leads initialized at 16Z on June 1, 2018, running 3 times. 
# First, the UserScript tool is called. This tool calls a Python script to convert the 
# kml shapefiles to polylines. Then, GenVxMask is run to convert the shapefile 
# produced by UserScript to a netCDF mask, providing the observation input for GridStat. 
# Finally, GridStat is called to compare the WRF-Fire forecast of fire area to the 
# observation mask created using the GenVxMask tool. The GridStat call uses Python Embedding 
# in order to read the WRF-Fire subgrid into GridStat.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file,
# then it loads any configuration files passed to METplus via the command line
# e.g. parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter.conf
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
#    .. highlight:: bash
#    .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read the WRF-Fire forecast into GridStat. 
# The script hard codes settings directly from WRF-Fire for the WRF-Fire netCDF variable name (FIRE_AREA) 
# as well as the format of the WRF-Fire forecast file template. The input directory and valid time 
# are read from the METplus script. Once the file(s) are found, the script sets attributes for 
# initiation and valid times, variable name, level, and units in MET format and defines a grid 
# based on the input WRF-Fire netCDF file's subgrid. The data from the FIRE_AREA variable and MET attributes 
# are then printed to be read in by GridStat.
#
# .. dropdown:: parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter/read_wrfout_fire.py
#
#    .. highlight:: python
#    .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter/read_wrfout_fire.py
# 
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_

##############################################################################
# User Scripting
# --------------
#
# This use case calls a Python script to read MMA fire perimeter .kml files and convert them 
# into a poly line file that can be read by GenVxMask. The script hard codes the filename template 
# for the .kml files and a valid time format. This valid time format is provided by the METplus configuration file. 
# The script the sets up a variable for the previous valid time and an output file path. 
# If a .kml file is not found for the current valid time, the script searches for a .kml file 
# from the previous hours. Once a file is found, the Python script parses the input file to find 
# the set of coordinates that define the fire perimeter. These coordinates are then written to 
# a text file (.poly file) in the order longitude, latitude, elevation for each point. 
# This .poly file is then ready to be read in by the GenVxMask tool.
#
# .. dropdown:: parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter/find_and_read_fire_perim_poly.py
#
#    .. highlight:: python
#    .. literalinclude:: ../../../../parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter/find_and_read_fire_perim_poly.py
#



##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/fire/GridStat_fcstWRF_obsMMA_fire_perimeter.conf /path/to/user_system.conf
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
# There are three groups of outputs. First, three polyline files resulting from the UserScript tool
#
# * poly/fire_perim_20180601_20.poly
# * poly/fire_perim_20180602_15.poly
# * poly/fire_perim_20180603_00.poly
#
# Second, three netCDF files resulting from the GenVxMask tool containing fire perimeter observations
#
# * mask/fire_perim_20180601_20_mask.nc
# * mask/fire_perim_20180602_15_mask.nc
# * mask/fire_perim_20180603_00_mask.nc
#
# Finally, six files from the GridStat tool run with Python Embedding. The .stat files contain the 
# CTC and CTS line types for the FIRE_AREA variable at the given lead time (two lines total per stat file). 
# The netCDF files contain the following five fields: lat (latitude), lon (longitude), 
# FCST_FIRE_AREA_Z0_FULL (fire spread area from the WRF-Fire forecast), OBS_FIRE_PERIM_all_all_FULL (fire spread area from the .kml observations), 
# and DIFF_FIRE_AREA_Z0_FIRE_PERIM_all_all_FULL (both the forecast and observed fire spread areas, including overlaps and differences).
#
# * grid_stat/2018060120/grid_stat_040000L_20180601_200000V.stat
# * grid_stat/2018060120/grid_stat_040000L_20180601_200000V_pairs.nc
# * grid_stat/2018060215/grid_stat_230000L_20180602_150000V.stat
# * grid_stat/2018060215/grid_stat_230000L_20180602_150000V_pairs.nc
# * grid_stat/2018060300/grid_stat_320000L_20180603_000000V.stat
# * grid_stat/2018060300/grid_stat_320000L_20180603_000000V_pairs.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * GenVxMaskToolUseCase
#   * GridStatToolUseCase
#   * PythonEmbeddingFileUseCase
#   * GRIB2FileUseCase
#   * FireAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/fire-GridStat_fcstWRF_obsMMA_fire_perimeter.png'
