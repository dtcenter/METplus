"""
UserScript: Make MaKE-MaKI  plots from calculated MaKE and MaKI  indices
======================================================

model_applications/
s2s_mjo/
UserScript_obsCFSR_obsOnly_MJO_ENSO.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To compute the MaKE and MaKI indices using the zonal and meridional comomponents of  windstress (taux,tauy), zonal and meridional components of surface ocean currents (u,v), and sea surface temperature (SST). Specifically, MaKE and MaKI indices aree computed using taux, tauy, u, v and SST ddata between 30S and 30N and 125E and 80W. Daily anomalies of wind stress components are filtered for 30-90 day using a Convolutional Neural Network-based filter. The weights of the filter are computed offline. The bandpass filtered wind stress components are projected onto 4 Empirical Orthogonal Functions (EOFs) data. The obtained PCs are standardized and combined with the EOFs to obtain the Madden-Julian Oscillation (MJO) component of the surface wind stress (taux_MJO, tauy_MJO). u and v daily anomalies are multiplied by meridional structure of Kelvin wave (u_K, v_K). Windpower (W_MJO,K) is then computed as taux_MJO*u_k+tauy_MJO*v_K. Theh standardized W_MJO,K and SST areree projected onto the first two multivariate EOFs of W_MJO,K and SST. The resulting dadily time seeries (PCs) are normalized and used to compute monthly values of MaKE and MaKI. Monthly valuees of MaKE and MaKI are saved into a text (.csv) file and plotted as time series.     
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset:  None
#  * Observation dataset: CFSR Reanalysis 

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
# This use case runs the MJO-ENSO driver, which first computes the MJO components of taux and tauy, then the MJO wind power, the MJO-ENSO indices, their plot. Inputs to the MJO-ENSO driver include netCDF files that are in MET's netCDF version.  In addition, a text file containing the listing of these input netCDF files for taux, tauy, u, v, and SST is required.  Some optional pre-processing steps include RegridDataPlane for regridding  the data. 
#

##############################################################################
# METplus Workflow
# ----------------
# The MJO-ENSO driver script python code is run for each lead time on the forecast and observations data. This example loops by valid time for the model pre-processing, and valid time for the other steps.  This version is set to only process the regridding, and MaKE and MaKI calculation, omitting the caluclation of the mean daily annucal cycle and daily anomalies pre-processing steps.  However, the configurations for pre-processing are available for user reference.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO.conf.
# The file UserScript_obsCFSR_obsOnly_MJO_ENSO/mjo_ensodriver.py runs the python program and  
# UserScript_obsCFSR_obsOnly_MJO_ENSO.conf sets the variables for all steps of the MJO-ENSO use case.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
#

##############################################################################
# Python Scripts
# ----------------
#
# The MJO-ENSO driver script orchestrates the calculation of the MaKE and MaKI indices and 
# the generation of a text file and a plot for the indices:
# parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO/mjo_enso_driver.py:
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO/mjo_enso_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in UserScript_obsCFSR_obsOnly_MJO_ENSO.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_obsCFSR_obsOnly_MJO_ENSO.py::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use case will be found in model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO.  This may include the regridded data.  In addition, a text (.csv) file  will be generated and a time serie plot, and the output location can be specified as PLOT_OUTPUT_DIR.  If it is not specified, plots will be sent to model_applications/s2s_mjo/UserScript_obsCFSR_obsOnly_MJO_ENSO/plots (relative to **OUTPUT_BASE**).
# 

##############################################################################
# Keywords
# --------
#
#
# .. note::
#
#   * S2SAppUseCase
#   * S2SMJOAppUseCase
#   * NetCDFFileUseCase
#   * RegridDataPlaneUseCase
#   * PCPCombineUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/s2s_mjo-UserScript_obsCFSr_obsOnly_MJO_ENSO.png'
#
