"""
TCGen:  2021 Global Forecast System (GFS) Tropical Cyclone Genesis Forecast
===========================================================================

model_applications/tc_and_extra_tc/TCGen_fcstGFS_obsBDECK_2021season.conf

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
# This use case runs TC-Gen to analyze the operational Global Forecast System (GFS) tropical cyclone (TC) genesis forecasts for a portion of the 2021 Atlantic and
# Eastern Pacific basin hurrican seasons. TC-Gen will produce verification of deterministic and probabilistic tropical cyclone genesis forecasts in the ATCF
# file and shape file formats.  TC-Gen will output deterministic and probabilistic categorical counts and statistics and genesis matched pairs, which is a specific
# line type for TC-Gen.

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS genesis file, GFS E Deck
#
# **Observation:** B Deck, A Deck 
#
# **Warning Areas:** Shapefiles 
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
# **Data Source:** NHC ftp.noaa.gov/atcf
#
# **Data Source:** www.nhc.noaa.gov/archive/wgtwo/

##############################################################################
# METplus Components
# ------------------
#
# This case utilizes the METplus TC-Gen wrapper to run TC-Gen for deterministic 
# and probabilistic genesis forecasts with ASCII and netcdf output.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2021
#
# TC-Gen is the only tool called in this example. It processes the following
# run times:
#
# | **Init:** 2021-05-07 00 UTC - 2021-11-13 12 UTC
# | **Forecast lead:** 06 - 120 hours

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/tc_and_extra_tc/TCGen_fcstGFS_obsBDECK_2021season.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/TCGen_fcstGFS_obsBDECK_2021season.conf

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
# .. dropdown:: TCGenConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/TCGenConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

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
#   run_metplus.py /path/to/METplus/parm/model_applications/tc_and_extra_tc/TCGen_fcstGFS_obsBDECK_2021season.conf /path/to/user_system.conf
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
# Output for this use case will be found in model_applications/tc_and_extra_tc/TCGen (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * tc_gen.stat
# * tc_gen_pstd.txt
# * tc_gen_prc.txt
# * tc_gen_pjc.txt
# * tc_gen_pct.txt
# * tc_gen_cts.txt
# * tc_gen_ctc.txt
# * tc_gen_genmpr.txt
# * tc_gen_pairs.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCGenToolUseCase
#   * TropicalCycloneUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-TCGen_fcstGFS_obsBDECK_2021season.png'

