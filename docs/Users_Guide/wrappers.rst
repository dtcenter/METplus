***************
Python Wrappers
***************

This chapter provides a description of each supported Python wrapper in
METplus Wrappers. A wrapper is generally a Python script that
encapsulates the behavior of a corresponding MET tool. Each of these
sections can be added to the PROCESS_LIST configuration list variable.
The METplus Configuration section of each wrapper section below lists the
METplus Wrappers configuration variables that are specific to that
wrapper organized by config file section. You can find more information
about each item in the METplus Configuration Glossary.
The MET Configuration section of each wrapper (if applicable) displays the
wrapped MET configuration file that utilizes environment variables to override
settings. These sections also contain a list of environment variables that
are referenced in the wrapped MET configuration files and a table to show
which METplus configuration variables are used to set them and which MET
configuration variables they override.

.. _ascii2nc_wrapper:

ASCII2NC
========

Description
-----------

Used to configure the MET tool ASCII2NC

METplus Configuration
---------------------

| :term:`ASCII2NC_INPUT_DIR`
| :term:`ASCII2NC_OUTPUT_DIR`
| :term:`ASCII2NC_INPUT_TEMPLATE`
| :term:`ASCII2NC_OUTPUT_TEMPLATE`
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
| :term:`ASCII2NC_MET_CONFIG_OVERRIDES`
|

.. _ascii2nc-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/Ascii2NcConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/Ascii2NcConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/Ascii2NcConfig_wrapped

**${METPLUS_TIME_SUMMARY_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ASCII2NC_TIME_SUMMARY_FLAG`
     - time_summary.flag
   * - :term:`ASCII2NC_TIME_SUMMARY_RAW_DATA`
     - time_summary.raw_data
   * - :term:`ASCII2NC_TIME_SUMMARY_BEG`
     - time_summary.beg
   * - :term:`ASCII2NC_TIME_SUMMARY_END`
     - time_summary.end
   * - :term:`ASCII2NC_TIME_SUMMARY_STEP`
     - time_summary.step
   * - :term:`ASCII2NC_TIME_SUMMARY_WIDTH`
     - time_summary.width
   * - :term:`ASCII2NC_TIME_SUMMARY_GRIB_CODES`
     - time_summary.grib_code
   * - :term:`ASCII2NC_TIME_SUMMARY_VAR_NAMES`
     - time_summary.obs_var
   * - :term:`ASCII2NC_TIME_SUMMARY_TYPES`
     - time_summary.type
   * - :term:`ASCII2NC_TIME_SUMMARY_VALID_FREQ`
     - time_summary.vld_freq
   * - :term:`ASCII2NC_TIME_SUMMARY_VALID_THRESH`
     - time_summary.vld_thresh

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ASCII2NC_MET_CONFIG_OVERRIDES`
     - n/a

.. _cyclone_plotter_wrapper:

CyclonePlotter
==============

Description
-----------

This wrapper does not have a corresponding MET tool but instead wraps
the logic necessary to create plots of cyclone tracks. Currently only
the output from the MET tc-pairs tool can be plotted. If used on an internet-limited system,
additional dependencies may apply. See :ref:`install` for details.

METplus Configuration
---------------------

| :term:`CYCLONE_PLOTTER_INPUT_DIR`
| :term:`CYCLONE_PLOTTER_OUTPUT_DIR`
| :term:`CYCLONE_PLOTTER_INIT_DATE`
| :term:`CYCLONE_PLOTTER_INIT_HR`
| :term:`CYCLONE_PLOTTER_MODEL`
| :term:`CYCLONE_PLOTTER_PLOT_TITLE`
| :term:`CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE`
| :term:`CYCLONE_PLOTTER_CROSS_MARKER_SIZE`
| :term:`CYCLONE_PLOTTER_GENERATE_TRACK_ASCII`
| :term:`CYCLONE_PLOTTER_ADD_WATERMARK`
| :term:`CYCLONE_PLOTTER_GLOBAL_PLOT`
| :term:`CYCLONE_PLOTTER_WEST_LON`
| :term:`CYCLONE_PLOTTER_EAST_LON`
| :term:`CYCLONE_PLOTTER_NORTH_LAT`
| :term:`CYCLONE_PLOTTER_SOUTH_LAT`
| :term:`CYCLONE_PLOTTER_ANNOTATION_FONT_SIZE`
| :term:`CYCLONE_PLOTTER_RESOLUTION_DPI`
|

.. warning:: **DEPRECATED:**

   | :term:`CYCLONE_OUT_DIR`
   | :term:`CYCLONE_INIT_DATE`
   | :term:`CYCLONE_INIT_HR`
   | :term:`CYCLONE_MODEL`
   | :term:`CYCLONE_PLOT_TITLE`
   | :term:`CYCLONE_CIRCLE_MARKER_SIZE`
   | :term:`CYCLONE_CROSS_MARKER_SIZE`
   | :term:`CYCLONE_GENERATE_TRACK_ASCII`
   |

.. _ensemble_stat_wrapper:

EnsembleStat
============

Description
-----------

Used to configure the MET tool ensemble_stat.

METplus Configuration
---------------------

| :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_DIR`
| :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_DIR`
| :term:`FCST_ENSEMBLE_STAT_INPUT_DIR`
| :term:`ENSEMBLE_STAT_OUTPUT_DIR`
| :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE`
| :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE`
| :term:`FCST_ENSEMBLE_STAT_INPUT_TEMPLATE`
| :term:`FCST_ENSEMBLE_STAT_INPUT_FILE_LIST`
| :term:`ENSEMBLE_STAT_OUTPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_CTRL_INPUT_DIR`
| :term:`ENSEMBLE_STAT_CTRL_INPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_ENS_MEAN_INPUT_TEMPLATE`
| :term:`ENSEMBLE_STAT_ENS_MEAN_INPUT_DIR`
| :term:`LOG_ENSEMBLE_STAT_VERBOSITY`
| :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE`
| :term:`ENSEMBLE_STAT_REGRID_TO_GRID`
| :term:`ENSEMBLE_STAT_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_REGRID_CONVERT`
| :term:`ENSEMBLE_STAT_REGRID_CENSOR_THRESH`
| :term:`ENSEMBLE_STAT_REGRID_CENSOR_VAL`
| :term:`ENSEMBLE_STAT_CONFIG_FILE`
| :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE`
| :term:`ENSEMBLE_STAT_N_MEMBERS`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_END`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_END`
| :term:`ENSEMBLE_STAT_ENS_THRESH`
| :term:`ENSEMBLE_STAT_VLD_THRESH`
| :term:`ENSEMBLE_STAT_OBS_THRESH`
| :term:`ENSEMBLE_STAT_CUSTOM_LOOP_LIST`
| :term:`ENSEMBLE_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`ENSEMBLE_STAT_DESC`
| :term:`ENSEMBLE_STAT_ENS_SSVAR_BIN_SIZE`
| :term:`ENSEMBLE_STAT_ENS_PHIST_BIN_SIZE`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_BINS`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_DIRECT_PROB`
| :term:`ENSEMBLE_STAT_DUPLICATE_FLAG`
| :term:`ENSEMBLE_STAT_SKIP_CONST`
| :term:`ENSEMBLE_STAT_CENSOR_THRESH`
| :term:`ENSEMBLE_STAT_CENSOR_VAL`
| :term:`ENSEMBLE_STAT_DUPLICATE_FLAG`
| :term:`ENSEMBLE_STAT_SKIP_CONST`
| :term:`ENSEMBLE_STAT_OBS_ERROR_FLAG`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_VAR<n>_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_VAR<n>_LEVELS`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_VAR<n>_OPTIONS`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_FIELD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_USE_FCST`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_USE_OBS`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_VAR<n>_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_VAR<n>_LEVELS`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_VAR<n>_OPTIONS`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_FIELD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_USE_FCST`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_USE_OBS`
| :term:`ENSEMBLE_STAT_MASK_GRID`
| :term:`ENSEMBLE_STAT_CI_ALPHA`
| :term:`ENSEMBLE_STAT_INTERP_FIELD`
| :term:`ENSEMBLE_STAT_INTERP_VLD_THRESH`
| :term:`ENSEMBLE_STAT_INTERP_SHAPE`
| :term:`ENSEMBLE_STAT_INTERP_METHOD`
| :term:`ENSEMBLE_STAT_INTERP_WIDTH`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ECNT`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RPS`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RHIST`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PHIST`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ORANK`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RELP`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PCT`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PSTD`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PJC`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PRC`
| :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ECLV`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_LATLON`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_MEAN`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_RAW`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_RANK`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_PIT`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_VLD_COUNT`
| :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_WEIGHT`
| :term:`ENSEMBLE_STAT_OBS_QUALITY_INC`
| :term:`ENSEMBLE_STAT_OBS_QUALITY_EXC`
| :term:`ENSEMBLE_STAT_MET_CONFIG_OVERRIDES`
| :term:`ENSEMBLE_STAT_ENS_MEMBER_IDS`
| :term:`ENSEMBLE_STAT_CONTROL_ID`
| :term:`ENSEMBLE_STAT_GRID_WEIGHT_FLAG`
| :term:`ENSEMBLE_STAT_PROB_CAT_THRESH`
| :term:`ENSEMBLE_STAT_PROB_PCT_THRESH`
| :term:`ENSEMBLE_STAT_ECLV_POINTS`
| :term:`FCST_ENSEMBLE_STAT_IS_PROB`
| :term:`FCST_ENSEMBLE_STAT_PROB_IN_GRIB_PDS`
| :term:`ENSEMBLE_STAT_VERIFICATION_MASK_TEMPLATE`
| :term:`ENS_VAR<n>_NAME`
| :term:`ENS_VAR<n>_LEVELS`
| :term:`ENS_VAR<n>_THRESH`
| :term:`ENS_VAR<n>_OPTIONS`
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_NAME`
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_LEVELS`
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_THRESH`
| :term:`FCST_ENSEMBLE_STAT_VAR<n>_OPTIONS`
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_NAME`
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_LEVELS`
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_THRESH`
| :term:`OBS_ENSEMBLE_STAT_VAR<n>_OPTIONS`
|

.. warning:: **DEPRECATED:**

   | :term:`ENSEMBLE_STAT_OUT_DIR`
   | :term:`ENSEMBLE_STAT_CONFIG`
   | :term:`ENSEMBLE_STAT_MET_OBS_ERROR_TABLE`
   | :term:`ENSEMBLE_STAT_GRID_VX`
   | :term:`ENSEMBLE_STAT_CLIMO_MEAN_INPUT_DIR`
   | :term:`ENSEMBLE_STAT_CLIMO_STDEV_INPUT_DIR`
   | :term:`ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
   | :term:`ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE`

.. _ens-stat-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/EnsembleStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/EnsembleStatConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/EnsembleStatConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` or :term:`ENSEMBLE_STAT_DESC`
     - desc

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBTYPE`
     - obtype

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_REGRID_SHAPE`
     - regrid.shape
   * - :term:`ENSEMBLE_STAT_REGRID_METHOD`
     - regrid.method
   * - :term:`ENSEMBLE_STAT_REGRID_WIDTH`
     - regrid.width
   * - :term:`ENSEMBLE_STAT_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`ENSEMBLE_STAT_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`ENSEMBLE_STAT_REGRID_CONVERT`
     - regrid.convert
   * - :term:`ENSEMBLE_STAT_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`ENSEMBLE_STAT_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CENSOR_VAL`
     - censor_val

**${METPLUS_ENS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENS_ENSEMBLE_STAT_INPUT_DATATYPE`
     - ens.file_type

**${METPLUS_ENS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_THRESH`
     - fcst.ens_thresh

**${METPLUS_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_VLD_THRESH`
     - fcst.vld_thresh

**${METPLUS_OBS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OBS_THRESH`
     - obs_thresh

**${METPLUS_ENS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENS_VAR<n>_NAME`
     - ens.field.name
   * - :term:`ENS_VAR<n>_LEVELS`
     - ens.field.level
   * - :term:`ENS_VAR<n>_THRESH`
     - ens.field.cat_thresh
   * - :term:`ENS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_PROB_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_PROB_CAT_THRESH`
     - prob_cat_thresh

**${METPLUS_PROB_PCT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_PROB_PCT_THRESH`
     - prob_pct_thresh

**${METPLUS_ECLV_POINTS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ECLV_POINTS`
     - eclv_points

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`
     - fcst.file_type

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE` -or- :term:`OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE`
     - obs.file_type

**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_MESSAGE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_MESSAGE_TYPE`
     - message_type

**${METPLUS_DUPLICATE_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_DUPLICATE_FLAG`
     - duplicate_flag

**${METPLUS_SKIP_CONST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_SKIP_CONST`
     - skip_const

**${METPLUS_OBS_ERROR_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OBS_ERROR_FLAG`
     - obs_error.flag

**${METPLUS_ENS_SSVAR_BIN_SIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_SSVAR_BIN_SIZE`
     - ens_ssvar_bin_size

**${METPLUS_ENS_PHIST_BIN_SIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_PHIST_BIN_SIZE`
     - ens_phist_bin_size

**${METPLUS_CLIMO_MEAN_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME`
     - climo_mean.file_name
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_FIELD`
     - climo_mean.field
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD`
     - climo_mean.regrid.method
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH`
     - climo_mean.regrid.width
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
     - climo_mean.regrid.vld_thresh
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE`
     - climo_mean.regrid.shape
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
     - climo_mean.time_interp_method
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH`
     - climo_mean.match_month
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL`
     - climo_mean.day_interval
   * - :term:`ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL`
     - climo_mean.hour_interval


**${METPLUS_CLIMO_STDEV_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME`
     - climo_stdev.file_name
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_FIELD`
     - climo_stdev.field
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD`
     - climo_stdev.regrid.method
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH`
     - climo_stdev.regrid.width
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
     - climo_stdev.regrid.vld_thresh
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE`
     - climo_stdev.regrid.shape
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
     - climo_stdev.time_interp_method
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH`
     - climo_stdev.match_month
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL`
     - climo_stdev.day_interval
   * - :term:`ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL`
     - climo_stdev.hour_interval


**${METPLUS_CLIMO_CDF_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_OBS_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CLIMO_CDF_BINS`
     - climo_cdv.cdf_bins
   * - :term:`ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS`
     - climo_cdv.center_bins
   * - :term:`ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS`
     - climo_cdv.write_bins
   * - :term:`ENSEMBLE_STAT_CLIMO_CDF_DIRECT_PROB`
     - climo_cdf.direct_prob

**${METPLUS_MASK_GRID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_MASK_GRID`
     - mask.grid

**${METPLUS_MASK_POLY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_MASK_POLY`
     - mask.poly

**${METPLUS_CI_ALPHA}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CI_ALPHA`
     - ci_alpha

**${METPLUS_INTERP_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_INTERP_FIELD`
     - interp.field
   * - :term:`ENSEMBLE_STAT_INTERP_VLD_THRESH`
     - interp.vld_thresh
   * - :term:`ENSEMBLE_STAT_INTERP_SHAPE`
     - interp.shape
   * - :term:`ENSEMBLE_STAT_INTERP_METHOD`
     - interp.type.method
   * - :term:`ENSEMBLE_STAT_INTERP_WIDTH`
     - interp.type.width

**${METPLUS_OUTPUT_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ECNT`
     - output_flag.ecnt
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RPS`
     - output_flag.rps
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RHIST`
     - output_flag.rhist
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PHIST`
     - output_flag.phist
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ORANK`
     - output_flag.orank
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR`
     - output_flag.ssvar
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_RELP`
     - output_flag.relp
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PCT`
     - output_flag.pct
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PSTD`
     - output_flag.pstd
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PJC`
     - output_flag.pjc
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_PRC`
     - output_flag.prc
   * - :term:`ENSEMBLE_STAT_OUTPUT_FLAG_ECLV`
     - output_flag.eclv

**${METPLUS_NC_ORANK_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_LATLON`
     - nc_orank_flag.latlon
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_MEAN`
     - nc_orank_flag.mean
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_RAW`
     - nc_orank_flag.raw
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_RANK`
     - nc_orank_flag.rank
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_PIT`
     - nc_orank_flag.pit
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_VLD_COUNT`
     - nc_orank_flag.vld_count
   * - :term:`ENSEMBLE_STAT_NC_ORANK_FLAG_WEIGHT`
     - nc_orank_flag.weight

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_OBS_QUALITY_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OBS_QUALITY_INC`
     - obs_quality_inc

**${METPLUS_OBS_QUALITY_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OBS_QUALITY_EXC`
     - obs_quality_exc

**${METPLUS_ENS_MEMBER_IDS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_MEMBER_IDS`
     - ens_member_ids

**${METPLUS_CONTROL_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_CONTROL_ID`
     - control_id

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_GRID_WEIGHT_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_GRID_WEIGHT_FLAG`
     - grid_weight_flag


.. _example_wrapper:

Example
=======

Description
-----------

Used to demonstrate how the METplus wrappers handle looping and building commands.

Configuration
-------------

| :term:`EXAMPLE_INPUT_DIR`
| :term:`EXAMPLE_INPUT_TEMPLATE`
| :term:`EXAMPLE_CUSTOM_LOOP_LIST`
|

.. _extract_tiles_wrapper:

ExtractTiles
============

Description
-----------

The ExtractTiles wrapper is used to regrid and extract subregions from
paired tropical cyclone tracks generated with TCStat, or from cluster object
centroids generated with MODE Time Domain (MTD).
Unlike the other wrappers, the extract_tiles_wrapper does not correspond
to a specific MET tool. It reads track information to determine the
lat/lon positions of the paired track data.
This information is then used to create tiles of subregions.
The ExtractTiles wrapper creates a 2n degree x 2m degree
grid/tile with each storm located at the center.

METplus Configuration
---------------------

The following should be set in the METplus configuration file to define
the dimensions and density of the tiles comprising the subregion:

| :term:`EXTRACT_TILES_OUTPUT_DIR`
| :term:`EXTRACT_TILES_TC_STAT_INPUT_DIR`
| :term:`FCST_EXTRACT_TILES_INPUT_DIR`
| :term:`OBS_EXTRACT_TILES_INPUT_DIR`
| :term:`FCST_EXTRACT_TILES_INPUT_TEMPLATE`
| :term:`OBS_EXTRACT_TILES_INPUT_TEMPLATE`
| :term:`FCST_EXTRACT_TILES_OUTPUT_TEMPLATE`
| :term:`OBS_EXTRACT_TILES_OUTPUT_TEMPLATE`
| :term:`EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE`
| :term:`EXTRACT_TILES_MTD_INPUT_DIR`
| :term:`EXTRACT_TILES_MTD_INPUT_TEMPLATE`
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
|

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
   | :term:`EXTRACT_TILES_STAT_INPUT_DIR`
   | :term:`EXTRACT_TILES_STAT_INPUT_TEMPLATE`
   |

.. _gempak_to_cf_wrapper:

GempakToCF
==========

Description
-----------

Used to configure the utility GempakToCF.

METplus Configuration
---------------------

| :term:`GEMPAKTOCF_JAR`
| :term:`GEMPAKTOCF_INPUT_DIR`
| :term:`GEMPAKTOCF_OUTPUT_DIR`
| :term:`GEMPAKTOCF_INPUT_TEMPLATE`
| :term:`GEMPAKTOCF_OUTPUT_TEMPLATE`
| :term:`GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS`
| :term:`GEMPAKTOCF_CUSTOM_LOOP_LIST`
|

.. warning:: **DEPRECATED:**

   | :term:`GEMPAKTOCF_CLASSPATH`
   |

.. _gen_ens_prod_wrapper:

GenEnsProd
==========

Description
-----------

Used to configure the MET tool gen_ens_prod to generate ensemble products.

METplus Configuration
---------------------

| :term:`GEN_ENS_PROD_INPUT_DIR`
| :term:`GEN_ENS_PROD_INPUT_TEMPLATE`
| :term:`GEN_ENS_PROD_INPUT_FILE_LIST`
| :term:`GEN_ENS_PROD_CTRL_INPUT_DIR`
| :term:`GEN_ENS_PROD_CTRL_INPUT_TEMPLATE`
| :term:`GEN_ENS_PROD_OUTPUT_DIR`
| :term:`GEN_ENS_PROD_OUTPUT_TEMPLATE`
| :term:`LOG_GEN_ENS_PROD_VERBOSITY`
| :term:`MODEL`
| :term:`GEN_ENS_PROD_DESC`
| :term:`GEN_ENS_PROD_REGRID_TO_GRID`
| :term:`GEN_ENS_PROD_REGRID_METHOD`
| :term:`GEN_ENS_PROD_REGRID_WIDTH`
| :term:`GEN_ENS_PROD_REGRID_VLD_THRESH`
| :term:`GEN_ENS_PROD_REGRID_SHAPE`
| :term:`GEN_ENS_PROD_REGRID_CONVERT`
| :term:`GEN_ENS_PROD_REGRID_CENSOR_THRESH`
| :term:`GEN_ENS_PROD_REGRID_CENSOR_VAL`
| :term:`GEN_ENS_PROD_CENSOR_THRESH`
| :term:`GEN_ENS_PROD_CENSOR_VAL`
| :term:`GEN_ENS_PROD_CAT_THRESH`
| :term:`GEN_ENS_PROD_NORMALIZE`
| :term:`GEN_ENS_PROD_NC_VAR_STR`
| :term:`GEN_ENS_PROD_ENS_THRESH`
| :term:`GEN_ENS_PROD_ENS_VLD_THRESH`
| :term:`GEN_ENS_PROD_NBRHD_PROB_WIDTH`
| :term:`GEN_ENS_PROD_NBRHD_PROB_SHAPE`
| :term:`GEN_ENS_PROD_NBRHD_PROB_VLD_THRESH`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_VLD_THRESH`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_SHAPE`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_DX`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_RADIUS`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_METHOD`
| :term:`GEN_ENS_PROD_NMEP_SMOOTH_WIDTH`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_FILE_NAME`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_VAR<n>_NAME`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_VAR<n>_LEVELS`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_VAR<n>_OPTIONS`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_FIELD`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_METHOD`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_WIDTH`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_SHAPE`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_MATCH_MONTH`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_DAY_INTERVAL`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_USE_FCST`
| :term:`GEN_ENS_PROD_CLIMO_MEAN_USE_OBS`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_FILE_NAME`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_VAR<n>_NAME`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_VAR<n>_LEVELS`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_VAR<n>_OPTIONS`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_FIELD`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_METHOD`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_WIDTH`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_SHAPE`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_MATCH_MONTH`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_DAY_INTERVAL`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_USE_FCST`
| :term:`GEN_ENS_PROD_CLIMO_STDEV_USE_OBS`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_LATLON`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MEAN`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_STDEV`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MINUS`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_PLUS`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MIN`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MAX`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_RANGE`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_VLD_COUNT`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_FREQUENCY`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_NEP`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_NMEP`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO`
| :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO_CDP`
| :term:`GEN_ENS_PROD_ENS_MEMBER_IDS`
| :term:`GEN_ENS_PROD_CONTROL_ID`
| :term:`GEN_ENS_PROD_MET_CONFIG_OVERRIDES`

.. _gen-ens-prod-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/GenEnsProdConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/GenEnsProdConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/GenEnsProdConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` or :term:`GEN_ENS_PROD_DESC`
     - desc

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_REGRID_SHAPE`
     - regrid.shape
   * - :term:`GEN_ENS_PROD_REGRID_METHOD`
     - regrid.method
   * - :term:`GEN_ENS_PROD_REGRID_WIDTH`
     - regrid.width
   * - :term:`GEN_ENS_PROD_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`GEN_ENS_PROD_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`GEN_ENS_PROD_REGRID_CONVERT`
     - regrid.convert
   * - :term:`GEN_ENS_PROD_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`GEN_ENS_PROD_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CENSOR_VAL`
     - censor_val

**${METPLUS_NORMALIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_NORMALIZE`
     - normalize

**${METPLUS_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CAT_THRESH`
     - cat_thresh

**${METPLUS_NC_VAR_STR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_NC_VAR_STR`
     - nc_var_str

**${METPLUS_ENS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_ENS_FILE_TYPE`
     - ens.file_type

**${METPLUS_ENS_ENS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_ENS_THRESH`
     - ens.ens_thresh

**${METPLUS_ENS_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_ENS_VLD_THRESH`
     - ens.vld_thresh

**${METPLUS_ENS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENS_VAR<n>_NAME`
     - ens.field.name
   * - :term:`ENS_VAR<n>_LEVELS`
     - ens.field.level
   * - :term:`ENS_VAR<n>_THRESH`
     - ens.field.cat_thresh
   * - :term:`ENS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_NBRHD_PROB_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_NBRHD_PROB_WIDTH`
     - nbrhd_prob.width
   * - :term:`GEN_ENS_PROD_NBRHD_PROB_SHAPE`
     - nbrhd_prob.shape
   * - :term:`GEN_ENS_PROD_NBRHD_PROB_VLD_THRESH`
     - nbrhd_prob.vld_thresh

**${METPLUS_NMEP_SMOOTH_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_VLD_THRESH`
     - nmep_smooth.vld_thresh
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_SHAPE`
     - nmep_smooth.shape
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_DX`
     - nmep_smooth.gaussian_dx
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_GAUSSIAN_RADIUS`
     - nmep_smooth.gaussian_radius
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_METHOD`
     - nmep_smooth.type.method
   * - :term:`GEN_ENS_PROD_NMEP_SMOOTH_WIDTH`
     - nmep_smooth.type.width

**${METPLUS_CLIMO_MEAN_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_FILE_NAME`
     - climo_mean.file_name
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_FIELD`
     - climo_mean.field
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_METHOD`
     - climo_mean.regrid.method
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_WIDTH`
     - climo_mean.regrid.width
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_VLD_THRESH`
     - climo_mean.regrid.vld_thresh
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_REGRID_SHAPE`
     - climo_mean.regrid.shape
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_TIME_INTERP_METHOD`
     - climo_mean.time_interp_method
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_MATCH_MONTH`
     - climo_mean.match_month
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_DAY_INTERVAL`
     - climo_mean.day_interval
   * - :term:`GEN_ENS_PROD_CLIMO_MEAN_HOUR_INTERVAL`
     - climo_mean.hour_interval

**${METPLUS_CLIMO_STDEV_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_FILE_NAME`
     - climo_stdev.file_name
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_FIELD`
     - climo_stdev.field
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_METHOD`
     - climo_stdev.regrid.method
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_WIDTH`
     - climo_stdev.regrid.width
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_VLD_THRESH`
     - climo_stdev.regrid.vld_thresh
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_REGRID_SHAPE`
     - climo_stdev.regrid.shape
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_TIME_INTERP_METHOD`
     - climo_stdev.time_interp_method
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_MATCH_MONTH`
     - climo_stdev.match_month
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_DAY_INTERVAL`
     - climo_stdev.day_interval
   * - :term:`GEN_ENS_PROD_CLIMO_STDEV_HOUR_INTERVAL`
     - climo_stdev.hour_interval

**${METPLUS_ENSEMBLE_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_LATLON`
     - ensemble_flag.latlon
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MEAN`
     - ensemble_flag.mean
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_STDEV`
     - ensemble_flag.stdev
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MINUS`
     - ensemble_flag.minus
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_PLUS`
     - ensemble_flag.plus
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MIN`
     - ensemble_flag.min
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_MAX`
     - ensemble_flag.max
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_RANGE`
     - ensemble_flag.range
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_VLD_COUNT`
     - ensemble_flag.vld_count
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_FREQUENCY`
     - ensemble_flag.frequency
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_NEP`
     - ensemble_flag.nep
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_NMEP`
     - ensemble_flag.nmep
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO`
     - ensemble_flag.climo
   * - :term:`GEN_ENS_PROD_ENSEMBLE_FLAG_CLIMO_CDP`
     - ensemble_flag.climo_cdp

**${METPLUS_ENS_MEMBER_IDS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_ENS_MEMBER_IDS`
     - ens_member_ids

**${METPLUS_CONTROL_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_CONTROL_ID`
     - control_id

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GEN_ENS_PROD_MET_CONFIG_OVERRIDES`
     - n/a


.. _gen_vx_mask_wrapper:

GenVxMask
=========

Description
-----------

Used to configure the MET tool GenVxMask to define and generate masking regions.

Configuration
-------------

| :term:`GEN_VX_MASK_INPUT_DIR`
| :term:`GEN_VX_MASK_INPUT_MASK_DIR`
| :term:`GEN_VX_MASK_OUTPUT_DIR`
| :term:`GEN_VX_MASK_INPUT_TEMPLATE`
| :term:`GEN_VX_MASK_INPUT_MASK_TEMPLATE`
| :term:`GEN_VX_MASK_OUTPUT_TEMPLATE`
| :term:`GEN_VX_MASK_OPTIONS`
| :term:`LOG_GEN_VX_MASK_VERBOSITY`
| :term:`GEN_VX_MASK_SKIP_IF_OUTPUT_EXISTS`
| :term:`GEN_VX_MASK_CUSTOM_LOOP_LIST`
| :term:`GEN_VX_MASK_FILE_WINDOW_BEGIN`
| :term:`GEN_VX_MASK_FILE_WINDOW_END`
|

.. _gfdl_tracker_wrapper:

GFDLTracker
===========

Description
-----------

Used to call the GFDL Tracker applications to objectively analyze forecast data
to provide an estimate of the vortex center position (latitude and longitude),
and track the storm for the duration of the forecast. The wrapper copies files
and uses symbolic links to ensure that input files are named and located in
the correct place so that the tracker can read them. The wrapper also generates
index files and other inputs that are required to run the tool and substitutes
values into template configuration files that are read by the tracker.
Relevant output files are renamed based on user configuration.
See :ref:`external-components-gfdl-tracker` for more information.

METplus Configuration
---------------------

| :term:`GFDL_TRACKER_BASE`
| :term:`GFDL_TRACKER_INPUT_DIR`
| :term:`GFDL_TRACKER_INPUT_TEMPLATE`
| :term:`GFDL_TRACKER_TC_VITALS_INPUT_DIR`
| :term:`GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE`
| :term:`GFDL_TRACKER_OUTPUT_DIR`
| :term:`GFDL_TRACKER_OUTPUT_TEMPLATE`
| :term:`GFDL_TRACKER_GRIB_VERSION`
| :term:`GFDL_TRACKER_NML_TEMPLATE_FILE`
| :term:`GFDL_TRACKER_DATEIN_INP_MODEL`
| :term:`GFDL_TRACKER_DATEIN_INP_MODTYP`
| :term:`GFDL_TRACKER_DATEIN_INP_LT_UNITS`
| :term:`GFDL_TRACKER_DATEIN_INP_FILE_SEQ`
| :term:`GFDL_TRACKER_DATEIN_INP_NESTTYP`
| :term:`GFDL_TRACKER_ATCFINFO_ATCFNUM`
| :term:`GFDL_TRACKER_ATCFINFO_ATCFNAME`
| :term:`GFDL_TRACKER_ATCFINFO_ATCFFREQ`
| :term:`GFDL_TRACKER_TRACKERINFO_TYPE`
| :term:`GFDL_TRACKER_TRACKERINFO_MSLPTHRESH`
| :term:`GFDL_TRACKER_TRACKERINFO_USE_BACKUP_MSLP_GRAD_CHECK`
| :term:`GFDL_TRACKER_TRACKERINFO_V850THRESH`
| :term:`GFDL_TRACKER_TRACKERINFO_USE_BACKUP_850_VT_CHECK`
| :term:`GFDL_TRACKER_TRACKERINFO_ENABLE_TIMING`
| :term:`GFDL_TRACKER_TRACKERINFO_GRIDTYPE`
| :term:`GFDL_TRACKER_TRACKERINFO_CONTINT`
| :term:`GFDL_TRACKER_TRACKERINFO_WANT_OCI`
| :term:`GFDL_TRACKER_TRACKERINFO_OUT_VIT`
| :term:`GFDL_TRACKER_TRACKERINFO_USE_LAND_MASK`
| :term:`GFDL_TRACKER_TRACKERINFO_INP_DATA_TYPE`
| :term:`GFDL_TRACKER_TRACKERINFO_GRIBVER`
| :term:`GFDL_TRACKER_TRACKERINFO_G2_JPDTN`
| :term:`GFDL_TRACKER_TRACKERINFO_G2_MSLP_PARM_ID`
| :term:`GFDL_TRACKER_TRACKERINFO_G1_MSLP_PARM_ID`
| :term:`GFDL_TRACKER_TRACKERINFO_G1_SFCWIND_LEV_TYP`
| :term:`GFDL_TRACKER_TRACKERINFO_G1_SFCWIND_LEV_VAL`
| :term:`GFDL_TRACKER_PHASEINFO_PHASEFLAG`
| :term:`GFDL_TRACKER_PHASEINFO_PHASESCHEME`
| :term:`GFDL_TRACKER_PHASEINFO_WCORE_DEPTH`
| :term:`GFDL_TRACKER_STRUCTINFO_STRUCTFLAG`
| :term:`GFDL_TRACKER_STRUCTINFO_IKEFLAG`
| :term:`GFDL_TRACKER_FNAMEINFO_GMODNAME`
| :term:`GFDL_TRACKER_FNAMEINFO_RUNDESCR`
| :term:`GFDL_TRACKER_FNAMEINFO_ATCFDESCR`
| :term:`GFDL_TRACKER_WAITINFO_USE_WAITFOR`
| :term:`GFDL_TRACKER_WAITINFO_WAIT_MIN_AGE`
| :term:`GFDL_TRACKER_WAITINFO_WAIT_MIN_SIZE`
| :term:`GFDL_TRACKER_WAITINFO_WAIT_MAX_WAIT`
| :term:`GFDL_TRACKER_WAITINFO_WAIT_SLEEPTIME`
| :term:`GFDL_TRACKER_WAITINFO_USE_PER_FCST_COMMAND`
| :term:`GFDL_TRACKER_WAITINFO_PER_FCST_COMMAND`
| :term:`GFDL_TRACKER_NETCDFINFO_LAT_NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_LMASKNAME`
| :term:`GFDL_TRACKER_NETCDFINFO_LON_NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_MSLPNAME`
| :term:`GFDL_TRACKER_NETCDFINFO_NETCDF_FILENAME`
| :term:`GFDL_TRACKER_NETCDFINFO_NUM_NETCDF_VARS`
| :term:`GFDL_TRACKER_NETCDFINFO_RV700NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_RV850NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_TIME_NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_TIME_UNITS`
| :term:`GFDL_TRACKER_NETCDFINFO_TMEAN_300_500_NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_U500NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_U700NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_U850NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_USFCNAME`
| :term:`GFDL_TRACKER_NETCDFINFO_V500NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_V700NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_V850NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_VSFCNAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z200NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z300NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z350NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z400NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z450NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z500NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z550NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z600NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z650NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z700NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z750NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z800NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z850NAME`
| :term:`GFDL_TRACKER_NETCDFINFO_Z900NAME`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETA700`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRC850`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRC700`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_GPH850`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_GPH700`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_MSLP`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRCSFC`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETASFC`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK500850`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK200500`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK200850`
| :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETA850`
| :term:`GFDL_TRACKER_VERBOSE_VERB`
| :term:`GFDL_TRACKER_VERBOSE_VERB_G2`
| :term:`GFDL_TRACKER_KEEP_INTERMEDIATE`

.. _gfdl_tracker-nml-conf:

NML Configuration
-----------------

Below is the NML template configuration file used for this wrapper. The wrapper
substitutes values from the METplus configuration file into this configuration
file. While it may appear that environment variables are used in the NML
template file, they are not actually environment variables. The wrapper
searches for these strings and substitutes the values as appropriate.

.. literalinclude:: ../../parm/use_cases/met_tool_wrapper/GFDLTracker/template.nml

**${METPLUS_DATEIN_INP_BCC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &datein: inp%bcc

**${METPLUS_DATEIN_INP_BYY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &datein: inp%byy

**${METPLUS_DATEIN_INP_BMM}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &datein: inp%bmm

**${METPLUS_DATEIN_INP_BDD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &datein: inp%bdd

**${METPLUS_DATEIN_INP_BHH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &datein: inp%bhh

**${METPLUS_DATEIN_INP_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_DATEIN_INP_MODEL`
     - &datein: inp%model

**${METPLUS_DATEIN_INP_MODTYP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_DATEIN_INP_MODTYP`
     - &datein: inp%modtyp

**${METPLUS_DATEIN_INP_LT_UNITS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_DATEIN_INP_LT_UNITS`
     - &datein: inp%lt_units

**${METPLUS_DATEIN_INP_FILE_SEQ}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_DATEIN_INP_FILE_SEQ`
     - &datein: inp%file_seq

**${METPLUS_DATEIN_INP_NESTTYP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_DATEIN_INP_NESTTYP`
     - &datein: inp%nesttyp

**${METPLUS_ATCFINFO_ATCFNUM}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_ATCFINFO_ATCFNUM`
     - &atcfinfo: atcfnum

**${METPLUS_ATCFINFO_ATCFNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_ATCFINFO_ATCFNAME`
     - &atcfinfo: atcfname

**${METPLUS_ATCFINFO_ATCFYMDH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`INIT_BEG`
     - &atcfinfo: atcfymdh

**${METPLUS_ATCFINFO_ATCFFREQ}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_ATCFINFO_ATCFFREQ`
     - &atcfinfo: atcffreq

**${METPLUS_TRACKERINFO_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_TYPE`
     - &trackerinfo: trkrinfo%type

**${METPLUS_TRACKERINFO_MSLPTHRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_MSLPTHRESH`
     - &trackerinfo: trkrinfo%mslpthresh

**${METPLUS_TRACKERINFO_USE_BACKUP_MSLP_GRAD_CHECK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_USE_BACKUP_MSLP_GRAD_CHECK`
     - &trackerinfo: trkrinfo%use_backup_mslp_grad_check

**${METPLUS_TRACKERINFO_V850THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_V850THRESH`
     - &trackerinfo: trkrinfo%v850thresh

**${METPLUS_TRACKERINFO_USE_BACKUP_850_VT_CHECK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_USE_BACKUP_850_VT_CHECK`
     - &trackerinfo: trkrinfo%use_backup_850_vt_check

**${METPLUS_TRACKERINFO_ENABLE_TIMING}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_ENABLE_TIMING`
     - &trackerinfo: trkrinfo%enable_timing

**${METPLUS_TRACKERINFO_GRIDTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_GRIDTYPE`
     - &trackerinfo: trkrinfo%gridtype

**${METPLUS_TRACKERINFO_CONTINT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_CONTINT`
     - &trackerinfo: trkrinfo%contint

**${METPLUS_TRACKERINFO_WANT_OCI}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_WANT_OCI`
     - &trackerinfo: trkrinfo%want_oci

**${METPLUS_TRACKERINFO_OUT_VIT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_OUT_VIT`
     - &trackerinfo: trkrinfo%out_vit

**${METPLUS_TRACKERINFO_USE_LAND_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_USE_LAND_MASK`
     - &trackerinfo: trkrinfo%use_land_mask

**${METPLUS_TRACKERINFO_INP_DATA_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_INP_DATA_TYPE`
     - &trackerinfo: trkrinfo%inp_data_type

**${METPLUS_TRACKERINFO_GRIBVER}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_GRIBVER`
     - &trackerinfo: trkrinfo%gribver

**${METPLUS_TRACKERINFO_G2_JPDTN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_G2_JPDTN`
     - &trackerinfo: trkrinfo%g2_jpdtn

**${METPLUS_TRACKERINFO_G2_MSLP_PARM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_G2_MSLP_PARM_ID`
     - &trackerinfo: trkrinfo%g2_mslp_parm_id

**${METPLUS_TRACKERINFO_G1_MSLP_PARM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_G1_MSLP_PARM_ID`
     - &trackerinfo: trkrinfo%g1_mslp_parm_id

**${METPLUS_TRACKERINFO_G1_SFCWIND_LEV_TYP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_G1_SFCWIND_LEV_TYP`
     - &trackerinfo: trkrinfo%g1_sfcwind_lev_typ

**${METPLUS_TRACKERINFO_G1_SFCWIND_LEV_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_TRACKERINFO_G1_SFCWIND_LEV_VAL`
     - &trackerinfo: trkrinfo%g1_sfcwind_lev_val

**${METPLUS_PHASEINFO_PHASEFLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_PHASEINFO_PHASEFLAG`
     - &phaseinfo: phaseflag

**${METPLUS_PHASEINFO_PHASESCHEME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_PHASEINFO_PHASESCHEME`
     - &phaseinfo: phasescheme

**${METPLUS_PHASEINFO_WCORE_DEPTH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_PHASEINFO_WCORE_DEPTH`
     - &phaseinfo: wcore_depth

**${METPLUS_STRUCTINFO_STRUCTFLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_STRUCTINFO_STRUCTFLAG`
     - &structinfo: structflag

**${METPLUS_STRUCTINFO_IKEFLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_STRUCTINFO_IKEFLAG`
     - &structinfo: ikeflag

**${METPLUS_FNAMEINFO_GMODNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_FNAMEINFO_GMODNAME`
     - &fnameinfo: gmodname

**${METPLUS_FNAMEINFO_RUNDESCR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_FNAMEINFO_RUNDESCR`
     - &fnameinfo: rundescr

**${METPLUS_FNAMEINFO_ATCFDESCR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_FNAMEINFO_ATCFDESCR`
     - &fnameinfo: atcfdescr

**${METPLUS_WAITINFO_USE_WAITFOR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_USE_WAITFOR`
     - &waitinfo: use_waitfor

**${METPLUS_WAITINFO_WAIT_MIN_AGE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_WAIT_MIN_AGE`
     - &waitinfo: wait_min_age

**${METPLUS_WAITINFO_WAIT_MIN_SIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_WAIT_MIN_SIZE`
     - &waitinfo: wait_min_size

**${METPLUS_WAITINFO_WAIT_MAX_WAIT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_WAIT_MAX_WAIT`
     - &waitinfo: wait_max_wait

**${METPLUS_WAITINFO_WAIT_SLEEPTIME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_WAIT_SLEEPTIME`
     - &waitinfo: wait_sleeptime

**${METPLUS_WAITINFO_USE_PER_FCST_COMMAND}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_USE_PER_FCST_COMMAND`
     - &waitinfo: use_per_fcst_command

**${METPLUS_WAITINFO_PER_FCST_COMMAND}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_WAITINFO_PER_FCST_COMMAND`
     - &waitinfo: per_fcst_command

**${METPLUS_NETCDFINFO_LAT_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_LAT_NAME`
     - &netcdflist: netcdfinfo%lat_name

**${METPLUS_NETCDFINFO_LMASKNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_LMASKNAME`
     - &netcdflist: netcdfinfo%lmaskname

**${METPLUS_NETCDFINFO_LON_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_LON_NAME`
     - &netcdflist: netcdfinfo%lon_name

**${METPLUS_NETCDFINFO_MSLPNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_MSLPNAME`
     - &netcdflist: netcdfinfo%mslpname

**${METPLUS_NETCDFINFO_NETCDF_FILENAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_NETCDF_FILENAME`
     - &netcdflist: netcdfinfo%netcdf_filename

**${METPLUS_NETCDFINFO_NUM_NETCDF_VARS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_NUM_NETCDF_VARS`
     - &netcdflist: netcdfinfo%num_netcdf_vars

**${METPLUS_NETCDFINFO_RV700NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_RV700NAME`
     - &netcdflist: netcdfinfo%rv700name

**${METPLUS_NETCDFINFO_RV850NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_RV850NAME`
     - &netcdflist: netcdfinfo%rv850name

**${METPLUS_NETCDFINFO_TIME_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_TIME_NAME`
     - &netcdflist: netcdfinfo%time_name

**${METPLUS_NETCDFINFO_TIME_UNITS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_TIME_UNITS`
     - &netcdflist: netcdfinfo%time_units

**${METPLUS_NETCDFINFO_TMEAN_300_500_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_TMEAN_300_500_NAME`
     - &netcdflist: netcdfinfo%tmean_300_500_name

**${METPLUS_NETCDFINFO_U500NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_U500NAME`
     - &netcdflist: netcdfinfo%u500name

**${METPLUS_NETCDFINFO_U700NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_U700NAME`
     - &netcdflist: netcdfinfo%u700name

**${METPLUS_NETCDFINFO_U850NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_U850NAME`
     - &netcdflist: netcdfinfo%u850name

**${METPLUS_NETCDFINFO_USFCNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_USFCNAME`
     - &netcdflist: netcdfinfo%usfcname

**${METPLUS_NETCDFINFO_V500NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_V500NAME`
     - &netcdflist: netcdfinfo%v500name

**${METPLUS_NETCDFINFO_V700NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_V700NAME`
     - &netcdflist: netcdfinfo%v700name

**${METPLUS_NETCDFINFO_V850NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_V850NAME`
     - &netcdflist: netcdfinfo%v850name

**${METPLUS_NETCDFINFO_VSFCNAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_VSFCNAME`
     - &netcdflist: netcdfinfo%vsfcname

**${METPLUS_NETCDFINFO_Z200NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z200NAME`
     - &netcdflist: netcdfinfo%z200name

**${METPLUS_NETCDFINFO_Z300NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z300NAME`
     - &netcdflist: netcdfinfo%z300name

**${METPLUS_NETCDFINFO_Z350NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z350NAME`
     - &netcdflist: netcdfinfo%z350name

**${METPLUS_NETCDFINFO_Z400NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z400NAME`
     - &netcdflist: netcdfinfo%z400name

**${METPLUS_NETCDFINFO_Z450NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z450NAME`
     - &netcdflist: netcdfinfo%z450name

**${METPLUS_NETCDFINFO_Z500NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z500NAME`
     - &netcdflist: netcdfinfo%z500name

**${METPLUS_NETCDFINFO_Z550NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z550NAME`
     - &netcdflist: netcdfinfo%z550name

**${METPLUS_NETCDFINFO_Z600NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z600NAME`
     - &netcdflist: netcdfinfo%z600name

**${METPLUS_NETCDFINFO_Z650NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z650NAME`
     - &netcdflist: netcdfinfo%z650name

**${METPLUS_NETCDFINFO_Z700NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z700NAME`
     - &netcdflist: netcdfinfo%z700name

**${METPLUS_NETCDFINFO_Z750NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z750NAME`
     - &netcdflist: netcdfinfo%z750name

**${METPLUS_NETCDFINFO_Z800NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z800NAME`
     - &netcdflist: netcdfinfo%z800name

**${METPLUS_NETCDFINFO_Z850NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z850NAME`
     - &netcdflist: netcdfinfo%z850name

**${METPLUS_NETCDFINFO_Z900NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_NETCDFINFO_Z900NAME`
     - &netcdflist: netcdfinfo%z900name

**${METPLUS_USER_WANTS_TO_TRACK_ZETA700}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETA700`
     - &parmpreflist: user_wants_to_track_zeta700

**${METPLUS_USER_WANTS_TO_TRACK_WCIRC850}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRC850`
     - &parmpreflist: user_wants_to_track_wcirc850

**${METPLUS_USER_WANTS_TO_TRACK_WCIRC700}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRC700`
     - &parmpreflist: user_wants_to_track_wcirc700

**${METPLUS_USER_WANTS_TO_TRACK_GPH850}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_GPH850`
     - &parmpreflist: user_wants_to_track_gph850

**${METPLUS_USER_WANTS_TO_TRACK_GPH700}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_GPH700`
     - &parmpreflist: user_wants_to_track_gph700

**${METPLUS_USER_WANTS_TO_TRACK_MSLP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_MSLP`
     - &parmpreflist: user_wants_to_track_mslp

**${METPLUS_USER_WANTS_TO_TRACK_WCIRCSFC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_WCIRCSFC`
     - &parmpreflist: user_wants_to_track_wcircsfc

**${METPLUS_USER_WANTS_TO_TRACK_ZETASFC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETASFC`
     - &parmpreflist: user_wants_to_track_zetasfc

**${METPLUS_USER_WANTS_TO_TRACK_THICK500850}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK500850`
     - &parmpreflist: user_wants_to_track_thick500850

**${METPLUS_USER_WANTS_TO_TRACK_THICK200500}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK200500`
     - &parmpreflist: user_wants_to_track_thick200500

**${METPLUS_USER_WANTS_TO_TRACK_THICK200850}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_THICK200850`
     - &parmpreflist: user_wants_to_track_thick200850

**${METPLUS_USER_WANTS_TO_TRACK_ZETA850}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_USER_WANTS_TO_TRACK_ZETA850`
     - &parmpreflist: user_wants_to_track_zeta850

**${METPLUS_VERBOSE_VERB}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_VERBOSE_VERB`
     - &verbose: verb

**${METPLUS_VERBOSE_VERB_G2}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - NML Config File
   * - :term:`GFDL_TRACKER_VERBOSE_VERB_G2`
     - &verbose: verb_g2


.. _grid_diag_wrapper:

GridDiag
========

Description
-----------

Used to configure the MET tool grid_diag.

METplus Configuration
---------------------

| :term:`GRID_DIAG_INPUT_DIR`
| :term:`GRID_DIAG_OUTPUT_DIR`
| :term:`GRID_DIAG_INPUT_TEMPLATE`
| :term:`GRID_DIAG_OUTPUT_TEMPLATE`
| :term:`GRID_DIAG_VERIFICATION_MASK_TEMPLATE`
| :term:`LOG_GRID_DIAG_VERBOSITY`
| :term:`GRID_DIAG_CONFIG_FILE`
| :term:`GRID_DIAG_CUSTOM_LOOP_LIST`
| :term:`GRID_DIAG_INPUT_DATATYPE`
| :term:`GRID_DIAG_REGRID_METHOD`
| :term:`GRID_DIAG_REGRID_WIDTH`
| :term:`GRID_DIAG_REGRID_VLD_THRESH`
| :term:`GRID_DIAG_REGRID_SHAPE`
| :term:`GRID_DIAG_REGRID_TO_GRID`
| :term:`GRID_DIAG_REGRID_CONVERT`
| :term:`GRID_DIAG_REGRID_CENSOR_THRESH`
| :term:`GRID_DIAG_REGRID_CENSOR_VAL`
| :term:`GRID_DIAG_DESC`
| :term:`GRID_DIAG_SKIP_IF_OUTPUT_EXISTS`
| :term:`GRID_DIAG_RUNTIME_FREQ`
| :term:`GRID_DIAG_DESC`
| :term:`GRID_DIAG_MET_CONFIG_OVERRIDES`
|

.. _grid-diag-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/GridDiagConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/GridDiagConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/GridDiagConfig_wrapped

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` or :term:`GRID_DIAG_DESC`
     - desc

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_DIAG_REGRID_SHAPE`
     - regrid.shape
   * - :term:`GRID_DIAG_REGRID_METHOD`
     - regrid.method
   * - :term:`GRID_DIAG_REGRID_WIDTH`
     - regrid.width
   * - :term:`GRID_DIAG_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`GRID_DIAG_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`GRID_DIAG_REGRID_CONVERT`
     - regrid.convert
   * - :term:`GRID_DIAG_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`GRID_DIAG_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_DIAG_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_DIAG_CENSOR_VAL`
     - censor_val


**${METPLUS_DATA_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`BOTH_VAR<n>_NAME`
     - data.field.name
   * - :term:`BOTH_VAR<n>_LEVELS`
     - data.field.level
   * - :term:`BOTH_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_DIAG_MASK_GRID`
     - mask.grid
   * - :term:`GRID_DIAG_MASK_POLY`
     - mask.poly

.. note:: Since the default value in the MET config file for 'grid' is grid = [ "FULL" ];, setting GRID_DIAG_MASK_GRID to an empty string will result in a value of grid = []; in the MET config file.

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_DIAG_MET_CONFIG_OVERRIDES`
     - n/a

.. _grid_stat_wrapper:

GridStat
========

Description
-----------

Used to configure the MET tool grid_stat.

METplus Configuration
---------------------

| :term:`FCST_GRID_STAT_INPUT_DIR`
| :term:`OBS_GRID_STAT_INPUT_DIR`
| :term:`GRID_STAT_OUTPUT_DIR`
| :term:`FCST_GRID_STAT_INPUT_TEMPLATE`
| :term:`OBS_GRID_STAT_INPUT_TEMPLATE`
| :term:`GRID_STAT_OUTPUT_TEMPLATE`
| :term:`GRID_STAT_VERIFICATION_MASK_TEMPLATE`
| :term:`LOG_GRID_STAT_VERBOSITY`
| :term:`GRID_STAT_OUTPUT_PREFIX`
| :term:`GRID_STAT_CONFIG_FILE`
| :term:`FCST_GRID_STAT_INPUT_DATATYPE`
| :term:`OBS_GRID_STAT_INPUT_DATATYPE`
| :term:`GRID_STAT_ONCE_PER_FIELD`
| :term:`GRID_STAT_CUSTOM_LOOP_LIST`
| :term:`GRID_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`GRID_STAT_DESC`
| :term:`GRID_STAT_REGRID_TO_GRID`
| :term:`GRID_STAT_REGRID_METHOD`
| :term:`GRID_STAT_REGRID_WIDTH`
| :term:`GRID_STAT_REGRID_VLD_THRESH`
| :term:`GRID_STAT_REGRID_SHAPE`
| :term:`GRID_STAT_REGRID_CONVERT`
| :term:`GRID_STAT_REGRID_CENSOR_THRESH`
| :term:`GRID_STAT_REGRID_CENSOR_VAL`
| :term:`GRID_STAT_CLIMO_CDF_BINS`
| :term:`GRID_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`GRID_STAT_CLIMO_CDF_WRITE_BINS`
| :term:`GRID_STAT_CLIMO_CDF_DIRECT_PROB`
| :term:`GRID_STAT_OUTPUT_FLAG_FHO`
| :term:`GRID_STAT_OUTPUT_FLAG_CTC`
| :term:`GRID_STAT_OUTPUT_FLAG_CTS`
| :term:`GRID_STAT_OUTPUT_FLAG_MCTC`
| :term:`GRID_STAT_OUTPUT_FLAG_MCTS`
| :term:`GRID_STAT_OUTPUT_FLAG_CNT`
| :term:`GRID_STAT_OUTPUT_FLAG_SL1L2`
| :term:`GRID_STAT_OUTPUT_FLAG_SAL1L2`
| :term:`GRID_STAT_OUTPUT_FLAG_VL1L2`
| :term:`GRID_STAT_OUTPUT_FLAG_VAL1L2`
| :term:`GRID_STAT_OUTPUT_FLAG_VCNT`
| :term:`GRID_STAT_OUTPUT_FLAG_PCT`
| :term:`GRID_STAT_OUTPUT_FLAG_PSTD`
| :term:`GRID_STAT_OUTPUT_FLAG_PJC`
| :term:`GRID_STAT_OUTPUT_FLAG_PRC`
| :term:`GRID_STAT_OUTPUT_FLAG_ECLV`
| :term:`GRID_STAT_OUTPUT_FLAG_NBRCTC`
| :term:`GRID_STAT_OUTPUT_FLAG_NBRCTS`
| :term:`GRID_STAT_OUTPUT_FLAG_NBRCNT`
| :term:`GRID_STAT_OUTPUT_FLAG_GRAD`
| :term:`GRID_STAT_OUTPUT_FLAG_DMAP`
| :term:`GRID_STAT_OUTPUT_FLAG_SEEPS`
| :term:`GRID_STAT_NC_PAIRS_FLAG_LATLON`
| :term:`GRID_STAT_NC_PAIRS_FLAG_RAW`
| :term:`GRID_STAT_NC_PAIRS_FLAG_DIFF`
| :term:`GRID_STAT_NC_PAIRS_FLAG_CLIMO`
| :term:`GRID_STAT_NC_PAIRS_FLAG_CLIMO_CDP`
| :term:`GRID_STAT_NC_PAIRS_FLAG_WEIGHT`
| :term:`GRID_STAT_NC_PAIRS_FLAG_NBRHD`
| :term:`GRID_STAT_NC_PAIRS_FLAG_FOURIER`
| :term:`GRID_STAT_NC_PAIRS_FLAG_GRADIENT`
| :term:`GRID_STAT_NC_PAIRS_FLAG_DISTANCE_MAP`
| :term:`GRID_STAT_NC_PAIRS_FLAG_APPLY_MASK`
| :term:`GRID_STAT_NC_PAIRS_FLAG_SEEPS`
| :term:`GRID_STAT_INTERP_FIELD`
| :term:`GRID_STAT_INTERP_VLD_THRESH`
| :term:`GRID_STAT_INTERP_SHAPE`
| :term:`GRID_STAT_INTERP_TYPE_METHOD`
| :term:`GRID_STAT_INTERP_TYPE_WIDTH`
| :term:`GRID_STAT_NC_PAIRS_VAR_NAME`
| :term:`GRID_STAT_GRID_WEIGHT_FLAG`
| :term:`FCST_GRID_STAT_FILE_TYPE`
| :term:`OBS_GRID_STAT_FILE_TYPE`
| :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`
| :term:`GRID_STAT_CLIMO_MEAN_VAR<n>_NAME`
| :term:`GRID_STAT_CLIMO_MEAN_VAR<n>_LEVELS`
| :term:`GRID_STAT_CLIMO_MEAN_VAR<n>_OPTIONS`
| :term:`GRID_STAT_CLIMO_MEAN_FIELD`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`GRID_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`GRID_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`GRID_STAT_CLIMO_MEAN_USE_FCST`
| :term:`GRID_STAT_CLIMO_MEAN_USE_OBS`
| :term:`GRID_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`GRID_STAT_CLIMO_STDEV_VAR<n>_NAME`
| :term:`GRID_STAT_CLIMO_STDEV_VAR<n>_LEVELS`
| :term:`GRID_STAT_CLIMO_STDEV_VAR<n>_OPTIONS`
| :term:`GRID_STAT_CLIMO_STDEV_FIELD`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`GRID_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`GRID_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`GRID_STAT_CLIMO_STDEV_USE_FCST`
| :term:`GRID_STAT_CLIMO_STDEV_USE_OBS`
| :term:`GRID_STAT_HSS_EC_VALUE`
| :term:`GRID_STAT_DISTANCE_MAP_BADDELEY_P`
| :term:`GRID_STAT_DISTANCE_MAP_BADDELEY_MAX_DIST`
| :term:`GRID_STAT_DISTANCE_MAP_FOM_ALPHA`
| :term:`GRID_STAT_DISTANCE_MAP_ZHU_WEIGHT`
| :term:`GRID_STAT_DISTANCE_MAP_BETA_VALUE_N`
| :term:`GRID_STAT_FOURIER_WAVE_1D_BEG`
| :term:`GRID_STAT_FOURIER_WAVE_1D_END`
| :term:`GRID_STAT_CENSOR_THRESH`
| :term:`GRID_STAT_CENSOR_VAL`
| :term:`FCST_GRID_STAT_IS_PROB`
| :term:`FCST_GRID_STAT_PROB_IN_GRIB_PDS`
| :term:`GRID_STAT_MASK_GRID`
| :term:`GRID_STAT_MASK_POLY`
| :term:`GRID_STAT_MET_CONFIG_OVERRIDES`
| :term:`FCST_GRID_STAT_PROB_THRESH`
| :term:`OBS_GRID_STAT_PROB_THRESH`
| :term:`GRID_STAT_NEIGHBORHOOD_WIDTH`
| :term:`GRID_STAT_NEIGHBORHOOD_SHAPE`
| :term:`GRID_STAT_NEIGHBORHOOD_COV_THRESH`
| :term:`FCST_GRID_STAT_WINDOW_BEGIN`
| :term:`FCST_GRID_STAT_WINDOW_END`
| :term:`OBS_GRID_STAT_WINDOW_BEGIN`
| :term:`OBS_GRID_STAT_WINDOW_END`
| :term:`FCST_GRID_STAT_FILE_WINDOW_BEGIN`
| :term:`FCST_GRID_STAT_FILE_WINDOW_END`
| :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN`
| :term:`OBS_GRID_STAT_FILE_WINDOW_END`
| :term:`FCST_GRID_STAT_VAR<n>_NAME`
| :term:`FCST_GRID_STAT_VAR<n>_LEVELS`
| :term:`FCST_GRID_STAT_VAR<n>_THRESH`
| :term:`FCST_GRID_STAT_VAR<n>_OPTIONS`
| :term:`OBS_GRID_STAT_VAR<n>_NAME`
| :term:`OBS_GRID_STAT_VAR<n>_LEVELS`
| :term:`OBS_GRID_STAT_VAR<n>_THRESH`
| :term:`OBS_GRID_STAT_VAR<n>_OPTIONS`
| :term:`GRID_STAT_SEEPS_P1_THRESH`
|

.. warning:: **DEPRECATED**

   | :term:`GRID_STAT_OUT_DIR`
   | :term:`GRID_STAT_CONFIG`
   | :term:`CLIMO_GRID_STAT_INPUT_DIR`
   | :term:`CLIMO_GRID_STAT_INPUT_TEMPLATE`
   | :term:`GRID_STAT_CLIMO_MEAN_INPUT_DIR`
   | :term:`GRID_STAT_CLIMO_STDEV_INPUT_DIR`
   | :term:`GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
   | :term:`GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE`
   |

.. _grid-stat-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/GridStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/GridStatConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/GridStatConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` or :term:`GRID_STAT_DESC`
     - desc

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBTYPE`
     - obtype

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_REGRID_SHAPE`
     - regrid.shape
   * - :term:`GRID_STAT_REGRID_METHOD`
     - regrid.method
   * - :term:`GRID_STAT_REGRID_WIDTH`
     - regrid.width
   * - :term:`GRID_STAT_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`GRID_STAT_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`GRID_STAT_REGRID_CONVERT`
     - regrid.convert
   * - :term:`GRID_STAT_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`GRID_STAT_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_GRID_STAT_FILE_TYPE`
     - fcst.file_type

**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_GRID_STAT_FILE_TYPE`
     - obs.file_type

**${METPLUS_CLIMO_MEAN_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`
     - climo_mean.file_name
   * - :term:`GRID_STAT_CLIMO_MEAN_FIELD`
     - climo_mean.field
   * - :term:`GRID_STAT_CLIMO_MEAN_REGRID_METHOD`
     - climo_mean.regrid.method
   * - :term:`GRID_STAT_CLIMO_MEAN_REGRID_WIDTH`
     - climo_mean.regrid.width
   * - :term:`GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
     - climo_mean.regrid.vld_thresh
   * - :term:`GRID_STAT_CLIMO_MEAN_REGRID_SHAPE`
     - climo_mean.regrid.shape
   * - :term:`GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
     - climo_mean.time_interp_method
   * - :term:`GRID_STAT_CLIMO_MEAN_MATCH_MONTH`
     - climo_mean.match_month
   * - :term:`GRID_STAT_CLIMO_MEAN_DAY_INTERVAL`
     - climo_mean.day_interval
   * - :term:`GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL`
     - climo_mean.hour_interval

**${METPLUS_CLIMO_STDEV_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CLIMO_STDEV_FILE_NAME`
     - climo_stdev.file_name
   * - :term:`GRID_STAT_CLIMO_STDEV_FIELD`
     - climo_stdev.field
   * - :term:`GRID_STAT_CLIMO_STDEV_REGRID_METHOD`
     - climo_stdev.regrid.method
   * - :term:`GRID_STAT_CLIMO_STDEV_REGRID_WIDTH`
     - climo_stdev.regrid.width
   * - :term:`GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
     - climo_stdev.regrid.vld_thresh
   * - :term:`GRID_STAT_CLIMO_STDEV_REGRID_SHAPE`
     - climo_stdev.regrid.shape
   * - :term:`GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
     - climo_stdev.time_interp_method
   * - :term:`GRID_STAT_CLIMO_STDEV_MATCH_MONTH`
     - climo_stdev.match_month
   * - :term:`GRID_STAT_CLIMO_STDEV_DAY_INTERVAL`
     - climo_stdev.day_interval
   * - :term:`GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL`
     - climo_stdev.hour_interval

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_MASK_GRID`
     - mask.grid
   * - :term:`GRID_STAT_MASK_POLY`
     - mask.poly

.. note:: Since the default value in the MET config file for 'grid' is grid = [ "FULL" ];, setting GRID_STAT_MASK_GRID to an empty string will result in a value of grid = []; in the MET config file.

**${METPLUS_NBRHD_SHAPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_NEIGHBORHOOD_SHAPE`
     - nbrhd.shape

**${METPLUS_NBRHD_WIDTH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_NEIGHBORHOOD_WIDTH`
     - nbrhd.width

**${METPLUS_NBRHD_COV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_NEIGHBORHOOD_COV_THRESH`
     - nbrhd.cov_thresh

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_CLIMO_CDF_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CLIMO_CDF_BINS`
     - climo_cdf.cdf_bins
   * - :term:`GRID_STAT_CLIMO_CDF_CENTER_BINS`
     - climo_cdf.center_bins
   * - :term:`GRID_STAT_CLIMO_CDF_WRITE_BINS`
     - climo_cdf.write_bins
   * - :term:`GRID_STAT_CLIMO_CDF_DIRECT_PROB`
     - climo_cdf.direct_prob

**${METPLUS_OUTPUT_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_OUTPUT_FLAG_FHO`
     - output_flag.fho
   * - :term:`GRID_STAT_OUTPUT_FLAG_CTC`
     - output_flag.ctc
   * - :term:`GRID_STAT_OUTPUT_FLAG_CTS`
     - output_flag.cts
   * - :term:`GRID_STAT_OUTPUT_FLAG_MCTC`
     - output_flag.mctc
   * - :term:`GRID_STAT_OUTPUT_FLAG_MCTS`
     - output_flag.mcts
   * - :term:`GRID_STAT_OUTPUT_FLAG_CNT`
     - output_flag.cnt
   * - :term:`GRID_STAT_OUTPUT_FLAG_SL1L2`
     - output_flag.sl1l2
   * - :term:`GRID_STAT_OUTPUT_FLAG_SAL1L2`
     - output_flag.sal1l2
   * - :term:`GRID_STAT_OUTPUT_FLAG_VL1L2`
     - output_flag.vl1l2
   * - :term:`GRID_STAT_OUTPUT_FLAG_VAL1L2`
     - output_flag.val1l2
   * - :term:`GRID_STAT_OUTPUT_FLAG_VCNT`
     - output_flag.vcnt
   * - :term:`GRID_STAT_OUTPUT_FLAG_PCT`
     - output_flag.pct
   * - :term:`GRID_STAT_OUTPUT_FLAG_PSTD`
     - output_flag.pstd
   * - :term:`GRID_STAT_OUTPUT_FLAG_PJC`
     - output_flag.pjc
   * - :term:`GRID_STAT_OUTPUT_FLAG_PRC`
     - output_flag.prc
   * - :term:`GRID_STAT_OUTPUT_FLAG_ECLV`
     - output_flag.eclv
   * - :term:`GRID_STAT_OUTPUT_FLAG_NBRCTC`
     - output_flag.nbrctc
   * - :term:`GRID_STAT_OUTPUT_FLAG_NBRCTS`
     - output_flag.nbrcts
   * - :term:`GRID_STAT_OUTPUT_FLAG_NBRCNT`
     - output_flag.nbrcnt
   * - :term:`GRID_STAT_OUTPUT_FLAG_GRAD`
     - output_flag.grad
   * - :term:`GRID_STAT_OUTPUT_FLAG_DMAP`
     - output_flag.dmap
   * - :term:`GRID_STAT_OUTPUT_FLAG_SEEPS`
     - output_flag.seeps

**${METPLUS_NC_PAIRS_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_LATLON`
     - nc_pairs_flag.latlon
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_RAW`
     - nc_pairs_flag.raw
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_DIFF`
     - nc_pairs_flag.diff
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_CLIMO`
     - nc_pairs_flag.climo
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_CLIMO_CDP`
     - nc_pairs_flag.climo_cdp
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_WEIGHT`
     - nc_pairs_flag.weight
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_NBRHD`
     - nc_pairs_flag.nbrhd
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_FOURIER`
     - nc_pairs_flag.fourier
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_GRADIENT`
     - nc_pairs_flag.gradient
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_DISTANCE_MAP`
     - nc_pairs_flag.distance_map
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_APPLY_MASK`
     - nc_pairs_flag.apply_mask
   * - :term:`GRID_STAT_NC_PAIRS_FLAG_SEEPS`
     - nc_pairs_flag.seeps

**${METPLUS_INTERP_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_INTERP_FIELD`
     - interp.field
   * - :term:`GRID_STAT_INTERP_VLD_THRESH`
     - interp.vld_thresh
   * - :term:`GRID_STAT_INTERP_SHAPE`
     - interp.shape
   * - :term:`GRID_STAT_INTERP_TYPE_METHOD`
     - interp.type.method
   * - :term:`GRID_STAT_INTERP_TYPE_WIDTH`
     - interp.type.width

**${METPLUS_NC_PAIRS_VAR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_NC_PAIRS_VAR_NAME`
     - nc_pairs_var_name

**${METPLUS_GRID_WEIGHT_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_GRID_WEIGHT_FLAG`
     - grid_weight_flag

**${METPLUS_HSS_EC_VALUE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_HSS_EC_VALUE`
     - hss_ec_value

**${METPLUS_DISTANCE_MAP_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_DISTANCE_MAP_BADDELEY_P`
     - distance_map.baddeley_p
   * - :term:`GRID_STAT_DISTANCE_MAP_BADDELEY_MAX_DIST`
     - distance_map.baddeley_max_dist
   * - :term:`GRID_STAT_DISTANCE_MAP_FOM_ALPHA`
     - distance_map.fom_alpha
   * - :term:`GRID_STAT_DISTANCE_MAP_ZHU_WEIGHT`
     - distance_map.zhu_weight
   * - :term:`GRID_STAT_DISTANCE_MAP_BETA_VALUE_N`
     - distance_map.beta_value(n)

**${METPLUS_FOURIER_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_FOURIER_WAVE_1D_BEG`
     - fourier.wave_1d_beg
   * - :term:`GRID_STAT_FOURIER_WAVE_1D_END`
     - fourier.wave_1d_end

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CENSOR_VAL`
     - censor_val

**${METPLUS_SEEPS_P1_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_SEEPS_P1_THRESH`
     - seeps_p1_thresh


.. _ioda2nc_wrapper:

IODA2NC
========

Description
-----------

Used to configure the MET tool ioda2nc

METplus Configuration
---------------------

| :term:`IODA2NC_INPUT_DIR`
| :term:`IODA2NC_INPUT_TEMPLATE`
| :term:`IODA2NC_OUTPUT_DIR`
| :term:`IODA2NC_OUTPUT_TEMPLATE`
| :term:`LOG_IODA2NC_VERBOSITY`
| :term:`IODA2NC_SKIP_IF_OUTPUT_EXISTS`
| :term:`IODA2NC_CONFIG_FILE`
| :term:`IODA2NC_FILE_WINDOW_BEG`
| :term:`IODA2NC_FILE_WINDOW_END`
| :term:`IODA2NC_VALID_BEG`
| :term:`IODA2NC_VALID_END`
| :term:`IODA2NC_NMSG`
| :term:`IODA2NC_MESSAGE_TYPE`
| :term:`IODA2NC_MESSAGE_TYPE_MAP`
| :term:`IODA2NC_MESSAGE_TYPE_GROUP_MAP`
| :term:`IODA2NC_STATION_ID`
| :term:`IODA2NC_OBS_WINDOW_BEG`
| :term:`IODA2NC_OBS_WINDOW_END`
| :term:`IODA2NC_MASK_GRID`
| :term:`IODA2NC_MASK_POLY`
| :term:`IODA2NC_ELEVATION_RANGE_BEG`
| :term:`IODA2NC_ELEVATION_RANGE_END`
| :term:`IODA2NC_LEVEL_RANGE_BEG`
| :term:`IODA2NC_LEVEL_RANGE_END`
| :term:`IODA2NC_OBS_VAR`
| :term:`IODA2NC_OBS_NAME_MAP`
| :term:`IODA2NC_METADATA_MAP`
| :term:`IODA2NC_MISSING_THRESH`
| :term:`IODA2NC_QUALITY_MARK_THRESH`
| :term:`IODA2NC_TIME_SUMMARY_FLAG`
| :term:`IODA2NC_TIME_SUMMARY_RAW_DATA`
| :term:`IODA2NC_TIME_SUMMARY_BEG`
| :term:`IODA2NC_TIME_SUMMARY_END`
| :term:`IODA2NC_TIME_SUMMARY_STEP`
| :term:`IODA2NC_TIME_SUMMARY_WIDTH`
| :term:`IODA2NC_TIME_SUMMARY_GRIB_CODE`
| :term:`IODA2NC_TIME_SUMMARY_OBS_VAR`
| :term:`IODA2NC_TIME_SUMMARY_TYPE`
| :term:`IODA2NC_TIME_SUMMARY_VLD_FREQ`
| :term:`IODA2NC_TIME_SUMMARY_VLD_THRESH`
| :term:`IODA2NC_CUSTOM_LOOP_LIST`
| :term:`IODA2NC_MET_CONFIG_OVERRIDES`

.. _ioda2nc-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/IODA2NCConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/IODA2NCConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/IODA2NCConfig_wrapped

**${METPLUS_MESSAGE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MESSAGE_TYPE`
     - message_type

**${METPLUS_MESSAGE_TYPE_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MESSAGE_TYPE_MAP`
     - message_type_map

**${METPLUS_MESSAGE_TYPE_GROUP_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MESSAGE_TYPE_GROUP_MAP`
     - message_type_group_map

**${METPLUS_STATION_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_STATION_ID`
     - station_id

**${METPLUS_OBS_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_OBS_WINDOW_BEG`
     - obs_window.beg
   * - :term:`IODA2NC_OBS_WINDOW_END`
     - obs_window.end

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MASK_GRID`
     - mask.grid
   * - :term:`IODA2NC_MASK_POLY`
     - mask.poly

**${METPLUS_ELEVATION_RANGE_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_ELEVATION_RANGE_BEG`
     - elevation_range.beg
   * - :term:`IODA2NC_ELEVATION_RANGE_END`
     - elevation_range.end

**${METPLUS_LEVEL_RANGE_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_LEVEL_RANGE_BEG`
     - level_range.beg
   * - :term:`IODA2NC_LEVEL_RANGE_END`
     - level_range.end

**${METPLUS_OBS_VAR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_OBS_VAR`
     - obs_var

**${METPLUS_OBS_NAME_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_OBS_NAME_MAP`
     - obs_name_map

**${METPLUS_METADATA_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_METADATA_MAP`
     - metadata_map

**${METPLUS_MISSING_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MISSING_THRESH`
     - missing_thresh

**${METPLUS_QUALITY_MARK_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_QUALITY_MARK_THRESH`
     - quality_mark_thresh

**${METPLUS_TIME_SUMMARY_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_TIME_SUMMARY_FLAG`
     - time_summary.flag
   * - :term:`IODA2NC_TIME_SUMMARY_RAW_DATA`
     - time_summary.raw_data
   * - :term:`IODA2NC_TIME_SUMMARY_BEG`
     - time_summary.beg
   * - :term:`IODA2NC_TIME_SUMMARY_END`
     - time_summary.end
   * - :term:`IODA2NC_TIME_SUMMARY_STEP`
     - time_summary.step
   * - :term:`IODA2NC_TIME_SUMMARY_WIDTH`
     - time_summary.width
   * - :term:`IODA2NC_TIME_SUMMARY_GRIB_CODE`
     - time_summary.grib_code
   * - :term:`IODA2NC_TIME_SUMMARY_OBS_VAR`
     - time_summary.obs_var
   * - :term:`IODA2NC_TIME_SUMMARY_TYPE`
     - time_summary.type
   * - :term:`IODA2NC_TIME_SUMMARY_VLD_FREQ`
     - time_summary.vld_freq
   * - :term:`IODA2NC_TIME_SUMMARY_VLD_THRESH`
     - time_summary.vld_thresh

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`IODA2NC_MET_CONFIG_OVERRIDES`
     - n/a


.. _met_db_load_wrapper:

METdbLoad
=========

Description
-----------

Used to call the met_db_load.py script from dtcenter/METdataio to load MET
output into a METviewer database.

METplus Configuration
---------------------

| :term:`MET_DB_LOAD_RUNTIME_FREQ`
| :term:`MET_DATA_DB_DIR`
| :term:`MET_DB_LOAD_XML_FILE`
| :term:`MET_DB_LOAD_REMOVE_TMP_XML`
| :term:`MET_DB_LOAD_MV_HOST`
| :term:`MET_DB_LOAD_MV_DATABASE`
| :term:`MET_DB_LOAD_MV_USER`
| :term:`MET_DB_LOAD_MV_PASSWORD`
| :term:`MET_DB_LOAD_MV_VERBOSE`
| :term:`MET_DB_LOAD_MV_INSERT_SIZE`
| :term:`MET_DB_LOAD_MV_MODE_HEADER_DB_CHECK`
| :term:`MET_DB_LOAD_MV_DROP_INDEXES`
| :term:`MET_DB_LOAD_MV_APPLY_INDEXES`
| :term:`MET_DB_LOAD_MV_GROUP`
| :term:`MET_DB_LOAD_MV_LOAD_STAT`
| :term:`MET_DB_LOAD_MV_LOAD_MODE`
| :term:`MET_DB_LOAD_MV_LOAD_MTD`
| :term:`MET_DB_LOAD_MV_LOAD_MPR`
| :term:`MET_DB_LOAD_INPUT_TEMPLATE`

.. _met_db_load-xml-conf:

XML Configuration
-----------------

Below is the XML template configuration file used for this wrapper. The wrapper
substitutes values from the METplus configuration file into this configuration
file. While it may appear that environment variables are used in the XML
template file, they are not actually environment variables. The wrapper
searches for these strings and substitutes the values as appropriate.

.. literalinclude:: ../../parm/use_cases/met_tool_wrapper/METdbLoad/METdbLoadConfig.xml

**${METPLUS_MV_HOST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_HOST`
     - <load_spec><connection><host>

**${METPLUS_MV_DATABASE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_DATABASE`
     - <load_spec><connection><database>

**${METPLUS_MV_USER}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_USER`
     - <load_spec><connection><user>

**${METPLUS_MV_PASSWORD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_PASSWORD`
     - <load_spec><connection><password>

**${METPLUS_MV_VERBOSE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_VERBOSE`
     - <load_spec><verbose>

**${METPLUS_MV_INSERT_SIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_INSERT_SIZE`
     - <load_spec><insert_size>

**${METPLUS_MV_MODE_HEADER_DB_CHECK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_MODE_HEADER_DB_CHECK`
     - <load_spec><mode_header_db_check>

**${METPLUS_MV_DROP_INDEXES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_DROP_INDEXES`
     - <load_spec><drop_indexes>

**${METPLUS_MV_APPLY_INDEXES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_APPLY_INDEXES`
     - <load_spec><apply_indexes>

**${METPLUS_MV_GROUP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_GROUP`
     - <load_spec><group>

**${METPLUS_MV_LOAD_STAT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_LOAD_STAT`
     - <load_spec><load_stat>

**${METPLUS_MV_LOAD_MODE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_LOAD_MODE`
     - <load_spec><load_mode>

**${METPLUS_MV_LOAD_MTD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_LOAD_MTD`
     - <load_spec><load_mtd>

**${METPLUS_MV_LOAD_MPR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_MV_LOAD_MPR`
     - <load_spec><load_mpr>

**${METPLUS_INPUT_PATHS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - XML Config File
   * - :term:`MET_DB_LOAD_INPUT_TEMPLATE`
     - <load_val><field name="dirs"><val>

.. _mode_wrapper:

MODE
====

Description
-----------

Used to configure the MET Method for Object-based Diagnostic Evaluation tool mode.

METplus Configuration
---------------------

| :term:`FCST_MODE_INPUT_DIR`
| :term:`OBS_MODE_INPUT_DIR`
| :term:`MODE_OUTPUT_DIR`
| :term:`FCST_MODE_INPUT_TEMPLATE`
| :term:`OBS_MODE_INPUT_TEMPLATE`
| :term:`MODE_OUTPUT_TEMPLATE`
| :term:`MODE_VERIFICATION_MASK_TEMPLATE`
| :term:`LOG_MODE_VERBOSITY`
| :term:`MODE_OUTPUT_PREFIX`
| :term:`MODE_REGRID_TO_GRID`
| :term:`MODE_REGRID_METHOD`
| :term:`MODE_REGRID_WIDTH`
| :term:`MODE_REGRID_VLD_THRESH`
| :term:`MODE_REGRID_SHAPE`
| :term:`MODE_REGRID_CONVERT`
| :term:`MODE_REGRID_CENSOR_THRESH`
| :term:`MODE_REGRID_CENSOR_VAL`
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
| :term:`MODE_DESC`
| :term:`MODE_MET_CONFIG_OVERRIDES`
| :term:`MODE_WEIGHT_CENTROID_DIST`
| :term:`MODE_WEIGHT_BOUNDARY_DIST`
| :term:`MODE_WEIGHT_CONVEX_HULL_DIST`
| :term:`MODE_WEIGHT_ANGLE_DIFF`
| :term:`MODE_WEIGHT_ASPECT_DIFF`
| :term:`MODE_WEIGHT_AREA_RATIO`
| :term:`MODE_WEIGHT_INT_AREA_RATIO`
| :term:`MODE_WEIGHT_CURVATURE_RATIO`
| :term:`MODE_WEIGHT_COMPLEXITY_RATIO`
| :term:`MODE_WEIGHT_INTEN_PERC_RATIO`
| :term:`MODE_WEIGHT_INTEN_PERC_VALUE`
| :term:`MODE_MASK_GRID`
| :term:`MODE_MASK_GRID_FLAG`
| :term:`MODE_MASK_POLY`
| :term:`MODE_MASK_POLY_FLAG`
| :term:`MODE_FCST_FILTER_ATTR_NAME`
| :term:`MODE_FCST_FILTER_ATTR_THRESH`
| :term:`MODE_FCST_CENSOR_THRESH`
| :term:`MODE_FCST_CENSOR_VAL`
| :term:`MODE_FCST_VLD_THRESH`
| :term:`MODE_OBS_FILTER_ATTR_NAME`
| :term:`MODE_OBS_FILTER_ATTR_THRESH`
| :term:`MODE_OBS_CENSOR_THRESH`
| :term:`MODE_OBS_CENSOR_VAL`
| :term:`MODE_OBS_VLD_THRESH`
| :term:`MODE_NC_PAIRS_FLAG_LATLON`
| :term:`MODE_NC_PAIRS_FLAG_RAW`
| :term:`MODE_NC_PAIRS_FLAG_OBJECT_RAW`
| :term:`MODE_NC_PAIRS_FLAG_OBJECT_ID`
| :term:`MODE_NC_PAIRS_FLAG_CLUSTER_ID`
| :term:`MODE_NC_PAIRS_FLAG_POLYLINES`
| :term:`MODE_MASK_MISSING_FLAG`
| :term:`MODE_MATCH_FLAG`
| :term:`MODE_MAX_CENTROID_DIST`
| :term:`MODE_TOTAL_INTEREST_THRESH`
| :term:`MODE_INTEREST_FUNCTION_CENTROID_DIST`
| :term:`MODE_INTEREST_FUNCTION_BOUNDARY_DIST`
| :term:`MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST`
| :term:`MODE_PS_PLOT_FLAG`
| :term:`MODE_CT_STATS_FLAG`
| :term:`FCST_MODE_IS_PROB`
| :term:`FCST_MODE_PROB_IN_GRIB_PDS`
| :term:`MODE_MULTIVAR_LOGIC`
| :term:`MODE_MULTIVAR_INTENSITY`
| :term:`FCST_MODE_VAR<n>_NAME`
| :term:`FCST_MODE_VAR<n>_LEVELS`
| :term:`FCST_MODE_VAR<n>_THRESH`
| :term:`FCST_MODE_VAR<n>_OPTIONS`
| :term:`MODE_FCST_FILE_TYPE`
| :term:`MODE_FCST_MULTIVAR_NAME`
| :term:`MODE_FCST_MULTIVAR_LEVEL`
| :term:`OBS_MODE_VAR<n>_NAME`
| :term:`OBS_MODE_VAR<n>_LEVELS`
| :term:`OBS_MODE_VAR<n>_THRESH`
| :term:`OBS_MODE_VAR<n>_OPTIONS`
| :term:`MODE_OBS_FILE_TYPE`
| :term:`MODE_OBS_MULTIVAR_NAME`
| :term:`MODE_OBS_MULTIVAR_LEVEL`
|

.. warning:: **DEPRECATED:**

   | :term:`MODE_OUT_DIR`
   | :term:`MODE_CONFIG`
   |

.. _mode-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/MODEConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/MODEConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/MODEConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_DESC`
     - desc

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBTYPE`
     - obtype

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_REGRID_SHAPE`
     - regrid.shape
   * - :term:`MODE_REGRID_METHOD`
     - regrid.method
   * - :term:`MODE_REGRID_WIDTH`
     - regrid.width
   * - :term:`MODE_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`MODE_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`MODE_REGRID_CONVERT`
     - regrid.convert
   * - :term:`MODE_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`MODE_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_GRID_RES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_GRID_RES`
     - grid_res

**${METPLUS_QUILT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_QUILT`
     - quilt

**${METPLUS_MULTIVAR_LOGIC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MULTIVAR_LOGIC`
     - multivar_logic

**${METPLUS_MULTIVAR_INTENSITY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MULTIVAR_INTENSITY`
     - multivar_intensity

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_FCST_CONV_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_CONV_RADIUS`
     - fcst.conv_radius

**${METPLUS_FCST_CONV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_CONV_THRESH`
     - fcst.conv_thresh

**${METPLUS_FCST_MERGE_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_MERGE_THRESH`
     - fcst.merge_thresh

**${METPLUS_FCST_MERGE_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_MERGE_FLAG`
     - fcst.merge_flag

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_FILE_TYPE`
     - fcst.file_type

**${METPLUS_FCST_MULTIVAR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_MULTIVAR_NAME`
     - fcst.multivar_name

**${METPLUS_FCST_MULTIVAR_LEVEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_MULTIVAR_LEVEL`
     - fcst.multivar_level


**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_CONV_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_MODE_CONV_RADIUS`
     - obs.conv_radius

**${METPLUS_OBS_CONV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_MODE_CONV_THRESH`
     - obs.conv_thresh

**${METPLUS_OBS_MERGE_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_MODE_MERGE_THRESH`
     - obs.merge_thresh

**${METPLUS_OBS_MERGE_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_MODE_MERGE_FLAG`
     - obs.merge_flag

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_FILE_TYPE`
     - obs.file_type

**${METPLUS_OBS_MULTIVAR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_MULTIVAR_NAME`
     - obs.multivar_name

**${METPLUS_OBS_MULTIVAR_LEVEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_MULTIVAR_LEVEL`
     - obs.multivar_level

**${METPLUS_MASK_POLY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MASK_POLY`
     - mask.poly

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_FCST_FILTER_ATTR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_FILTER_ATTR_NAME`
     - fcst.filter_attr_name

**${METPLUS_FCST_FILTER_ATTR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_FILTER_ATTR_THRESH`
     - fcst.filter_attr_thresh

**${METPLUS_FCST_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_CENSOR_THRESH`
     - fcst.censor_thresh

**${METPLUS_FCST_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_CENSOR_VAL`
     - fcst.censor_val

**${METPLUS_FCST_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_FCST_VLD_THRESH`
     - fcst.vld_thresh

**${METPLUS_OBS_FILTER_ATTR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_FILTER_ATTR_NAME`
     - obs.filter_attr_name

**${METPLUS_OBS_FILTER_ATTR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_FILTER_ATTR_THRESH`
     - obs.filter_attr_thresh

**${METPLUS_OBS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_CENSOR_THRESH`
     - obs.censor_thresh

**${METPLUS_OBS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_CENSOR_VAL`
     - obs.censor_val

**${METPLUS_OBS_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_OBS_VLD_THRESH`
     - obs.vld_thresh

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MASK_GRID`
     - mask.grid
   * - :term:`MODE_MASK_GRID_FLAG`
     - mask.grid_flag
   * - :term:`MODE_MASK_POLY`
     - mask.poly
   * - :term:`MODE_MASK_POLY_FLAG`
     - mask.poly_flag

**${METPLUS_MASK_MISSING_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MASK_MISSING_FLAG`
     - mask_missing_flag

**${METPLUS_MATCH_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MATCH_FLAG`
     - match_flag

**${METPLUS_WEIGHT_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_WEIGHT_CENTROID_DIST`
     - weight.centroid_dist
   * - :term:`MODE_WEIGHT_BOUNDARY_DIST`
     - weight.boundary_dist
   * - :term:`MODE_WEIGHT_CONVEX_HULL_DIST`
     - weight.convex_hull_dist
   * - :term:`MODE_WEIGHT_ANGLE_DIFF`
     - weight.angle_diff
   * - :term:`MODE_WEIGHT_ASPECT_DIFF`
     - weight.aspect_diff
   * - :term:`MODE_WEIGHT_AREA_RATIO`
     - weight.area_ratio
   * - :term:`MODE_WEIGHT_INT_AREA_RATIO`
     - weight.int_area_ratio
   * - :term:`MODE_WEIGHT_CURVATURE_RATIO`
     - weight.curvature_ratio
   * - :term:`MODE_WEIGHT_COMPLEXITY_RATIO`
     - weight.complexity_ratio
   * - :term:`MODE_WEIGHT_INTEN_PERC_RATIO`
     - weight.inten_perc_ratio
   * - :term:`MODE_WEIGHT_INTEN_PERC_VALUE`
     - weight.inten_perc_value

**${METPLUS_NC_PAIRS_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_NC_PAIRS_FLAG_LATLON`
     - nc_pairs_flag.latlon
   * - :term:`MODE_NC_PAIRS_FLAG_RAW`
     - nc_pairs_flag.raw
   * - :term:`MODE_NC_PAIRS_FLAG_OBJECT_RAW`
     - nc_pairs_flag.object_raw
   * - :term:`MODE_NC_PAIRS_FLAG_OBJECT_ID`
     - nc_pairs_flag.object_id
   * - :term:`MODE_NC_PAIRS_FLAG_CLUSTER_ID`
     - nc_pairs_flag.cluster_id
   * - :term:`MODE_NC_PAIRS_FLAG_POLYLINES`
     - nc_pairs_flag.polylines

**${METPLUS_MAX_CENTROID_DIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_MAX_CENTROID_DIST`
     - max_centroid_dist

**${METPLUS_INTEREST_FUNCTION_CENTROID_DIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_INTEREST_FUNCTION_CENTROID_DIST`
     - interest_function.centroid_dist

**${METPLUS_INTEREST_FUNCTION_BOUNDARY_DIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_INTEREST_FUNCTION_BOUNDARY_DIST`
     - interest_function.boundary_dist

**${METPLUS_INTEREST_FUNCTION_CONVEX_HULL_DIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST`
     - interest_function.convex_hull_dist

**${METPLUS_TOTAL_INTEREST_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_TOTAL_INTEREST_THRESH`
     - total_interest_thresh

**${METPLUS_PS_PLOT_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_PS_PLOT_FLAG`
     - ps_plot_flag

**${METPLUS_CT_STATS_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODE_CT_STATS_FLAG`
     - ct_stats_flag


.. _mtd_wrapper:

MTD
===

Description
-----------

Used to configure the MET MODE Time Domain tool mtd.  This tools follows objects through time and can also be used to track objects.

METplus Configuration
---------------------

| :term:`FCST_MTD_INPUT_DIR`
| :term:`OBS_MTD_INPUT_DIR`
| :term:`MTD_OUTPUT_DIR`
| :term:`FCST_MTD_INPUT_TEMPLATE`
| :term:`OBS_MTD_INPUT_TEMPLATE`
| :term:`FCST_MTD_INPUT_FILE_LIST`
| :term:`OBS_MTD_INPUT_FILE_LIST`
| :term:`MTD_OUTPUT_TEMPLATE`
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
| :term:`MTD_DESC`
| :term:`MTD_REGRID_TO_GRID`
| :term:`MTD_REGRID_METHOD`
| :term:`MTD_REGRID_WIDTH`
| :term:`MTD_REGRID_VLD_THRESH`
| :term:`MTD_REGRID_SHAPE`
| :term:`MTD_REGRID_CONVERT`
| :term:`MTD_REGRID_CENSOR_THRESH`
| :term:`MTD_REGRID_CENSOR_VAL`
| :term:`MTD_MET_CONFIG_OVERRIDES`
| :term:`FCST_MTD_IS_PROB`
| :term:`FCST_MTD_PROB_IN_GRIB_PDS`
| :term:`FCST_MTD_VAR<n>_NAME`
| :term:`FCST_MTD_VAR<n>_LEVELS`
| :term:`FCST_MTD_VAR<n>_THRESH`
| :term:`FCST_MTD_VAR<n>_OPTIONS`
| :term:`OBS_MTD_VAR<n>_NAME`
| :term:`OBS_MTD_VAR<n>_LEVELS`
| :term:`OBS_MTD_VAR<n>_THRESH`
| :term:`OBS_MTD_VAR<n>_OPTIONS`
|

.. warning:: **DEPRECATED:**

   | :term:`MTD_OUT_DIR`
   | :term:`MTD_CONFIG`
   | :term:`MTD_SINGLE_RUN_SRC`
   |

.. _mtd-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/MTDConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/MTDConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/MTDConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_DESC`
     - desc

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBTYPE`
     - obtype

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_REGRID_SHAPE`
     - regrid.shape
   * - :term:`MTD_REGRID_METHOD`
     - regrid.method
   * - :term:`MTD_REGRID_WIDTH`
     - regrid.width
   * - :term:`MTD_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`MTD_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`MTD_REGRID_CONVERT`
     - regrid.convert
   * - :term:`MTD_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`MTD_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_MTD_INPUT_DATATYPE`
     - fcst.file_type

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_FCST_CONV_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_FCST_CONV_RADIUS`
     - fcst.conv_radius

**${METPLUS_FCST_CONV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_FCST_CONV_THRESH`
     - fcst.conv_thresh

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_MTD_INPUT_DATATYPE`
     - obs.file_type

**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_CONV_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_OBS_CONV_RADIUS`
     - obs.conv_radius

**${METPLUS_OBS_CONV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_OBS_CONV_THRESH`
     - obs.conv_thresh

**${METPLUS_MIN_VOLUME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_MIN_VOLUME`
     - min_volume

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MTD_MET_CONFIG_OVERRIDES`
     - n/a

.. _pb2nc_wrapper:

PB2NC
=====

Description
-----------

The PB2NC wrapper is a Python script that encapsulates the behavior of
the MET pb2nc tool to convert prepBUFR files into netCDF.

METplus Configuration
---------------------

| :term:`PB2NC_INPUT_DIR`
| :term:`PB2NC_OUTPUT_DIR`
| :term:`PB2NC_INPUT_TEMPLATE`
| :term:`PB2NC_OUTPUT_TEMPLATE`
| :term:`PB2NC_SKIP_IF_OUTPUT_EXISTS`
| :term:`PB2NC_OFFSETS`
| :term:`PB2NC_INPUT_DATATYPE`
| :term:`PB2NC_CONFIG_FILE`
| :term:`PB2NC_MESSAGE_TYPE`
| :term:`PB2NC_STATION_ID`
| :term:`PB2NC_GRID`
| :term:`PB2NC_POLY`
| :term:`PB2NC_OBS_BUFR_VAR_LIST`
| :term:`PB2NC_TIME_SUMMARY_FLAG`
| :term:`PB2NC_TIME_SUMMARY_BEG`
| :term:`PB2NC_TIME_SUMMARY_END`
| :term:`PB2NC_TIME_SUMMARY_VAR_NAMES`
| :term:`PB2NC_TIME_SUMMARY_TYPES`
| :term:`PB2NC_OBS_WINDOW_BEGIN`
| :term:`PB2NC_OBS_WINDOW_END`
| :term:`PB2NC_VALID_BEGIN`
| :term:`PB2NC_VALID_END`
| :term:`PB2NC_CUSTOM_LOOP_LIST`
| :term:`PB2NC_MET_CONFIG_OVERRIDES`
| :term:`PB2NC_PB_REPORT_TYPE`
| :term:`PB2NC_LEVEL_RANGE_BEG`
| :term:`PB2NC_LEVEL_RANGE_END`
| :term:`PB2NC_LEVEL_CATEGORY`
| :term:`PB2NC_QUALITY_MARK_THRESH`
| :term:`PB2NC_OBS_BUFR_MAP`

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
   |

.. _pb2nc-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/PB2NCConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/PB2NCConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/PB2NCConfig_wrapped

**${METPLUS_MESSAGE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_MESSAGE_TYPE`
     - message_type

**${METPLUS_STATION_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_STATION_ID`
     - station_id

**${METPLUS_OBS_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_OBS_WINDOW_BEGIN`
     - obs_window.beg
   * - :term:`PB2NC_OBS_WINDOW_END`
     - obs_window.end

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_MASK_GRID`
     - mask.grid
   * - :term:`PB2NC_MASK_POLY`
     - mask.poly

.. note:: Since the default value in the MET config file for 'grid' is grid = [ "FULL" ];, setting GRID_STAT_MASK_GRID to an empty string will result in a value of grid = []; in the MET config file.

**${METPLUS_OBS_BUFR_VAR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_OBS_BUFR_VAR_LIST`
     - obs_bufr_var

**${METPLUS_TIME_SUMMARY_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_TIME_SUMMARY_FLAG`
     - time_summary.flag
   * - :term:`PB2NC_TIME_SUMMARY_RAW_DATA`
     - time_summary.raw_data
   * - :term:`PB2NC_TIME_SUMMARY_BEG`
     - time_summary.beg
   * - :term:`PB2NC_TIME_SUMMARY_END`
     - time_summary.end
   * - :term:`PB2NC_TIME_SUMMARY_STEP`
     - time_summary.step
   * - :term:`PB2NC_TIME_SUMMARY_WIDTH`
     - time_summary.width
   * - :term:`PB2NC_TIME_SUMMARY_GRIB_CODES`
     - time_summary.grib_code
   * - :term:`PB2NC_TIME_SUMMARY_VAR_NAMES`
     - time_summary.obs_var
   * - :term:`PB2NC_TIME_SUMMARY_TYPES`
     - time_summary.type
   * - :term:`PB2NC_TIME_SUMMARY_VALID_FREQ`
     - time_summary.vld_freq
   * - :term:`PB2NC_TIME_SUMMARY_VALID_THRESH`
     - time_summary.vld_thresh

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_PB_REPORT_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_PB_REPORT_TYPE`
     - pb_report_type

**${METPLUS_LEVEL_RANGE_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_LEVEL_RANGE_BEG`
     - level_range.beg
   * - :term:`PB2NC_LEVEL_RANGE_END`
     - level_range.end

**${METPLUS_LEVEL_CATEGORY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_LEVEL_CATEGORY`
     - level_category

**${METPLUS_QUALITY_MARK_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_QUALITY_MARK_THRESH`
     - quality_mark_thresh

**${METPLUS_OBS_BUFR_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PB2NC_OBS_BUFR_MAP`
     - obs_bufr_map

.. _pcp_combine_wrapper:

PCPCombine
==========

Description
-----------

The PCPCombine wrapper is a Python script that encapsulates the MET
PCPCombine tool. It provides the infrastructure to combine or extract
from files to build desired accumulations.

PCPCombine wrapper can be configured to process forecast and/or observation
data. Setting :term:`FCST_PCP_COMBINE_RUN` = True will process forecast data
and setting :term:`OBS_PCP_COMBINE_RUN` = True will process observation data.

PCPCombine wrapper can be configured to build a command for the sum, add, subtract,
and derive methods using :term:`FCST_PCP_COMBINE_METHOD` and/or
:term:`OBS_PCP_COMBINE_METHOD`. Each method executes logic to gather the
desired input files to build the command based on specific examples.

Accumulations
^^^^^^^^^^^^^

The desired accumulation to build is defined using
:term:`FCST_PCP_COMBINE_OUTPUT_ACCUM` or :term:`OBS_PCP_COMBINE_OUTPUT_ACCUM`.
The default units are hours unless otherwise specified.
The output field name can be set explicitly using
:term:`FCST_PCP_COMBINE_OUTPUT_NAME` or :term:`OBS_PCP_COMBINE_OUTPUT_NAME`.

For the ADD and DERIVE methods, the input accumulation(s) can be specified using
:term:`FCST_PCP_COMBINE_INPUT_ACCUMS` or :term:`OBS_PCP_COMBINE_INPUT_ACCUMS`.
The default units are hours unless otherwise specified.
This can be a list of accumulation amounts in order of preference.
If the remaining accumulation needed to build the desired accumulation is
less than the first accumulation, then the next value in the list will be used.
The name and level of the field to read for each input accumulation can be
specified with
:term:`FCST_PCP_COMBINE_INPUT_NAMES`/:term:`FCST_PCP_COMBINE_INPUT_LEVELS` or
:term:`OBS_PCP_COMBINE_INPUT_NAMES`/:term:`OBS_PCP_COMBINE_INPUT_LEVELS`.
These lists must be the same length as
:term:`FCST_PCP_COMBINE_INPUT_ACCUMS` or :term:`OBS_PCP_COMBINE_INPUT_ACCUMS`.

Constant Initialization Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the ADD and DERIVE methods, :term:`FCST_PCP_COMBINE_CONSTANT_INIT` or
:term:`OBS_PCP_COMBINE_CONSTANT_INIT` can be set to **True** to gather input
files that all contain the same initialization time.


User-Defined Commands
^^^^^^^^^^^^^^^^^^^^^

There are many ways to utilize PCPCombine that may not align with the logic
used to gather files. If this is the case, then the method can be set to
**USER_DEFINED** and the explicit command arguments can be specified using
:term:`FCST_PCP_COMBINE_COMMAND` or :term:`OBS_PCP_COMBINE_COMMAND`.
Other METplus configuration variables and filename template tags can be
referenced in the explicit command. Note that the path to the pcp_combine
executable and the output path should not be included in the command value.
The output path is controlled by
:term:`FCST_PCP_COMBINE_INPUT_TEMPLATE`/:term:`FCST_PCP_COMBINE_INPUT_DIR` or
:term:`OBS_PCP_COMBINE_INPUT_TEMPLATE`/:term:`OBS_PCP_COMBINE_INPUT_DIR` and
will automatically be added to the end of the command.


METplus Configuration
---------------------

| :term:`FCST_PCP_COMBINE_INPUT_DIR`
| :term:`FCST_PCP_COMBINE_OUTPUT_DIR`
| :term:`OBS_PCP_COMBINE_INPUT_DIR`
| :term:`OBS_PCP_COMBINE_OUTPUT_DIR`
| :term:`FCST_PCP_COMBINE_INPUT_TEMPLATE`
| :term:`FCST_PCP_COMBINE_OUTPUT_TEMPLATE`
| :term:`OBS_PCP_COMBINE_INPUT_TEMPLATE`
| :term:`OBS_PCP_COMBINE_OUTPUT_TEMPLATE`
| :term:`LOG_PCP_COMBINE_VERBOSITY`
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
| :term:`PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS`
| :term:`FCST_PCP_COMBINE_COMMAND`
| :term:`OBS_PCP_COMBINE_COMMAND`
| :term:`PCP_COMBINE_CUSTOM_LOOP_LIST`
| :term:`FCST_PCP_COMBINE_LOOKBACK`
| :term:`OBS_PCP_COMBINE_LOOKBACK`
| :term:`FCST_PCP_COMBINE_USE_ZERO_ACCUM`
| :term:`OBS_PCP_COMBINE_USE_ZERO_ACCUM`
| :term:`FCST_PCP_COMBINE_EXTRA_NAMES`
| :term:`FCST_PCP_COMBINE_EXTRA_LEVELS`
| :term:`FCST_PCP_COMBINE_EXTRA_OUTPUT_NAMES`
| :term:`OBS_PCP_COMBINE_EXTRA_NAMES`
| :term:`OBS_PCP_COMBINE_EXTRA_LEVELS`
| :term:`OBS_PCP_COMBINE_EXTRA_OUTPUT_NAMES`
| :term:`FCST_PCP_COMBINE_OUTPUT_ACCUM`
| :term:`FCST_PCP_COMBINE_OUTPUT_NAME`
| :term:`OBS_PCP_COMBINE_OUTPUT_ACCUM`
| :term:`OBS_PCP_COMBINE_OUTPUT_NAME`
|

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
   | :term:`FCST_PCP_COMBINE_DATA_INTERVAL`
   | :term:`OBS_PCP_COMBINE_DATA_INTERVAL`
   | :term:`FCST_PCP_COMBINE_TIMES_PER_FILE`
   | :term:`OBS_PCP_COMBINE_TIMES_PER_FILE`
   | :term:`FCST_PCP_COMBINE_IS_DAILY_FILE`
   | :term:`OBS_PCP_COMBINE_IS_DAILY_FILE`
   | :term:`FCST_PCP_COMBINE_DERIVE_LOOKBACK`
   | :term:`OBS_PCP_COMBINE_DERIVE_LOOKBACK`
   |

.. _plot_data_plane_wrapper:

PlotDataPlane
=============

Description
-----------

The PlotDataPlane wrapper is a Python script that encapsulates the MET
plot_data_plane tool. It provides the infrastructure to read in any input that
MET can read and plot them. This tool is often used to verify that the data
is mapped to the correct grid location.

Configuration
-------------

| :term:`PLOT_DATA_PLANE_INPUT_DIR`
| :term:`PLOT_DATA_PLANE_OUTPUT_DIR`
| :term:`PLOT_DATA_PLANE_INPUT_TEMPLATE`
| :term:`PLOT_DATA_PLANE_OUTPUT_TEMPLATE`
| :term:`PLOT_DATA_PLANE_FIELD_NAME`
| :term:`PLOT_DATA_PLANE_FIELD_LEVEL`
| :term:`PLOT_DATA_PLANE_FIELD_EXTRA`
| :term:`LOG_PLOT_DATA_PLANE_VERBOSITY`
| :term:`PLOT_DATA_PLANE_TITLE`
| :term:`PLOT_DATA_PLANE_COLOR_TABLE`
| :term:`PLOT_DATA_PLANE_RANGE_MIN_MAX`
| :term:`PLOT_DATA_PLANE_CONVERT_TO_IMAGE`
| :term:`PLOT_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS`

.. _plot_point_obs_wrapper:

PlotPointObs
============

Description
-----------

The PlotPointObs wrapper is a Python script that encapsulates the MET
plot_point_obs tool. It provides the infrastructure to read in any input that
MET can read and plot them.

Configuration
-------------

| :term:`PLOT_POINT_OBS_RUNTIME_FREQ`
| :term:`PLOT_POINT_OBS_INPUT_TEMPLATE`
| :term:`PLOT_POINT_OBS_INPUT_DIR`
| :term:`PLOT_POINT_OBS_GRID_INPUT_TEMPLATE`
| :term:`PLOT_POINT_OBS_GRID_INPUT_DIR`
| :term:`PLOT_POINT_OBS_OUTPUT_TEMPLATE`
| :term:`PLOT_POINT_OBS_OUTPUT_DIR`
| :term:`PLOT_POINT_OBS_SKIP_IF_OUTPUT_EXISTS`
| :term:`PLOT_POINT_OBS_TITLE`
| :term:`LOG_PLOT_POINT_OBS_VERBOSITY`
| :term:`PLOT_POINT_OBS_GRID_DATA_FIELD`
| :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_TO_GRID`
| :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_METHOD`
| :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_WIDTH`
| :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_VLD_THRESH`
| :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_SHAPE`
| :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLOR_TABLE`
| :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MIN`
| :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MAX`
| :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLORBAR_FLAG`
| :term:`PLOT_POINT_OBS_MSG_TYP`
| :term:`PLOT_POINT_OBS_SID_INC`
| :term:`PLOT_POINT_OBS_SID_EXC`
| :term:`PLOT_POINT_OBS_OBS_VAR`
| :term:`PLOT_POINT_OBS_OBS_GC`
| :term:`PLOT_POINT_OBS_OBS_QUALITY`
| :term:`PLOT_POINT_OBS_VALID_BEG`
| :term:`PLOT_POINT_OBS_VALID_END`
| :term:`PLOT_POINT_OBS_LAT_THRESH`
| :term:`PLOT_POINT_OBS_LON_THRESH`
| :term:`PLOT_POINT_OBS_ELV_THRESH`
| :term:`PLOT_POINT_OBS_HGT_THRESH`
| :term:`PLOT_POINT_OBS_PRS_THRESH`
| :term:`PLOT_POINT_OBS_OBS_THRESH`
| :term:`PLOT_POINT_OBS_CENSOR_THRESH`
| :term:`PLOT_POINT_OBS_CENSOR_VAL`
| :term:`PLOT_POINT_OBS_DOTSIZE`
| :term:`PLOT_POINT_OBS_LINE_COLOR`
| :term:`PLOT_POINT_OBS_LINE_WIDTH`
| :term:`PLOT_POINT_OBS_FILL_COLOR`
| :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_FLAG`
| :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_COLOR_TABLE`
| :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MIN`
| :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MAX`
| :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_COLORBAR_FLAG`
| :term:`PLOT_POINT_OBS_POINT_DATA`
| :term:`PLOT_POINT_OBS_MET_CONFIG_OVERRIDES`


.. _plot-point-obs-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/PlotPointObsConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/PlotPointObsConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/PlotPointObsConfig_wrapped

**${METPLUS_GRID_DATA_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_GRID_DATA_FIELD`
     - grid_data.field
   * - :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_TO_GRID`
     - grid_data.regrid.to_grid
   * - :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_METHOD`
     - grid_data.regrid.method
   * - :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_WIDTH`
     - grid_data.regrid.width
   * - :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_VLD_THRESH`
     - grid_data.regrid.vld_thresh
   * - :term:`PLOT_POINT_OBS_GRID_DATA_REGRID_SHAPE`
     - grid_data.regrid.shape
   * - :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLOR_TABLE`
     - grid_data.grid_plot_info.color_table
   * - :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MIN`
     - grid_data.grid_plot_info.plot_min
   * - :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_PLOT_MAX`
     - grid_data.grid_plot_info.plot_max
   * - :term:`PLOT_POINT_OBS_GRID_DATA_GRID_PLOT_INFO_COLORBAR_FLAG`
     - grid_data.grid_plot_info.colorbar_flag

**${METPLUS_MSG_TYP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_MSG_TYP`
     - msg_typ

**${METPLUS_SID_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_SID_INC`
     - sid_inc

**${METPLUS_SID_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_SID_EXC`
     - sid_exc

**${METPLUS_OBS_VAR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_OBS_VAR`
     - obs_var

**${METPLUS_OBS_GC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_OBS_GC`
     - obs_gc

**${METPLUS_OBS_QUALITY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_OBS_QUALITY`
     - obs_quality

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_VALID_END`
     - valid_end

**${METPLUS_LAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_LAT_THRESH`
     - lat_thresh

**${METPLUS_LON_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_LON_THRESH`
     - lon_thresh

**${METPLUS_ELV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_ELV_THRESH`
     - elv_thresh

**${METPLUS_HGT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_HGT_THRESH`
     - hgt_thresh

**${METPLUS_PRS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_PRS_THRESH`
     - prs_thresh

**${METPLUS_OBS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_OBS_THRESH`
     - obs_thresh

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_CENSOR_VAL`
     - censor_val

**${METPLUS_DOTSIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_DOTSIZE`
     - dotsize

**${METPLUS_LINE_COLOR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_LINE_COLOR`
     - line_color

**${METPLUS_LINE_WIDTH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_LINE_WIDTH`
     - line_width

**${METPLUS_FILL_COLOR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_FILL_COLOR`
     - fill_color

**${METPLUS_FILL_PLOT_INFO_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_FLAG`
     - fill_plot_info.flag
   * - :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_COLOR_TABLE`
     - fill_plot_info.color_table
   * - :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MIN`
     - fill_plot_info.plot_min
   * - :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_PLOT_MAX`
     - fill_plot_info.plot_max
   * - :term:`PLOT_POINT_OBS_FILL_PLOT_INFO_COLORBAR_FLAG`
     - fill_plot_info.colorbar_flag

**${METPLUS_POINT_DATA}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`PLOT_POINT_OBS_POINT_DATA`
     - point_data


.. _point2grid_wrapper:

Point2Grid
==========

Description
-----------

The Point2Grid wrapper is a Python script that encapsulates the MET
point2grid tool. It provides the infrastructure to read in point observations
and place them on a grid

METplus Configuration
---------------------

| :term:`POINT2GRID_INPUT_DIR`
| :term:`POINT2GRID_OUTPUT_DIR`
| :term:`POINT2GRID_INPUT_TEMPLATE`
| :term:`POINT2GRID_OUTPUT_TEMPLATE`
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
|

.. _point_stat_wrapper:

PointStat
=========

Description
-----------

The PointStat wrapper is a Python script that encapsulates the MET
point_stat tool. It provides the infrastructure to read in gridded model
data and netCDF point observation data to perform grid-to-point
(grid-to-obs) verification.

Configuration
-------------

| :term:`FCST_POINT_STAT_INPUT_DIR`
| :term:`OBS_POINT_STAT_INPUT_DIR`
| :term:`POINT_STAT_OUTPUT_DIR`
| :term:`FCST_POINT_STAT_INPUT_TEMPLATE`
| :term:`OBS_POINT_STAT_INPUT_TEMPLATE`
| :term:`POINT_STAT_VERIFICATION_MASK_TEMPLATE`
| :term:`POINT_STAT_OUTPUT_PREFIX`
| :term:`LOG_POINT_STAT_VERBOSITY`
| :term:`POINT_STAT_OFFSETS`
| :term:`FCST_POINT_STAT_INPUT_DATATYPE`
| :term:`OBS_POINT_STAT_INPUT_DATATYPE`
| :term:`POINT_STAT_FCST_FILE_TYPE`
| :term:`POINT_STAT_OBS_FILE_TYPE`
| :term:`POINT_STAT_CONFIG_FILE`
| :term:`MODEL`
| :term:`POINT_STAT_REGRID_TO_GRID`
| :term:`POINT_STAT_REGRID_METHOD`
| :term:`POINT_STAT_REGRID_WIDTH`
| :term:`POINT_STAT_REGRID_VLD_THRESH`
| :term:`POINT_STAT_REGRID_SHAPE`
| :term:`POINT_STAT_REGRID_CONVERT`
| :term:`POINT_STAT_REGRID_CENSOR_THRESH`
| :term:`POINT_STAT_REGRID_CENSOR_VAL`
| :term:`POINT_STAT_MASK_GRID`
| :term:`POINT_STAT_MASK_POLY`
| :term:`POINT_STAT_MASK_SID`
| :term:`POINT_STAT_MASK_LLPNT`
| :term:`POINT_STAT_MESSAGE_TYPE`
| :term:`POINT_STAT_CUSTOM_LOOP_LIST`
| :term:`POINT_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`POINT_STAT_DESC`
| :term:`POINT_STAT_MET_CONFIG_OVERRIDES`
| :term:`POINT_STAT_CLIMO_CDF_BINS`
| :term:`POINT_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`POINT_STAT_CLIMO_CDF_WRITE_BINS`
| :term:`POINT_STAT_CLIMO_CDF_DIRECT_PROB`
| :term:`POINT_STAT_OBS_QUALITY_INC`
| :term:`POINT_STAT_OBS_QUALITY_EXC`
| :term:`POINT_STAT_OUTPUT_FLAG_FHO`
| :term:`POINT_STAT_OUTPUT_FLAG_CTC`
| :term:`POINT_STAT_OUTPUT_FLAG_CTS`
| :term:`POINT_STAT_OUTPUT_FLAG_MCTC`
| :term:`POINT_STAT_OUTPUT_FLAG_MCTS`
| :term:`POINT_STAT_OUTPUT_FLAG_CNT`
| :term:`POINT_STAT_OUTPUT_FLAG_SL1L2`
| :term:`POINT_STAT_OUTPUT_FLAG_SAL1L2`
| :term:`POINT_STAT_OUTPUT_FLAG_VL1L2`
| :term:`POINT_STAT_OUTPUT_FLAG_VAL1L2`
| :term:`POINT_STAT_OUTPUT_FLAG_VCNT`
| :term:`POINT_STAT_OUTPUT_FLAG_PCT`
| :term:`POINT_STAT_OUTPUT_FLAG_PSTD`
| :term:`POINT_STAT_OUTPUT_FLAG_PJC`
| :term:`POINT_STAT_OUTPUT_FLAG_PRC`
| :term:`POINT_STAT_OUTPUT_FLAG_ECNT`
| :term:`POINT_STAT_OUTPUT_FLAG_ORANK`
| :term:`POINT_STAT_OUTPUT_FLAG_RPS`
| :term:`POINT_STAT_OUTPUT_FLAG_ECLV`
| :term:`POINT_STAT_OUTPUT_FLAG_MPR`
| :term:`POINT_STAT_OUTPUT_FLAG_SEEPS`
| :term:`POINT_STAT_OUTPUT_FLAG_SEEPS_MPR`
| :term:`POINT_STAT_INTERP_VLD_THRESH`
| :term:`POINT_STAT_INTERP_SHAPE`
| :term:`POINT_STAT_INTERP_TYPE_METHOD`
| :term:`POINT_STAT_INTERP_TYPE_WIDTH`
| :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`
| :term:`POINT_STAT_CLIMO_MEAN_VAR<n>_NAME`
| :term:`POINT_STAT_CLIMO_MEAN_VAR<n>_LEVELS`
| :term:`POINT_STAT_CLIMO_MEAN_VAR<n>_OPTIONS`
| :term:`POINT_STAT_CLIMO_MEAN_FIELD`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`POINT_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`POINT_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`POINT_STAT_CLIMO_MEAN_USE_FCST`
| :term:`POINT_STAT_CLIMO_MEAN_USE_OBS`
| :term:`POINT_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`POINT_STAT_CLIMO_STDEV_VAR<n>_NAME`
| :term:`POINT_STAT_CLIMO_STDEV_VAR<n>_LEVELS`
| :term:`POINT_STAT_CLIMO_STDEV_VAR<n>_OPTIONS`
| :term:`POINT_STAT_CLIMO_STDEV_FIELD`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`POINT_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`POINT_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`POINT_STAT_CLIMO_STDEV_USE_FCST`
| :term:`POINT_STAT_CLIMO_STDEV_USE_OBS`
| :term:`POINT_STAT_HSS_EC_VALUE`
| :term:`POINT_STAT_HIRA_FLAG`
| :term:`POINT_STAT_HIRA_WIDTH`
| :term:`POINT_STAT_HIRA_VLD_THRESH`
| :term:`POINT_STAT_HIRA_COV_THRESH`
| :term:`POINT_STAT_HIRA_SHAPE`
| :term:`POINT_STAT_HIRA_PROB_CAT_THRESH`
| :term:`POINT_STAT_MESSAGE_TYPE_GROUP_MAP`
| :term:`FCST_POINT_STAT_IS_PROB`
| :term:`FCST_POINT_STAT_PROB_IN_GRIB_PDS`
| :term:`FCST_POINT_STAT_WINDOW_BEGIN`
| :term:`FCST_POINT_STAT_WINDOW_END`
| :term:`OBS_POINT_STAT_WINDOW_BEGIN`
| :term:`OBS_POINT_STAT_WINDOW_END`
| :term:`POINT_STAT_NEIGHBORHOOD_WIDTH`
| :term:`POINT_STAT_NEIGHBORHOOD_SHAPE`
| :term:`FCST_POINT_STAT_VAR<n>_NAME`
| :term:`FCST_POINT_STAT_VAR<n>_LEVELS`
| :term:`FCST_POINT_STAT_VAR<n>_THRESH`
| :term:`FCST_POINT_STAT_VAR<n>_OPTIONS`
| :term:`OBS_POINT_STAT_VAR<n>_NAME`
| :term:`OBS_POINT_STAT_VAR<n>_LEVELS`
| :term:`OBS_POINT_STAT_VAR<n>_THRESH`
| :term:`OBS_POINT_STAT_VAR<n>_OPTIONS`
| :term:`POINT_STAT_OBS_VALID_BEG`
| :term:`POINT_STAT_OBS_VALID_END`
| :term:`POINT_STAT_SEEPS_P1_THRESH`
|

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
   | :term:`POINT_STAT_CLIMO_MEAN_INPUT_DIR`
   | :term:`POINT_STAT_CLIMO_STDEV_INPUT_DIR`
   | :term:`POINT_STAT_CLIMO_MEAN_INPUT_TEMPLATE`
   | :term:`POINT_STAT_CLIMO_STDEV_INPUT_TEMPLATE`
   |

.. _point-stat-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/PointStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/PointStatConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/PointStatConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` -or- :term:`POINT_STAT_DESC`
     - desc

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_REGRID_SHAPE`
     - regrid.shape
   * - :term:`POINT_STAT_REGRID_METHOD`
     - regrid.method
   * - :term:`POINT_STAT_REGRID_WIDTH`
     - regrid.width
   * - :term:`POINT_STAT_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`POINT_STAT_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`POINT_STAT_REGRID_CONVERT`
     - regrid.convert
   * - :term:`POINT_STAT_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`POINT_STAT_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_FCST_FILE_TYPE`
     - fcst.file_type

**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - obs.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - obs.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - obs.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OBS_FILE_TYPE`
     - obs.file_type

**${METPLUS_MESSAGE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MESSAGE_TYPE`
     - message_type


**${METPLUS_CLIMO_MEAN_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`
     - climo_mean.file_name
   * - :term:`POINT_STAT_CLIMO_MEAN_FIELD`
     - climo_mean.field
   * - :term:`POINT_STAT_CLIMO_MEAN_REGRID_METHOD`
     - climo_mean.regrid.method
   * - :term:`POINT_STAT_CLIMO_MEAN_REGRID_WIDTH`
     - climo_mean.regrid.width
   * - :term:`POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
     - climo_mean.regrid.vld_thresh
   * - :term:`POINT_STAT_CLIMO_MEAN_REGRID_SHAPE`
     - climo_mean.regrid.shape
   * - :term:`POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
     - climo_mean.time_interp_method
   * - :term:`POINT_STAT_CLIMO_MEAN_MATCH_MONTH`
     - climo_mean.match_month
   * - :term:`POINT_STAT_CLIMO_MEAN_DAY_INTERVAL`
     - climo_mean.day_interval
   * - :term:`POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL`
     - climo_mean.hour_interval

**${METPLUS_CLIMO_STDEV_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_CLIMO_STDEV_FILE_NAME`
     - climo_stdev.file_name
   * - :term:`POINT_STAT_CLIMO_STDEV_FIELD`
     - climo_stdev.field
   * - :term:`POINT_STAT_CLIMO_STDEV_REGRID_METHOD`
     - climo_stdev.regrid.method
   * - :term:`POINT_STAT_CLIMO_STDEV_REGRID_WIDTH`
     - climo_stdev.regrid.width
   * - :term:`POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
     - climo_stdev.regrid.vld_thresh
   * - :term:`POINT_STAT_CLIMO_STDEV_REGRID_SHAPE`
     - climo_stdev.regrid.shape
   * - :term:`POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
     - climo_stdev.time_interp_method
   * - :term:`POINT_STAT_CLIMO_STDEV_MATCH_MONTH`
     - climo_stdev.match_month
   * - :term:`POINT_STAT_CLIMO_STDEV_DAY_INTERVAL`
     - climo_stdev.day_interval
   * - :term:`POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL`
     - climo_stdev.hour_interval


**${METPLUS_OBS_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_WINDOW_BEGIN`
     - obs_window.beg
   * - :term:`OBS_WINDOW_END`
     - obs_window.end

**${METPLUS_MASK_GRID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MASK_GRID`
     - mask.grid

**${METPLUS_MASK_POLY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MASK_POLY`
     - mask.poly

**${METPLUS_MASK_SID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MASK_SID`
     - mask.sid

**${METPLUS_MASK_LLPNT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MASK_LLPNT`
     - mask.llpnt


**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_CLIMO_CDF_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_CLIMO_CDF_BINS`
     - climo_cdf.cdf_bins
   * - :term:`POINT_STAT_CLIMO_CDF_CENTER_BINS`
     - climo_cdf.center_bins
   * - :term:`POINT_STAT_CLIMO_CDF_WRITE_BINS`
     - climo_cdf.write_bins
   * - :term:`POINT_STAT_CLIMO_CDF_DIRECT_PROB`
     - climo_cdf.direct_prob

**${METPLUS_OBS_QUALITY_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OBS_QUALITY_INC`
     - obs_quality_inc

**${METPLUS_OBS_QUALITY_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OBS_QUALITY_EXC`
     - obs_quality_exc

**${METPLUS_OUTPUT_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OUTPUT_FLAG_FHO`
     - output_flag.fho
   * - :term:`POINT_STAT_OUTPUT_FLAG_CTC`
     - output_flag.ctc
   * - :term:`POINT_STAT_OUTPUT_FLAG_CTS`
     - output_flag.cts
   * - :term:`POINT_STAT_OUTPUT_FLAG_MCTC`
     - output_flag.mctc
   * - :term:`POINT_STAT_OUTPUT_FLAG_MCTS`
     - output_flag.mcts
   * - :term:`POINT_STAT_OUTPUT_FLAG_CNT`
     - output_flag.cnt
   * - :term:`POINT_STAT_OUTPUT_FLAG_SL1L2`
     - output_flag.sl1l2
   * - :term:`POINT_STAT_OUTPUT_FLAG_SAL1L2`
     - output_flag.sal1l2
   * - :term:`POINT_STAT_OUTPUT_FLAG_VL1L2`
     - output_flag.vl1l2
   * - :term:`POINT_STAT_OUTPUT_FLAG_VAL1L2`
     - output_flag.val1l2
   * - :term:`POINT_STAT_OUTPUT_FLAG_VCNT`
     - output_flag.vcnt
   * - :term:`POINT_STAT_OUTPUT_FLAG_PCT`
     - output_flag.pct
   * - :term:`POINT_STAT_OUTPUT_FLAG_PSTD`
     - output_flag.pstd
   * - :term:`POINT_STAT_OUTPUT_FLAG_PJC`
     - output_flag.pjc
   * - :term:`POINT_STAT_OUTPUT_FLAG_PRC`
     - output_flag.prc
   * - :term:`POINT_STAT_OUTPUT_FLAG_ECNT`
     - output_flag.ecnt
   * - :term:`POINT_STAT_OUTPUT_FLAG_ORANK`
     - output_flag.orank
   * - :term:`POINT_STAT_OUTPUT_FLAG_RPS`
     - output_flag.rps
   * - :term:`POINT_STAT_OUTPUT_FLAG_ECLV`
     - output_flag.eclv
   * - :term:`POINT_STAT_OUTPUT_FLAG_MPR`
     - output_flag.mpr
   * - :term:`POINT_STAT_OUTPUT_FLAG_SEEPS`
     - output_flag.seeps
   * - :term:`POINT_STAT_OUTPUT_FLAG_SEEPS_MPR`
     - output_flag.seeps_mpr

**${METPLUS_INTERP_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_INTERP_VLD_THRESH`
     - interp.vld_thresh
   * - :term:`POINT_STAT_INTERP_SHAPE`
     - interp.shape
   * - :term:`POINT_STAT_INTERP_TYPE_METHOD`
     - interp.type.method
   * - :term:`POINT_STAT_INTERP_TYPE_WIDTH`
     - interp.type.width

**${METPLUS_HSS_EC_VALUE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_HSS_EC_VALUE`
     - hss_ec_value

**${METPLUS_HIRA_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_HIRA_FLAG`
     - hira.flag
   * - :term:`POINT_STAT_HIRA_WIDTH`
     - hira.width
   * - :term:`POINT_STAT_HIRA_VLD_THRESH`
     - hira.vld_thresh
   * - :term:`POINT_STAT_HIRA_COV_THRESH`
     - hira.cov_thresh
   * - :term:`POINT_STAT_HIRA_SHAPE`
     - hira.shape
   * - :term:`POINT_STAT_HIRA_PROB_CAT_THRESH`
     - hira.prob_cat_thresh

**${METPLUS_MESSAGE_TYPE_GROUP_MAP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_MESSAGE_TYPE_GROUP_MAP`
     - message_type_group_map

**${METPLUS_SEEPS_P1_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_SEEPS_P1_THRESH`
     - seeps_p1_thresh


.. _py_embed_ingest_wrapper:

PyEmbedIngest
=============

Description
-----------

Used to configure the PyEmbedIngest wrapper that runs RegridDataPlane to convert data using python embedding scripts into NetCDF so it can be read by the MET tools.

METplus Configuration
---------------------

| :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`
| :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`
| :term:`PY_EMBED_INGEST_<n>_SCRIPT`
| :term:`PY_EMBED_INGEST_<n>_TYPE`
| :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`
| :term:`PY_EMBED_INGEST_CUSTOM_LOOP_LIST`
| :term:`PY_EMBED_INGEST_<n>_OUTPUT_FIELD_NAME`
| :term:`PY_EMBED_INGEST_SKIP_IF_OUTPUT_EXISTS`
|

.. warning:: **DEPRECATED:**

    | :term:`CUSTOM_INGEST_<n>_OUTPUT_DIR`
    | :term:`CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE`
    | :term:`CUSTOM_INGEST_<n>_SCRIPT`
    | :term:`CUSTOM_INGEST_<n>_TYPE`
    | :term:`CUSTOM_INGEST_<n>_OUTPUT_GRID`
    |

.. _regrid_data_plane_wrapper:

RegridDataPlane
===============

Description
-----------

Used to configure the MET tool regrid_data_plane which can be used to change projections of a grid with user configurable interpolation choices.  It can also be used to convert GRIB1 and GRIB2 files into netcdf files if desired.

METplus Configuration
---------------------

| :term:`FCST_REGRID_DATA_PLANE_INPUT_DIR`
| :term:`OBS_REGRID_DATA_PLANE_INPUT_DIR`
| :term:`FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE`
| :term:`FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`
| :term:`FCST_REGRID_DATA_PLANE_TEMPLATE`
| :term:`OBS_REGRID_DATA_PLANE_TEMPLATE`
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
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME`
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL`
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME`
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME`
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL`
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME`
|

.. warning:: **DEPRECATED:**

   | :term:`VERIFICATION_GRID`
   |

.. _series_analysis_wrapper:

SeriesAnalysis
==============

Description
-----------

The SeriesAnalysis wrapper is used to find files and build a command that calls
the MET tool SeriesAnalysis. It can be configured to process ranges of inputs,
i.e. once for all files, once for each forecast lead (using , once for a group of
forecast leads, once for each initialization time, etc. with the
:term:`SERIES_ANALYSIS_RUNTIME_FREQ` variable.
Optionally, a .tcst file generated by TCStat can be provided to allow
filtering by storm ID (see :term:`SERIES_ANALYSIS_RUN_ONCE_PER_STORM_ID`).
Images of the output data can also optionally be generated as well as animated
gif images (See
:term:`SERIES_ANALYSIS_GENERATE_PLOTS` and
:term:`SERIES_ANALYSIS_GENERATE_ANIMATIONS`)

METplus Configuration
---------------------

| :term:`LOG_SERIES_ANALYSIS_VERBOSITY`
| :term:`SERIES_ANALYSIS_CONFIG_FILE`
| :term:`SERIES_ANALYSIS_RUNTIME_FREQ`
| :term:`SERIES_ANALYSIS_RUN_ONCE_PER_STORM_ID`
| :term:`SERIES_ANALYSIS_BACKGROUND_MAP`
| :term:`SERIES_ANALYSIS_REGRID_TO_GRID`
| :term:`SERIES_ANALYSIS_REGRID_METHOD`
| :term:`SERIES_ANALYSIS_REGRID_WIDTH`
| :term:`SERIES_ANALYSIS_REGRID_VLD_THRESH`
| :term:`SERIES_ANALYSIS_REGRID_SHAPE`
| :term:`SERIES_ANALYSIS_REGRID_CONVERT`
| :term:`SERIES_ANALYSIS_REGRID_CENSOR_THRESH`
| :term:`SERIES_ANALYSIS_REGRID_CENSOR_VAL`
| :term:`SERIES_ANALYSIS_STAT_LIST`
| :term:`SERIES_ANALYSIS_IS_PAIRED`
| :term:`SERIES_ANALYSIS_CUSTOM_LOOP_LIST`
| :term:`SERIES_ANALYSIS_SKIP_IF_OUTPUT_EXISTS`
| :term:`SERIES_ANALYSIS_GENERATE_PLOTS` (Optional)
| :term:`SERIES_ANALYSIS_GENERATE_ANIMATIONS` (Optional)
| :term:`PLOT_DATA_PLANE_TITLE` (Optional)
| :term:`LEAD_SEQ_\<n\>` (Optional)
| :term:`LEAD_SEQ_<n>_LABEL` (Optional)
| :term:`SERIES_ANALYSIS_DESC`
| :term:`SERIES_ANALYSIS_CAT_THRESH`
| :term:`SERIES_ANALYSIS_VLD_THRESH`
| :term:`SERIES_ANALYSIS_BLOCK_SIZE`
| :term:`SERIES_ANALYSIS_CTS_LIST`
| :term:`FCST_SERIES_ANALYSIS_PROB_THRESH`
| :term:`SERIES_ANALYSIS_MET_CONFIG_OVERRIDES`
| :term:`FCST_SERIES_ANALYSIS_INPUT_DIR`
| :term:`OBS_SERIES_ANALYSIS_INPUT_DIR`
| :term:`BOTH_SERIES_ANALYSIS_INPUT_DIR`
| :term:`SERIES_ANALYSIS_TC_STAT_INPUT_DIR`
| :term:`SERIES_ANALYSIS_OUTPUT_DIR`
| :term:`FCST_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`OBS_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`FCST_SERIES_ANALYSIS_INPUT_FILE_LIST`
| :term:`OBS_SERIES_ANALYSIS_INPUT_FILE_LIST`
| :term:`BOTH_SERIES_ANALYSIS_INPUT_FILE_LIST`
| :term:`SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_OUTPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_VAR<n>_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_VAR<n>_LEVELS`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_VAR<n>_OPTIONS`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_FIELD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_TYPE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_USE_FCST`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_USE_OBS`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_VAR<n>_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_VAR<n>_LEVELS`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_VAR<n>_OPTIONS`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_FIELD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_TYPE`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_USE_FCST`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_USE_OBS`
| :term:`SERIES_ANALYSIS_CLIMO_CDF_BINS`
| :term:`SERIES_ANALYSIS_CLIMO_CDF_CENTER_BINS`
| :term:`SERIES_ANALYSIS_CLIMO_CDF_DIRECT_PROB`
| :term:`SERIES_ANALYSIS_HSS_EC_VALUE`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_FHO`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_CTC`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_CTS`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_MCTC`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_MCTS`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_CNT`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_SL1L2`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_SAL1L2`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_PCT`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_PSTD`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_PJC`
| :term:`SERIES_ANALYSIS_OUTPUT_STATS_PRC`
| :term:`FCST_SERIES_ANALYSIS_CAT_THRESH`
| :term:`OBS_SERIES_ANALYSIS_CAT_THRESH`
| :term:`FCST_SERIES_ANALYSIS_IS_PROB`
| :term:`FCST_SERIES_ANALYSIS_PROB_IN_GRIB_PDS`
| :term:`SERIES_ANALYSIS_MASK_GRID`
| :term:`SERIES_ANALYSIS_MASK_POLY`
|

.. warning:: **DEPRECATED:**

   | :term:`SERIES_ANALYSIS_CLIMO_MEAN_INPUT_DIR`
   | :term:`SERIES_ANALYSIS_CLIMO_STDEV_INPUT_DIR`
   | :term:`SERIES_ANALYSIS_CLIMO_MEAN_INPUT_TEMPLATE`
   | :term:`SERIES_ANALYSIS_CLIMO_STDEV_INPUT_TEMPLATE`

.. _series-analysis-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/SeriesAnalysisConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/SeriesAnalysisConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/SeriesAnalysisConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` -or- :term:`SERIES_ANALYSIS_DESC`
     - desc

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBTYPE`
     - obtype

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_REGRID_SHAPE`
     - regrid.shape
   * - :term:`SERIES_ANALYSIS_REGRID_METHOD`
     - regrid.method
   * - :term:`SERIES_ANALYSIS_REGRID_WIDTH`
     - regrid.width
   * - :term:`SERIES_ANALYSIS_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`SERIES_ANALYSIS_REGRID_TO_GRID`
     - regrid.to_grid
   * - :term:`SERIES_ANALYSIS_REGRID_CONVERT`
     - regrid.convert
   * - :term:`SERIES_ANALYSIS_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`SERIES_ANALYSIS_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_CAT_THRESH`
     - cat_thresh

**${METPLUS_FCST_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_SERIES_ANALYSIS_INPUT_DATATYPE`
     - fcst.file_type

**${METPLUS_FCST_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`FCST_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`FCST_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`FCST_VAR<n>_OPTIONS`
     - n/a
   * - :term:`FCST_SERIES_ANALYSIS_PROB_THRESH`
     - n/a

.. note:: For more information on controlling the forecast field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_OBS_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_SERIES_ANALYSIS_INPUT_DATATYPE`
     - obs.file_type

**${METPLUS_OBS_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR<n>_NAME`
     - fcst.field.name
   * - :term:`OBS_VAR<n>_LEVELS`
     - fcst.field.level
   * - :term:`OBS_VAR<n>_THRESH`
     - fcst.field.cat_thresh
   * - :term:`OBS_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the observation field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_CLIMO_MEAN_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME`
     - climo_mean.file_name
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_FIELD`
     - climo_mean.field
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD`
     - climo_mean.regrid.method
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH`
     - climo_mean.regrid.width
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH`
     - climo_mean.regrid.vld_thresh
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE`
     - climo_mean.regrid.shape
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD`
     - climo_mean.time_interp_method
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH`
     - climo_mean.match_month
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL`
     - climo_mean.day_interval
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL`
     - climo_mean.hour_interval
   * - :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_TYPE`
     - climo_mean.file_type

**${METPLUS_CLIMO_STDEV_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME`
     - climo_stdev.file_name
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_FIELD`
     - climo_stdev.field
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD`
     - climo_stdev.regrid.method
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH`
     - climo_stdev.regrid.width
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH`
     - climo_stdev.regrid.vld_thresh
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE`
     - climo_stdev.regrid.shape
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD`
     - climo_stdev.time_interp_method
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH`
     - climo_stdev.match_month
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL`
     - climo_stdev.day_interval
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL`
     - climo_stdev.hour_interval
   * - :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_TYPE`
     - climo_stdev.file_type

**${METPLUS_CLIMO_CDF_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_CLIMO_CDF_BINS`
     - climo_cdf.cdf_bins
   * - :term:`SERIES_ANALYSIS_CLIMO_CDF_CENTER_BINS`
     - climo_cdf.center_bins
   * - :term:`SERIES_ANALYSIS_CLIMO_CDF_DIRECT_PROB`
     - climo_cdf.direct_prob

**${METPLUS_MASK_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_MASK_GRID`
     - mask.grid
   * - :term:`SERIES_ANALYSIS_MASK_POLY`
     - mask.poly

**${METPLUS_BLOCK_SIZE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_BLOCK_SIZE`
     - block_size

**${METPLUS_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_VLD_THRESH`
     - vld_thresh

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_HSS_EC_VALUE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_HSS_EC_VALUE`
     - hss_ec_value

**${METPLUS_OUTPUT_STATS_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_FHO`
     - output_stats.fho
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_CTC`
     - output_stats.ctc
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_CTS`
     - output_stats.cts
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_MCTC`
     - output_stats.mctc
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_MCTS`
     - output_stats.mcts
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_CNT`
     - output_stats.cnt
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_SL1L2`
     - output_stats.sl1l2
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_SAL1L2`
     - output_stats.sal1l2
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_PCT`
     - output_stats.pct
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_PSTD`
     - output_stats.pstd
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_PJC`
     - output_stats.pjc
   * - :term:`SERIES_ANALYSIS_OUTPUT_STATS_PRC`
     - output_stats.prc

**${METPLUS_FCST_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_SERIES_ANALYSIS_CAT_THRESH`
     - fcst.cat_thresh

**${METPLUS_OBS_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_SERIES_ANALYSIS_CAT_THRESH`
     - obs.cat_thresh


SeriesByInit
============

Description
-----------

.. warning:: **This tool has been DEPRECATED. Please use SeriesAnalysis wrapper**

SeriesByLead
============

Description
-----------

.. warning:: **This tool has been DEPRECATED. Please use SeriesAnalysis wrapper**

.. _stat_analysis_wrapper:

StatAnalysis
============

Description
-----------

The StatAnalysis wrapper encapsulates the behavior of the MET
stat_analysis tool. It provides the infrastructure to summarize and
filter the MET .stat files.

Timing
^^^^^^

This wrapper is configured differently than many of the other wrappers that
loop over multiple run times. The StatAnalysis wrapper is designed to process
a range of run times at once using filtering to subset what is processed.
The VALID_BEG and VALID_END or INIT_BEG and INIT_END variables are used to
calculate filtering criteria.

Prior to v5.0.0, only the year, month, and day (YYYYMMDD) of the init/valid
begin and end times were read by the wrapper. The hours, minutes, and seconds
were ignored to be filtered using FCST_HOUR_LIST and OBS_HOUR_LIST.
Now the full time information is read and to enable users to process a more
specific range of time. To preserve the original behavior, end times that
do not include hours, minutes, or seconds will process up to 23:59:59 on that
day unless specific hours are defined with FCST_HOUR_LIST or OBS_HOUR_LIST.

Note: The LEAD_SEQ variable that typically defines a list of forecast leads to
process is not used by the wrapper. Instead the FCST_LEAD_LIST and
OBS_LEAD_LIST are used to filter out forecast leads from the data.

Optional MET Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The wrapped MET config file specified with :term:`STAT_ANALYSIS_CONFIG_FILE` is
optional in the StatAnalysis wrapper. Excluding this option will result in a
call to stat_analysis with the job arguments added via the command line.
Only 1 job can be defined in no wrapped MET configuration file is used.
To use a configuration file, set the following in the METplus config file::

    STAT_ANALYSIS_CONFIG_FILE = {PARM_BASE}/met_config/STATAnalysisConfig_wrapped

Jobs
^^^^

The job arguments can be defined by setting :term:`STAT_ANALYSIS_JOB\<n\>`
variables, e.g. STAT_ANALYSIS_JOB1. All of the job commands including the -job
argument are set here.
Prior to v5.0.0, the config variables STAT_ANALYSIS_JOB_NAME and
STAT_ANALYSIS_JOB_ARGS were used to set the value following the -job argument
and any other job arguments respectively.

Multiple jobs can be defined as of v5.0.0 using
STAT_ANALYSIS_JOB1, STAT_ANALYSIS_JOB2, etc. All jobs will be passed to each
call to stat_analysis. Only 1 job can be specified if no MET config file is
set with :term:`STAT_ANALYSIS_CONFIG_FILE`.

Filtering with Lists
^^^^^^^^^^^^^^^^^^^^

There are many configuration variables that end with \_LIST that control
settings in the STATAnalysisConfig_wrapped file.
For example, MODEL_LIST controls the model variable in the MET config file and
FCST_LEAD_LIST controls the fcst_lead variable. The value for each of these
\_LIST variables can be a list of values separated by comma.
The value of GROUP_LIST_ITEMS is a comma-separated list of \_LIST variable
names that will be grouped together for each call to stat_analysis.
The value of LOOP_LIST_ITEMS is a comma-separated list of \_LIST variable
names that will be looped over to create multiple calls to stat_analysis.
The tool will be called with every combination of the LOOP_LIST_ITEMS
list values. List variables that are not included in either GROUP_LIST_ITEMS
or LOOP_LIST_ITEMS will be automatically added to GROUP_LIST_ITEMS. Lists
defined in LOOP_LIST_ITEMS that are empty lists will be automatically moved
to GROUP_LIST_ITEMS.

.. _stat-analysis-looping-groups:

Looping Over Groups of Lists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New in v5.0.0 is the ability to define groups of list items that can be looped
over. For example, a user may want to process forecast leads 1-3 in a
single run, then process forecast leads 4-6 in the next. To accomplish this,
define each group of items in a separate config variable ending with a number.
Then add the name of the list (without the numbers) to LOOP_LIST_ITEMS::

    [config]
    FCST_LEAD_LIST1 = 1,2,3
    FCST_LEAD_LIST2 = 4,5,6
    LOOP_LIST_ITEMS = FCST_LEAD_LIST

If FCST_LEAD_LIST was added to GROUP_LIST_ITEMS instead, then all 6 items
defined in the 2 lists will be combined and passed to the tool at once.

Filtering Begin and End Times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting in v5.0.0, the [fcst/obs]_[init/valid]_[beg/end] in the wrapped
MET config file can be set using the corresponding METplus config variables.
The values can include the filename template tags that are supported in the
wrapper (see :ref:`stat-analysis-filename-template`). For example,
to set the fcst_valid_beg value::

    [config]
    VALID_BEG = 20221014
    STAT_ANALYSIS_FCST_VALID_BEG = {fcst_valid_beg?fmt=%Y%m%d_%H%M%S}

This will set fcst_valid_beg = "20221014_000000"; in the MET config file.

Prior to v5.0.0, settings hour values in [FCST/OBS]_[INIT/VALID]_HOUR_LIST
would result in the corresponding _beg and _end values in the wrapped MET
config file to be set based on the hours and the [INIT/VALID]_[BEG/END] values.


.. _stat-analysis-filename-template:

Additional Filename Template Tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The StatAnalysis wrapper supports additional tags that can be substituted into
the input and output paths because the wrapper processes a range of time.

The following filename template tags can be used:

* model
* desc
* vx_mask
* interp_mthd
* interp_pnts
* cov_thresh
* alpha
* line_type
* fcst_var
* obs_var
* fcst_units
* obs_units
* fcst_thresh
* obs_thresh
* fcst_level
* obs_level
* fcst_valid_hour
* obs_valid_hour
* fcst_init_hour
* obs_init_hour
* fcst_lead
* obs_lead
* fcst_valid_hour_beg
* fcst_valid_hour_end
* obs_valid_hour_beg
* obs_valid_hour_end
* fcst_init_hour_beg
* fcst_init_hour_end
* obs_init_hour_beg
* obs_init_hour_end
* valid_hour
* valid_hour_beg
* valid_hour_end
* init_hour
* init_hour_beg
* init_hour_end
* fcst_valid
* fcst_valid_beg
* fcst_valid_end
* fcst_init
* fcst_init_beg
* fcst_init_end
* obs_valid
* obs_valid_beg
* obs_valid_end
* obs_init
* obs_init_beg
* obs_init_end
* valid
* valid_beg
* valid_end
* init
* init_beg
* init_end
* fcst_lead
* fcst_lead_hour
* fcst_lead_min
* fcst_lead_sec
* fcst_lead_totalsec
* obs_lead
* obs_lead_hour
* obs_lead_min
* obs_lead_sec
* obs_lead_totalsec
* lead
* lead_hour
* lead_min
* lead_sec
* lead_totalsec

Please note that some of these items will be set to an empty string depending
on the configuration. For example, lead_hour, lead_min, lead_sec, and
lead_totalsec cannot be computed if there are multiple leads being processed
in a given run. Another example, if fcst_valid_beg has the same value as
fcst_valid_end, then fcst_valid will be set to the same value, otherwise it
will be left as an empty string.

Outputs
^^^^^^^

This wrapper can be configured to write 3 types of output files.
Output files specified with the -out command line argument can be defined by
setting :term:`STAT_ANALYSIS_OUTPUT_TEMPLATE` and optionally
:term:`STAT_ANALYSIS_OUTPUT_DIR`.
Output files specified with the -dump_row or -out_stat arguments must be
defined in a job using :term:`STAT_ANALYSIS_JOB\<n\>`.
The [dump_row_file] keyword can be added to a job after the -dump_row argument
only if a :term:`MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE` is set. Similarly,
the [out_stat_file] keyword can be added to a job after the -out_stat argument
only if a :term:`MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE` is set.


METplus Configuration
---------------------

The following values **must** be defined in the METplus configuration file:

| :term:`STAT_ANALYSIS_JOB\<n\>`
| :term:`STAT_ANALYSIS_OUTPUT_DIR`
| :term:`MODEL\<n\>`
| :term:`MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR`
| :term:`GROUP_LIST_ITEMS`
| :term:`LOOP_LIST_ITEMS`

The following values are optional in the METplus configuration file:

| :term:`STAT_ANALYSIS_CONFIG_FILE`
| :term:`LOG_STAT_ANALYSIS_VERBOSITY`
| :term:`STAT_ANALYSIS_CUSTOM_LOOP_LIST`
| :term:`MODEL<n>_OBTYPE`
| :term:`VAR<n>_FOURIER_DECOMP`
| :term:`VAR<n>_WAVE_NUM_LIST`
| :term:`MODEL_LIST`
| :term:`DESC_LIST`
| :term:`FCST_LEAD_LIST`
| :term:`OBS_LEAD_LIST`
| :term:`FCST_VALID_HOUR_LIST`
| :term:`FCST_INIT_HOUR_LIST`
| :term:`OBS_VALID_HOUR_LIST`
| :term:`OBS_INIT_HOUR_LIST`
| :term:`FCST_VAR_LIST`
| :term:`OBS_VAR_LIST`
| :term:`FCST_UNITS_LIST`
| :term:`OBS_UNITS_LIST`
| :term:`FCST_LEVEL_LIST`
| :term:`OBS_LEVEL_LIST`
| :term:`VX_MASK_LIST`
| :term:`INTERP_MTHD_LIST`
| :term:`INTERP_PNTS_LIST`
| :term:`FCST_THRESH_LIST`
| :term:`OBS_THRESH_LIST`
| :term:`COV_THRESH_LIST`
| :term:`ALPHA_LIST`
| :term:`LINE_TYPE_LIST`
| :term:`STAT_ANALYSIS_HSS_EC_VALUE`
| :term:`STAT_ANALYSIS_OUTPUT_TEMPLATE`
| :term:`MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE`
| :term:`MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE`
| :term:`STAT_ANALYSIS_FCST_INIT_BEG`
| :term:`STAT_ANALYSIS_FCST_INIT_END`
| :term:`STAT_ANALYSIS_FCST_VALID_BEG`
| :term:`STAT_ANALYSIS_FCST_VALID_END`
| :term:`STAT_ANALYSIS_OBS_INIT_BEG`
| :term:`STAT_ANALYSIS_OBS_INIT_END`
| :term:`STAT_ANALYSIS_OBS_VALID_BEG`
| :term:`STAT_ANALYSIS_OBS_VALID_END`
| :term:`STAT_ANALYSIS_MET_CONFIG_OVERRIDES`

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
   | JOB_NAME
   | :term:`JOB_ARGS`
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
   | :term:`MODEL<n>_NAME`
   | :term:`MODEL<n>_OBS_NAME`
   | MODEL<n>_NAME_ON_PLOT
   | :term:`MODEL<n>_STAT_DIR`
   | :term:`REGION_LIST`
   | :term:`LEAD_LIST`
   | :term:`STAT_ANALYSIS_JOB_NAME`
   | :term:`STAT_ANALYSIS_JOB_ARGS`


.. _stat-analysis-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/STATAnalysisConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/STATAnalysisConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/STATAnalysisConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC_LIST`
     - desc

**${METPLUS_FCST_LEAD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_LEAD_LIST`
     - fcst_lead

**${METPLUS_OBS_LEAD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_LEAD_LIST`
     - obs_lead

**${METPLUS_FCST_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VALID_HOUR_LIST` and :term:`VALID_BEG`
     - fcst_valid_beg

**${METPLUS_FCST_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VALID_HOUR_LIST` and :term:`VALID_END`
     - fcst_valid_end

**${METPLUS_FCST_VALID_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VALID_HOUR_LIST`
     - fcst_valid_hour

**${METPLUS_OBS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VALID_HOUR_LIST` and :term:`VALID_BEG`
     - obs_valid_beg

**${METPLUS_OBS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VALID_HOUR_LIST` and :term:`VALID_END`
     - obs_valid_end

**${METPLUS_OBS_VALID_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VALID_HOUR_LIST`
     - obs_valid_hour

**${METPLUS_FCST_INIT_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_INIT_HOUR_LIST` and :term:`INIT_BEG`
     - fcst_init_beg

**${METPLUS_FCST_INIT_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_INIT_HOUR_LIST` and :term:`INIT_END`
     - fcst_init_end

**${METPLUS_FCST_INIT_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_INIT_HOUR_LIST`
     - fcst_init_hour

**${METPLUS_OBS_INIT_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_INIT_HOUR_LIST` and :term:`INIT_BEG`
     - obs_init_beg

**${METPLUS_OBS_INIT_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_INIT_HOUR_LIST` and :term:`INIT_END`
     - obs_init_end

**${METPLUS_OBS_INIT_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_INIT_HOUR_LIST`
     - obs_init_hour

**${METPLUS_FCST_VAR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_VAR_LIST`
     - fcst_var

**${METPLUS_OBS_VAR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_VAR_LIST`
     - obs_var

**${METPLUS_FCST_UNITS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_UNITS_LIST`
     - fcst_units

**${METPLUS_OBS_UNITS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_UNITS_LIST`
     - obs_units

**${METPLUS_FCST_LEVEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_LEVEL_LIST`
     - fcst_lev

**${METPLUS_OBS_LEVEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_LEVEL_LIST`
     - obs_lev

**${METPLUS_OBTYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL<n>_OBTYPE`
     - obtype

**${METPLUS_VX_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`VX_MASK_LIST`
     - vx_mask

**${METPLUS_INTERP_MTHD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`INTERP_MTHD_LIST`
     - interp_mthd

**${METPLUS_INTERP_PNTS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`INTERP_PNTS_LIST`
     - interp_pnts

**${METPLUS_FCST_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`FCST_THRESH_LIST`
     - fcst_thresh

**${METPLUS_OBS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`OBS_THRESH_LIST`
     - obs_thresh

**${METPLUS_COV_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`COV_THRESH_LIST`
     - cov_thresh

**${METPLUS_ALPHA}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ALPHA_LIST`
     - alpha

**${METPLUS_LINE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`LINE_TYPE_LIST`
     - line_type

**${METPLUS_JOBS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`STAT_ANALYSIS_JOB_NAME`
     - jobs

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`STAT_ANALYSIS_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_HSS_EC_VALUE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`STAT_ANALYSIS_HSS_EC_VALUE`
     - hss_ec_value


.. _tc_diag_wrapper:

TCDiag
======

Description
-----------

Used to configure the MET tool TC-Diag.

METplus Configuration
---------------------

| :term:`TC_DIAG_INPUT_DIR`
| :term:`TC_DIAG_DECK_INPUT_DIR`
| :term:`TC_DIAG_OUTPUT_DIR`
| :term:`TC_DIAG_DECK_TEMPLATE`
| :term:`TC_DIAG_INPUT_TEMPLATE`
| :term:`TC_DIAG_INPUT_FILE_LIST`
| :term:`TC_DIAG_OUTPUT_TEMPLATE`
| :term:`LOG_TC_DIAG_VERBOSITY`
| :term:`TC_DIAG_CONFIG_FILE`
| :term:`TC_DIAG_MODEL`
| :term:`TC_DIAG_STORM_ID`
| :term:`TC_DIAG_BASIN`
| :term:`TC_DIAG_CYCLONE`
| :term:`TC_DIAG_INIT_INCLUDE`
| :term:`TC_DIAG_VALID_BEG`
| :term:`TC_DIAG_VALID_END`
| :term:`TC_DIAG_VALID_INCLUDE`
| :term:`TC_DIAG_VALID_EXCLUDE`
| :term:`TC_DIAG_VALID_HOUR`
| :term:`TC_DIAG_DIAG_SCRIPT`
| :term:`TC_DIAG_DOMAIN_INFO<n>_DOMAIN`
| :term:`TC_DIAG_DOMAIN_INFO<n>_N_RANGE`
| :term:`TC_DIAG_DOMAIN_INFO<n>_N_AZIMUTH`
| :term:`TC_DIAG_DOMAIN_INFO<n>_DELTA_RANGE_KM`
| :term:`TC_DIAG_DOMAIN_INFO<n>_DIAG_SCRIPT`
| :term:`TC_DIAG_CENSOR_THRESH`
| :term:`TC_DIAG_CENSOR_VAL`
| :term:`TC_DIAG_CONVERT`
| :term:`TC_DIAG_INPUT_DATATYPE`
| :term:`TC_DIAG_DATA_DOMAIN`
| :term:`TC_DIAG_DATA_LEVEL`
| :term:`TC_DIAG_REGRID_METHOD`
| :term:`TC_DIAG_REGRID_WIDTH`
| :term:`TC_DIAG_REGRID_VLD_THRESH`
| :term:`TC_DIAG_REGRID_SHAPE`
| :term:`TC_DIAG_REGRID_CENSOR_THRESH`
| :term:`TC_DIAG_REGRID_CENSOR_VAL`
| :term:`TC_DIAG_REGRID_CONVERT`
| :term:`TC_DIAG_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS`
| :term:`TC_DIAG_U_WIND_FIELD_NAME`
| :term:`TC_DIAG_V_WIND_FIELD_NAME`
| :term:`TC_DIAG_TANGENTIAL_VELOCITY_FIELD_NAME`
| :term:`TC_DIAG_TANGENTIAL_VELOCITY_LONG_FIELD_NAME`
| :term:`TC_DIAG_RADIAL_VELOCITY_FIELD_NAME`
| :term:`TC_DIAG_RADIAL_VELOCITY_LONG_FIELD_NAME`
| :term:`TC_DIAG_VORTEX_REMOVAL`
| :term:`TC_DIAG_NC_RNG_AZI_FLAG`
| :term:`TC_DIAG_NC_DIAG_FLAG`
| :term:`TC_DIAG_CIRA_DIAG_FLAG`
| :term:`TC_DIAG_OUTPUT_PREFIX`
| :term:`TC_DIAG_SKIP_IF_OUTPUT_EXISTS`
| :term:`TC_DIAG_MET_CONFIG_OVERRIDES`
|

.. _tc-diag-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/TCDiagConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/TCDiagConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/TCDiagConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_STORM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_STORM_ID`
     - storm_id

**${METPLUS_BASIN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_BASIN`
     - basin

**${METPLUS_CYCLONE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_CYCLONE`
     - cyclone

**${METPLUS_INIT_INCLUDE_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_INIT_INCLUDE`
     - init_inc

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VALID_END`
     - valid_end

**${METPLUS_VALID_INCLUDE_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VALID_INCLUDE`
     - valid_inc

**${METPLUS_VALID_EXCLUDE_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VALID_EXCLUDE`
     - valid_exc

**${METPLUS_VALID_HOUR_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VALID_HOUR`
     - valid_hour

**${METPLUS_LEAD_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`LEAD_SEQ`
     - lead

**${METPLUS_DIAG_SCRIPT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_DIAG_SCRIPT`
     - diag_script

**${METPLUS_DOMAIN_INFO_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_DOMAIN_INFO<n>_DOMAIN`
     - domain_info.domain
   * - :term:`TC_DIAG_DOMAIN_INFO<n>_N_RANGE`
     - domain_info.n_range
   * - :term:`TC_DIAG_DOMAIN_INFO<n>_N_AZIMUTH`
     - domain_info.n_azimuth
   * - :term:`TC_DIAG_DOMAIN_INFO<n>_DELTA_RANGE_KM`
     - domain_info.delta_range_km
   * - :term:`TC_DIAG_DOMAIN_INFO<n>_DIAG_SCRIPT`
     - domain_info.diag_script

**${METPLUS_CENSOR_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_CENSOR_THRESH`
     - censor_thresh

**${METPLUS_CENSOR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_CENSOR_VAL`
     - censor_val

**${METPLUS_CONVERT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_CONVERT`
     - convert

**${METPLUS_DATA_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`BOTH_VAR<n>_NAME`
     - data.field.name
   * - :term:`BOTH_VAR<n>_LEVELS`
     - data.field.level
   * - :term:`BOTH_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_DATA_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_INPUT_DATATYPE`
     - data.file_type

**${METPLUS_DATA_DOMAIN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_DATA_DOMAIN`
     - data.domain

**${METPLUS_DATA_LEVEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_DATA_LEVEL`
     - data.level

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_REGRID_SHAPE`
     - regrid.shape
   * - :term:`TC_DIAG_REGRID_METHOD`
     - regrid.method
   * - :term:`TC_DIAG_REGRID_WIDTH`
     - regrid.width
   * - :term:`TC_DIAG_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`TC_DIAG_REGRID_CONVERT`
     - regrid.convert
   * - :term:`TC_DIAG_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`TC_DIAG_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS`
     - compute_tangential_and_radial_winds

**${METPLUS_U_WIND_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_U_WIND_FIELD_NAME`
     - u_wind_field_name

**${METPLUS_V_WIND_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_V_WIND_FIELD_NAME`
     - v_wind_field_name

**${METPLUS_TANGENTIAL_VELOCITY_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_TANGENTIAL_VELOCITY_FIELD_NAME`
     - tangential_velocity_field_name

**${METPLUS_TANGENTIAL_VELOCITY_LONG_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_TANGENTIAL_VELOCITY_LONG_FIELD_NAME`
     - tangential_velocity_long_field_name

**${METPLUS_RADIAL_VELOCITY_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_RADIAL_VELOCITY_FIELD_NAME`
     - radial_velocity_field_name

**${METPLUS_RADIAL_VELOCITY_LONG_FIELD_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_RADIAL_VELOCITY_LONG_FIELD_NAME`
     - radial_velocity_long_field_name

**${METPLUS_VORTEX_REMOVAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_VORTEX_REMOVAL`
     - vortex_removal

**${METPLUS_NC_RNG_AZI_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_NC_RNG_AZI_FLAG`
     - nc_rng_azi_flag

**${METPLUS_NC_DIAG_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_NC_DIAG_FLAG`
     - nc_diag_flag

**${METPLUS_CIRA_DIAG_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_CIRA_DIAG_FLAG`
     - cira_diag_flag

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_DIAG_MET_CONFIG_OVERRIDES`
     - n/a


.. _tc_gen_wrapper:

TCGen
=====

Description
-----------

The TCGen wrapper encapsulates the behavior of the MET tc_gen tool.
The wrapper accepts track (Adeck or Bdeck) data and Genesis data.

METplus Configuration
---------------------

| :term:`TC_GEN_TRACK_INPUT_DIR`
| :term:`TC_GEN_TRACK_INPUT_TEMPLATE`
| :term:`TC_GEN_GENESIS_INPUT_DIR`
| :term:`TC_GEN_GENESIS_INPUT_TEMPLATE`
| :term:`TC_GEN_EDECK_INPUT_DIR`
| :term:`TC_GEN_EDECK_INPUT_TEMPLATE`
| :term:`TC_GEN_SHAPE_INPUT_DIR`
| :term:`TC_GEN_SHAPE_INPUT_TEMPLATE`
| :term:`TC_GEN_OUTPUT_DIR`
| :term:`TC_GEN_OUTPUT_TEMPLATE`
| :term:`LOG_TC_GEN_VERBOSITY`
| :term:`TC_GEN_CUSTOM_LOOP_LIST`
| :term:`TC_GEN_SKIP_IF_OUTPUT_EXISTS`
| :term:`TC_GEN_MET_CONFIG_OVERRIDES`
| :term:`TC_GEN_CONFIG_FILE`
| :term:`TC_GEN_INIT_FREQ`
| :term:`TC_GEN_VALID_FREQ`
| :term:`TC_GEN_FCST_HR_WINDOW_BEGIN`
| :term:`TC_GEN_FCST_HR_WINDOW_END`
| :term:`TC_GEN_MIN_DURATION`
| :term:`TC_GEN_FCST_GENESIS_VMAX_THRESH`
| :term:`TC_GEN_FCST_GENESIS_MSLP_THRESH`
| :term:`TC_GEN_BEST_GENESIS_TECHNIQUE`
| :term:`TC_GEN_BEST_GENESIS_CATEGORY`
| :term:`TC_GEN_BEST_GENESIS_VMAX_THRESH`
| :term:`TC_GEN_BEST_GENESIS_MSLP_THRESH`
| :term:`TC_GEN_OPER_TECHNIQUE`
| :term:`TC_GEN_FILTER_\<n\>`
| :term:`TC_GEN_DESC`
| :term:`MODEL`
| :term:`TC_GEN_STORM_ID`
| :term:`TC_GEN_STORM_NAME`
| :term:`TC_GEN_INIT_BEG`
| :term:`TC_GEN_INIT_END`
| :term:`TC_GEN_INIT_INC`
| :term:`TC_GEN_INIT_EXC`
| :term:`TC_GEN_VALID_BEG`
| :term:`TC_GEN_VALID_END`
| :term:`TC_GEN_INIT_HOUR`
| :term:`LEAD_SEQ`
| :term:`TC_GEN_VX_MASK`
| :term:`TC_GEN_BASIN_MASK`
| :term:`TC_GEN_DLAND_THRESH`
| :term:`TC_GEN_GENESIS_MATCH_RADIUS`
| :term:`TC_GEN_GENESIS_MATCH_POINT_TO_TRACK`
| :term:`TC_GEN_GENESIS_MATCH_WINDOW_BEG`
| :term:`TC_GEN_GENESIS_MATCH_WINDOW_END`
| :term:`TC_GEN_DEV_HIT_RADIUS`
| :term:`TC_GEN_DEV_HIT_WINDOW_BEGIN`
| :term:`TC_GEN_DEV_HIT_WINDOW_END`
| :term:`TC_GEN_OPS_HIT_WINDOW_BEG`
| :term:`TC_GEN_OPS_HIT_WINDOW_END`
| :term:`TC_GEN_DISCARD_INIT_POST_GENESIS_FLAG`
| :term:`TC_GEN_DEV_METHOD_FLAG`
| :term:`TC_GEN_OPS_METHOD_FLAG`
| :term:`TC_GEN_CI_ALPHA`
| :term:`TC_GEN_OUTPUT_FLAG_FHO`
| :term:`TC_GEN_OUTPUT_FLAG_CTC`
| :term:`TC_GEN_OUTPUT_FLAG_CTS`
| :term:`TC_GEN_OUTPUT_FLAG_PCT`
| :term:`TC_GEN_OUTPUT_FLAG_PSTD`
| :term:`TC_GEN_OUTPUT_FLAG_PJC`
| :term:`TC_GEN_OUTPUT_FLAG_PRC`
| :term:`TC_GEN_OUTPUT_FLAG_GENMPR`
| :term:`TC_GEN_NC_PAIRS_FLAG_LATLON`
| :term:`TC_GEN_NC_PAIRS_FLAG_FCST_GENESIS`
| :term:`TC_GEN_NC_PAIRS_FLAG_FCST_TRACKS`
| :term:`TC_GEN_NC_PAIRS_FLAG_FCST_FY_OY`
| :term:`TC_GEN_NC_PAIRS_FLAG_FCST_FY_ON`
| :term:`TC_GEN_NC_PAIRS_FLAG_BEST_GENESIS`
| :term:`TC_GEN_NC_PAIRS_FLAG_BEST_TRACKS`
| :term:`TC_GEN_NC_PAIRS_FLAG_BEST_FY_OY`
| :term:`TC_GEN_NC_PAIRS_FLAG_BEST_FN_OY`
| :term:`TC_GEN_VALID_MINUS_GENESIS_DIFF_THRESH`
| :term:`TC_GEN_BEST_UNIQUE_FLAG`
| :term:`TC_GEN_DLAND_FILE`
| :term:`TC_GEN_BASIN_FILE`
| :term:`TC_GEN_NC_PAIRS_GRID`

.. warning:: **DEPRECATED:**

   | :term:`TC_GEN_LEAD_WINDOW_BEGIN`
   | :term:`TC_GEN_LEAD_WINDOW_END`
   | :term:`TC_GEN_OPER_GENESIS_TECHNIQUE`
   | :term:`TC_GEN_OPER_GENESIS_CATEGORY`
   | :term:`TC_GEN_OPER_GENESIS_VMAX_THRESH`
   | :term:`TC_GEN_OPER_GENESIS_MSLP_THRESH`
   | :term:`TC_GEN_GENESIS_RADIUS`
   | :term:`TC_GEN_GENESIS_WINDOW_BEGIN`
   | :term:`TC_GEN_GENESIS_WINDOW_END`

.. _tc-gen-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/TCGenConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/TCGenConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.


.. literalinclude:: ../../parm/met_config/TCGenConfig_wrapped

**${METPLUS_INIT_FREQ}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_FREQ`
     - init_freq

**${METPLUS_VALID_FREQ}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_VALID_FREQ`
     - valid_freq

**${METPLUS_FCST_HR_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_FCST_HR_WINDOW_BEGIN`
     - fcst_hr_window.beg
   * - :term:`TC_GEN_FCST_HR_WINDOW_END`
     - fcst_hr_window.end

**${METPLUS_MIN_DURATION}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_MIN_DURATION`
     - min_duration

**${METPLUS_FCST_GENESIS_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_FCST_GENESIS_VMAX_THRESH`
     - fcst_genesis.vmax_thresh
   * - :term:`TC_GEN_FCST_GENESIS_MSLP_THRESH`
     - fcst_genesis.mslp_thresh

**${METPLUS_BEST_GENESIS_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_BEST_GENESIS_TECHNIQUE`
     - best_genesis.technique
   * - :term:`TC_GEN_BEST_GENESIS_CATEGORY`
     - best_genesis.category
   * - :term:`TC_GEN_BEST_GENESIS_VMAX_THRESH`
     - best_genesis.vmax_thresh
   * - :term:`TC_GEN_BEST_GENESIS_MSLP_THRESH`
     - best_genesis.mslp_thresh

**${METPLUS_OPER_TECHNIQUE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_OPER_TECHNIQUE`
     - oper_technique

**${METPLUS_FILTER}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_FILTER_\<n\>`
     - filter

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` -or- :term:`TC_GEN_DESC`
     - desc

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_STORM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_STORM_ID`
     - storm_id

**${METPLUS_STORM_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_STORM_NAME`
     - storm_name

**${METPLUS_INIT_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_BEG`
     - init_beg

**${METPLUS_INIT_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_END`
     - init_end

**${METPLUS_INIT_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_INC`
     - init_inc


**${METPLUS_INIT_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_EXC`
     - init_exc

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_VALID_END`
     - valid_end

**${METPLUS_INIT_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_INIT_HOUR`
     - init_hour

**${METPLUS_LEAD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`LEAD_SEQ`
     - lead

**${METPLUS_VX_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_VX_MASK`
     - vx_mask

**${METPLUS_BASIN_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_BASIN_MASK`
     - basin_mask

**${METPLUS_DLAND_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DLAND_THRESH`
     - dland_thresh

**${METPLUS_DEV_HIT_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DEV_HIT_WINDOW_BEGIN`
     - dev_hit_window.beg
   * - :term:`TC_GEN_DEV_HIT_WINDOW_END`
     - dev_hit_window.end

**${METPLUS_GENESIS_MATCH_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_GENESIS_MATCH_RADIUS`
     - genesis_match_radius

**${METPLUS_GENESIS_MATCH_POINT_TO_TRACK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_GENESIS_MATCH_POINT_TO_TRACK`
     - genesis_match_point_to_track

**${METPLUS_GENESIS_MATCH_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_GENESIS_MATCH_WINDOW_BEG`
     - genesis_match_window.beg
   * - :term:`TC_GEN_GENESIS_MATCH_WINDOW_END`
     - genesis_match_window.end

**${METPLUS_DEV_HIT_RADIUS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DEV_HIT_RADIUS`
     - dev_hit_radius

**${METPLUS_OPS_HIT_WINDOW_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_OPS_HIT_WINDOW_BEG`
     - ops_hit_window.beg
   * - :term:`TC_GEN_OPS_HIT_WINDOW_END`
     - ops_hit_window.end

**${METPLUS_DISCARD_INIT_POST_GENESIS_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DISCARD_INIT_POST_GENESIS_FLAG`
     - discard_init_post_genesis_flag

**${METPLUS_DEV_METHOD_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DEV_METHOD_FLAG`
     - dev_method_flag

**${METPLUS_OPS_METHOD_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_OPS_METHOD_FLAG`
     - ops_method_flag

**${METPLUS_CI_ALPHA}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_CI_ALPHA`
     - ci_alpha

**${METPLUS_OUTPUT_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_OUTPUT_FLAG_FHO`
     - output_flag.fho
   * - :term:`TC_GEN_OUTPUT_FLAG_CTC`
     - output_flag.ctc
   * - :term:`TC_GEN_OUTPUT_FLAG_CTS`
     - output_flag.cts
   * - :term:`TC_GEN_OUTPUT_FLAG_PCT`
     - output_flag.pct
   * - :term:`TC_GEN_OUTPUT_FLAG_PSTD`
     - output_flag.pstd
   * - :term:`TC_GEN_OUTPUT_FLAG_PJC`
     - output_flag.pjc
   * - :term:`TC_GEN_OUTPUT_FLAG_PRC`
     - output_flag.prc
   * - :term:`TC_GEN_OUTPUT_FLAG_GENMPR`
     - output_flag.genmpr

**${METPLUS_NC_PAIRS_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_NC_PAIRS_FLAG_LATLON`
     - nc_pairs_flag.latlon
   * - :term:`TC_GEN_NC_PAIRS_FLAG_FCST_GENESIS`
     - nc_pairs_flag.fcst_genesis
   * - :term:`TC_GEN_NC_PAIRS_FLAG_FCST_TRACKS`
     - nc_pairs_flag.fcst_tracks
   * - :term:`TC_GEN_NC_PAIRS_FLAG_FCST_FY_OY`
     - nc_pairs_flag.fcst_fy_oy
   * - :term:`TC_GEN_NC_PAIRS_FLAG_FCST_FY_ON`
     - nc_pairs_flag.fcst_fy_on
   * - :term:`TC_GEN_NC_PAIRS_FLAG_BEST_GENESIS`
     - nc_pairs_flag.best_genesis
   * - :term:`TC_GEN_NC_PAIRS_FLAG_BEST_TRACKS`
     - nc_pairs_flag.best_tracks
   * - :term:`TC_GEN_NC_PAIRS_FLAG_BEST_FY_OY`
     - nc_pairs_flag.best_fy_oy
   * - :term:`TC_GEN_NC_PAIRS_FLAG_BEST_FN_OY`
     - nc_pairs_flag.best_fn_oy

**${METPLUS_VALID_MINUS_GENESIS_DIFF_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_VALID_MINUS_GENESIS_DIFF_THRESH`
     - valid_minus_genesis_diff_thresh

**${METPLUS_BEST_UNIQUE_FLAG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_BEST_UNIQUE_FLAG`
     - best_unique_flag

**${METPLUS_DLAND_FILE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_DLAND_FILE`
     - dland_file

**${METPLUS_BASIN_FILE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_BASIN_FILE`
     - basin_file

**${METPLUS_NC_PAIRS_GRID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_NC_PAIRS_GRID`
     - nc_pairs_grid

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_GEN_MET_CONFIG_OVERRIDES`
     - n/a

.. _tcmpr_plotter_wrapper:

TCMPRPlotter
============

Description
-----------

The TCMPRPlotter wrapper is a Python script that wraps the R script
plot_tcmpr.R. This script is useful for plotting the calculated
statistics for the output from the MET-TC tools. This script, and other
R scripts are included in the MET installation. Please refer to
the MET User's Guide for usage information.

METplus Configuration
---------------------

| :term:`TCMPR_PLOTTER_TCMPR_DATA_DIR`
| :term:`TCMPR_PLOTTER_PLOT_OUTPUT_DIR`
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
| :term:`TCMPR_PLOTTER_DEP_LABELS`
| :term:`TCMPR_PLOTTER_PLOT_LABELS`
| :term:`TCMPR_PLOTTER_READ_ALL_FILES`
|

The following are TCMPR flags, if set to 'no', then don't set flag, if
set to 'yes', then set the flag

| :term:`TCMPR_PLOTTER_NO_EE`
| :term:`TCMPR_PLOTTER_NO_LOG`
| :term:`TCMPR_PLOTTER_SAVE`
|

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
   |

.. _tc_pairs_wrapper:

TCPairs
=======

Description
-----------

The TCPairs wrapper encapsulates the behavior of the MET tc_pairs tool.
The wrapper accepts Adeck and Bdeck (Best track) cyclone track data in
extra tropical cyclone format (such as the data used by sample data
provided in the METplus tutorial), or ATCF formatted track data. If data
is in an extra tropical cyclone (non-ATCF) format, the data is
reformatted into an ATCF format that is recognized by MET.

METplus Configuration
---------------------

| :term:`TC_PAIRS_ADECK_INPUT_DIR`
| :term:`TC_PAIRS_BDECK_INPUT_DIR`
| :term:`TC_PAIRS_EDECK_INPUT_DIR`
| :term:`TC_PAIRS_OUTPUT_DIR`
| :term:`TC_PAIRS_REFORMAT_DIR`
| :term:`TC_PAIRS_ADECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_BDECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_EDECK_INPUT_TEMPLATE`
| :term:`TC_PAIRS_OUTPUT_TEMPLATE`
| :term:`TC_PAIRS_CONFIG_FILE`
| :term:`TC_PAIRS_INIT_INCLUDE`
| :term:`TC_PAIRS_INIT_EXCLUDE`
| :term:`TC_PAIRS_VALID_INCLUDE`
| :term:`TC_PAIRS_VALID_EXCLUDE`
| :term:`TC_PAIRS_WRITE_VALID`
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
| :term:`TC_PAIRS_DESC`
| :term:`TC_PAIRS_MET_CONFIG_OVERRIDES`
| :term:`TC_PAIRS_CONSENSUS<n>_NAME`
| :term:`TC_PAIRS_CONSENSUS<n>_MEMBERS`
| :term:`TC_PAIRS_CONSENSUS<n>_REQUIRED`
| :term:`TC_PAIRS_CONSENSUS<n>_MIN_REQ`
| :term:`TC_PAIRS_CONSENSUS<n>_WRITE_MEMBERS`
| :term:`TC_PAIRS_SKIP_LEAD_SEQ`
| :term:`TC_PAIRS_RUN_ONCE`
| :term:`TC_PAIRS_CHECK_DUP`
| :term:`TC_PAIRS_INTERP12`
| :term:`TC_PAIRS_MATCH_POINTS`
| :term:`TC_PAIRS_DIAG_INFO_MAP<n>_DIAG_SOURCE`
| :term:`TC_PAIRS_DIAG_INFO_MAP<n>_TRACK_SOURCE`
| :term:`TC_PAIRS_DIAG_INFO_MAP<n>_FIELD_SOURCE`
| :term:`TC_PAIRS_DIAG_INFO_MAP<n>_MATCH_TO_TRACK`
| :term:`TC_PAIRS_DIAG_INFO_MAP<n>_DIAG_NAME`
| :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_DIAG_SOURCE`
| :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_KEY`
| :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_CONVERT`
| :term:`TC_PAIRS_DIAG_SOURCE\<n\>`
| :term:`TC_PAIRS_DIAG_TEMPLATE\<n\>`
| :term:`TC_PAIRS_DIAG_DIR\<n\>`
|

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
   |

.. _tc-pairs-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/TCPairsConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/TCPairsConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/TCPairsConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`DESC` -or- :term:`TC_PAIRS_DESC`
     - desc

**${METPLUS_STORM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_STORM_ID`
     - storm_id

**${METPLUS_BASIN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_BASIN`
     - basin

**${METPLUS_CYCLONE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_CYCLONE`
     - cyclone

**${METPLUS_STORM_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_STORM_NAME`
     - storm_name

**${METPLUS_INIT_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_BEG`
     - init_beg

**${METPLUS_INIT_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_END`
     - init_end

**${METPLUS_INIT_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_INCLUDE`
     - init_inc

**${METPLUS_INIT_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_EXCLUDE`
     - init_exc

**${METPLUS_VALID_INC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_VALID_INCLUDE`
     - valid_inc

**${METPLUS_VALID_EXC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_VALID_EXCLUDE`
     - valid_exc

**${METPLUS_WRITE_VALID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_WRITE_VALID`
     - write_valid

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_VALID_END`
     - valid_end

**${METPLUS_MATCH_POINTS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_MATCH_POINTS`
     - match_points

**${METPLUS_DLAND_FILE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_DLAND_FILE`
     - dland_file

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_CONSENSUS_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_CONSENSUS<n>_NAME`
     - consensus.name
   * - :term:`TC_PAIRS_CONSENSUS<n>_MEMBERS`
     - consensus.members
   * - :term:`TC_PAIRS_CONSENSUS<n>_REQUIRED`
     - consensus.required
   * - :term:`TC_PAIRS_CONSENSUS<n>_MIN_REQ`
     - consensus.min_req
   * - :term:`TC_PAIRS_CONSENSUS<n>_WRITE_MEMBERS`
     - consensus.write_members


**${METPLUS_CHECK_DUP}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_CHECK_DUP`
     - check_dup

**${METPLUS_INTERP12}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INTERP12`
     - interp12

**${METPLUS_DIAG_INFO_MAP_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_DIAG_INFO_MAP<n>_DIAG_SOURCE`
     - diag_info_map.diag_source
   * - :term:`TC_PAIRS_DIAG_INFO_MAP<n>_TRACK_SOURCE`
     - diag_info_map.track_source
   * - :term:`TC_PAIRS_DIAG_INFO_MAP<n>_FIELD_SOURCE`
     - diag_info_map.field_source
   * - :term:`TC_PAIRS_DIAG_INFO_MAP<n>_MATCH_TO_TRACK`
     - diag_info_map.match_to_track
   * - :term:`TC_PAIRS_DIAG_INFO_MAP<n>_DIAG_NAME`
     - diag_info_map.diag_name

**${METPLUS_DIAG_CONVERT_MAP_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_DIAG_SOURCE`
     - diag_convert_map.diag_source
   * - :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_KEY`
     - diag_convert_map.key
   * - :term:`TC_PAIRS_DIAG_CONVERT_MAP<n>_CONVERT`
     - diag_convert_map.convert


.. _tcrmw_wrapper:

TCRMW
=====

Description
-----------

Used to configure the MET tool TC-RMW.

METplus Configuration
---------------------

| :term:`TC_RMW_INPUT_DIR`
| :term:`TC_RMW_DECK_INPUT_DIR`
| :term:`TC_RMW_OUTPUT_DIR`
| :term:`TC_RMW_DECK_TEMPLATE`
| :term:`TC_RMW_INPUT_TEMPLATE`
| :term:`TC_RMW_INPUT_FILE_LIST`
| :term:`TC_RMW_OUTPUT_TEMPLATE`
| :term:`LOG_TC_RMW_VERBOSITY`
| :term:`TC_RMW_CONFIG_FILE`
| :term:`TC_RMW_INPUT_DATATYPE`
| :term:`TC_RMW_REGRID_METHOD`
| :term:`TC_RMW_REGRID_WIDTH`
| :term:`TC_RMW_REGRID_VLD_THRESH`
| :term:`TC_RMW_REGRID_SHAPE`
| :term:`TC_RMW_REGRID_CONVERT`
| :term:`TC_RMW_REGRID_CENSOR_THRESH`
| :term:`TC_RMW_REGRID_CENSOR_VAL`
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
| :term:`TC_RMW_DESC`
| :term:`MODEL`
| :term:`LEAD_SEQ`
| :term:`TC_RMW_MET_CONFIG_OVERRIDES`
|

.. _tc-rmw-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/TCRMWConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/TCRMWConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/TCRMWConfig_wrapped

**${METPLUS_MODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`MODEL`
     - model

**${METPLUS_STORM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_STORM_ID`
     - storm_id

**${METPLUS_BASIN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_BASIN`
     - basin

**${METPLUS_CYCLONE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_CYCLONE`
     - cyclone

**${METPLUS_INIT_INCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_INIT_INCLUDE`
     - init_inc

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_VALID_END`
     - valid_end

**${METPLUS_VALID_INCLUDE_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_VALID_INCLUDE_LIST`
     - valid_inc

**${METPLUS_VALID_EXCLUDE_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_VALID_EXCLUDE_LIST`
     - valid_exc

**${METPLUS_VALID_HOUR_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_VALID_HOUR_LIST`
     - valid_hour

**${METPLUS_LEAD_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`LEAD_SEQ`
     - lead

**${METPLUS_DATA_FILE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_INPUT_DATATYPE`
     - data.file_type

**${METPLUS_DATA_FIELD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`BOTH_VAR<n>_NAME`
     - data.field.name
   * - :term:`BOTH_VAR<n>_LEVELS`
     - data.field.level
   * - :term:`BOTH_VAR<n>_OPTIONS`
     - n/a

.. note:: For more information on controlling the field attributes in METplus, please see the :ref:`Field_Info` section of the User's Guide.

**${METPLUS_REGRID_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_REGRID_SHAPE`
     - regrid.shape
   * - :term:`TC_RMW_REGRID_METHOD`
     - regrid.method
   * - :term:`TC_RMW_REGRID_WIDTH`
     - regrid.width
   * - :term:`TC_RMW_REGRID_VLD_THRESH`
     - regrid.vld_thresh
   * - :term:`TC_RMW_REGRID_CONVERT`
     - regrid.convert
   * - :term:`TC_RMW_REGRID_CENSOR_THRESH`
     - regrid.censor_thresh
   * - :term:`TC_RMW_REGRID_CENSOR_VAL`
     - regrid.censor_val

**${METPLUS_N_RANGE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_N_RANGE`
     - n_range

**${METPLUS_N_AZIMUTH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_N_AZIMUTH`
     - n_azimuth

**${METPLUS_MAX_RANGE_KM}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_MAX_RANGE_KM`
     - max_range_km

**${METPLUS_DELTA_RANGE_KM}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_DELTA_RANGE_KM`
     - delta_range_km

**${METPLUS_RMW_SCALE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_SCALE`
     - rmw_scale

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_RMW_MET_CONFIG_OVERRIDES`
     - n/a

.. _tc_stat_wrapper:

TCStat
======

Description
-----------

Used to configure the MET tool tc_stat.

METplus Configuration
---------------------

| :term:`TC_STAT_LOOKIN_DIR`
| :term:`TC_STAT_OUTPUT_DIR`
| :term:`TC_STAT_OUTPUT_TEMPLATE`
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
| :term:`TC_STAT_MET_CONFIG_OVERRIDES`
| :term:`TC_STAT_COLUMN_STR_EXC_NAME`
| :term:`TC_STAT_COLUMN_STR_EXC_VAL`
| :term:`TC_STAT_INIT_STR_EXC_NAME`
| :term:`TC_STAT_INIT_STR_EXC_VAL`
| :term:`TC_STAT_DIAG_THRESH_NAME`
| :term:`TC_STAT_DIAG_THRESH_VAL`
| :term:`TC_STAT_INIT_DIAG_THRESH_NAME`
| :term:`TC_STAT_INIT_DIAG_THRESH_VAL`
| :term:`TC_STAT_LINE_TYPE`
| :term:`TC_STAT_EVENT_EQUAL`
| :term:`TC_STAT_EVENT_EQUAL_LEAD`
| :term:`TC_STAT_OUT_INIT_MASK`
| :term:`TC_STAT_OUT_VALID_MASK`
|

.. warning:: **DEPRECATED:**

   | :term:`TC_STAT_INPUT_DIR`
   | :term:`TC_STAT_RUN_VIA`
   | :term:`TC_STAT_CMD_LINE_JOB`
   | :term:`TC_STAT_JOBS_LIST`
   |

.. _tc-stat-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/TCStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/data/config/TCStatConfig_default>`_

Below the file contents are descriptions of each environment variable
referenced in this file and the corresponding METplus configuration item used
to set the value of the environment variable. For detailed examples showing
how METplus sets the values of these environment variables,
see :ref:`How METplus controls MET config file settings<metplus-control-met>`.

.. literalinclude:: ../../parm/met_config/TCStatConfig_wrapped

**${METPLUS_AMODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_AMODEL`
     - amodel

**${METPLUS_BMODEL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_BMODEL`
     - bmodel

**${METPLUS_DESC}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_DESC`
     - desc

**${METPLUS_STORM_ID}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_STORM_ID`
     - storm_id

**${METPLUS_BASIN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_BASIN`
     - basin

**${METPLUS_CYCLONE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_CYCLONE`
     - cyclone

**${METPLUS_STORM_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_STORM_NAME`
     - storm_name

**${METPLUS_INIT_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_BEG`
     - init_beg

**${METPLUS_INIT_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_END`
     - init_end

**${METPLUS_INIT_INCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_INCLUDE`
     - init_inc

**${METPLUS_INIT_EXCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_EXCLUDE`
     - init_exc

**${METPLUS_VALID_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_BEG`
     - valid_beg

**${METPLUS_VALID_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_END`
     - valid_end

**${METPLUS_VALID_INCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_INCLUDE`
     - valid_inc

**${METPLUS_VALID_EXCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_EXCLUDE`
     - valid_exc

**${METPLUS_INIT_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_HOUR`
     - init_hour

**${METPLUS_VALID_HOUR}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_HOUR`
     - valid_hour

**${METPLUS_LEAD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LEAD`
     - lead

**${METPLUS_LEAD_REQ}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LEAD_REQ`
     - lead_req

**${METPLUS_INIT_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_MASK`
     - init_mask

**${METPLUS_VALID_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_VALID_MASK`
     - valid_mask

**${METPLUS_LINE_TYPE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LINE_TYPE`
     - line_type

**${METPLUS_TRACK_WATCH_WARN}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_TRACK_WATCH_WARN`
     - track_watch_warn

**${METPLUS_COLUMN_THRESH_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_THRESH_NAME`
     - column_thresh_name

**${METPLUS_COLUMN_THRESH_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_THRESH_VAL`
     - column_thresh_val

**${METPLUS_COLUMN_STR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_STR_NAME`
     - column_str_name

**${METPLUS_COLUMN_STR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_STR_VAL`
     - column_str_val

**${METPLUS_COLUMN_STR_EXC_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_STR_EXC_NAME`
     - column_str_exc_name

**${METPLUS_COLUMN_STR_EXC_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_COLUMN_STR_EXC_VAL`
     - column_str_exc_val

**${METPLUS_INIT_THRESH_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_THRESH_NAME`
     - init_thresh_name

**${METPLUS_INIT_THRESH_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_THRESH_VAL`
     - init_thresh_val

**${METPLUS_INIT_STR_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_STR_NAME`
     - init_str_name

**${METPLUS_INIT_STR_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_STR_VAL`
     - init_str_val

**${METPLUS_INIT_STR_EXC_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_STR_EXC_NAME`
     - init_str_exc_name

**${METPLUS_INIT_STR_EXC_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_STR_EXC_VAL`
     - init_str_exc_val

**${METPLUS_DIAG_THRESH_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_DIAG_THRESH_NAME`
     - diag_thresh_name

**${METPLUS_DIAG_THRESH_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_DIAG_THRESH_VAL`
     - diag_thresh_val

**${METPLUS_INIT_DIAG_THRESH_NAME}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_DIAG_THRESH_NAME`
     - init_diag_thresh_name

**${METPLUS_INIT_DIAG_THRESH_VAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_INIT_DIAG_THRESH_VAL`
     - init_diag_thresh_val

**${METPLUS_WATER_ONLY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_WATER_ONLY`
     - water_only

**${METPLUS_LANDFALL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LANDFALL`
     - landfall

**${METPLUS_LANDFALL_BEG}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LANDFALL_BEG`
     - landfall_beg

**${METPLUS_LANDFALL_END}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_LANDFALL_END`
     - landfall_end

**${METPLUS_MATCH_POINTS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_MATCH_POINTS`
     - match_points

**${METPLUS_JOBS}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_JOBS_LIST`
     - jobs

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_MET_CONFIG_OVERRIDES`
     - n/a

**${METPLUS_EVENT_EQUAL}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_EVENT_EQUAL`
     - event_equal

**${METPLUS_EVENT_EQUAL_LEAD}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_EVENT_EQUAL_LEAD`
     - event_equal_lead

**${METPLUS_OUT_INIT_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_OUT_INIT_MASK`
     - out_init_mask

**${METPLUS_OUT_VALID_MASK}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_STAT_OUT_VALID_MASK`
     - out_valid_mask


.. _user_script_wrapper:

UserScript
==========

Description
-----------

Used to generate user-defined commands to run in the process list. Commands
can be run once, run once for each runtime (init/valid/lead combination) or
once for init, valid, or lead only. The command to run is specified with the
:term:`USER_SCRIPT_COMMAND` variable. The command should include a script or
executable and any desired arguments. The variable support filename template
substitution to send information like the current initialization or forecast
lead time. See :ref:`Runtime_Freq` for more information on how the value of
:term:`USER_SCRIPT_RUNTIME_FREQ` can control how the commands are called.
Optionally, file paths can be defined with filename templates to generate
a file list text file that contains all existing file paths that correspond
to the appropriate runtime frequency for the current run time. The path to
the file list text files are set as environment variables that can be
referenced inside the user-defined script to obtain a list of the files that
should be processed.
See :term:`USER_SCRIPT_INPUT_TEMPLATE` for more information.

Note: This wrapper may be disabled upon installation to prevent security risks.

METplus Configuration
---------------------

| :term:`USER_SCRIPT_RUNTIME_FREQ`
| :term:`USER_SCRIPT_COMMAND`
| :term:`USER_SCRIPT_CUSTOM_LOOP_LIST`
| :term:`USER_SCRIPT_SKIP_TIMES`
| :term:`USER_SCRIPT_INPUT_DIR`
| :term:`USER_SCRIPT_INPUT_TEMPLATE`
| :term:`USER_SCRIPT_INPUT_TEMPLATE_LABELS`
|
