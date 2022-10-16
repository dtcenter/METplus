"""
UserScript: Physics Tendency Vertical Profile plot
=========================================================================

model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf

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
# how to generate the vertical profile plot.

##############################################################################
# Datasets
# --------
#
#  * Forecast dataset: FV3 Model member data
#  * Grid specification: Grid specification data
#  * Mid-CONUS Shapefiles: (uncompress and place under shapefile/MID_CONUS directory under the appropriate METPLUS_DATA directory)
#    * MID_CONUS.cpg
#    * MID_CONUS.dbf
#    * MID_CONUS.poly
#    * MID_CONUS.prj
#    * MID_CONUS.shp
#    * MID_CONUS.shx
#
#

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the METplotpy vert_profile_fv3.py script to generate the plan views.
#

##############################################################################
# METplus Workflow
# ----------------
#
#
# | This use case does not loop but plots physics tendency data that has been
# | subsetted to one date: 2019-05-04.
# |


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e.  parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf
#

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
# 1) Passing in UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf  /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.conf
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
# The following file will be created:
#
# short_range-physics_tendency_vertical_profile.png
#
#


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
# sphinx_gallery_thumbnail_path = '_static/short_range-UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalProfile.png'
#
