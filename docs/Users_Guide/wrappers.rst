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


ASCII2NC
--------

.. _description-1:

Description
~~~~~~~~~~~

Used to configure the MET tool ASCII2NC

.. _configuration-1:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`ASCII2NC_INPUT_DIR`
| :term:`ASCII2NC_OUTPUT_DIR`

[filename_templates]

| :term:`ASCII2NC_INPUT_TEMPLATE`
| :term:`ASCII2NC_OUTPUT_TEMPLATE`

[config]

| :term:`LOG_ASCII2NC_VERBOSITY`
| :term:`ASCII2NC_SKIP_IF_OUTPUT_EXISTS`
| :term:`ASCII2NC_CONFIG_FILE`
| :term:`ASCII2NC_FILE_WINDOW_BEGIN`
| :term:`ASCII2NC_FILE_WINDOW_END`
| :term:`ASCII2NC_WINDOW_BEGIN`
| :term:`ASCII2NC_WINDOW_END`
| :term:`ASCII2NC_INPUT_FORMAT`
| :term:`ASCII2NC_MASK_GRID`
| :term:`ASCII2NC_MASK_POLY`
| :term:`ASCII2NC_MASK_SID`
| :term:`ASCII2NC_TIME_SUMMARY_FLAG`
| :term:`ASCII2NC_TIME_SUMMARY_RAW_DATA`
| :term:`ASCII2NC_TIME_SUMMARY_BEG`
| :term:`ASCII2NC_TIME_SUMMARY_END`
| :term:`ASCII2NC_TIME_SUMMARY_STEP`
| :term:`ASCII2NC_TIME_SUMMARY_WIDTH`
| :term:`ASCII2NC_TIME_SUMMARY_GRIB_CODES`
| :term:`ASCII2NC_TIME_SUMMARY_VAR_NAMES`
| :term:`ASCII2NC_TIME_SUMMARY_TYPES`
| :term:`ASCII2NC_TIME_SUMMARY_VALID_FREQ`
| :term:`ASCII2NC_TIME_SUMMARY_VALID_THRESH`
| :term:`ASCII2NC_CUSTOM_LOOP_LIST`



CyclonePlotter
--------------

.. _description-2:

Description
~~~~~~~~~~~

This wrapper does not have a corresponding MET tool but instead wraps
the logic necessary to create plots of cyclone tracks. Currently only
the output from the MET tc-pairs tool can be plotted.

.. _configuration-2:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`CYCLONE_PLOTTER_INPUT_DIR`
| :term:`CYCLONE_PLOTTER_OUTPUT_DIR`

[config]

| :term:`CYCLONE_PLOTTER_INIT_DATE`
| :term:`CYCLONE_PLOTTER_INIT_HR`
| :term:`CYCLONE_PLOTTER_MODEL`
| :term:`CYCLONE_PLOTTER_PLOT_TITLE`
| :term:`CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE`
| :term:`CYCLONE_PLOTTER_CROSS_MARKER_SIZE`
| :term:`CYCLONE_PLOTTER_GENERATE_TRACK_ASCII`

.. warning:: **DEPRECATED:**

   | :term:`CYCLONE_OUT_DIR`
   | :term:`CYCLONE_INIT_DATE`
   | :term:`CYCLONE_INIT_HR`
   | :term:`CYCLONE_MODEL`
   | :term:`CYCLONE_PLOT_TITLE`
   | :term:`CYCLONE_CIRCLE_MARKER_SIZE`
   | :term:`CYCLONE_CROSS_MARKER_SIZE`
   | :term:`CYCLONE_GENERATE_TRACK_ASCII`

EnsembleStat
------------

.. _description-3:

Description
~~~~~~~~~~~

Used to configure the MET tool ensemble_stat.

.. _configuration-3:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_DIR`
| :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_DIR`
| :term:`FCST_ENSEMBLE_STAT_INPUT_DIR`
| :term:`ENSEMBLE_STAT_OUTPUT_DIR`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_INPUT_DIR`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_INPUT_DIR`

[filename_templates]

| :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE`
| :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE`
| :term:`FCST_ENSEMBLE_STAT_INPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_OUTPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE`

[config]

| :term:`LOG_ENSEMBLE_STAT_VERBOSITY`
| :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE`
| :term:`ENSEMBLE_STAT_REGRID_TO_GRID`
| :term:`ENSEMBLE_STAT_CONFIG_FILE`
| :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE`
| :term:`ENSEMBLE_STAT_N_MEMBERS`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_END`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_END`
| :term:`ENSEMBLE_STAT_ENS_THRESH`
| :term:`ENSEMBLE_STAT_ENS_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CUSTOM_LOOP_LIST`
| :term:`ENSEMBLE_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`ENS_VAR<n>_NAME` (optional)
| :term:`ENS_VAR<n>_LEVELS` (optional)
| :term:`ENS_VAR<n>_THRESH` (optional)
| :term:`ENS_VAR<n>_OPTIONS` (optional)
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_NAME` (optional)
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_LEVELS` (optional)
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_THRESH` (optional)
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_OPTIONS` (optional)
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_NAME` (optional)
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_LEVELS` (optional)
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_THRESH` (optional)
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_OPTIONS` (optional)

.. warning:: **DEPRECATED:**

   | :term:`ENSEMBLE_STAT_OUT_DIR`
   | :term:`ENSEMBLE_STAT_CONFIG`
   | :term:`ENSEMBLE_STAT_MET_OBS_ERROR_TABLE`
   | :term:`ENSEMBLE_STAT_GRID_VX`


Example
--------

.. _description-4:

Description
~~~~~~~~~~~

Used to demonstrate how the METplus wrappers handle looping and building commands.

.. _configuration-4:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`EXAMPLE_INPUT_DIR`

[filename_templates]

| :term:`EXAMPLE_INPUT_TEMPLATE`

[config]
| :term:`EXAMPLE_CUSTOM_LOOP_LIST`


ExtractTiles
------------

.. _description-5:

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

.. _configuration-5:

Configuration
~~~~~~~~~~~~~

The following should be set in the METplus configuration file to define
the dimensions and density of the tiles comprising the subregion:

[dir]

| :term:`EXTRACT_TILES_OUTPUT_DIR`
| :term:`EXTRACT_TILES_STAT_INPUT_DIR`
| :term:`FCST_EXTRACT_TILES_INPUT_DIR`
| :term:`OBS_EXTRACT_TILES_INPUT_DIR`

[filename_templates]

| :term:`FCST_EXTRACT_TILES_INPUT_TEMPLATE`
| :term:`OBS_EXTRACT_TILES_INPUT_TEMPLATE`
| :term:`FCST_EXTRACT_TILES_OUTPUT_TEMPLATE`
| :term:`OBS_EXTRACT_TILES_OUTPUT_TEMPLATE`
| :term:`EXTRACT_TILES_STAT_INPUT_TEMPLATE`

[config]

| :term:`EXTRACT_TILES_LON_ADJ`
| :term:`EXTRACT_TILES_LAT_ADJ`
| :term:`EXTRACT_TILES_NLAT`
| :term:`EXTRACT_TILES_NLON`
| :term:`EXTRACT_TILES_DLON`
| :term:`EXTRACT_TILES_DLAT`
| :term:`EXTRACT_TILES_FILTER_OPTS`
| :term:`EXTRACT_TILES_VAR_LIST`
| :term:`EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS`
| :term:`EXTRACT_TILES_CUSTOM_LOOP_LIST`

.. warning:: **DEPRECATED:**

   | :term:`EXTRACT_OUT_DIR`
   | :term:`LON_ADJ`
   | :term:`LAT_ADJ`
   | :term:`NLAT`
   | :term:`NLON`
   | :term:`DLON`
   | :term:`DLAT`
   | :term:`EXTRACT_TILES_OVERWRITE_TRACK`
   | :term:`EXTRACT_TILES_PAIRS_INPUT_DIR`
   | :term:`EXTRACT_TILES_FILTERED_OUTPUT_TEMPLATE`
   | :term:`EXTRACT_TILES_GRID_INPUT_DIR`

GempakToCF
----------

.. _description-6:

Description
~~~~~~~~~~~

Used to configure the utility GempakToCF.

.. _configuration-6:

Configuration
~~~~~~~~~~~~~

[exe]

| :term:`GEMPAKTOCF_JAR`

[dir]

| :term:`GEMPAKTOCF_INPUT_DIR`
| :term:`GEMPAKTOCF_OUTPUT_DIR`

[filename_templates]

| :term:`GEMPAKTOCF_INPUT_TEMPLATE`
| :term:`GEMPAKTOCF_OUTPUT_TEMPLATE`

[config]

| :term:`GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS`
| :term:`GEMPAKTOCF_CUSTOM_LOOP_LIST`

.. warning:: **DEPRECATED:**

   | :term:`GEMPAKTOCF_CLASSPATH`

GenVxMask
---------

.. _description-6a:

Description
~~~~~~~~~~~

Used to configure the MET tool GenVxMask to define and generate masking regions.

.. _configuration-6a:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`GEN_VX_MASK_INPUT_DIR`
| :term:`GEN_VX_MASK_INPUT_MASK_DIR`
| :term:`GEN_VX_MASK_OUTPUT_DIR`

[filename_templates]

| :term:`GEN_VX_MASK_INPUT_TEMPLATE`
| :term:`GEN_VX_MASK_INPUT_MASK_TEMPLATE`
| :term:`GEN_VX_MASK_OUTPUT_TEMPLATE`

[config]

| :term:`GEN_VX_MASK_OPTIONS`
| :term:`LOG_GEN_VX_MASK_VERBOSITY`
| :term:`GEN_VX_MASK_SKIP_IF_OUTPUT_EXISTS`
| :term:`GEN_VX_MASK_CUSTOM_LOOP_LIST`
| :term:`GEN_VX_MASK_FILE_WINDOW_BEGIN`
| :term:`GEN_VX_MASK_FILE_WINDOW_END`

GridDiag
--------

.. _description-7a:

Description
~~~~~~~~~~~

Used to configure the MET tool grid_diag.

.. _configuration-7a:

METplus Configuration
~~~~~~~~~~~~~~~~~~~~~

[dir]

| :term:`GRID_DIAG_INPUT_DIR`
| :term:`GRID_DIAG_OUTPUT_DIR`

[filename_templates]

| :term:`GRID_DIAG_INPUT_TEMPLATE`
| :term:`GRID_DIAG_OUTPUT_TEMPLATE`
| :term:`GRID_DIAG_VERIFICATION_MASK_TEMPLATE` (optional)


[config]

| :term:`LOG_GRID_DIAG_VERBOSITY`
| :term:`GRID_DIAG_CONFIG_FILE`
| :term:`GRID_DIAG_CUSTOM_LOOP_LIST`
| :term:`GRID_DIAG_INPUT_DATATYPE`
| :term:`GRID_DIAG_REGRID_METHOD`
| :term:`GRID_DIAG_REGRID_WIDTH`
| :term:`GRID_DIAG_REGRID_VLD_THRESH`
| :term:`GRID_DIAG_REGRID_SHAPE`
| :term:`GRID_DIAG_REGRID_TO_GRID`
| :term:`GRID_DIAG_DESCRIPTION`
| :term:`GRID_DIAG_SKIP_IF_OUTPUT_EXISTS`

MET Configuration
~~~~~~~~~~~~~~~~~

This is the MET configuration file used for this wrapper. Below the file contents are descriptions of each environment variable referenced in this file and how the METplus configuration variables relate to them.

.. literalinclude:: ../../parm/met_config/GridDiagConfig_wrapped

The following environment variables are referenced in the MET configuration file. The values are generated based on values in the METplus configuration files.

**${MODEL}** - Corresponds to MODEL in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    MODEL = GFS

Resulting value::

    model = "GFS";

**${DATA_FIELD}** - Formatted input field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.

METplus Configuration::

    [config]
    BOTH_VAR1_NAME = APCP
    BOTH_VAR1_LEVELS = L0
    BOTH_VAR1_OPTIONS = n_bins = 55; range  = [0, 55];

    BOTH_VAR2_NAME = PWAT
    BOTH_VAR2_LEVELS =  L0
    BOTH_VAR2_OPTIONS = n_bins = 35; range  = [35, 70];

Resulting value::

    { name="APCP"; level="L0"; n_bins = 55; range  = [0, 55]; },{ name="PWAT"; level="L0"; n_bins = 35; range  = [35, 70];}

**${DATA_FILE_TYPE}** - Type of input data set only if necessary to allow MET to read the data. Generated from GRID_DIAG_INPUT_DATATYPE in the METplus configuration file.

METplus Configuration::

    [config]
    GRID_DIAG_INPUT_DATATYPE = GRIB2

Resulting value::

    file_type = GRIB2;

**${REGRID_DICT}** - Corresponds to GRID_DIAG_REGRID_METHOD, GRID_DIAG_REGRID_WIDTH, GRID_DIAG_REGRID_VLD_THRESH, GRID_DIAG_REGRID_SHAPE, and GRID_DIAG_REGRID_TO_GRID in the METplus configuration file. If any of these variables are unset in METplus, value set in the default MET GridDiag configuration file will be used.

METplus Configuration 1::

    [config]
    GRID_DIAG_REGRID_SHAPE = SQUARE

Resulting value 1::

    regrid = {shape = SQUARE;}

METplus Configuration 2::

    [config]
    GRID_DIAG_REGRID_WIDTH = 2
    GRID_DIAG_REGRID_SHAPE = SQUARE

Resulting value 2::

    regrid = {width = 2; shape = SQUARE;}

METplus Configuration 3::

    [config]
    GRID_DIAG_REGRID_WIDTH = 2
    GRID_DIAG_REGRID_SHAPE = SQUARE
    GRID_DIAG_REGRID_TO_GRID = NONE

Resulting value 2::

    regrid = {to_grid = NONE; width = 2; shape = SQUARE;}

**${VERIF_MASK}** - Path to verification mask file. Generated from GRID_DIAG_VERIFICATION_MASK_TEMPLATE in the METplus configuration file. Filename template syntax can be used in here to find a file based on run time, i.e. file.{valid?fmt=%Y%m%d%H}.ext

METplus Configuration::

    [filename_templates]
    GRID_DIAG_VERIFICATION_MASK_TEMPLATE = MET_BASE/poly/SAO.poly

Resulting value::

    poly = "MET_BASE/poly/SAO.poly";

GridStat
--------

.. _description-7:

Description
~~~~~~~~~~~

Used to configure the MET tool grid_stat.

.. _configuration-7:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_GRID_STAT_INPUT_DIR`
| :term:`OBS_GRID_STAT_INPUT_DIR`
| :term:`GRID_STAT_OUTPUT_DIR`
| :term:`GRID_STAT_CLIMO_MEAN_INPUT_DIR`
| :term:`GRID_STAT_CLIMO_STDEV_INPUT_DIR`

[filename_templates]

| :term:`FCST_GRID_STAT_INPUT_TEMPLATE`
| :term:`OBS_GRID_STAT_INPUT_TEMPLATE`
| :term:`GRID_STAT_OUTPUT_TEMPLATE`
| :term:`GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
| :term:`GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE`
| :term:`GRID_STAT_VERIFICATION_MASK_TEMPLATE` (optional)


[config]

| :term:`LOG_GRID_STAT_VERBOSITY`
| :term:`GRID_STAT_OUTPUT_PREFIX`
| :term:`GRID_STAT_CONFIG_FILE`
| :term:`FCST_GRID_STAT_INPUT_DATATYPE`
| :term:`OBS_GRID_STAT_INPUT_DATATYPE`
| :term:`GRID_STAT_ONCE_PER_FIELD`
| :term:`GRID_STAT_CUSTOM_LOOP_LIST`
| :term:`GRID_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_GRID_STAT_PROB_THRESH` (optional)
| :term:`OBS_GRID_STAT_PROB_THRESH` (optional)
| :term:`GRID_STAT_NEIGHBORHOOD_WIDTH` (optional)
| :term:`GRID_STAT_NEIGHBORHOOD_SHAPE` (optional)
| :term:`GRID_STAT_NEIGHBORHOOD_COV_THRESH` (optional)
| :term:`FCST_GRID_STAT_WINDOW_BEGIN` (optional)
| :term:`FCST_GRID_STAT_WINDOW_END` (optional)
| :term:`OBS_GRID_STAT_WINDOW_BEGIN` (optional)
| :term:`OBS_GRID_STAT_WINDOW_END` (optional)
| :term:`FCST_GRID_STAT_FILE_WINDOW_BEGIN` (optional)
| :term:`FCST_GRID_STAT_FILE_WINDOW_END` (optional)
| :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN` (optional)
| :term:`OBS_GRID_STAT_FILE_WINDOW_END` (optional)
| :term:`FCST_GRID_STAT_VAR<n>_NAME` (optional)
| :term:`FCST_GRID_STAT_VAR<n>_LEVELS` (optional)
| :term:`FCST_GRID_STAT_VAR<n>_THRESH` (optional)
| :term:`FCST_GRID_STAT_VAR<n>_OPTIONS` (optional)
| :term:`OBS_GRID_STAT_VAR<n>_NAME` (optional)
| :term:`OBS_GRID_STAT_VAR<n>_LEVELS` (optional)
| :term:`OBS_GRID_STAT_VAR<n>_THRESH` (optional)
| :term:`OBS_GRID_STAT_VAR<n>_OPTIONS` (optional)

.. warning:: **DEPRECATED:**

   | :term:`GRID_STAT_OUT_DIR`
   | :term:`GRID_STAT_CONFIG`
   | :term:`CLIMO_GRID_STAT_INPUT_DIR`
   | :term:`CLIMO_GRID_STAT_INPUT_TEMPLATE`

MakePlots
---------

.. _description-8:

Description
~~~~~~~~~~~

The MakePlots wrapper creates various statistical plots using python
scripts for the various METplus Wrappers use cases. This can only be run
following StatAnalysis wrapper when LOOP_ORDER = processes. To run
MakePlots wrapper, include MakePlots in PROCESS_LIST.

.. _configuration-8:

Configuration
~~~~~~~~~~~~~

The following values **must** be defined in the METplus Wrappers
configuration file:

[dir]

| :term:`MAKE_PLOTS_SCRIPTS_DIR`
| :term:`MAKE_PLOTS_INPUT_DIR`
| :term:`MAKE_PLOTS_OUTPUT_DIR`

[config]

| :term:`MAKE_PLOTS_VERIF_CASE`
| :term:`MAKE_PLOTS_VERIF_TYPE`
| :term:`DATE_TYPE`
| :term:`MODEL\<n\>`
| :term:`MODEL<n>_OBTYPE`
| :term:`MODEL<n>_REFERENCE_NAME`
| :term:`GROUP_LIST_ITEMS`
| :term:`LOOP_LIST_ITEMS`
| :term:`MODEL_LIST`
| :term:`FCST_LEAD_LIST`
| :term:`VX_MASK_LIST`
| :term:`LINE_TYPE_LIST`
| :term:`MAKE_PLOTS_AVERAGE_METHOD`
| :term:`MAKE_PLOTS_STATS_LIST`
| :term:`MAKE_PLOTS_CI_METHOD`
| :term:`MAKE_PLOTS_VERIF_GRID`
| :term:`MAKE_PLOTS_EVENT_EQUALIZATION`

The following values are **optional** in the METplus Wrappers
configuration file:

[config]

| :term:`VAR<n>_FOURIER_DECOMP`
| :term:`VAR<n>_WAVE_NUM_LIST`
| :term:`FCST_VALID_HOUR_LIST`
| :term:`OBS_VALID_HOUR_LIST`
| :term:`FCST_INIT_HOUR_LIST`
| :term:`OBS_INIT_HOUR_LIST`
| :term:`OBS_LEAD_LIST`
| :term:`DESC_LIST`
| :term:`INTERP_MTHD_LIST`
| :term:`INTERP_PNTS_LIST`
| :term:`COV_THRESH_LIST`
| :term:`ALPHA_LIST`

.. warning:: **DEPRECATED:**

   | :term:`PLOTTING_SCRIPTS_DIR`
   | :term:`STAT_FILES_INPUT_DIR`
   | :term:`PLOTTING_OUTPUT_DIR`
   | :term:`VERIF_CASE`
   | :term:`VERIF_TYPE`
   | :term:`PLOT_TIME`
   | :term:`MODEL<n>_NAME`
   | :term:`MODEL<n>_OBS_NAME`
   | :term:`MODEL<n>_NAME_ON_PLOT`
   | :term:`VALID_HOUR_METHOD`
   | :term:`VALID_HOUR_BEG`
   | :term:`VALID_HOUR_END`
   | :term:`VALID_HOUR_INCREMENT`
   | :term:`INIT_HOUR_BEG`
   | :term:`INIT_HOUR_END`
   | :term:`INIT_HOUR_INCREMENT`
   | :term:`REGION_LIST`
   | :term:`LEAD_LIST`
   | :term:`LINE_TYPE`
   | :term:`INTERP`
   | :term:`PLOT_STATS_LIST`
   | :term:`CI_METHOD`
   | :term:`VERIF_GRID`
   | :term:`EVENT_EQUALIZATION`

MODE
----

.. _description-9:

Description
~~~~~~~~~~~

Used to configure the MET Method for Object-based Diagnostic Evaluation tool mode.

.. _configuration-9:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_MODE_INPUT_DIR`
| :term:`OBS_MODE_INPUT_DIR`
| :term:`MODE_OUTPUT_DIR`

[filename_templates]

| :term:`FCST_MODE_INPUT_TEMPLATE`
| :term:`OBS_MODE_INPUT_TEMPLATE`
| :term:`MODE_OUTPUT_TEMPLATE`
| :term:`MODE_VERIFICATION_MASK_TEMPLATE`

[config]

| :term:`LOG_MODE_VERBOSITY`
| :term:`MODE_OUTPUT_PREFIX`
| :term:`MODE_REGRID_TO_GRID`
| :term:`MODE_CONFIG_FILE`
| :term:`FCST_MODE_INPUT_DATATYPE`
| :term:`OBS_MODE_INPUT_DATATYPE`
| :term:`MODE_QUILT`
| :term:`MODE_CONV_RADIUS`
| :term:`FCST_MODE_CONV_RADIUS`
| :term:`OBS_MODE_CONV_RADIUS`
| :term:`MODE_CONV_THRESH`
| :term:`FCST_MODE_CONV_THRESH`
| :term:`OBS_MODE_CONV_THRESH`
| :term:`MODE_MERGE_THRESH`
| :term:`FCST_MODE_MERGE_THRESH`
| :term:`OBS_MODE_MERGE_THRESH`
| :term:`MODE_MERGE_FLAG`
| :term:`FCST_MODE_MERGE_FLAG`
| :term:`OBS_MODE_MERGE_FLAG`
| :term:`MODE_MERGE_CONFIG_FILE`
| :term:`FCST_MODE_WINDOW_BEGIN`
| :term:`FCST_MODE_WINDOW_END`
| :term:`OBS_MODE_WINDOW_BEGIN`
| :term:`OBS_MODE_WINDOW_END`
| :term:`FCST_MODE_FILE_WINDOW_BEGIN`
| :term:`FCST_MODE_FILE_WINDOW_END`
| :term:`OBS_MODE_FILE_WINDOW_BEGIN`
| :term:`OBS_MODE_FILE_WINDOW_END`
| :term:`MODE_CUSTOM_LOOP_LIST`
| :term:`MODE_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_MODE_VAR<n>_NAME` (optional)
| :term:`FCST_MODE_VAR<n>_LEVELS` (optional)
| :term:`FCST_MODE_VAR<n>_THRESH` (optional)
| :term:`FCST_MODE_VAR<n>_OPTIONS` (optional)
| :term:`OBS_MODE_VAR<n>_NAME` (optional)
| :term:`OBS_MODE_VAR<n>_LEVELS` (optional)
| :term:`OBS_MODE_VAR<n>_THRESH` (optional)
| :term:`OBS_MODE_VAR<n>_OPTIONS` (optional)


.. warning:: **DEPRECATED:**

   | :term:`MODE_OUT_DIR`
   | :term:`MODE_CONFIG`

MTD
---

.. _description-10:

Description
~~~~~~~~~~~

Used to configure the MET MODE Time Domain tool mtd.  This tools follows objects through time and can also be used to track objects.

.. _configuration-10:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_MTD_INPUT_DIR`
| :term:`OBS_MTD_INPUT_DIR`
| :term:`MTD_OUTPUT_DIR`

[filename_templates]

| :term:`FCST_MTD_INPUT_TEMPLATE`
| :term:`OBS_MTD_INPUT_TEMPLATE`
| :term:`MTD_OUTPUT_TEMPLATE`

[config]

| :term:`MTD_CONFIG_FILE`
| :term:`MTD_MIN_VOLUME`
| :term:`MTD_SINGLE_RUN`
| :term:`MTD_SINGLE_DATA_SRC`
| :term:`FCST_MTD_INPUT_DATATYPE`
| :term:`OBS_MTD_INPUT_DATATYPE`
| :term:`FCST_MTD_CONV_RADIUS`
| :term:`FCST_MTD_CONV_THRESH`
| :term:`OBS_MTD_CONV_RADIUS`
| :term:`OBS_MTD_CONV_THRESH`
| :term:`MTD_CUSTOM_LOOP_LIST`
| :term:`MTD_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_MTD_VAR<n>_NAME` (optional)
| :term:`FCST_MTD_VAR<n>_LEVELS` (optional)
| :term:`FCST_MTD_VAR<n>_THRESH` (optional)
| :term:`FCST_MTD_VAR<n>_OPTIONS` (optional)
| :term:`OBS_MTD_VAR<n>_NAME` (optional)
| :term:`OBS_MTD_VAR<n>_LEVELS` (optional)
| :term:`OBS_MTD_VAR<n>_THRESH` (optional)
| :term:`OBS_MTD_VAR<n>_OPTIONS` (optional)

.. warning:: **DEPRECATED:**

   | :term:`MTD_OUT_DIR`
   | :term:`MTD_CONFIG`
   | :term:`MTD_SINGLE_RUN_SRC`

PB2NC
-----

.. _description-11:

Description
~~~~~~~~~~~

The PB2NC wrapper is a Python script that encapsulates the behavior of
the MET pb2nc tool to convert prepBUFR files into netCDF.

.. _configuration-11:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`PB2NC_INPUT_DIR`
| :term:`PB2NC_OUTPUT_DIR`

[filename_templates]

| :term:`PB2NC_INPUT_TEMPLATE`
| :term:`PB2NC_OUTPUT_TEMPLATE`

[config]

| :term:`PB2NC_SKIP_IF_OUTPUT_EXISTS`
| :term:`PB2NC_OFFSETS`
| :term:`PB2NC_INPUT_DATATYPE`
| :term:`PB2NC_CONFIG_FILE`
| :term:`PB2NC_MESSAGE_TYPE` (optional)
| :term:`PB2NC_STATION_ID` (optional)
| :term:`PB2NC_GRID` (optional)
| :term:`PB2NC_POLY`
| :term:`PB2NC_OBS_BUFR_VAR_LIST` (optional)
| :term:`PB2NC_TIME_SUMMARY_FLAG`
| :term:`PB2NC_TIME_SUMMARY_BEG`
| :term:`PB2NC_TIME_SUMMARY_END`
| :term:`PB2NC_TIME_SUMMARY_VAR_NAMES`
| :term:`PB2NC_TIME_SUMMARY_TYPES`
| :term:`PB2NC_WINDOW_BEGIN`
| :term:`PB2NC_WINDOW_END`
| :term:`PB2NC_VALID_BEGIN`
| :term:`PB2NC_VALID_END`
| :term:`PB2NC_CUSTOM_LOOP_LIST`

.. warning:: **DEPRECATED:**

   | :term:`PREPBUFR_DATA_DIR`
   | :term:`PREPBUFR_MODEL_DIR_NAME`
   | :term:`PREPBUFR_DIR_REGEX`
   | :term:`PREPBUFR_FILE_REGEX`
   | :term:`NC_FILE_TMPL`
   | :term:`PB2NC_VERTICAL_LEVEL`
   | :term:`OBS_BUFR_VAR_LIST`
   | :term:`TIME_SUMMARY_FLAG`
   | :term:`TIME_SUMMARY_BEG`
   | :term:`TIME_SUMMARY_END`
   | :term:`TIME_SUMMARY_VAR_NAMES`
   | :term:`TIME_SUMMARY_TYPES`
   | :term:`OVERWRITE_NC_OUTPUT`
   | :term:`VERTICAL_LOCATION`

PCPCombine
----------

.. _description-12:

Description
~~~~~~~~~~~

The PCPCombine wrapper is a Python script that encapsulates the MET
PCPCombine tool. It provides the infrastructure to combine or extract
from files to build desired accumulations.

.. _configuration-12:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_PCP_COMBINE_INPUT_DIR`
| :term:`FCST_PCP_COMBINE_OUTPUT_DIR`
| :term:`OBS_PCP_COMBINE_INPUT_DIR`
| :term:`OBS_PCP_COMBINE_OUTPUT_DIR`

[filename_templates]

| :term:`FCST_PCP_COMBINE_INPUT_TEMPLATE`
| :term:`FCST_PCP_COMBINE_OUTPUT_TEMPLATE`
| :term:`OBS_PCP_COMBINE_INPUT_TEMPLATE`
| :term:`OBS_PCP_COMBINE_OUTPUT_TEMPLATE`

[config]

| :term:`LOG_PCP_COMBINE_VERBOSITY`
| :term:`FCST_IS_PROB`
| :term:`OBS_IS_PROB`
| :term:`FCST_PCP_COMBINE_INPUT_ACCUMS`
| :term:`FCST_PCP_COMBINE_INPUT_NAMES`
| :term:`FCST_PCP_COMBINE_INPUT_LEVELS`
| :term:`FCST_PCP_COMBINE_INPUT_OPTIONS`
| :term:`OBS_PCP_COMBINE_INPUT_ACCUMS`
| :term:`OBS_PCP_COMBINE_INPUT_NAMES`
| :term:`OBS_PCP_COMBINE_INPUT_LEVELS`
| :term:`OBS_PCP_COMBINE_INPUT_OPTIONS`
| :term:`FCST_PCP_COMBINE_INPUT_DATATYPE`
| :term:`OBS_PCP_COMBINE_INPUT_DATATYPE`
| :term:`FCST_PCP_COMBINE_RUN`
| :term:`OBS_PCP_COMBINE_RUN`
| :term:`FCST_PCP_COMBINE_METHOD`
| :term:`OBS_PCP_COMBINE_METHOD`
| :term:`FCST_PCP_COMBINE_MIN_FORECAST`
| :term:`OBS_PCP_COMBINE_MIN_FORECAST`
| :term:`FCST_PCP_COMBINE_MAX_FORECAST`
| :term:`OBS_PCP_COMBINE_MAX_FORECAST`
| :term:`FCST_PCP_COMBINE_BUCKET_INTERVAL`
| :term:`OBS_PCP_COMBINE_BUCKET_INTERVAL`
| :term:`FCST_PCP_COMBINE_CONSTANT_INIT`
| :term:`OBS_PCP_COMBINE_CONSTANT_INIT`
| :term:`FCST_PCP_COMBINE_STAT_LIST`
| :term:`OBS_PCP_COMBINE_STAT_LIST`
| :term:`FCST_PCP_COMBINE_DERIVE_LOOKBACK`
| :term:`OBS_PCP_COMBINE_DERIVE_LOOKBACK`
| :term:`PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_PCP_COMBINE_DATA_INTERVAL`
| :term:`OBS_PCP_COMBINE_DATA_INTERVAL`
| :term:`FCST_PCP_COMBINE_TIMES_PER_FILE`
| :term:`OBS_PCP_COMBINE_TIMES_PER_FILE`
| :term:`FCST_PCP_COMBINE_IS_DAILY_FILE`
| :term:`OBS_PCP_COMBINE_IS_DAILY_FILE`
| :term:`FCST_PCP_COMBINE_COMMAND`
| :term:`OBS_PCP_COMBINE_COMMAND`
| :term:`PCP_COMBINE_CUSTOM_LOOP_LIST`
| :term:`FCST_PCP_COMBINE_OUTPUT_ACCUM` (optional)
| :term:`FCST_PCP_COMBINE_OUTPUT_NAME` (optional)
| :term:`OBS_PCP_COMBINE_OUTPUT_ACCUM` (optional)
| :term:`OBS_PCP_COMBINE_OUTPUT_NAME` (optional)

.. warning:: **DEPRECATED:**

   | :term:`PCP_COMBINE_METHOD`
   | :term:`FCST_MIN_FORECAST`
   | :term:`FCST_MAX_FORECAST`
   | :term:`OBS_MIN_FORECAST`
   | :term:`OBS_MAX_FORECAST`
   | :term:`FCST_DATA_INTERVAL`
   | :term:`OBS_DATA_INTERVAL`
   | :term:`FCST_IS_DAILY_FILE`
   | :term:`OBS_IS_DAILY_FILE`
   | :term:`FCST_TIMES_PER_FILE`
   | :term:`OBS_TIMES_PER_FILE`
   | :term:`FCST_LEVEL`
   | :term:`OBS_LEVEL`
   | :term:`FCST_PCP_COMBINE_INPUT_LEVEL`
   | :term:`OBS_PCP_COMBINE_INPUT_LEVEL`
   | :term:`FCST_PCP_COMBINE_<n>_FIELD_NAME`
   | :term:`OBS_PCP_COMBINE_<n>_FIELD_NAME`

PlotDataPlane
-------------

Description
~~~~~~~~~~~

The PlotDataPlane wrapper is a Python script that encapsulates the MET
plot_data_plane tool. It provides the infrastructure to read in any input that
MET can read and plot them. This tool is often used to verify that the data
is mapped to the correct grid location.

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`PLOT_DATA_PLANE_INPUT_DIR`
| :term:`PLOT_DATA_PLANE_OUTPUT_DIR`

[filename_templates]

| :term:`PLOT_DATA_PLANE_INPUT_TEMPLATE`
| :term:`PLOT_DATA_PLANE_OUTPUT_TEMPLATE`

[config]

| :term:`PLOT_DATA_PLANE_FIELD_NAME`
| :term:`PLOT_DATA_PLANE_FIELD_LEVEL`
| :term:`PLOT_DATA_PLANE_FIELD_EXTRA`
| :term:`LOG_PLOT_DATA_PLANE_VERBOSITY`
| :term:`PLOT_DATA_PLANE_TITLE`
| :term:`PLOT_DATA_PLANE_COLOR_TABLE`
| :term:`PLOT_DATA_PLANE_RANGE_MIN_MAX`
| :term:`PLOT_DATA_PLANE_CONVERT_TO_IMAGE`
| :term:`PLOT_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS`

Point2Grid
----------

.. _description-13:

Description
~~~~~~~~~~~

The Point2Grid wrapper is a Python script that encapsulates the MET
point2grid tool. It provides the infrastructure to read in point observations
and place them on a grid

.. _configuration-13:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`POINT2GRID_INPUT_DIR`
| :term:`POINT2GRID_OUTPUT_DIR`

[filename_templates]

| :term:`POINT2GRID_INPUT_TEMPLATE`
| :term:`POINT2GRID_OUTPUT_TEMPLATE`

[config]

| :term:`POINT2GRID_WINDOW_BEGIN`
| :term:`POINT2GRID_WINDOW_END`
| :term:`POINT2GRID_REGRID_TO_GRID`
| :term:`POINT2GRID_INPUT_FIELD`
| :term:`POINT2GRID_INPUT_LEVEL`
| :term:`POINT2GRID_QC_FLAGS`
| :term:`POINT2GRID_ADP`
| :term:`POINT2GRID_REGRID_METHOD`
| :term:`POINT2GRID_GAUSSIAN_DX`
| :term:`POINT2GRID_GAUSSIAN_RADIUS`
| :term:`POINT2GRID_PROB_CAT_THRESH`
| :term:`POINT2GRID_VLD_THRESH`
| :term:`POINT2GRID_CUSTOM_LOOP_LIST`
| :term:`POINT2GRID_SKIP_IF_OUTPUT_EXISTS`

PointStat
---------

.. _description-14:

Description
~~~~~~~~~~~

The PointStat wrapper is a Python script that encapsulates the MET
point_stat tool. It provides the infrastructure to read in gridded model
data and netCDF point observation data to perform grid-to-point
(grid-to-obs) verification.

.. _configuration-14:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_POINT_STAT_INPUT_DIR`
| :term:`OBS_POINT_STAT_INPUT_DIR`
| :term:`POINT_STAT_OUTPUT_DIR`
| :term:`POINT_STAT_CLIMO_MEAN_INPUT_DIR`
| :term:`POINT_STAT_CLIMO_STDEV_INPUT_DIR`

[filename_templates]

| :term:`FCST_POINT_STAT_INPUT_TEMPLATE`
| :term:`OBS_POINT_STAT_INPUT_TEMPLATE`
| :term:`POINT_STAT_VERIFICATION_MASK_TEMPLATE` (optional)
| :term:`POINT_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
| :term:`POINT_STAT_CLIMO_STDEV_INPUT_TEMPLATE`

[config]

| :term:`POINT_STAT_OUTPUT_PREFIX`
| :term:`LOG_POINT_STAT_VERBOSITY`
| :term:`POINT_STAT_OFFSETS`
| :term:`FCST_POINT_STAT_INPUT_DATATYPE`
| :term:`OBS_POINT_STAT_INPUT_DATATYPE`
| :term:`POINT_STAT_CONFIG_FILE`
| :term:`MODEL`
| :term:`POINT_STAT_REGRID_TO_GRID`
| :term:`POINT_STAT_GRID`
| :term:`POINT_STAT_POLY`
| :term:`POINT_STAT_STATION_ID`
| :term:`POINT_STAT_MESSAGE_TYPE`
| :term:`POINT_STAT_CUSTOM_LOOP_LIST`
| :term:`POINT_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_POINT_STAT_WINDOW_BEGIN` (optional)
| :term:`FCST_POINT_STAT_WINDOW_END` (optional)
| :term:`OBS_POINT_STAT_WINDOW_BEGIN` (optional)
| :term:`OBS_POINT_STAT_WINDOW_END` (optional)
| :term:`POINT_STAT_NEIGHBORHOOD_WIDTH` (optional)
| :term:`POINT_STAT_NEIGHBORHOOD_SHAPE` (optional)
| :term:`FCST_POINT_STAT_VAR<n>_NAME` (optional)
| :term:`FCST_POINT_STAT_VAR<n>_LEVELS` (optional)
| :term:`FCST_POINT_STAT_VAR<n>_THRESH` (optional)
| :term:`FCST_POINT_STAT_VAR<n>_OPTIONS` (optional)
| :term:`OBS_POINT_STAT_VAR<n>_NAME` (optional)
| :term:`OBS_POINT_STAT_VAR<n>_LEVELS` (optional)
| :term:`OBS_POINT_STAT_VAR<n>_THRESH` (optional)
| :term:`OBS_POINT_STAT_VAR<n>_OPTIONS` (optional)
| :term:`POINT_STAT_OBS_VALID_BEG` (optional)
| :term:`POINT_STAT_OBS_VALID_END` (optional)

.. warning:: **DEPRECATED:**

   | :term:`FCST_INPUT_DIR`
   | :term:`OBS_INPUT_DIR`
   | :term:`START_HOUR`
   | :term:`END_HOUR`
   | :term:`BEG_TIME`
   | :term:`FCST_HR_START`
   | :term:`FCST_HR_END`
   | :term:`FCST_HR_INTERVAL`
   | :term:`OBS_INPUT_DIR_REGEX`
   | :term:`FCST_INPUT_DIR_REGEX`
   | :term:`FCST_INPUT_FILE_REGEX`
   | :term:`OBS_INPUT_FILE_REGEX`
   | :term:`OBS_INPUT_FILE_TMPL`
   | :term:`FCST_INPUT_FILE_TMPL`
   | :term:`REGRID_TO_GRID`
   | :term:`CLIMO_POINT_STAT_INPUT_DIR`
   | :term:`CLIMO_POINT_STAT_INPUT_TEMPLATE`


PyEmbedIngest
-------------

.. _description-15:

Description
~~~~~~~~~~~

Used to configure the PyEmbedIngest wrapper that runs RegridDataPlane to convert data using python embedding scripts into NetCDF so it can be read by the MET tools.

.. _configuration-15:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`

[filename_templates]

| :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`

[config]

| :term:`PY_EMBED_INGEST_<n>_SCRIPT`
| :term:`PY_EMBED_INGEST_<n>_TYPE`
| :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`
| :term:`PY_EMBED_INGEST_CUSTOM_LOOP_LIST`
| :term:`PY_EMBED_INGEST_<n>_OUTPUT_FIELD_NAME`
| :term:`PY_EMBED_INGEST_SKIP_IF_OUTPUT_EXISTS`

.. warning:: **DEPRECATED:**

    | :term:`CUSTOM_INGEST_<n>_OUTPUT_DIR`
    | :term:`CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE`
    | :term:`CUSTOM_INGEST_<n>_SCRIPT`
    | :term:`CUSTOM_INGEST_<n>_TYPE`
    | :term:`CUSTOM_INGEST_<n>_OUTPUT_GRID`


RegridDataPlane
---------------

.. _description-16:

Description
~~~~~~~~~~~

Used to configure the MET tool regrid_data_plane which can be used to change projections of a grid with user configurable interpolation choices.  It can also be used to convert GRIB1 and GRIB2 files into netcdf files if desired.

.. _configuration-16:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_REGRID_DATA_PLANE_INPUT_DIR`
| :term:`OBS_REGRID_DATA_PLANE_INPUT_DIR`

[filename_templates]

| :term:`FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE`
| :term:`FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`
| :term:`FCST_REGRID_DATA_PLANE_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_TEMPLATE`

[config]

| :term:`FCST_REGRID_DATA_PLANE_RUN`
| :term:`OBS_REGRID_DATA_PLANE_RUN`
| :term:`REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS`
| :term:`REGRID_DATA_PLANE_VERIF_GRID`
| :term:`FCST_REGRID_DATA_PLANE_INPUT_DATATYPE`
| :term:`OBS_REGRID_DATA_PLANE_INPUT_DATATYPE`
| :term:`REGRID_DATA_PLANE_GAUSSIAN_DX`
| :term:`REGRID_DATA_PLANE_GAUSSIAN_RADIUS`
| :term:`REGRID_DATA_PLANE_WIDTH`
| :term:`REGRID_DATA_PLANE_METHOD`
| :term:`REGRID_DATA_PLANE_CUSTOM_LOOP_LIST`
| :term:`REGRID_DATA_PLANE_ONCE_PER_FIELD`
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME` (optional)
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL` (optional)
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME` (optional)

.. warning:: **DEPRECATED:**

   | :term:`VERIFICATION_GRID`

SeriesAnalysis
----------------

.. _description-17:

Description
~~~~~~~~~~~

The SeriesAnalysis wrapper is used to find files and build a command that calls the MET tool SeriesAnalysis.

.. _configuration-17:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`FCST_SERIES_ANALYSIS_INPUT_DIR`
| :term:`OBS_SERIES_ANALYSIS_INPUT_DIR`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_INPUT_DIR`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_INPUT_DIR`
| :term:`SERIES_ANALYSIS_OUTPUT_DIR`

[filename_templates]

| :term:`FCST_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`OBS_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_OUTPUT_TEMPLATE`

[config]

| :term:`LOG_SERIES_ANALYSIS_VERBOSITY`
| :term:`SERIES_ANALYSIS_IS_PAIRED`
| :term:`SERIES_ANALYSIS_CONFIG_FILE`
| :term:`SERIES_ANALYSIS_REGRID_TO_GRID`
| :term:`SERIES_ANALYSIS_STAT_LIST`
| :term:`SERIES_ANALYSIS_CUSTOM_LOOP_LIST`
| :term:`SERIES_ANALYSIS_SKIP_IF_OUTPUT_EXISTS`

SeriesByInit
------------

.. _description-18:

Description
~~~~~~~~~~~

The SeriesByInit wrapper provides the infrastructure needed to demonstrates the use  of the series analysis tool using tropical cyclone data, based on initialization times. The SeriesByInit_wrapper creates numerous plots that represent the
field, level, and statistic for each initialization time.

.. _configuration-18:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`SERIES_ANALYSIS_TILE_INPUT_DIR`
| :term:`SERIES_ANALYSIS_FILTERED_OUTPUT_DIR`
| :term:`SERIES_ANALYSIS_OUTPUT_DIR`
| :term:`SERIES_ANALYSIS_STAT_INPUT_DIR`

[config]

| :term:`SERIES_ANALYSIS_CONFIG_FILE`
| :term:`SERIES_ANALYSIS_REGRID_TO_GRID`
| :term:`SERIES_ANALYSIS_STAT_LIST`
| :term:`INIT_HOUR_END`
| :term:`INIT_INCLUDE`
| :term:`INIT_EXCLUDE`
| :term:`SERIES_ANALYSIS_BACKGROUND_MAP`
| :term:`SERIES_ANALYSIS_GENERATE_PLOTS`

[filename_templates]

| :term:`SERIES_ANALYSIS_STAT_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_OUTPUT_TEMPLATE`

.. warning:: **DEPRECATED:**

   | :term:`SERIES_INIT_FILTERED_OUT_DIR`
   | :term:`SERIES_BY_INIT_OUTPUT_DIR`
   | :term:`FCST_TILE_PREFIX`
   | :term:`ANLY_TILE_PREFIX`
   | :term:`FCST_TILE_REGEX`
   | :term:`ANLY_TILE_REGEX`
   | :term:`FCST_NC_TILE_REGEX`
   | :term:`ANLY_NC_TILE_REGEX`
   | :term:`FCST_ASCII_REGEX_LEAD`
   | :term:`ANLY_ASCII_REGEX_LEAD`
   | :term:`SERIES_ANALYSIS_FILTER_OPTS`
   | :term:`SERIES_ANALYSIS_INPUT_DIR`
   | :term:`FCST_SERIES_ANALYSIS_NC_TILE_REGEX`
   | :term:`OBS_SERIES_ANALYSIS_NC_TILE_REGEX`
   | :term:`FCST_SERIES_ANALYSIS_ASCII_REGEX_LEAD`
   | :term:`OBS_SERIES_ANALYSIS_ASCII_REGEX_LEAD`

SeriesByLead
------------

.. _description-19:

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

.. _configuration-19:

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

| :term:`SERIES_ANALYSIS_INPUT_DIR`
| :term:`SERIES_ANALYSIS_FILTERED_OUTPUT`
| :term:`SERIES_ANALYSIS_OUTPUT_DIR`

[regex_patterns]

| :term:`FCST_SERIES_ANALYSIS_NC_TILE_REGEX`
| :term:`OBS_SERIES_ANALYSIS_NC_TILE_REGEX`
| :term:`FCST_SERIES_ANALYSIS_ASCII_REGEX_LEAD`
| :term:`OBS_SERIES_ANALYSIS_ASCII_REGEX_LEAD`

[config]

| :term:`SERIES_ANALYSIS_REGRID_TO_GRID`
| :term:`SERIES_ANALYSIS_STAT_LIST`
| :term:`SERIES_ANALYSIS_BACKGROUND_MAP`
| :term:`SERIES_ANALYSIS_GROUP_FCSTS`
| :term:`LEAD_SEQ_<n>_LABEL`
| :term:`LEAD_SEQ_\<n\>`
| :term:`SERIES_ANALYSIS_FILTER_OPTS`
| :term:`SERIES_ANALYSIS_STAT_LIST`

.. warning:: **DEPRECATED:**

   | :term:`SERIES_LEAD_FILTERED_OUT_DIR`
   | :term:`SERIES_BY_LEAD_FILTERED_OUTPUT`
   | :term:`SERIES_BY_LEAD_OUTPUT_DIR`
   | :term:`SERIES_BY_LEAD_GROUP_FCSTS`
   | :term:`VAR_LIST`
   | :term:`STAT_LIST`

StatAnalysis
------------

.. _description-20:

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

.. _configuration-20:

Configuration
~~~~~~~~~~~~~

The following values must be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

[dir]

| :term:`STAT_ANALYSIS_OUTPUT_DIR`

[filename_templates]

| :term:`MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE`
| :term:`MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE`

[config]

| :term:`LOG_STAT_ANALYSIS_VERBOSITY`
| :term:`MODEL\<n\>`
| :term:`MODEL<n>_OBTYPE`
| :term:`MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR`
| :term:`MODEL_LIST`
| :term:`GROUP_LIST_ITEMS`
| :term:`LOOP_LIST_ITEMS`
| :term:`STAT_ANALYSIS_CONFIG_FILE`
| :term:`STAT_ANALYSIS_JOB_NAME`
| :term:`STAT_ANALYSIS_JOB_ARGS`

The following values are **optional** in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

[config]

| :term:`DESC_LIST`
| :term:`FCST_VALID_HOUR_LIST`
| :term:`OBS_VALID_HOUR_LIST`
| :term:`FCST_INIT_HOUR_LIST`
| :term:`OBS_INIT_HOUR_LIST`
| :term:`FCST_VAR_LIST`
| :term:`OBS_VAR_LIST`
| :term:`FCST_LEVEL_LIST`
| :term:`OBS_LEVEL_LIST`
| :term:`FCST_UNITS_LIST`
| :term:`OBS_UNITS_LIST`
| :term:`FCST_THRESH_LIST`
| :term:`OBS_THRESH_LIST`
| :term:`FCST_LEAD_LIST`
| :term:`OBS_LEAD_LIST`
| :term:`VX_MASK_LIST`
| :term:`INTERP_MTHD_LIST`
| :term:`INTERP_PNTS_LIST`
| :term:`ALPHA_LIST`
| :term:`COV_THRESH_LIST`
| :term:`LINE_TYPE_LIST`
| :term:`STAT_ANALYSIS_SKIP_IF_OUTPUT_EXISTS`

The following values **must** be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = processes:

[dir]

| :term:`STAT_ANALYSIS_OUTPUT_DIR`

[config]

| :term:`LOG_STAT_ANALYSIS_VERBOSITY`
| :term:`DATE_TYPE`
| :term:`STAT_ANALYSIS_CONFIG_FILE`
| :term:`MODEL\<n\>`
| :term:`MODEL<n>_OBTYPE`
| :term:`MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR`
| :term:`MODEL<n>_REFERENCE_NAME`
| :term:`GROUP_LIST_ITEMS`
| :term:`LOOP_LIST_ITEMS`
| :term:`MODEL_LIST`
| :term:`VX_MASK_LIST`
| :term:`FCST_LEAD_LIST`
| :term:`LINE_TYPE_LIST`

The following values are optional in the METplus Wrappers configuration
file for running with LOOP_ORDER = processes:

| :term:`VAR<n>_FOURIER_DECOMP`
| :term:`VAR<n>_WAVE_NUM_LIST`
| :term:`FCST_VALID_HOUR_LIST`
| :term:`OBS_VALID_HOUR_LIST`
| :term:`FCST_INIT_HOUR_LIST`
| :term:`OBS_INIT_HOUR_LIST`
| :term:`OBS_LEAD_LIST`
| :term:`DESC_LIST`
| :term:`INTERP_MTHD_LIST`
| :term:`INTERP_PNTS_LIST`
| :term:`COV_THRESH_LIST`
| :term:`ALPHA_LIST`

.. warning:: **DEPRECATED:**

   | :term:`STAT_ANALYSIS_LOOKIN_DIR`
   | :term:`STAT_ANALYSIS_OUT_DIR`
   | :term:`STAT_ANALYSIS_CONFIG`
   | :term:`VALID_HOUR_METHOD`
   | :term:`VALID_HOUR_BEG`
   | :term:`VALID_HOUR_END`
   | :term:`VALID_HOUR_INCREMENT`
   | :term:`INIT_HOUR_BEG`
   | :term:`INIT_HOUR_END`
   | :term:`INIT_HOUR_INCREMENT`
   | :term:`MODEL`
   | :term:`OBTYPE`
   | :term:`JOB_NAME`
   | :term:`JOB_ARGS`
   | :term:`DESC`
   | :term:`FCST_LEAD`
   | :term:`FCST_VAR_NAME`
   | :term:`FCST_VAR_LEVEL`
   | :term:`OBS_VAR_NAME`
   | :term:`OBS_VAR_LEVEL`
   | :term:`REGION`
   | :term:`INTERP`
   | :term:`INTERP_PTS`
   | :term:`FCST_THRESH`
   | :term:`COV_THRESH`
   | :term:`LINE_TYPE`
   | :term:`STAT_ANALYSIS_DUMP_ROW_TMPL`
   | :term:`STAT_ANALYSIS_OUT_STAT_TMPL`
   | :term:`PLOT_TIME`
   | :term:`VERIF_CASE`
   | :term:`VERIF_TYPE`
   | :term:`MODEL<n>_NAME`
   | :term:`MODEL<n>_OBS_NAME`
   | :term:`MODEL<n>_NAME_ON_PLOT`
   | :term:`MODEL<n>_STAT_DIR`
   | :term:`REGION_LIST`
   | :term:`LEAD_LIST`

TCGen
-------

Description
~~~~~~~~~~~

The TCGen wrapper encapsulates the behavior of the MET tc_gen tool.
The wrapper accepts track (Adeck or Bdeck) data and Genesis data.

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`TC_GEN_TRACK_INPUT_DIR`
| :term:`TC_GEN_GENESIS_INPUT_DIR`
| :term:`TC_GEN_OUTPUT_DIR`

[filename_templates]

| :term:`TC_GEN_TRACK_INPUT_TEMPLATE`
| :term:`TC_GEN_GENESIS_INPUT_TEMPLATE`
| :term:`TC_GEN_OUTPUT_TEMPLATE`

[config]

| :term:`LOG_TC_GEN_VERBOSITY`
| :term:`TC_GEN_CUSTOM_LOOP_LIST`
| :term:`TC_GEN_CONFIG_FILE`
| :term:`TC_GEN_INIT_FREQUENCY`
| :term:`TC_GEN_LEAD_WINDOW_BEGIN`
| :term:`TC_GEN_LEAD_WINDOW_END`
| :term:`TC_GEN_MIN_DURATION`

| :term:`TC_GEN_FCST_GENESIS_VMAX_THRESH`
| :term:`TC_GEN_FCST_GENESIS_MSLP_THRESH`
| :term:`TC_GEN_BEST_GENESIS_TECHNIQUE`
| :term:`TC_GEN_BEST_GENESIS_CATEGORY`
| :term:`TC_GEN_BEST_GENESIS_VMAX_THRESH`
| :term:`TC_GEN_BEST_GENESIS_MSLP_THRESH`
| :term:`TC_GEN_OPER_GENESIS_TECHNIQUE`
| :term:`TC_GEN_OPER_GENESIS_CATEGORY`
| :term:`TC_GEN_OPER_GENESIS_VMAX_THRESH`
| :term:`TC_GEN_OPER_GENESIS_MSLP_THRESH`
| :term:`TC_GEN_FILTER_\<n\>`
| :term:`MODEL`
| :term:`TC_GEN_STORM_ID`
| :term:`TC_GEN_STORM_NAME`
| :term:`TC_GEN_INIT_BEG`
| :term:`TC_GEN_INIT_END`
| :term:`TC_GEN_VALID_BEG`
| :term:`TC_GEN_VALID_END`
| :term:`TC_GEN_INIT_HOUR_LIST`
| :term:`TC_GEN_VX_MASK`
| :term:`TC_GEN_GENESIS_WINDOW_BEGIN`
| :term:`TC_GEN_GENESIS_WINDOW_END`
| :term:`TC_GEN_GENESIS_RADIUS`
| :term:`TC_GEN_DLAND_FILE`
| :term:`TC_GEN_SKIP_IF_OUTPUT_EXISTS`

TCMPRPlotter
-------------

.. _description-21:

Description
~~~~~~~~~~~

The TCMPRPlotter wrapper is a Python script that wraps the R script
plot_tcmpr.R. This script is useful for plotting the calculated
statistics for the output from the MET-TC tools. This script, and other
R scripts are included in the MET installation. Please refer to section
21.2.3 of the MET User's Guide for usage information.

.. _configuration-21:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`TCMPR_PLOTTER_TCMPR_DATA_DIR`
| :term:`TCMPR_PLOTTER_PLOT_OUTPUT_DIR`

[config]

| :term:`TCMPR_PLOTTER_CONFIG_FILE`
| :term:`TCMPR_PLOTTER_PREFIX`
| :term:`TCMPR_PLOTTER_TITLE`
| :term:`TCMPR_PLOTTER_SUBTITLE`
| :term:`TCMPR_PLOTTER_XLAB`
| :term:`TCMPR_PLOTTER_YLAB`
| :term:`TCMPR_PLOTTER_XLIM`
| :term:`TCMPR_PLOTTER_YLIM`
| :term:`TCMPR_PLOTTER_FILTER`
| :term:`TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE`
| :term:`TCMPR_PLOTTER_DEP_VARS`
| :term:`TCMPR_PLOTTER_SCATTER_X`
| :term:`TCMPR_PLOTTER_SCATTER_Y`
| :term:`TCMPR_PLOTTER_SKILL_REF`
| :term:`TCMPR_PLOTTER_SERIES`
| :term:`TCMPR_PLOTTER_SERIES_CI`
| :term:`TCMPR_PLOTTER_LEGEND`
| :term:`TCMPR_PLOTTER_LEAD`
| :term:`TCMPR_PLOTTER_PLOT_TYPES`
| :term:`TCMPR_PLOTTER_RP_DIFF`
| :term:`TCMPR_PLOTTER_DEMO_YR`
| :term:`TCMPR_PLOTTER_HFIP_BASELINE`
| :term:`TCMPR_PLOTTER_FOOTNOTE_FLAG`
| :term:`TCMPR_PLOTTER_PLOT_CONFIG_OPTS`
| :term:`TCMPR_PLOTTER_SAVE_DATA`

The following are TCMPR flags, if set to 'no', then don't set flag, if
set to 'yes', then set the flag

| :term:`TCMPR_PLOTTER_NO_EE`
| :term:`TCMPR_PLOTTER_NO_LOG`
| :term:`TCMPR_PLOTTER_SAVE`

.. warning:: **DEPRECATED:**

   | :term:`TCMPR_PLOT_OUT_DIR`
   | :term:`TITLE`
   | :term:`SUBTITLE`
   | :term:`XLAB`
   | :term:`YLAB`
   | :term:`XLIM`
   | :term:`YLIM`
   | :term:`FILTER`
   | :term:`FILTERED_TCST_DATA_FILE`
   | :term:`DEP_VARS`
   | :term:`SCATTER_X`
   | :term:`SCATTER_Y`
   | :term:`SKILL_REF`
   | :term:`SERIES`
   | :term:`SERIES_CI`
   | :term:`LEGEND`
   | :term:`LEAD`
   | :term:`PLOT_TYPES`
   | :term:`RP_DIFF`
   | :term:`DEMO_YR`
   | :term:`HFIP_BASELINE`
   | :term:`FOOTNOTE_FLAG`
   | :term:`PLOT_CONFIG_OPTS`
   | :term:`SAVE_DATA`

TCPairs
-------

.. _description-22:

Description
~~~~~~~~~~~

The TCPairs wrapper encapsulates the behavior of the MET tc_pairs tool.
The wrapper accepts Adeck and Bdeck (Best track) cyclone track data in
extra tropical cyclone format (such as the data used by sample data
provided in the METplus tutorial), or ATCF formatted track data. If data
is in an extra tropical cyclone (non-ATCF) format, the data is
reformatted into an ATCF format that is recognized by MET.

.. _configuration-22:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`TC_PAIRS_ADECK_INPUT_DIR`
| :term:`TC_PAIRS_BDECK_INPUT_DIR`
| :term:`TC_PAIRS_EDECK_INPUT_DIR`
| :term:`TC_PAIRS_OUTPUT_DIR`
| :term:`TC_PAIRS_REFORMAT_DIR`

[filename_templates]

| :term:`TC_PAIRS_ADECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_BDECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_EDECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_OUTPUT_TEMPLATE`

[config]

| :term:`TC_PAIRS_CONFIG_FILE`
| :term:`TC_PAIRS_INIT_INCLUDE`
| :term:`TC_PAIRS_INIT_EXCLUDE`
| :term:`TC_PAIRS_READ_ALL_FILES`
| :term:`TC_PAIRS_MODEL`
| :term:`TC_PAIRS_STORM_ID`
| :term:`TC_PAIRS_BASIN`
| :term:`TC_PAIRS_CYCLONE`
| :term:`TC_PAIRS_STORM_NAME`
| :term:`TC_PAIRS_DLAND_FILE`
| :term:`TC_PAIRS_MISSING_VAL_TO_REPLACE`
| :term:`TC_PAIRS_MISSING_VAL`
| :term:`TC_PAIRS_SKIP_IF_REFORMAT_EXISTS`
| :term:`TC_PAIRS_SKIP_IF_OUTPUT_EXISTS`
| :term:`TC_PAIRS_REFORMAT_DECK`
| :term:`TC_PAIRS_REFORMAT_TYPE`
| :term:`TC_PAIRS_CUSTOM_LOOP_LIST`

.. warning:: **DEPRECATED:**

   | :term:`ADECK_TRACK_DATA_DIR`
   | :term:`BDECK_TRACK_DATA_DIR`
   | :term:`TRACK_DATA_SUBDIR_MOD`
   | :term:`TC_PAIRS_DIR`
   | :term:`TOP_LEVEL_DIRS`
   | :term:`MODEL`
   | :term:`STORM_ID`
   | :term:`BASIN`
   | :term:`CYCLONE`
   | :term:`STORM_NAME`
   | :term:`DLAND_FILE`
   | :term:`TRACK_TYPE`
   | :term:`ADECK_FILE_PREFIX`
   | :term:`BDECK_FILE_PREFIX`
   | :term:`MISSING_VAL_TO_REPLACE`
   | :term:`MISSING_VAL`
   | :term:`INIT_INCLUDE`
   | :term:`INIT_EXCLUDE`
   | :term:`INIT_HOUR_END`

TCRMW
------

.. _tc_rmw_description:

Description
~~~~~~~~~~~

Used to configure the MET tool TC-RMW.

.. _tc_rmw_metplus_conf:

METplus Configuration
~~~~~~~~~~~~~~~~~~~~~

[dir]

| :term:`TC_RMW_INPUT_DIR`
| :term:`TC_RMW_DECK_INPUT_DIR`
| :term:`TC_RMW_OUTPUT_DIR`

[filename_templates]

| :term:`TC_RMW_DECK_TEMPLATE`
| :term:`TC_RMW_INPUT_TEMPLATE`
| :term:`TC_RMW_OUTPUT_TEMPLATE`

[config]

| :term:`LOG_TC_RMW_VERBOSITY`
| :term:`TC_RMW_CONFIG_FILE`
| :term:`TC_RMW_INPUT_DATATYPE`
| :term:`TC_RMW_REGRID_METHOD`
| :term:`TC_RMW_REGRID_WIDTH`
| :term:`TC_RMW_REGRID_VLD_THRESH`
| :term:`TC_RMW_REGRID_SHAPE`
| :term:`TC_RMW_N_RANGE`
| :term:`TC_RMW_N_AZIMUTH`
| :term:`TC_RMW_MAX_RANGE_KM`
| :term:`TC_RMW_DELTA_RANGE_KM`
| :term:`TC_RMW_SCALE`
| :term:`TC_RMW_STORM_ID`
| :term:`TC_RMW_BASIN`
| :term:`TC_RMW_CYCLONE`
| :term:`TC_RMW_STORM_NAME`
| :term:`TC_RMW_INIT_INCLUDE`
| :term:`TC_RMW_VALID_BEG`
| :term:`TC_RMW_VALID_END`
| :term:`TC_RMW_VALID_INCLUDE_LIST`
| :term:`TC_RMW_VALID_EXCLUDE_LIST`
| :term:`TC_RMW_VALID_HOUR_LIST`
| :term:`TC_RMW_SKIP_IF_OUTPUT_EXISTS`
| :term:`MODEL`
| :term:`LEAD_SEQ`

.. _tc-rmw-met-conf:

MET Configuration
~~~~~~~~~~~~~~~~~

This is the MET configuration file used for this wrapper. Below the file contents are descriptions of each environment variable referenced in this file and how the METplus configuration variables relate to them.

.. literalinclude:: ../../parm/met_config/TCRMWConfig_wrapped

The following environment variables are referenced in the MET configuration file. The values are generated based on values in the METplus configuration files.

**${MODEL}** - Corresponds to MODEL in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    MODEL = GFS

Resulting value::

    model = "GFS";

**${STORM_ID}** - Corresponds to TC_RMW_STORM_ID in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_STORM_ID = al062018

Resulting value::

    storm_id = "al062018";

**${BASIN}** - Corresponds to TC_RMW_BASIN in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_BASIN = AL

Resulting value::

    basin = "AL";

**${CYCLONE}** - Corresponds to TC_RMW_CYCLONE in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_CYCLONE = 06

Resulting value::

   cyclone = "06";

**${STORM_NAME}** - Corresponds to TC_RMW_STORM_NAME in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_STORM_NAME = al062018

Resulting value::

    storm_name = "al062018";

**${INIT_INCLUDE}** - Corresponds to TC_RMW_INIT_INCLUDE in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_INIT_INCLUDE = 20101231_06

Resulting value::

    init_inc = "20101231_06";

Resulting value::

    init_exc = "20101231_00";

**${VALID_BEG}** - Corresponds to TC_RMW_VALID_BEG in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_VALID_BEG = 20100101

Resulting value::

    valid_beg = "20100101";

**${VALID_END}** - Corresponds to TC_RMW_VALID_END in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_VALID_END = 20101231_12

Resulting value::

    valid_end = "20101231_12";

**${VALID_INCLUDE_LIST}** - Corresponds to TC_RMW_VALID_INCLUDE_LIST in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_VALID_INCLUDE_LIST = 20101231_06, 20101231_12

Resulting value::

    valid_inc = [ "20101231_06", "20101231_12" ];

**${VALID_EXCLUDE_LIST}** - Corresponds to TC_RMW_VALID_EXCLUDE_LIST in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_VALID_EXCLUDE_LIST = 20101231_00, 20101231_03

Resulting value::

    valid_exc = [ "20101231_00", "20101231_03" ];

**${VALID_HOUR_LIST}** - Corresponds to TC_RMW_VALID_HOUR_LIST in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_VALID_HOUR_LIST = 12, 15

Resulting value::

    valid_hour = [ "12", "15" ];

**${LEAD_LIST}** - Corresponds to LEAD_SEQ in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    LEAD_SEQ = 6, 12, 18, 24

Resulting value::

    lead = ["06", "12", "18", "24"];

**${DATA_FIELD}** - Formatted input field information. Generated from [FCST/BOTH]_VAR<n>_[NAME/LEVEL/THRESH/OPTIONS] in the METplus configuration file.

METplus Configuration::

    [config]
    BOTH_VAR1_NAME = PRMSL
    BOTH_VAR1_LEVELS = L0
    BOTH_VAR2_NAME = TMP
    BOTH_VAR2_LEVELS = P1000, P750

Resulting value::

    { name="PRMSL"; level="L0"; },{ name="TMP"; level="P1000"; },{ name="TMP"; level="P750"; }

**${DATA_FILE_TYPE}** - Type of input data set only if necessary to allow MET to read the data. Generated from TC_RMW_INPUT_DATATYPE in the METplus configuration file.

METplus Configuration::

    [config]
    TC_RMW_INPUT_DATATYPE = GRIB2

Resulting value::

    file_type = GRIB2;

**${N_RANGE}** - Corresponds to TC_RMW_N_RANGE in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_N_RANGE = 100

Resulting value::

    n_range = 100;

**${N_AZIMUTH}** - Corresponds to TC_RMW_N_AZIMUTH in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_N_AZIMUTH = 180

Resulting value::

    n_azimuth = 180;

**${MAX_RANGE_KM}** - Corresponds to TC_RMW_MAX_RANGE_KM in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_MAX_RANGE_KM = 1000.0

Resulting value::

    max_range_km = 1000.0;

**${DELTA_RANGE_KM}** - Corresponds to TC_RMW_DELTA_RANGE_KM in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_DELTA_RANGE_KM = 10.0

Resulting value::

    delta_range_km = 10.0;

**${RMW_SCALE}** - Corresponds to TC_RMW_SCALE in the METplus configuration file. If unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration::

    [config]
    TC_RMW_SCALE = 0.2

Resulting value::

    rmw_scale = 0.2;

**${REGRID_DICT}** - Corresponds to TC_RMW_REGRID_METHOD, TC_RMW_REGRID_WIDTH, TC_RMW_REGRID_VLD_THRESH, and TC_RMW_REGRID_SHAPE in the METplus configuration file. If any of these variables are unset in METplus, value set in the default MET TCRMW configuration file will be used.

METplus Configuration 1::

    [config]
    TC_RMW_REGRID_SHAPE = SQUARE

Resulting value 1::

    regrid = {shape = SQUARE;}

METplus Configuration 2::

    [config]
    TC_RMW_REGRID_WIDTH = 2
    TC_RMW_REGRID_SHAPE = SQUARE

Resulting value 2::

    regrid = {width = 2; shape = SQUARE;}


TCStat
------

.. _description-23:

Description
~~~~~~~~~~~

Used to configure the MET tool tc_stat. This wrapper can be run by
listing it in the PROCESS_LIST, or can be called from the ExtractTiles
wrapper (via the MET tc-stat command line commands).

.. _configuration-23:

Configuration
~~~~~~~~~~~~~

[dir]

| :term:`TC_STAT_LOOKIN_DIR`
| :term:`TC_STAT_OUTPUT_DIR`

[config]

| :term:`TC_STAT_CONFIG_FILE`
| :term:`TC_STAT_JOB_ARGS`
| :term:`TC_STAT_AMODEL`
| :term:`TC_STAT_BMODEL`
| :term:`TC_STAT_DESC`
| :term:`TC_STAT_STORM_ID`
| :term:`TC_STAT_BASIN`
| :term:`TC_STAT_CYCLONE`
| :term:`TC_STAT_STORM_NAME`
| :term:`TC_STAT_INIT_BEG`
| :term:`TC_STAT_INIT_INCLUDE`
| :term:`TC_STAT_INIT_EXCLUDE`
| :term:`TC_STAT_INIT_HOUR`
| :term:`TC_STAT_VALID_BEG`
| :term:`TC_STAT_VALID_END`
| :term:`TC_STAT_VALID_INCLUDE`
| :term:`TC_STAT_VALID_EXCLUDE`
| :term:`TC_STAT_VALID_HOUR`
| :term:`TC_STAT_LEAD_REQ`
| :term:`TC_STAT_INIT_MASK`
| :term:`TC_STAT_VALID_MASK`
| :term:`TC_STAT_VALID_HOUR`
| :term:`TC_STAT_LEAD`
| :term:`TC_STAT_TRACK_WATCH_WARN`
| :term:`TC_STAT_COLUMN_THRESH_NAME`
| :term:`TC_STAT_COLUMN_THRESH_VAL`
| :term:`TC_STAT_COLUMN_STR_NAME`
| :term:`TC_STAT_COLUMN_STR_VAL`
| :term:`TC_STAT_INIT_THRESH_NAME`
| :term:`TC_STAT_INIT_THRESH_VAL`
| :term:`TC_STAT_INIT_STR_NAME`
| :term:`TC_STAT_INIT_STR_VAL`
| :term:`TC_STAT_WATER_ONLY`
| :term:`TC_STAT_LANDFALL`
| :term:`TC_STAT_LANDFALL_BEG`
| :term:`TC_STAT_LANDFALL_END`
| :term:`TC_STAT_MATCH_POINTS`
| :term:`TC_STAT_SKIP_IF_OUTPUT_EXISTS`

.. warning:: **DEPRECATED:**

   | :term:`TC_STAT_INPUT_DIR`
   | :term:`TC_STAT_RUN_VIA`
   | :term:`TC_STAT_CMD_LINE_JOB`
   | :term:`TC_STAT_JOBS_LIST`
