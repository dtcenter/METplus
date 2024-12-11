"""
Surrogate Severe Calculation: PCPCombine, GenEnsProd, and RegridDataPlane
=========================================================================

model_applications/short_range/GenEnsProd_fcstHRRR_fcstOnly_SurrogateSevere.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

###################################################################################################
# Scientific Objective
# --------------------
#
# Run PCPCombine, GenEnsProd, and RegridDataPlane tools to create surrogate severe probability
# forecasts (SSPFs) for a given date. SSPFs are a severe weather forecasting tool and is a technique
# used by the Storm Prediction Center (SPC) as well as others. SSPFs are based on updraft helicity
# (UH; :math:`\text{UH} = \int_{z_0}^{z_t} ( \omega * \zeta ) dz`) since certain thresholds of UH
# have been shown as good proxies for severe weather. SSPFs can be thought of as the perfect model
# forecast. They are derived as follows:
#
#    1. Regrid the maximum UH value over the 2-5km layer at each grid point to the NCEP 211 grid (dx = ~80km).
#    2. Create a binary mask of points that meet a given threshold of UH.
#    3. Convert the binary mask into a probability field by applying a Gaussian filter.
# 
# For more information, please reference Sobash et al. 2011 (https://journals.ametsoc.org/doi/full/10.1175/WAF-D-10-05046.1).

##############################################################################
# Version Added
# -------------
#
# METplus version 3.1

###############################################################################
# Datasets
# --------
#
# **Forecast:** 
#
# **Observation:**
#
# **Climatology:** None
#
# **Location:** All of the input data required for this use case can be 
# found in a sample data tarball. Each use case category will have 
# one or more sample data tarballs. It is only necessary to download 
# the tarball with the use case’s dataset and not the entire collection 
# of sample data. Click here to access the METplus releases page and download sample data 
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will 
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.

# **Data Source:** Originally received from Burkely Gallo at the Storm Prediction Center. 

# There are two dates that can be used as input data for this use case 20190518 or 20200205.
# 
# * Input Data: HRRR data
#   - There should 24 grib2 files.
#   - Variable of interest: MXUPHL; the maximum updraft helicity
#   - Level: Z2000-5000; from 2 - 5km
#   - Format: grib2
#   - Projection: Lambert Conformal

###################################################################################################
# METplus Components
# ------------------
#
# This use case runs the PCPCombine, GenEnsProd, and RegridDataPlane MET tools.

###################################################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2020020500
#
# **End time (INIT_END):** 2020020500
#
# **Increment between beginning and end times (INIT_INCREMENT):** 86400
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 36
#
# This workflow loops over the data by process, meaning that each MET tool will run over all times
# before moving onto the tool. PCPCombine is called first, followed by GenEnsProd,
# and then, finally, RegridDataPlane.

###################################################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# i.e. parm/use_cases/model_applications/short_range/GenEnsProd_fcstHRRR_fcstOnly_SurrogateSevere.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GenEnsProd_fcstHRRR_fcstOnly_SurrogateSevere.conf

###################################################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus configuration file. 
# See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details. 
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently not supported by METplus you'd like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: GenEnsProdConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GenEnsProdConfig_wrapped

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

###################################################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GenEnsProd_fcstHRRR_fcstOnly_SurrogateSevere.conf
#
# See :ref:`running-metplus` for more information.

###################################################################################################
# Expected Output
# ---------------

# A successful run of this use case will output the following to the screen and logfile::
#  
#    INFO: METplus has successfully finished runing.
#
# A successful run will have the following output files in the location defined by {OUTPUT_BASE}, which
# is located in the metplus_system.conf configuration file located in /path/to/METplus/parm/metplus_config.
# This list of files should be found for every time run through METplus. Using the output for 20190518 as an example.
#
# **PCPCombine output**:
#
# * 20190518/hrrr_ncep_2019051800f036.nc
#
# **GenEnsProd output**:
#
# * gen_ens_prod_20190519_120000V_ens.nc
#
# **RegridDataPlane output**:
# 
# * surrogate_severe_20190518_036V_regrid.nc
#

###################################################################################################
# Keywords
# --------
#
# .. note::
#
#   * PCPCombineUseCase
#   * GenEnsProdUseCase
#   * RegridDataPlaneUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-GenEnsProd_fcstHRRR_fcstOnly_SurrogateSevere.png'
#
