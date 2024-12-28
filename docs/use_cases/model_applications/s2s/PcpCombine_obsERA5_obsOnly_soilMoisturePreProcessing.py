"""
PCP-Combine: Compute 1m Soil Moisture and 30 year Climatology
=============================================================

model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.conf

"""

##############################################################################
# Scientific Objective
# --------------------
# [UPDATE_SECTION_CONTENT]
#
# This use case computes pre-processing on Soil Moisture data to prepare it to
# be run through Grid-Stat or another program to verify Soil Moisture.
# To provide statistical information on the forecast hail size compared to
# the observed hail size from MRMS MESH data. Using objects to verify hail size
# avoids the “unfair penalty” issue, where a CAM must first generate convection
# to have any chance of accurately predicting the hail size. In addition, studies
# have shown that MRMS MESH observed hail sizes do not correlate one-to-one with
# observed sizes but can only be used to group storms into general categories.
# Running MODE allows a user to do this.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** None
#
# **Observation:** ERA-5 Land Soil Moisture top 3 layers
#
# **Climatology:** None
#
# **Location:** The input data required for PCP-Combine in this use case can be
# found in a sample data tarball. Each use case category will have
# one or more sample data tarballs. It is only necessary to download
# the tarball with the use case’s dataset and not the entire collection
# of sample data. Click here to access the METplus releases page and download sample data
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#
# Data for the Regrid-Data-Plane runsis not contained in the sample data tar files due
# to its size. Rather, it is stored as additional data in a separate tar file, named
# additional_data_PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.tar.gz and can be
# downloaded at https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/v6.1/.

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script,
# in this case, polar_t_u_driver.py which output data into MET's matched pair format.  
# It then runs Stat-Analysis to compute the bias and RMSE, and another UserScript, 
# bias_rmse_plot_driver.py, to create the plots.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case loops over lead times for the first UserScript and Stat-Analysis,
# and the plotting proceeds over the entire time period
# 
# UserScript: Computes polar cap temperature and polar vortex U
# Stat-Analysis: Computes ME and RMSE on polar cap temperature and polar vortex U
# UserScript: Creates ME and RMSE plots
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# **STATAnalysisConfig_wrapped**
#
# .. note:: See the :ref:`Series-Analysis MET Configuration<series-analysis-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/STATAnalysisConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use python embedding
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstGFS_obsERA_StratospherePolar.conf, 
# then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstGFS_obsERA_StratospherePolar.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s_stratosphere/UserScript_fcstGFS_obsERA_StratospherePolar.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  No executables are required for performing this use case.
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
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
#   * S2SAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.png'
