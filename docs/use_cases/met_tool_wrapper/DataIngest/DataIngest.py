"""
DataIngest: Basic Use Case
============================================================================

met_tool_wrapper/DataIngest/DataIngest.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Download input files and optionally decompress them.

##############################################################################
# Datasets
# --------
#
# | **Inputs:** None

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus DataIngest wrapper to download and
# decompress input files.

##############################################################################
# METplus Workflow
# ----------------
#
# **Beginning time (VALID_BEG):** 2022-07-20 0Z
#
# **End time (VALID_END):** 2022-07-20 12Z
#
# **Increment between beginning and end times (VALID_INCREMENT):** 12 hours
#
# **Sequence of forecast leads to process (LEAD_SEQ):** None
#
# DataIngest is the only tool called in this example.
# It has two run times.
# The MADIS data is hourly, so two files are downloaded.
# The Surfrad data is daily, so one file is downloaded.
# The MADIS files are compressed with gzip compression, so they are
# automatically decompressed into NetCDF format.
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line,
# i.e. parm/use_cases/met_tool_wrapper/DataIngest/DataIngest.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/DataIngest/DataIngest.conf

##############################################################################
# MET Configuration
# -----------------
#
# None.
#

##############################################################################
# Python Embedding
# ----------------
#
# This use case does not use Python Embedding.

##############################################################################
# User Scripting
# --------------
#
# This user case does not call a user-defined script.

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script along
# with any user-specific system configuration files if desired::
#
#   run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/DataIngest/DataIngest.conf /path/to/user_system.conf
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
# Output for this use case will be found in data_ingest (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * madis_metar/20220720_0000.nc
# * madis_metar/20220720_1200.nc
# * surfrad/tbl20220720.dat
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * DataIngestToolUseCase
#   * MADISFileUseCase
#   * NetCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
