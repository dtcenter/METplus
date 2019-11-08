===========
Background
===========

- tests for tc_stat where the MET tc_stat config file is by-passed and the job summary is made on the command line
- MET tc-stat can be run from the commane line, wher you need to specify "job summary ..."


=============
Pre-condition
=============

tc-pairs must be run for SBU extra tropical cyclone data, which is located on the host 'eyewall'. Replace all instances of 
"/path/to" with the following:

 TRACK_DATA_DIR = /d1/SBU/GFS/track_data
   EXTRACT_TILES_GRID_INPUT_DIR = /d1/SBU/GFS/model_data

   ADECK_TRACK_DATA_DIR = /d1/METplus_TC/adeck
   BDECK_TRACK_DATA_DIR = /d1/METplus_TC/bdeck

Set the process list to run tc-pairs wrapper to generate the input files upon which tc_stat_wrapper can act upon:
PROCESS_LIST=TCPairs


For these /path/to's, set these to the appropriate location (i.e. the permanent location where automated tests are run)
OUTPUT_BASE = /path/to

# Uncomment and indicate path to the following if not using the values from higher
# level config files or if they have not yet been defined
TMP_DIR = /path/to
METPLUS_BASE = /path/to


=============================
Run the tc_stat_wrapper tests
=============================
-use the config file tc_stat_cli.conf file with master_metplus.py
-set PROCESS_LIST=TCStat
-replace all instances of "/path/to" to the appropriate path:
   OUTPUT_BASE
   PROJ_DIR
   METPLUS_BASE
   TMP_DIR
