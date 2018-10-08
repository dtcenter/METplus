Model Evaluation Tools Plus  (METplus)           {#METplus_install_guide}
======================================================

Welcome to the documentation for METplus.  METplus is a set of Python wrapper scripts around the MET verification tools
and METViewer (a tool used for plotting MET output verification statistics).


Background and Future
---------------------

METplus development began in 2016 with initial development for the cyclone-relative verification for the Stony Brook University (SBU) project.
Development in 2017 replicated the Global Deterministic National Centers for Environmental Prediction (NCEP) Verification. 
Future work will focus on ensemble, meso, and storm scale verification at NCEP and providing public support.


Dependencies
------------

The MET verification tools package is required to be installed on your system prior to running the METplus wrapper scripts.

METplus was developed using Python version 2.7.9.  Python version 2.7 or greater is required.

- METplus requires the following to be installed on your system:
  - ncdump utility
    - http://www.unidata.ucar.edu/downloads/netcdf/index.jsp
  - ncap2 utility
    - http://nco.sourceforge.net/
  - convert utility (part of ImageMagick)
    - https://www.imagemagick.org/script/binary-releases.php
  - wgrib2 utility
    - http://www.cpc.noaa.gov/products/wesley/wgrib2/compile_questions.html
  - egrep utility
    - http://directory.fsf.org/wiki/Grep
  - rm, cut, tr utilities (standard on Linux)

as these additional executables are needed to perform series analyses.


Version Control
---------------

METplus uses GIT for version control in a public GitHub repository:
https://github.com/NCAR/METplus.


Getting the Code and Test Data
------------------------------

Get the METplus latest release from the NCAR/METplus GitHub repository, and
click on the 'releases' link to download the latest release, documentation,
and sample data.



Configuring the Environment
---------------------------

Configure the following environment variables in your login shell.
The example below assumes C shell.
Open up your .cshrc (or similar file) using the editor of your choice and add the following:

  To your PYTHONPATH, add:

        (full path to METplus/ush):${PYTHONPATH} (replacing the text and () with the full path)

  If you do not currently have a PYTHONPATH, add:

        setenv PYTHONPATH (full path to METplus/ush) (replacing the text and () with the full path)

  To your PATH (path), add:

        setenv PATH ${PATH}:(full path to METplus/ush) (replacing the text and () with the full path)

  Optional: Add the METplus job log file,  JLOGFILE

        setenv JLOGFILE (full path/filename) (replacing the text in () with the desired full
                                          path and filename of your job log file.

Save the changes and source your .cshrc (or similar file) by running, for example:

        source ~/.cshrc


Configuration Files
-------------------

There are two sets of configuration files - one for running METplus and one for running MET.
The MET configuration files are found in the parm/met_config directory.

There are three main configuration files for METplus:
    + METplus_data.conf
    + METplus_system.conf
    + METplus_runtime.conf

These are located in the parm/metplus_config subdirectory.

Users have the ability to override specific fields in metplus_data.conf, metplus_system.conf, and/or
metplus_runtime.conf via use case configuration files and/or their own config file.
The three main METplus configuration files do not need to be specified on the
command line when running METplus.  Any additional configuration file


Configuration Setup
-------------------

The user should look at metplus_data.conf, metplus_system.conf, and metplus_runtime.conf
to modify necessary and desired fields.
Please refer to @ref confguide


How to Run?
-----------

Once you have set up your environment variables and necessary configuration
files, run the following from the command line:

+ for running a particular use case:

          master_metplus.py -c parm/use_cases/<use_case_name>/<use_case_name>.conf

+ for running a specific example under a use case:

          master_metplus.py -c  parm/use_cases/<use_case_name>/<use_case_name>.conf
                            -c parm/use_cases/<use_case_name>/examples/<some_example_name>.conf

+ for running a particular use case with settings from your custom configuration
  file (to over-ride existing settings set in one of the main METplus configuration files):

          master_metplus.py -c parm/use_cases/<use_case_name>/<use_case_name>.conf
                            -c /full/path/to/my_custom.conf




================================================================================
Release Notes
================================================================================


2.0 Release Notes:
=================
2018 September 28:
METplus v2.0 is available under the 'release' link of the GitHub repository.  
The release contains the METplus user documentation and sample data for running
the use cases.  Global grid-to-point (aka grid-to-obs) and grid-to-grid support 
use cases have been added.  Additional code refactoring was done to
address issues from the Beta release:


What's New
----------
The following wrappers were added:
- pb2nc
- point_stat
- grid-stat


Improvements
------------
- clean up code inconsistencies in the METplus configuration files
- remove hard-coded paths
- remove deprecated code and configuration file entries


Beta Release Notes:
------------------
2017 October 20:
METplus Beta is available under the 'release' link of the GitHub repository. The
release contains the METplus training tutorial documentation and accompanying
sample data.  The feature relative, QPE, track and intensity, and cyclone plotter
use cases are now available for users to use by simply replacing /path/to with
the appropriate full file paths.

Alpha Release Notes:
-------------------
2017 May 9:
METplus is now using the NOAA/NCEP/EMC produtil package.
This changed how configuration files, logging, subprocess execution,
and some file operations are implemented.

2017 Jan:
- Initial release of the code.

