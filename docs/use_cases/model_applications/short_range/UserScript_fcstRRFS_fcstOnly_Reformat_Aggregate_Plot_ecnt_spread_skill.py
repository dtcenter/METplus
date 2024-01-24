"""
UserScript: Reformat MET ECNT linetype, Aggregate based on XYZ, and generate a spread skill plot
=================================================================================================

model_applications/
short_range/
UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot_ecnt_spread_skill.py

"""

#################################################################################
# Scientific Objective
# --------------------
#
# This use case illustrates how to use MET .stat output (using the ECNT linetype data)  to generate a
# spread skill plot using a subset of the METplus Analysis Tools (METdataio, METcalcpy,
# and METplotpy). The METdataio METreformat module extracts the ECNT linetype data and
# performas reformatting, the METcalcpy pre-processing module performs aggregation, and the
# METplotpy line plot is used to generate the spread skill plot.
#

#################################################################################
# Datasets
# --------
#
#  * Forecast dataset: RRFS
#  * Observation dataset: None
#

#############################################################################
# External Dependencies
# ---------------------



##############################################################################
# METplus Components
# ------------------
#
# This use case runs the UserScript wrapper tool to run a user provided script, 
# in this case, reformat_ecnt_linetype.py, XYZ.py and plot_spread_skill.py.
# It also requires the METdataio, METcalcpy and METplotpy source code to reformat the MET .stat output,
# perform aggregation, and generate the plot. Clone the METdataio repository
# (https://github.com/dtcenter/METdataio),
# METcalcpy repository (https://github.com/dtcenter/METcalcpy, and the METplotpy
# repository (https://github.com/dtcenter/METplotpy) under the same base directory as the
# METPLUS_BASE directory so that the METdataio, METcalcpy, and METplotpy directories are under the
# same base directory (i.e. if the METPLUS_BASE directory is /home/username/working/METplus,
# then clone the METdataio, METcalcpy and METplotpy source code into the /home/username/working directory)
#
# Define the METDATAIO_BASE, METCALCPY_BASE, and METPLOTPY_BASE environment variables in the user configurations
# file. Refer to this documentation  https://metplus.readthedocs.io/en/latest/Users_Guide/systemconfiguration.html#user-configuration-file
# for additional information about the user configuration file.
# The METDATAIO_BASE is the full path to where the METdataio code was cloned, the METCALCPY_BASE is the full path
# to the location of the METcalcpy code, and the METPLOTPY_BASE is the full path to the location of the
# METplotpy code. In addition, define the OUTPUT_BASE, INPUT_BASE, and MET_INSTALL_DIR settings in the user
# configuration file.
#


##############################################################################
# METplus Workflow
# ----------------
#
# This use case reads in the MET .stat output that contains the ECNT linetype (from
# the MET ensemble-stat tool).  The .stat output *MUST* reside under one directory.
# If .stat files are spread among multiple directories, these must be consolidated under a
# single directory.
# The use case loops over three processes: reformatting, aggregating, and plotting.
#


##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.conf
#

#############################################################################
# MET Configuration
# ---------------------
#
# There are no MET tools used in this use case. The use case uses MET .stat
# output as input for the reformatting step.
#

##############################################################################
# Python Embedding
# ----------------
#
# There is no python embedding in this use case
#

##############################################################################
# Python Scripts
# ----------------
#
# This use case uses the following Python script (from METdataio) to reformat the MET .stat ECNT linetype data
# into a format that can be used by the plotting scripts.
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot/reformat_ecnt.py
#

# This use case uses a Python script (from METcalcpy) to aggregate based on XYZ
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot/plot_spread_skill.py
#

# This use case uses a Python script (from METplotpy) to perform plotting
#
# .. highlight:: python
# .. literalinclude:: ../../../../parm/use_cases/model_applications/short_range/UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot/plot_spread_skill.py
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot.conf,
# then a user-specific system configuration file::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot.conf::
#
#        run_metplus.py -c /path/to/METplus/parm/use_cases/model_applications/short_range/UserScript_fcstRRFS_fcstOnly_Reformat_Aggregate_Plot.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
#  and for the [exe] section, you will need to define the location of NON-MET executables.
#  If the executable is in the user's path, METplus will find it from the name. 
#  If the executable is not in the path, specify the full path to the executable here (i.e. RM = /bin/rm)  
#  The following executables are required for performing series analysis use cases:
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y
#
#   [exe]
#   RM = /path/to/rm
#   CUT = /path/to/cut
#   TR = /path/to/tr
#   NCAP2 = /path/to/ncap2
#   CONVERT = /path/to/convert
#   NCDUMP = /path/to/ncdump
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile, one for the
# reformat, aggregate, and plot steps of the use case::
#
#   INFO: METplus has successfully finished running.
#
# Reformat Output
#----------------
#
# The reformatted ensemble-stat ECNT linetype data should exist in the location specified in the user
# configuration file (OUTPUT_BASE)



##############################################################################
# Keywords
# --------
#
# .. note::
#
#   * UserScriptUseCase
#   * ShortRangeAppUseCase
#   * METdataioUseCas
#   * METcalcpyUseCase
#   * METplotpyUseCase
#
#   Navigate to the :ref:`quick-search` page to discover other similar use cases.
#
#
#
# sphinx_gallery_thumbnail_path = '_static/short_range-UserScript_fcstRRFS_fcstOnly_spread_skill_ecnt.png'
