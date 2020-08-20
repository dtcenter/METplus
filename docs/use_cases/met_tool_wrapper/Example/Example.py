"""
Example: Introductory Use Case
==================================

met_tool_wrapper/Example/Example.conf

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None.

##############################################################################
# Datasets
# --------
#
# None.

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus Example wrapper to demonstrate the effect of time looping and filename template METplus configuration variables.

##############################################################################
# METplus Workflow
# ----------------
#
# Example is the only tool called in this example. This configuration loops by valid time every 6 hours from 2017-02-01 at 0Z until 2017-02-02 at 0Z. For each valid time, the 3, 6, 9, and 12 hour forecast leads are processed. It processes the following run times:
#
# | **Valid:** 2017-02-01 0Z
# | **Forecast lead:** 3 hour
#
# | **Valid:** 2017-02-01 0Z
# | **Forecast lead:** 6 hour
#
# | **Valid:** 2017-02-01 0Z
# | **Forecast lead:** 9 hour
#
# | **Valid:** 2017-02-01 0Z
# | **Forecast lead:** 12 hour
#
# | **Valid:** 2017-02-01 6Z
# | **Forecast lead:** 3 hour
#
# | **Valid:** 2017-02-01 6Z
# | **Forecast lead:** 6 hour
#
# | **Valid:** 2017-02-01 6Z
# | **Forecast lead:** 9 hour
#
# | **Valid:** 2017-02-01 6Z
# | **Forecast lead:** 12 hour
#
# | **Valid:** 2017-02-01 12Z
# | **Forecast lead:** 3 hour
#
# | **Valid:** 2017-02-01 12Z
# | **Forecast lead:** 6 hour
#
# | **Valid:** 2017-02-01 12Z
# | **Forecast lead:** 9 hour
#
# | **Valid:** 2017-02-01 12Z
# | **Forecast lead:** 12 hour
#
# | **Valid:** 2017-02-01 18Z
# | **Forecast lead:** 3 hour
#
# | **Valid:** 2017-02-01 18Z
# | **Forecast lead:** 6 hour
#
# | **Valid:** 2017-02-01 18Z
# | **Forecast lead:** 9 hour
#
# | **Valid:** 2017-02-01 18Z
# | **Forecast lead:** 12 hour
#
# | **Valid:** 2017-02-02 0Z
# | **Forecast lead:** 3 hour
#
# | **Valid:** 2017-02-02 0Z
# | **Forecast lead:** 6 hour
#
# | **Valid:** 2017-02-02 0Z
# | **Forecast lead:** 9 hour
#
# | **Valid:** 2017-02-02 0Z
# | **Forecast lead:** 12 hour
#

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config, then it loads any configuration files passed to METplus via the command line with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/Example/Example.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/Example/Example.conf
#
# The following configuration variables tell METplus to loop by valid time starting at 2017-02-01 0Z, ending on 2017-02-02 0Z, incrementing 6 hours each iteration::
#
#   LOOP_BY = VALID
#   VALID_TIME_FMT = %Y%m%d%H
#   VALID_BEG = 2017020100
#   VALID_END = 2017020200
#   VALID_INCREMENT = 6H
#
# The following configuration variable tells METplus to process the 3 hour, 6 hour, 9 hour, and 12 hour forecast leads for EACH valid time::
#
#   LEAD_SEQ = 3H, 6H, 9H, 12H
#
# The following configuration variable tells METplus to look in /dir/containing/example/data to find data to process::
#
#   [dir]
#   EXAMPLE_INPUT_DIR = /dir/containing/example/data
#
# Note that this variable must be found following the [dir] section header
#
# The following configuration variable tells METplus to look for files in the input directory matching the format specified::
#
#   [filename_templates]
#   EXAMPLE_INPUT_TEMPLATE = {init?fmt=%Y%m%d}/file_{init?fmt=%Y%m%d}_{init?fmt=%2H}_F{lead?fmt=%3H}.ext
#
# For example, valid time 2017-02-01 18Z and forecast lead 3 hours, the desired file is /dir/containing/example/data/20170201/file_20170201_15_F03.ext
#
# Note that the initialization time used is 2017-02-01 15Z, which is calculated by subtracting the forecast lead from the valid time.
#

##############################################################################
# MET Configuration
# -----------------
#
# None.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in Example.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/Example/Example.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in Example.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/Example/Example.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# You should also see a series of log output listing init/valid times, forecast lead times, and filenames derived from the filename templates. Here is an excerpt::
#
#   12/30 19:44:02.901 metplus (met_util.py:425) INFO: ****************************************
#   12/30 19:44:02.901 metplus (met_util.py:426) INFO: * Running METplus
#   12/30 19:44:02.902 metplus (met_util.py:432) INFO: *  at valid time: 201702010000
#   12/30 19:44:02.902 metplus (met_util.py:435) INFO: ****************************************
#   12/30 19:44:02.902 metplus.Example (example_wrapper.py:58) INFO: Running ExampleWrapper at valid time 20170201000000
#   12/30 19:44:02.902 metplus.Example (example_wrapper.py:63) INFO: Input directory is /dir/containing/example/data
#   12/30 19:44:02.902 metplus.Example (example_wrapper.py:64) INFO: Input template is {init?fmt=%Y%m%d}/file_{init?fmt=%Y%m%d}_{init?fmt=%2H}_F{lead?fmt=%3H}.ext
#   12/30 19:44:02.902 metplus.Example (example_wrapper.py:79) INFO: Processing forecast lead 3 hours initialized at 2017-01-31 21Z and valid at 2017-02-01 00Z
#   12/30 19:44:02.903 metplus.Example (example_wrapper.py:88) INFO: Looking in input directory for file: 20170131/file_20170131_21_F003.ext
#   12/30 19:44:02.903 metplus.Example (example_wrapper.py:79) INFO: Processing forecast lead 6 hours initialized at 2017-01-31 18Z and valid at 2017-02-01 00Z
#   12/30 19:44:02.903 metplus.Example (example_wrapper.py:88) INFO: Looking in input directory for file: 20170131/file_20170131_18_F006.ext
#   12/30 19:44:02.904 metplus.Example (example_wrapper.py:79) INFO: Processing forecast lead 9 hours initialized at 2017-01-31 15Z and valid at 2017-02-01 00Z
#   12/30 19:44:02.904 metplus.Example (example_wrapper.py:88) INFO: Looking in input directory for file: 20170131/file_20170131_15_F009.ext
#   12/30 19:44:02.904 metplus.Example (example_wrapper.py:79) INFO: Processing forecast lead 12 hours initialized at 2017-01-31 12Z and valid at 2017-02-01 00Z
#   12/30 19:44:02.904 metplus.Example (example_wrapper.py:88) INFO: Looking in input directory for file: 20170131/file_20170131_12_F012.ext
#   12/30 19:44:02.904 metplus (met_util.py:425) INFO: ****************************************
#   12/30 19:44:02.904 metplus (met_util.py:426) INFO: * Running METplus
#   12/30 19:44:02.905 metplus (met_util.py:432) INFO: *  at valid time: 201702010600
#   12/30 19:44:02.905 metplus (met_util.py:435) INFO: ****************************************
#   12/30 19:44:02.905 metplus.Example (example_wrapper.py:58) INFO: Running ExampleWrapper at valid time 20170201060000
#   12/30 19:44:02.905 metplus.Example (example_wrapper.py:63) INFO: Input directory is /dir/containing/example/data
#   12/30 19:44:02.905 metplus.Example (example_wrapper.py:64) INFO: Input template is {init?fmt=%Y%m%d}/file_{init?fmt=%Y%m%d}_{init?fmt=%2H}_F{lead?fmt=%3H}.ext
#   12/30 19:44:02.905 metplus.Example (example_wrapper.py:79) INFO: Processing forecast lead 3 hours initialized at 2017-02-01 03Z and valid at 2017-02-01 06Z
#   12/30 19:44:02.906 metplus.Example (example_wrapper.py:88) INFO: Looking in input directory for file: 20170201/file_20170201_03_F003.ext
#

##############################################################################
# Keywords
# --------
#
# .. note:: `ExampleToolUseCase <https://dtcenter.github.io/METplus/search.html?q=ExampleToolUseCase&check_keywords=yes&area=default>`_
