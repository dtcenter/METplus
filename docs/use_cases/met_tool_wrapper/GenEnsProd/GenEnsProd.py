"""
GenEnsProd: Basic Use Case
==========================

met_tool_wrapper/GenEnsProd/GenEnsProd.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Generate ensemble products.

##############################################################################
# Datasets
# --------
#
# **Input:** WRF ARW ensemble 24 hour precipitation accumulation
#
# **Location:** All of the input data required for this use case can be found
# in the met_test sample data tarball. Click here to the METplus releases
# page and download sample data for the appropriate release:
# https://github.com/dtcenter/METplus/releases
# This tarball should be unpacked into the directory that you will set the
# value of INPUT_BASE. See the `Running METplus`_ section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus GenEnsProd wrapper to generate a command
# to run the MET tool gen_ens_prod if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# GenEnsProd is the only tool called in this example.
# It processes the following run time(s):
#
# | **Initialization:** 2009-12-31 12Z
# | **Forecast Lead:** 24 hour
# |
#

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/GenEnsProd/GenEnsProd.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/GenEnsProd/GenEnsProd.conf

##############################################################################
# MET Configuration
# ---------------------
#
# .. note::
#     See the :ref:`GenEnsProd MET Configuration<gen-ens-prod-met-conf>`
#     section of the User's Guide for more information on the environment
#     variables used in the file below.
#
# parm/met_config/GenEnsProdConfig_wrapped
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/GenEnsProdConfig_wrapped
#

##############################################################################
# Running METplus
# ---------------
#
# Provide the use case .conf configuration file to the run_metplus.py script.
#
# /path/to/METplus/parm/use_cases/met_tool_wrapper/GenEnsProd/GenEnsProd.conf
#
# See the :ref:`running-metplus` section of the System Configuration chapter
# for more details.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following to the screen and the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data
# was generated. Output for this use case will be found in
# met_tool_wrapper/gen_ens_prod
# (relative to **OUTPUT_BASE**)
# and will contain the following file(s):
#
# * gen_ens_prod_20100101_120000V_ens.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * GenEnsProdToolUseCase
#   * GRIBFileUseCase
#   * EnsembleAppUseCase
#
#   Navigate to :ref:`quick-search` to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-GenEnsProd.png'
#
