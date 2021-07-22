"""
UserScript: Make RMM plots from calculated MJO indices
===========================================================================

model_applications/
s2s/
UserScript_fcstGFS_obsERA_RMM.py

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To compute the Real-time Multivariate MJO Index (RMM) using Outgoing Longwave Radiation (OLR), 850 hPa wind (U850), and 200 hPa wind (U200). Specifically, RMM is computed using OLR, U850, andU200 data between 15N and 15S.  Anomalies of OLR, U850, and U200 are then created, 120 day day mean removed, and the data are normalized by normalization factors (generally the square root of the average variance)  The anomalies are projected onto Empirical Orthogonal Function (EOF) data.  The OLR is then filtered for 20 - 96 days, and regressed onto the daily EOFs.  Finally, it's normalized and these normalized components are plotted on a phase diagram and timeseries plot.
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset:  GFS Model Outgoing Longwave Radiation
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
# This use case runs the OMI driver which computes OMI and creates a phase diagram. Inputs to the OMI driver include netCDF files that are in MET's netCDF version.  In addition, a txt file containing the listing of these input netCDF files is required, as well as text file listings of the EOF1 and EOF2 files.  Some optional pre-processing steps include using regrid_data_plane to either regrid your data or cut the domain t0 20N - 20S. 
#

##############################################################################
# METplus Workflow
# ----------------
# 
# The OMI driver script python code is run for each lead time on the forecast and observations data. This example loops by valid time for the model pre-processing, and valid time for the other steps.  This version is set to only process the OMI calculation and creating a text file listing of the EOF files, omitting the regridding, and anomaly caluclation pre-processing steps.  However, the configurations for pre-processing are available for user reference.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.conf.  
# The file OMI_driver.py runs the python program and  
# UserScript_fcstGFS_obsERA_OMI/UserScript_fcstGFS_obsERA_OMI.conf sets the 
# variables for all steps of the OMI use case.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.conf

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
# The OMI driver script orchestrates the calculation of the MJO indices and 
# the generation of a phase diagram OMI plot:
# parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI/OMI_driver.py:
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI/OMI_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_OMI.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_OMI.py::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use case will be found in model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.  This may include the regridded data and daily averaged files.  In addition, the phase diagram plots will be generated and the output location can be specified as OMI_PLOT_OUTPUT_DIR.  If it is not specified, plots will be sent to model_applications/s2s/UserScript_fcstGFS_obsERA_OMI/plots (relative to **OUTPUT_BASE**). 

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/s2s-OMI_phase_diagram.png'
#
# .. note:: `XXXX`, `S2SAppUseCase <https://dtcenter.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_
#  `RegridDataPlaneUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneUseCase&check_keywords=yes&area=default>`_,
#  `PCPCombineUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineUseCase&check_keywords=yes&area=default>`_
 
 
# 
# 

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset:  GFS Model Outgoing Longwave Radiation, 850 hPa wind and 200 hPa wind
#  * Observation dataset: ERA Reanlaysis Outgoing Longwave Radiation, 850 hPa wind and 200 hPa wind

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
# This use case runs the RMM driver which computes RMM and creates a phase diagram, time series, and EOF plot. Inputs to the RMM driver include netCDF files that are in MET's netCDF version.  In addition, a text file containing the listing of these input netCDF files for OLR, u850 and u200 is required.  Some optional pre-processing steps include using regrid_data_plane to either regrid your data or cut the domain t0 20N - 20S. 
#

##############################################################################
# METplus Workflow
# ----------------
# The RMM driver script python code is run for each lead time on the forecast and observations data. This example loops by valid time for the model pre-processing, and valid time for the other steps.  This version is set to only process the RMM calculation, omitting the regridding, and anomaly caluclation, and creation of the text file listing for OLR, u850, and u200 pre-processing steps.  However, the configurations for pre-processing are available for user reference.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e. parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM.conf.  
# The file UserScript_fcstGFS_obsERA_RMM/RMM_driver.py runs the python program and  
# UserScript_fcstGFS_obsERA_RMM.conf sets the variables for all steps of the RMM use case.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM.conf

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
# The RMM driver script orchestrates the calculation of the MJO indices and 
# the generation of three RMM plots:
# parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM/RMM_driver.py:
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM/RMM_driver.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case is run in the following ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_RMM.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_RMM.py::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/UserScript_fcstGFS_obsERA_RMM.conf
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
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. Output for this use case will be found in model_applications/s2s/UserScript_fcstGFS_obsERA_RMM.  This may include the regridded data and daily averaged files.  In addition, three plots will be generated, a phase diagram, time series, and EOF plot, and the output location can be specified as RMM_PLOT_OUTPUT_DIR.  If it is not specified, plots will be sent to model_applications/s2s/UserScript_fcstGFS_obsERA_RMM/plots (relative to **OUTPUT_BASE**).
# 

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/s2s-RMM_time_series.png'
#
# .. note:: `XXXX`, `S2SAppUseCase <https://dtcenter.github.io/METplus/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_, 
#  `NetCDFFileUseCase <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&chek_keywords=yes&area=default>`
#  `RegridDataPlaneUseCase <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneUseCase&check_keywords=yes&area=default>`_,
#  `PCPCombineUseCase <https://dtcenter.github.io/METplus/search.html?q=PCPCombineUseCase&check_keywords=yes&area=default>`__
