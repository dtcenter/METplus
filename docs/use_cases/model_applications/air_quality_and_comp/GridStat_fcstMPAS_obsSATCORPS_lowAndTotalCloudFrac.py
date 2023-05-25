"""
GridStat: Cloud Fractions with Various Settings
===============================================

model_applications/air_quality_and_comp/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# This use case captures various statistical measures of two model comparisons
# for low and total cloud fraction with different neighborhood and probability
# settings for internal model metrics and to aid in future model updates
# 

##############################################################################
# Datasets
# --------
#
# | **Forecast:** Model for Prediction Across Scales (MPAS)
# | **Observations:** Satellite ClOud and Radiation Property retrieval System (SatCORPS)
# | **Grid:** GPP 17km masking region
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/dtcenter/METplus/releases
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus PlotPointObs wrapper to generate a
# command to run the MET tool plot_point_obs if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# PlotPointObs is the only tool called in this example.
# It processes the following run time:
#
# | **Valid:** 2012-04-09 12Z
# | **Forecast lead:** 12 hour
# |

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads the default configuration file found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line:
# parm/use_cases/met_tool_wrapper/PlotPointObs/PlotPointObs.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/PlotPointObs/PlotPointObs.conf

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
# .. note:: See the :ref:`PlotPointObs MET Configuration<plot-point-obs-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/PlotPointObsConfig_wrapped


##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/PlotPointObs/PlotPointObs.conf /path/to/user_system.conf
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
# Output for this use case will be found in plot_point_obs
# (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * nam_and_ndas.20120409.t12z.prepbufr_CONFIG.ps

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * PlotPointObsToolUseCase
#   * GRIBFileUseCase
#   * NetCDFFileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-PlotPointObs.png'
