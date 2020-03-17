"""
MTD: Basic Object Tracking through Time  
===========================================================================

This use case identifies objects through space and time.
This is a forecast only use-case. (HRRR-TLE:NA:Gempak) 

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To provide useful statistical information on aggregated object-based information
# over a time series. This non-standard approach (i.e. a holistic approach to
# weather systems over grid or point assessments) provides alternative views to numerical model
# accuracy and offers new solutions to model adjustments.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: HREF forecasts in Gempak
#  * Sources of data (links, contacts, etc...)
#

##############################################################################
#External Dependencies
#---------------------
#
# GempakToCF.jar
#
# GempakToCF is an external too that utilizes the Unidata NetCDF-Java package. The jar file that can be used to run the utility is available here: https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
#
# For more information, please see the GempakToCF file documentation: parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.py

##############################################################################
# METplus Components
# ------------------
#
# This use case runs MTD (MODE Time Domain) over multiple forecast leads.

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time:
#
# * MTD
#
# This example loops by valid time. For each valid time
# it will run once, processing forecast leads 12 and 36. There is only one
# valid time in this example, so the following will be run:
#
# Run times:
#
# | **Valid:** 2019-02-05 12Z
# | **Forecast leads:** 12, 36
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/convection_allowing_models/MTD_fcstHREF_FcstOnly_Gempak.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/convection_allowing_models/MTD_fcstHREF_FcstOnly_Gempak.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/MTDConfig_wrapped
#
# See the following files for more information about the environment variables set in this configuration file.
# 
# parm/use_cases/met_tool_wrapper/MTD/MTD.py

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in MTD_fcstHREF_FcstOnly_Gempak.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MTD_fcstHREF_FcstOnly_Gempak.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MTD_fcstHREF_FcstOnly_Gempak.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/convection_allowing_models/MTD_fcstHREF_FcstOnly_Gempak.conf
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
# Output for this use case will be found in model_applications/convection_allowing_models/MTD_fcstHREF_FcstOnly_Gempak/met_out/HREF/201902051200/mtd (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * mtd_20190205_120000V_2d.txt
# * mtd_20190205_120000V_3d_single_simple.txt
# * mtd_20190205_120000V_obj.nc
#

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/convection_allowing_models-MTD_fcstHREF_FcstOnly_Gempak.png'
#
# .. note::
#    `MTDToolUseCase <https://ncar.github.io/METplus/search.html?q=MTDToolUseCase&check_keywords=yes&area=default>`_,
#    `NOAAHMTOrgUseCase <https://ncar.github.io/METplus/search.html?q=NOAAHMTOrgUseCase&check_keywords=yes&area=default>`_,
#    `GEMPAKFileUseCase <https://ncar.github.io/METplus/search.html?q=GEMPAKFileUseCase&check_keywords=yes&area=default>`_,
#    `NCAROrgUseCase <https://ncar.github.io/METplus/search.html?q=NCAROrgUseCase&check_keywords=yes&area=default>`_,
#    `NOAAWPCOrgUseCase <https://ncar.github.io/METplus/search.html?q=NOAAWPCOrgUseCase&check_keywords=yes&area=default>`_,
#    `DiagnosticsUseCase <https://ncar.github.io/METplus/search.html?q=DiagnosticsUseCase&check_keywords=yes&area=default>`_
