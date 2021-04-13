"""
TCGen: Genesis Density Function (GDF) and Track Density Function (TDF) 
=============================================================================

model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# 
# Tropocal cyclone (TC) genesis density function (GDF) and track density function (TDF) are designed to
# quantitatively evaluate geographic distributions of TC activities including TC genesis frequency and
# subsequent TC tracks. Spatial patterns of long-term averaged GDF or TDF on the regional or global scale
# are particularly useful to evaluate TC forecasts against those derived from an observational best-track
# dataset, such as IBTrACS or ATCF B-decks, from a climate perspective. The metrics can help assess the forecast biases
# (under- or over-prediction) of TC formations or TC vortices around particular locations in a numerical model.
#

##############################################################################
# Datasets
# --------
#
# Both forecast and observation datasets for this use case must adhere to the ATCF format.
#
# **Forecast data:**
# GFDL Cyclone Tracker output configured for "genesis mode" for the Global Forecast System (GFS) model
#
# **Observation data:**
# Global ATCF B-decks files from the National Hurricane Center (NHC) and Joint Typhoon Warning Center (JTWC)
#
# **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. 
# Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See ‘Running METplus’ section for more information.
#
# The MET TCGen tool requires forecast data to be provided from the GFDL cyclone tracker. More information
# about the GFDL cyclone tracker can be found here: https://dtcenter.org/community-code/gfdl-vortex-tracker
#
# Archives of ATCF B-decks files can be found at these locations:
#
# | https://www.metoc.navy.mil/jtwc/jtwc.html?best-tracks
# | https://www.nhc.noaa.gov/data/#hurdat
# |
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the MET TCGen tool to generate matched pairs of TC genesis,
# and then uses Python Embedding to compute the TDF and GDF metrics and create graphics for
# the year 2016.
#

##############################################################################
# METplus Workflow
# ----------------
#
# The following tools are used for each run time: TCGen, Python
#
# The TCGen tool is designed to be provided a single file pair or a directory containing a list of files,
# rather than loop over valid or initialization times. Thus, a single year is used in the METplus configuration
# file and wildcard symbols are provided to gather all the tracker and genesis input files at each
# input directory.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf
#

##############################################################################
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
# **TCGenConfig_wrapped**
#
# .. note:: See the :ref:`TCGen MET Configuration<tc-gen-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCGenConfig_wrapped
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses a Python embedding script to create output graphics
#
# parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF/UserScript_fcstGFSO_obsBDECKS_GDF_TDF.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF/UserScript_fcstGFSO_obsBDECKS_GDF_TDF.py
#

##############################################################################
# Running METplus
# ---------------
# This use case can be run two ways:
#
# 1) Passing in TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [config]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
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
#
# Output from TCGen for this use case will be found in model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF/TCGen (relative to **OUTPUT_BASE**)
#
# For each month and year there will be five files written::
#
# * tc_gen_2016_pairs.nc
# * tc_gen_2016_genmpr.txt
# * tc_gen_2016_ctc.txt
# * tc_gen_2016_cts.txt
# * tc_gen_2016.stat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#    `TCGenToolUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=TCGenToolUseCase&check_keywords=yes&area=default>`_
#    `S2SAppUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=S2SAppUseCase&check_keywords=yes&area=default>`_
#    `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_
#
# sphinx_gallery_thumbnail_path = '_static/s2s-TCGen_fcstGFSO_obsBDECKS_GDF_TDF.png'
#
