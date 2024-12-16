"""
UserScript: Physics Tendency Vertical Cross Section plot
========================================================

model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf

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
# Version Added
# -------------
#
# METplus version 5.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** FV3 3-D history file with physics and dynamics tendencies
#
# **Observation:** [UPDATE_SECTION_CONTENT]
#
# **Climatology:** [UPDATE_SECTION_CONTENT]
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#
# **Grid specification:** FV3 2-D grid specification file with latitude and longitude of each grid point

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

##############################################################################
# METplus Components
# ------------------
#
# This use case runs the METplotpy cross_section_vert.py script to generate the plan views.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2019
#
# This use case does not loop but plots physics tendency data that has been
# subsetted to one date: 2019-06-15.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf

##############################################################################
# MET Configuration
# -----------------
#
# No MET tools are used in this use case.

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# User Scripting is not used in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstFV3_fcstOnly_PhysicsTendency_VerticalCrossSection.conf  /path/to/user_system.conf
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
# The following file will be created:
#
# short_range-physics_tendency_vertical_cross_section.png

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
