Model Evaluation Tools Plus  (METplus)           {#METplus_install_guide}
======================================================

Welcome to the documentation for METplus.  METplus is a set of Python wrapper scripts around the MET verification tools
(and eventually METViewer, a tool used for plotting MET output verification statistics).


Background and Future
---------------------

METplus development began in 2016 with initial development for the cyclone-relative verification for the Stony Brook University (SBU) project.
Development in 2017 will focus on replicating the Global Deterministic National Centers for Environmental Prediction (NCEP) Verification and
future work will focus on ensemble, meso, and storm scale verification at NCEP and public support.


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


Version Control
---------------

METplus uses GIT for version control in a public GitHub repository: NCAR/METplus.


Getting the Code and Test Data
------------------------------

Get the METplus latest release:

  wget http://www.dtcenter.org/met/users/downloads/METplus/METplus_vX.2017XXXX.tar


Decide where you would like to put the code and copy the METplus Package to that location.  Unpack the gzipped tar file in that directory by running:

  tar -xf METplus_vX.2017XXXX.tar

Decide where you would like to put the test data and copy the METplus test data to that location.  Unpack the gzipped tar file in that directory by running:

  tar -zxf METplus_test_data.20170109.tar.gz


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

- METplus

The main configuration file for METplus is metplus.conf, which is located in the "parm" subdirectory.

Users have the ability to override specific fields in metplus.conf in their own config file. 
As a starting point, an example file with some typical fields to override is user.template.conf


- MET

The configuration files for the MET tools are also located in the "parm" subdirectory.  Currently, the applicable configuration files are
TCPairsETCConfig (for the extra tropical cyclone TCPairs run) and the SeriesAnalysisConfig_by_init and SeriesAnalysisConfig_by_lead.


Configuration Setup
-------------------

The user should look at metplus.conf to modify necessary and desired fields.  The information below will cover the various variables:

NON-MET EXECUTABLES

Some of these fields may need to be modified based on the location of the executables on your system, but some may be standard. Note that
the WGRIB2 executable is not currently in a standard location and will need to be modified.


COMMONLY USED BASE VARIABLES

MET_BUILD_BASE is the base location for the MET release that you will be using. Please set that to an appropriate location.  

OUTPUT_BASE is the base area for where the user would like to store their output data.

PARM_BASE is the parm subdirectory for the METplus configuration files.   


MET EXECUTABLES

These fields rely on MET_BUILD_BASE and its "bin" subdirectory.  


INPUT DATA DIRECTORIES

These fields indicate where your input data is located.

For example, the METplus_test_data.20170109.tar.gz, includes a "reduced_model_data" directory, which contains GFS data, and a "track_data"
directory, which contains extra tropical cyclone track data.  If you wanted to put this data at "/d1/data/SBU", you would set the following:

PROJ_DIR = /d1/data/SBU
MODEL_DATA_DIR = GFS_DIR = {PROJ_DIR}/reduced_model_data
TRACK_DATA_DIR = {PROJ_DIR}/track_data


OUTPUT DIRECTORIES

These fields include a log directory and a tmp directory along with other output directories. 
The TRACK_DATA_SUBDIR_MOD refers to the subdirectory where the track data will be written, 
reformatted to be in true ATCF format, which the MET tools need for processing.


FILENAME TEMPLATES

These fields contain templates for filenames and filename prefixes and regular expressions.


CONFIGURATION FILES

These fields indicate which configuration files to use for MET.


LISTS AND SETTINGS

PROCESS_LIST is the list of processes that the user wants the master script to run.  
For example, a full run from start to finish for running series analysis by lead, would be:

 PROCESS_LIST = run_tc_pairs.py, extract_tiles.py, series_by_lead.py

STAT_LIST is the list of statistics to be computed (e.g. STAT_LIST = TOTAL, FBAR, OBAR ).
NOTE: Currently, "TOTAL" is a REQUIRED cnt statistic used by the series analysis scripts, so it must be in the STAT_LIST.

INIT_DATE_BEG is the beginning date in the format YYYYMMDD (e.g. 20141201 ) for the initialization time.
INIT_DATE_END is the ending date in the format YYYYMMDD (e.g. 20150331 ) for the initialization time.
INIT_HOUR_INC is the hour increment in the format H < 10 or HH >= 10 (e.g. 6)
INIT_HOUR_END is the last increment hour you'd like to process in the format (e.g. For the sample data provided, GFS has 00, 06, 12, and 18, so this value would be "18")

VAR_LIST OR  EXTRACT_TILES_VAR_LIST is the list of variables of interest with their levels: 
Values SHOULD NOT be present in both the VAR_LIST and the EXTRACT_TILES_VAR_LIST.
e.g. VAR_LIST = HGT/P500, PRMSL/Z0, TMP/Z2
     EXTRACT_TILES_VAR_LIST =

The following are used for performing series analysis based on lead time:
FHR_BEG is the beginning forecast time.  
FHR_END is the ending forecast time.
FHR_INC is the forecast hour increment.

NLAT and NLON are the dimensions of the tile.

DLAT and DLON is the resolution of the data in degrees.

LON_ADJ and LAT_ADJ are the degrees to subtract from the center lat and lon to calculate the lower left lat (lat_ll) and lower left lon (lon_ll) for a grid that is 2n X 2m, 
where n = LAT_ADJ degrees and m = LON_ADJ degrees.  For example, where n=15 and m=15, this results in a 30 deg X 30 deg grid.


TC PAIRS filtering options

These variables contains the options used for the call to MET's tc_pairs code.


TC-STAT filtering options

These variables contains the filtering options for the call to MET's tc_stat code.


OVERWRITE OPTIONS

These variables exist so that you can choose whether or not to overwrite already processed data sets.


PLOTTING

These variables contains the possible plotting options


REGRIDDING

Tese variables contain the possible regridding options.  
REGRID_USING_MET_TOOL is currently set to FALSE, as METplus is currently using wgrib2,
as opposed to regrid_data_plane, for part of its processing.


TESTING

These options are currently used by the developers and shouldn't need to be modified.


LOGGING

These variables contain the logging options.  
A LOG_LEVEL of "DEBUG" will likely provide too much information for the general user, so the user
may wish to start off with "INFO" instead.



How to Run?
-----------

Once you have set up user.template.conf you can simply run:

  master_met_plus.py -c user.template.conf



================================================================================
Release Notes
================================================================================

Alpha Release Notes:
-------------------
2017 May 9:
METplus is now using the NOAA/NCEP/EMC produtil package.
This changed how configuration files, logging, subprocess execution,
and some file operations are implemented.

2017 Jan:
- Initial release of the code.
