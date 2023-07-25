"""
UserScript: Make a Phase Diagram plot from input RMM or OMI
===========================================================

model_applications/
s2s_mjo/
UserScript_obsERA_obsOnly_PhaseDiagram.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To produce a phase diagram using either OLR based MJO Index (OMI) or the Real-time Multivariate MJO index (RMM)
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset:  None.
#  * Observation dataset: ERA Reanlaysis Outgoing Longwave Radiation.

##############################################################################
# External Dependencies
# ---------------------
#
# You will need to use a version of Python 3.6+ that has the following packages installed::
#
# * numpy
# * netCDF4
# * datetime
# * xarray
# * matplotlib
# * scipy
# * pandas 
#
# If the version of Python used to compile MET did not have these libraries at the time of compilation, you will need to add these packages or create a new Python environment with these packages.
#
# If this is the case, you will need to set the MET_PYTHON_EXE environment variable to the path of the version of Python you want to use. If you want this version of Python to only apply to this use case, set it in the [user_env_vars] section of a METplus configuration file.:
#
#    [user_env_vars]
#    MET_PYTHON_EXE = /path/to/python/with/required/packages/bin/python
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the Phase Diagram driver which and creates a phase diagram. Inputs to the driver are a text file containing the following columns, yyyy,mm,dd,hh,pc1,pc2,amp for OMI, or yyyy,mm,dd,pc1,pc2,phase,amp,source for RMM.
#

##############################################################################
# METplus Workflow
# ----------------
# 
# The Phase diagram driver script python code is run for each lead time on the forecast and observations data. This example loops by valid time for the model pre-processing, and valid time for the other steps.  It creates the phase diagram plot and a text file listing of the valid times to use in creating the plots.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsERA_OMI.conf.
# The file UserScript_obsERA_obsOnly_PhaseDiagram/PhaseDiagram_driver.py runs the python 
# program and UserScript_obsERA_obsOnly_PhaseDiagram.conf sets the variables for all steps 
# of the use case.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#

##############################################################################
# Python Scripts
# ----------------
#
# The phase diagram driver script orchestrates the generation of a phase diagram plot:
# parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_OMI/PhaseDiagram_driver.py:
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/PhaseDiagram_driver.py
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/save_input_files_txt.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in UserScript_obsERA_obsOnly_PhaseDiagram.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_obsERA_obsOnly_PhaseDiagram.py::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.conf
#
# The following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
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

##############################################################################
# Expected Output
# ---------------
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use case will be found in model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.  This may include the regridded data and daily averaged files.  In addition, the phase diagram plots will be generated and the output location can be specified as PHASE_DIAGRAM_PLOT_OUTPUT_DIR.  If it is not specified, plots will be sent to model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram/plots (relative to **OUTPUT_BASE**).

##############################################################################
# Keywords
# --------
#
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SMJOAppUseCase
#   * METplotpyUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_obsERA_obsOnly_PhaseDiagram.png'
#
