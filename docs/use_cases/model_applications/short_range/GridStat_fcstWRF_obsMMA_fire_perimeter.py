"""
GridStat: WRF and MMA Fire Perimeter
====================================

model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter.conf

"""
##############################################################################
# .. contents::
#    :depth: 1
#    :local:
#    :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
#
# **REPLACE THIS!**
#
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
# **REVIEW AND REPLACE THIS!**
#
# | **Forecast:** WRF Fire
#
# | **Observations:** MMA
#
# | **Location:** All of the input data required for this use case can be found in the short_range sample data tarball.
# | Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE.
# | See `Running METplus`_ section for more information.
#

##############################################################################
# Python Dependencies
# ---------------------
#
# This use case utilizes MET Python Embedding.
# See the `MET User's Guide <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html>`_
# for more information about Python requirements.
#

##############################################################################
# METplus Components
# ------------------
#
# **REVIEW AND REPLACE THIS!**
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
# **REVIEW AND REPLACE THIS!**
#
# | **Init Beg:** 2018-06-01 at 16Z
# | **Init End:** 2018-06-01 at 16Z
# | **Forecast Leads:** 4 hour, 23 hour, 32 hour
#
# This use case processes 3 forecast leads initialized at 16Z on June 1, 2018.
#


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file,
# then it loads any configuration files passed to METplus via the command line
# e.g. parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter.conf
#

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file.
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF!
# THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
# If there is a setting in the MET configuration file that is not controlled by an environment variable,
# you can add additional environment variables to be set only within the METplus environment using the
# [user_env_vars] section of the METplus configuration files. # See the ‘User Defined Config’ section on the
# ‘System Configuration’ page of the METplus User’s Guide for more information.
#
# .. dropdown:: Click to view parm/met_config/GridStatConfig_wrapped
#
#    .. highlight:: bash
#    .. literalinclude:: ../../../../parm/met_config/GridStatConfig_wrapped
#

##############################################################################
# Python Scripting
# ----------------
#
# **REVIEW THIS!**
#
# This use case calls a Python script to read MMA fire perimeter .kml files
# and convert them into a poly line file that can be read by GenVxMask:
#
# .. dropdown:: Click to view find_and_read_fire_perim_poly.py
#
#    parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter/find_and_read_fire_perim_poly.py
#
#    .. highlight:: python
#    .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter/find_and_read_fire_perim_poly.py
#

##############################################################################
# Python Embedding
# ----------------
#
# **REVIEW THIS!**
#
# This use case uses a Python embedding script to read the WRF fire forecast into GridStat:
#
# parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter/read_wrfout_fire.py
#
# .. dropdown:: Click to view read_wrfout_fire.py
#
#    .. highlight:: python
#    .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter/read_wrfout_fire.py
#


##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GridStat_fcstWRF_obsMMA_fire_perimeter.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
#

##############################################################################
# Expected Output
# ---------------
#
# **REVIEW AND REPLACE THIS!**
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
#
# * poly/fire_perim_20180601_20.poly
# * poly/fire_perim_20180602_15.poly
# * poly/fire_perim_20180603_00.poly
# * mask/fire_perim_20180601_20_mask.nc
# * mask/fire_perim_20180602_15_mask.nc
# * mask/fire_perim_20180603_00_mask.nc
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
#   * ShortRangeAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-GridStat_fcstWRF_obsMMA_fire_perimeter.png'
