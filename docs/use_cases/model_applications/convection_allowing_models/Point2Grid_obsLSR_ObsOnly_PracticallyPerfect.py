"""
Point2Grid: Calculate Practically Perfect Probabilities
============================================================

model_applications/
convection_allowing_models/
Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To use storm reports as observations to calculate 
# Practically Perfect probabilities.
#

##############################################################################
# Datasets
# --------
#
# Relevant information about the datasets that would be beneficial include:
# 
# * Observation dataset: Local Storm Reports
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs ASCII2NC to get the storm reports in netcdf format, runs
# Point2Grid to get those netcdf observations onto a grid, runs RegridDataPlane
# to use that gridded data as a mask to calculate probabilities 
#

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# ASCII2NC > Point2Grid > RegridDataPlane 
#
# This example runs on a single time/file at a time. Each storm report is 
# assumed to have no more than 24 hours of data inside 
#
# Run times:
#
# | 2020-02-05
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf
#

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# See the following files for more information about the environment variables set in this configuration file.
#
# parm/use_cases/met_tool_wrapper/Point2Grid/Point2Grid.py
# parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
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
# Output for this use case will be found in model_applications/convection_allowing_models/practically_perfect/ (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * StormReps_211_Probs.20200205.nc 
#


##############################################################################
# Keywords
# --------
#
# .. note::
#   `ASCII2NC <https://dtcenter.github.io/METplus/search.html?q=ASCII2NCToolUseCase&check_keywords=yes&area=default>`_
#   `Point2Grid <https://dtcenter.github.io/METplus/search.html?q=Point2GridUseCase&check_keywords=yes&area=default>`_
#   `RegridDataPlane <https://dtcenter.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`_
#   `Python Embedding Ingest <https://dtcenter.github.io/METplus/search.html?q=PyEmbedIngestToolUseCase&check_keywords=yes&area=default>`_
#   `Regridding in Tool <https://dtcenter.github.io/METplus/search.html?q=RegriddingInToolUseCase&check_keywords=yes&area=default>`_
#   `NetCDF  <https://dtcenter.github.io/METplus/search.html?q=NetCDFFileUseCase&check_keywords=yes&area=default>`_
#   `Python Embedding  <https://dtcenter.github.io/METplus/search.html?q=PythonEmbeddingFileUseCase&check_keywords=yes&area=default>`_
#   `ConvectionAllowingModelsAppUseCase <https://dtcenter.github.io/METplus/search.html?q=ConvectionAllowingModelsAppUseCase&check_keywords=yes&area=default>`_,
#   `NCAROrgUseCase <https://dtcenter.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_,
#   `ProbabilityGenerationUseCase <https://dtcenter.github.io/METplus/search.html?q=ProbabilityGenerationUseCase&check_keywords=yes&area=default>`_,
#   `MaskingFeatureUseCase <https://dtcenter.github.io/METplus/search.html?q=MaskingFeatureUseCase&check_keywords=yes&area=default>`_ 
#   `HMTOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=HMTOrgUseCase&check_keywords=yes&area=default>`_ 
#   `HWTOrgUseCase <https://dtcenter.github.io/METplus/search.html?q=HWTOrgUseCase&check_keywords=yes&area=default>`_ 
#

# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.png'
