"""
PointStat: Hurricane Matthew I-WRF
==================================

model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf

"""
##############################################################################
# .. contents::
#   :depth: 1
#   :local:
#   :backlinks: none

##############################################################################
# Scientific Objective
# --------------------
# [UPDATE_SECTION_CONTENT]
#
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
# **Forecast:** WRF, temperature and wind
#
# **Observation:** MADIS RAOB and METAR
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

##############################################################################
# METplus Components
# ------------------
#
# This use case calls 2 instances of MADIS2NC to convert the RAOB and METAR
# observations to NetCDF.
# Then 2 instances of PointStat are called to process surface and
# upper air fields.
# Next, UserScript is used to call a python script to plot the WRF data.
# Finally, another UserScript instance calls a METdataio script to reformat
# the PointStat output and a METplotpy script to produce a line plot.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2016-10-06 00Z
#
# **End time (INIT_END):** 2016-10-06 00Z
#
# **Increment between beginning and end times (INIT_INCREMENT):** 6 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48
#
# The MADIS2NC instances process every forecast lead from 0-48.
# The RAOB MADIS2NC instance has missing data for a few of the leads,
# so a missing data threshold of 87.5% is set to prevent errors.
# The surface instance of PointStat allows a +/- 30 minute window for observations and
# includes files from the previous hour.
# The upper air instance of PointStat allows +/- 90 minute window for observations and
# includes files from +/- 2 hours around the valid time.


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line:
# parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf

##############################################################################
# MET Configuration
# -----------------
#
# METplus sets environment variables based on user settings in the METplus
# configuration file. See :ref:`How METplus controls MET config file settings<metplus-control-met>` for more details.
#
# **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!**
#
# If there is a setting in the MET configuration file that is currently
# not supported by METplus you’d like to control, please refer to:
# :ref:`Overriding Unsupported MET config file settings<met-config-overrides>`
#
# .. dropdown:: PointStatConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/PointStatConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python Embedding.

##############################################################################
# User Scripting
# --------------
# [UPDATE_SECTION_CONTENT]
#
# This use case uses a Python script to perform plotting, which at the time of 
# this use case creation was not an ability METplus had. Additionally some of 
# the plotting features used in this script are not currently slated for METplus 
# analysis suite development.
# In order to create the plots, the script reads in a yaml file and sets up 
# the correct environment. Plot parameters (which are hard coded in the script) are set, 
# and the datasets are read in from the input file. The desired variable fields 
# are placed into arrays, which are then treated for bad data and squeezed to the 
# appropriate dimensions. Additional basic math is completed on the resulting arrays 
# to create the cross spectra values with the results being graphed.
#
# .. dropdown:: parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra/cross_spectra_plot.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/tc_and_extra_tc/PointStat_fcstWRF_obsMADIS_hurricane_matthew.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.

##############################################################################
# Expected Output
# ---------------
# [UPDATE_SECTION_CONTENT]
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated. 
# Output for this use case will be found in {OUTPUT_BASE}
# and will contain the following files::
#
#  * grid_stat_198201_000000L_19700101_000000V_pairs.nc
#  * grid_stat_198201_000000L_19700101_000000V_pstd.txt
#  * grid_stat_198201_000000L_19700101_000000V.stat
#
# Each file should contain corresponding statistics for the line type(s) requested.
# For the netCDF file, five variable fields are present (not including the lat/lon fields). 
# Those variables are::
#
#  * FCST_fcst_ENS_FREQ_lt-0.43_0_0_all_all_FULL(lat, lon)
#  * OBS_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_MEAN_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_STDEV_tmp2m_20100101_000000_all_all_FULL(lat, lon)
#  * CLIMO_CDF_tmp2m_20100101_000000_all_all_FULL(lat, lon)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCandExtraTCAppUseCase
#   * PointStatToolUseCase
#   * METplotpyUseCase
#   * UserScriptUseCase
#   * WRFFileUseCase
#   * MADIS2NCToolUseCase
#   * GRIB2FileUseCase
#   * MADISFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/tc_and_extra_tc-PointStat_fcstWRF_obsMADIS_hurricane_matthew.png'
