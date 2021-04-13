"""
CyclonePlotter: Use Case for OPC (EMC) cyclone data
===================================================

model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_OPC.conf

"""
###########################################
# Scientific Objective
# --------------------
#
# Once this method is complete, a user-created extra TC track file
# for the valid date of interest (YYYYMMDDHH) will have been created, 
# paired up by TCPairs, and global storm tracks 
# for the valid date of interest will be plotted by CyclonePlotter (PlateCaree projection)

##############################################################################
# Datasets
# --------
#
#
# | **Forecast:** Adeck
# |     /path/to/{init?fmt=%Y}/trak.gfso.atcf_gen.glbl.{init?fmt=%Y}
# | **Observation:** Bdeck
# |     /path/to/{init?fmt=%Y}/trak.gfso.atcf_gen.glbl.{init?fmt=%Y}
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Data Source:** GFS
# |

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
# TCPairs is the first tool called in this example. It processes the following
# run times for each storm file:
#
# | **Init/Valid:** 2020100700
# |
#
# CyclonePlotter is the second (and final) tool called in this example. It processes the output
# from TCPairs.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c /path/to/TCPairs_extra_tropical.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_OPC.conf

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
# .. note:: See the :ref:`TCPairs MET Configuration<tc-pairs-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCPairsConfig_wrapped

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
# parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_OPC/extract_opc_decks.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_OPC/extract_opc_decks.py
#


##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in TCPairs_extra_tropical.conf then a user-specific system configuration file::
#
#   run_metplus.py -c /path/to/CyclonePlotter_fcstGFS_obsGFS_OPC.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where EMC data files (csv) are read (See Datasets section to obtain tarballs).
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
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
#  `TCPairsToolUseCase <https://dtcenter.github.io/METplus/search.html?q=TCPairsToolUseCase&check_keywords=yes&area=default>`_,
#  `SBUOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=SBUOrgUseCase&check_keywords=yes&area=default>`_
# .. note:: `CyclonePlotterUseCase <https://dtcenter.github.io/METplus/search.html?q=CyclonePlotterUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-CyclonePlotter_fcstGFS_obsGFS_OPC.png'




