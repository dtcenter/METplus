"""
CyclonePlotter: Extra-TC Tracker and Plotting Capabilities
==========================================================

model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.conf

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
# Once this method is complete, a user-created extra TC track file
# for the valid date of interest (YYYYMMDDHH) will have been created, 
# paired up by TCPairs, and global storm tracks 
# for the valid date of interest will be plotted by CyclonePlotter (PlateCaree projection)

##############################################################################
# Version Added
# -------------
#
# METplus version 5.1

##############################################################################
# Datasets
# --------
#
# | **Forecast:** Adeck
# |     /path/to/{init?fmt=%Y}/trak.gfso.atcf_gen.glbl.{init?fmt=%Y}
#
# | **Observation:** Bdeck
# |     /path/to/{init?fmt=%Y}/trak.gfso.atcf_gen.glbl.{init?fmt=%Y}
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
# **Data Source:** GFS

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed:
#
# * cartopy
# * matplotlib
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes Python user script-created output files that are accessible via the TCPairs wrapper.
# Due to the nature of the source file (already tracked extra TCs), the TCPairs wrapper is passed the "Adeck" file for each storm twice:
# once as the adeck or forecast file, and once as the bdeck or analysis file. Essentially, TCPairs is matching a forecast to itself.
# It then uses the CyclonePlotter wrapper to create a global plot of storm tracks for the desired day of interest (YYYYMMDDHH).

##############################################################################
# METplus Workflow
# ----------------
#
# | LOOP_BY = INIT
# | INIT_TIME_FMT = %Y%m%d
# | INIT_BEG = 20201007
# | 
# | USER_SCRIPT_RUNTIME_FREQ = RUN_ONCE
# | TC_PAIRS_RUNTIME_FREQ = RUN_ONCE
#
# TCPairs is the first tool called in this example. It processes the following
# run times for each storm file:
#
# **Init/Valid:** 2020100700
#
# CyclonePlotter is the second (and final) tool called in this example. It processes the output
# from TCPairs.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.conf

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
# .. dropdown:: TCPairsConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/TCPairsConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to read input data.
# Because the source file already contains "analysis" tracks for the extra TCs,
# this Python script only needs to output storm tracks that have a valid time matching
# the user input. These storms are put into separate storm files, to better mimic how TC storms are
# typically passed to TCPairs.
#
# .. dropdown:: parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC/extract_opc_decks.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC/extract_opc_decks.py
#
# For more information on the basic requirements to utilize Python Embedding in METplus, 
# please refer to the MET User’s Guide section on `Python embedding <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html#appendix-f-python-embedding>`_.


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
#   run_metplus.py /path/to/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.conf /path/to/user_system.conf
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
# Output for this use case will be found in **tc_pairs/201412** (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * decks/adeck/adeck.2020100700.xxxx.dat
# * tc_pairs/tc_pairs.2020100700.xxxx.tcst
# * cyclone/20201007.png
# * cyclone/20201007.txt
#
# where "xxxx" is the unique four digit storm identifier for TCPairs wrapper to use.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCPairsToolUseCase
#   * SBUOrgUseCase
#   * CyclonePlotterUseCase
#   * TropicalCycloneUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.png'




