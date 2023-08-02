"""
UserScript: Make a Hovmoeller plot 
========================================================================

model_applications/
s2s/
UserScript_obsPrecip_obsOnly_Hovmoeller.py

"""

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
# Datasets
# --------
#

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
# This use case can be run two ways:
#
# 1) Passing in UserScript_obsPrecip_obsOnly_Hovmoeller.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py \
#        /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.conf \
#        /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_obsPrecip_obsOnly_Hovmoeller.conf::
#
#        run_metplus.py \
#        /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.conf
#     
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  If the executable is in the user's path, METplus will find it from the name. 
#  If the executable is not in the path, specify the full path to the executable here (i.e. RM = /bin/rm)  
#  The following executables are required for performing series analysis use cases:
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
#   [exe]
#   RM = /path/to/rm
#   CUT = /path/to/cut
#   TR = /path/to/tr
#   NCAP2 = /path/to/ncap2
#   CONVERT = /path/to/convert
#   NCDUMP = /path/to/ncdump
#

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
