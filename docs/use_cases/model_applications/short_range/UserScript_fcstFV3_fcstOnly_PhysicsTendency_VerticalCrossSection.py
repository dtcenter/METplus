"""
UserScript: Physics Tendency Vertical Cross Section plot
=========================================================================

model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# To plot tendencies of temperature, moisture, and wind components averaged over 
# a time window and spatial domain.  Tendencies are partitioned into physics 
# parameterizations and dynamics.  Physics parameterizations include schemes like 
# deep convection, convective gravity wave drag, short wave radiation, plantetary
# boundary layer, microphysics, and others.  Non-physics tendencies (or dynamics)
# are due to horizontal and vertical motion.  The residual (which should be zero)
# is the difference between the actual change in the state variable over the requested
# time window and the expected change due to physics parameterizations and dynamics
# tendencies.  One can plot a single tendency component at multiple pressure levels or
# plot all tendency components at a single pressure level.  This use case illustrates 
# how to generate the vertical cross section plot. The METplotpy source code is needed to generate the plot.
# Clone the METplotpy repository (https://github.com/dtcenter/METplotpy) under the same base
# directory as the METPLUS_BASE directory so that the METplus and
# METplotpy directories are under the same base directory (i.e. if the METPLUS_BASE directory is
# /home/username/working/METplus, then clone the METplotpy source
# code into the /home/username/working directory).


##############################################################################
# Datasets
# --------
#
# | Forecast dataset: FV3 3-D history file with physics and dynamics tendencies
# | Grid specification: FV3 2-D grid specification file with latitude and longitude of each grid point
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#



##############################################################################
# External Dependencies 
# ---------------------
# You will need to use a versio of Python 3.86 that has the following packages
# installed:
#
#  * cartopy (0.20.3 only)
#  * matplotlib
#  * metpy
#  * numpy
#  * pandas
#  * shapely
#  * xarray
#



##############################################################################
# METplus Components
# ------------------
#
# This use case runs the METplotpy cross_section_vert.py script to generate the plan views.
#

##############################################################################
# METplus Workflow
# ----------------
#
# This use case does not loop but plots physics tendency data that has been
# subsetted to one date: 2019-05-04.
# 


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# i.e.  parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf
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
# 1) Passing in UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf then a user-specific system configuration file::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf  /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf::
#
#        run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf
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
# short_range-physics_tendency_vertical_cross_section.png
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
#   * S2SAppUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.png'
#
