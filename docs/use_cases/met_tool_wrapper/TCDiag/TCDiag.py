"""
TCDiag: Basic Use Case
======================

met_tool_wrapper/TCDiag/TCDiag.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# TODO: Add content here

##############################################################################
# Datasets
# --------
#
# **Forecast:** GFS FV3
# **Track:** A Deck
#
# **Location:** All of the input data required for this use case can be found
# in the met_test sample data tarball. Click here to the METplus releases page
# and download sample data for the appropriate release:
# https://github.com/dtcenter/METplus/releases
#
# This tarball should be unpacked into the directory that you will set the
# value of INPUT_BASE. See `Running METplus`_ section for more information.
#

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus TCDiag wrapper to search for
# the desired ADECK file and forecast files that are correspond to the track.
# It generates a command to run tc_diag if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# TCDiag is the only tool called in this example. It processes the following
# run times:
#
# **Init:** 2016-09-29- 00Z
# **Forecast lead:** 141, 143, and 147 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf

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
# .. note:: See the :ref:`TCDiag MET Configuration<tc-rmw-met-conf>` section of the User's Guide for more information on the environment variables used in the file below:
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/TCDiagConfig_wrapped

##############################################################################
# Running METplus
# ---------------
#
# Pass the use case configuration file to the run_metplus.py script
# along with any user-specific system configuration files if desired::
#
#    run_metplus.py /path/to/METplus/parm/use_cases/met_tool_wrapper/TCDiag/TCDiag.conf /path/to/user_system.conf
#
# See :ref:`running-metplus` for more information.
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
# Output for this use case will be found in met_tool_wrapper/TCDiag (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * tc_diag_aal142016.nc
#

##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * TCDiagToolUseCase
#   * GRIB2FileUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/met_tool_wrapper-TCDiag.png'
#
