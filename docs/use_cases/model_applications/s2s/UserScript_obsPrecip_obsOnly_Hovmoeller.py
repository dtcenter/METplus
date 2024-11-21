"""
UserScript: Make a Hovmoeller plot 
==================================

model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.py

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
# This use case calls the METplotpy hovmoeller plot to create a sample Hovmoeller diagram
# using sample data created by METcalcpy hovmoeller functions
#
# The Hovmoeller plot and hovmoeller calculations where created by Maria Gehne at the 
# Physical Sciences Labratory in NOAA 

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** [UPDATE_SECTION_CONTENT]
#
# **Observation:** [UPDATE_SECTION_CONTENT]
#
# **Climatology:** [UPDATE_SECTION_CONTENT]
#
# **Location:** [UPDATE_SECTION_CONTENT] 


##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, hovmoeller.py.
#
# It also requires the METcalcpy and METplotpy source code to generate the plot.
# Clone the METcalcpy repository (https://github.com/dtcenter/METcalcpy) and the
# METplotpy repository (https://github.com/dtcenter/METplotpy) under the same base
# directory as the METPLUS_BASE directory so that the METplotpy, METcalcpy, and
# METplotpy directories are under the same base directory (i.e. if the METPLUS_BASE directory is
# /home/username/working/METplus, then clone the METcalcpy and METplotpy source
# code into the /home/username/working directory).  
#


##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots the entire time period of data
# 
# 
# This uses data from 2016-01-01 to 2016-03-31
#
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# There are no MET tools used in this use case.
#

##############################################################################
# Python Embedding
# ----------------
#
# There is no python embedding in this use case
#

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.conf /path/to/user_system.conf
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

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * S2SAppUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/Hovmoeller_ERAIprecip_2016-01-01-2016-03-31.png'
