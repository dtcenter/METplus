"""
GridDiag: Compute Energy Spectra and Error Spectra
==================================================

model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra.conf

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
# This use case shows how to set up and compute both energy spectra and error
# spectra on regional forecast data.  The spectra are computed using a discrete
# cosine transform using the methods described in Denis et al. 2002 and Durran et
# al. 2017.  It also creates a graphic to display error spectra.
#
#  * Denis, B., J Cote, and R. Laprise, 2002: Spectral Decomposition of Two-Dimensional Atmospheric Fields on Limited-Area Domains Using the Discrete Cosine Transform (DCT).  Monthly Weather Review, 130, 1812 - 1829, https://doi.org/10.1175/1520-0493(2002)130%3C1812:SDOTDA%3E2.0.CO;2.
#  * Durran, D., J. A. Weyn, and M. Q. Menchaca, 2017:  Practical Considerations for Computing Dimensional Spectra from Gridded Data, Monthly Weather Review, 145, 3901 - 3910, https://doi.org/10.1175/MWR-D-17-0056.1.

##############################################################################
# Version Added
# -------------
#
# METplus version 13.0

##############################################################################
# Datasets
# --------
#
# **Forecast:** RRFS FV3 model from ensemble member 1
#
# **Observation:** None
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
# This use case calls GridDiag and UserScript once.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (INIT_BEG):** 2023-09-15
#
# **End time (INIT_END):** 2023-09-15
#
# **Increment between beginning and end times (INIT_INCREMENT):** 1 day
#
# **Sequence of forecast leads to process (LEAD_SEQ):** 1, 3, 6, 12, 24
#
# For one model initialization, the 1, 3, 6, 12, and 24 hour lead times are run through
# Grid-Diag to compute both energy spectra and error spectra.  Then, UserScript is called
# once to create a graphic displaying the error spectra for all forecast lead times.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, 
# then it loads any configuration files passed to METplus via the command line, 
# e.g., parm/use_cases/model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra.conf

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
# .. dropdown:: GridDiagConfig_wrapped
#
#   .. literalinclude:: ../../../../parm/met_config/GridDiagConfig_wrapped

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python embedding.

##############################################################################
# User Scripting
# --------------
#
# This use case uses a Python script to perform plotting, specifically to create
# an image of the output error spectra.  In order to create the plots, the script 
# reads in the data output from GridDiag.  Then it sets up the plot axes and graphs
# the error spectra. 
#
# .. dropdown:: parm/use_cases/model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra/plot_energy_spectra.py
# 
#   .. highlight:: python
#   .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra/plot_energy_spectra.py

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along 
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/model_applications/short_range/GridDiag_fcstFV3_fcstOnly_EnergySpectra.conf /path/to/user_system.conf
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
# Output will contain the following files:
#
#  * energy_spectra_FV3_2023091500_f001.nc
#  * energy_spectra_FV3_2023091500_f003.nc
#  * energy_spectra_FV3_2023091500_f006.nc
#  * energy_spectra_FV3_2023091500_f012.nc
#  * energy_spectra_FV3_2023091500_f024.nc
#
# The output will also contain the energy spectra graphic:
#
#  * Grid_Diag_Spectra_FV3_multiple_leads.png
#
# For the netCDF files, five variable fields are present (not including the lat/lon fields). 
# Those variables are:
#
#  * wavenumber(wavenumber)
#  * wavelength(wavenumber)
#  * power_spectrum_KENG_CTRL_P500(wavenumber)
#  * power_spectrum_KENG_EXPT_P500(wavenumber)
#  * error_power_spectrum_KENG_CTRL_P500_KENG_EXPT_P500(wavenumber)

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GridDiagToolUseCase
#   * UserScriptUseCase
#   * ShortRangeAppUseCase
#   * NetCDFFileUseCase
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
# sphinx_gallery_thumbnail_path = '_static/short-range-GridDiag_fcstFV3_fcstOnly_EnergySpectra.png'
