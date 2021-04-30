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
# For demonstration purposes, only cyclone tracker output and b-decks data for 2016 are used.
# 
# The following settings are used in the use case, all of which are configurable in the METplus configuration file (see below).
#
# Forecast genesis event criteria:
#
# | Minimum forecast lead: 48h
# | Maximum forecast lead: 120h
# | Maximum velocity threshold: >= 16.5 m/s
# | Minimum TC duration: 24h
# |
#
# Observed genesis event criteria:
#
# | Minimum TC duration: 24h
# | Maximum velocity threshold: >= 17.0 m/s
# | Minimum TC Category: TD
# |
#
# Matching settings:
#
# | Genesis matching window: +/- 24h
# | Early genesis matching window: -120h
# | Late genesis matching window: +120h
# | Genesis hit scoring window: +/- 24h
# | Early genesis hit scoring window: -120h
# | Late genesis hit scoring window: +120h
# | Matching and Scoring radius: 555 km
# | 
#
# In addition to the above settings, normalization is performed on the metrics by the number of years included in the dataset
# (in this example, just one), and the total number of model forecasts valid at the time of an observed genesis event. The latter
# can also be thought of as the total number of chances that the model had to forecast a genesis event.
#

##############################################################################
# Datasets
# --------
#
# Both forecast and observation datasets for this use case must adhere to the ATCF format.
#
# **Forecast data:**
# GFDL Cyclone Tracker output configured for "genesis mode" for the FV3GFS model. This configuration used an experimental GFSv15 physics package,
# and had a horizontal grid spacing of ~25 km with 64 vertical levels.
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
# Software Versions
# -----------------
#
# This use case was developed with specific versions of various software and Python packages. Any deviation from these versions
# may require re-configuration or adaptation to reproduce the results shown.
#
# Names and version numbers::
#
#  python-3.6.3
#  cartopy-0.18.0
#  matplotlib-3.1.2
#  MET-10.0.0
#  METplus-4.0.0
#  METplotpy-1.0.0
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
