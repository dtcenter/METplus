"""
Point-Stat: Standard Verification for CONUS Surface 
==============================================================================

model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD
_NetCDF.conf

"""
##############################################################################
# Scientific Objective
# --------------------
# To provide useful statistical information on the relationship between observation data
# in point format to a gridded forecast. These values can be used to assess the skill 
# of the prediction. Statistics are store as partial sums to save space and Stat-Analysis
# must be used to compute Continuous statistics.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** HAFS temperature
# | **Observation:** HRD Dropsonde data 
#
# | **Location of Model forecast and Dropsonde files:** All of the input data required for this use case can be found in the sample data tarball. Click `here <https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data>`_ to download.
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See `Running METplus`_ section for more information.
#
# | **Dropsonde Data Source:** `Hurricane Research Division Sonde Archive  <https://www.aoml.noaa.gov/hrd/data_sub/dropsonde.html>`_
# |
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus ASCII2NC wrapper to convert full-resolution data (frd) dopsonde point observations to NetCDF format and then compare them to gridded forecast data using PointStat.


##############################################################################
# METplus Workflow
# ----------------
#
# The use case runs the UserScript wrapper (untar the dropsonde file and extract the files to a directory), ASCII2NC (convert the ascii files to NetCDF format), and PointStat (compute statistics against HAFS model output), which are the tools called in this example. It processes the following run times:
#
# | **Valid:** 2019-08-29 12Z
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf
#
# Notes for USER_SCRIPT* METplus conf items for this use case:
#
# * **${USER_SCRIPT_RUNTIME_FREQ}** - Corresponds to USER_SCRIPT_RUNTIME_FREQ in the METplus configuration file.
# * **${USER_SCRIPT_INPUT_DIR}** - Corresponds to USER_SCRIPT_INPUT_DIR in the METplus configuration file.
# * **${USER_SCRIPT_OUTPUT_DIR}** - Corresponds to USER_SCRIPT_OUTPUT_DIR in the METplus configuration file.
# * **${USER_SCRIPT_COMMAND}** - Arguments needed to hrd_frd_sonde_find_tar.py corresponds to USER_SCRIPT_INPUT_TEMPLATE.
# * **${USER_SCRIPT_INPUT_TEMPLATE}** - Input template to hrd_frd_sonde_find_tar.py: USER_SCRIPT_INPUT_DIR, valid date (%Y%m%d), and USER_SCRIPT_OUTPUT_DIR.

##############################################################################
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
# **Ascii2NcConfig_wrapped**
#
# .. note:: See the :ref:`ASCII2NC MET Configuration<ascii2nc-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/Ascii2NcConfig_wrapped
#
# **PointStatConfig_wrapped**
#
# .. note:: See the :ref:`PointStat MET Configuration<point-stat-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case uses two Python embedding scripts: one to download the data (hrd_frd_sonde_find_tar.py) and the other to process it (hrd_frd_sonde_for_ascii2nc.py).
#
# parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_find_tar.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_find_tar.py
#
# parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_for_ascii2nc.py
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF/hrd_frd_sonde_for_ascii2nc.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications//tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf:
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.conf
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

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in nam (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * point_stat_180000L_20190829_120000V.stat
# * point_stat_180000L_20190829_120000V_fho.txt
# * point_stat_180000L_20190829_120000V_eclv.txt
# * point_stat_180000L_20190829_120000V_ctc.txt
# * point_stat_180000L_20190829_120000V_cnt.txt
# * point_stat_180000L_20190829_120000V_mpr.txt

##############################################################################
# Keywords
# --------
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF.png'
#
# .. note:: `TCandExtraTCAppUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=TCandExtraTCAppUseCase&check_keywords=yes&area=default>`_, `UserScriptUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=UserScriptUseCase&check_keywords=yes&area=default>`_, `PointStatToolUseCase <https://dtcenter.github.io/METplus/develop/search.html?q=PointStatToolUseCase&check_keywords=yes&area=default>`_, `ASCII2NC <https://dtcenter.github.io/METplus/search.html?q=ASCII2NCToolUseCase&check_keywords=yes&area=default>`_
