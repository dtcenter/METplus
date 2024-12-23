"""
UserScript: Compute Cross Spectra and Make a Plot 
=================================================

model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.py

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

#################################################################################
# Scientific Objective
# --------------------
#
# This use case calls the METcalcpy cross spectra function and then the METplotpy 
# space time plot to compute cross-spectra and create a sample cross spectra 
# diagram using sample data.
#
# The space time plot and cross spectra calculations were created by Maria Gehne 
# at the Physical Sciences Labratory in NOAA. 

##############################################################################
# Version Added
# -------------
#
# METplus version 5.1

#################################################################################
# Datasets
# --------
#
#  * Forecast dataset: UFS Prototype 7
#  * Observation dataset: ERAI
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script, 
# in this case, cross_spectra.py and cross_spectra_plot.py.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case computes spectra and plots for the entire time period of data. 
# The use case loops over two processes, computing and plotting the 
# cross-spectra. The user is able to edit the process list to turn off the 
# computation part if only plotting is desired, or vice versa.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.conf

#############################################################################
# MET Configuration
# -----------------
#
# There are no MET tools used in this use case.

##############################################################################
# Python Embedding
# ----------------
#
# There is no Python embedding in this use case.

##############################################################################
# User Scripting
# --------------
#
# This use case uses a Python script to perform plotting.
#
# .. dropdown:: parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py
#
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.conf -c /path/to/user_system.conf
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
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-UserScript_fcstS2S_obsERAI_CrossSpectra.png'
