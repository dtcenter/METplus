Python Wrappers
===============

This chapter provides a description of each supported Python wrapper in
METplus Wrappers. A wrapper is generally a Python script that
encapsulates the behavior of a corresponding MET tool. Each of these
sections can be added to the PROCESS_LIST configuration list variable.
The Configuration section of each wrapper section below lists the
METplus Wrappers configuration variables that are specific to that
wrapper organized by config file section. You can find more information
about each item in the A-Z Config Glossary
(`[sec:SC_AZ_Config_Glossary] <#sec:SC_AZ_Config_Glossary>`__).

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

| CYCLONE_PLOTTER_INPUT_DIR `[sec:C] <#sec:C>` __
| CYCLONE_PLOTTER_OUTPUT_DIR `[sec:SC_C] <#sec:SC_C>`__

[config]

| CYCLONE_PLOTTER_INIT_DATE `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_INIT_HOUR `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_MODEL `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_PLOT_TITLE `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_CROSS_MARKER_SIZE `[sec:SC_C] <#sec:SC_C>`__
| CYCLONE_PLOTTER_GENERATE_TRACK_ASCII `[sec:SC_G] <#sec:SC_G>`__

**Deprecated:**

CYCLONE_OUT_DIR\ `[sec:SC_C] <#sec:SC_C>`__

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

| OBS_ENSEMBLE_STAT_POINT_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| OBS_ENSEMBLE_STAT_GRID_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| FCST_ENSEMBLE_STAT_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| ENSEMBLE_STAT_OUTPUT_DIR `[sec:SC_E] <#sec:SC_E>`__

[filename_templates]

| OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__
| OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__
| FCST_ENSEMBLE_STAT_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__

[config]

| ENSEMBLE_STAT_ONCE_PER_FIELD `[sec:SC_E] <#sec:SC_E>`__
| FCST_ENSEMBLE_STAT_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| ENSEMBLE_STAT_GRID_VX `[sec:SC_E] <#sec:SC_E>`__
| ENSEMBLE_STAT_CONFIG_FILE `[sec:SC_E] <#sec:SC_E>`__
| ENSEMBLE_STAT_MET_OBS_ERR_TABLE `[sec:SC_E] <#sec:SC_E>`__
| ENSEMBLE_STAT_N_MEMBERS `[sec:SC_E] <#sec:SC_E>`__
| OBS_ENSEMBLE_STAT_WINDOW_BEGIN `[sec:SC_O] <#sec:SC_O>`__
| OBS_ENSEMBLE_STAT_WINDOW_END `[sec:SC_O] <#sec:SC_O>`__
| ENSEMBLE_STAT_ENS_THRESH `[sec:SC_E] <#sec:SC_E>`__
| ENS_VAR<n>_NAME (optional) `[sec:SC_E] <#sec:SC_E>`__
| ENS_VAR<n>_LEVELS (optional) `[sec:SC_E] <#sec:SC_E>`__
| ENS_VAR<n>_THRESH (optional) `[sec:SC_E] <#sec:SC_E>`__
| ENS_VAR<n>_OPTIONS (optional) `[sec:SC_E] <#sec:SC_E>`__

**Deprecated:**

| ENSEMBLE_STAT_OUT_DIR\ `[sec:SC_E] <#sec:SC_E>`__
| ENSEMBLE_STAT_CONFIG\ `[sec:SC_E] <#sec:SC_E>`__
| ENSEMBLE_STAT_MET_OBS_ERROR_TABLE `[sec:SC_E] <#sec:SC_E>`__

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

EXTRACT_TILES_OUTPUT_DIR `[sec:SC_E] <#sec:SC_E>`__

[config]

| LON_ADJ\ `[sec:SC_L] <#sec:SC_L>`__
| LAT_ADJ `[sec:SC_L] <#sec:SC_L>`__
| NLAT `[sec:SC_N] <#sec:SC_N>`__
| NLON `[sec:SC_N] <#sec:SC_N>`__
| DLON `[sec:SC_D] <#sec:SC_D>`__
| DLAT `[sec:SC_D] <#sec:SC_D>`__
| EXTRACT_TILES_FILTER_OPTS `[sec:SC_E] <#sec:SC_E>`__
| EXTRACT_TILES_VAR_LIST `[sec:SC_E] <#sec:SC_E>`__

**Deprecated:**

EXTRACT_OUT_DIR\ `[sec:SC_E] <#sec:SC_E>`__

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

GEMPAKTOCF_JAR `[sec:SC_G] <#sec:SC_G>`__

[dir]

| GEMPAKTOCF_INPUT_DIR `[sec:SC_G] <#sec:SC_G>`__
| GEMPAKTOCF_OUTPUT_DIR `[sec:SC_G] <#sec:SC_G>`__

[filename_templates]

| GEMPAKTOCF_INPUT_TEMPLATE `[sec:SC_G] <#sec:SC_G>`__
| GEMPAKTOCF_OUTPUT_TEMPLATE `[sec:SC_G] <#sec:SC_G>`__

[config]

| GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS `[sec:SC_G] <#sec:SC_G>`__

**Deprecated:**

| GEMPAKTOCF_CLASSPATH `[sec:SC_G] <#sec:SC_G>`__

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

| FCST_GRID_STAT_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_GRID_STAT_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| GRID_STAT_OUTPUT_DIR `[sec:SC_G] <#sec:SC_G>`__

[filename_templates]

| FCST_GRID_STAT_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_GRID_STAT_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__
| GRID_STAT_VERIFICATION_MASK_TEMPLATE (optional)
  `[sec:SC_G] <#sec:SC_G>`__

[config]

| GRID_STAT_CONFIG_FILE `[sec:SC_G] <#sec:SC_G>`__
| FCST_GRID_STAT_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_GRID_STAT_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| GRID_STAT_ONCE_PER_FIELD `[sec:SC_G] <#sec:SC_G>`__
| FCST_GRID_STAT_PROB_THRESH (optional) `[sec:SC_F] <#sec:SC_F>`__
| OBS_GRID_STAT_PROB_THRESH (optional) `[sec:SC_O] <#sec:SC_O>`__
| GRID_STAT_NEIGHBORHOOD_WIDTH (optional) `[sec:SC_G] <#sec:SC_G>`__
| GRID_STAT_NEIGHBORHOOD_SHAPE (optional) `[sec:SC_G] <#sec:SC_G>`__
| FCST_GRID_STAT_WINDOW_BEGIN (optional) `[sec:SC_F] <#sec:SC_F>`__
| FCST_GRID_STAT_WINDOW_END (optional) `[sec:SC_F] <#sec:SC_F>`__
| OBS_GRID_STAT_WINDOW_BEGIN (optional) `[sec:SC_O] <#sec:SC_O>`__
| OBS_GRID_STAT_WINDOW_END (optional) `[sec:SC_O] <#sec:SC_O>`__

**Deprecated:**

| GRID_STAT_OUT_DIR\ `[sec:SC_G] <#sec:SC_G>`__
| GRID_STAT_CONFIG\ `[sec:SC_G] <#sec:SC_G>`__

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

| PLOTTING_SCRIPTS_DIR `[sec:SC_P] <#sec:SC_P>`__
| STAT_FILES_INPUT_DIR `[sec:SC_S] <#sec:SC_S>`__
| PLOTTING_OUTPUT_DIR `[sec:SC_P] <#sec:SC_P>`__

[config]

| VERIF_CASE `[sec:SC_V] <#sec:SC_V>`__
| VERIF_TYPE `[sec:SC_V] <#sec:SC_V>`__
| PLOT_TIME `[sec:SC_P] <#sec:SC_P>`__
| VALID_BEG `[sec:SC_V] <#sec:SC_V>`__
| VALID_END `[sec:SC_V] <#sec:SC_V>`__
| INIT_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_END `[sec:SC_I] <#sec:SC_I>`__
| VALID_HOUR_METHOD `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_BEG `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_END `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_INCREMENT `[sec:SC_V] <#sec:SC_V>`__
| INIT_HOUR_METHOD `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| MODEL<n>_NAME `[sec:SC_M] <#sec:SC_M>`__
| MODEL<n>_OBS_NAME `[sec:SC_M] <#sec:SC_M>`__
| MODEL<n>_NAME_ON_PLOT `[sec:SC_M] <#sec:SC_M>`__
| FCST_VAR<n>_NAME `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_LEVELS `[sec:SC_F] <#sec:SC_F>`__
| REGION_LIST `[sec:SC_R] <#sec:SC_R>`__
| LEAD_LIST `[sec:SC_L] <#sec:SC_L>`__
| INTERP `[sec:SC_I] <#sec:SC_I>`__
| PLOT_STATS_LIST `[sec:SC_P] <#sec:SC_P>`__
| CI_METHOD `[sec:SC_C] <#sec:SC_C>`__
| VERIF_GRID `[sec:SC_V] <#sec:SC_V>`__
| EVENT_EQUALIZATION `[sec:SC_E] <#sec:SC_E>`__

The following values are **optional** in the METplus Wrappers
configuration file:

| FCST_VAR<n>_THRESH `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_OPTIONS `[sec:SC_F] <#sec:SC_F>`__
| VAR<n>_FOURIER_DECOMP `[sec:SC_V] <#sec:SC_V>`__
| VAR<n>_WAVE_NUM_LIST `[sec:SC_V] <#sec:SC_V>`__

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

| FCST_MODE_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| MODE_OUTPUT_DIR `[sec:SC_M] <#sec:SC_M>`__

[filename_templates]

| FCST_MODE_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__

[config]

| MODE_CONFIG_FILE `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| MODE_QUILT `[sec:SC_M] <#sec:SC_M>`__
| MODE_CONV_RADIUS `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_CONV_RADIUS `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_CONV_RADIUS `[sec:SC_O] <#sec:SC_O>`__
| MODE_CONV_THRESH `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_CONV_THRESH `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_CONV_THRESH `[sec:SC_O] <#sec:SC_O>`__
| MODE_MERGE_THRESH `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_MERGE_THRESH `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_MERGE_THRESH `[sec:SC_O] <#sec:SC_O>`__
| MODE_MERGE_FLAG `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_MERGE_FLAG `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_MERGE_FLAG `[sec:SC_O] <#sec:SC_O>`__
| MODE_MERGE_CONFIG_FILE `[sec:SC_M] <#sec:SC_M>`__
| FCST_MODE_WINDOW_BEGIN `[sec:SC_F] <#sec:SC_F>`__
| FCST_MODE_WINDOW_END `[sec:SC_F] <#sec:SC_F>`__
| OBS_MODE_WINDOW_BEGIN `[sec:SC_O] <#sec:SC_O>`__
| OBS_MODE_WINDOW_END `[sec:SC_O] <#sec:SC_O>`__

**Deprecated:**

| MODE_OUT_DIR\ `[sec:SC_M] <#sec:SC_M>`__
| MODE_CONFIG\ `[sec:SC_M] <#sec:SC_M>`__

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

| FCST_MTD_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_MTD_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| MTD_OUTPUT_DIR `[sec:SC_M] <#sec:SC_M>`__

[filename_templates]

| FCST_MTD_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_MTD_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__

[config]

| MTD_CONFIG_FILE `[sec:SC_M] <#sec:SC_M>`__
| MTD_MIN_VOLUME `[sec:SC_M] <#sec:SC_M>`__
| MTD_SINGLE_RUN `[sec:SC_M] <#sec:SC_M>`__
| MTD_SINGLE_DATA_SRC `[sec:SC_M] <#sec:SC_M>`__
| FCST_MTD_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_MTD_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| FCST_MTD_CONV_RADIUS `[sec:SC_F] <#sec:SC_F>`__
| FCST_MTD_CONV_THRESH `[sec:SC_F] <#sec:SC_F>`__ OBS_MTD_CONV_RADIUS
  `[sec:SC_O] <#sec:SC_O>`__
| OBS_MTD_CONV_THRESH `[sec:SC_O] <#sec:SC_O>`__

**Deprecated:**

| MTD_OUT_DIR\ `[sec:SC_M] <#sec:SC_M>`__
| MTD_CONFIG\ `[sec:SC_M] <#sec:SC_M>`__

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

| PB2NC_INPUT_DIR `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_OUTPUT_DIR `[sec:SC_P] <#sec:SC_P>`__

[filename_templates]

| PB2NC_INPUT_TEMPLATE `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_OUTPUT_TEMPLATE `[sec:SC_P] <#sec:SC_P>`__

[config]

| PB2NC_SKIP_IF_OUTPUT_EXISTS `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_OFFSETS `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_INPUT_DATATYPE `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_CONFIG_FILE `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_MESSAGE_TYPE (optional) `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_STATION_ID (optional) `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_GRID (optional) `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_POLY `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_OBS_BUFR_VAR_LIST (optional) `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_TIME_SUMMARY_FLAG `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_TIME_SUMMARY_BEG `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_TIME_SUMMARY_END `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_TIME_SUMMARY_VAR_NAMES `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_TIME_SUMMARY_TYPES `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_WINDOW_BEGIN `[sec:SC_P] <#sec:SC_P>`__
| PB2NC_WINDOW_END `[sec:SC_P] <#sec:SC_P>`__

**Deprecated:**

| PREPBUFR_DATA_DIR\ `[sec:SC_P] <#sec:SC_P>`__
| PREPBUFR_MODEL_DIR_NAME\ `[sec:SC_P] <#sec:SC_P>`__
| PREPBUFR_DIR_REGEX\ `[sec:SC_P] <#sec:SC_P>`__
| PREPBUFR_FILE_REGEX\ `[sec:SC_P] <#sec:SC_P>`__
| NC_FILE_TMPL\ `[sec:SC_N] <#sec:SC_N>`__
| PB2NC_VERTICAL_LEVEL\ `[sec:SC_P] <#sec:SC_P>`__
| OBS_BUFR_VAR_LIST\ `[sec:SC_O] <#sec:SC_O>`__
| TIME_SUMMARY_FLAG\ `[sec:SC_T] <#sec:SC_T>`__
| TIME_SUMMARY_BEG\ `[sec:SC_T] <#sec:SC_T>`__
| TIME_SUMMARY_END\ `[sec:SC_T] <#sec:SC_T>`__
| TIME_SUMMARY_VAR_NAMES\ `[sec:SC_T] <#sec:SC_T>`__
| TIME_SUMMARY_TYPE\ `[sec:SC_T] <#sec:SC_T>`__
| OVERWRITE_NC_OUTPUT\ `[sec:SC_O] <#sec:SC_O>`__
| VERTICAL_LOCATION\ `[sec:SC_V] <#sec:SC_V>`__

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

| FCST_PCP_COMBINE_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| FCST_PCP_COMBINE_OUTPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| OBS_PCP_COMBINE_OUTPUT_DIR `[sec:SC_O] <#sec:SC_O>`__

[filename_templates]

| FCST_PCP_COMBINE_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| FCST_PCP_COMBINE_OUTPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__
| OBS_PCP_COMBINE_OUTPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__

[config]

| FCST_IS_PROB `[sec:SC_F] <#sec:SC_F>`__
| OBS_IS_PROB `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_<n>_FIELD_NAME `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_<n>_FIELD_NAME `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_DATA_INTERVAL `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_DATA_INTERVAL `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_TIMES_PER_FILE `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_TIMES_PER_FILE `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_IS_DAILY_FILE `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_IS_DAILY_FILE `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_INPUT_LEVEL `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_INPUT_LEVEL `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_RUN `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_RUN `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_METHOD `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_METHOD `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_MIN_FORECAST `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_MIN_FORECAST `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_MAX_FORECAST `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_MAX_FORECAST `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_STAT_LIST `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_STAT_LIST `[sec:SC_O] <#sec:SC_O>`__
| FCST_PCP_COMBINE_DERIVE_LOOKBACK `[sec:SC_F] <#sec:SC_F>`__
| OBS_PCP_COMBINE_DERIVE_LOOKBACK `[sec:SC_O] <#sec:SC_O>`__
| PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS `[sec:SC_P] <#sec:SC_P>`__

**Deprecated:**

| PCP_COMBINE_METHOD\ `[sec:SC_P] <#sec:SC_P>`__
| FCST_MIN_FORECAST\ `[sec:SC_F] <#sec:SC_F>`__
| FCST_MAX_FORECAST\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_MIN_FORECAST\ `[sec:SC_O] <#sec:SC_O>`__
| OBS_MAX_FORECAST\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_DATA_INTERVAL\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_DATA_INTERVAL\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_IS_DAILY_FILE\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_IS_DAILY_FILE\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_TIMES_PER_FILE\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_TIMES_PER_FILE\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_LEVEL\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_LEVEL\ `[sec:SC_O] <#sec:SC_O>`__

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

| FCST_POINT_STAT_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_POINT_STAT_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__
| POINT_STAT_OUTPUT_DIR `[sec:SC_P] <#sec:SC_P>`__

[filename_templates]

| FCST_POINT_STAT_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_POINT_STAT_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__
| POINT_STAT_VERIFICATION_MASK_TEMPLATE (optional)
  `[sec:SC_P] <#sec:SC_P>`__

[config]

| POINT_STAT_OFFSETS `[sec:SC_P] <#sec:SC_P>`__
| FCST_POINT_STAT_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_POINT_STAT_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| POINT_STAT_CONFIG_FILE `[sec:SC_P] <#sec:SC_P>`__
| MODEL `[sec:SC_M] <#sec:SC_M>`__
| POINT_STAT_REGRID_TO_GRID `[sec:SC_P] <#sec:SC_P>`__
| POINT_STAT_GRID `[sec:SC_P] <#sec:SC_P>`__
| POINT_STAT_POLY `[sec:SC_P] <#sec:SC_P>`__
| POINT_STAT_STATION_ID `[sec:SC_P] <#sec:SC_P>`__
| POINT_STAT_MESSAGE_TYPE `[sec:SC_P] <#sec:SC_P>`__
| FCST_POINT_STAT_WINDOW_BEGIN (optional) `[sec:SC_F] <#sec:SC_F>`__
| FCST_POINT_STAT_WINDOW_END (optional) `[sec:SC_F] <#sec:SC_F>`__
| OBS_POINT_STAT_WINDOW_BEGIN (optional) `[sec:SC_O] <#sec:SC_O>`__
| OBS_POINT_STAT_WINDOW_END (optional) `[sec:SC_O] <#sec:SC_O>`__
| POINT_STAT_NEIGHBORHOOD_WIDTH (optional) `[sec:SC_P] <#sec:SC_P>`__
| POINT_STAT_NEIGHBORHOOD_SHAPE (optional) `[sec:SC_P] <#sec:SC_P>`__

**Deprecated:**

| FCST_INPUT_DIR\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_INPUT_DIR\ `[sec:SC_O] <#sec:SC_O>`__
| START_HOUR\ `[sec:SC_S] <#sec:SC_S>`__
| END_HOUR\ `[sec:SC_E] <#sec:SC_E>`__
| BEG_TIME\ `[sec:SC_B] <#sec:SC_B>`__
| FCST_HR_START\ `[sec:SC_F] <#sec:SC_F>`__
| FCST_HR_END\ `[sec:SC_F] <#sec:SC_F>`__
| FCST_HR_INTERVAL\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_INPUT_DIR_REGEX\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_INPUT_DIR_REGEX\ `[sec:SC_F] <#sec:SC_F>`__
| FCST_INPUT_FILE_REGEX\ `[sec:SC_F] <#sec:SC_F>`__
| OBS_INPUT_FILE_REGEX\ `[sec:SC_O] <#sec:SC_O>`__
| OBS_INPUT_FILE_TMPL\ `[sec:SC_O] <#sec:SC_O>`__
| FCST_INPUT_FILE_TMPL\ `[sec:SC_F] <#sec:SC_F>`__
| REGRID_TO_GRID\ `[sec:SC_R] <#sec:SC_R>`__

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

| FCST_REGRID_DATA_PLANE_INPUT_DIR `[sec:SC_F] <#sec:SC_F>`__
| OBS_REGRID_DATA_PLANE_INPUT_DIR `[sec:SC_O] <#sec:SC_O>`__

[filename_templates]

| FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE `[sec:SC_F] <#sec:SC_F>`__
| OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE `[sec:SC_O] <#sec:SC_O>`__

[config]

| FCST_REGRID_DATA_PLANE_RUN `[sec:SC_F] <#sec:SC_F>`__
| OBS_REGRID_DATA_PLANE_RUN `[sec:SC_O] <#sec:SC_O>`__
| REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS `[sec:SC_R] <#sec:SC_R>`__
| REGRID_DATA_PLANE_VERIF_GRID `[sec:SC_R] <#sec:SC_R>`__
| FCST_REGRID_DATA_PLANE_INPUT_DATATYPE `[sec:SC_F] <#sec:SC_F>`__
| OBS_REGRID_DATA_PLANE_INPUT_DATATYPE `[sec:SC_O] <#sec:SC_O>`__
| REGRID_DATA_PLANE_GAUSSIAN_DX
| REGRID_DATA_PLANE_GAUSSIAN_RADIUS
| REGRID_DATA_PLANE_WIDTH
| REGRID_DATA_PLANE_METHOD

**Deprecated:**

VERIFICATION_GRID\ `[sec:SC_V] <#sec:SC_V>`__

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

| SERIES_BY_INIT_FILTERED_OUTPUT_DIR `[sec:SC_S] <#sec:SC_S>`__
| SERIES_BY_INIT_OUTPUT_DIR `[sec:SC_S] <#sec:SC_S>`__

[regex_patterns]

| FCST_TILE_PREFIX `[sec:SC_F] <#sec:SC_F>`__
| ANLY_TILE_PREFIX `[sec:SC_A] <#sec:SC_A>`__
| FCST_TILE_REGEX `[sec:SC_F] <#sec:SC_F>`__
| ANLY_TILE_REGEX `[sec:SC_A] <#sec:SC_A>`__
| FCST_NC_TILE_REGEX `[sec:SC_F] <#sec:SC_F>`__
| ANLY_NC_TILE_REGEX `[sec:SC_A] <#sec:SC_A>`__
| FCST_ASCII_REGEX_LEAD `[sec:SC_F] <#sec:SC_F>`__
| ANLY_ASCII_REGEX_LEAD `[sec:SC_A] <#sec:SC_A>`__

[config]

| INIT_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_INCLUDE `[sec:SC_I] <#sec:SC_I>`__
| INIT_EXCLUDE `[sec:SC_I] <#sec:SC_I>`__
| SERIES_ANALYSIS_FILTER_OPTS `[sec:SC_S] <#sec:SC_S>`__

**Deprecated:**

SERIES_INIT_FILTERED_OUT_DIR\ `[sec:SC_S] <#sec:SC_S>`__

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

| SERIES_BY_LEAD_FILTERED_OUTPUT `[sec:SC_S] <#sec:SC_S>`__
| SERIES_BY_LEAD_OUTPUT_DIR `[sec:SC_S] <#sec:SC_S>`__

[config]

| INIT_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_TIME_FMT `[sec:SC_I] <#sec:SC_I>`__
| INIT_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| SERIES_BY_LEAD_GROUP_FCSTS `[sec:SC_S] <#sec:SC_S>`__
| LEAD_SEQ_<n> `[sec:SC_L] <#sec:SC_L>`__
| LEAD_SEQ_<n>_LABEL `[sec:SC_L] <#sec:SC_L>`__
| SERIES_ANALYSIS_FILTER_OPT `[sec:SC_S] <#sec:SC_S>`__
| VAR_LIST `[sec:SC_V] <#sec:SC_V>`__
| STAT_LIST `[sec:SC_S] <#sec:SC_S>`__

**Deprecated:**

SERIES_LEAD_FILTERED_OUT_DIR\ `[sec:SC_S] <#sec:SC_S>`__

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

| STAT_ANALYSIS_LOOKIN_DIR\ `[sec:SC_S] <#sec:SC_S>`__
| STAT_ANALYSIS_OUTPUT_DIR `[sec:SC_S] <#sec:SC_S>`__

[config]

| LOOP_BY `[sec:SC_L] <#sec:SC_L>`__
| [VALID/INIT]\_TIME_FMT `[sec:SC_V] <#sec:SC_V>`__
| [VALID/INIT]\_BEG `[sec:SC_V] <#sec:SC_V>`__
  `[sec:SC_I] <#sec:SC_I>`__
| [VALID/INIT]\_END `[sec:SC_V] <#sec:SC_V>`__
  `[sec:SC_I] <#sec:SC_I>`__
| VALID_HOUR_METHOD `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_BEG `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_END `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_INCREMENT `[sec:SC_V] <#sec:SC_V>`__
| INIT_HOUR_METHOD `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| STAT_ANALYSIS_CONFIG `[sec:SC_S] <#sec:SC_S>`__
| MODEL `[sec:SC_M] <#sec:SC_M>`__
| OBTYPE `[sec:SC_O] <#sec:SC_O>`__
| JOB_NAME `[sec:SC_J] <#sec:SC_J>`__
| JOB_ARGS `[sec:SC_J] <#sec:SC_J>`__

The following values are **optional** in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

| DESC `[sec:SC_D] <#sec:SC_D>`__
| FCST_LEAD `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_NAME `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_LEVEL `[sec:SC_F] <#sec:SC_F>`__
| OBS_VAR<n>_NAME `[sec:SC_O] <#sec:SC_O>`__
| OBS_VAR<n>_LEVEL\ `[sec:SC_O] <#sec:SC_O>`__
| REGION `[sec:SC_R] <#sec:SC_R>`__
| INTERP `[sec:SC_I] <#sec:SC_I>`__
| INTERP_PTS `[sec:SC_I] <#sec:SC_I>`__
| FCST_THRESH `[sec:SC_F] <#sec:SC_F>`__
| COV_THRESH `[sec:SC_C] <#sec:SC_C>`__
| LINE_TYPE `[sec:SC_L] <#sec:SC_L>`__
| STAT_ANALYSIS_DUMP_ROW_TMPL `[sec:SC_S] <#sec:SC_S>`__
| STAT_ANALYSIS_OUT_STAT_TMPL `[sec:SC_S] <#sec:SC_S>`__

The following values **must** be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = processes:

| STAT_ANALYSIS_OUTPUT_DIR `[sec:SC_S] <#sec:SC_S>`__
| VERIF_CASE `[sec:SC_V] <#sec:SC_V>`__
| VERIF_TYPE `[sec:SC_V] <#sec:SC_V>`__
| PLOT_TIME `[sec:SC_P] <#sec:SC_P>`__
| [VALID/INIT]\_BEG `[sec:SC_V] <#sec:SC_V>`__
  `[sec:SC_I] <#sec:SC_I>`__
| [VALID/INIT]\_END `[sec:SC_V] <#sec:SC_V>`__
  `[sec:SC_I] <#sec:SC_I>`__
| VALID_HOUR_METHOD `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_BEG `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_END `[sec:SC_V] <#sec:SC_V>`__
| VALID_HOUR_INCREMENT `[sec:SC_V] <#sec:SC_V>`__
| INIT_HOUR_METHOD `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| STAT_ANALYSIS_CONFIG `[sec:SC_S] <#sec:SC_S>`__
| MODEL<n>_NAME `[sec:SC_M] <#sec:SC_M>`__
| MODEL<n>_OBS_NAME `[sec:SC_M] <#sec:SC_M>`__
| MODEL<n>_NAME_ON_PLOT `[sec:SC_M] <#sec:SC_M>`__
| FCST_VAR<n>_NAME `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_LEVELS `[sec:SC_F] <#sec:SC_F>`__
| REGION_LIST `[sec:SC_R] <#sec:SC_R>`__
| LEAD_LIST `[sec:SC_L] <#sec:SC_L>`__
| INTERP `[sec:SC_I] <#sec:SC_I>`__
| LINE_TYPE `[sec:SC_L] <#sec:SC_L>`__

The following values are optional in the METplus Wrappers configuration
file for running with LOOP_ORDER = processes:

| FCST_VAR<n>_THRESH `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_THRESH `[sec:SC_F] <#sec:SC_F>`__
| FCST_VAR<n>_OPTIONS `[sec:SC_F] <#sec:SC_F>`__
| VAR<n>_FOURIER_DECOMP `[sec:SC_V] <#sec:SC_V>`__
| VAR<n>_WAVE_NUM_LIST `[sec:SC_V] <#sec:SC_V>`__
| **Deprecated:**

STAT_ANALYSIS_OUT_DIR\ `[sec:SC_S] <#sec:SC_S>`__

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

| TC_PAIRS_ADECK_INPUT_DIR `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_BDECK_INPUT_DIR `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_EDECK_INPUT_DIR `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_OUTPUT_DIR `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_REFORMAT_DIR `[sec:SC_T] <#sec:SC_T>`__
| [filename_templates]

| TC_PAIRS_ADECK_INPUT_TEMPLATE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_BDECK_INPUT_TEMPLATE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_EDECK_INPUT_TEMPLATE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_OUTPUT_TEMPLATE `[sec:SC_T] <#sec:SC_T>`__
| [config]

| TC_PAIRS_CONFIG_FILE `[sec:SC_T] <#sec:SC_T>`__
| INIT_BEG `[sec:SC_I] <#sec:SC_I>`__
| INIT_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_INCREMENT `[sec:SC_I] <#sec:SC_I>`__
| INIT_HOUR_END `[sec:SC_I] <#sec:SC_I>`__
| INIT_INCLUDE `[sec:SC_I] <#sec:SC_I>`__
| INIT_EXCLUDE `[sec:SC_I] <#sec:SC_I>`__
| TC_PAIRS_READ_ALL_FILES `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_MODEL `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_STORM_ID `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_BASIN `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_CYCLONE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_STORM_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_DLAND_FILE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_MISSING_VAL_TO_REPLACE `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_MISSING_VAL `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_SKIP_IF_REFACTOR_EXISTS `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_SKIP_IF_OUTPUT_EXISTS `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_REFORMAT_DECK `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_REFORMAT_TYPE `[sec:SC_T] <#sec:SC_T>`__
| **Deprecated:**
| ADECK_TRACK_DATA_DIR\ `[sec:SC_A] <#sec:SC_A>`__
| BDECK_TRACK_DATA_DIR\ `[sec:SC_B] <#sec:SC_B>`__
| TRACK_DATA_SUBDIR_MOD\ `[sec:SC_T] <#sec:SC_T>`__
| TC_PAIRS_DIR\ `[sec:SC_T] <#sec:SC_T>`__
| TOP_LEVEL_DIRS\ `[sec:SC_T] <#sec:SC_T>`__
| MODEL\ `[sec:SC_M] <#sec:SC_M>`__
| STORM_ID\ `[sec:SC_S] <#sec:SC_S>`__
| BASIN\ `[sec:SC_B] <#sec:SC_B>`__
| CYCLONE\ `[sec:SC_C] <#sec:SC_C>`__
| STORM_NAME\ `[sec:SC_S] <#sec:SC_S>`__
| DLAND_FILE\ `[sec:SC_D] <#sec:SC_D>`__
| TRACK_TYPE\ `[sec:SC_T] <#sec:SC_T>`__
| ADECK_FILE_PREFIX\ `[sec:SC_A] <#sec:SC_A>`__
| BDECK_FILE_PREFIX\ `[sec:SC_B] <#sec:SC_B>`__
| MISSING_VAL_TO_REPLACE\ `[sec:SC_M] <#sec:SC_M>`__
| MISSING_VAL\ `[sec:SC_M] <#sec:SC_M>`__

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

| TC_STAT_INPUT_DIR `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_OUTPUT_DIR `[sec:SC_T] <#sec:SC_T>`__

[config]

| TC_STAT_RUN_VIA `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_CONFIG_FILE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_CMD_LINE_JOB `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_JOBS_LIST `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_AMODEL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_BMODEL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_DESC `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_STORM_ID `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_BASIN `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_CYCLONE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_STORM_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_BEG `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_INCLUDE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_EXCLUDE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_HOUR `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_BEG `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_END `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_INCLUDE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_EXCLUDE `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_HOUR `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_LEAD_REQ `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_MASK `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_MASK `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_VALID_HOUR `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_LEAD `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_TRACK_WATCH_WARN `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_COLUMN_THRESH_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_COLUNN_THRESH_VAL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_COLUMN_STR_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_COLUMN_STR_VAL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_THRESH_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_THRESH_VAL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_STR_NAME `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_INIT_STR_VAL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_WATER_ONLY `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_LANDFALL `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_LANDFALL_BEG `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_LANDFALL_END `[sec:SC_T] <#sec:SC_T>`__
| TC_STAT_MATCH_POINTS `[sec:SC_T] <#sec:SC_T>`__

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

| LOOP ORDER `[sec:SC_L] <#sec:SC_L>`__
| TCMPR_PLOTTER_CONFIG_FILE `[sec:SC_C] <#sec:SC_C>`__
| TCMPR_PLOTTER_PREFIX `[sec:SC_P] <#sec:SC_P>`__
| TCMPR_PLOTTER_TITLE `[sec:SC_T] <#sec:SC_T>`__
| TCMPR_PLOTTER_SUBTITLE `[sec:SC_S] <#sec:SC_S>`__
| TCMPR_PLOTTER_XLAB `[sec:SC_X] <#sec:SC_X>`__
| TCMPR_PLOTTER_YLAB `[sec:SC_Y] <#sec:SC_Y>`__
| TCMPR_PLOTTER_XLIM\ `[sec:SC_X] <#sec:SC_X>`__
| TCMPR_PLOTTER_YLIM `[sec:SC_Y] <#sec:SC_Y>`__
| TCMPR_PLOTTER_FILTER `[sec:SC_F] <#sec:SC_F>`__
| TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE `[sec:SC_F] <#sec:SC_F>`__
| TCMPR_PLOTTER_DEP_VARS `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_SCATTER_X `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_SCATTER_Y `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_SKILL_REF `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_SERIES `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_SERIES_CI `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_LEGEND `[sec:SC_L] <#sec:SC_L>`__
| TCMPR_PLOTTER_LEAD `[sec:SC_L] <#sec:SC_L>`__
| TCMPR_PLOTTER_PLOT_TYPES `[sec:SC_P] <#sec:SC_P>`__
| TCMPR_PLOTTER_RP_DIFF `[sec:SC_R] <#sec:SC_R>`__
| TCMPR_PLOTTER_DEMO_YR `[sec:SC_D] <#sec:SC_D>`__
| TCMPR_PLOTTER_HFIP_BASELINE `[sec:SC_H] <#sec:SC_H>`__
| TCMPR_PLOTTER_FOOTNOTE_FLAG `[sec:SC_F] <#sec:SC_F>`__
| TCMPR_PLOTTER_PLOT_CONFIG_OPTS `[sec:SC_P] <#sec:SC_P>`__
| TCMPR_PLOTTER_SAVE_DATA `[sec:SC_D] <#sec:SC_D>`__

The following are TCMPR flags, if set to 'no', then don't set flag, if
set to 'yes', then set the flag

| TCMPR_PLOTTER_NO_EE `[sec:SC_N] <#sec:SC_N>`__
| TCMPR_PLOTTER_NO_LOG `[sec:SC_N] <#sec:SC_N>`__
| TCMPR_PLOTTER_SAVE `[sec:SC_S] <#sec:SC_S>`__
| TCMPR_PLOTTER_TCMPR_DATA_DIR `[sec:SC_T] <#sec:SC_T>`__
| TCMPR_PLOTTER_PLOT_OUTPUT_DIR `[sec:SC_T] <#sec:SC_T>`__

**Deprecated:**

TCMPR_PLOT_OUT_DIR\ `[sec:SC_T] <#sec:SC_T>`__
