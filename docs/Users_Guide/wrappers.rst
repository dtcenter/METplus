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

`MET_INSTALL_DIR/share/met/config/Ascii2NcConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/Ascii2NcConfig_default>`_

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
the output from the MET tc-pairs tool can be plotted.

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
| :term:`ENSEMBLE_STAT_OUTPUT_TEMPLATE`
| :term:`LOG_ENSEMBLE_STAT_VERBOSITY`
| :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE`
| :term:`OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE`
| :term:`ENSEMBLE_STAT_REGRID_TO_GRID`
| :term:`ENSEMBLE_STAT_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_CONFIG_FILE`
| :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE`
| :term:`ENSEMBLE_STAT_N_MEMBERS`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_WINDOW_END`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN`
| :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_END`
| :term:`ENSEMBLE_STAT_ENS_THRESH`
| :term:`ENSEMBLE_STAT_ENS_VLD_THRESH`
| :term:`ENSEMBLE_STAT_ENS_OBS_THRESH`
| :term:`ENSEMBLE_STAT_CUSTOM_LOOP_LIST`
| :term:`ENSEMBLE_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`ENSEMBLE_STAT_DESC`
| :term:`ENSEMBLE_STAT_ENS_SSVAR_BIN_SIZE`
| :term:`ENSEMBLE_STAT_ENS_PHIST_BIN_SIZE`
| :term:`ENSEMBLE_STAT_NBRHD_PROB_WIDTH`
| :term:`ENSEMBLE_STAT_NBRHD_PROB_SHAPE`
| :term:`ENSEMBLE_STAT_NBRHD_PROB_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_BINS`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS`
| :term:`ENSEMBLE_STAT_DUPLICATE_FLAG`
| :term:`ENSEMBLE_STAT_SKIP_CONST`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_DX`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_RADIUS`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_VLD_THRESH`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_SHAPE`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_METHOD`
| :term:`ENSEMBLE_STAT_NMEP_SMOOTH_WIDTH`
| :term:`ENSEMBLE_STAT_CENSOR_THRESH`
| :term:`ENSEMBLE_STAT_CENSOR_VAL`
| :term:`ENSEMBLE_STAT_DUPLICATE_FLAG`
| :term:`ENSEMBLE_STAT_SKIP_CONST`
| :term:`ENSEMBLE_STAT_OBS_ERROR_FLAG`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_FIELD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_FIELD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL`
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
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_RANK`
| :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_WEIGHT`
| :term:`ENSEMBLE_STAT_MET_CONFIG_OVERRIDES`
| :term:`ENSEMBLE_STAT_VERIFICATION_MASK_TEMPLATE` (optional)
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

`MET_INSTALL_DIR/share/met/config/EnsembleStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/EnsembleStatConfig_default>`_

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
     - ens.ens_thresh

**${METPLUS_ENS_VLD_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_VLD_THRESH`
     - ens.vld_thresh

**${METPLUS_ENS_OBS_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENS_OBS_THRESH`
     - ens.obs_thresh

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
   * - :term:`ENSEMBLE_STAT_NBRHD_PROB_WIDTH`
     - nbrhd_prob.width
   * - :term:`ENSEMBLE_STAT_NBRHD_PROB_SHAPE`
     - nbrhd_prob.shape
   * - :term:`ENSEMBLE_STAT_NBRHD_PROB_VLD_THRESH`
     - nbrhd_prob.vld_thresh

**${METPLUS_NMEP_SMOOTH_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_VLD_THRESH`
     - nmep_smooth.vld_thresh
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_SHAPE`
     - nmep_smooth.shape
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_DX`
     - nmep_smooth.gaussian_dx
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_RADIUS`
     - nmep_smooth.gaussian_radius
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_METHOD`
     - nmep_smooth.type.method
   * - :term:`ENSEMBLE_STAT_NMEP_SMOOTH_WIDTH`
     - nmep_smooth.type.width

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

**${METPLUS_ENSEMBLE_FLAG_DICT}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON`
     - ensemble_flag.latlon
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN`
     - ensemble_flag.mean
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV`
     - ensemble_flag.stdev
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS`
     - ensemble_flag.minus
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS`
     - ensemble_flag.plus
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN`
     - ensemble_flag.min
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX`
     - ensemble_flag.max
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE`
     - ensemble_flag.range
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT`
     - ensemble_flag.vld_count
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY`
     - ensemble_flag.frequency
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP`
     - ensemble_flag.nep
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP`
     - ensemble_flag.nmep
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_RANK`
     - ensemble_flag.rank
   * - :term:`ENSEMBLE_STAT_ENSEMBLE_FLAG_WEIGHT`
     - ensemble_flag.weight

**${METPLUS_OUTPUT_PREFIX}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_OUTPUT_PREFIX`
     - output_prefix

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`ENSEMBLE_STAT_MET_CONFIG_OVERRIDES`
     - n/a

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
paired tropical cyclone tracks that are created by the tc_pairs_wrapper.
Unlike the other wrappers, the extract_tiles_wrapper does not correspond
to a specific MET tool. It invokes the tc_stat_wrapper, which in turn
calls the MET tc_stat tool to determine the lat/lon positions of the
paired track data. This information is then used to create tiles of
subregions. The ExtractTiles wrapper creates a 2n degree x 2m degree
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
| :term:`GRID_DIAG_VERIFICATION_MASK_TEMPLATE` (optional)
| :term:`LOG_GRID_DIAG_VERBOSITY`
| :term:`GRID_DIAG_CONFIG_FILE`
| :term:`GRID_DIAG_CUSTOM_LOOP_LIST`
| :term:`GRID_DIAG_INPUT_DATATYPE`
| :term:`GRID_DIAG_REGRID_METHOD`
| :term:`GRID_DIAG_REGRID_WIDTH`
| :term:`GRID_DIAG_REGRID_VLD_THRESH`
| :term:`GRID_DIAG_REGRID_SHAPE`
| :term:`GRID_DIAG_REGRID_TO_GRID`
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

`MET_INSTALL_DIR/share/met/config/GridDiagConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/GridDiagConfig_default>`_

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
| :term:`GRID_STAT_VERIFICATION_MASK_TEMPLATE` (optional)
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
| :term:`GRID_STAT_CLIMO_CDF_BINS`
| :term:`GRID_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`GRID_STAT_CLIMO_CDF_WRITE_BINS`
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
| :term:`GRID_STAT_CLIMO_MEAN_FIELD`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`GRID_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`GRID_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`GRID_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`GRID_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`GRID_STAT_CLIMO_STDEV_FIELD`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`GRID_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`GRID_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`GRID_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL`
| :term:`GRID_STAT_MASK_GRID` (optional)
| :term:`GRID_STAT_MASK_POLY` (optional)
| :term:`GRID_STAT_MET_CONFIG_OVERRIDES`
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

`MET_INSTALL_DIR/share/met/config/GridStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/GridStatConfig_default>`_

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


.. _make_plots_wrapper:

MakePlots
=========

Description
-----------

The MakePlots wrapper creates various statistical plots using python
scripts for the various METplus Wrappers use cases. This can only be run
following StatAnalysis wrapper when LOOP_ORDER = processes. To run
MakePlots wrapper, include MakePlots in PROCESS_LIST.

METplus Configuration
---------------------

The following values **must** be defined in the METplus Wrappers
configuration file:

| :term:`MAKE_PLOTS_SCRIPTS_DIR`
| :term:`MAKE_PLOTS_INPUT_DIR`
| :term:`MAKE_PLOTS_OUTPUT_DIR`
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
|

The following values are **optional** in the METplus Wrappers
configuration file:

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
|

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
   |

.. _met_db_load_wrapper:

METdbLoad
=========

Description
-----------

Used to call the met_db_load.py script from dtcenter/METdatadb to load MET
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
| :term:`MODE_MATCH_FLAG`
| :term:`MODE_MAX_CENTROID_DIST`
| :term:`MODE_TOTAL_INTEREST_THRESH`
| :term:`MODE_INTEREST_FUNCTION_CENTROID_DIST`
| :term:`MODE_INTEREST_FUNCTION_BOUNDARY_DIST`
| :term:`MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST`
| :term:`FCST_MODE_VAR<n>_NAME` (optional)
| :term:`FCST_MODE_VAR<n>_LEVELS` (optional)
| :term:`FCST_MODE_VAR<n>_THRESH` (optional)
| :term:`FCST_MODE_VAR<n>_OPTIONS` (optional)
| :term:`OBS_MODE_VAR<n>_NAME` (optional)
| :term:`OBS_MODE_VAR<n>_LEVELS` (optional)
| :term:`OBS_MODE_VAR<n>_THRESH` (optional)
| :term:`OBS_MODE_VAR<n>_OPTIONS` (optional)
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

`MET_INSTALL_DIR/share/met/config/MODEConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/MODEConfig_default>`_

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
| :term:`MTD_MET_CONFIG_OVERRIDES`
| :term:`FCST_MTD_VAR<n>_NAME` (optional)
| :term:`FCST_MTD_VAR<n>_LEVELS` (optional)
| :term:`FCST_MTD_VAR<n>_THRESH` (optional)
| :term:`FCST_MTD_VAR<n>_OPTIONS` (optional)
| :term:`OBS_MTD_VAR<n>_NAME` (optional)
| :term:`OBS_MTD_VAR<n>_LEVELS` (optional)
| :term:`OBS_MTD_VAR<n>_THRESH` (optional)
| :term:`OBS_MTD_VAR<n>_OPTIONS` (optional)
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

`MET_INSTALL_DIR/share/met/config/MTDConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/MTDConfig_default>`_

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
| :term:`PB2NC_MET_CONFIG_OVERRIDES`
| :term:`PB2NC_PB_REPORT_TYPE`
| :term:`PB2NC_LEVEL_RANGE_BEG`
| :term:`PB2NC_LEVEL_RANGE_END`
| :term:`PB2NC_LEVEL_CATEGORY`
| :term:`PB2NC_QUALITY_MARK_THRESH`

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

`MET_INSTALL_DIR/share/met/config/PB2NCConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/PB2NCConfig_default>`_

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
   * - :term:`PB2NC_WINDOW_BEGIN`
     - obs_window.beg
   * - :term:`PB2NC_WINDOW_END`
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


.. _pcp_combine_wrapper:

PCPCombine
==========

Description
-----------

The PCPCombine wrapper is a Python script that encapsulates the MET
PCPCombine tool. It provides the infrastructure to combine or extract
from files to build desired accumulations.

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
| :term:`FCST_PCP_COMBINE_EXTRA_NAMES` (optional)
| :term:`FCST_PCP_COMBINE_EXTRA_LEVELS` (optional)
| :term:`FCST_PCP_COMBINE_EXTRA_OUTPUT_NAMES` (optional)
| :term:`OBS_PCP_COMBINE_EXTRA_NAMES` (optional)
| :term:`OBS_PCP_COMBINE_EXTRA_LEVELS` (optional)
| :term:`OBS_PCP_COMBINE_EXTRA_OUTPUT_NAMES` (optional)
| :term:`FCST_PCP_COMBINE_OUTPUT_ACCUM` (optional)
| :term:`FCST_PCP_COMBINE_OUTPUT_NAME` (optional)
| :term:`OBS_PCP_COMBINE_OUTPUT_ACCUM` (optional)
| :term:`OBS_PCP_COMBINE_OUTPUT_NAME` (optional)
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
|

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
| :term:`POINT_STAT_VERIFICATION_MASK_TEMPLATE` (optional)
| :term:`POINT_STAT_OUTPUT_PREFIX`
| :term:`LOG_POINT_STAT_VERBOSITY`
| :term:`POINT_STAT_OFFSETS`
| :term:`FCST_POINT_STAT_INPUT_DATATYPE`
| :term:`OBS_POINT_STAT_INPUT_DATATYPE`
| :term:`POINT_STAT_CONFIG_FILE`
| :term:`MODEL`
| :term:`POINT_STAT_REGRID_TO_GRID`
| :term:`POINT_STAT_REGRID_METHOD`
| :term:`POINT_STAT_REGRID_WIDTH`
| :term:`POINT_STAT_REGRID_VLD_THRESH`
| :term:`POINT_STAT_REGRID_SHAPE`
| :term:`POINT_STAT_GRID`
| :term:`POINT_STAT_POLY`
| :term:`POINT_STAT_STATION_ID`
| :term:`POINT_STAT_MESSAGE_TYPE`
| :term:`POINT_STAT_CUSTOM_LOOP_LIST`
| :term:`POINT_STAT_SKIP_IF_OUTPUT_EXISTS`
| :term:`POINT_STAT_DESC`
| :term:`POINT_STAT_MET_CONFIG_OVERRIDES`
| :term:`POINT_STAT_CLIMO_CDF_BINS`
| :term:`POINT_STAT_CLIMO_CDF_CENTER_BINS`
| :term:`POINT_STAT_CLIMO_CDF_WRITE_BINS`
| :term:`POINT_STAT_OBS_QUALITY`
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
| :term:`POINT_STAT_OUTPUT_FLAG_RPS`
| :term:`POINT_STAT_OUTPUT_FLAG_ECLV`
| :term:`POINT_STAT_OUTPUT_FLAG_MPR`
| :term:`POINT_STAT_INTERP_VLD_THRESH`
| :term:`POINT_STAT_INTERP_SHAPE`
| :term:`POINT_STAT_INTERP_TYPE_METHOD`
| :term:`POINT_STAT_INTERP_TYPE_WIDTH`
| :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`
| :term:`POINT_STAT_CLIMO_MEAN_FIELD`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_METHOD`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_WIDTH`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`POINT_STAT_CLIMO_MEAN_REGRID_SHAPE`
| :term:`POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`POINT_STAT_CLIMO_MEAN_MATCH_MONTH`
| :term:`POINT_STAT_CLIMO_MEAN_DAY_INTERVAL`
| :term:`POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`POINT_STAT_CLIMO_STDEV_FILE_NAME`
| :term:`POINT_STAT_CLIMO_STDEV_FIELD`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_METHOD`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_WIDTH`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`POINT_STAT_CLIMO_STDEV_REGRID_SHAPE`
| :term:`POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`POINT_STAT_CLIMO_STDEV_MATCH_MONTH`
| :term:`POINT_STAT_CLIMO_STDEV_DAY_INTERVAL`
| :term:`POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL`
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

`MET_INSTALL_DIR/share/met/config/PointStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/PointStatConfig_default>`_

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

**${METPLUS_OBS_QUALITY}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`POINT_STAT_OBS_QUALITY`
     - obs_quality

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
   * - :term:`POINT_STAT_OUTPUT_FLAG_RPS`
     - output_flag.rps
   * - :term:`POINT_STAT_OUTPUT_FLAG_ECLV`
     - output_flag.eclv
   * - :term:`POINT_STAT_OUTPUT_FLAG_MPR`
     - output_flag.mpr

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
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME` (optional)
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL` (optional)
| :term:`FCST_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL` (optional)
| :term:`OBS_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME` (optional)
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
| :term:`SERIES_ANALYSIS_MET_CONFIG_OVERRIDES`
| :term:`FCST_SERIES_ANALYSIS_INPUT_DIR`
| :term:`OBS_SERIES_ANALYSIS_INPUT_DIR`
| :term:`SERIES_ANALYSIS_TC_STAT_INPUT_DIR`
| :term:`SERIES_ANALYSIS_OUTPUT_DIR`
| :term:`FCST_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`OBS_SERIES_ANALYSIS_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_OUTPUT_TEMPLATE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_FIELD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_FIELD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL`
| :term:`SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL`
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

`MET_INSTALL_DIR/share/met/config/SeriesAnalysisConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/SeriesAnalysisConfig_default>`_

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

**${METPLUS_CTS_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_CTS_LIST`
     - output_stats.cts

**${METPLUS_STAT_LIST}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_STAT_LIST`
     - output_stats.cnt

**${METPLUS_MET_CONFIG_OVERRIDES}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`SERIES_ANALYSIS_MET_CONFIG_OVERRIDES`
     - n/a

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
filter the MET .stat files. StatAnalysis wrapper can be run in two
different methods. First is to look at the STAT lines for a single date,
to use this method set LOOP_ORDER = times. Second is to look at the STAT
lines over a span of dates, to use this method set LOOP_ORDER =
processes. To run StatAnalysis wrapper, include StatAnalysis in
PROCESS_LIST.

METplus Configuration
---------------------

The following values must be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

| :term:`STAT_ANALYSIS_OUTPUT_DIR`
| :term:`MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE`
| :term:`MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE`
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
| :term:`STAT_ANALYSIS_MET_CONFIG_OVERRIDES`
|

The following values are **optional** in the METplus Wrappers
configuration file for running with LOOP_ORDER = times:

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
|

The following values **must** be defined in the METplus Wrappers
configuration file for running with LOOP_ORDER = processes:

| :term:`STAT_ANALYSIS_OUTPUT_DIR`
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
|

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
|

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
   |

.. _stat-analysis-met-conf:

MET Configuration
-----------------

Below is the wrapped MET configuration file used for this wrapper.
Environment variables are used to control entries in this configuration file.
The default value for each environment variable is obtained from
(except where noted below):

`MET_INSTALL_DIR/share/met/config/STATAnalysisConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/STATAnalysisConfig_default>`_

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

`MET_INSTALL_DIR/share/met/config/TCGenConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/TCGenConfig_default>`_

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

`MET_INSTALL_DIR/share/met/config/TCPairsConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/TCPairsConfig_default>`_

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

**${METPLUS_INIT_INCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_INCLUDE`
     - init_inc

**${METPLUS_INIT_EXCLUDE}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`TC_PAIRS_INIT_EXCLUDE`
     - init_exc

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
| :term:`TC_RMW_OUTPUT_TEMPLATE`
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

`MET_INSTALL_DIR/share/met/config/TCRMWConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/TCRMWConfig_default>`_

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

`MET_INSTALL_DIR/share/met/config/TCStatConfig_default <https://github.com/dtcenter/MET/blob/HEAD/met/data/config/TCStatConfig_default>`_

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

METplus Configuration
---------------------

| :term:`USER_SCRIPT_RUNTIME_FREQ`
| :term:`USER_SCRIPT_COMMAND`
| :term:`USER_SCRIPT_CUSTOM_LOOP_LIST`
| :term:`USER_SCRIPT_SKIP_TIMES`
|
