"""
GenEnsProd: Basic Use Case
==========================

met_tool_wrapper/GenEnsProd/GenEnsProd.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Generate ensemble products. This use case demonstrates how to configure
# the gen_ens_prod tool if you expect that there will occasionally be missing
# ensembles. 7 ensemble paths are specified but only 6 of them exist in the
# sample input data set. The wrapper will mark ensembles that are not found
# with the MISSING keyword in the file-list file that is read by the tool.
# Also, one of the ensembles is listed as the control member. The gen_ens_prod
# application will error and exit if the control member is included in the
# ensemble list, but the GenEnsProd wrapper will automatically remove the
# control member from the ensemble list. This makes it easier to configure
# the tool to change the control member without having to change the ensemble
# list. The number of expected members (defined with GEN_ENS_PROD_N_MEMBERS)
# is 6 (7 members - 1 control member). The actual number of ensemble members
# that will be found in this example is 5 (arw-tom-gep4 is not included).
# The ens.ens_thresh value (defined by GEN_ENS_PROD_ENS_THRESH) is set to 0.8.
# There are ~0.833 (5/6) valid ensemble members so the application will run.

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
# A file-list file will also be generated in stage/file_lists called:
#
# * 20091231120000_24_gen_ens_prod.txt
#
# It should contain a list of 6 files in {INPUT_BASE} with 1 file marked as
# missing because it was not found::
#
#    file_list
#    {INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-sch-gep2/d01_2009123112_02400.grib
#    {INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-tom-gep3/d01_2009123112_02400.grib
#    MISSING/{INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-tom-gep4/d01_2009123112_02400.grib
#    {INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-fer-gep5/d01_2009123112_02400.grib
#    {INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-sch-gep6/d01_2009123112_02400.grib
#    {INPUT_BASE}/met_test/data/sample_fcst/2009123112/arw-tom-gep7/d01_2009123112_02400.grib
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
