"""
PCP-Combine: Compute 1m Soil Moisture and 30 year Climatology
=============================================================

model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.conf

"""

##############################################################################
# Scientific Objective
# --------------------
#
# This use case performs pre-processing on Soil Moisture data to prepare it to
# be run through Grid-Stat or another program for verification.  As part of that
# pre-processing, 1 m soil moisture is calculated by adding the soil moisture for
# the top three layers (0-7cm, 7-28 cm, 28-100 cm), each multipled by the layer 
# thickness.  After 1m soil moisture is calculated for each month, a 30 year 
# climatology is calculated by computing the mean and standard deviation for 
# each month between 1991 and 2020.

##############################################################################
# Version Added
# -------------
#
# METplus version 6.1

##############################################################################
# Datasets
# --------
#
# **Forecast:** None
#
# **Observation:** ERA-5 Land Soil Moisture top 3 layers
#
# **Climatology:** None
#
# **Location:** The input data required for PCP-Combine in this use case can be
# found in a sample data tarball. Each use case category will have
# one or more sample data tarballs. It is only necessary to download
# the tarball with the use case’s dataset and not the entire collection
# of sample data. Click here to access the METplus releases page and download sample data
# for the appropriate release: https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will
# set the value of INPUT_BASE. See :ref:`running-metplus` section for more information.
#
# Data for the Regrid-Data-Plane runsis not contained in the sample data tar files due
# to its size. Rather, it is stored as additional data in a separate tar file, named
# additional_data_PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.tar.gz and can be
# downloaded at https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/v6.1/.

##############################################################################
# METplus Components
# ------------------
#
# This use case calls PCP-Combine twice.  There is an additional call to
# Regrid-Data-Plane that is commented out but may be turned back on by the user.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 1991-01-01
#
# **End time (VALID_END):** 2020-12-01
#
# **Increment between beginning and end times (VALID_INCREMENT):** 1 month
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 0
#
# The first PCP-Combine run computes the sum of soil moisture of the top three layers
# multiplied by the thickness of each layer.  It loops over valid time, running once for
# each valid time which is monthly data for 1991 through 2020.  This is a total of 360
# PCP-Combine runs.  The second call to PCP-Combine computes a 30 year mean and standard
# deviation.  It runs once for each month, for a total of 12 runs
#
# When turned on, Regrid-Data-Plane regrids the data to a 1 degree latitude/longitude grid.
# Like the first PCP-Combine run, it loops over valid time, running once for each month
# between 1991 and 2020, for a total of 360 runs. Regrid-Data-Plane can be turned back on
# by using the PROCESS_LIST that is commented out:
#
# PROCESS_LIST = RegridDataPlane, PcpCombine(create_1m), PcpCombine(obs_mean_stdev)
#
# Settings for the Regrid-Data-Plane run are provided in the configuration file.  Data is
# not included in the tarball, but can be downloaded from the link provided in the Datasets
# section above.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.conf

#############################################################################
# MET Configuration
# ---------------------
#
# There are no MET configuration files in this use case.

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# There are no user scripts in this use case.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.conf /path/to/user_system.conf
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
# Output for this use case will be found in
# {OUTPUT_BASE}/model_applications/s2s/PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.
# Output from the first netCDF run will be in the ERA5_land_soilm1m subdirectory and will
# contain 360 files, one for each month, with the format shown below (for January and
# February 1991)::
#
#  * ERA5_soilm1m_1x1_mon_199101.nc
#  * ERA5_soilm1m_1x1_mon_199102.nc
#
# Output from the second call to PCP-Combine will be in the ERA5_land_clim subdirectory
# and will contain 12 files::
#
#  * ERA5_soilm1m_1x1_30year_1991_2020_01_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_02_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_03_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_04_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_05_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_06_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_07_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_08_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_09_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_10_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_11_mean_stdev.nc
#  * ERA5_soilm1m_1x1_30year_1991_2020_12_mean_stdev.nc
#
# The netCDF output files for the first PCP-Combine run contains one variable (not
# including the lat/lon fields)::
#
#  * soilm1m(lat, lon)
#
# The netCDF output files for the second PCP-Combine run contains two variables (not
# including the lat/lon fields)::
#
#  * soilm1m_mean(lat, lon)
#  * soilm1m_stdev(lat, lon)
#
# If the Regrid-Data-Plane step is turned on 360 regridded files will be output to
# the ERA5_land_regrid subdirectory.

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * S2SAppUseCase
#   * PCPCombineToolUseCase
#   * RegridDataPlaneToolUseCase
#   * NetCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/s2s-PcpCombine_obsERA5_obsOnly_soilMoisturePreProcessing.png'
