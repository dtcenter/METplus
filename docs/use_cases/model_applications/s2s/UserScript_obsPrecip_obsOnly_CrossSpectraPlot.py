"""
UserScript: Make a Cross Spectra plot 
========================================================================

model_applications/
s2s/
UserScript_obsPrecip_obsOnly_CrossSpectraPlot.py

"""

#################################################################################
# Scientific Objective
# --------------------
#
# This use case calls the METplotpy space time plot to create a sample cross 
# spectra diagram
# using sample data created by METcalcpy cross spectra functions
#
# The space time plot and cross spectra calculations were created by Maria Gehne 
# at the 
# Physical Sciences Labratory in NOAA 

#################################################################################
# Datasets
# --------
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, cross_spectra_plot.py.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots the entire time period of data
# 
# UserScript
#
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf
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
# Python Scripts
# ----------------
#
# This use case uses a Python script to perform plotting
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot/cross_spectra_plot.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf \
#        -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf::
#
#        run_metplus.py \
#        -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.conf
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
#  `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_,
#  `S2SAppUseCase <https://dtcenter.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_,
#
# sphinx_gallery_thumbnail_path = '_static/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.png'
