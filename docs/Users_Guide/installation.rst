.. _install:

*************************************
Software Installation/Getting Started
*************************************

Introduction
============

This chapter describes how to download and set up METplus Wrappers.
METplus Wrappers has been developed and tested on the Debian Linux
operating system.

Supported architectures
=======================

METplus Wrappers was developed on Debian Linux and is supported on this
platform.

Programming/scripting languages
===============================

METplus Wrappers is written in Python 3.6.3. It is intended to be a tool
for the modeling community to use and adapt. As users make upgrades and
improvements to the tools, they are encouraged to offer those upgrades
to the broader community by offering feedback to the developers or
coordinating for a GitHub pull. For more information on contributing
code to METplus Wrappers, please contact
`met_help@ucar.edu <met_help@ucar.edu>`__.

Requirements
============

Software Requirements
---------------------

**Minimum Requirements**

The following software is required to run METplus Wrappers:

-  Python 3.6.3 or above

-  MET version 10.0.0 or above

**Wrapper Specific Requirements**

- TCMPRPlotter wrapper

    - R version 3.2.5

-  SeriesAnalysis wrapper

    - convert (ImageMagick) utility
      if generating plots and/or animated images from the output

-  PlotDataPlane wrapper

    - convert (ImageMagick) utility
      if generating images from the Postscript output

Python Package Requirements
---------------------------

The version number listed next to any Python package corresponds to the version
that was used for testing purposes. Other versions of the packages **may**
still work but it is not guaranteed.

**Minimum Requirements**

To run most of the METplus wrappers, the following packages are required:

- dateutil (2.8)

Using pip::

    pip3 install python-dateutil==2.8

Using Conda::

  conda install -c conda-forge python-dateutil=2.8


**MET Python Embedding Requirements**

If running use cases that use Python embedding, the **MET** executables
must be installed with Python enabled
and the following Python packages installed:

- xarray (0.17.0)

- numpy (1.19.2)

- pandas (1.0.5)

- netCDF4 (1.5.4)

See the Software Installation section in the MET User's Guide
for more information.

**Wrapper Specific Requirements**

Some of the wrappers have additional Python package dependencies
that are required to run.

-  SeriesAnalysis wrapper

    - netCDF4 (1.5.4)

-  MakePlots wrapper

    - cartopy (0.17.0)
    - pandas (1.0.5)

-  CyclonePlotter wrapper

    - cartopy (0.17.0)
    - matplotlib (3.3.4)

.. _getcode:

Getting the METplus Wrappers source code
========================================

The METplus Wrappers source code is available for download from the public
GitHub repository. The source code can retrieved through a web
browser or the command line.

Get the source code via Web Browser
-----------------------------------

-  On your local host, create a directory where the METplus Wrappers will be
   installed

-  Open a web browser and navigate to
   https://github.com/dtcenter/METplus/releases/latest to view the
   latest stable release.

.. image:: ../_static/metplus_repo_releases_page.png

-  Click on the 'Source code' link (either the *zip* or *tar.gz*) under Assets
   and when prompted, save it to the directory.

-  Uncompress the source code (on Linux/Unix\ *: gunzip* for zip file or
   *tar xvfz* for the tar.gz file)

Get the source code via Command Line
------------------------------------

- Open a shell terminal

- Clone the DTCenter/METplus GitHub repository:

SSH::

    git@github.com:dtcenter/metplus

HTTPS::

    https://github.com/dtcenter/metplus

Obtain Sample Input Data (optional)
-----------------------------------

-  Create a directory to put the sample input data. This will be the directory
   to set for the value of INPUT_BASE in the METplus Configuration.

- Navigate to the sample input data web URL: https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data

- Click on the vX.Y version directory that corresponds to the release to
  install, i.e. v4.0 directory for the v4.0.0 release.

-  Click on the sample data tgz file for the desired use case category or
   categories run and when prompted, save the file to the directory created
   above.

.. note::
    Files with the version number in the name,
    i.e. sample_data-data_assimilation-4.0.tgz, have been updated since the
    last major release. Files without the version number in the file name have
    not changed since the last major release and could be skipped if the data
    was already obtained with the previous release.


METplus Wrappers directory structure
====================================

The METplus Wrappers source code contains the following directory structure::

  METplus/
    build_components/
    ci/
    docs/
    environment.yml
    internal_tests/
    manage_exernals/
    metplus/
    parm/
    produtil/
    README.md
    requirements.txt
    setup.py
    ush/

The top-level METplus Wrappers directory consists of a README.md file
and several subdirectories.

The build_components/ directory contains scripts that use manage_externals
and files available on dtcenter.org to download MET and start the build process

The ci/ directory contains scripts that are used for creating Docker images and
script that are used internally for automation

The docs/ directory contains documentation for users and contributors (HTML) and Doxygen
files that are used to create the METplus wrapper API documentaton. The Doxygen
documentation can be created and viewed via web browser if the developer
has Doxygen installed on the host.  The Doxygen documentation is useful to contributors and is not
necessary for METplus end-users.

The internal_tests/ directory contains test scripts that are only
relevant to METplus developers and contributors.

The manage_externals/ directory contains scripts used to facilitate the downloading and management
of components that METplus interacts with such as MET and METviewer

The metplus/ directory contains the wrapper scripts and utilities

The parm/ directory contains all the configuration files for MET and
METplus Wrappers.

The produtil/ directory contains part of the external utility produtil

The ush/ directory contains the run_metplus.py script that is executed to run
use cases

Build_components and using manage_externals
===========================================

Running build_components/build_MET.sh will

-  clone MET and METviewer from github using the manage_externals scripts
-  grab the current MET compile script and all of the necessary external libraries
-  build the external libraries
-  attempt to build met

Building MET requires fine tuning on just about all systems, this should at least get most of
the way through the process and allow just a few manual changes to get it completely built.

External Components
===================

GFDL Tracker
------------

-  The standalone Geophysical Fluid Dynamics Laboratory (GFDL) vortex tracker is a program that objectively analyzes forecast data to provide an estimate of the vortex center position (latitude and longitude), and track the storm for the duration of the forecast.

-  Visit https://dtcenter.org/community-code/gfdl-vortex-tracker for more information

    -  See the manage externals section of this documentation to download the GFDL vortex tracker automatically as part of the system.

    -  To download and install in your own location get http://dtcenter.org/sites/default/files/community-code/gfdl/standalone_gfdl-vortextracker_v3.9a.tar.gz and follow the instructions listed in that archive to build on your system.

    -  Instructions on how to configure and use the GFDL tracker are found here https://dtcenter.org/sites/default/files/community-code/gfdl/standalone_tracker_UG_v3.9a.pdf

Add ush directory to shell path (optional)
==========================================

To call the run_metplus.py script from any directory, add the ush directory
to the path. The following commands can be run in a terminal. They can also
be added to the shell run commands file, i.e.
.cshrc for csh/tcsh  or .bashrc for bash.
For the following commands, change **/path/to** to
the actual path to the METplus directory on your file system.

**csh/tcsh**:

.. code-block:: tcsh

    # Add METplus to $PATH
    set path = (/path/to/METplus/ush $path)

**bash/ksh**:

.. code-block:: bash

    # Add METplus to $PATH
    export PATH=/path/to/METplus/ush:$PATH

Set Default Configuration File for Shared Install
=================================================

The default METplus configurations are found in
*parm/metplus_config/defaults.conf*.
If configuring METplus Wrappers in a common location for multiple users,
it is recommended that the values for **MET_INSTALL_DIR** and **INPUT_BASE**
are set in the default configuration file. More information on how to
set these values can be found in the
:ref:`Default Configuration File section<default_configuration_file>`.


Updating Configuration Files - Handling Deprecated Configuration Variables
==========================================================================

If upgrading from a METplus version earlier than v3.0, this content is
important to getting started using a newly released version. **If upgrading
from METplus v3.0 and above or if installing METplus for the first time, you
can skip this section.**

METplus developers strive to allow backwards compatibility so new versions of the tools will continue to work as they did in previous versions.
However, sometimes changes are necessary for clarity and cohesion. Many configuration variable names have changed in version 3.0 in an attempt to make their function more clear.
If any deprecated METplus configuration variables are found in a user's use case, execution will stop immediately and an error report of all variables that must be updated is output.
In some cases, simply renaming the variable is sufficient. Other changes may require more thought. The next few sections will outline a few of common changes that will need to be made. In the last section, a tool called validate_config.py is described. This tool can be used to help with this transition by automating some of the work required to update your configuration files.

Simple Rename
-------------

In most cases, there is a simple one-to-one relationship between a deprecated configuration variable and a valid one. In this case, renaming the variable will resolve the issue.

Example::

    (met_util.py) ERROR: DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE REMOVE/REPLACE THEM FROM CONFIG FILES
    (met_util.py) ERROR: [dir] MODEL_DATA_DIR should be replaced with EXTRACT_TILES_GRID_INPUT_DIR
    (met_util.py) ERROR: [config] STAT_LIST should be replaced with SERIES_ANALYSIS_STAT_LIST

These cases can be handled automatically by using the :ref:`validate_config`.

FCST/OBS/BOTH Variables
-----------------------

Field information passed into many of the MET tools is defined with the [FCST/OBS]_VAR<n>_[NAME/LEVELS/THRESH/OPTIONS] configuration variables.
For example, FCST_VAR1_NAME and FCST_VAR1_LEVELS are used to define forecast name/level values that are compared to observations defined with OBS_VAR1_NAME and OBS_VAR1_LEVELS.

Before METplus 3.0, users could define the FCST_* variables and omit the OBS_* variables or vice versa. In this case, it was assumed the undefined values matched the coresponding term. For example, if FCST_VAR1_NAME = TMP and OBS_VAR1_NAME is not defined, it was assumed that OBS_VAR1_NAME = TMP as well. This method was not always clear to users.

Starting in METplus 3.0, users are required to either explicitly set both FCST_* and OBS_* variables or set the equivalent BOTH_* variables to make it clear that the values apply to both forecast and observation data.

Example::

    (met_util.py) ERROR: If FCST_VAR1_NAME is set, you must either set OBS_VAR1_NAME or change FCST_VAR1_NAME to BOTH_VAR1_NAME
    (met_util.py) ERROR: If FCST_VAR2_NAME is set, you must either set OBS_VAR2_NAME or change FCST_VAR2_NAME to BOTH_VAR2_NAME
    (met_util.py) ERROR: If FCST_VAR1_LEVELS is set, you must either set OBS_VAR1_LEVELS or change FCST_VAR1_LEVELS to BOTH_VAR1_LEVELS
    (met_util.py) ERROR: If FCST_VAR2_LEVELS is set, you must either set OBS_VAR2_LEVELS or change FCST_VAR2_LEVELS to BOTH_VAR2_LEVELS

These cases can be handled automatically by using the :ref:`validate_config`, but users should review the suggested changes, as they may want to update differently.

PCPCombine Input Levels
-----------------------

Prior to METplus 3.0, the PCPCombine wrapper only allowed the user to define a single input accumulation amount to be used to build a desired accumulation. However, some data sets include more than one accumulation field.
PCPCombine wrapper was enhanced in version 3.0 to allow users to specify a list of accumulations available in the input data.
Instead of only being able to specify FCST_PCP_COMBINE_INPUT_LEVEL, users can now specify a list of accumulations with :term:`FCST_PCP_COMBINE_INPUT_ACCUMS`.

Example::

    (met_util.py) ERROR: [config] OBS_PCP_COMBINE_INPUT_LEVEL should be replaced with OBS_PCP_COMBINE_INPUT_ACCUMS

These cases can be handled automatically by using the :ref:`validate_config`, but users should review the suggested changes, as they may want to include other available input accumulations.

MET Configuration Files
-----------------------

The METplus wrappers set environment variables that are read by the MET configuration files to customize each run. Some of the environment variables that were previously set by METplus wrappers to handle very specific use cases are no longer set in favor of using a common set of variables across the MET tools. The following are examples of changes that have occurred in METplus regarding environment variables.

EnsembleStat previously set $GRID_VX to define the grid to use to regrid data within the tool. In version 3.0, MET tools that have a 'to_grid' value in the 'grid' dictionary of the MET config file have a uniformly named METplus configuration variable called <MET-tool>_REGRID_TO_GRID (i.e. :term:`ENSEMBLE_STAT_REGRID_TO_GRID`) that is used to define this value::

    Before:
       to_grid    = ${GRID_VX};

    After:
       to_grid    = ${REGRID_TO_GRID};

MET_VALID_HHMM was used by GridStat wrapper to set part of the climatology file path. This was replaced by the METplus configuration variables <MET-tool>_CLIMO_[MEAN/STDEV]_INPUT_[DIR/TEMPLATE] (i.e. :term:`GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE`)::

  Before:
     file_name = [ "${INPUT_BASE}/grid_to_grid/nwprod/fix/cmean_1d.1959${MET_VALID_HHMM}" ];

  After:
     file_name = [ ${CLIMO_MEAN_FILE} ];

The output_prefix variable in the MET config files was previously set by referencing variable environment variables set by METplus. This has since been changed so that output_prefix references the $OUTPUT_PREFIX environment variable. This value is now set in the METplus configuration files using the wrapper-specific configuration variable, such as :term:`GRID_STAT_OUTPUT_PREFIX` or :term:`ENSEMBLE_STAT_OUTPUT_PREFIX`::

  Before:
     output_prefix    = "${FCST_VAR}_vs_${OBS_VAR}";

  After:
     output_prefix    = "${OUTPUT_PREFIX}";

Due to these changes, MET configuration files that refer to any of these deprecated environment variables will throw an error. While the :ref:`validate_config` will automatically remove any invalid environment variables that may be set in the MET configuration files, the user will be responsible for adding the corresponding METplus configuration variable to reproduce the intended behavior. The tool will give a suggested value for <MET-tool>_OUTPUT_PREFIX.

Example log output::

    (met_util.py) DEBUG: Checking for deprecated environment variables in: DeprecatedConfig
    (met_util.py) ERROR: Please remove deprecated environment variable ${GRID_VX} found in MET config file: DeprecatedConfig
    (met_util.py) ERROR: MET to_grid variable should reference ${REGRID_TO_GRID} environment variable
    (met_util.py) INFO: Be sure to set GRID_STAT_REGRID_TO_GRID to the correct value.

    (met_util.py) ERROR: Please remove deprecated environment variable ${MET_VALID_HHMM} found in MET config file: DeprecatedConfig
    (met_util.py) ERROR: Set GRID_STAT_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in a METplus config file to set CLIMO_MEAN_FILE in a MET config

    (met_util.py) ERROR: output_prefix variable should reference ${OUTPUT_PREFIX} environment variable
    (met_util.py) INFO: You will need to add GRID_STAT_OUTPUT_PREFIX to the METplus config file that sets GRID_STAT_CONFIG_FILE. Set it to:
    (met_util.py) INFO: GRID_STAT_OUTPUT_PREFIX = {CURRENT_FCST_NAME}_vs_{CURRENT_OBS_NAME}

These cases can be handled automatically by using the :ref:`validate_config`, but users should review the suggested changes and make sure they add the appropriate recommended METplus configuration variables to their files to achieve the same behavior.

SED Commands
------------

Running run_metplus.py with one or more configuration files that contain deprecated variables that can be fixed with a find/replace command will generate a file in the {OUTPUT_BASE} called sed_commands.txt. This file contains a list of commands that can be run to update the configuration file. Lines that start with "#Add" are intended to notify the user to add a variable to their METplus configuration file.

The :ref:`validate_config` will step you through each of these commands and execute them upon your approval.

Example sed_commands.txt content::

    sed -i 's|^   to_grid    = ${GRID_VX};|   to_grid    = ${REGRID_TO_GRID};|g' DeprecatedConfig
    #Add GRID_STAT_REGRID_TO_GRID
    sed -i 's|^   file_name = [ "${INPUT_BASE}/grid_to_grid/nwprod/fix/cmean_1d.1959${MET_VALID_HHMM}" ];|   file_name = [ ${CLIMO_MEAN_FILE} ];|g' DeprecatedConfig
    #Add GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE
    sed -i 's|^output_prefix    = "${FCST_VAR}_vs_${OBS_VAR}";|output_prefix    = "${OUTPUT_PREFIX}";|g' DeprecatedConfig
    #Add GRID_STAT_OUTPUT_PREFIX = {CURRENT_FCST_NAME}_vs_{CURRENT_OBS_NAME}
    sed -i 's|^FCST_VAR1_NAME|BOTH_VAR1_NAME|g' deprecated.conf
    sed -i 's|^FCST_VAR1_LEVELS|BOTH_VAR1_LEVELS|g' deprecated.conf

.. _validate_config:

Validate Config Helper Script
-----------------------------

The script named validate_config.py is found in the same directory as run_metplus.py. To use this script, call it with the same arguments that you would pass to run_metplus.py::

  run_metplus.py  -c ./my_conf.py -c ./another_config.py
  validate_config.py -c ./my_conf.py -c ./another_config.py

You must pass a valid configuration to the script, as in you must properly set :term:`MET_INSTALL_DIR`, :term:`INPUT_BASE`, and :term:`OUTPUT_BASE`, or it will not run.

The script will evaluate all of the configuration files, including any MET configuration file that is referenced in a _CONFIG_FILE variable, such as :term:`GRID_STAT_CONFIG_FILE`.  For each deprecated item that is found, the script will suggest a replacement for the file where the deprecated item was found.

Example 1 (Simple Rename)::

    The following replacement is suggested for ./deprecated.conf

    Before:
    STAT_LIST = TOTAL, OBAR, FBAR

    After:
    SERIES_ANALYSIS_STAT_LIST = TOTAL, OBAR, FBAR

    Would you like the make this change to ./deprecated.conf? (y/n)[n]

Example 2 (FCST/OBS/BOTH Variables)::

    The following replacement is suggested for ./deprecated.conf

    Before:
    FCST_VAR1_NAME = TMP

    After:
    BOTH_VAR1_NAME = TMP

    Would you like the make this change to ./deprecated.conf? (y/n)[n]

Example 3 (PCPCombine Input Levels)::

    The following replacement is suggested for ./deprecated.conf

    Before:
    OBS_PCP_COMBINE_INPUT_LEVEL = 6

    After:
    OBS_PCP_COMBINE_INPUT_ACCUMS = 6

    Would you like the make this change to ./deprecated.conf? (y/n)[n]

Example 4 (MET Configuration File)::

    The following replacement is suggested for DeprecatedConfig

    Before:
       to_grid    = ${GRID_VX};

    After:
       to_grid    = ${REGRID_TO_GRID};

    Would you like the make this change to DeprecatedConfig? (y/n)[n]

    IMPORTANT: If it is not already set, add the following in the [config] section to your METplus configuration file that sets GRID_STAT_CONFIG_FILE:

    GRID_STAT_REGRID_TO_GRID
    Make this change before continuing! [OK]

Example 5 (Another MET Configuration File)::

  The following replacement is suggested for DeprecatedConfig

  Before:
  output_prefix    = "${FCST_VAR}_vs_${OBS_VAR}";

  After:
  output_prefix    = "${OUTPUT_PREFIX}";

  Would you like the make this change to DeprecatedConfig? (y/n)[n]

  IMPORTANT: If it is not already set, add the following in the [config] section to your METplus configuration file that sets GRID_STAT_CONFIG_FILE:

  GRID_STAT_OUTPUT_PREFIX = {CURRENT_FCST_NAME}_vs_{CURRENT_OBS_NAME}
  Make this change before continuing! [OK]

.. note::
    While the METplus developers are very diligent to include deprecated variables in this functionality, some may slip through the cracks. When upgrading to a new version of METplus, it is important to test and review your use cases to ensure they produce the same results as the previous version. Please contact met_help@ucar.edu with any questions.

Running METplus Wrappers
========================

Running METplus Wrappers involves invoking the Python script
run_metplus.py from any directory followed by a list of configuration
files (file path relative to the
*<path_to_METplus_install_dir>*/parm directory).

.. note::
   The executable named 'python3' that contains the packages required to run the
   METplus wrappers must be found first in the path.

**Example 1: Using a "default" configuration:**
Copy and paste the following into an empty text file and name it 'my_user_config.conf':

.. code-block:: ini

  # This is a comment, comments are defined with a # at the beginning of the line

  # Set the MET_INSTALL_DIR to the location of the MET install
  [dir]
  MET_INSTALL_DIR = /usr/local/met-9.0

  # Set INPUT_BASE to the directory containing sample input data if running use cases in the repository
  # Otherwise set INPUT_BASE to any path that does not contain /path/to.
  INPUT_BASE = /tmp/input

  # Set OUTPUT_BASE to a directory where you have permission to write output files
  # It will be created if it does not exist
  OUTPUT_BASE = /tmp/output

Run METplus via: ``run_metplus.py -c ./<my_user_config.conf>`` or ``run_metplus.py -c /<username>/<my_user_config.conf>`` if you saved your default config in a directory other than where you are running run_metplus.py.

When the above command is run, a usage message appears indicating that other config files are required to perform useful tasks, as well as a list of currently supported wrappers:

.. code-block:: ini

  USAGE: This text is displayed when [config] PROCESS_LIST = Usage.
  Pass in a configuration file (with -c or --config) that overrides [config] PROCESS_LIST to run other processes. For example:

  run_metplus.py -c parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf

  or

  run_metplus.py --config parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf

  Possible processes:
  - ASCII2NC
  - CyclonePlotter
  - EnsembleStat
  - Example
  - ExtractTiles
  - GempakToCF
  - GenVxMask
  - GridDiag
  - GridStat
  - MakePlots
  - MODE
  - MTD
  - PB2NC
  - PCPCombine
  - PlotDataPlane
  - Point2Grid
  - PointStat
  - PyEmbedIngest
  - RegridDataPlane
  - SeriesAnalysis
  - StatAnalysis
  - TCGen
  - TCMPRPlotter
  - TCPairs
  - TCRMW
  - TCStat
  - Usage
  - UserScript

**Example 2: Using a use-case configuration:**

The command:

.. code-block:: ini

  run_metplus.py -c use_cases/met_tool_wrapper/GridStat/GridStat.conf

will run METplus using the defaults set in parm/metplus_config/defaults.conf. Any variables defined in these three config files can be overridden in the parm/use_cases/GridStat/GridStat.conf file. METplus will run using the values specified in the GridStat.conf file.

**Example 3: Using example configuration to perform a specific evaluation (e.g. Model 1 vs. Obs 1, Model 1 vs. Obs 2, Model 2 vs. Obs 1, etc...):**

The command:

.. code-block:: ini

  run_metplus.py -c use_cases/met_tool_wrapper/GridStat/GridStat.conf \
  -c use_cases/met_tool_wrapper/GridStat/GridStat_forecast.conf \
  -c use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf

will run METplus using the defaults set in parm/metplus_config/defaults.conf, where variables can be overridden by parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf, then by parm/use_cases/met_tool_wrapper/GridStat/GridStat_forecast.conf, then by parm/use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf. The order in which conf files are called is important. Variables that are defined in intermediate conf files will be overridden by the same variables set in the conf file following it, or the last conf file. For example, if FCST_VAR1_NAME = TMP in GridStat.conf and FCST_VAR1_NAME = TEMP in GridStat_forecast.conf, the value used will be TEMP because GridStat_forecast.conf was read after GridStat.conf.

Separating configurations into multiple files can be useful if you want to compare different forecasts or observations in the same way. For example, to compare a different forecast to the observation in this example, copy GridStat_forecast.conf into a directory outside of the METplus repository (i.e. /home/user/METplus_user_config), rename it (i.e. GridStat_myforecast.conf), then change the values to match the new data set (input directory, input filename template, field name, etc.). Then you can run the new use case:

.. code-block:: ini

  run_metplus.py -c use_cases/met_tool_wrapper/GridStat/GridStat.conf \
  -c /home/user/METplus_user_config/GridStat_myforecast.conf \
  -c use_cases/met_tool_wrapper/GridStat/GridStat_observation.conf
