Python Wrappers
===============

This chapter provides a description of each supported Python wrapper in
METplus Wrappers. A wrapper is generally a Python script that
encapsulates the behavior of a corresponding MET tool. Each of these
sections can be added to the PROCESS_LIST configuration list variable.
The Configuration section of each wrapper section below lists the
METplus Wrappers configuration variables that are specific to that
wrapper organized by config file section. You can find more information
about each item in the METplus Configuration Glossary.

CyclonePlotter
--------------

Description
~~~~~~~~~~~

This wrapper does not have a corresponding MET tool but instead wraps
the logic necessary to create plots of cyclone tracks. Currently only
the output from the MET tc-pairs tool can be plotted.

Configuration
~~~~~~~~~~~~~

[dir]

| CYCLONE_PLOTTER_INPUT_DIR
| CYCLONE_PLOTTER_OUTPUT_DIR 

[config]

| CYCLONE_PLOTTER_INIT_DATE 
| CYCLONE_PLOTTER_INIT_HOUR 
| CYCLONE_PLOTTER_MODEL 
| CYCLONE_PLOTTER_PLOT_TITLE 
| CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE 
| CYCLONE_PLOTTER_CROSS_MARKER_SIZE 
| CYCLONE_PLOTTER_GENERATE_TRACK_ASCII

**Deprecated:**

CYCLONE_OUT_DIR

EnsembleStat
------------

.. _description-1:

Description
~~~~~~~~~~~

Used to configure the MET tool ensemble_stat.

.. _configuration-1:

Configuration
~~~~~~~~~~~~~

[dir]

| OBS_ENSEMBLE_STAT_POINT_INPUT_DIR 
| OBS_ENSEMBLE_STAT_GRID_INPUT_DIR 
| FCST_ENSEMBLE_STAT_INPUT_DIR 
| ENSEMBLE_STAT_OUTPUT_DIR

[filename_templates]

| OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE 
| OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE 
| FCST_ENSEMBLE_STAT_INPUT_TEMPLATE 

[config]

| ENSEMBLE_STAT_ONCE_PER_FIELD
| FCST_ENSEMBLE_STAT_INPUT_DATATYPE 
| OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE 
| OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE 
| ENSEMBLE_STAT_GRID_VX
| ENSEMBLE_STAT_CONFIG_FILE
| ENSEMBLE_STAT_MET_OBS_ERR_TABLE
| ENSEMBLE_STAT_N_MEMBERS
| OBS_ENSEMBLE_STAT_WINDOW_BEGIN 
| OBS_ENSEMBLE_STAT_WINDOW_END 
| ENSEMBLE_STAT_ENS_THRESH
| ENS_VAR<n>_NAME (optional)
| ENS_VAR<n>_LEVELS (optional)
| ENS_VAR<n>_THRESH (optional)
| ENS_VAR<n>_OPTIONS (optional)

**Deprecated:**

| ENSEMBLE_STAT_OUT_DIR
| ENSEMBLE_STAT_CONFIG
| ENSEMBLE_STAT_MET_OBS_ERROR_TABLE

ExtractTiles
------------

.. _description-2:

3.5.1 Description
~~~~~~~~~~~~~~~~~

The ExtractTiles wrapper is used to regrid and extract subregions from
paired tropical cyclone tracks that are created by the tc_pairs_wrapper.
Unlike the other wrappers, the extract_tiles_wrapper does not correspond
to a specific MET tool. It invokes the tc_stat_wrapper, which in turn
calls the MET tc_stat tool to determine the lat/lon positions of the
paired track data. This information is then used to create tiles of
subregions. The ExtractTiles wrapper creates a 2n degree x 2m degree
grid/tile with each storm located at the center.

.. _configuration-2:

Configuration 
~~~~~~~~~~~~~

The following should be set in the METplus configuration file to define
the dimensions and density of the tiles comprising the subregion:

[dir]

EXTRACT_TILES_OUTPUT_DIR

[config]

| LON_ADJ
| LAT_ADJ
| NLAT
| NLON
| DLON
| DLAT
| EXTRACT_TILES_FILTER_OPTS
| EXTRACT_TILES_VAR_LIST

**Deprecated:**

EXTRACT_OUT_DIR

GempakToCF
----------

.. _description-3:

Description
~~~~~~~~~~~

Used to configure the utility GempakToCF.

.. _configuration-3:

Configuration
~~~~~~~~~~~~~

[exe]

GEMPAKTOCF_JAR

[dir]

| GEMPAKTOCF_INPUT_DIR
| GEMPAKTOCF_OUTPUT_DIR

[filename_templates]

| GEMPAKTOCF_INPUT_TEMPLATE
| GEMPAKTOCF_OUTPUT_TEMPLATE

[config]

| GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS

**Deprecated:**

| GEMPAKTOCF_CLASSPATH

GridStat
--------

.. _description-4:

Description
~~~~~~~~~~~

Used to configure the MET tool grid_stat.

.. _configuration-4:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_GRID_STAT_INPUT_DIR 
| OBS_GRID_STAT_INPUT_DIR 
| GRID_STAT_OUTPUT_DIR

[filename_templates]

| FCST_GRID_STAT_INPUT_TEMPLATE 
| OBS_GRID_STAT_INPUT_TEMPLATE 
| GRID_STAT_VERIFICATION_MASK_TEMPLATE (optional)
 

[config]

| GRID_STAT_CONFIG_FILE
| FCST_GRID_STAT_INPUT_DATATYPE 
| OBS_GRID_STAT_INPUT_DATATYPE 
| GRID_STAT_ONCE_PER_FIELD
| FCST_GRID_STAT_PROB_THRESH (optional) 
| OBS_GRID_STAT_PROB_THRESH (optional) 
| GRID_STAT_NEIGHBORHOOD_WIDTH (optional)
| GRID_STAT_NEIGHBORHOOD_SHAPE (optional)
| FCST_GRID_STAT_WINDOW_BEGIN (optional) 
| FCST_GRID_STAT_WINDOW_END (optional) 
| OBS_GRID_STAT_WINDOW_BEGIN (optional) 
| OBS_GRID_STAT_WINDOW_END (optional) 

**Deprecated:**

| GRID_STAT_OUT_DIR
| GRID_STAT_CONFIG

MakePlots
---------

.. _description-5:

Description
~~~~~~~~~~~

The MakePlots wrapper creates various statistical plots using python
scripts for the various METplus Wrappers use cases. This can only be run
following StatAnalysis wrapper when LOOP_ORDER = processes. To run
MakePlots wrapper, include MakePlots in PROCESS_LIST.

.. _configuration-5:

Configuration
~~~~~~~~~~~~~

The following values **must** be defined in the METplus Wrappers
configuration file:

[dir]

| PLOTTING_SCRIPTS_DIR 
| STAT_FILES_INPUT_DIR 
| PLOTTING_OUTPUT_DIR 

[config]

| VERIF_CASE
| VERIF_TYPE
| PLOT_TIME 
| VALID_BEG
| VALID_END
| INIT_BEG 
| INIT_END 
| VALID_HOUR_METHOD
| VALID_HOUR_BEG
| VALID_HOUR_END
| VALID_HOUR_INCREMENT
| INIT_HOUR_METHOD 
| INIT_HOUR_BEG 
| INIT_HOUR_END 
| INIT_HOUR_INCREMENT 
| MODEL<n>_NAME 
| MODEL<n>_OBS_NAME 
| MODEL<n>_NAME_ON_PLOT 
| FCST_VAR<n>_NAME 
| FCST_VAR<n>_LEVELS 
| REGION_LIST 
| LEAD_LIST 
| INTERP 
| PLOT_STATS_LIST 
| CI_METHOD 
| VERIF_GRID
| EVENT_EQUALIZATION

The following values are **optional** in the METplus Wrappers
configuration file:

| FCST_VAR<n>_THRESH 
| FCST_VAR<n>_OPTIONS 
| VAR<n>_FOURIER_DECOMP
| VAR<n>_WAVE_NUM_LIST

Mode
----

.. _description-6:

Description
~~~~~~~~~~~

Used to configure the MET tool mode.

.. _configuration-6:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_MODE_INPUT_DIR 
| OBS_MODE_INPUT_DIR 
| MODE_OUTPUT_DIR 

[filename_templates]

| FCST_MODE_INPUT_TEMPLATE 
| OBS_MODE_INPUT_TEMPLATE 

[config]

| MODE_CONFIG_FILE 
| FCST_MODE_INPUT_DATATYPE 
| OBS_MODE_INPUT_DATATYPE 
| MODE_QUILT 
| MODE_CONV_RADIUS 
| FCST_MODE_CONV_RADIUS 
| OBS_MODE_CONV_RADIUS 
| MODE_CONV_THRESH 
| FCST_MODE_CONV_THRESH 
| OBS_MODE_CONV_THRESH 
| MODE_MERGE_THRESH 
| FCST_MODE_MERGE_THRESH 
| OBS_MODE_MERGE_THRESH 
| MODE_MERGE_FLAG 
| FCST_MODE_MERGE_FLAG 
| OBS_MODE_MERGE_FLAG 
| MODE_MERGE_CONFIG_FILE 
| FCST_MODE_WINDOW_BEGIN 
| FCST_MODE_WINDOW_END 
| OBS_MODE_WINDOW_BEGIN 
| OBS_MODE_WINDOW_END 

**Deprecated:**

| MODE_OUT_DIR
| MODE_CONFIG 

MTD
---

.. _description-7:

Description
~~~~~~~~~~~

Used to configure the MET tool mtd (mode time domain).

.. _configuration-7:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_MTD_INPUT_DIR 
| OBS_MTD_INPUT_DIR 
| MTD_OUTPUT_DIR 

[filename_templates]

| FCST_MTD_INPUT_TEMPLATE 
| OBS_MTD_INPUT_TEMPLATE 

[config]

| MTD_CONFIG_FILE 
| MTD_MIN_VOLUME 
| MTD_SINGLE_RUN 
| MTD_SINGLE_DATA_SRC 
| FCST_MTD_INPUT_DATATYPE 
| OBS_MTD_INPUT_DATATYPE 
| FCST_MTD_CONV_RADIUS 
| FCST_MTD_CONV_THRESH
| OBS_MTD_CONV_RADIUS
| OBS_MTD_CONV_THRESH 

**Deprecated:**

| MTD_OUT_DIR
| MTD_CONFIG 

PB2NC
-----

.. _description-8:

Description
~~~~~~~~~~~

The PB2NC wrapper is a Python script that encapsulates the behavior of
the MET pb2nc tool to convert prepBUFR files into netCDF.

.. _configuration-8:

Configuration
~~~~~~~~~~~~~

[dir]

| PB2NC_INPUT_DIR 
| PB2NC_OUTPUT_DIR 

[filename_templates]

| PB2NC_INPUT_TEMPLATE 
| PB2NC_OUTPUT_TEMPLATE 

[config]

| PB2NC_SKIP_IF_OUTPUT_EXISTS 
| PB2NC_OFFSETS 
| PB2NC_INPUT_DATATYPE 
| PB2NC_CONFIG_FILE 
| PB2NC_MESSAGE_TYPE (optional) 
| PB2NC_STATION_ID (optional) 
| PB2NC_GRID (optional) 
| PB2NC_POLY 
| PB2NC_OBS_BUFR_VAR_LIST (optional) 
| PB2NC_TIME_SUMMARY_FLAG 
| PB2NC_TIME_SUMMARY_BEG 
| PB2NC_TIME_SUMMARY_END 
| PB2NC_TIME_SUMMARY_VAR_NAMES 
| PB2NC_TIME_SUMMARY_TYPES 
| PB2NC_WINDOW_BEGIN 
| PB2NC_WINDOW_END 

**Deprecated:**

| PREPBUFR_DATA_DIR
| PREPBUFR_MODEL_DIR_NAME
| PREPBUFR_DIR_REGEX
| PREPBUFR_FILE_REGEX
| NC_FILE_TMPL
| PB2NC_VERTICAL_LEVEL
| OBS_BUFR_VAR_LIST
| TIME_SUMMARY_FLAG
| TIME_SUMMARY_BEG
| TIME_SUMMARY_END
| TIME_SUMMARY_VAR_NAMES
| TIME_SUMMARY_TYPE
| OVERWRITE_NC_OUTPUT 
| VERTICAL_LOCATION

PcpCombine
----------

.. _description-9:

Description
~~~~~~~~~~~

The PcpCombine wrapper is a Python script that encapsulates the MET
pcp_combine tool. It provides the infrastructure to combine or extract
from files to build desired accumulations.

.. _configuration-9:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_PCP_COMBINE_INPUT_DIR 
| FCST_PCP_COMBINE_OUTPUT_DIR 
| OBS_PCP_COMBINE_INPUT_DIR 
| OBS_PCP_COMBINE_OUTPUT_DIR 

[filename_templates]

| FCST_PCP_COMBINE_INPUT_TEMPLATE 
| FCST_PCP_COMBINE_OUTPUT_TEMPLATE 
| OBS_PCP_COMBINE_INPUT_TEMPLATE 
| OBS_PCP_COMBINE_OUTPUT_TEMPLATE 

[config]

| FCST_IS_PROB 
| OBS_IS_PROB 
| FCST_PCP_COMBINE_<n>_FIELD_NAME 
| OBS_PCP_COMBINE_<n>_FIELD_NAME 
| FCST_PCP_COMBINE_DATA_INTERVAL 
| OBS_PCP_COMBINE_DATA_INTERVAL 
| FCST_PCP_COMBINE_TIMES_PER_FILE 
| OBS_PCP_COMBINE_TIMES_PER_FILE 
| FCST_PCP_COMBINE_IS_DAILY_FILE 
| OBS_PCP_COMBINE_IS_DAILY_FILE 
| FCST_PCP_COMBINE_INPUT_DATATYPE 
| OBS_PCP_COMBINE_INPUT_DATATYPE 
| FCST_PCP_COMBINE_INPUT_LEVEL 
| OBS_PCP_COMBINE_INPUT_LEVEL 
| FCST_PCP_COMBINE_RUN 
| OBS_PCP_COMBINE_RUN 
| FCST_PCP_COMBINE_METHOD 
| OBS_PCP_COMBINE_METHOD 
| FCST_PCP_COMBINE_MIN_FORECAST 
| OBS_PCP_COMBINE_MIN_FORECAST 
| FCST_PCP_COMBINE_MAX_FORECAST 
| OBS_PCP_COMBINE_MAX_FORECAST 
| FCST_PCP_COMBINE_STAT_LIST 
| OBS_PCP_COMBINE_STAT_LIST 
| FCST_PCP_COMBINE_DERIVE_LOOKBACK 
| OBS_PCP_COMBINE_DERIVE_LOOKBACK 
| PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS 

**Deprecated:**

| PCP_COMBINE_METHOD
| FCST_MIN_FORECAST 
| FCST_MAX_FORECAST 
| OBS_MIN_FORECAST 
| OBS_MAX_FORECAST 
| FCST_DATA_INTERVAL 
| OBS_DATA_INTERVAL 
| FCST_IS_DAILY_FILE 
| OBS_IS_DAILY_FILE 
| FCST_TIMES_PER_FILE 
| OBS_TIMES_PER_FILE 
| FCST_LEVEL
| OBS_LEVEL 

PointStat
---------

.. _description-10:

Description
~~~~~~~~~~~

The PointStat wrapper is a Python script that encapsulates the MET
point_stat tool. It provides the infrastructure to read in gridded model
data and netCDF point observation data to perform grid-to-point
(grid-to-obs) verification.

.. _configuration-10:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_POINT_STAT_INPUT_DIR 
| OBS_POINT_STAT_INPUT_DIR 
| POINT_STAT_OUTPUT_DIR 

[filename_templates]

| FCST_POINT_STAT_INPUT_TEMPLATE 
| OBS_POINT_STAT_INPUT_TEMPLATE 
| POINT_STAT_VERIFICATION_MASK_TEMPLATE (optional)
  

[config]

| POINT_STAT_OFFSETS 
| FCST_POINT_STAT_INPUT_DATATYPE 
| OBS_POINT_STAT_INPUT_DATATYPE 
| POINT_STAT_CONFIG_FILE 
| MODEL 
| POINT_STAT_REGRID_TO_GRID 
| POINT_STAT_GRID 
| POINT_STAT_POLY 
| POINT_STAT_STATION_ID 
| POINT_STAT_MESSAGE_TYPE 
| FCST_POINT_STAT_WINDOW_BEGIN (optional) 
| FCST_POINT_STAT_WINDOW_END (optional) 
| OBS_POINT_STAT_WINDOW_BEGIN (optional) 
| OBS_POINT_STAT_WINDOW_END (optional) 
| POINT_STAT_NEIGHBORHOOD_WIDTH (optional) 
| POINT_STAT_NEIGHBORHOOD_SHAPE (optional) 

**Deprecated:**

| FCST_INPUT_DIR
| OBS_INPUT_DIR
| START_HOUR
| END_HOUR
| BEG_TIME
| FCST_HR_START
| FCST_HR_END
| FCST_HR_INTERVAL
| OBS_INPUT_DIR_REGEX
| FCST_INPUT_DIR_REGEX
| FCST_INPUT_FILE_REGEX
| OBS_INPUT_FILE_REGEX
| OBS_INPUT_FILE_TMPL 
| FCST_INPUT_FILE_TMPL
| REGRID_TO_GRID

RegridDataPlane
---------------

.. _description-11:

Description
~~~~~~~~~~~

Used to configure the MET tool regrid_data_plane.

.. _configuration-11:

Configuration
~~~~~~~~~~~~~

[dir]

| FCST_REGRID_DATA_PLANE_INPUT_DIR 
| OBS_REGRID_DATA_PLANE_INPUT_DIR 

[filename_templates]

| FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE 
| OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE 

[config]

| FCST_REGRID_DATA_PLANE_RUN
| OBS_REGRID_DATA_PLANE_RUN
| REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS
| REGRID_DATA_PLANE_VERIF_GRID
| FCST_REGRID_DATA_PLANE_INPUT_DATATYPE
| OBS_REGRID_DATA_PLANE_INPUT_DATATYPE
| REGRID_DATA_PLANE_GAUSSIAN_DX
| REGRID_DATA_PLANE_GAUSSIAN_RADIUS
| REGRID_DATA_PLANE_WIDTH
| REGRID_DATA_PLANE_METHOD

**Deprecated:**

VERIFICATION_GRID

SeriesByInit
------------

.. _description-12:

Description
~~~~~~~~~~~

The SeriesByInit wrapper provides the infrastructure needed to perform a
series analysis on tropical cyclone data, based on initialization times.
The SeriesByInit_wrapper creates numerous plots that represent the
field, level, and statistic for each initialization time.

.. _configuration-12:

Configuration
~~~~~~~~~~~~~

[dir]

| SERIES_BY_INIT_FILTERED_OUTPUT_DIR 
| SERIES_BY_INIT_OUTPUT_DIR 

[regex_patterns]

| FCST_TILE_PREFIX 
| ANLY_TILE_PREFIX
| FCST_TILE_REGEX 
| ANLY_TILE_REGEX
| FCST_NC_TILE_REGEX 
| ANLY_NC_TILE_REGEX
| FCST_ASCII_REGEX_LEAD 
| ANLY_ASCII_REGEX_LEAD

[config]

| INIT_BEG 
| INIT_END 
| INIT_INCREMENT 
| INIT_HOUR_END 
| INIT_INCLUDE 
| INIT_EXCLUDE 
| SERIES_ANALYSIS_FILTER_OPTS 

**Deprecated:**

SERIES_INIT_FILTERED_OUT_DIR

SeriesByLead
------------

.. _description-13:

Description
~~~~~~~~~~~

The SeriesByLead wrapper provides the infrastructure needed to perform a
series analysis on tropical cyclone data, based on lead (forecast hour)
times. The SeriesByLead wrapper creates numerous plots that represent
the field, level, and statistic for each lead (forecast) time. The
SeriesByLead can be done in one of two ways: by all forecast hours or by
forecast hour groupings. Performing a series analysis by valid time with
forecast hour groupings can be useful when analyzing storm tracks based
on time 'bins' such as by days (eg. day 1, day 2, day 3, etc.).

.. _configuration-13:

Configuration
~~~~~~~~~~~~~

The input track and model data files are defined in any one of the
user's METplus Wrappers configuration files. If creating a final
configuration file that overrides all other config files, it is
customary to define the MODEL_DATA_DIR, pointing to the directory where
all model data resides. The full file path to the INIT_INCLUDE and
INIT_EXCLUDE are used to list the times in YYYYMMDD_HH format to include
or exclude from your time window. If these values are undefined (i.e. no
value is set for the variable), then all available times in your time
window will be considered. For example, if your data is available every
6 hours and you are interested in creating a series analysis from init
time 20180601 to 20180615 for all available times, from 00z to 23z, you
would set the following:

[dir]

| SERIES_BY_LEAD_FILTERED_OUTPUT 
| SERIES_BY_LEAD_OUTPUT_DIR 

[config]

| INIT_BEG 
| INIT_TIME_FMT 
| INIT_END 
| INIT_INCREMENT 
| SERIES_BY_LEAD_GROUP_FCSTS 
| LEAD_SEQ_<n> 
| LEAD_SEQ_<n>_LABEL 
| SERIES_ANALYSIS_FILTER_OPT 
| VAR_LIST
| STAT_LIST 

**Deprecated:**

SERIES_LEAD_FILTERED_OUT_DIR

StatAnalysis
------------

.. _description-14:

Description
~~~~~~~~~~~

The StatAnalysis wrapper encapsulates the behavior of the MET
stat_analysis tool. It provides the infrastructure to summarize and
filter the MET .stat files. StatAnalysis wrapper can be run in two
different methods. First is to look at the STAT lines for a single date,
to use this method set LOOP_ORDER = times. Second is to look at the STAT
lines over a span of dates, to use this method set LOOP_ORDER =
processes. To run StatAnalysis wrapper, include StatAnalysis in
PROCESS_LIST.

.. _configuration-14:

Configuration
~~~~~~~~~~~~~

The following values must be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

[dir]

| STAT_ANALYSIS_LOOKIN_DIR
| STAT_ANALYSIS_OUTPUT_DIR 

[config]

| LOOP_BY 
| [VALID/INIT]\_TIME_FMT
| [VALID/INIT]\_BEG
  
| [VALID/INIT]\_END
  
| VALID_HOUR_METHOD
| VALID_HOUR_BEG
| VALID_HOUR_END
| VALID_HOUR_INCREMENT
| INIT_HOUR_METHOD 
| INIT_HOUR_BEG 
| INIT_HOUR_END 
| INIT_HOUR_INCREMENT 
| STAT_ANALYSIS_CONFIG 
| MODEL 
| OBTYPE 
| JOB_NAME
| JOB_ARGS

The following values are **optional** in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

| DESC
| FCST_LEAD 
| FCST_VAR<n>_NAME 
| FCST_VAR<n>_LEVEL 
| OBS_VAR<n>_NAME 
| OBS_VAR<n>_LEVEL
| REGION 
| INTERP 
| INTERP_PTS 
| FCST_THRESH 
| COV_THRESH 
| LINE_TYPE 
| STAT_ANALYSIS_DUMP_ROW_TMPL 
| STAT_ANALYSIS_OUT_STAT_TMPL 

The following values **must** be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = processes:

| STAT_ANALYSIS_OUTPUT_DIR 
| VERIF_CASE
| VERIF_TYPE
| PLOT_TIME 
| [VALID/INIT]\_BEG
  
| [VALID/INIT]\_END
  
| VALID_HOUR_METHOD
| VALID_HOUR_BEG
| VALID_HOUR_END
| VALID_HOUR_INCREMENT
| INIT_HOUR_METHOD 
| INIT_HOUR_BEG 
| INIT_HOUR_END 
| INIT_HOUR_INCREMENT 
| STAT_ANALYSIS_CONFIG 
| MODEL<n>_NAME 
| MODEL<n>_OBS_NAME 
| MODEL<n>_NAME_ON_PLOT 
| FCST_VAR<n>_NAME 
| FCST_VAR<n>_LEVELS 
| REGION_LIST 
| LEAD_LIST 
| INTERP 
| LINE_TYPE 

The following values are optional in the METplus Wrappers configuration
file for running with LOOP_ORDER = processes:

| FCST_VAR<n>_THRESH 
| FCST_VAR<n>_THRESH 
| FCST_VAR<n>_OPTIONS 
| VAR<n>_FOURIER_DECOMP
| VAR<n>_WAVE_NUM_LIST
| **Deprecated:**

STAT_ANALYSIS_OUT_DIR

TcPairs
-------

.. _description-15:

Description
~~~~~~~~~~~

The TcPairs wrapper encapsulates the behavior of the MET tc_pairs tool.
The wrapper accepts Adeck and Bdeck (Best track) cyclone track data in
extra tropical cyclone format (such as the data used by sample data
provided in the METplus tutorial), or ATCF formatted track data. If data
is in an extra tropical cyclone (non-ATCF) format, the data is
reformatted into an ATCF format that is recognized by MET.

.. _configuration-15:

Configuration
~~~~~~~~~~~~~

[dir]

| TC_PAIRS_ADECK_INPUT_DIR
| TC_PAIRS_BDECK_INPUT_DIR
| TC_PAIRS_EDECK_INPUT_DIR
| TC_PAIRS_OUTPUT_DIR
| TC_PAIRS_REFORMAT_DIR
| [filename_templates]

| TC_PAIRS_ADECK_INPUT_TEMPLATE
| TC_PAIRS_BDECK_INPUT_TEMPLATE
| TC_PAIRS_EDECK_INPUT_TEMPLATE
| TC_PAIRS_OUTPUT_TEMPLATE
| [config]

| TC_PAIRS_CONFIG_FILE
| INIT_BEG 
| INIT_END 
| INIT_INCREMENT 
| INIT_HOUR_END 
| INIT_INCLUDE 
| INIT_EXCLUDE 
| TC_PAIRS_READ_ALL_FILES
| TC_PAIRS_MODEL
| TC_PAIRS_STORM_ID
| TC_PAIRS_BASIN
| TC_PAIRS_CYCLONE
| TC_PAIRS_STORM_NAME
| TC_PAIRS_DLAND_FILE
| TC_PAIRS_MISSING_VAL_TO_REPLACE
| TC_PAIRS_MISSING_VAL
| TC_PAIRS_SKIP_IF_REFACTOR_EXISTS
| TC_PAIRS_SKIP_IF_OUTPUT_EXISTS
| TC_PAIRS_REFORMAT_DECK
| TC_PAIRS_REFORMAT_TYPE
| **Deprecated:**
| ADECK_TRACK_DATA_DIR
| BDECK_TRACK_DATA_DIR
| TRACK_DATA_SUBDIR_MOD
| TC_PAIRS_DIR
| TOP_LEVEL_DIRS
| MODEL
| STORM_ID
| BASIN
| CYCLONE
| STORM_NAME
| DLAND_FILE
| TRACK_TYPE
| ADECK_FILE_PREFIX
| BDECK_FILE_PREFIX
| MISSING_VAL_TO_REPLACE
| MISSING_VAL

TcStat
------

.. _description-16:

Description
~~~~~~~~~~~

Used to configure the MET tool tc_stat. This wrapper can be run by
listing it in the PROCESS_LIST, or can be called from the ExtractTiles
wrapper (via the MET tc-stat command line commands).

.. _configuration-16:

Configuration
~~~~~~~~~~~~~

[dir]

| TC_STAT_INPUT_DIR
| TC_STAT_OUTPUT_DIR

[config]

| TC_STAT_RUN_VIA
| TC_STAT_CONFIG_FILE
| TC_STAT_CMD_LINE_JOB
| TC_STAT_JOBS_LIST
| TC_STAT_AMODEL
| TC_STAT_BMODEL
| TC_STAT_DESC
| TC_STAT_STORM_ID
| TC_STAT_BASIN
| TC_STAT_CYCLONE
| TC_STAT_STORM_NAME
| TC_STAT_INIT_BEG
| TC_STAT_INIT_INCLUDE
| TC_STAT_INIT_EXCLUDE
| TC_STAT_INIT_HOUR
| TC_STAT_VALID_BEG
| TC_STAT_VALID_END
| TC_STAT_VALID_INCLUDE
| TC_STAT_VALID_EXCLUDE
| TC_STAT_VALID_HOUR
| TC_STAT_LEAD_REQ
| TC_STAT_INIT_MASK
| TC_STAT_VALID_MASK
| TC_STAT_VALID_HOUR
| TC_STAT_LEAD
| TC_STAT_TRACK_WATCH_WARN
| TC_STAT_COLUMN_THRESH_NAME
| TC_STAT_COLUNN_THRESH_VAL
| TC_STAT_COLUMN_STR_NAME
| TC_STAT_COLUMN_STR_VAL
| TC_STAT_INIT_THRESH_NAME
| TC_STAT_INIT_THRESH_VAL
| TC_STAT_INIT_STR_NAME
| TC_STAT_INIT_STR_VAL
| TC_STAT_WATER_ONLY
| TC_STAT_LANDFALL
| TC_STAT_LANDFALL_BEG
| TC_STAT_LANDFALL_END
| TC_STAT_MATCH_POINTS

TCMPRPlotter 
-------------

.. _description-17:

Description
~~~~~~~~~~~

The TCMPRPlotter wrapper is a Python script that wraps the R script
plot_tcmpr.R. This script is useful for plotting the calculated
statistics for the output from the MET-TC tools. This script, and other
R scripts are included in the MET installation. Please refer to section
21.2.3 of the MET User's Guide for usage information.

.. _configuration-17:

Configuration
~~~~~~~~~~~~~

| LOOP ORDER 
| TCMPR_PLOTTER_CONFIG_FILE 
| TCMPR_PLOTTER_PREFIX 
| TCMPR_PLOTTER_TITLE
| TCMPR_PLOTTER_SUBTITLE 
| TCMPR_PLOTTER_XLAB
| TCMPR_PLOTTER_YLAB
| TCMPR_PLOTTER_XLIM
| TCMPR_PLOTTER_YLIM
| TCMPR_PLOTTER_FILTER 
| TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE 
| TCMPR_PLOTTER_DEP_VARS
| TCMPR_PLOTTER_SCATTER_X
| TCMPR_PLOTTER_SCATTER_Y
| TCMPR_PLOTTER_SKILL_REF
| TCMPR_PLOTTER_SERIES
| TCMPR_PLOTTER_SERIES_CI
| TCMPR_PLOTTER_LEGEND 
| TCMPR_PLOTTER_LEAD 
| TCMPR_PLOTTER_PLOT_TYPES 
| TCMPR_PLOTTER_RP_DIFF 
| TCMPR_PLOTTER_DEMO_YR
| TCMPR_PLOTTER_HFIP_BASELINE
| TCMPR_PLOTTER_FOOTNOTE_FLAG 
| TCMPR_PLOTTER_PLOT_CONFIG_OPTS 
| TCMPR_PLOTTER_SAVE_DATA

The following are TCMPR flags, if set to 'no', then don't set flag, if
set to 'yes', then set the flag

| TCMPR_PLOTTER_NO_EE
| TCMPR_PLOTTER_NO_LOG
| TCMPR_PLOTTER_SAVE 
| TCMPR_PLOTTER_TCMPR_DATA_DIR
| TCMPR_PLOTTER_PLOT_OUTPUT_DIR

**Deprecated:**

TCMPR_PLOT_OUT_DIR
