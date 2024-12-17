"""
UserScript: Make a Phase Diagram plot from input RMM or OMI
===========================================================

model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.py

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
# Phase diagrams are used to Indices for MJO and QBO.  This use case produces a 
# phase diagram using either OLR based MJO Index (OMI) or the Real-time Multivariate 
# MJO index (RMM)

##############################################################################
# Version Added
# -------------
#
# METplus version 4.1

##############################################################################
# Datasets
# --------
#
# **Forecast:**  None
#
# **Observation:** ERA Reanlaysis Outgoing Longwave Radiation
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
# This use case runs UserScript twice, once to create a text file containing a listing 
# of input files and then to create a Phase Diagram.

##############################################################################
# METplus Workflow
# ----------------
# 
# **Beginning time (INIT_BEG):** 2012-01-01
#
# **End time (INIT_END):** 2012-03-31
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# The UserScript that creates a filelist is run once for each valid time, while the UserScript to create
# a phase diagram is run only once.  It creates a phase diagram plot using the input files.  Variables for 
# the phase diagram are set in the [user_env_vars] section of the .conf file.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf

##############################################################################
# MET Configuration
# -----------------
#
# There are no MET configuration files in this use case.

###############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding. 

##############################################################################
# User Scripting
# --------------
#
# The first UserScript creates a listing of text file (save_inpput_file_txt).  The second, 
# PhaseDiagram_driver.py orchestrates the generation of a phase diagram plot.  Inputs to the 
# phase diagram driver are a text file containing the following columns, yyyy,mm,dd,hh,pc1,pc2,amp for OMI, 
# or yyyy,mm,dd,pc1,pc2,phase,amp,source for RMM.
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/save_input_files_txt.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/save_input_files_txt.py
#
# .. dropdown:: parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/PhaseDiagram_driver.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/PhaseDiagram_driver.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf /path/to/user_system.conf
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
# {OUTPUT_BASE}/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/plots
# The output is one plot::
#
# * RMM_phase_diagram.png

##############################################################################
# Keywords
# --------
#
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SMJOAppUseCase
#   * UserScriptUseCase
#   * METplotpyUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_obsERA_obsOnly_PhaseDiagram.png'
