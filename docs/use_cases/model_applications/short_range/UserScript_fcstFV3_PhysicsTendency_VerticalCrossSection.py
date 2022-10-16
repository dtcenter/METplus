"""
UserScript: Physics Tendency Vertical Cross Section plot
=========================================================================

model_applications/
short_range/
UserScript_fcstFV3_PhysicsTendency_VerticalCrossSection.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# To plot tendencies of temperature, moisture, and wind components averaged over 
# a time window and spatial domain.  Tendencies are partitioned into physics 
# parameterizations and dynamics.  Physics parameterizations include schemes like 
# deep convection, convective gravity wave drag, short wave radiatioin, plantetary
# boundary layer, microphysics, and others.  Non-physics tendencies (or dynamics)
# are due to horizontal and vertical motion.  The residual (which should be zero)
# is the difference between the actual change in the state variable over the requested
# time window and the expected change due to physics parameterizations and dynamics
# tendencies.  One can plpt a single tendency component at multiple pressure levels or
# plot all tendency components at a single pressure level.  This use case illustrates 
# how to generate vertical cross section plots.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: FV3 Model member data
#  * Grid specification: Grid specification data 
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the METplotpy planview_fv3.py script to generate the plan views. 

##############################################################################
# METplus Workflow
# ----------------
#
#
# | **Valid:** 2019-05-21_01Z
# | **Forecast lead:** 01
# |
#
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/short_range/UserScript_fcstFV3_PhysicsTendency_Planview.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstFV3_PhysicsTendency_Planview.conf

##############################################################################
# MET Configuration
# ---------------------
#
# No MET tools are used in this use case.
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# .. note:: See the :ref:`MODE MET Configuration<mode-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run in the following way: 
#
# 1) Passing in MODE_fcstFV3_obsGOES_BrightnessTemp.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTemp.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in MODE_fcstFV3_obsGOES_BrightnessTemp.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/MODE_fcstFV3_obsGOES_BrightnessTemp.conf
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
# Output for this use case will be found in short_range/brightness_temperature
# (relative to **OUTPUT_BASE**) and will contain the following files:
#
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_cts.txt
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.nc
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA_obj.txt
# mode_FV3_core_lsm1_010000L_20190521_010000V_NAA.ps
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_cts.txt
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.nc
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA_obj.txt
# mode_FV3_core_lsm1_010000L_20190521_020000V_NAA.ps
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_cts.txt
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.nc
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA_obj.txt
# mode_FV3_core_mp1_010000L_20190521_010000V_NAA.ps
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_cts.txt
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.nc
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA_obj.txt
# mode_FV3_core_mp1_010000L_20190521_020000V_NAA.ps


##############################################################################
# Keywords
# --------
#
#
# .. note::
#
#   * MediumRangeAppUseCase
#   * PhysicsTendency
#   * ValidationUseCase
#   * ShortRangeAppUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-MODE_fcstFV3_obsGOES_BrightnessTemp.png'
#
