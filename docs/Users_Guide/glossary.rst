******************************
METplus Configuration Glossary
******************************

.. glossary::
   :sorted:

   REGRID_DATA_PLANE_ONCE_PER_FIELD
     If True, run RegridDataPlane separately for each field name/level combination specified in the configuration file. See  :ref:`Field_Info` for more information on how fields are specified. If False, run RegridDataPlane once with all of the fields specified.

     | *Used by:*  RegridDataPlane

   CUSTOM_LOOP_LIST
     List of strings that are used to run each item in the :term:`PROCESS_LIST` multiple times for each run time to allow the tool to be run with different configurations. The filename template tag {custom?fmt=%s} can be used throughout the METplus configuration file. For example, the text can be used to supply different configuration files (if the MET tool uses them) and output filenames/directories. If you have two configuration files, SeriesAnalysisConfig_one and SeriesAnalysisConfig_two, you can set::

       [config]
       CUSTOM_LOOP_LIST = one, two
       SERIES_ANALYSIS_CONFIG_FILE = {CONFIG_DIR}/SeriesAnalysisConfig_{custom?fmt=%s}

       [dir]
       SERIES_ANALYSIS_OUTPUT_DIR = {OUTPUT_BASE}/{custom?fmt=%s}

    With this configuration, SeriesAnalysis will be called twice. The first run will use SeriesAnalysisConfig_one and write output to {OUTPUT_BASE}/one. The second run will use SeriesAnalysisConfig_two and write output to {OUTPUT_BASE}/two.

    If unset or left blank, the wrapper will run once per run time. There are also wrapper-specific configuration variables to define a custom string loop list for a single wrapper, i.e. :term:`SERIES_ANALYSIS_CUSTOM_LOOP_LIST` and :term:`PCP_COMBINE_CUSTOM_LOOP_LIST`.

     | *Used by:* Many

   SERIES_ANALYSIS_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* SeriesAnalysis

   PCP_COMBINE_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* PCPCombine

   ASCII2NC_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* ASCII2NC

   ENSEMBLE_STAT_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* EnsembleStat

   EXAMPLE_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* Example

   GEMPAKTOCF_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* GempakToCF

   GRID_STAT_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* GridStat

   MODE_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* MODE

   MTD_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* MTD

   PB2NC_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* PB2NC

   POINT_STAT_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* PointStat

   PY_EMBED_INGEST_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* PyEmbedIngest

   REGRID_DATA_PLANE_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* RegridDataPlane

   TC_GEN_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* TCGen

   TC_PAIRS_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* TCPairs

   EXTRACT_TILES_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* ExtractTiles

   POINT2GRID_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* Point2Grid

   GROUP_LIST_ITEMS
     Names of the lists in the METplus .conf file to treat the items in those lists as a group.

     | *Used by:* MakePlots, StatAnalysis

   LOOP_LIST_ITEMS
     Names of the lists in the METplus .conf file to treat the items in those lists individually.

     | *Used by:* MakePlots, StatAnalysis

   MAKE_PLOTS_AVERAGE_METHOD
     The method to use to average the data. Valid options are MEAN, MEDIAN, and AGGREGATION.

     | *Used by:* MakePlots

   MAKE_PLOTS_SCRIPTS_DIR
     Directory to find scripts used by MakePlots.

     | *Used by:* MakePlots

   MAKE_PLOTS_INPUT_DIR
     Directory containing input files used by MakePlots.

     | *Used by:* MakePlots

   MAKE_PLOTS_OUTPUT_DIR
     Directory to write files generated by MakePlots.

     | *Used by:* MakePlots

   MAKE_PLOTS_VERIF_CASE
     Verification case used by MakePlots. Valid options for this include: grid2grid, grid2obs, precip.

     | *Used by:* MakePlots

   CYCLONE_PLOTTER_OUTPUT_DIR
     Directory for saving files generated by CyclonePlotter.

     | *Used by:* CyclonePlotter

   CYCLONE_PLOTTER_MODEL
     Model used in CyclonePlotter.

     | *Used by:* CyclonePlotter

   TCMPR_PLOTTER_PREFIX
     Prefix used in TCMPRPlotter.

     | *Used by:* TCMPRPlotter

   TCMPR_PLOTTER_CONFIG_FILE
     Configuration file used by TCMPRPlotter.

     | *Used by:* TCMPRPlotter

   ASCII2NC_WINDOW_BEGIN
     Passed to the ASCII2NC MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, ASCII2NC will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  ASCII2NC

   ASCII2NC_WINDOW_END
     Passed to the ASCII2NC MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, ASCII2NC will use :term:`OBS_WINDOW_END`.

     | *Used by:*  ASCII2NC

   POINT2GRID_GAUSSIAN_DX
     Gaussian dx value to add to the Point2Grid command line call with -gaussian_dx. Not added to call if unset or set to empty string.

     | *Used by:* Point2Grid

   POINT2GRID_GAUSSIAN_RADIUS
     Gaussian radius value to add to the Point2Grid command line call with -gaussian_radius. Not added to call if unset or set to empty string.

     | *Used by:* Point2Grid

   REGRID_DATA_PLANE_GAUSSIAN_DX
     Gaussian dx value to add to the RegridDataPlane command line call with -gaussian_dx. Not added to call if unset or set to empty string.

     | *Used by:* RegridDataPlane

   REGRID_DATA_PLANE_GAUSSIAN_RADIUS
     Gaussian radius value to add to the RegridDataPlane command line call with -gaussian_radius. Not added to call if unset or set to empty string.

     | *Used by:* RegridDataPlane

   FCST_PCP_COMBINE_CONSTANT_INIT
     If True, only look for forecast files that have a given initialization time. Used only if :term:`FCST_PCP_COMBINE_INPUT_TEMPLATE` has a 'lead' tag. If set to False, the lowest forecast lead for each search (valid) time is used. See :term:`OBS_PCP_COMBINE_CONSTANT_INIT`

     | *Used by:* PCPCombine

   OBS_PCP_COMBINE_CONSTANT_INIT
     If True, only look for observation files that have a given initialization time. Used only if :term:`OBS_PCP_COMBINE_INPUT_TEMPLATE` has a 'lead' tag. If set to False, the lowest forecast lead for each search (valid) time is used. This variable is only used if model data is used as the OBS to compare to other model data as the FCST.

     | *Used by:* PCPCombine

   CURRENT_FCST_NAME
     Generated by METplus in wrappers that loop over forecast names/levels to keep track of the current forecast name that is being processed. It can be referenced in the [GRID_STAT/MODE/MTD]_OUTPUT_PREFIX to set the output file names. This should not be set by a user!

     | *Used by:* GridStat, MODE, MTD

   CURRENT_OBS_NAME
     Generated by METplus in wrappers that loop over observation names/levels to keep track of the current observation name that is being processed. It can be referenced in the [GRID_STAT/MODE/MTD]_OUTPUT_PREFIX to set the output file names. This should not be set by a user!

     | *Used by:* GridStat, MODE, MTD

   CURRENT_FCST_LEVEL
     Generated by METplus in wrappers that loop over forecast names/levels to keep track of the current forecast level that is being processed. It can be referenced in the [GRID_STAT/MODE/MTD]_OUTPUT_PREFIX to set the output file names. This should not be set by a user!

     | *Used by:* GridStat, MODE, MTD

   CURRENT_OBS_LEVEL
     Generated by METplus in wrappers that loop over observation names/levels to keep track of the current observation level that is being processed. It can be referenced in the [GRID_STAT/MODE/MTD]_OUTPUT_PREFIX to set the output file names. This should not be set by a user!

     | *Used by:* GridStat, MODE, MTD


   CYCLONE_PLOTTER_INPUT_DIR
      The directory containing the input data to be plotted.

     | *Used by:* CyclonePlotter

   ANLY_ASCII_REGEX_LEAD
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_PREFIX` instead.

   ANLY_NC_TILE_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_PREFIX` instead.

   ENSEMBLE_STAT_OUTPUT_PREFIX
     String to pass to the MET config file to prepend text to the output filenames.

     | *Used by:* EnsembleStat

   GRID_STAT_OUTPUT_PREFIX
     String to pass to the MET config file to prepend text to the output filenames.

     | *Used by:* GridStat

   POINT_STAT_OUTPUT_PREFIX
     String to pass to the MET config file to prepend text to the output filenames.

     | *Used by:* PointStat

   MODE_OUTPUT_PREFIX
     String to pass to the MET config file to prepend text to the output filenames.

     | *Used by:* MODE

   MTD_OUTPUT_PREFIX
     String to pass to the MET config file to prepend text to the output filenames.

     | *Used by:* MTD

   OBS_SERIES_ANALYSIS_ASCII_REGEX_LEAD
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_PREFIX` instead.

   OBS_SERIES_ANALYSIS_NC_TILE_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_PREFIX` instead.

   ANLY_TILE_PREFIX
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_PREFIX` instead.

   ANLY_TILE_REGEX
     .. warning:: **DEPRECATED:** No longer used. The regular expression for the analysis input file. The file is in GRIBv2 format.

   OBS_EXTRACT_TILES_PREFIX
     Prefix for observation tile files. Used to create filename of intermediate files that are created while performing a series analysis.

     | *Used by:*  ExtractTiles

   CYCLONE_INPUT_DIR
     Input directory for the cyclone plotter. This should be the output directory for the MET TC-Pairs utility

     | *Used by:* CyclonePlotter

   FCST_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME
     Specify the forecast output field name that is created by RegridDataPlane. The name corresponds to :term:`FCST_VAR<n>_NAME`. This is used when using Python Embedding as input to the MET tool, because the :term:`FCST_VAR<n>_NAME` defines the python script to call.

     | *Used by:* RegridDataPlane


   OBS_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME
     Specify the observation output field name that is created by RegridDataPlane. The name corresponds to :term:`OBS_VAR<n>_NAME`. This is used when using Python Embedding as input to the MET tool, because the :term:`OBS_VAR<n>_NAME` defines the python script to call.

     | *Used by:* RegridDataPlane

   POINT2GRID_WINDOW_BEGIN
     Specify the beginning of the time window to use for a date stamp window to grab observations

     | *Used by:* Point2Grid

   POINT2GRID_WINDOW_END
     Specify the end of the time window to use for a date stamp window to grab observations

     | *Used by:* Point2Grid


   POINT2GRID_INPUT_FIELD
     Specify the input field name that is read by Point2Grid.

     | *Used by:* Point2Grid

   POINT2GRID_INPUT_LEVEL
     Specify the input level name that is read by Point2Grid.

     | *Used by:* Point2Grid

   POINT2GRID_QC_FLAGS
     Specify the qc flags name that is read by Point2Grid.

     | *Used by:* Point2Grid

   POINT2GRID_ADP
     Provides an additional Aerosol Detection Product when GOES 16/17 input and an AOD variable name is used.

     | *Used by:* Point2Grid

   POINT2GRID_PROB_CAT_THRESH
     Specify the probability threshold for practically perfect forecasts

     | *Used by:* Point2Grid

   POINT2GRID_VLD_THRESH
     Specify the required ratio of valid data for regridding

     | *Used by:* Point2Grid

   FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME
     Specify the (optional) forecast input field name that is read by RegridDataPlane. The name corresponds to :term:`FCST_VAR<n>_NAME`. This is used when using Python Embedding as input to the MET tool, because the :term:`FCST_VAR<n>_NAME` defines the python script to call.

     | *Used by:* RegridDataPlane


   OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME
     Specify the (optional) observation input field name that is created by RegridDataPlane. The name corresponds to :term:`OBS_VAR<n>_NAME`. This is used when using Python Embedding as input to the MET tool, because the :term:`OBS_VAR<n>_NAME` defines the python script to call.

     | *Used by:* RegridDataPlane

   FCST_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL
     Specify the (optional) forecast input field level that is read by RegridDataPlane. The name corresponds to :term:`FCST_VAR<n>_LEVELS`. This is used when using Python Embedding as input to the MET tool, because the :term:`FCST_VAR<n>_LEVELS` defines the python script to call.

     | *Used by:* RegridDataPlane


   OBS_REGRID_DATA_PLANE_VAR<n>_INPUT_LEVEL
     Specify the (optional) observation input field level that is created by RegridDataPlane. The name corresponds to :term:`OBS_VAR<n>_LEVELS`. This is used when using Python Embedding as input to the MET tool, because the :term:`OBS_VAR<n>_LEVELS` defines the python script to call.

     | *Used by:* RegridDataPlane

   LOG_ASCII2NC_VERBOSITY
     Overrides the log verbosity for ASCII2NC only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* ASCII2NC

   LOG_SERIES_ANALYSIS_VERBOSITY
     Overrides the log verbosity for SeriesAnalysis only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* SeriesAnalysis

   LOG_ENSEMBLE_STAT_VERBOSITY
     Overrides the log verbosity for EnsembleStat only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* EnsembleStat

   LOG_STAT_ANALYSIS_VERBOSITY
     Overrides the log verbosity for StatAnalysis only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* StatAnalysis

   LOG_GRID_STAT_VERBOSITY
     Overrides the log verbosity for GridStat only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* GridStat

   LOG_MODE_VERBOSITY
     Overrides the log verbosity for MODE only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* MODE

   LOG_MTD_VERBOSITY
     Overrides the log verbosity for MTD only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* MTD

   LOG_PB2NC_VERBOSITY
     Overrides the log verbosity for PB2NC only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* PB2NC

   LOG_PCP_COMBINE_VERBOSITY
     Overrides the log verbosity for PCPCombine only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* PCPCombine

   LOG_POINT_STAT_VERBOSITY
     Overrides the log verbosity for PointStat only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* PointStat

   LOG_REGRID_DATA_PLANE_VERBOSITY
     Overrides the log verbosity for RegridDataPlane only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* RegridDataPlane

   LOG_TC_PAIRS_VERBOSITY
     Overrides the log verbosity for TCPairs only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* TCPairs

   LOG_TC_RMW_VERBOSITY
     Overrides the log verbosity for TCRMW  only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* TCRMW

   LOG_TC_STAT_VERBOSITY
     Overrides the log verbosity for TCStat only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* TCStat

   LOG_LINE_FORMAT
     Defines the formatting of each METplus log output line. For more information on acceptable values, see the Python documentation for LogRecord: https://docs.python.org/3/library/logging.html#logging.LogRecord

     | *Used by:* All

   LOG_LINE_DATE_FORMAT
     Defines the formatting of the date in the METplus log output. See :term:`LOG_LINE_FORMAT`.

     | *Used by:* All

   FCST_PCP_COMBINE_COMMAND
     Used only when :term:`FCST_PCP_COMBINE_METHOD` = USER_DEFINED. Custom command to run PCPCombine with a complex call that doesn't fit common use cases. Value can include filename template syntax, i.e. {valid?fmt=%Y%m%d}, that will be substituted based on the current runtime. The name of the application and verbosity flag does not need to be included. For example, if set to '-derive min,max /some/file' the command run will be pcp_combine -v 2 -derive min,max /some/file. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_COMMAND`.

     | *Used by:* PCPCombine

   OBS_PCP_COMBINE_COMMAND
     Used only when :term:`OBS_PCP_COMBINE_METHOD` = USER_DEFINED. Custom command to run PCPCombine with a complex call that doesn't fit common use cases. Value can include filename template syntax, i.e. {valid?fmt=%Y%m%d}, that will be substituted based on the current runtime. The name of the application and verbosity flag does not need to be included. For example, if set to '-derive min,max /some/file' the command run will be pcp_combine -v 2 -derive min,max /some/file. A corresponding variable exists for forecast data called :term:`FCST_PCP_COMBINE_COMMAND`.

     | *Used by:* PCPCombine

   PY_EMBED_INGEST_<n>_SCRIPT
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the python script with arguments to run through RegridDataPlane to generate a file that can be read by the MET tools. This variable supports filename template syntax, so you can specify filenames with time information, i.e. {valid?fmt=%Y%m%d}. See also :term:`PY_EMBED_INGEST_<n>_TYPE`, :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`, :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`.

     | *Used by:* PyEmbedIngest

   PY_EMBED_INGEST_<n>_TYPE
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the type of output generated by the Python script. Valid options are NUMPY, XARRAY, and PANDAS. See also :term:`PY_EMBED_INGEST_<n>_SCRIPT`, :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`, :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`.

     | *Used by:* PyEmbedIngest

   PY_EMBED_INGEST_<n>_OUTPUT_GRID
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the grid information that RegridDataPlane will use to generate a file that can be read by the MET tools. This can be a file path or a grid definition. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information. See also :term:`PY_EMBED_INGEST_<n>_TYPE`, :term:`PY_EMBED_INGEST_<n>_SCRIPT`, :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`.

     | *Used by:* PyEmbedIngest

   PY_EMBED_INGEST_<n>_OUTPUT_FIELD_NAME
     Used to specify the forecast output field name that is created by RegridDataPlane. If this option is not set, RegridDataPlane will call the field name "name_level".

     | *Used by:* PyEmbedIngest

   PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the output filename using filename template syntax. The value will be substituted with time information and appended to :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR` if it is set. See also :term:`PY_EMBED_INGEST_<n>_TYPE`, :term:`PY_EMBED_INGEST_<n>_SCRIPT`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`.

     | *Used by:* PyEmbedIngest

   PY_EMBED_INGEST_<n>_OUTPUT_DIR
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the output diirectory to write data. See also :term:`PY_EMBED_INGEST_<n>_TYPE`, :term:`PY_EMBED_INGEST_<n>_SCRIPT`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`, and :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`.

     | *Used by:* PyEmbedIngest

   CUSTOM_INGEST_<n>_SCRIPT
     .. warning:: **DEPRECATED:** Please use :term:`PY_EMBED_INGEST_<n>_SCRIPT`.

   CUSTOM_INGEST_<n>_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`PY_EMBED_INGEST_<n>_TYPE`.

   CUSTOM_INGEST_<n>_OUTPUT_GRID
     .. warning:: **DEPRECATED:** Please use :term:`PY_EMBED_INGEST_<n>_OUTPUT_GRID`.

   CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE`.

   CUSTOM_INGEST_<n>_OUTPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`PY_EMBED_INGEST_<n>_OUTPUT_DIR`.

   ASCII2NC_CONFIG_FILE
     Path to optional configuration file read by ASCII2NC.

     | *Used by:* ASCII2NC

   ASCII2NC_SKIP_IF_OUTPUT_EXISTS
     If True, do not run ASCII2NC if output file already exists. Set to False to overwrite files.

     | *Used by:*  ASCII2NC

   TC_STAT_CONFIG_FILE
     Path to optional configuration file read by TCStat.

     | *Used by:* TCStat

   TC_RMW_CONFIG_FILE
     Path to optional configuration file read by TCRMW.

     | *Used by:* TCRMW

   ASCII2NC_INPUT_FORMAT
     Optional string to specify the format of the input data. Valid options are "met_point", "little_r", "surfrad", "wwsis", "aeronet", "aeronetv2", or "aeronetv3."

     | *Used by:* ASCII2NC

   ASCII2NC_MASK_GRID
     Named grid or a data file defining the grid for filtering the point observations spatially (optional).

     | *Used by:* ASCII2NC

   ASCII2NC_MASK_POLY
     A polyline file, the output of gen_vx_mask, or a gridded data file with field information for filtering the point observations spatially (optional).

     | *Used by:* ASCII2NC

   ASCII2NC_MASK_SID
     A station ID masking file or a comma-separated list of station ID's for filtering the point observations spatially (optional).

     | *Used by:* ASCII2NC

   ASCII2NC_INPUT_DIR
     Directory containing input data to ASCII2NC. This variable is optional because you can specify the full path to the input files using :term:`ASCII2NC_INPUT_TEMPLATE`.

     | *Used by:* ASCII2NC

   ASCII2NC_INPUT_TEMPLATE
     Filename template of the input file used by ASCII2NC. See also :term:`ASCII2NC_INPUT_DIR`.

     | *Used by:* ASCII2NC

   EXAMPLE_INPUT_DIR
     Directory containing fake input data for Example wrapper. This variable is optional because you can specify the full path to the input files using :term:`EXAMPLE_INPUT_TEMPLATE`.

     | *Used by:* Example

   EXAMPLE_INPUT_TEMPLATE
     Filename template of the fake input files used by Example wrapper to demonstrate how filename templates correspond to run times. See also :term:`EXAMPLE_INPUT_DIR`.

     | *Used by:* Example

   PB2NC_INPUT_TEMPLATE
     Filename template of the input file used by PB2NC. See also :term:`PB2NC_INPUT_DIR`.

     | *Used by:* PB2NC

   ASCII2NC_OUTPUT_DIR
     Directory to write output data generated by ASCII2NC. This variable is optional because you can specify the full path to the output files using :term:`ASCII2NC_OUTPUT_TEMPLATE`.

     | *Used by:* ASCII2NC

   ASCII2NC_OUTPUT_TEMPLATE
     Filename template of the output file generated by ASCII2NC. See also :term:`ASCII2NC_OUTPUT_DIR`.

     | *Used by:* ASCII2NC

   SERIES_ANALYSIS_OUTPUT_TEMPLATE
     Filename template of the output file generated by SeriesAnalysis. See also :term:`SERIES_ANALYSIS_OUTPUT_DIR`.

     | *Used by:* SeriesAnalysis

   ASCII2NC_TIME_SUMMARY_FLAG
     Boolean value to turn on/off time summarization. Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_RAW_DATA
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_BEG
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_END
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_STEP
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_WIDTH
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_GRIB_CODES
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_VAR_NAMES
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_TYPES
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_VALID_FREQ
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_TIME_SUMMARY_VALID_THRESH
     Read by the ASCII2NC configuration file if specified by :term:`ASCII2NC_CONFIG_FILE`. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding ASCII2NC configuration files for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if an ASCII2NC input file should be used for processing. Overrides :term:`OBS_FILE_WINDOW_BEGIN`. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* ASCII2NC

   ASCII2NC_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if an ASCII2NC input file should be used for processing. Overrides :term:`OBS_FILE_WINDOW_BEGIN`. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* ASCII2NC

   CLIMO_GRID_STAT_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`.

   GRID_STAT_CLIMO_MEAN_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`.

     | *Used by:* GridStat

   CLIMO_GRID_STAT_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`.

   GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_MEAN_FILE_NAME`.

   CLIMO_POINT_STAT_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`.


   POINT2GRID_INPUT_TEMPLATE
     Filename template for the point file used by Point2Grid.

     | *Used by:* Point2Grid

   POINT2GRID_OUTPUT_TEMPLATE
     Filename template for the output of  Point2Grid.

     | *Used by:* Point2Grid

   POINT2GRID_INPUT_DIR
     Directory containing the file containing point data used by point2grid. This variable is optional because you can specify the full path to a point file using :term:`POINT2GRID_INPUT_TEMPLATE`.

     | *Used by:* Point2Grid

   POINT_STAT_CLIMO_MEAN_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`.

   CLIMO_POINT_STAT_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`.

   POINT_STAT_CLIMO_MEAN_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_MEAN_FILE_NAME`.

   ENSEMBLE_STAT_CLIMO_MEAN_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME`.

   ENSEMBLE_STAT_CLIMO_MEAN_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME`.

   SERIES_ANALYSIS_CLIMO_MEAN_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME`.

   SERIES_ANALYSIS_CLIMO_MEAN_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME`.

   ENSEMBLE_STAT_CLIMO_STDEV_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME`.

   ENSEMBLE_STAT_CLIMO_STDEV_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME`.

   GRID_STAT_CLIMO_STDEV_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_STDEV_FILE_NAME`.

   GRID_STAT_CLIMO_STDEV_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CLIMO_STDEV_FILE_NAME`.

   POINT_STAT_CLIMO_STDEV_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_STDEV_FILE_NAME`.

   POINT_STAT_CLIMO_STDEV_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_CLIMO_STDEV_FILE_NAME`.

   SERIES_ANALYSIS_CLIMO_STDEV_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME`.

   SERIES_ANALYSIS_CLIMO_STDEV_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME`.

   ADECK_FILE_PREFIX
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_ADECK_TEMPLATE`.

   ADECK_TRACK_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_ADECK_INPUT_DIR`.

   AMODEL
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_AMODEL`.

   SERIES_ANALYSIS_GENERATE_PLOTS
     If set to True, run plot_data_plane and convert to generate images.
     Previously, plots were always generated.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_GENERATE_ANIMATIONS
     If set to True, create GIF animated images images.
     Previously, animated images were always generated.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_BACKGROUND_MAP
     Control whether or not a background map shows up for series analysis plots. Set to 'yes' if background map desired.

     | *Used by:*  SeriesAnalysis

   BACKGROUND_MAP
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_BACKGROUND_MAP` instead.

   BASIN
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_BASIN` or :term:`TC_STAT_BASIN`.

   BDECK_FILE_PREFIX
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_BDECK_TEMPLATE`.

   BDECK_TRACK_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_BDECK_INPUT_DIR`.

   BEG_TIME
     .. warning:: **DEPRECATED:** Please use :term:`INIT_BEG` or :term:`VALID_BEG` instead.

   BMODEL
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_BMODEL`.

   CI_METHOD
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_CI_METHOD`.

   MAKE_PLOTS_CI_METHOD
     The method for creating confidence intervals. Valid options are EMC, or NONE.

     | *Used by:*  MakePlots

   CYCLONE_CIRCLE_MARKER_SIZE
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE`.

   CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE
     Control the size of the circle marker in the cyclone plotter.

     | *Used by:*  CyclonePlotter

   CLOCK_TIME
     Automatically set by METplus with the time that the run was started. Setting this variable has no effect as it will be overwritten. Can be used for reference in metplus_final.conf or used with other config variables.

     | *Used by:*  All

   CONFIG_DIR
     Directory containing config files relevant to MET tools.

     | *Used by:*  EnsembleStat, GridStat, MODE, StatAnalysis

   CONFIG_FILE
     Specific configuration file name to use for MET tools.

     | *Used by:*  TCMPRPlotter

   CONVERT
     Path to the ImageMagick convert executable.

     | *Used by:*  PlotDataPlane

   CONVERT_EXE
     .. warning:: **DEPRECATED:** Please use :term:`CONVERT`.

   COV_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`COV_THRESH_LIST` instead.

   COV_THRESH_LIST
     Specify the values of the COV_THRESH column in the MET .stat file to use;

     | *Used by:*  MakePlots, StatAnalysis

   CYCLONE_CROSS_MARKER_SIZE
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_CROSS_MARKER_SIZE`.

   CYCLONE_PLOTTER_CROSS_MARKER_SIZE
     Control the size of the cross marker in the cyclone plotter.

     | *Used by:*  CyclonePlotter

   CUT
     Path to the Linux cut executable.

     | *Used by:*  PB2NC, PointStat

   CUT_EXE
     .. warning:: **DEPRECATED:** Please use :term:`CUT`.

   CYCLONE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_CYCLONE` or :term:`TC_STAT_CYCLONE`.

   CYCLONE_INIT_DATE
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_INIT_DATE` instead.

   CYCLONE_PLOTTER_INIT_HR
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_INIT_DATE` instead.

   CYCLONE_PLOTTER_INIT_DATE
     Initialization date for the cyclone forecasts in YYYYMMDD format.

     | *Used by:*  CyclonePlotter

   CYCLONE_INIT_HR
     Initialization hour for the cyclone forecasts in HH format.

     | *Used by:*  CyclonePlotter

   CYCLONE_MODEL
     Define the model being used for the tropical cyclone forecasts.

     | *Used by:*  CyclonePlotter

   CYCLONE_OUT_DIR
     Specify the directory where the output from the cyclone plotter should go.

     | *Used by:*  CyclonePlotter

   CYCLONE_PLOT_TITLE
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_PLOT_TITLE`.

   CYCLONE_PLOTTER_PLOT_TITLE
     Title string for the cyclone plotter.

     | *Used by:*  CyclonePlotter

   DEMO_YR
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_DEMO_YR` instead.

   TCMPR_PLOTTER_DEMO_YR
     The demo year. This is an optional value used by the plot_TCMPR.R script, (which is wrapped by TCMPRPlotter). Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more details.

     | *Used by:*  TCMPRPlotter

   DEP_VARS
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_DEP_VARS` instead.

   TCMPR_PLOTTER_DEP_VARS
     Corresponds to the optional flag -dep in the plot_TCMPR.R script, which is wrapped by TCMPRPlotter. The value to this flag is a comma-separated list (no whitespace) of dependent variable columns to plot ( e.g. AMSLP-BMSLP, AMAX_WIND-BMAX_WIND, TK_ERR). If this is undefined, then the default plot for TK_ERR (track error) is generated. Note, if you want the track error plot generated, in addition to other plots, then you need to explicitly list this with the other variables. Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more details.

     | *Used by:*  TCMPRPlotter

   DESC_LIST
     A single value or list of values used in the stat_analysis data stratification. Specifies the values of the DESC column in the MET .stat file to use.

     | *Used by:*  MakePlots, StatAnalysis

   ALPHA_LIST
     A single value or list of values used in the stat_analysis data stratification. Specifies the values of the ALPHA column in the MET .stat file to use.

     | *Used by:*  MakePlots, StatAnalysis

   DLAND_FILE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_DLAND_FILE`.

   EXTRACT_TILES_DLAT
     The latitude value, in degrees. Set to the value that defines the resolution of the data (in decimal degrees).

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_DLON
     The longitude value, in degrees. Set to the value that defines the resolution of the data (in decimal degrees).

     | *Used by:*  ExtractTiles

   DLAT
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_DLAT` instead.

   DLON
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_DLON` instead.

   EXTRACT_TILES_PAIRS_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_TC_STAT_INPUT_DIR` instead.

   EXTRACT_TILES_STAT_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_TC_STAT_INPUT_DIR` instead.

   EXTRACT_TILES_TC_STAT_INPUT_DIR
     Directory containing TCStat output to be read by ExtractTiles.

     | *Used by:*  ExtractTiles

   SERIES_ANALYSIS_STAT_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_TC_STAT_INPUT_DIR` instead.

   SERIES_ANALYSIS_TC_STAT_INPUT_DIR
     Directory containing TCStat output to be read by SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   DO_NOT_RUN_EXE
     True/False. If True, applications will not run and will only output command that would have been called.

     | *Used by:*  All

   END_DATE
     .. warning:: **DEPRECATED:** Please use :term:`INIT_END` or :term:`VALID_END` instead.

   END_HOUR
     .. warning:: **DEPRECATED:** Ending hour for analysis with format HH.

   END_TIME
     .. warning:: **DEPRECATED:** Ending date string for analysis with format YYYYMMDD.

   ENSEMBLE_STAT_CONFIG
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_CONFIG_FILE` instead.

   ENSEMBLE_STAT_CONFIG_FILE
     Specify the absolute path to the configuration file for the MET ensemble_stat tool.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENS_THRESH
     Threshold for the ratio of the number of valid ensemble fields to the total number of expected ensemble members. This value is passed into the ensemble_stat config file to make sure the percentage of files that are valid meets the expectation.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENS_VLD_THRESH
     Threshold for the ratio of the number of valid data values to the total number of expected ensemble members. This value is passed into the ensemble_stat config file to make sure the percentage of files that are valid meets the expectation.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENS_OBS_THRESH
     Sets the ens.obs_thresh value in the ensemble_stat MET config file.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_GRID_VX
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_REGRID_TO_GRID`.

   ENSEMBLE_STAT_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET EnsembleStat config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  EnsembleStat

   GRID_STAT_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET GridStat config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  GridStat

   POINT2GRID_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET Point2Grid config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  Point2Grid

   POINT_STAT_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET PointStat config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PointStat

   REGRID_TO_GRID
     .. warning:: **DEPRECATED:** Please use :term:`POINT_STAT_REGRID_TO_GRID` instead.


   MODE_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET MODE config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  MODE

   MTD_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET MTD config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  MTD

   SERIES_ANALYSIS_REGRID_TO_GRID
     Used to set the regrid dictionary item 'to_grid' in the MET SeriesAnalysis config file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_IS_PAIRED
     If true, the -paired flag is added to the SeriesAnalysis command.

     | *Used by:* SeriesAnalysis

   ENSEMBLE_STAT_MET_OBS_ERR_TABLE

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_MET_OBS_ERROR_TABLE
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE` instead.

   ENSEMBLE_STAT_N_MEMBERS
     Expected number of ensemble members found. This should correspond to the number of items in :term:`FCST_ENSEMBLE_STAT_INPUT_TEMPLATE`. If this number differs from the number of files are found for a given run, then ensemble_stat will not run for that time.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_DIR
     Specify the output directory where files from the MET ensemble_stat tool are written.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`ENSEMBLE_STAT_OUTPUT_DIR` instead.

   ENSEMBLE_STAT_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`ENSEMBLE_STAT_OUTPUT_DIR` using a template to allow run time information. If :term:`LOOP_BY` = VALID, default value is valid time YYYYMMDDHHMM/ensemble_stat. If :term:`LOOP_BY` = INIT, default value is init time YYYYMMDDHHMM/ensemble_stat.

     | *Used by:*  EnsembleStat

   ENS_VAR<n>_LEVELS
     Define the levels for the <n>th ensemble variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items. You can define NetCDF levels, such as (0,*,*), but you will need to surround these values with quotation marks so that the commas in the item are not interpreted as an item delimeter. Some examples:

     | ENS_VAR1_LEVELS = A06, P500
     | ENS_VAR2_LEVELS ="(0,*,*)", "(1,*,*)"

     There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | ENS_VAR1_LEVELS
     | ENS_VAR2_LEVELS
     | ...
     | ENS_VAR<n>_LEVELS

     See :ref:`Field_Info` for more information.

     | *Used by:*  EnsembleStat

   ENS_VAR<n>_NAME
     Define the name for the <n>th ensemble variable to be used in the analysis where <n> is an integer >= 1. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | ENS_VAR1_NAME
     | ENS_VAR2_NAME
     | ...
     | ENS_VAR<n>_NAME

     See :ref:`Field_Info` for more information.

     | *Used by:*  EnsembleStat

   ENS_VAR<n>_OPTIONS
     Define the options for the <n>th ensemble variable to be used in the analysis where <n> is an integer >= 1. These addition options will be applied to every name/level/threshold combination for VAR<n>. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | ENS_VAR1_OPTIONS
     | ENS_VAR2_OPTIONS
     | ...
     | ENS_VAR<n>_OPTION

     See :ref:`Field_Info` for more information.

     | *Used by:*  EnsembleStat

   ENS_VAR<n>_THRESH
     Define the threshold(s) for the <n>th ensemble variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items that must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le). There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | ENS_VAR1_THRESH
     | ENS_VAR2_THRESH
     | ...
     | ENS_VAR<n>_THRESH

     See :ref:`Field_Info` for more information.

     | *Used by:*  EnsembleStat

   EVENT_EQUALIZATION
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_EVENT_EQUALIZATION`.

   MAKE_PLOTS_EVENT_EQUALIZATION
     If event equalization is to be used (True) or not (False). If set to True, if any of the listed models are missing data for a particular time, data for all models will be masked out for this time. If set to False, there are no changes to the data.

     | *Used by:*  MakePlots

   EXTRACT_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_OUTPUT_DIR`.

   EXTRACT_TILES_FILTER_OPTS
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_JOB_ARGS` instead. Control what options are passed to the METplus extract_tiles utility.

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_OUTPUT_DIR
     Set the output directory for the METplus extract_tiles utility.

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_VAR_LIST
     Control what variables the METplus extract_tiles utility runs on. Additional filtering by summary (via the MET tc_stat tool). Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ (TC-STAT Tools) for all the available options for filtering by summary method in tc-stat. If no additional filtering is required, simply leave the value to :term:`EXTRACT_TILES_FILTER_OPTS` blank/empty in the METplus configuration file.

     | *Used by:*  ExtractTiles

   FCST_EXACT_VALID_TIME
     .. warning:: **DEPRECATED:** No longer used. Please use :term:`FCST_WINDOW_BEGIN` and :term:`FCST_WINDOW_END` instead. If both of those variables are set to 0, the functionality is the same as FCST_EXACT_VALID_TIME = True.

   FCST_<n>_FIELD_NAME
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_<n>_FIELD_NAME` where N >=1 instead.

   FCST_ASCII_REGEX_LEAD
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_PREFIX` instead.

   FCST_SERIES_ANALYSIS_ASCII_REGEX_LEAD
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_PREFIX` instead.

   FCST_ENSEMBLE_STAT_FILE_WINDOW_BEGIN
     See :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN`

     | *Used by:*

   FCST_ENSEMBLE_STAT_FILE_WINDOW_END
     See :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_END`

     | *Used by:*  EnsembleStat

   FCST_ENSEMBLE_STAT_INPUT_DIR
     Input directory for forecast files to use with the MET tool ensemble_stat. Corresponding variable exist for point and grid observation data called :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_DIR` and :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_DIR`.

     | *Used by:*  EnsembleStat

   FCST_ENSEMBLE_STAT_INPUT_TEMPLATE
     Template used to specify forecast input filenames for the MET tool ensemble_stat. Corresponding variables exist for point and grid observation data called :term:`OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE` and :term:`OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  EnsembleStat

   FCST_FILE_WINDOW_BEGIN
     See :term:`OBS_FILE_WINDOW_BEGIN`

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   FCST_FILE_WINDOW_END
     See :term:`OBS_FILE_WINDOW_END`

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   FCST_GEMPAK_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GEMPAKTOCF_INPUT_DIR` instead.

   FCST_GEMPAK_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`GEMPAKTOCF_INPUT_TEMPLATE` if GempakToCF is in the PROCESS_LIST.

   FCST_GRID_STAT_FILE_WINDOW_BEGIN
     See :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN`

     | *Used by:*  GridStat

   FCST_GRID_STAT_FILE_WINDOW_END
     See :term:`OBS_GRID_STAT_FILE_WINDOW_END`

     | *Used by:*  GridStat

   FCST_GRID_STAT_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET grid_stat tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A corresponding variable exists for observation data called :term:`OBS_GRID_STAT_INPUT_DATATYPE`.

     | *Used by:*  GridStat

   FCST_GRID_STAT_INPUT_DIR
     Input directory for forecast files to use with the MET tool grid_stat. A corresponding variable exists for observation data called :term:`OBS_GRID_STAT_INPUT_DIR`.

     | *Used by:*  GridStat

   FCST_GRID_STAT_INPUT_TEMPLATE
     Template used to specify forecast input filenames for the MET tool grid_stat. A corresponding variable exists for observation data called :term:`OBS_GRID_STAT_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  GridStat

   FCST_GRID_STAT_PROB_THRESH
     Threshold values to be used for probabilistic data in grid_stat. The value can be a single item or a comma separated list of items that must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le). A corresponding variable exists for observation data called :term:`OBS_GRID_STAT_PROB_THRESH`.

     | *Used by:*  GridStat

   FCST_HR_END
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FCST_HR_INTERVAL
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FCST_HR_START
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FCST_INIT_INTERVAL
     .. warning:: **DEPRECATED:** Specify the stride for forecast initializations.

   FCST_INPUT_DIR_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`FCST_POINT_STAT_INPUT_DIR` instead.

   FCST_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use FCST_[MET-APP]_INPUT_DIR` instead, i.e. :term:`FCST_GRID_STAT_INPUT_DIR`

   FCST_INPUT_FILE_REGEX
     .. warning:: **DEPRECATED:** Regular expression to use when identifying which forecast file to use.

   FCST_INPUT_FILE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`FCST_POINT_STAT_INPUT_TEMPLATE` instead.

   FCST_IS_DAILY_FILE
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_IS_DAILY_FILE` instead.

   FCST_IS_PROB
     Specify whether the forecast data are probabilistic or not. Acceptable values: true/false

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PointStat

   FCST_PROB_IN_GRIB_PDS
     Specify whether the probabilistic forecast data is stored in the GRIB Product Definition Section or not.Acceptable values: true/false. Only used when FCST_IS_PROB is True. This does not need to be set if the FCST_<APP_NAME>_INPUT_DATATYPE is set to NetCDF.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PointStat

   FCST_LEAD
     .. warning:: **DEPRECATED:** Please use :term:`FCST_LEAD_LIST` instead.

   FCST_LEVEL
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_INPUT_ACCUMS` instead.

   FCST_MAX_FORECAST
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ_MAX` instead.

   FCST_MODE_CONV_RADIUS
     Comma separated list of convolution radius values used by mode for forecast fields. A corresponding variable exists for observation data called :term:`OBS_MODE_CONV_RADIUS`.

     | *Used by:*  MODE

   FCST_MODE_CONV_THRESH
     Comma separated list of convolution threshold values used by mode for forecast fields. A corresponding variable exists for observation data called :term:`OBS_MODE_CONV_THRESH`.

     | *Used by:*  MODE

   FCST_MODE_FILE_WINDOW_BEGIN
     See :term:`OBS_MODE_FILE_WINDOW_BEGIN`

     | *Used by:*  MODE

   FCST_MODE_FILE_WINDOW_END
     See :term:`OBS_MODE_FILE_WINDOW_END`

     | *Used by:*  MODE

   FCST_MODE_MERGE_FLAG
     Sets the merge_flag value in the mode config file for forecast fields. Valid values are NONE, THRESH, ENGINE, and BOTH. A corresponding variable exists for observation data called :term:`OBS_MODE_MERGE_FLAG`.

     | *Used by:*  MODE

   FCST_MODE_MERGE_THRESH
     Comma separated list of merge threshold values used by mode for forecast fields. A corresponding variable exists for observation data called :term:`OBS_MODE_MERGE_THRESH`.

     | *Used by:*  MODE

   FCST_MODE_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET mode tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A corresponding variable exists for observation data called :term:`OBS_MODE_INPUT_DATATYPE`.

     | *Used by:*  MODE

   FCST_MODE_INPUT_DIR
     Input directory for forecast files to use with the MET tool mode. A corresponding variable exists for observation data called :term:`OBS_MODE_INPUT_DIR`.

     | *Used by:*  MODE

   FCST_MODE_INPUT_TEMPLATE
     Template used to specify forecast input filenames for the MET tool mode. A corresponding variable exists for observation data called :term:`OBS_MODE_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  MODE

   FCST_MTD_CONV_RADIUS
     Comma separated list of convolution radius values used by mode-TD for forecast files. A corresponding variable exists for observation data called :term:`OBS_MTD_CONV_RADIUS`.

     | *Used by:*

   FCST_MTD_CONV_THRESH
     Comma separated list of convolution threshold values used by mode-TD for forecast files. A corresponding variable exists for observation data called :term:`OBS_MTD_CONV_THRESH`.

     | *Used by:*

   FCST_MTD_FILE_WINDOW_BEGIN
     See :term:`OBS_MTD_FILE_WINDOW_BEGIN`

     | *Used by:* MTD

   FCST_MTD_FILE_WINDOW_END
     See :term:`OBS_MTD_FILE_WINDOW_END`

     | *Used by:* MTD

   FCST_MTD_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET mode-TD tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A corresponding variable exists for observation data called :term:`OBS_MTD_INPUT_DATATYPE`.

     | *Used by:* MTD

   FCST_MTD_INPUT_DIR
     Input directory for forecast files to use with the MET tool mode-TD. A corresponding variable exists for observation data called :term:`OBS_MTD_INPUT_DIR`.

     | *Used by:* MTD

   FCST_MTD_INPUT_TEMPLATE
     Template used to specify forecast input filenames for the MET tool mode-TD. A corresponding variable exists for observation data called :term:`OBS_MTD_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:* MTD

   FCST_NATIVE_DATA_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_INPUT_DATATYPE` instead

   FCST_NC_TILE_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_PREFIX` instead.

   FCST_SERIES_ANALYSIS_NC_TILE_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_PREFIX` instead.

   FCST_PCP_COMBINE_<n>_FIELD_NAME
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_INPUT_NAMES` instead.

   FCST_PCP_COMBINE_DATA_INTERVAL
     Specify the accumulation interval of the forecast dataset used by the MET pcp_combine tool when processing daily input files. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_DATA_INTERVAL`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_DERIVE_LOOKBACK
     Specify how far to look back in time in hours to find files for running the MET pcp_combine tool in derive mode. If set to 0 or unset, data will be obtained by using the input template with the current runtime instead of looking backwards in time. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_DERIVE_LOOKBACK`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET pcp_combine tool. Currently valid options are NETCDF, GRIB, and GEMPAK. Required by pcp_combine if :term:`FCST_PCP_COMBINE_RUN` is True. Replaces deprecated variable :term:`FCST_NATIVE_DATA_TYPE`. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_DATATYPE`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_DIR
     Specify the input directory for forecast files used with the MET pcp_combine tool. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_DIR`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_LEVEL
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_INPUT_ACCUMS`.

   FCST_PCP_COMBINE_INPUT_TEMPLATE
     Template used to specify input filenames for forecast files used by the MET pcp_combine tool. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_IS_DAILY_FILE
     Specify whether the forecast file is a daily file or not. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_IS_DAILY_FILE`.Acceptable values: true/false

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_METHOD
     Specify the method to be used with the MET pcp_combine tool processing forecast data.Valid options are ADD, SUM, SUBTRACT, DERIVE, and USER_DEFINED. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_METHOD`.

     | *Used by:*  PCPCombine

   FCST_MIN_FORECAST
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_MIN_FORECAST`.

   OBS_MIN_FORECAST
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_MIN_FORECAST`.

   OBS_MAX_FORECAST
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_MAX_FORECAST`.

   FCST_PCP_COMBINE_MIN_FORECAST
     Specify the minimum forecast lead time to use when finding the lowest forecast lead to use in pcp_combine. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_MIN_FORECAST`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_MAX_FORECAST
     Specify the maximum forecast lead time to use when finding the lowest forecast lead to use in pcp_combine. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_MAX_FORECAST`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_OUTPUT_DIR
     Specify the output directory for forecast files generated by the MET pcp_combine tool. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_OUTPUT_DIR`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_OUTPUT_TEMPLATE
     Template used to specify output filenames for forecast files generated by the MET pcp_combine tool. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_OUTPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_RUN
     Specify whether to run the MET pcp_combine tool on forecast data or not. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_RUN`.Acceptable values: true/false

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_STAT_LIST
     List of statistics to process when using the MET pcp_combine tool on forecast data in derive mode. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_STAT_LIST`.Acceptable values: sum, min, max, range, mean, stdev, vld_count

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_TIMES_PER_FILE
     Specify the number of accumulation intervals of the forecast dataset used by the MET pcp_combine tool when processing daily input files. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_TIMES_PER_FILE`.

     | *Used by:*  PCPCombine

   FCST_POINT_STAT_FILE_WINDOW_BEGIN
     See :term:`OBS_POINT_STAT_FILE_WINDOW_BEGIN`

     | *Used by:*  PointStat

   FCST_POINT_STAT_FILE_WINDOW_END
     See :term:`OBS_POINT_STAT_FILE_WINDOW_END`

     | *Used by:*  PointStat

   FCST_POINT_STAT_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET point_stat tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A corresponding variable exists for observation data called :term:`OBS_POINT_STAT_INPUT_DATATYPE`.

     | *Used by:*  PointStat

   FCST_POINT_STAT_INPUT_DIR
     Input directory for forecast files to use with the MET tool point_stat. A corresponding variable exists for observation data called :term:`OBS_POINT_STAT_INPUT_DIR`.

     | *Used by:*  PointStat

   FCST_POINT_STAT_INPUT_TEMPLATE
     Template used to specify forecast input filenames for the MET tool point_stat. A corresponding variable exists for observation data called :term:`OBS_POINT_STAT_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  GriPointStat

   FCST_REGRID_DATA_PLANE_RUN
     If True, process forecast data with RegridDataPlane.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_RUN
     If True, process observation data with RegridDataPlane.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET regrid_data_plane tool. Currently valid options are NETCDF, GRIB, and GEMPAK. Required by pcp_combine. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_INPUT_DATATYPE`.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_INPUT_DIR
     Specify the input directory for forecast files used with the MET regrid_data_plane tool. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_INPUT_DIR`.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE
     Template used to specify input filenames for forecast data used by the MET regrid_data_plane tool. It not set, METplus will use :term:`FCST_REGRID_DATA_PLANE_TEMPLATE`. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE
     Template used to specify output filenames for forecast data used by the MET regrid_data_plane tool. It not set, METplus will use :term:`FCST_REGRID_DATA_PLANE_TEMPLATE`. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_TEMPLATE
     Template used to specify filenames for forecast data used by the MET regrid_data_plane tool. To specify different templates for input and output files , use :term:`FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE` and :term:`FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_TEMPLATE`.

     | *Used by:*  RegridDataPlane

   FCST_REGRID_DATA_PLANE_OUTPUT_DIR
     Specify the output directory for forecast files used with the MET regrid_data_plane tool. A corresponding variable exists for observation data called :term:`OBS_REGRID_DATA_PLANE_OUTPUT_DIR`.

     | *Used by:*  RegridDataPlane

   FCST_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`FCST_THRESH_LIST` instead.

   FCST_THRESH_LIST
     Specify the values of the FCST_THRESH column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   OBS_THRESH_LIST
     Specify the values of the OBS_THRESH column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   FCST_TILE_PREFIX
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_PREFIX` instead.

   FCST_TILE_REGEX
     .. warning:: **DEPRECATED:** No longer used. Regular expression for forecast input files that are in GRIB2.

   FCST_EXTRACT_TILES_PREFIX
     Prefix for forecast tile files. Used to create filename of intermediate files that are created while performing a series analysis.

     | *Used by:*  ExtractTiles

   FCST_VAR
     .. warning:: **DEPRECATED:** No longer used.

   FCST_VAR_LEVEL
     .. warning:: **DEPRECATED:** Please use :term:`FCST_LEVEL_LIST` instead.

   FCST_LEVEL_LIST
     Specify the values of the FCST_LEV column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   FCST_VAR_NAME
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VAR_LIST` instead.

   FCST_VAR_LIST
     Specify the values of the FCST_VAR column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   FCST_UNITS_LIST
     Specify the values of the FCST_UNITS column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   FCST_VAR<n>_LEVELS
     Define the levels for the <n>th forecast variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items. You can define NetCDF levels, such as (0,*,*), but you will need to surround these values with quotation marks so that the commas in the item are not interpreted as an item delimeter. Some examples:

     | FCST_VAR1_LEVELS = A06, P500
     | FCST_VAR2_LEVELS ="(0,*,*),(1,*,*)"

     There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | FCST_VAR1_LEVELS
     | FCST_VAR2_LEVELS
     | ...
     | FCST_VAR<n>_LEVELS

     If FCST_VAR<n>_LEVELS is set, then :term:`OBS_VAR<n>_LEVELS` must be set as well. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_LEVELS`.

     See :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   FCST_VAR<n>_NAME
     Define the name for the <n>th forecast variable to be used in the analysis where <n> is an integer >= 1. If :term:`FCST_VAR<n>_NAME` is set, then :term:`OBS_VAR<n>_NAME` must be set. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_NAME`. There can be s<n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | FCST_VAR1_NAME
     | FCST_VAR2_NAME
     | ...
     | FCST_VAR<n>_NAME

     See :ref:`Field_Info` for more information.

     This value can be set to a call to a python script with arguments to supply data to the MET tools via Python Embedding. Filename template syntax can be used here to specify time information of an input file, i.e. {valid?fmt=%Y%m%d%H}. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information about Python Embedding in the MET tools.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   FCST_VAR<n>_OPTIONS
     Define the options for the <n>th forecast variable to be used in the analysis where <n> is an integer >= 1. These addition options will be applied to every name/level/threshold combination for VAR<n>. There can be <n> number of these variables defined in configuration files, simply increment the VAR1  string to match the total number of variables being used, e.g.:

     | FCST_VAR1_OPTIONS
     | FCST_VAR2_OPTIONS
     | ...
     | FCST_VAR<n>_OPTIONS

     See :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   FCST_VAR<n>_THRESH
     Define the threshold(s) for the <n>th forecast variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items that must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le). If :term:`FCST_VAR<n>_THRESH` is not set but :term:`OBS_VAR<n>_THRESH` is, the same information will be used for both variables. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:
     | FCST_VAR1_THRESH
     | FCST_VAR2_THRESH
     | ...
     | FCST_VAR<n>_THRESH

     If :term:`FCST_VAR<n>_THRESH` is set, then :term:`OBS_VAR<n>_THRESH` must be set as well. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_THRESH`.

     See :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   BOTH_VAR<n>_LEVELS
     Define the levels for the <n>th forecast and observation variables to be used in the analysis where <n> is an integer >= 1. See :term:`FCST_VAR<n>_LEVELS`, :term:`OBS_VAR<n>_LEVELS`, or :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   BOTH_VAR<n>_NAME
     Define the name for the <n>th forecast and observation variables to be used in the analysis where <n> is an integer >= 1. See :term:`FCST_VAR<n>_NAME`, :term:`OBS_VAR<n>_NAME`, or :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   BOTH_VAR<n>_OPTIONS
     Define the extra options for the <n>th forecast and observation variables to be used in the analysis where <n> is an integer >= 1. See :term:`FCST_VAR<n>_OPTIONS`, :term:`OBS_VAR<n>_OPTIONS`, or :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   BOTH_VAR<n>_THRESH
     Define the threshold list for the <n>th forecast and observation variables to be used in the analysis where <n> is an integer >= 1. See :term:`FCST_VAR<n>_THRESH`, :term:`OBS_VAR<n>_THRESH`, or :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   FCST_MODE_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_NAME`.

     | *Used by:*  MODE

   FCST_MTD_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_NAME`.

     | *Used by:*  MTD

   FCST_GRID_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_NAME`.

     | *Used by:*  GridStat

   FCST_ENSEMBLE_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_NAME`.

     | *Used by:*  EnsembleStat

   FCST_POINT_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_NAME`.

     | *Used by:*  PointStat

   FCST_MODE_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_LEVELS`.

     | *Used by:*  MODE

   FCST_MTD_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_LEVELS`.

     | *Used by:*  MTD

   FCST_GRID_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_LEVELS`.

     | *Used by:*  GridStat

   FCST_ENSEMBLE_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_LEVELS`.

     | *Used by:*  EnsembleStat

   FCST_POINT_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_LEVELS`.

     | *Used by:*  PointStat

   FCST_MODE_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_OPTIONS`.

     | *Used by:*  MODE

   FCST_MTD_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_OPTIONS`.

     | *Used by:*  MTD

   FCST_GRID_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_OPTIONS`.

     | *Used by:*  GridStat

   FCST_ENSEMBLE_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_OPTIONS`.

     | *Used by:*  EnsembleStat

   FCST_POINT_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_OPTIONS`.

     | *Used by:*  PointStat

   FCST_MODE_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_THRESH`.

     | *Used by:*  MODE

   FCST_MTD_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_THRESH`.

     | *Used by:*  MTD

   FCST_GRID_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_THRESH`.

     | *Used by:*  GridStat

   FCST_ENSEMBLE_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_THRESH`.

     | *Used by:*  EnsembleStat

   FCST_POINT_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`FCST_VAR<n>_THRESH`.

     | *Used by:*  PointStat

   OBS_MODE_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_NAME`.

     | *Used by:*  MODE

   OBS_MTD_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_NAME`.

     | *Used by:*  MTD

   OBS_GRID_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_NAME`.

     | *Used by:*  GridStat

   OBS_ENSEMBLE_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_NAME`.

     | *Used by:*  EnsembleStat

   OBS_POINT_STAT_VAR<n>_NAME
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_NAME`.

     | *Used by:*  PointStat

   OBS_MODE_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_LEVELS`.

     | *Used by:*  MODE

   OBS_MTD_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_LEVELS`.

     | *Used by:*  MTD

   OBS_GRID_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_LEVELS`.

     | *Used by:*  GridStat

   OBS_ENSEMBLE_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_LEVELS`.

     | *Used by:*  EnsembleStat

   OBS_POINT_STAT_VAR<n>_LEVELS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_LEVELS`.

     | *Used by:*  PointStat

   OBS_MODE_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_OPTIONS`.

     | *Used by:*  MODE

   OBS_MTD_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_OPTIONS`.

     | *Used by:*  MTD

   OBS_GRID_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_OPTIONS`.

     | *Used by:*  GridStat

   OBS_ENSEMBLE_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_OPTIONS`.

     | *Used by:*  EnsembleStat

   OBS_POINT_STAT_VAR<n>_OPTIONS
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_OPTIONS`.

     | *Used by:*  PointStat

   OBS_MODE_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_THRESH`.

     | *Used by:*  MODE

   OBS_MTD_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_THRESH`.

     | *Used by:*  MTD

   OBS_GRID_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_THRESH`.

     | *Used by:*  GridStat

   OBS_ENSEMBLE_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_THRESH`.

     | *Used by:*  EnsembleStat

   OBS_POINT_STAT_VAR<n>_THRESH
     Wrapper specific field info variable. See :term:`OBS_VAR<n>_THRESH`.

     | *Used by:*  PointStat

   FCST_WINDOW_BEGIN
     See :term:`OBS_WINDOW_BEGIN`

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   FCST_WINDOW_END
     See :term:`OBS_WINDOW_END`

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   FHR_BEG
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FHR_END
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FHR_GROUP_BEG
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ_\<n>` instead.

   FHR_GROUP_END
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ_\<n>` instead.

   FHR_GROUP_LABELS
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ_\<n>_LABEL` instead.

   FHR_INC
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ` instead.

   FILTER
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_FILTER` instead.

   TCMPR_PLOTTER_FILTER
     Corresponds to the optional -filter argument to the plot_TCMPR.R script which is wrapped by TCMPRPlotter. This is a list of filtering options for the tc_stat tool.

     | *Used by:*  TCMPRPlotter

   FILTERED_TCST_DATA_FILE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE` instead.

   TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE
     Corresponds to the optional -tcst argument to the plot_TCMPR.R script which is wrapped by TCMPRPlotter. This is a tcst data file to be used instead of running the tc_stat tool. Indicate a full path to the data file.

     | *Used by:*  TCMPRPlotter

   FOOTNOTE_FLAG
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_FOOTNOTE_FLAG` instead.

   TCMPR_PLOTTER_FOOTNOTE_FLAG
     This corresponds to the optional -footnote flag in the plot_TCMPR.R script which is wrapped by TCMPRPlotter. According to the plot_TCMPR.R usage, this flag is used to disable footnote (date).

     | *Used by:*  TCMPRPlotter

   FORECAST_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_ADECK_TEMPLATE`.

   GEMPAKTOCF_CLASSPATH
     .. warning:: **DEPRECATED:** Please use :term:`GEMPAKTOCF_JAR` instead. Path to the GempakToCF binary file and the NetCDF jar file required to run GempakToCF.

   GEMPAKTOCF_JAR
     Path to the GempakToCF.jar file to run GempakToCF.
     The tool is available on the MET webpage here:
     https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar.
     Must be set if running GempakToCF wrapper, if using a filename template
     that ends with .grd, or if specifying an \*_INPUT_DATATYPE item as GEMPAK.

     | *Used by:*  GempakToCF, other wrappers that will read Gempak data

   GEMPAKTOCF_INPUT_DIR
     Specify the input directory for the tool used to convert GEMPAK files to netCDF.

     | *Used by:*  GempakToCF

   GEMPAKTOCF_INPUT_TEMPLATE
     Filename template used for input files to the tool used to convert GEMPAK files to netCDF.

     | *Used by:*  GempakToCF

   GEMPAKTOCF_OUTPUT_DIR
     Specify the output directory for files generated by the tool used to convert GEMPAK files to netCDF.

     | *Used by:*  GempakToCF

   GEMPAKTOCF_OUTPUT_TEMPLATE
     Filename template used for output files from the tool used to convert GEMPAK files to netCDF.

     | *Used by:*  GempakToCF

   GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS
     If True, do not run GempakToCF if output file already exists. Set to False to overwrite files.

     | *Used by:*  GempakToCF

   CYCLONE_GENERATE_TRACK_ASCII
     .. warning:: **DEPRECATED:** Please use :term:`CYCLONE_PLOTTER_GENERATE_TRACK_ASCII` instead.

   CYCLONE_PLOTTER_GENERATE_TRACK_ASCII
     Specify whether or not to produce an ASCII file containing all of the tracks in the plot. Acceptable values: true/false

     | *Used by:*  CyclonePlotter

   GEN_SEQ
     .. warning:: **DEPRECATED:**

   FCST_EXTRACT_TILES_INPUT_TEMPLATE
     Filename template used to identify forecast input file to ExtractTiles.

     | *Used by:*  ExtractTiles

   OBS_EXTRACT_TILES_INPUT_TEMPLATE
     Filename template used to identify observation input file to ExtractTiles.

     | *Used by:*  ExtractTiles

   FCST_EXTRACT_TILES_OUTPUT_TEMPLATE
     Filename template used to identify the forecast output file generated by ExtractTiles.

     | *Used by:* ExtractTiles

   OBS_EXTRACT_TILES_OUTPUT_TEMPLATE
     Filename template used to identify the observation output file generated by ExtractTiles.

     | *Used by:* ExtractTiles

   GFS_ANLY_FILE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`OBS_EXTRACT_TILES_INPUT_TEMPLATE` instead.

   GFS_FCST_FILE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_INPUT_TEMPLATE` instead.


   GRID_STAT_CONFIG
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_CONFIG_FILE` instead.

   GRID_STAT_CONFIG_FILE
     Specify the absolute path to the configuration file used by the MET grid_stat tool.

     | *Used by:*  GridStat

   GRID_STAT_ONCE_PER_FIELD
     True/False. If True, grid_stat will run once to process all name/level/threshold combinations specified. If False, it will run once for each name/level. Some cases require this to be set to False, for example processing probablistic forecasts or precipitation accumulations.

     | *Used by:*  GridStat

   GRID_STAT_NEIGHBORHOOD_WIDTH
     Sets the neighborhood width used by GridStat. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  GridStat

   GRID_STAT_NEIGHBORHOOD_SHAPE
     Sets the neighborhood shape used by GridStat. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  GridStat

   GRID_STAT_NEIGHBORHOOD_COV_THRESH
     Sets the neighborhood cov_thresh list used by GridStat. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  GridStat

   POINT_STAT_NEIGHBORHOOD_WIDTH
     Sets the neighborhood width used by PointStat. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PointStat

   POINT_STAT_NEIGHBORHOOD_SHAPE
     Sets the neighborhood shape used by PointStat. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PointStat

   POINT_STAT_OBS_VALID_BEG
     Optional variable that sets the -obs_valid_beg command line argument for PointStat if set to something other than an empty string. Accepts filename template syntax, i.e. {valid?fmt=%Y%m%d_%H}

     | *Used by:* PointStat

   POINT_STAT_OBS_VALID_END
     Optional variable that sets the -obs_valid_end command line argument for PointStat if set to something other than an empty string. Accepts filename template syntax, i.e. {valid?fmt=%Y%m%d_%H}

     | *Used by:* PointStat

   GRID_STAT_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GRID_STAT_OUTPUT_DIR` instead.

   GRID_STAT_OUTPUT_DIR
     Specify the output directory where files from the MET grid_stat tool are written.

     | *Used by:*  GridStat

   GRID_STAT_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`GRID_STAT_OUTPUT_DIR` using a template to allow run time information. If LOOP_BY = VALID, default value is valid time YYYYMMDDHHMM/grid_stat. If LOOP_BY = INIT, default value is init time YYYYMMDDHHMM/grid_stat.

     | *Used by:*  GridStat

   GRID_STAT_VERIFICATION_MASK_TEMPLATE
     Template used to specify the verification mask filename for the MET tool grid_stat. Now supports a list of filenames.

     | *Used by:*  GridStat

   ENSEMBLE_STAT_VERIFICATION_MASK_TEMPLATE
     Template used to specify the verification mask filename for the MET tool ensemble_stat. Now supports a list of filenames.

     | *Used by:*  EnsembleStat

   HFIP_BASELINE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_HFIP_BASELINE` instead.

   TCMPR_PLOTTER_HFIP_BASELINE
     Corresponds to the optional -hfip_bsln flag in the plot_TCMPR.R script which is wrapped by TCMPRPlotter. This is a string that indicates whether to add the HFIP baseline, and indicates the version (no, 0, 5, 10 year goal).

     | *Used by:*  TCMPRPlotter

   INIT_BEG
     Specify the beginning initialization time to be used in the analysis. Format can be controlled by :term:`INIT_TIME_FMT`. See :ref:`Looping_by_Initialization_Time` for more information.

     | *Used by:*  All

   INIT_END
     Specify the ending initialization time to be used in the analysis. Format can be controlled by :term:`INIT_TIME_FMT`. See :ref:`Looping_by_Initialization_Time` for more information.

     | *Used by:*  All

   INIT_EXCLUDE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_INIT_EXCLUDE`  instead.

   TC_PAIRS_INIT_EXCLUDE
     Specify which, if any, forecast initializations to exclude from the analysis.

     | *Used by:*  TCPairs

   FCST_INIT_HOUR_LIST
     Specify a list of hours for initialization times of forecast files for use in the analysis.

     | *Used by:*  MakePlots, StatAnalysis

   OBS_INIT_HOUR_LIST
     Specify a list of hours for initialization times of observation files for use in the analysis.

     | *Used by:*  MakePlots, StatAnalysis

   INIT_HOUR_BEG
     .. warning:: **DEPRECATED:** Please use :term:`FCST_INIT_HOUR_LIST` or :term:`OBS_INIT_HOUR_LIST` instead.

   INIT_HOUR_END
     .. warning:: **DEPRECATED:** Please use :term:`FCST_INIT_HOUR_LIST` or :term:`OBS_INIT_HOUR_LIST` instead.

   INIT_HOUR_INCREMENT
     .. warning:: **DEPRECATED:** Please use :term:`FCST_INIT_HOUR_LIST` or :term:`OBS_INIT_HOUR_LIST` instead.

   INIT_HOUR_METHOD
     .. warning:: **DEPRECATED:** No longer used.

   INIT_INCLUDE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_INIT_INCLUDE`  instead.

   TC_PAIRS_INIT_INCLUDE
     Specify which forecast initializations to include in the analysis.

     | *Used by:*  TCPairs

   INIT_INCREMENT
     Control the increment or stride to use when stepping between forecast initializations. Units are seconds. See :ref:`Looping_by_Initialization_Time` for more information. Units are assumed to be seconds unless specified with Y, m, d, H, M, or S.

     | *Used by:*  All

   INIT_SEQ
     Specify a list of initialization hours that are used to build a sequence of forecast lead times to include in the analysis. Used only when looping by valid time (LOOP_BY = VALID). Comma separated list format, e.g.:0, 6, 12 See :ref:`looping_over_forecast_leads` for more information.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PCPCombine, PointStat, RegridDataPlane, SeriesAnalysis

   INIT_TIME_FMT
     Specify a formatting string to use for :term:`INIT_BEG` and :term:`INIT_END`. See :ref:`Looping_by_Initialization_Time` for more information.

     | *Used by:*  All

   INTERP
     .. warning:: **DEPRECATED:** Please use :term:`INTERP_MTHD_LIST` instead.

   INTERP_MTHD_LIST
     Specify the values of the INTERP_MTHD column in the MET .stat file to use; specify the interpolation used to create the MET .stat files.

     | *Used by:*  MakePlots, StatAnalysis

   INTERP_PTS
     .. warning:: **DEPRECATED:** Please use :term:`INTERP_PNTS_LIST` instead.

   INTERP_PNTS_LIST
     Specify the values of the INTERP_PNTS column in the MET .stat file to use; corresponds to the interpolation in the MET .stat files.

     | *Used by:*  MakePlots, StatAnalysis

   INTERVAL_TIME
     Define the interval time in hours (HH) to be used by the MET pb2nc tool.

     | *Used by:*  PB2NC

   JOB_ARGS
     .. warning:: **DEPRECATED:** Please use :term:`STAT_ANALYSIS_JOB_ARGS` instead.

   STAT_ANALYSIS_JOB_ARGS
     Specify stat_analysis job arguments to run. The job arguments that are to be run with the corresponding :term:`STAT_ANALYSIS_JOB_NAME`. If using -dump_row, use -dump_row [dump_row_filename]. If using -out_stat, -out_stat [out_stat_filename]. For more information on these job arguments, please see the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_.

     | *Used by:*  StatAnalysis

   JOB_NAME
     .. warning:: **DEPRECATED:** Please use :term:`STAT_ANALYSIS_JOB_NAME` instead.

   STAT_ANALYSIS_JOB_NAME
     Specify stat_analysis job name to run. Valid options are filter, summary, aggregate, aggregate_stat, go_index, and ramp. For more information on these job names and what they do, please see the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_.

     | *Used by:*  StatAnalysis

   EXTRACT_TILES_LAT_ADJ
     Specify a latitude adjustment, in degrees to be used in the analysis. In the ExtractTiles wrapper, this corresponds to the 2m portion of the 2n x 2m subregion tile.

     | *Used by:*  ExtractTiles

   LAT_ADJ
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_LAT_ADJ` instead.

   LEAD
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_LEAD` instead.

   TCMPR_PLOTTER_LEAD
     For CyclonePlotter, this refers to the column of interest in the input ASCII cyclone file.In the TCMPRPlotter, this corresponds to the optional -lead argument in the plot_TCMPR.R script (which is wrapped by TCMPRPlotter). This argument is set to a comma-separted list of lead times (h) to be plotted.In TCStat, this corresponds to the name of the column of interest in the input ASCII data file.

     | *Used by:*  TCMPRPlotter

   LEAD_LIST
     .. warning:: **DEPRECATED:** Please use :term:`FCST_LEAD_LIST` instead.

   FCST_LEAD_LIST
     Specify the values of the FSCT_LEAD column in the MET .stat file to use. Comma separated list format, e.g.: 00, 24, 48, 72, 96, 120

     | *Used by:*  MakePlots, StatAnalysis

   OBS_LEAD_LIST
     Specify the values of the OBS_LEAD column in the MET .stat file to use. Comma separated list format, e.g.: 00, 24, 48, 72, 96, 120

     | *Used by:*  MakePlots, StatAnalysis

   LEAD_SEQ
     Specify the sequence of forecast lead times to include in the analysis. Comma separated list format, e.g.:0, 6, 12. See :ref:`looping_over_forecast_leads` for more information. Units are assumed to be hours unless specified with Y, m, d, H, M, or S.

     | *Used by:*  All

   LEAD_SEQ_MIN
     Minimum forecast lead to be processed. Used primarily with INIT_SEQ but also affects LEAD_SEQ. See :ref:`looping_over_forecast_leads` for more information. Units are assumed to be hours unless specified with Y, m, d, H, M, or S.

     | *Used by:*  All

   LEAD_SEQ_MAX
     Maximum forecast lead to be processed. Used primarily with :term:`INIT_SEQ` but also affects :term:`LEAD_SEQ`. See :ref:`looping_over_forecast_leads` for more information. Units are assumed to be hours unless specified with Y, m, d, H, M, or S.

     | *Used by:*  All

   LEAD_SEQ_<n>
     Specify the sequence of forecast lead times to include in the analysis. Comma separated list format, e.g.:0, 6, 12. <n> corresponds to the bin in which the user wishes to aggregate series by lead results.

     | *Used by:*  SeriesAnalysis

   LEAD_SEQ_<n>_LABEL
     Required when SERIES_BY_LEAD_GROUP_FCSTS=True. Specify the label of the corresponding bin of series by lead results.

     | *Used by:*  SeriesAnalysis

   LEGEND
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_LEGEND` instead.

   TCMPR_PLOTTER_LEGEND
     The text to be included in the legend of your plot.

     | *Used by:*  TCMPRPlotter

   LINE_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`LINE_TYPE_LIST` instead.


   LINE_TYPE_LIST
     Specify the MET STAT line types to be considered. For TCMPRPlotter, this is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  MakePlots, StatAnalysis, TCMPRPlotter

   LOG_DIR
     Specify the directory where log files from MET and METplus should be written.

     | *Used by:*  All

   LOG_LEVEL
     Specify the level of logging. Everything above this level is sent to standard output. To quiet the output to a comfortable level, set this to "ERROR"

     Options (ordered MOST verbose to LEAST verbose):
     | NOTSET
     | DEBUG
     | INFO
     | WARNING
     | ERROR
     | CRITICAL

     | *Used by:*  All

   LOG_METPLUS
     Control the filename of the METplus log file. Control the timestamp appended to the filename with LOG_TIMESTAMP_TEMPLATE. To turn OFF all logging, do not set this option.

     | *Used by:*  All

   LOG_MET_OUTPUT_TO_METPLUS
     Control whether logging output from the MET tools is sent to the METplus log file, or individual log files for each MET tool.

     | *Used by:*  All

   LOG_MET_VERBOSITY
     Control the verbosity of the logging from the MET tools.0 = Least amount of logging (lowest verbosity)5 = Most amount of logging (highest verbosity)

     | *Used by:*  All

   LOG_TIMESTAMP_TEMPLATE
     Set the timestamp template for the METplus log file. Use Python strftime directives, e.g.%Y%m%d for YYYYMMDD.

     | *Used by:*  All

   LOG_TIMESTAMP_USE_DATATIME
     True/False. Determines which time to use for the log filenames. If True, use :term:`INIT_BEG` if LOOP_BY is INIT or :term:`VALID_BEG` if LOOP_BY is VALID. If False, use current time.

     | *Used by:*  All

   EXTRACT_TILES_LON_ADJ
     Specify a longitude adjustment, in degrees to be used in the analysis. In the ExtractTiles wrapper, this corresponds to the 2n portion of the 2n x 2m subregion tile.

     | *Used by:*  ExtractTiles

   LON_ADJ
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_LON_ADJ` instead.

   LOOP_BY
     Control whether the analysis is processed across valid or initialization times. See section :ref:`LOOP_BY_ref` for more information.

     | *Used by:*  All

   LOOP_BY_INIT
     .. warning:: **DEPRECATED:** Please use :term:`LOOP_BY` instead.

   LOOP_ORDER
     Control the looping order for METplus. Valid options are "times" or "processes". "times" runs all items in the :term:`PROCESS_LIST` for a single run time, then repeat until all times have been evaluated. "processes" runs each item in the :term:`PROCESS_LIST` for all times specified, then repeat for the next item in the :term:`PROCESS_LIST`.

     | *Used by:*  All

   METPLUS_BASE
     This variable will automatically be set by METplus when it is started. It will be set to the location of METplus that is currently being run. Setting this variable in a config file will have no effect and will report a warning that it is being overridden.

     | *Used by:*  All

   METPLUS_CONF
     Provide the absolute path to the METplus final configuration file. This file will contain every configuration option and value used when METplus was run.

     | *Used by:*  All

   MET_BASE
     .. warning:: **DEPRECATED:** Do not set.

   MET_BIN
     .. warning:: **DEPRECATED:** Please use :term:`MET_INSTALL_DIR` instead.

   MET_BUILD_BASE
     The base directory of the MET install. Only needed if using MET version 6.0

     | *Used by:*  TCMPRPlotter

   MET_INSTALL_DIR
     The base directory of the MET install. To be defined when using MET version 6.1 and beyond. Used to get the full path of the MET executable and the share directory when calling from METplus Wrappers.

     | *Used by:*  All

   MET_BIN_DIR
     The directory of the MET executables. Used to get the full path of the MET executable when calling from METplus Wrappers. When using the --bindir option in configuring MET, set MET_BIN_DIR to the same location.  MET_BIN_DIR will be set to {MET_INSTALL_DIR}/bin. Users can unset MET_BIN_DIR or set it to an empty string if the MET tools are found in the user's path, e.g. when using module loads.
     | *Used by:*  All

   MISSING_VAL
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_MISSING_VAL`.

   MISSING_VAL_TO_REPLACE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_MISSING_VAL_TO_REPLACE`.

   MODEL
     Specify the model name. This is the model name listed in the MET .stat files.

     | *Used by:*  EnsembleStat, GridStat, PointStat, PCPCombine, TCPairs, GridDiag, TCRMW

   MODEL_LIST
     List of the specified the model names.

     | *Used by:*  MakePlots, StatAnalysis

   MODEL<n>_NAME
        .. warning:: **DEPRECATED:** Please use :term:`MODEL\<n\>`.

   MODEL<n>
     Define the model name for the first model to be used in the analysis. This is the model name listed in the MET .stat files.There can be <n> number of models defined in configuration files, simply increment the "MODEL1" string to match the total number of models being used, e.g.:

     | MODEL1
     | MODEL2
     | ...
     | MODEL<n>

     | *Used by:*  MakePlots, StatAnalysis

   MODEL<n>_NAME_ON_PLOT
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_REFERENCE_NAME` instead.

   MODEL<n>_REFERENCE_NAME
     Define the name the first model will be listed as on the plots. There can be <n> number of models defined in configuration files, simply increment the "MODEL1" string to match the total number of models being used, e.g.:

     | MODEL1_REFERENCE_NAME
     | MODEL2_REFERENCE_NAME
     | ...
     | MODELN_REFERENCE_NAME

     | *Used by:*  MakePlots, StatAnalysis

   MODEL<n>_OBS_NAME
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_OBTYPE` instead.

   MODEL<n>_OBTYPE
     Define the observation name that was used to compare the first model to be. This is the observation name listed in the MET .stat files. There can be <n> number of observation names defined in configuration files, simply increment the "MODEL1" string to match the total number of models being used, e.g.:

     | MODEL1_OBTYPE
     | MODEL2_OBTYPE
     | ...
     | MODEL<n>_OBTYPE

     | *Used by:*  MakePlots, StatAnalysis

   MODEL<n>_STAT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR` instead.

   EXTRACT_TILES_GRID_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`FCST_EXTRACT_TILES_INPUT_DIR` and :term:`OBS_EXTRACT_TILES_INPUT_DIR` instead.

   FCST_EXTRACT_TILES_INPUT_DIR
     Directory containing gridded forecast data to be used in ExtractTiles

     | *Used by:*  ExtractTiles

   OBS_EXTRACT_TILES_INPUT_DIR
     Directory containing gridded observation data to be used in ExtractTiles

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_FILTERED_OUTPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE` instead.

   EXTRACT_TILES_STAT_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE` instead.

   EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE
     Template used to specify the dump row output tcst file generated by TCStat
     to filter input data to be used in ExtractTiles.
     Example: {init?fmt=%Y%m%d_%H}/filter_{init?fmt=%Y%m%d_%H}.tcst

     | *Used by:*  ExtractTiles

   SERIES_ANALYSIS_STAT_INPUT_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE` instead.

   SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE
     Template used to specify the dump row output tcst file generated by TCStat
     to filter input data to be used in SeriesAnalysis.
     Example: {init?fmt=%Y%m%d_%H}/filter_{init?fmt=%Y%m%d_%H}.tcst

     | *Used by:*  SeriesAnalysis

   MODEL_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_GRID_INPUT_DIR` instead.

   MODEL_NAME
     .. warning:: **DEPRECATED:** Please use :term:`MODEL` instead.

   MODE_CONFIG
     .. warning:: **DEPRECATED:** Please use :term:`MODE_CONFIG_FILE` instead. Path to mode configuration file.

   MODE_CONFIG_FILE
     Path to mode configuration file.

     | *Used by:*  MODE

   MODE_CONV_RADIUS
     Comma separated list of convolution radius values used by mode for both forecast and observation fields. Has the same behavior as setting :term:`FCST_MODE_CONV_RADIUS` and :term:`OBS_MODE_CONV_RADIUS` to the same value.

     | *Used by:*  MODE

   MODE_CONV_THRESH
     Comma separated list of convolution threshold values used by mode for both forecast and observation fields. Has the same behavior as setting :term:`FCST_MODE_CONV_THRESH` and :term:`OBS_MODE_CONV_THRESH` to the same value.

     | *Used by:*  MODE

   MODE_FCST_CONV_RADIUS
     Comma separated list of convolution radius values used by mode for forecast fields.

     | *Used by:*  MODE

   MODE_FCST_CONV_THRESH
     Comma separated list of convolution threshold values used by mode for forecast fields.

     | *Used by:*  MODE

   MODE_FCST_MERGE_FLAG
     Sets the merge_flag value in the mode config file for forecast fields. Valid values are NONE, THRESH, ENGINE, and BOTH.

     | *Used by:*  MODE

   MODE_FCST_MERGE_THRESH
     Comma separated list of merge threshold values used by mode for forecast fields.

     | *Used by:*  MODE

   MODE_MERGE_CONFIG_FILE
     Path to mode merge config file.

     | *Used by:*  MODE

   MODE_MERGE_FLAG
     Sets the merge_flag value in the mode config file for both forecast and observation fields. Has the same behavior as setting :term:`MODE_FCST_MERGE_FLAG` and :term:`MODE_OBS_MERGE_FLAG` to the same value. Valid values are NONE, THRESH, ENGINE, and BOTH.

     | *Used by:*  MODE

   MODE_MERGE_THRESH
     Comma separated list of merge threshold values used by mode for forecast and observation fields. Has the same behavior as setting :term:`MODE_FCST_MERGE_THRESH` and :term:`MODE_OBS_MERGE_THRESH` to the same value.

     | *Used by:*  MODE

   MODE_OBS_CONV_RADIUS
     .. warning:: **DEPRECATED:** Please see `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ instead.

   MODE_OBS_CONV_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`OBS_MODE_CONV_THRESH` instead.

   MODE_OBS_MERGE_FLAG
     .. warning:: **DEPRECATED:** Please use :term:`OBS_MODE_MERGE_FLAG` instead.

   MODE_OBS_MERGE_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`OBS_MODE_MERGE_THRESH` instead.

   MODE_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`MODE_OUTPUT_DIR` instead.

   MODE_OUTPUT_DIR
     Output directory to write mode files.

     | *Used by:*  MODE

   MODE_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`MODE_OUTPUT_DIR` using a template to allow run time information. If LOOP_BY = VALID, default value is valid time YYYYMMDDHHMM/mode. If LOOP_BY = INIT, default value is init time YYYYMMDDHHMM/mode.

     | *Used by:*  MODE

   MODE_VERIFICATION_MASK_TEMPLATE
     Template used to specify the verification mask filename for the MET tool mode. Now supports a list of filenames.

     | *Used by:*  MODE

   MODE_QUILT
     True/False. If True, run all permutations of radius and threshold.

     | *Used by:*  MODE

   MTD_CONFIG
     .. warning:: **DEPRECATED:** Please use :term:`MTD_CONFIG_FILE` instead.

   MTD_CONFIG_FILE
     Path to mode-TD configuration file.

     | *Used by:* MTD

   MTD_CONV_RADIUS
     Comma separated list of convolution radius values used by mode-TD for both forecast and observation files. Has the same behavior as setting :term:`FCST_MTD_CONV_RADIUS` and :term:`OBS_MTD_CONV_RADIUS` to the same value.

     | *Used by:* MTD

   MTD_CONV_THRESH
     Comma separated list of convolution threshold values used by mode-TD for both forecast and observation files. Has the same behavior as setting :term:`FCST_MTD_CONV_THRESH` and :term:`OBS_MTD_CONV_THRESH` to the same value.

     | *Used by:* MTD

   MTD_FCST_CONV_RADIUS
     Comma separated list of convolution radius values used by mode-TD for forecast files.

     | *Used by:* MTD

   MTD_MIN_VOLUME
     Sets min_volume in the MET MODE-TD config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:* MTD

   MTD_SINGLE_RUN
     Set to True to only process one data set (forecast or observation) in MODE-TD. If True, must set :term:`MTD_SINGLE_RUN_SRC` to either 'FCST' or 'OBS'.

     | *Used by:* MTD

   MTD_SINGLE_RUN_SRC
     .. warning:: **DEPRECATED:** Please use :term:`MTD_SINGLE_DATA_SRC` instead.

   MTD_SINGLE_DATA_SRC
     Used only if MTD_SINGLE_RUN is set to True. Valid options are 'FCST' or 'OBS'.

     | *Used by:* MTD

   MTD_FCST_CONV_THRESH
     Comma separated list of convolution threshold values used by mode-TD for forecast files.

     | *Used by:* MTD

   MTD_OBS_CONV_RADIUS
     Comma separated list of convolution radius values used by mode-TD for observation files.

     | *Used by:* MTD

   MTD_OBS_CONV_THRESH
     Comma separated list of convolution threshold values used by mode-TD for observation files.

     | *Used by:* MTD

   MTD_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`MTD_OUTPUT_DIR`.

   MTD_OUTPUT_DIR
     Output directory to write mode-TD files.

     | *Used by:* MTD

   MTD_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`MTD_OUTPUT_DIR` using a template to allow run time information. If LOOP_BY = VALID, default value is valid time YYYYMMDDHHMM/mtd. If LOOP_BY = INIT, default value is init time YYYYMMDDHHMM/mtd.

     | *Used by:* MTD

   NCDUMP
     Path to thencdump executable.

     | *Used by:*  PB2NC, PointStat

   NCDUMP_EXE
     .. warning:: **DEPRECATED:** Please use :term:`NCDUMP`.

   NC_FILE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_OUTPUT_TEMPLATE` instead.

   PB2NC_OUTPUT_TEMPLATE
     File template used to create netCDF files generated by PB2NC.

     | *Used by:*  PB2NC

   EXTRACT_TILES_NLAT
     The number of latitude points, set to a whole number. This defines the number of latitude points to incorporate into the subregion (density).

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_NLON
     The number of longitude points, set to a whole number. This defines the number of longitude points to incorporate into the subregion (density).

     | *Used by:*  ExtractTiles

   NLAT
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_NLAT` instead.

   NLON
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_NLON` instead.

   NO_EE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_NO_EE` instead.

   TCMPR_PLOTTER_NO_EE
     Set the :term:`NO_EE` flag for the TC Matched Pairs plotting utility.Acceptable values: yes/no

     | *Used by:*  TCMPRPlotter

   NO_LOG
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_NO_LOG` instead.

   TCMPR_PLOTTER_NO_LOG
     Set the NO_LOG flag for the TC Matched Pairs plotting utility.Acceptable values: yes/no

     | *Used by:*  TCMPRPlotter

   OBS_<n>_FIELD_NAME
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_<n>_FIELD_NAME` instead.

   OBS_BUFR_VAR_LIST
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_OBS_BUFR_VAR_LIST` instead.

   OBS_DATA_INTERVAL
     .. warning:: **DEPRECATED:** Use :term:`OBS_PCP_COMBINE_DATA_INTERVAL` instead.

   FCST_DATA_INTERVAL
     .. warning:: **DEPRECATED:** Use :term:`FCST_PCP_COMBINE_DATA_INTERVAL` instead.

   FCST_ENSEMBLE_STAT_INPUT_DATATYPE
     Specify the data type of the input directory for forecast files used with the MET ensemble_stat tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. Similar variables exists for observation grid and point data called :term:`OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE` and :term:`OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE
     Specify the data type of the input directory for grid observation files used with the MET ensemble_stat tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_GRID_INPUT_DIR
     Input directory for grid observation files to use with the MET tool ensemble_stat. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_DIR`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE
     Template used to specify grid observation input filenames for the MET tool ensemble_stat. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_NUMPY or PYTHON_XARRAY.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE
     Specify the data type of the input directory for point observation files used with the MET ensemble_stat tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_DATATYPE`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_POINT_INPUT_DIR
     Input directory for point observation files to use with the MET tool ensemble_stat. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_DIR`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE
     Template used to specify point observation input filenames for the MET tool ensemble_stat. A similar variable exists for forecast data called :term:`FCST_ENSEMBLE_STAT_INPUT_TEMPLATE`. To utilize Python Embedding as input to the MET tools, set this value to PYTHON_PANDAS.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by EnsembleStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by EnsembleStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_ENSEMBLE_STAT_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  EnsembleStat

   OBS_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds.This value will be used for all wrappers that look for an observation file unless it is overridden by a wrapper specific configuration variable. For example, if :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN` is set, the GridStat wrapper will use that value. If :term:`PB2NC_FILE_WINDOW_BEGIN` is not set, then the PB2NC wrapper will use :term:`OBS_FILE_WINDOW_BEGIN`.A corresponding variable exists for forecast data called :term:`FCST_FILE_WINDOW_BEGIN`.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   OBS_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds.This value will be used for all wrappers that look for an observation file unless it is overridden by a wrapper specific configuration variable. For example, if :term:`OBS_GRID_STAT_WINDOW_END` is set, the GridStat wrapper will use that value. If :term:`PB2NC_WINDOW_END` is not set, then the PB2NC wrapper will use :term:`OBS_WINDOW_END`. A corresponding variable exists for forecast data called :term:`FCST_FILE_WINDOW_END`.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PB2NC, PointStat

   FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used
     for processing. See :ref:`Directory_and_Filename_Template_Info` subsection called
     'Using Windows to Find Valid Files.' Units are seconds. This value will be used for all wrappers that look for
     all files unless it is overridden by a wrapper specific configuration variable. For example,
     if :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN` is set, the GridStat wrapper will use that value.
     If :term:`PB2NC_FILE_WINDOW_BEGIN` is not set, then the PB2NC wrapper will use
     :term:`OBS_FILE_WINDOW_BEGIN`. If :term:`OBS_FILE_WINDOW_BEGIN` is not set, it will use FILE_WINDOW_BEGIN if it
     is set. If not, it will default to 0. If the begin and end file window values are both 0, then only a file
     matching the exact run time will be considered.

     | *Used by:*  All

   FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used
     for processing. See :ref:`Directory_and_Filename_Template_Info` subsection called
     'Using Windows to Find Valid Files.' Units are seconds. This value will be used for all wrappers that look for
     all files unless it is overridden by a wrapper specific configuration variable. For example,
     if :term:`OBS_GRID_STAT_FILE_WINDOW_END` is set, the GridStat wrapper will use that value.
     If :term:`PB2NC_FILE_WINDOW_END` is not set, then the PB2NC wrapper will use
     :term:`OBS_FILE_WINDOW_END`. If :term:`OBS_FILE_WINDOW_END` is not set, it will use FILE_WINDOW_END if it
     is set. If not, it will default to 0. If the begin and end file window values are both 0, then only a file
     matching the exact run time will be considered.

     | *Used by:*  All

   OBS_GRID_STAT_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by GridStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_GRID_STAT_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  GridStat

   OBS_GRID_STAT_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by GridStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_GRID_STAT_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  GridStat

   OBS_GRID_STAT_INPUT_DATATYPE
     See :term:`FCST_GRID_STAT_INPUT_DATATYPE`

     | *Used by:*  GridStat

   OBS_GRID_STAT_INPUT_DIR
     See :term:`FCST_GRID_STAT_INPUT_DIR`

     | *Used by:*  GridStat

   OBS_GRID_STAT_INPUT_TEMPLATE
     See :term:`FCST_GRID_STAT_INPUT_TEMPLATE`

     | *Used by:*  GridStat

   OBS_GRID_STAT_PROB_THRESH
     See :term:`FCST_GRID_STAT_PROB_THRESH`

     | *Used by:*  GridStat

   OBS_GEMPAK_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`GEMPAKTOCF_INPUT_DIR` instead.

   OBS_GEMPAK_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`GEMPAKTOCF_INPUT_TEMPLATE` instead.

   OBS_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`OBS_POINT_STAT_INPUT_DIR` instead.

   OBS_INPUT_DIR_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`OBS_POINT_STAT_INPUT_DIR` instead.

   OBS_INPUT_FILE_REGEX
     .. warning:: **DEPRECATED:** Please use :term:`OBS_POINT_STAT_INPUT_TEMPLATE` instead.

   OBS_INPUT_FILE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`OBS_POINT_STAT_INPUT_TEMPLATE` instead.

   OBS_IS_DAILY_FILE
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_IS_DAILY_FILE` instead.

   OBS_IS_PROB
     Used when setting OBS_* variables to process forecast data for comparisons with mtd. Specify whether the observation data are probabilistic or not. See :term:`FCST_IS_PROB` .Acceptable values: true/false

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PointStat

   OBS_PROB_IN_GRIB_PDS
     Specify whether the probabilistic observation data is stored in the GRIB Product Definition Section or not.Acceptable values: true/false. Only used when :term:`OBS_IS_PROB` is True. This does not need to be set if the OBS_<APP_NAME>_INPUT_DATATYPE is set to NetCDF.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PointStat

   OBS_LEVEL
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_INPUT_LEVEL` instead.

   OBS_MODE_CONV_RADIUS
     See :term:`FCST_MODE_CONV_RADIUS`

     | *Used by:*  MODE

   OBS_MODE_CONV_THRESH
     See :term:`FCST_MODE_CONV_THRESH`

     | *Used by:*  MODE

   OBS_MODE_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by MODE. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_MODE_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  MODE

   OBS_MODE_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by MODE. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_MODE_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  MODE

   OBS_MODE_MERGE_FLAG
     See :term:`FCST_MODE_MERGE_FLAG`.

     | *Used by:*  MODE

   OBS_MODE_MERGE_THRESH
     See :term:`FCST_MODE_MERGE_THRESH`.

     | *Used by:*  MODE

   OBS_MODE_INPUT_DATATYPE
     See :term:`FCST_MODE_INPUT_DATATYPE`.

     | *Used by:*  MODE

   OBS_MODE_INPUT_DIR
     See :term:`FCST_MODE_INPUT_DIR`.

     | *Used by:*  MODE

   OBS_MODE_INPUT_TEMPLATE
     See :term:`FCST_MODE_INPUT_TEMPLATE`.

     | *Used by:*  MODE

   OBS_MTD_CONV_RADIUS
     See :term:`FCST_MTD_CONV_RADIUS`.

     | *Used by:* MTD

   OBS_MTD_CONV_THRESH
     See :term:`FCST_MTD_CONV_THRESH`.

     | *Used by:* MTD

   OBS_MTD_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by MTD. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_MTD_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*

   OBS_MTD_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by MTD. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_MTD_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:* MTD

   OBS_MTD_INPUT_DATATYPE
     See :term:`FCST_MTD_INPUT_DATATYPE`.

     | *Used by:* MTD

   OBS_MTD_INPUT_DIR
     See :term:`FCST_MTD_INPUT_DIR`.

     | *Used by:* MTD

   OBS_MTD_INPUT_TEMPLATE
     See :term:`FCST_MTD_INPUT_TEMPLATE`.

     | *Used by:*

   OBS_NAME
     .. warning:: **DEPRECATED:** No longer used. Provide a string to identify the observation dataset name.

   OBS_NATIVE_DATA_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_INPUT_DATATYPE` instead.

   OBS_TIMES_PER_FILE
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_TIMES_PER_FILE` instead.

   FCST_TIMES_PER_FILE
     .. warning:: **DEPRECATED:** Please use :term:`FCST_PCP_COMBINE_TIMES_PER_FILE` instead.

   OBS_PCP_COMBINE_<n>_FIELD_NAME
     See :term:`FCST_PCP_COMBINE_<n>_FIELD_NAME`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_DATA_INTERVAL
     See :term:`FCST_PCP_COMBINE_DATA_INTERVAL`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_DERIVE_LOOKBACK
     See :term:`FCST_PCP_COMBINE_DERIVE_LOOKBACK`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_DATATYPE
     See :term:`FCST_PCP_COMBINE_INPUT_DATATYPE`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_DIR
     See :term:`FCST_PCP_COMBINE_INPUT_DIR`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_LEVEL
     See :term:`FCST_PCP_COMBINE_INPUT_LEVEL`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_TEMPLATE
     See :term:`FCST_PCP_COMBINE_INPUT_TEMPLATE`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_IS_DAILY_FILE
     See :term:`FCST_PCP_COMBINE_IS_DAILY_FILE`. Acceptable values: true/false

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_METHOD
     See :term:`FCST_PCP_COMBINE_METHOD`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_MIN_FORECAST
     See :term:`FCST_PCP_COMBINE_MIN_FORECAST`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_MAX_FORECAST
     See :term:`FCST_PCP_COMBINE_MAX_FORECAST`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_OUTPUT_DIR
     See :term:`FCST_PCP_COMBINE_OUTPUT_DIR`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_OUTPUT_TEMPLATE
     See :term:`FCST_PCP_COMBINE_OUTPUT_TEMPLATE`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_RUN
     See :term:`FCST_PCP_COMBINE_RUN`. Acceptable values: true/false

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_STAT_LIST
     See :term:`FCST_PCP_COMBINE_STAT_LIST`. Acceptable values: sum, min, max, range, mean, stdev, vld_count

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_TIMES_PER_FILE
     See :term:`FCST_PCP_COMBINE_TIMES_PER_FILE`.

     | *Used by:*  PCPCombine

   OBS_POINT_STAT_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by PointStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_POINT_STAT_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  PointStat

   OBS_POINT_STAT_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by PointStat. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`OBS_POINT_STAT_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  PointStat

   OBS_POINT_STAT_INPUT_DATATYPE
     See :term:`FCST_POINT_STAT_INPUT_DATATYPE`.

     | *Used by:*  PointStat

   OBS_POINT_STAT_INPUT_DIR
     See :term:`FCST_POINT_STAT_INPUT_DIR`.

     | *Used by:*  PointStat

   OBS_POINT_STAT_INPUT_TEMPLATE
     See :term:`FCST_POINT_STAT_INPUT_TEMPLATE`.

     | *Used by:*  GriPointStat

   FCST_POINT_STAT_WINDOW_BEGIN
     Passed to the PointStat MET config file to determine the range of data within a file that should be used for processing forecast data. Units are seconds. If the variable is not set, PointStat will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  PointStat

   FCST_POINT_STAT_WINDOW_END
     Passed to the PointStat MET config file to determine the range of data within a file that should be used for processing forecast data. Units are seconds. If the variable is not set, PointStat will use :term:`OBS_WINDOW_END`.

     | *Used by:*  PointStat

   OBS_POINT_STAT_WINDOW_BEGIN
     Passed to the PointStat MET config file to determine the range of data within a file that should be used for processing observation data. Units are seconds. If the variable is not set, PointStat will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  PointStat

   OBS_POINT_STAT_WINDOW_END
     Passed to the PointStat MET config file to determine the range of data within a file that should be used for processing observation data. Units are seconds. If the variable is not set, PointStat will use :term:`OBS_WINDOW_END`.

     | *Used by:*  PointStat

   FCST_GRID_STAT_WINDOW_BEGIN
     Passed to the GridStat MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, GridStat will use :term:`FCST_WINDOW_BEGIN`.

     | *Used by:*  GridStat

   FCST_GRID_STAT_WINDOW_END
     Passed to the GridStat MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, GridStat will use :term:`FCST_WINDOW_END`.

     | *Used by:*  GridStat

   OBS_GRID_STAT_WINDOW_BEGIN
     Passed to the GridStat MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, GridStat will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  GridStat

   OBS_GRID_STAT_WINDOW_END
     Passed to the GridStat MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, GridStat will use :term:`OBS_WINDOW_END`.

     | *Used by:*  GridStat

   FCST_MODE_WINDOW_BEGIN
     Passed to the MODE MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, MODE will use :term:`FCST_WINDOW_BEGIN`.

     | *Used by:*  MODE

   FCST_MODE_WINDOW_END
     Passed to the MODE MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, MODE will use :term:`FCST_WINDOW_END`.

     | *Used by:*  MODE

   OBS_MODE_WINDOW_BEGIN
     Passed to the MODE MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, MODE will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  MODE

   OBS_MODE_WINDOW_END
     Passed to the MODE MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, MODE will use :term:`OBS_WINDOW_END`.

     | *Used by:*  MODE

   OBS_ENSEMBLE_STAT_WINDOW_BEGIN
     Passed to the EnsembleStat MET config file to determine the range of data within a file that should be used for processing observation data. Units are seconds. If the variable is not set, EnsembleStat will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  EnsembleStat

   OBS_ENSEMBLE_STAT_WINDOW_END
     Passed to the EnsembleStat MET config file to determine the range of data within a file that should be used for processing observation data. Units are seconds. If the variable is not set, ensemble_stat will use :term:`OBS_WINDOW_END`.

     | *Used by:*  EnsembleStat

   FCST_ENSEMBLE_STAT_WINDOW_BEGIN
     Passed to the EnsembleStat MET config file to determine the range of data within a file that should be used for processing forecast data. Units are seconds. If the variable is not set, EnsembleStat will use :term:`FCST_WINDOW_BEGIN`.

     | *Used by:*  EnsembleStat

   FCST_ENSEMBLE_STAT_WINDOW_END
     Passed to the EnsembleStat MET config file to determine the range of data within a file that should be used for processing forecast data. Units are seconds. If the variable is not set, ensemble_stat will use :term:`FCST_WINDOW_END`.

     | *Used by:*  EnsembleStat

   OBS_REGRID_DATA_PLANE_INPUT_DATATYPE
     See :term:`FCST_REGRID_DATA_PLANE_INPUT_DATATYPE`.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_INPUT_DIR
     See :term:`FCST_REGRID_DATA_PLANE_INPUT_DIR`.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE
     See :term:`FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE`.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE
     See :term:`FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE`.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_TEMPLATE
     See :term:`FCST_REGRID_DATA_PLANE_TEMPLATE`.

     | *Used by:*  RegridDataPlane

   OBS_REGRID_DATA_PLANE_OUTPUT_DIR
     See :term:`FCST_REGRID_DATA_PLANE_OUTPUT_DIR`.

     | *Used by:*  RegridDataPlane

   OBS_VAR
     .. warning:: **DEPRECATED:** Specify the string for the observation variable used in the analysis. See :term:`OBS_VAR<n>_NAME`, :term:`OBS_VAR<n>_LEVELS`, :term:`OBS_VAR<n>_OPTIONS` and :term:`OBS_VAR<n>_THRESH` where n = integer >= 1.

   OBS_VAR_LEVEL
     .. warning:: **DEPRECATED:** Please use :term:`OBS_LEVEL_LIST` instead.

   OBS_LEVEL_LIST
     Specify the values of the OBS_LEV column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   OBS_VAR_NAME
     .. warning:: **DEPRECATED:** Please use :term:`OBS_VAR_LIST` instead.

   OBS_VAR_LIST
     Specify the values of the OBS_VAR column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   OBS_UNITS_LIST
     Specify the values of the OBS_UNITS column in the MET .stat file to use. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   OBS_VAR<n>_LEVELS
     Define the levels for the <n>th observation variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items. You can define NetCDF levels, such as (0,*,*), but you will need to surround these values with quotation marks so that the commas in the item are not interpreted as an item delimeter. Some examples:

     | OBS_VAR1_LEVELS = A06, P500
     | OBS_VAR2_LEVELS = "(0,*,*)", "(1,*,*)"

     There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | OBS_VAR1_LEVELS
     | OBS_VAR2_LEVELS
     | ...
     | OBS_VAR<n>_LEVELS

     If :term:`OBS_VAR<n>_LEVELS` is set, then :term:`FCST_VAR<n>_LEVELS` must be set as well. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_LEVELS`.

     See :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   OBS_VAR<n>_NAME
     Define the name for the <n>th observation variable to be used in the analysis where <n> is an integer >= 1. If :term:`OBS_VAR<n>_NAME` is set, then :term:`FCST_VAR<n>_NAME` must be set. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_NAME`. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | OBS_VAR1_NAME
     | OBS_VAR2_NAME
     | ...
     | OBS_VAR<n>_NAME

     This value can be set to a call to a python script with arguments to supply data to the MET tools via Python Embedding. Filename template syntax can be used here to specify time information of an input file, i.e. {valid?fmt=%Y%m%d%H}. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information about Python Embedding in the MET tools.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   OBS_VAR<n>_OPTIONS
     Define the options for the <n>th observation variable to be used in the analysis where <n> is an integer >= 1. These addition options will be applied to every name/level/threshold combination for VAR<n>. If OBS_VAR<n>_OPTIONS is not set but :term:`FCST_VAR<n>_OPTIONS` is, the same information will be used for both variables. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | OBS_VAR1_OPTIONS
     | OBS_VAR2_OPTIONS
     | ...
     | OBS_VAR<n>_OPTIONS

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   OBS_VAR<n>_THRESH
     Define the threshold(s) for the <n>th observation variable to be used in the analysis where <n> is an integer >= 1. The value can be a single item or a comma separated list of items that must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le). If :term:`OBS_VAR<n>_THRESH` is not set but :term:`FCST_VAR<n>_THRESH` is, the same information will be used for both variables. There can be <n> number of these variables defined in configuration files, simply increment the VAR1 string to match the total number of variables being used, e.g.:

     | OBS_VAR1_THRESH
     | OBS_VAR2_THRESH
     | ...
     | OBS_VAR<n>_THRESH

     If OBS_VAR<n>_THRESH is set, then :term:`FCST_VAR<n>_THRESH` must be set as well. If the same value applies to both forecast and observation data, use :term:`BOTH_VAR<n>_THRESH`.

     See :ref:`Field_Info` for more information.

     | *Used by:*  GridStat, EnsembleStat, PointStat, MODE, MTD, PCPCombine

   OBS_WINDOW_BEG
     .. warning:: **DEPRECATED:** Please use :term:`OBS_WINDOW_BEGIN`.

   OBS_WINDOW_BEGIN
     Passed to the MET config file to determine the range of data within a file that should be used for processing.Units are seconds. This value will be used for all wrappers that look for an observation file unless it is overridden by a wrapper specific configuration variable. For example, if :term:`OBS_POINT_STAT_WINDOW_BEGIN` is set, the PointStat wrapper will use that value. If :term:`PB2NC_WINDOW_BEGIN` is not set, then the PB2NC wrapper will use :term:`OBS_WINDOW_BEGIN`. A corresponding variable exists for forecast data called :term:`FCST_WINDOW_BEGIN`.

     | *Used by:*  PB2NC, PointStat

   OBS_WINDOW_END
     Passed to the MET config file to determine the range of data within a file that should be used for processing.Units are seconds. This value will be used for all wrappers that look for an observation file unless it is overridden by a wrapper specific configuration variable. For example, if :term:`OBS_POINT_STAT_WINDOW_END` is set, the PointStat wrapper will use that value. If :term:`PB2NC_WINDOW_END` is not set, then the PB2NC wrapper will use :term:`OBS_WINDOW_END`. A corresponding variable exists for forecast data called :term:`FCST_WINDOW_END`.

     | *Used by:*  PB2NC, PointStat

   OBTYPE
     Provide a string to represent the type of observation data used in the analysis. This is the observation time listed in the MET .stat files and is used in setting output filename.

     | *Used by:*  EnsembleStat, GridStat, MODE, MTD, PointStat

   OB_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`OBTYPE` instead.

   OUTPUT_BASE
     Provide a path to the top level output directory for METplus.

     | *Used by:*  All

   OVERWRITE_NC_OUTPUT
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_SKIP_IF_OUTPUT_EXISTS` instead.

   EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS
     Specify whether to overwrite the track data or not.
     Acceptable values: yes/no

     | *Used by:*  ExtractTiles

   EXTRACT_TILES_OVERWRITE_TRACK
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS` instead.

   OVERWRITE_TRACK
     .. warning:: **DEPRECATED:** Please use :term:`EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS` instead.

   PARM_BASE
     This variable will automatically be set by METplus when it is started. Specifies the top level METplus parameter file directory. You can override this value by setting the environment variable METPLUS_PARM_BASE to another directory containing a copy of the METPlus parameter file directory. If the environment variable is not set, the parm directory corresponding to the calling script is used. It is recommended that this variable is not set by the user. If it is set and is not equivalent to the value determined by METplus, execution will fail.

     | *Used by:*  All

   PB2NC_CONFIG_FILE
     Specify the absolute path to the configuration file for the MET pb2nc tool.

     | *Used by:*  PB2NC

   PB2NC_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a file should be used for processing by PB2NC. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`PB2NC_FILE_WINDOW_BEGIN` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_BEGIN` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  PB2NC

   PB2NC_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if a file should be used for processing by PB2NC. See :ref:`Directory_and_Filename_Template_Info` subsection called 'Using Windows to Find Valid Files.' Units are seconds. If :term:`PB2NC_FILE_WINDOW_END` is not set in the config file, the value of :term:`OBS_FILE_WINDOW_END` will be used instead. If both file window begin and window end values are set to 0, then METplus will require an input file with an exact time match to process.

     | *Used by:*  PB2NC

   PB2NC_VALID_BEGIN
     Used to set the command line argument -valid_beg that controls the lower bound of valid times of data to use. Filename template notation can be used, i.e. {valid?fmt=%Y%m%d_%H%M%S}

     | *Used by:*  PB2NC

   PB2NC_VALID_END
     Used to set the command line argument -valid_end that controls the upper bound of valid times of data to use. Filename template notation can be used, i.e. {valid?fmt=%Y%m%d_%H%M%S?shift=1d} (valid time shifted forward one day)

     | *Used by:*  PB2NC

   PB2NC_GRID
     Specify a grid to use with the MET pb2nc tool.

     | *Used by:*  PB2NC

   PB2NC_INPUT_DATATYPE
     Specify the data type of the input directory for prepbufr files used with the MET pb2nc tool. Currently valid options are NETCDF, GRIB, and GEMPAK. If set to GEMPAK, data will automatically be converted to NetCDF via GempakToCF.

     | *Used by:*  PB2NC

   PB2NC_MESSAGE_TYPE
     Specify which PREPBUFR (PB) message types to convert using the MET pb2nc tool.

     | *Used by:*  PB2NC

   PB2NC_OBS_BUFR_VAR_LIST
     Specify which BUFR codes to use from the observation dataset when using the MET pb2nc tool. Format is comma separated list, e.g.:PMO, TOB, TDO

     | *Used by:*  PB2NC

   PB2NC_OFFSETS
     A list of potential offsets (in hours) that can be found in the :term:`PB2NC_INPUT_TEMPLATE`. METplus will check if a file with a given offset exists in the order specified in this list, to be sure to put favored offset values first.

     | *Used by:*  PB2NC

   POINT_STAT_OFFSETS
     A list of potential offsets (in hours) that can be found in the :term:`OBS_POINT_STAT_INPUT_TEMPLATE` and  :term:`FCST_POINT_STAT_INPUT_TEMPLATE`. METplus will check if a file with a given offset exists in the order specified in this list, to be sure to put favored offset values first.

     | *Used by:*  PointStat

   PB2NC_OUTPUT_DIR
     Specify the directory where files will be written from the MET pb2nc tool. 

     | *Used by:*  PB2NC

   PB2NC_SKIP_IF_OUTPUT_EXISTS
     If True, do not run PB2NC if output file already exists. Set to False to overwrite files.

     | *Used by:*  PB2NC

   PB2NC_STATION_ID
     Specify the ID of the station to use with the MET PB2NC tool.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_FLAG
     Specify the time summary flag item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_BEG
     Specify the time summary beg item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_END
     Specify the time summary end item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_VAR_NAMES
     Specify the time summary obs_var list item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   TIME_SUMMARY_VAR_NAMES
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_TIME_SUMMARY_VAR_NAMES` instead.

   TIME_SUMMARY_TYPES
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_TIME_SUMMARY_TYPES` instead.

   PB2NC_TIME_SUMMARY_TYPES
     Specify the time summary type list item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_WINDOW_BEGIN
     Passed to the pb2nc MET config file to determine the range of data within a file that should be used for processing.Units are seconds. If the variable is not set, pb2nc will use :term:`OBS_WINDOW_BEGIN`.

     | *Used by:*  PB2NC

   PB2NC_WINDOW_END
     Passed to the pb2nc MET config file to determine the range of data within a file that should be used for processing. Units are seconds. If the variable is not set, pb2nc will use :term:`OBS_WINDOW_END`.

     | *Used by:*  PB2NC

   PCP_COMBINE_METHOD
     .. warning:: **DEPRECATED:** Please use :term:`OBS_PCP_COMBINE_METHOD` and/or  :term:`FCST_PCP_COMBINE_METHOD` instead.

   PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS
     If True, do not run pcp_combine if output file already exists. Set to False to overwrite files.

     | *Used by:*  PCPCombine

   PLOTTING_OUTPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_OUTPUT_DIR` instead.

   PLOTTING_SCRIPTS_DIR
      .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_SCRIPTS_DIR` instead.

   PLOT_CONFIG_OPTS
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_PLOT_CONFIG_OPTS` instead.

   TCMPR_PLOTTER_PLOT_CONFIG_OPTS
     Specify plot configuration options for the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   PLOT_STATS_LIST
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_STATS_LIST` instead.

   MAKE_PLOTS_STATS_LIST
     This is a list of the statistics to calculate and create plots for. Specify the list in a comma-separated list, e.g.:

     acc, bias, rmse

     The list of valid options varies depending on line type that was used during the filtering of stat_analysis_wrapper. For SL1L2, VL1L2 valid options are bias, rms, msess, rsd, rmse_md, rmse_pv, pcor, fbar, and fbar_obar. For SAL1L2, VAL1L2, the valid options is acc. For VCNT, bias, fbar, fbar_obar, speed_err, dir_err, rmsve, vdiff_speed, vdiff_dir, rsd, fbar_speed, fbar_dir, fbar_obar_speed, and fbar_obar_dir. For CTC, rate, baser, frate, orate_frate, baser_frate, accuracy, bias, fbias, pod, hrate, pofd, farate, podn, faratio, csi, ts, gss, ets, hk, tss, pss, hs

     | *Used by:*  MakePlots

   PLOT_TIME
     .. warning:: **DEPRECATED:** Please use :term:`DATE_TYPE` instead.

   DATE_TYPE
     In StatAnalysis, this specifies the way to treat the date information, where valid options are VALID and INIT.

     | *Used by:*  MakePlots, StatAnalysis

   PLOT_TYPES
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_PLOT_TYPES` instead.

   TCMPR_PLOTTER_PLOT_TYPES
     Specify what plot types are desired for the TC Matched Pairs plotting tool. By default, a boxplot is generated if this is undefined in the configuration file. If other plots are requested and a boxplot is also desired, you must explicitly listboxplot in your list of plot types. Supported plot types: BOXPLOT, POINT, MEAN, MEDIAN, RELPERF (relative performance), RANK (time series of ranks for the first model), SCATTER, SKILL_MN (mean skill scores) and SKILL_MD (median skill scores).

     | *Used by:*  TCMPRPlotter

   POINT_STAT_CONFIG_FILE
     Specify the absolute path to the configuration file to be used with the MET point_stat tool.

     | *Used by:*  PointStat

   POINT_STAT_GRID
     Specify the grid to use with the MET point_stat tool.

     .. note:: please use :term:`POINT_STAT_MASK_GRID`

     | *Used by:*  PointStat

   POINT_STAT_MESSAGE_TYPE
     Specify which PREPBUFR message types to process with the MET point_stat tool.

     | *Used by:*  PointStat

   POINT2GRID_OUTPUT_DIR
     Specify the directory where output files from the MET point2grid tool are written.

     | *Used by:*  Point2Grid

   POINT_STAT_OUTPUT_DIR
     Specify the directory where output files from the MET point_stat tool are written.

     | *Used by:*  PointStat

   POINT_STAT_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`POINT_STAT_OUTPUT_DIR` using a template to allow run time information. If LOOP_BY = VALID, default value is valid time YYYYMMDDHHMM/point_stat. If LOOP_BY = INIT, default value is init time YYYYMMDDHHMM/point_stat.

     | *Used by:*  PointStat

   POINT_STAT_POLY
     Specify a polygon to use with the MET PointStat tool.

     .. note:: please use :term:`POINT_STAT_MASK_POLY`

     | *Used by:*  PointStat

   PB2NC_POLY
     .. note:: please use :term:`PB2NC_MASK_POLY`

     | *Used by:*  PB2NC

   POINT_STAT_STATION_ID
     Specify the ID of a specific station to use with the MET point_stat tool.

     | *Used by:*  PointStat

   POINT_STAT_VERIFICATION_MASK_TEMPLATE
     Template used to specify the verification mask filename for the MET tool point_stat. Now supports a list of filenames.

     | *Used by:*  PointStat

   PB2NC_VERTICAL_LEVEL
     .. warning:: **DEPRECATED:** No longer used.

   PREFIX
     This corresponds to the optional -prefix flag of the plot_TCMPR.R script (which is wrapped by TCMPRPlotter). This is the output file name prefix.

     | *Used by:*  TCMPRPlotter

   PREPBUFR_DIR_REGEX
     .. warning:: **DEPRECATED:** No longer used. Regular expression to use when searching for PREPBUFR data.

   PREPBUFR_FILE_REGEX
     .. warning:: **DEPRECATED:** No longer used. Regular expression to use when searching for PREPBUFR files.

   PREPBUFR_MODEL_DIR_NAME
     .. warning:: **DEPRECATED:** Please put the value previously used here in the :term:`PB2NC_INPUT_DIR` path. Specify the name of the model being used with the MET pb2nc tool.

   PROCESS_LIST
     Specify the list of processes for METplus to perform, in a comma separated list.

     | *Used by:*  All

   INPUT_BASE
     Provide a path to the top level output directory for METplus.  It is required and must be set correctly to run any of the use cases. This can be the location of sample input data to run use cases found in the METplus repository.  Each of the sample data tarballs attached to the METplus release should be untarred in this directory. If done correctly, this directory should contain a directory named 'met_test' and a directory named 'model_applications.'

     | *Used by:*  All

   PROJ_DIR
     .. warning:: **DEPRECATED:** Please use :term:`INPUT_BASE` instead.

   REFERENCE_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_BDECK_TEMPLATE`.

   REGION
     .. warning:: **DEPRECATED:** Please use :term:`VX_MASK_LIST` instead.

   REGION_LIST
     .. warning:: **DEPRECATED:** Please use :term:`VX_MASK_LIST` instead.

   VX_MASK_LIST
     Specify the values of the VX_MASK column in the MET .stat file to use; a list of the verification regions of interest.

     | *Used by:*  MakePlots, StatAnalysis

   POINT2GRID_REGRID_METHOD
     Sets the gridding method used by point2grid.

     | *Used by:*  Point2Grid

   REGRID_DATA_PLANE_METHOD
     Sets the method used by regrid_data_plane. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  RegridDataPlane

   REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS
     If True, do not run regrid_data_plane if output file already exists. Set to False to overwrite files.

     | *Used by:*  RegridDataPlane

   REGRID_DATA_PLANE_WIDTH
     Sets the width used by regrid_data_plane. See `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  RegridDataPlane

   REGRID_DATA_PLANE_VERIF_GRID
     Specify the absolute path to a file containing information about the desired output grid from the MET regrid_data_plane tool.

     | *Used by:*  RegridDataPlane

   RM
     .. warning:: **DEPRECATED:** Do not use.

   RM_EXE
     .. warning:: **DEPRECATED:** Do not use.

   RP_DIFF
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_RP_DIFF` instead.

   TCMPR_PLOTTER_RP_DIFF
     This corresponds to the optional -rp_diff flag of the plot_TCMPR.R script (which is wrapped by TCMPRPlotter). This a comma-separated list of thresholds to specify meaningful differences for the relative performance plot.

     | *Used by:*  TCMPRPlotter

   SAVE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SAVE` instead.

   TCMPR_PLOTTER_SAVE
     Corresponds to the optional -save flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is a yes/no value to indicate whether to save the image (yes).

     | *Used by:*  TCMPRPlotter

   SAVE_DATA
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SAVE_DATA` instead.

   TCMPR_PLOTTER_SAVE_DATA
     Corresponds to the optional -save_data flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). Indicates whether to save the filtered track data to a file instead of deleting it.

     | *Used by:*  TCMPRPlotter

   SCATTER_X
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SCATTER_X` instead.

   TCMPR_PLOTTER_SCATTER_X
     Corresponds to the optional -scatter_x flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is a comma-separated list of x-axis variable columns to plot.

     | *Used by:*  TCMPRPlotter

   SCATTER_Y
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SCATTER_Y` instead.

   TCMPR_PLOTTER_SCATTER_Y
     Corresponds to the optional -scatter_y flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is a comma-separated list of y-axis variable columns to plot.

     | *Used by:*  TCMPRPlotter

   SCRUB_STAGING_DIR
     Remove staging directory after METplus has completed running if set to True. Set to False to preserve data for subsequent runs.

     | *Used by:* All

   SERIES
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SERIES` instead.

   TCMPR_PLOTTER_SERIES
     Corresponds to the optional -series flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is the column whose unique values define the series on the plot, optionally followed by a comma-separated list of values, including: ALL, OTHER, and colon-separated groups.

     | *Used by:*  TCMPRPlotter

   SERIES_ANALYSIS_CONFIG_FILE
     Specify the absolute path for the configuration file to use with the MET series_analysis tool by initialization time.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_BY_INIT_CONFIG_FILE
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CONFIG_FILE` instead.

   SERIES_ANALYSIS_BY_LEAD_CONFIG_FILE
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_CONFIG_FILE` instead.

   SERIES_ANALYSIS_FILTER_OPTS
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_JOB_ARGS` instead.

   SERIES_ANALYSIS_FILTERED_OUTPUT
     .. warning:: **DEPRECATED:** No longer used.


   SERIES_ANALYSIS_FILTERED_OUTPUT_DIR
     .. warning:: **DEPRECATED:** No longer used.

   SERIES_BY_INIT_FILTERED_OUTPUT_DIR
     .. warning:: **DEPRECATED:** No longer used.

   SERIES_BY_INIT_OUTPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_OUTPUT_DIR` instead.

   SERIES_BY_LEAD_FILTERED_OUTPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_FILTERED_OUTPUT_DIR` instead.

   SERIES_BY_LEAD_FILTERED_OUTPUT
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_FILTERED_OUTPUT_DIR` instead.

   SERIES_ANALYSIS_GROUP_FCSTS
     .. warning:: **DEPRECATED:** Please use :term:`LEAD_SEQ_\<n>` and :term:`SERIES_ANALYSIS_RUNTIME_FREQ` instead.

   SERIES_BY_LEAD_GROUP_FCSTS
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_GROUP_FCSTS` instead.

   SERIES_CI
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SERIES_CI` instead.

   TCMPR_PLOTTER_SERIES_CI
     Corresponds to the optional -series_ci flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is a list of true/false for confidence intervals. This list can be optionally followed by a comma-separated list of values, including ALL, OTHER, and colon-separated groups.

     | *Used by:*  TCMPRPlotter

   SERIES_INIT_FILTERED_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_FILTERED_OUTPUT_DIR` instead.

   SERIES_ANALYSIS_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_TILE_INPUT_DIR` instead.

   SERIES_ANALYSIS_TILE_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`FCST_SERIES_ANALYSIS_INPUT_DIR` and  :term:`OBS_SERIES_ANALYSIS_INPUT_DIR` instead.

   FCST_SERIES_ANALYSIS_TILE_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`FCST_SERIES_ANALYSIS_INPUT_DIR` instead.

   OBS_SERIES_ANALYSIS_TILE_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`OBS_SERIES_ANALYSIS_INPUT_DIR` instead.

   FCST_SERIES_ANALYSIS_INPUT_DIR
     Specify the directory to read forecast input in SeriesAnalysis. See also :term:`FCST_SERIES_ANALYSIS_INPUT_TEMPLATE`

     | *Used by:*  SeriesAnalysis

   OBS_SERIES_ANALYSIS_INPUT_DIR
     Specify the directory to read observation input in SeriesAnalysis. See also :term:`OBS_SERIES_ANALYSIS_INPUT_TEMPLATE`

     | *Used by:*  SeriesAnalysis

   FCST_SERIES_ANALYSIS_INPUT_TEMPLATE
     Template to find forecast input in SeriesAnalysis. See also :term:`FCST_SERIES_ANALYSIS_INPUT_DIR`

     | *Used by:*  SeriesAnalysis

   OBS_SERIES_ANALYSIS_INPUT_TEMPLATE
     Template to find observation input in SeriesAnalysis. See also :term:`OBS_SERIES_ANALYSIS_INPUT_DIR`

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_OUTPUT_DIR
     Specify the directory where files will be written from the MET series analysis tool.

     | *Used by:*  SeriesAnalysis

   SERIES_INIT_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_OUTPUT_DIR` instead.

   SERIES_LEAD_FILTERED_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_FILTERED_OUTPUT_DIR`.

   SERIES_LEAD_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_OUTPUT_DIR` instead.

   SERIES_BY_LEAD_OUTPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_OUTPUT_DIR` instead.

   SKILL_REF
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SKILL_REF` instead.

   TCMPR_PLOTTER_SKILL_REF
     This corresponds to the optional -skill_ref flag in plot_TCMPR.R (which is wrapped by TCMPRPlotter). This is the identifier for the skill score reference.

     | *Used by:*  TCMPRPlotter

   START_DATE
     .. warning:: **DEPRECATED:** Please use :term:`INIT_BEG` or :term:`VALID_BEG` instead.

   STAGING_DIR
     Directory to uncompress or convert data into for use in METplus.

     | *Used by:* All

   START_HOUR
     .. warning:: **DEPRECATED:** Please use :term:`INIT_BEG` or :term:`VALID_BEG` instead.

   STAT_ANALYSIS_CONFIG
     .. warning:: **DEPRECATED:** Please use :term:`STAT_ANALYSIS_CONFIG_FILE` instead.

   STAT_ANALYSIS_CONFIG_FILE
     Specify the absolute path for the configuration file used with the MET stat_analysis tool. It is recommended to set this to {PARM_BASE}/use_cases/plotting/met_config/STATAnalysisConfig.

     | *Used by:*  StatAnalysis

   STAT_ANALYSIS_DUMP_ROW_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE` instead.

   MODEL<n>_STAT_ANALYSIS_DUMP_ROW_TEMPLATE
     Specify the template to use for the stat_analysis dump_row file. A user customized template to use for the dump_row file. If left blank and a dump_row file is requested, a default version will be used. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   STAT_ANALYSIS_LOOKIN_DIR
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR` instead.

   MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR
     Specify the input directory where the MET stat_analysis tool will find input files. This is the directory that the stat_analysis wrapper will use to build the argument to -lookin for the MET stat_analysis tool. It can contain wildcards, i.e. \*.

     | *Used by:*  StatAnalysis

   STAT_ANALYSIS_OUT_STAT_TMPL
     .. warning:: **DEPRECATED:** Please use :term:`MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE` instead.

   MODEL<n>_STAT_ANALYSIS_OUT_STAT_TEMPLATE
     Specify the template to use for the stat_analysis out_stat file. A user customized template to use for the out_stat file. If left blank and a out_stat file is requested, a default version will be used. This is optional in the METplus configuration file for running with :term:`LOOP_ORDER` = times.

     | *Used by:*  StatAnalysis

   STAT_ANALYSIS_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`STAT_ANALYSIS_OUTPUT_DIR` instead.

   STAT_ANALYSIS_OUTPUT_DIR
     This is the base directory where the output from running stat_analysis_wrapper will be put.

     | *Used by:*  StatAnalysis

   STAT_FILES_INPUT_DIR
      .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_INPUT_DIR` instead.

   SERIES_ANALYSIS_STAT_LIST
     Specify a list of statistics to be computed by the MET series_analysis tool. Sets the 'cnt' value in the output_stats dictionary in the MET SeriesAnalysis config file

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CTS_LIST
     Specify a list of contingency table statistics to be computed by the MET series_analysis tool. Sets the 'cts' value in the output_stats dictionary in the MET SeriesAnalysis config file

     | *Used by:* SeriesAnalysis

   STAT_LIST
     .. warning:: **DEPRECATED:** Please use :term:`SERIES_ANALYSIS_STAT_LIST` instead.

   STORM_ID
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_STORM_ID` or :term:`TC_STAT_STORM_ID`.

   STORM_NAME
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_STORM_NAME`.

   SUBTITLE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_SUBTITLE`.

   TCMPR_PLOTTER_SUBTITLE
     The subtitle of the plot.

     | *Used by:*  TCMPRPlotter

   TCMPR_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_TCMPR_DATA_DIR`.

   TCMPR_PLOTTER_TCMPR_DATA_DIR
     Provide the input directory for the track data for the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   TCMPR_PLOT_OUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_PLOT_OUTPUT_DIR`.

   TCMPR_PLOTTER_PLOT_OUTPUT_DIR
     Provide the output directory where the TC Matched Pairs plotting tool will create files.

     | *Used by:*  TCMPRPlotter

   TC_PAIRS_ADECK_INPUT_DIR
     Directory that contains the ADECK files.

     | *Used by:*  TCPairs

   TC_PAIRS_ADECK_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_ADECK_INPUT_TEMPLATE`.

   TC_PAIRS_BDECK_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_BDECK_INPUT_TEMPLATE`.

   TC_PAIRS_EDECK_TEMPLATE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_EDECK_INPUT_TEMPLATE`.

   TC_PAIRS_ADECK_INPUT_TEMPLATE
     Template of the file names of ADECK data.

     | *Used by:*  TCPairs

   TC_PAIRS_BASIN
     Control what basins are desired for tropical cyclone analysis. Per the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ acceptable basin ID's are:WP = Western Northern PacificIO = Northern Indian OceanSH = Southern HemisphereCP = Central Northern PacificEP = Eastern Northern PacificAL = Northern AtlanticSL = Southern Atlantic

     | *Used by:*  TCPairs

   TC_PAIRS_BDECK_INPUT_DIR
     Directory that contains the BDECK files.

     | *Used by:*  TCPairs

   TC_PAIRS_BDECK_INPUT_TEMPLATE
     Template of the file names of BDECK data.

     | *Used by:*  TCPairs

   TC_PAIRS_CONFIG_FILE
     Provide the absolute path to the configuration file for the MET tc_pairs tool.

     | *Used by:*  TCPairs

   TC_PAIRS_CYCLONE
     Specify which cyclone numbers to include in the tropical cyclone analysis. Per the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_, this can be any number 01-99 (HH format). Use a space or comma separated list, or leave unset if all cyclones are desired.

     | *Used by:*  TCPairs

   TC_PAIRS_DLAND_FILE
     The file generated by the MET tool tc_dland, containing the gridded representation of the minimum distance to land. Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information about the tc_dland tool.

     | *Used by:*  TCPairs

   TC_PAIRS_EDECK_INPUT_DIR
     Directory that contains the EDECK files.

     | *Used by:*  TCPairs

   TC_PAIRS_EDECK_INPUT_TEMPLATE
     Template of the file names of EDECK data.

     | *Used by:*  TCPairs

   TC_PAIRS_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_OUTPUT_DIR`.

   TC_PAIRS_FORCE_OVERWRITE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_SKIP_IF_OUTPUT_EXISTS`.

   TC_PAIRS_MODEL
     .. warning:: **DEPRECATED:** Please use :term:`MODEL` instead.

   TC_PAIRS_MISSING_VAL
     Specify the missing value code.

     | *Used by:*  TCPairs

   TC_PAIRS_MISSING_VAL_TO_REPLACE
     Specify the missing value code to replace.

     | *Used by:*  TCPairs

   TC_PAIRS_OUTPUT_DIR
     Specify the directory where the MET tc_pairs tool will write files.

     | *Used by:*  TCPairs

   TC_PAIRS_OUTPUT_TEMPLATE
     Template of the output file names created by tc_pairs.

     | *Used by:*  TCPairs

   TC_PAIRS_READ_ALL_FILES
     Specify whether to pass the value specified in :term:`TC_PAIRS_ADECK_INPUT_DIR`, :term:`TC_PAIRS_BDECK_INPUT_DIR` and  :term:`TC_PAIRS_EDECK_INPUT_DIR`  to the MET tc_pairs utility or have the wrapper search for valid files in that directory based on the value of :term:`TC_PAIRS_ADECK_TEMPLATE`, :term:`TC_PAIRS_BDECK_TEMPLATE` and  :term:`TC_PAIRS_EDECK_TEMPLATE` and pass them individually to tc_pairs. Set to false or no to have the wrapper find valid files. This can speed up execution time of tc_pairs.Acceptable values: yes/no

     | *Used by:*  TCPairs


   TC_PAIRS_REFORMAT_DECK
     Set to true or yes if using cyclone data that needs to be reformatted to match the ATCF (Automated Tropical Cyclone Forecasting) format. If set to true or yes, you will need to set :term:`TC_PAIRS_REFORMAT_TYPE` to specify which type of reformatting to perform.

     | *Used by:*  TCPairs

   TC_PAIRS_REFORMAT_DIR
     Specify the directory to write reformatted track data to be read by tc_pairs. Used only if :term:`TC_PAIRS_REFORMAT_DECK` is true or yes.

     | *Used by:*  TCPairs

   TC_PAIRS_REFORMAT_TYPE
     Specify which type of reformatting to perform on cyclone data. Currently only SBU extra tropical cyclone reformatting is available. Only used if :term:`TC_PAIRS_REFORMAT_DECK` is true or yes.Acceptable values: SBU

     | *Used by:*  TCPairs

   TC_PAIRS_SKIP_IF_REFORMAT_EXISTS
     Specify whether to overwrite the reformatted cyclone data or not. If set to true or yes and the reformatted file already exists for a given run, the reformatting code will not be run. Used only when :term:`TC_PAIRS_REFORMAT_DECK` is set to true or yes.Acceptable values: yes/no

     | *Used by:*  TCPairs

   TC_PAIRS_SKIP_IF_OUTPUT_EXISTS
     Specify whether to overwrite the output from the MET tc_pairs tool or not. If set to true or yes and the output file already exists for a given run, tc_pairs will not be run.Acceptable values: yes/no

     | *Used by:*  TCPairs

   TC_PAIRS_STORM_ID
     The identifier of the storm(s) of interest.

     | *Used by:*  TCPairs

   TC_PAIRS_STORM_NAME
     The name(s) of the storm of interest.

     | *Used by:*  TCPairs

   TC_STAT_AMODEL
     Specify the AMODEL for the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_BASIN
     Specify the BASIN for the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_BMODEL
     Specify the BMODEL for the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_CMD_LINE_JOB
     .. warning:: **DEPRECATED:** Please set :term:`TC_STAT_CONFIG_FILE` to run using a config file and leave it unset to run via the command line.

     Old: Specify expression(s) that will be passed to the MET tc_stat tool via the command line. Only specify if TC_STAT_RUN_VIA=CLI. Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ chapter for tc-stat for the details on performing job summaries and job filters.

     | *Used by:*  TCStat

   TC_STAT_COLUMN_STR_NAME
     Specify the string names of the columns for stratification with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_COLUMN_STR_VAL
     Specify the values for the columns set via the :term:`TC_STAT_COLUMN_STR_NAME` option for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_COLUMN_THRESH_NAME
     Specify the string names of the columns for stratification by threshold with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_COLUMN_THRESH_VAL
     Specify the values used for thresholding the columns specified in the :term:`TC_STAT_COLUMN_THRESH_NAME` option for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_INIT_THRESH_NAME
     Specify the string names of the columns for stratification by threshold with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_INIT_THRESH_VAL
     Specify the values used for thresholding the columns specified in the :term:`TC_STAT_INIT_THRESH_NAME` option for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_CYCLONE
     Specify the cyclone of interest for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_DESC
     Specify the desc option for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_INIT_BEG
     Specify the beginning initialization time for stratification when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_INIT_END
     Specify the ending initialization time for stratification when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_INIT_EXCLUDE
     Specify the initialization times to exclude when using the MET tc_stat tool, via a comma separated list e.g.:20141220_18, 20141221_00Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_INIT_HOUR
     The beginning hour (HH) of the initialization time of interest.

     | *Used by:*  TCStat

   TC_STAT_INIT_INCLUDE
     Specify the initialization times to include when using the MET tc_stat tool, via a comma separated list e.g.:20141220_00, 20141220_06, 20141220_12Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_INIT_MASK
     This corresponds to the INIT_MASK keyword in the MET tc_stat config file. For more information, please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ .

     | *Used by:*  TCStat

   TC_STAT_INIT_STR_NAME
     This corresponds to the INIT_STR_NAME keyword in the MET tc_stat config file. Please refer to  the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more details.

     | *Used by:*  TCStat

   TC_STAT_INIT_STR_VAL
     This corresponds to the INIT_STR_VAL keyword in the MET tc_stat config file. Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  TCStat

   TC_STAT_INPUT_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_LOOKIN_DIR`.

     | *Used by:*  TCStat

   TC_STAT_LOOKIN_DIR
     Specify the input directory where the MET tc_stat tool will look for files.

     | *Used by:*  TCStat

   PB2NC_INPUT_DIR
     Specify the input directory where the MET PB2NC tool will look for files.

     | *Used by:*  PB2NC

   TC_STAT_JOB_ARGS
     Specify expressions for the MET tc_stat tool to execute.

     | *Used by:*  TCStat

   TC_STAT_JOBS_LIST
     .. warning:: **DEPRECATED:** Please use :term:`TC_STAT_JOB_ARGS`.

   TC_STAT_LANDFALL
     Specify whether only those points occurring near landfall should be retained when using the MET tc_stat tool. Acceptable values: True/False

     | *Used by:*  TCStat

   TC_STAT_LANDFALL_BEG
     Specify the beginning of the landfall window for use with the MET tc_stat tool. Acceptable formats: HH, HHmmss

     | *Used by:*  TCStat

   TC_STAT_LANDFALL_END
     Specify the end of the landfall window for use with the MET tc_stat tool. Acceptable formats: HH, HHmmss

     | *Used by:*  TCStat

   TC_STAT_LEAD
     Specify the lead times to stratify by when using the MET tc_stat tool. Acceptable formats: HH, HHmmss

     | *Used by:*  TCStat

   TC_STAT_LEAD_REQ
     Specify the LEAD_REQ when using the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_MATCH_POINTS
     Specify whether only those points common to both the ADECK and BDECK tracks should be written out or not when using the MET tc_stat tool. Acceptable values: True/False

     | *Used by:*  TCStat

   TC_STAT_OUTPUT_DIR
     Specify the output directory where the MET tc_stat tool will write files.

     | *Used by:*  TCStat

   TC_STAT_RUN_VIA
     .. warning:: **DEPRECATED:** Please set :term:`TC_STAT_CONFIG_FILE` to run using a config file and leave it unset to run via the command line.

     Old: Specify the method for running the MET tc_stat tool. Acceptable values: CONFIG. If left blank (unset), tc_stat will run via the command line.

     | *Used by:*  TCStat

   TC_STAT_STORM_ID
     Set the STORM_ID(s) of interest with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_STORM_NAME
     Set the environment variable STORM_NAME for use with the MET tc_stat tool.

     | *Used by:*  TCStat

   TC_STAT_TRACK_WATCH_WARN
     Specify which watches and warnings to stratify over when using the MET tc_stat tool. Acceptable values: HUWARN, HUWATCH, TSWARN, TSWATCH, ALLIf left blank (unset), no stratification will be done.

     | *Used by:*  TCStat

   TC_STAT_VALID_BEG
     Specify a comma separated list of beginning valid times to stratify with when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_VALID_END
     Specify a comma separated list of ending valid times to stratify with when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_VALID_EXCLUDE
     Specify a comma separated list of valid times to exclude from the stratification with when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_VALID_HOUR
     This corresponds to the VALID_HOUR keyword in the MET tc_stat config file. For more information, please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_.

     | *Used by:*  TCStat

   TC_STAT_VALID_INCLUDE
     Specify a comma separated list of valid times to include in the stratification with when using the MET tc_stat tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCStat

   TC_STAT_VALID_MASK
     This corresponds to the VALID_MASK in the MET tc_stat config file. Please refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  TCStat

   TC_STAT_WATER_ONLY
     Specify whether to exclude points where the distance to land is <= 0. If set to TRUE, once land is encountered the remainder of the forecast track is not used for the verification, even if the track moves back over water.Acceptable values: true/false

     | *Used by:*  TCStat

   TIME_METHOD
     .. warning:: **DEPRECATED:** Please use :term:`LOOP_BY` instead.

   TIME_SUMMARY_BEG
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_TIME_SUMMARY_BEG` instead.

   TIME_SUMMARY_END
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_TIME_SUMMARY_END` instead.

   TIME_SUMMARY_FLAG
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_TIME_SUMMARY_FLAG` instead.

   TITLE
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_TITLE` instead.

   TCMPR_PLOTTER_TITLE
     Specify a title string for the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   TMP_DIR
     Specify the path to a temporary directory where the user has write permissions.

     | *Used by:*  PB2NC, PointStat, TCStat

   TOP_LEVEL_DIRS
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_READ_ALL_FILES`.

   TRACK_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_ADECK_INPUT_DIR`, :term:`TC_PAIRS_BDECK_INPUT_DIR` and :term:`TC_PAIRS_EDECK_INPUT_DIR`.

   TRACK_DATA_MOD_FORCE_OVERWRITE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_SKIP_IF_REFORMAT_EXISTS`.

   TRACK_DATA_SUBDIR_MOD
     .. warning:: **DEPRECATED:** No longer used.

   TRACK_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`TC_PAIRS_REFORMAT_DECK`.

   TR
     Specify the path to the Linux "tr" executable.

     | *Used by:*  PB2NC, PointStat

   TR_EXE
     .. warning:: **DEPRECATED:** Please use :term:`TR`.

   VALID_BEG
     Specify a begin time for valid times for use in the analysis. This is the starting date in the format set in the :term:`VALID_TIME_FMT`. It is named accordingly to the value set for :term:`LOOP_BY`. However, in StatAnalysis, it is named accordingly to the value set for :term:`PLOT_TIME`. See :ref:`Looping_by_Valid_Time` for more information.

     | *Used by:*  All

   VALID_END
     Specify an end time for valid times for use in the analysis. This is the ending date in the format set in the :term:`VALID_TIME_FMT`. It is named accordingly to the value set for :term:`LOOP_BY`. See :ref:`Looping_by_Valid_Time` for more information.

     | *Used by:*  All

   FCST_VALID_HOUR_LIST
     Specify a list of hours for valid times of forecast files for use in the analysis.

     | *Used by:*  MakePlots, StatAnalysis

   OBS_VALID_HOUR_LIST
     Specify a list of hours for valid times of observation files for use in the analysis.

     | *Used by:*  MakePlots, StatAnalysis

   VALID_HOUR_BEG
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VALID_HOUR_LIST` or :term:`OBS_VALID_HOUR_LIST` instead.

   VALID_HOUR_END
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VALID_HOUR_LIST` or :term:`OBS_VALID_HOUR_LIST` instead.

   VALID_HOUR_INCREMENT
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VALID_HOUR_LIST` or :term:`OBS_VALID_HOUR_LIST` instead.

   VALID_HOUR_METHOD
     .. warning:: **DEPRECATED:** No longer used.

   VALID_INCREMENT
     Specify the time increment for valid times for use in the analysis. See :ref:`Looping_by_Valid_Time` for more information. Units are assumed to be seconds unless specified with Y, m, d, H, M, or S.

     | *Used by:*  All

   VALID_TIME_FMT
     Specify a strftime formatting string for use with :term:`VALID_BEG` and :term:`VALID_END`. See :ref:`Looping_by_Valid_Time` for more information.

     | *Used by:*  All

   SERIES_ANALYSIS_VAR_LIST
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VAR<n>_NAME` and :term:`OBS_VAR<n>_NAME` instead.

   VAR_LIST
     .. warning:: **DEPRECATED:** Please use :term:`FCST_VAR<n>_NAME` and :term:`OBS_VAR<n>_NAME` instead.

   VAR<n>_FOURIER_DECOMP
     Specify if Fourier decomposition is to be considered (True) or not (False). If this is set to True, data stratification will be done for the Fourier decomposition of FCS_VAR<n>_NAME. This should have been previously run in grid_stat_wrapper. The default value is set to False.

     | *Used by:*  MakePlots, StatAnalysis

   VAR<n>_WAVE_NUM_LIST
     Specify a comma separated list of wave numbers pairings of the Fourier decomposition.

     | *Used by:*  MakePlots, StatAnalysis

   VERIFICATION_GRID
     .. warning:: **DEPRECATED:** Please use :term:`REGRID_DATA_PLANE_VERIF_GRID` instead.

   VERIF_CASE
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_VERIF_CASE` instead.

   VERIF_GRID
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_VERIF_GRID` instead.

   MAKE_PLOTS_VERIF_GRID
     Specify a string describing the grid the verification was performed on. This is the name of the grid upon which the verification was done on, ex. G002.

     | *Used by:*  MakePlots

   VERIF_TYPE
     .. warning:: **DEPRECATED:** Please use :term:`MAKE_PLOTS_VERIF_TYPE` instead.

   MAKE_PLOTS_VERIF_TYPE
     Specify a string describing the type of verification being performed. For MAKE_PLOTS_VERIF_CASE = grid2grid, valid options are anom, pres, and sfc. For MAKE_PLOTS_VERIF_CASE = grid2obs, valid options are conus_sfc and upper_air. For MAKE_PLOTS_VERIF_CASE = precip, any accumulation amount is valid, ex. A24.

     | *Used by:*  MakePlots

   VERTICAL_LOCATION
     .. warning:: **DEPRECATED:** Specify the vertical location desired when using the MET pb2nc tool.

   XLAB
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_XLAB` instead.

   TCMPR_PLOTTER_XLAB
     Specify the x-axis label when using the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   XLIM
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_XLIM` instead.

   TCMPR_PLOTTER_XLIM
     Specify the x-axis limit when using the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   YLAB
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_YLAB` instead.

   TCMPR_PLOTTER_YLAB
     Specify the y-axis label when using the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   YLIM
     .. warning:: **DEPRECATED:** Please use :term:`TCMPR_PLOTTER_YLIM` instead.

   TCMPR_PLOTTER_YLIM
     Specify the y-axis limit when using the TC Matched Pairs plotting tool.

     | *Used by:*  TCMPRPlotter

   FCST_PCP_COMBINE_INPUT_ACCUMS
     Specify what accumulation levels should be used from the forecast data for the analysis. This is a list of input accumulations in the order of preference to use to build the desired accumulation. If an accumulation cannot be used (i.e. it is larger than the remaining accumulation that needs to be built) then the next value in the list is tried. Units are assumed to be hours unless a time identifier such as Y, m, d, H, M, S is specifed at the end of the value, i.e. 30M or 1m.

     If the name and/or level of the accumulation value must be specified for the data, then a list of equal length to this variable must be set for :term:`FCST_PCP_COMBINE_INPUT_NAMES` and :term:`FCST_PCP_COMBINE_INPUT_LEVELS`. See this sections for more information.

     This variable can be set to {lead} if the accumulation found in a given file corresponds to the forecast lead of the data. If this is the case, :term:`FCST_PCP_COMBINE_BUCKET_INTERVAL` can be used to reset the accumulation at a given interval.

     A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_ACCUMS`.

     Examples:

     1H, 30M

     This will attempt to use a 1 hour accumulation, then try to use a 30 minute accumulation if the first value did not succeed.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_ACCUMS
     See :term:`FCST_PCP_COMBINE_INPUT_ACCUMS`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_BUCKET_INTERVAL
     Used when :term:`FCST_PCP_COMBINE_INPUT_ACCUMS` contains {lead} in the list. This is the interval to reset the bucket accumulation. For example, if the accumulation is reset every 3 hours (forecast 1 hour has 1 hour accum, forecast 2 hour has 2 hour accum, forecast 3 hour has 3 hour accum, forecast 4 hour has 1 hour accum, etc.) then this should be set to 3 or 3H. Units are assumed to be hours unless specified with Y, m, d, H, M, or S.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_BUCKET_INTERVAL
     See :term:`FCST_PCP_COMBINE_BUCKET_INTERVAL`.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_NAMES
     Specify which field names correspond to each accumulation specifed in FCST_PCP_COMBINE_INPUT_ACCUMS for the forecast data for the analysis. See :term:`FCST_PCP_COMBINE_INPUT_ACCUMS` for more information. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_NAMES`. Examples:

     | FCST_PCP_COMBINE_INPUT_ACCUMS = 6, 1
     | FCST_PCP_COMBINE_INPUT_NAMES = P06M_NONE, P01M_NONE

     This says that the 6 hour accumulation field name is P06M_NONE and the 1 hour accumulation field name is P01M_NONE.

     To utilize Python Embedding as input to the MET tools, set this value to the python script command with arguments. This value can include filename template syntax such as {valid?fmt=%Y%m%d%H}.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_NAMES
     See :term:`FCST_PCP_COMBINE_INPUT_NAMES`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_LEVELS
     Specify which levels correspond to each accumulation specifed in FCST_PCP_COMBINE_INPUT_ACCUMS for the forecast data for the analysis. See :term:`FCST_PCP_COMBINE_INPUT_ACCUMS` for more information. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_LEVELS`. Examples:

     | FCST_PCP_COMBINE_INPUT_ACCUMS = 1
     | FCST_PCP_COMBINE_INPUT_NAMES = P01M_NONE
     | FCST_PCP_COMBINE_INPUT_LEVELS = "(0,*,*)"

     This says that the 1 hour accumulation field name is P01M_NONE and the level (0,*,*), which is NetCDF format to specify the first item of the first dimension.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_LEVELS
     See :term:`FCST_PCP_COMBINE_INPUT_LEVELS`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_INPUT_OPTIONS
     Specify optional additional options that correspond to each accumulation specifed in FCST_PCP_COMBINE_INPUT_ACCUMS for the forecast data for the analysis. See :term:`FCST_PCP_COMBINE_INPUT_ACCUMS` for more information. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_INPUT_OPTIONS`. Examples:

     | FCST_PCP_COMBINE_INPUT_ACCUMS = 6, 1
     | FCST_PCP_COMBINE_INPUT_NAMES = P06M_NONE, P01M_NONE
     | FCST_PCP_COMBINE_INPUT_OPTIONS = something = else;, another_thing = else;

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_INPUT_OPTIONS
     See :term:`FCST_PCP_COMBINE_INPUT_OPTIONS`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_OUTPUT_ACCUM
     Specify desired accumulation to be built from the forecast data. Units are assumed to be hours unless a time identifier such as Y, m, d, H, M, S is specifed at the end of the value, i.e. 30M or 1m. If this variable is not set, then FCST_VAR<n>_LEVELS is used.

     A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_OUTPUT_ACCUM`.

     Examples:

     15H

     This will attempt to build a 15 hour accumulation.

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_OUTPUT_NAME
     Specify the output field name from processing forecast data. If this variable is not set, then :term:`FCST_VAR<n>_NAME` is used.

     A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_OUTPUT_NAME`.

     Example: APCP

   OBS_PCP_COMBINE_OUTPUT_ACCUM
     See :term:`FCST_PCP_COMBINE_OUTPUT_NAME`.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_OUTPUT_NAME
     See :term:`FCST_PCP_COMBINE_OUTPUT_NAME`.

     | *Used by:*  PCPCombine

   PREPBUFR_DATA_DIR
     .. warning:: **DEPRECATED:** Please use :term:`PB2NC_INPUT_DIR` instead.

   GEN_VX_MASK_INPUT_DIR
     Directory containing input data to GenVxMask. This variable is optional because you can specify a
     full path to the input files using :term:`GEN_VX_MASK_INPUT_TEMPLATE`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_INPUT_TEMPLATE
     Filename template of the input grid used by GenVxMask. This can be an input filename or a grid definition.
     See also :term:`GEN_VX_MASK_INPUT_DIR`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_INPUT_MASK_DIR
     Directory containing mask data used by GenVxMask. This variable is optional because you can specify the
     full path to the input files using :term:`GEN_VX_MASK_INPUT_MASK_TEMPLATE`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_INPUT_MASK_TEMPLATE
     Filename template of the mask files used by GenVxMask. This can be a list of files or grids separated
     by commas to apply to the input grid. The wrapper will call GenVxMask once for each item in the list, passing
     its output to temporary files until the final command, which will write to the file specified by
     :term:`GEN_VX_MASK_OUTPUT_TEMPLATE` (and optionally :term:`GEN_VX_MASK_OUTPUT_DIR`. The length of this
     list must be the same length as :term:`GEN_VX_MASK_OPTIONS`. When "-type lat" or "-type lon" is set in
     :term:`GEN_VX_MASK_OPTIONS`, the corresponding mask template is ignored, but must be set to a placeholder
     string. See also :term:`GEN_VX_MASK_INPUT_MASK_DIR`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_OPTIONS
     Command line arguments to pass to each call of GenVxMask. This can be a list of sets of arguments
     separated by commas to apply to the input grid. The length of this list must be the same length as
     :term:`GEN_VX_MASK_INPUT_MASK_TEMPLATE`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_OUTPUT_DIR
     Directory to write output data generated by GenVxMask. This variable is optional because you can
     specify the full path to the input files using :term:`GEN_VX_MASK_OUTPUT_TEMPLATE`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_OUTPUT_TEMPLATE
     Filename template of the output file generated by GenVxMask. See also :term:`GEN_VX_MASK_OUTPUT_DIR`.

     | *Used by:* GenVxMask

   LOG_GEN_VX_MASK_VERBOSITY
     Overrides the log verbosity for GenVxMask only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_SKIP_IF_OUTPUT_EXISTS
     If True, do not run GenVxMask if output file already exists. Set to False to overwrite files.

     | *Used by:*  GenVxMask

   GEN_VX_MASK_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* GenVxMask

   GEN_VX_MASK_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if a GenVxMask input file should be used for processing. Overrides :term:`FILE_WINDOW_BEGIN`. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* GenVxMask

   GEN_VX_MASK_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if an GenVxMask input file should be used for processing. Overrides :term:`FILE_WINDOW_BEGIN`. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* GenVxMask

   TC_RMW_BASIN
     Specify the value for 'basin' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_CYCLONE
     Specify the value for 'cyclone' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_STORM_ID
     Specify the value for 'storm_id' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_STORM_NAME
     Specify the value for 'storm_name' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_SCALE
     Specify the value for 'rmw_scale' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_N_AZIMUTH
     Specify the value for 'n_azimuth' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_N_RANGE
     Specify the value for 'n_range' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_MAX_RANGE_KM
     Specify the value for 'max_range_km' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_DELTA_RANGE_KM
     Specify the value for 'delta_range_km' in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_INPUT_DATATYPE
     Specify the data type of the input directory for input files used with the MET TCRMW tool. Used to set the 'file_type' value of the data dictionary in the MET configuration file for TCRMW.

     | *Used by:*  TCRMW

   TC_RMW_INPUT_DIR
     Directory containing input data to TCRMW. This variable is optional because you can specify the full path to the input files using :term:`TC_RMW_INPUT_TEMPLATE`.

     | *Used by:* TCRMW

   TC_RMW_INPUT_TEMPLATE
     Filename template of the input data used by TCRMW. See also :term:`TC_RMW_INPUT_DIR`.

     | *Used by:* TCRMW

   TC_RMW_DECK_INPUT_DIR
     Directory containing ADECK input data to TCRMW. This variable is optional because you can specify the full path to the input files using :term:`TC_RMW_DECK_TEMPLATE`.

     | *Used by:* TCRMW

   TC_RMW_DECK_TEMPLATE
     Filename template of the ADECK input data used by TCRMW. See also :term:`TC_RMW_DECK_INPUT_DIR`.

     | *Used by:* TCRMW

   TC_RMW_OUTPUT_DIR
     Directory to write output data from TCRMW. This variable is optional because you can specify the full path to the output file using :term:`TC_RMW_OUTPUT_TEMPLATE`.

     | *Used by:* TCRMW

   TC_RMW_OUTPUT_TEMPLATE
     Filename template of write the output data generated by TCRMW. See also :term:`TC_RMW_OUTPUT_DIR`.

     | *Used by:* TCRMW

   TC_RMW_INIT_INCLUDE
     Value to set for init_include in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.

     | *Used by:*  TCRMW

   TC_RMW_VALID_BEG
     Value to set for valid_beg in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.

     | *Used by:*  TCRMW

   TC_RMW_VALID_END
     Value to set for valid_end in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.

     | *Used by:*  TCRMW

   TC_RMW_VALID_INCLUDE_LIST
     List of values to set for valid_inc in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.


     | *Used by:*  TCRMW

   TC_RMW_VALID_EXCLUDE_LIST
     List of values to set for valid_exc in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.

     | *Used by:*  TCRMW

   TC_RMW_VALID_HOUR_LIST
     List of values to set for valid_hour in the MET configuration file. See the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ section regarding Regrid-Data-Plane for more information.

     | *Used by:*  TCRMW

   GRID_DIAG_DESC
     Specify the value for 'desc' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   GRID_STAT_DESC
     Specify the value for 'desc' in the MET configuration file for grid_stat.

     | *Used by:*  GridStat

   ENSEMBLE_STAT_DESC
     Specify the value for 'desc' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   MODE_DESC
     Specify the value for 'desc' in the MET configuration file for MODE.

     | *Used by:* MODE

   MTD_DESC
     Specify the value for 'desc' in the MET configuration file for MTD.

     | *Used by:* MTD

   POINT_STAT_DESC
     Specify the value for 'desc' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   TC_GEN_DESC
     Specify the value for 'desc' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   TC_PAIRS_DESC
     Specify the value for 'desc' in the MET configuration file for TCPairs.

     | *Used by:* TCPairs

   TC_RMW_DESC
     Specify the value for 'desc' in the MET configuration file for TCRMW.

     | *Used by:* TCRMW

   GRID_DIAG_INPUT_DIR
     Input directory for files to use with the MET tool grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_INPUT_TEMPLATE
     Template used to specify input filenames for the MET tool grid_diag. This can be a comma-separated list. If there are more than one template, the number of fields specified must match the number of templates.

     | *Used by:*  GridDiag

   GRID_DIAG_OUTPUT_DIR
     Output directory for write files with the MET tool grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_OUTPUT_TEMPLATE
     Template used to specify output filenames created by MET tool grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_VERIFICATION_MASK_TEMPLATE
     Template used to specify the verification mask filename for the MET tool grid_diag. Supports a list of filenames.

     | *Used by:*  GridDiag

   LOG_GRID_DIAG_VERBOSITY
     Overrides the log verbosity for GridDiag only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* GridDiag

   GRID_DIAG_CONFIG_FILE
     Specify the absolute path to the configuration file used by the MET grid_stat tool.

     | *Used by:*  GridStat

   GRID_DIAG_CUSTOM_LOOP_LIST
    Sets custom string loop list for a specific wrapper. See :term:`CUSTOM_LOOP_LIST`.

     | *Used by:* GridDiag

   GRID_DIAG_INPUT_DATATYPE
     Specify the data type of the input directory for files used with the MET grid_diag tool.

     | *Used by:*  GridDiag

   GRID_DIAG_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   GRID_DIAG_REGRID_TO_GRID
     Specify the value for 'regrid.to_grid' in the MET configuration file for grid_diag.

     | *Used by:*  GridDiag

   SKIP_TIMES
     List of valid times to skip processing. Each value be surrounded by quotation marks and must contain a datetime format followed by a list of matching times to skip. Multiple items can be defined separated by commas. begin_end_incr syntax can be used to define a list as well.

     Examples:

     Value:
     SKIP_TIMES = "%m:11,12"

     Result:
     Skip the 11th and 12th month

     Value:
     SKIP_TIMES = "%m:11", "%d:31"

     Result:
     Skip if 11th month or 31st day.

     Value:
     SKIP_TIMES = "%Y%m%d:20201031"

     Result:
     Skip October 31, 2020

     Value:
     SKIP_TIMES = "%H:begin_end_incr(0,22, 2)"

     Result:
     Skip even hours: 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22

     | *Used by:*  GridStat, SeriesAnalysis

   TC_GEN_TRACK_INPUT_DIR
     Directory containing the track data used by TCGen. This variable is optional because you can specify the full path to track data using :term:`TC_GEN_TRACK_INPUT_TEMPLATE`.

     | *Used by:* TCGen

   TC_GEN_GENESIS_INPUT_DIR
     Directory containing the genesis data used by TCGen. This variable is optional because you can specify the full path to genesis data using :term:`TC_GEN_GENESIS_INPUT_TEMPLATE`.

     | *Used by:* TCGen

   TC_GEN_TRACK_INPUT_TEMPLATE
     Filename template of the track data used by TCGen. See also :term:`TC_GEN_TRACK_INPUT_DIR`.

     | *Used by:* TCGen

   TC_GEN_GENESIS_INPUT_TEMPLATE
     Filename template of the genesis data used by TCGen. See also :term:`TC_GEN_GENESIS_INPUT_DIR`.

     | *Used by:* TCGen

   TC_GEN_OUTPUT_DIR
     Specify the output directory where files from the MET TCGen tool are written.

     | *Used by:*  TCGen

   TC_GEN_OUTPUT_TEMPLATE
     Sets the subdirectories below :term:`TC_GEN_OUTPUT_DIR` using a template to allow run time information.

     | *Used by:*  TCGen

   LOG_TC_GEN_VERBOSITY
     Overrides the log verbosity for TCGen only. If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`.

     | *Used by:* TCGen

   TC_GEN_CONFIG_FILE
     Provide the absolute path to the configuration file for the MET TCGen tool.

     | *Used by:*  TCGen

   TC_GEN_INIT_FREQ
     Specify the value of 'init_freq' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_VALID_FREQ
     Specify the value of 'valid_freq' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_LEAD_WINDOW_BEGIN
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_FCST_HR_WINDOW_BEGIN`.

   TC_GEN_LEAD_WINDOW_END
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_FCST_HR_WINDOW_END`.

   TC_GEN_FCST_HR_WINDOW_BEGIN
     Specify the value of fcst_hr_window.begin in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_FCST_HR_WINDOW_END
     Specify the value of fcst_hr_window.end in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_MIN_DURATION
     Specify the value of 'min_duration' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_FCST_GENESIS_VMAX_THRESH
     Specify the value of fcst_genesis.vmax_thresh in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_FCST_GENESIS_MSLP_THRESH
     Specify the value of fcst_genesis.mslp_thresh in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BEST_GENESIS_TECHNIQUE
     Specify the value of best_genesis.technique in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BEST_GENESIS_CATEGORY
     Specify the value of best_genesis.category in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BEST_GENESIS_VMAX_THRESH
     Specify the value of best_genesis.vmax_thresh in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BEST_GENESIS_MSLP_THRESH
     Specify the value of best_genesis.mslp_thresh in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OPER_TECHNIQUE
     Specify the value of 'oper_technique' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OPER_GENESIS_TECHNIQUE
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_OPER_TECHNIQUE`.

   TC_GEN_OPER_GENESIS_CATEGORY
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_OPER_TECHNIQUE`.

   TC_GEN_OPER_GENESIS_VMAX_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_OPER_TECHNIQUE`.

   TC_GEN_OPER_GENESIS_MSLP_THRESH
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_OPER_TECHNIQUE`.

   TC_GEN_FILTER_<n>
     Specify the values of 'filter' in the MET configuration file where <n> is any integer.
     Any quotation marks that are found inside another set of quotation marks must be preceded with a backslash

     | *Used by:*  TCGen

   TC_GEN_STORM_ID
     The identifier of the storm(s) of interest.

     | *Used by:*  TCGen

   TC_GEN_STORM_NAME
     The name(s) of the storm of interest.

     | *Used by:*  TCGen

   TC_GEN_INIT_BEG
     Specify the beginning initialization time for stratification when using the MET TCGen tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCGen

   TC_GEN_INIT_END
     Specify the ending initialization time for stratification when using the MET TCGen tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCGen

   TC_GEN_INIT_INC
     Specify the value of 'init_inc' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_INIT_EXC
     Specify the value of 'init_exc' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_VALID_BEG
     Specify the beginning valid time for stratification when using the MET TCGen tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCGen

   TC_GEN_VALID_END
     Specify the ending valid time for stratification when using the MET TCGen tool. Acceptable formats: YYYYMMDD_HH, YYYYMMDD_HHmmss

     | *Used by:*  TCGen

   TC_GEN_INIT_HOUR
     Specify a list of hours for initialization times for use in the analysis.

     | *Used by:*  TCGen

   TC_GEN_VX_MASK
     Specify the 'vx_mask' value to set in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BASIN_MASK
     Specify the 'basin_mask' value to set in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_DLAND_THRESH
     Specify the value of 'dland_thresh' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_GENESIS_WINDOW_BEGIN
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_DEV_HIT_WINDOW_BEGIN`.

   TC_GEN_GENESIS_WINDOW_END
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_DEV_HIT_WINDOW_END`.

   TC_GEN_DEV_HIT_WINDOW_BEGIN
     Specify the value for dev_hit_window.begin in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_DEV_HIT_WINDOW_END
     Specify the value of dev_hit_window.end in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_DEV_HIT_RADIUS
     Specify the value of 'dev_hit_radius' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_DISCARD_INIT_POST_GENESIS_FLAG
     Specify the value of 'discard_init_post_genesis_flag' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_DEV_METHOD_FLAG
     Specify the value of 'dev_method_flag' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OPS_METHOD_FLAG
     Specify the value of 'ops_method_flag' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_CI_ALPHA
     Specify the value of 'ci_alpha' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OUTPUT_FLAG_FHO
     Specify the value of output_flag.fho in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OUTPUT_FLAG_CTC
     Specify the value of output_flag.ctc in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OUTPUT_FLAG_CTS
     Specify the value of output_flag.cts in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_OUTPUT_FLAG_GENMPR
     Specify the value of output_flag.genmpr in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_LATLON
     Specify the value of nc_pairs_flag.latlon in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_FCST_GENESIS
     Specify the value of nc_pairs_flag.fcst_genesis in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_FCST_TRACKS
     Specify the value of nc_pairs_flag.fcst_tracks in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_FCST_FY_OY
     Specify the value of nc_pairs_flag.fcst_fy_oy in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_FCST_FY_ON
     Specify the value of nc_pairs_flag.fcst_fy_on in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_BEST_GENESIS
     Specify the value of nc_pairs_flag.best_genesis in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_BEST_TRACKS
     Specify the value of nc_pairs_flag.best_tracks in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_BEST_FY_OY
     Specify the value of nc_pairs_flag.best_fy_oy in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_FLAG_BEST_FN_OY
     Specify the value of nc_pairs_flag.best_fn_oy in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_VALID_MINUS_GENESIS_DIFF_THRESH
     Specify the value of 'valid_minus_genesis_diff_thresh' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BEST_UNIQUE_FLAG
     Specify the value of 'best_unique_flag' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_BASIN_FILE
     Specify the value of 'basin_file' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_NC_PAIRS_GRID
     Specify the value of 'nc_pairs_grid' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_GENESIS_MATCH_RADIUS
     Specify the value of 'genesis_match_radius' in the MET configuration file.

     | *Used by:*  TCGen

   TC_GEN_GENESIS_RADIUS
     .. warning:: **DEPRECATED:** Please use :term:`TC_GEN_GENESIS_MATCH_RADIUS` and :term:`TC_GEN_DEV_HIT_RADIUS`.

   TC_GEN_DLAND_FILE
     Specify the value of 'dland_file' in the MET configuration file.

     | *Used by:*  TCGen

   PLOT_DATA_PLANE_INPUT_DIR
     Directory containing input data to PlotDataPlane. This variable is
     optional because you can specify the full path to the input files
     using :term:`PLOT_DATA_PLANE_INPUT_TEMPLATE`.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_INPUT_TEMPLATE
     Filename template of the input file used by PlotDataPlane.
     Set to PYTHON_NUMPY/XARRAY to read from a Python embedding script.
     See also :term:`PLOT_DATA_PLANE_INPUT_DIR`.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_OUTPUT_DIR
     Directory to write output data from PlotDataPlane. This variable is
     optional because you can specify the full path to the input files
     using :term:`PLOT_DATA_PLANE_OUTPUT_TEMPLATE`.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_OUTPUT_TEMPLATE
     Filename template of the output file created by PlotDataPlane.
     See also :term:`PLOT_DATA_PLANE_OUTPUT_DIR`.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_FIELD_NAME
     Name of field to read from input file. For Python embedding input, set to
     the path of a Python script and any arguments to the script.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_FIELD_LEVEL
     Level of field to read from input file. For Python embedding input, do not
     set this value.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_FIELD_EXTRA
     Additional options for input field. Multiple options can be specified.
     Each option must end with a semi-colon including the last (or only) item.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_CONVERT_TO_IMAGE
     If set to True, run convert to create a png image with the same name as
     the output from plot_data_plane (except the extension is png instead of
     ps). If set to True, the application convert must either be in the user's
     path or [exe] CONVERT must be set to the full path to the executable.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_TITLE
     (Optional) title to display on the output postscript file.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_COLOR_TABLE
     (Optional) path to color table file to override the default.

     | *Used by:* PlotDataPlane

   PLOT_DATA_PLANE_RANGE_MIN_MAX
     (Optional) minimum and maximum values to output to postscript file.

     | *Used by:* PlotDataPlane

   LOG_PLOT_DATA_PLANE_VERBOSITY
     Overrides the log verbosity for PlotDataPlane only.
     If not set, the verbosity level is controlled by :term:`LOG_MET_VERBOSITY`

     | *Used by:* PlotDataPlane

   ENSEMBLE_STAT_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  EnsembleStat

   GRID_DIAG_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  GridDiag

   GRID_STAT_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  GridStat

   MODE_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  MODE

   MTD_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  MTD

   PLOT_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  PlotDataPlane

   POINT2GRID_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  Point2Grid

   POINT_STAT_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  PointStat

   PY_EMBED_INGEST_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  PyEmbedIngest

   SERIES_ANALYSIS_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  SeriesAnalysis

   STAT_ANALYSIS_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  StatAnalysis

   TC_GEN_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  TCGen

   TC_RMW_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  TCRMW

   TC_STAT_SKIP_IF_OUTPUT_EXISTS
     If True, do not run app if output file already exists. Set to False to overwrite files.

     | *Used by:*  TCStat

   USER_SCRIPT_RUNTIME_FREQ
     Frequency to run the user-defined script. See :ref:`Runtime_Freq` for more information.

     | *Used by:*  UserScript

   USER_SCRIPT_COMMAND
     User-defined command to run. Filename template tags can be used to modify
     the command for each execution. See :term:`USER_SCRIPT_RUNTIME_FREQ` for
     more information.

     | *Used by:*  UserScript

   USER_SCRIPT_CUSTOM_LOOP_LIST
     List of strings to loop over for each runtime to run the command.

     | *Used by:*  UserScript

   USER_SCRIPT_SKIP_TIMES
     Run times to skip for this wrapper only. See :term:`SKIP_TIMES` for more
     information and how to format.

     | *Used by:*  UserScript

   GRID_DIAG_RUNTIME_FREQ
     Frequency to run Grid-Diag. See :ref:`Runtime_Freq` for more information.

     | *Used by:*  GridDiag

   SERIES_ANALYSIS_RUNTIME_FREQ
     Frequency to run SeriesAnalysis. See :ref:`Runtime_Freq` for more information.

     | *Used by:*  SeriesAnalysis


   SERIES_ANALYSIS_RUN_ONCE_PER_STORM_ID
     If True, run SeriesAnalysis once for each storm ID found in the .tcst (TCStat output) file specified with :term:`SERIES_ANALYSIS_TC_STAT_INPUT_DIR` and :term:`SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE`.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_DESC
     Specify the value for 'desc' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_CAT_THRESH
     Specify the value for 'cat_thresh' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_VLD_THRESH
     Specify the value for 'vld_thresh' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   SERIES_ANALYSIS_BLOCK_SIZE
     Specify the value for 'block_size' in the MET configuration file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   ENSEMBLE_STAT_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   GRID_STAT_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for GridStat.

     | *Used by:*  GridStat

   GRID_STAT_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for GridStat.

     | *Used by:*  GridStat

   GRID_STAT_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for GridStat.

     | *Used by:*  GridStat

   GRID_STAT_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for GridStat.

     | *Used by:*  GridStat

   MODE_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for MODE.

     | *Used by:*  MODE

   MODE_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for MODE.

     | *Used by:*  MODE

   MODE_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for MODE.

     | *Used by:*  MODE

   MODE_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for MODE.

     | *Used by:*  MODE

   MTD_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for MTD.

     | *Used by:*  MTD

   MTD_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for MTD.

     | *Used by:*  MTD

   MTD_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for MTD.

     | *Used by:*  MTD

   MTD_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for MTD.

     | *Used by:*  MTD

   POINT_STAT_REGRID_METHOD
     Specify the value for 'regrid.method' in the MET configuration file for PointStat.

     | *Used by:*  PointStat

   POINT_STAT_REGRID_WIDTH
     Specify the value for 'regrid.width' in the MET configuration file for PointStat.

     | *Used by:*  PointStat

   POINT_STAT_REGRID_VLD_THRESH
     Specify the value for 'regrid.vld_thresh' in the MET configuration file for PointStat.

     | *Used by:*  PointStat

   POINT_STAT_REGRID_SHAPE
     Specify the value for 'regrid.shape' in the MET configuration file for PointStat.

     | *Used by:*  PointStat

   ENSEMBLE_STAT_ENS_SSVAR_BIN_SIZE
     Specify the value for 'ens_ssvar_bin_size' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENS_PHIST_BIN_SIZE
     Specify the value for 'ens_phist_bin_size' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NBRHD_PROB_WIDTH
     Specify the value for 'nbrhd_prob.width' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NBRHD_PROB_SHAPE
     Specify the value for 'nbrhd_prob.shape' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NBRHD_PROB_VLD_THRESH
     Specify the value for 'nbrhd_prob.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CLIMO_CDF_CDF_BINS
     See :term:`ENSEMBLE_STAT_CLIMO_CDF_BINS`

   ENSEMBLE_STAT_CLIMO_CDF_BINS
     Specify the value for 'climo_cdf.cdf_bins' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CLIMO_CDF_CENTER_BINS
     Specify the value for 'climo_cdf.center_bins' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CLIMO_CDF_WRITE_BINS
     Specify the value for 'climo_cdf.write_bins' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_DUPLICATE_FLAG
     Specify the value for 'duplicate_flag' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_SKIP_CONST
     Specify the value for 'skip_const' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_DX
     Specify the value for 'nmep_smooth.gaussian_dx' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_RADIUS
     Specify the value for 'nmep_smooth.gaussian_radius' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_VLD_THRESH
     Specify the value for 'nmep_smooth.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_SHAPE
     Specify the value for 'nmep_smooth.shape' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_METHOD
     Specify the value for 'nmep_smooth.type.method' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_NMEP_SMOOTH_WIDTH
     Specify the value for 'nmep_smooth.type.width' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CENSOR_THRESH
     Specify the value for 'censor_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CENSOR_VAL
     Specify the value for 'censor_val' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OBS_ERROR_FLAG
     Specify the value for 'obs_error.flag' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_FILE_NAME
     Specify the value for 'climo_mean.file_name' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_FIELD
     Specify the value for 'climo_mean.field' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_REGRID_METHOD
     Specify the value for 'climo_mean.regrid.method' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_REGRID_WIDTH
     Specify the value for 'climo_mean.regrid.width' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_REGRID_VLD_THRESH
     Specify the value for 'climo_mean.regrid.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_REGRID_SHAPE
     Specify the value for 'climo_mean.regrid.shape' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_TIME_INTERP_METHOD
     Specify the value for 'climo_mean.time_interp_method' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_MATCH_MONTH
     Specify the value for 'climo_mean.match_month' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_DAY_INTERVAL
     Specify the value for 'climo_mean.day_interval' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_MEAN_HOUR_INTERVAL
     Specify the value for 'climo_mean.hour_interval' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_FILE_NAME
     Specify the value for 'climo_stdev.file_name' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_FIELD
     Specify the value for 'climo_stdev.field' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_REGRID_METHOD
     Specify the value for 'climo_stdev.regrid.method' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_REGRID_WIDTH
     Specify the value for 'climo_stdev.regrid.width' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_REGRID_VLD_THRESH
     Specify the value for 'climo_stdev.regrid.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_REGRID_SHAPE
     Specify the value for 'climo_stdev.regrid.shape' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_TIME_INTERP_METHOD
     Specify the value for 'climo_stdev.time_interp_method' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_MATCH_MONTH
     Specify the value for 'climo_stdev.match_month' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_DAY_INTERVAL
     Specify the value for 'climo_stdev.day_interval' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_CLIMO_STDEV_HOUR_INTERVAL
     Specify the value for 'climo_stdev.hour_interval' in the MET configuration file for EnsembleStat.

     | *Used by:* EnsembleStat

   ENSEMBLE_STAT_MASK_GRID
     Specify the value for 'mask.grid' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_CI_ALPHA
     Specify the value for 'ci_alpha' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat


   ENSEMBLE_STAT_INTERP_FIELD
     Specify the value for 'interp.field' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_INTERP_VLD_THRESH
     Specify the value for 'interp.vld_thresh' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_INTERP_SHAPE
     Specify the value for 'interp.shape' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_INTERP_METHOD
     Specify the value for 'interp.type.method' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_INTERP_WIDTH
     Specify the value for 'interp.type.width' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_ECNT
     Specify the value for 'output_flag.ecnt' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_RPS
     Specify the value for 'output_flag.rps' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_RHIST
     Specify the value for 'output_flag.rhist' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_PHIST
     Specify the value for 'output_flag.phist' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_ORANK
     Specify the value for 'output_flag.orank' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_SSVAR
     Specify the value for 'output_flag.ssvar' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_OUTPUT_FLAG_RELP
     Specify the value for 'output_flag.relp' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON
     Specify the value for 'ensemble_flag.latlon' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN
     Specify the value for 'ensemble_flag.mean' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV
     Specify the value for 'ensemble_flag.stdev' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS
     Specify the value for 'ensemble_flag.minus' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS
     Specify the value for 'ensemble_flag.plus' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN
     Specify the value for 'ensemble_flag.min' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX
     Specify the value for 'ensemble_flag.max' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE
     Specify the value for 'ensemble_flag.range' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT
     Specify the value for 'ensemble_flag.vld_count' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY
     Specify the value for 'ensemble_flag.frequency' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP
     Specify the value for 'ensemble_flag.nep' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP
     Specify the value for 'ensemble_flag.nmep' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_RANK
     Specify the value for 'ensemble_flag.rank' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_ENSEMBLE_FLAG_WEIGHT
     Specify the value for 'ensemble_flag.weight' in the MET configuration file for EnsembleStat.

     | *Used by:*  EnsembleStat

   GRID_STAT_MASK_GRID
     Specify the value for 'mask.grid' in the MET configuration file for GridStat.

     | *Used by:*  GridStat

   GRID_STAT_MASK_POLY
     Specify the value for 'mask.poly' in the MET configuration file for GridStat.

     | *Used by:*  GridStat
   
   DESC
     Specify the value for 'desc' in the MET configuration file for the MET tool being used

    | *Used by:* GridStat, PointStat, EnsembleStat, GridDiag, MODE, MTD, SeriesAnalysis, TCGen, TCPairs, TCStat

   ENSEMBLE_STAT_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     ENSEMBLE_STAT_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:*  EnsembleStat

   ASCII2NC_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     ASCII2NC_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* ASCII2NC

   GRID_DIAG_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     GRID_DIAG_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* GridDiag

   GRID_STAT_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     GRID_STAT_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";
  
     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* GridStat

   MODE_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     MODE_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* MODE

   MTD_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     MTD_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* MTD

   PB2NC_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     PB2NC_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* PB2NC

   POINT_STAT_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     POINT_STAT_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* PointStat

   SERIES_ANALYSIS_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     SERIES_ANALYSIS_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* SeriesAnalysis

   STAT_ANALYSIS_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     STAT_ANALYSIS_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* StatAnalysis

   TC_GEN_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     TC_GEN_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* TCGen

   TC_PAIRS_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     TC_PAIRS_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* TCPairs

   TC_RMW_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     TC_RMW_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* TCRMW

   TC_STAT_MET_CONFIG_OVERRIDES
     Override any variables in the MET configuration file that are not
     supported by the wrapper. This should be set to the full variable name
     and value that you want to override, including the equal sign and the
     ending semi-colon. The value is directly appended to the end of the
     wrapped MET config file.
     
     Example:
     TC_STAT_MET_CONFIG_OVERRIDES = desc = "override_desc"; model = "override_model";

     See :ref:`Overriding Unsupported MET config file settings<met-config-overrides>` for more information

     | *Used by:* TCStat

   FCST_PCP_COMBINE_EXTRA_NAMES
     Specify a list of any additional fields to add to the command. The items in this list correspond to the list set by :term:`FCST_PCP_COMBINE_EXTRA_LEVELS`. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_EXTRA_NAMES`. Example:

     | FCST_PCP_COMBINE_EXTRA_NAMES = TMP, HGT
     | FCST_PCP_COMBINE_EXTRA_LEVELS = "(*,*)", "(*,*)"

     This will add the following to the end of the command:

     -field 'name="TMP"; level="(*,*)";' -field 'name="HGT"; level="(*,*)";'

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_EXTRA_NAMES
     See :term:`FCST_PCP_COMBINE_EXTRA_NAMES`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_EXTRA_LEVELS
     Specify a list of any additional fields to add to the command. The items in this list correspond to the list set by :term:`FCST_PCP_COMBINE_EXTRA_NAMES`. If this list has fewer items than the names list, then no level value will be specified for those names (i.e. if using Python Embedding). A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_EXTRA_LEVELS`. See :term:`FCST_PCP_COMBINE_EXTRA_NAMES` for an example.

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_EXTRA_LEVELS
     See :term:`FCST_PCP_COMBINE_EXTRA_LEVELS`

     | *Used by:*  PCPCombine

   FCST_PCP_COMBINE_EXTRA_OUTPUT_NAMES
     Specify a list of output names for any additional fields to add to the command. The items in this list correspond to the list set by :term:`FCST_PCP_COMBINE_EXTRA_NAMES`. A corresponding variable exists for observation data called :term:`OBS_PCP_COMBINE_EXTRA_OUTPUT_NAMES`. Example:

     | *Used by:*  PCPCombine

   OBS_PCP_COMBINE_EXTRA_OUTPUT_NAMES
     See :term:`FCST_PCP_COMBINE_EXTRA_OUTPUT_NAMES`

     | *Used by:*  PCPCombine

   ENSEMBLE_STAT_MESSAGE_TYPE
     Set the message_type option in the EnsembleStat MET config file.

     | *Used by:*  EnsembleStat

   ENSEMBLE_STAT_MASK_POLY
     Set the mask.poly entry in the EnsembleStat MET config file.

     | *Used by:*  EnsembleStat

   GRID_DIAG_MASK_POLY
     Set the mask.poly entry in the GridDiag MET config file.

     | *Used by:*  GridDiag

   GRID_DIAG_MASK_GRID
     Set the mask.grid entry in the GridDiag MET config file.

     | *Used by:*  GridDiag

   GRID_DIAG_CENSOR_THRESH
     Set the censor_thresh entry in the GridDiag MET config file.

     | *Used by:*  GridDiag

   GRID_DIAG_CENSOR_VAL
     Set the censor_val entry in the GridDiag MET config file.

     | *Used by:*  GridDiag

   PB2NC_TIME_SUMMARY_RAW_DATA
     Specify the time summary raw_data item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_STEP
     Specify the time summary step item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_WIDTH
     Specify the time summary width item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_GRIB_CODES
     Specify the time summary grib_code item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_VALID_FREQ
     Specify the time summary valid_freq item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PB2NC

   PB2NC_TIME_SUMMARY_VALID_THRESH
     Specify the time summary valid_thresh item in the MET pb2nc config file. Refer to the `MET User's Guide <https://dtcenter.org/community-code/model-evaluation-tools-met/documentation>`_ for more information.

     | *Used by:*  PN2NC

   PB2NC_MASK_POLY
     Set the mask.poly entry in the PB2NC MET config file.

     | *Used by:*  PN2NC

   PB2NC_MASK_GRID
     Set the mask.grid entry in the PB2NC MET config file.

     | *Used by:*  PN2NC

   POINT_STAT_MASK_SID
     Set the mask.sid entry in the PointStat MET config file.

     | *Used by:*  PointStat

   POINT_STAT_MASK_GRID
     Set the mask.grid entry in the PointStat MET config file.

     | *Used by:*  PointStat

   POINT_STAT_MASK_POLY
     Set the mask.poly entry in the PointStat MET config file.

     | *Used by:*  PointStat

   MODE_GRID_RES
     Set the grid_res entry in the MODE MET config file.

     | *Used by:*  MODE

   TC_PAIRS_INIT_BEG
     Set the initialization begin time for TCpairs.

     | *Used by:*  TCPairs

   TC_PAIRS_INIT_END
     Set the initialization end time for TCpairs.

     | *Used by:*  TCPairs

   TC_PAIRS_VALID_BEG
     Set the valid begin time for TCPairs.

     | *Used by:*  TCPairs

   TC_PAIRS_VALID_END
     Set the valid end time for TCpairs.

     | *Used by:*  TCpairs

   ENS_ENSEMBLE_STAT_INPUT_DATATYPE
     Set the file_type entry of the ens dictionary in the MET config file for EnsembleStat.

     | *Used by:*  EnsembleStat

   FCST_SERIES_ANALYSIS_INPUT_DATATYPE
     Set the file_type entry of the fcst dictionary in the MET config file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   OBS_SERIES_ANALYSIS_INPUT_DATATYPE
     Set the file_type entry of the obs dictionary in the MET config file for SeriesAnalysis.

     | *Used by:*  SeriesAnalysis

   MET_DB_LOAD_RUNTIME_FREQ
     Frequency to run Grid-Diag. See :ref:`Runtime_Freq` for more information.

     | *Used by:*  GridDiag

   MET_DATA_DB_DIR
     Set this the location of the dtcenter/METdatadb repository.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_XML_FILE
     Template XML file that is used to load data into METviewer using the
     met_db_load.py script. Values from the METplus configuration file are
     substituted into this file before passing it to the script. The default
     value can be used to run unless the template doesn't fit the needs of the
     use case.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_REMOVE_TMP_XML
     If set to False, then the temporary XML file with substituted values will
     not be removed after the use case finishes. This is used for debugging
     purposes only. The temporary XML file may contain sensitive information
     like database credentials so it is recommended to remove the temporary
     file after each run.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_HOST
     Set the <load_spec><connection><host> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_DATABASE
     Set the <load_spec><connection><database> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_USER
     Set the <load_spec><connection><user> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_PASSWORD
     Set the <load_spec><connection><password> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_VERBOSE
     Set the <load_spec><verbose> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_INSERT_SIZE
     Set the <load_spec><insert_size> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_MODE_HEADER_DB_CHECK
     Set the <load_spec><mode_header_db_check> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_DROP_INDEXES
     Set the <load_spec><drop_indexes> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_APPLY_INDEXES
     Set the <load_spec><apply_indexes> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_GROUP
     Set the <load_spec><group> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_LOAD_STAT
     Set the <load_spec><load_stat> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_LOAD_MODE
     Set the <load_spec><load_mode> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_LOAD_MTD
     Set the <load_spec><load_mtd> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_MV_LOAD_MPR
     Set the <load_spec><load_mpr> value in the
     METdbLoad XML template file.

     | *Used by:*  METdbLoad

   MET_DB_LOAD_INPUT_TEMPLATE
     Path to a directory containing .stat or .tcst file that will be loaded
     into METviewer. This can be a single directory or a list of directories.
     The paths can include filename template tags that correspond to each
     run time. The wrapper will traverse through each sub directory under the
     directories listed here and add any directory that contains any files that
     end with .stat or .tcst to the XML file that is passed into the
     met_db_load.py script.

     | *Used by:*  METdbLoad

   CYCLONE_PLOTTER_ADD_WATERMARK
     If set to True, add a watermark with the current time to the image generated by
     CyclonePlotter.

     | *Used by:* CyclonePlotter

   GRID_STAT_CLIMO_CDF_CDF_BINS
     See :term:`GRID_STAT_CLIMO_CDF_BINS`

   GRID_STAT_CLIMO_CDF_BINS
     Specify the value for 'climo_cdf.cdf_bins' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_CDF_CENTER_BINS
     Specify the value for 'climo_cdf.center_bins' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_CDF_WRITE_BINS
     Specify the value for 'climo_cdf.write_bins' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   POINT_STAT_CLIMO_CDF_CDF_BINS
     See :term:`POINT_STAT_CLIMO_CDF_BINS`

   POINT_STAT_CLIMO_CDF_BINS
     Specify the value for 'climo_cdf.cdf_bins' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_CDF_CENTER_BINS
     Specify the value for 'climo_cdf.center_bins' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_CDF_WRITE_BINS
     Specify the value for 'climo_cdf.write_bins' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   GRID_STAT_OUTPUT_FLAG_FHO
     Specify the value for 'output_flag.fho' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_CTC
     Specify the value for 'output_flag.ctc' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_CTS
     Specify the value for 'output_flag.cts' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_MCTC
     Specify the value for 'output_flag.mctc' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_MCTS
     Specify the value for 'output_flag.mcts' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_CNT
     Specify the value for 'output_flag.cnt' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_SL1L2
     Specify the value for 'output_flag.sl1l2' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_SAL1L2
     Specify the value for 'output_flag.sal1l2' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_VL1L2
     Specify the value for 'output_flag.vl1l2' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_VAL1L2
     Specify the value for 'output_flag.val1l2' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_VCNT
     Specify the value for 'output_flag.vcnt' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_PCT
     Specify the value for 'output_flag.pct' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_PSTD
     Specify the value for 'output_flag.pstd' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_PJC
     Specify the value for 'output_flag.pjc' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_PRC
     Specify the value for 'output_flag.prc' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_ECLV
     Specify the value for 'output_flag.eclv' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_NBRCTC
     Specify the value for 'output_flag.nbrctc' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_NBRCTS
     Specify the value for 'output_flag.nbrcts' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_NBRCNT
     Specify the value for 'output_flag.nbrcnt' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_GRAD
     Specify the value for 'output_flag.grad' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_OUTPUT_FLAG_DMAP
     Specify the value for 'output_flag.dmap' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_LATLON
     Specify the value for 'nc_pairs_flag.latlon' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_RAW
     Specify the value for 'nc_pairs_flag.raw' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_DIFF
     Specify the value for 'nc_pairs_flag.diff' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_CLIMO
     Specify the value for 'nc_pairs_flag.climo' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_CLIMO_CDP
     Specify the value for 'nc_pairs_flag.climo_cdp' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_WEIGHT
     Specify the value for 'nc_pairs_flag.weight' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_NBRHD
     Specify the value for 'nc_pairs_flag.nbrhd' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_FOURIER
     Specify the value for 'nc_pairs_flag.fourier' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_GRADIENT
     Specify the value for 'nc_pairs_flag.gradient' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_DISTANCE_MAP
     Specify the value for 'nc_pairs_flag.distance_map' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_FLAG_APPLY_MASK
     Specify the value for 'nc_pairs_flag.apply_mask' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   TC_STAT_COLUMN_STR_EXC_NAME
     Specify the value for 'column_str_exc_name' in the MET configuration file for TCStat.

     | *Used by:* TCStat

   TC_STAT_COLUMN_STR_EXC_VAL
     Specify the value for 'column_str_exc_val' in the MET configuration file for TCStat.

     | *Used by:* TCStat

   TC_STAT_INIT_STR_EXC_NAME
     Specify the value for 'init_str_exc_name' in the MET configuration file for TCStat.

     | *Used by:* TCStat

   TC_STAT_INIT_STR_EXC_VAL
     Specify the value for 'init_str_exc_val' in the MET configuration file for TCStat.

     | *Used by:* TCStat

   TC_GEN_GENESIS_MATCH_POINT_TO_TRACK
     Specify the value for 'genesis_match_point_to_track' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   TC_GEN_GENESIS_MATCH_WINDOW_BEG
     Specify the value for 'genesis_match_window.beg' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   TC_GEN_GENESIS_MATCH_WINDOW_END
     Specify the value for 'genesis_match_window.end' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   TC_GEN_OPS_HIT_WINDOW_BEG
     Specify the value for 'ops_hit_window.beg' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   TC_GEN_OPS_HIT_WINDOW_END
     Specify the value for 'ops_hit_window.end' in the MET configuration file for TCGen.

     | *Used by:* TCGen

   MODE_FCST_FILTER_ATTR_NAME
     Specify the value for 'fcst.filter_attr_name' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_FCST_FILTER_ATTR_THRESH
     Specify the value for 'fcst.filter_attr_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_FCST_CENSOR_THRESH
     Specify the value for 'fcst.censor_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_FCST_CENSOR_VAL
     Specify the value for 'fcst.censor_val' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_FCST_VLD_THRESH
     Specify the value for 'fcst.vld_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_OBS_FILTER_ATTR_NAME
     Specify the value for 'obs.filter_attr_name' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_OBS_FILTER_ATTR_THRESH
     Specify the value for 'obs.filter_attr_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_OBS_CENSOR_THRESH
     Specify the value for 'obs.censor_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_OBS_CENSOR_VAL
     Specify the value for 'obs.censor_val' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_OBS_VLD_THRESH
     Specify the value for 'obs.vld_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_CENTROID_DIST
     Specify the value for 'weight.centroid_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_BOUNDARY_DIST
     Specify the value for 'weight.boundary_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_CONVEX_HULL_DIST
     Specify the value for 'weight.convex_hull_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_ANGLE_DIFF
     Specify the value for 'weight.angle_diff' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_ASPECT_DIFF
     Specify the value for 'weight.aspect_diff' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_AREA_RATIO
     Specify the value for 'weight.area_ratio' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_INT_AREA_RATIO
     Specify the value for 'weight.int_area_ratio' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_CURVATURE_RATIO
     Specify the value for 'weight.curvature_ratio' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_COMPLEXITY_RATIO
     Specify the value for 'weight.complexity_ratio' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_INTEN_PERC_RATIO
     Specify the value for 'weight.inten_perc_ratio' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_WEIGHT_INTEN_PERC_VALUE
     Specify the value for 'weight.inten_perc_value' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_LATLON
     Specify the value for 'nc_pairs_flag.latlon' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_RAW
     Specify the value for 'nc_pairs_flag.raw' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_OBJECT_RAW
     Specify the value for 'nc_pairs_flag.object_raw' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_OBJECT_ID
     Specify the value for 'nc_pairs_flag.object_id' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_CLUSTER_ID
     Specify the value for 'nc_pairs_flag.cluster_id' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_NC_PAIRS_FLAG_POLYLINES
     Specify the value for 'nc_pairs_flag.polylines' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MASK_GRID
     Specify the value for 'mask.grid' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MASK_GRID_FLAG
     Specify the value for 'mask.grid_flag' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MASK_POLY
     Specify the value for 'mask.poly' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MASK_POLY_FLAG
     Specify the value for 'mask.poly_flag' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MATCH_FLAG
     Specify the value for 'match_flag' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_MAX_CENTROID_DIST
     Specify the value for 'max_centroid_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_TOTAL_INTEREST_THRESH
     Specify the value for 'total_interest_thresh' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_INTEREST_FUNCTION_CENTROID_DIST
     Specify the value for 'interest_function.centroid_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_INTEREST_FUNCTION_BOUNDARY_DIST
     Specify the value for 'interest_function.boundary_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST
     Specify the value for 'interest_function.convex_hull_dist' in the MET configuration file for MODE.

     | *Used by:* MODE

   POINT_STAT_OBS_QUALITY
     Specify the value for 'obs_quality' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_FHO
     Specify the value for 'output_flag.fho' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_CTC
     Specify the value for 'output_flag.ctc' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_CTS
     Specify the value for 'output_flag.cts' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_MCTC
     Specify the value for 'output_flag.mctc' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_MCTS
     Specify the value for 'output_flag.mcts' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_CNT
     Specify the value for 'output_flag.cnt' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_SL1L2
     Specify the value for 'output_flag.sl1l2' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_SAL1L2
     Specify the value for 'output_flag.sal1l2' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_VL1L2
     Specify the value for 'output_flag.vl1l2' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_VAL1L2
     Specify the value for 'output_flag.val1l2' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_VCNT
     Specify the value for 'output_flag.vcnt' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_PCT
     Specify the value for 'output_flag.pct' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_PSTD
     Specify the value for 'output_flag.pstd' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_PJC
     Specify the value for 'output_flag.pjc' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_PRC
     Specify the value for 'output_flag.prc' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_ECNT
     Specify the value for 'output_flag.ecnt' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_RPS
     Specify the value for 'output_flag.rps' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_ECLV
     Specify the value for 'output_flag.eclv' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_OUTPUT_FLAG_MPR
     Specify the value for 'output_flag.mpr' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_INTERP_VLD_THRESH
     Specify the value for 'interp.vld_thresh' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_INTERP_SHAPE
     Specify the value for 'interp.shape' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_INTERP_TYPE_METHOD
     Specify the value for 'interp.type.method' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_INTERP_TYPE_WIDTH
     Specify the value for 'interp.type.width' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_FILE_NAME
     Specify the value for 'climo_mean.file_name' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_FIELD
     Specify the value for 'climo_mean.field' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_REGRID_METHOD
     Specify the value for 'climo_mean.regrid.method' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_REGRID_WIDTH
     Specify the value for 'climo_mean.regrid.width' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_REGRID_VLD_THRESH
     Specify the value for 'climo_mean.regrid.vld_thresh' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_REGRID_SHAPE
     Specify the value for 'climo_mean.regrid.shape' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD
     Specify the value for 'climo_mean.time_interp_method' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_MATCH_MONTH
     Specify the value for 'climo_mean.match_month' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_DAY_INTERVAL
     Specify the value for 'climo_mean.day_interval' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_MEAN_HOUR_INTERVAL
     Specify the value for 'climo_mean.hour_interval' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_FILE_NAME
     Specify the value for 'climo_stdev.file_name' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_FIELD
     Specify the value for 'climo_stdev.field' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_REGRID_METHOD
     Specify the value for 'climo_stdev.regrid.method' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_REGRID_WIDTH
     Specify the value for 'climo_stdev.regrid.width' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_REGRID_VLD_THRESH
     Specify the value for 'climo_stdev.regrid.vld_thresh' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_REGRID_SHAPE
     Specify the value for 'climo_stdev.regrid.shape' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD
     Specify the value for 'climo_stdev.time_interp_method' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_MATCH_MONTH
     Specify the value for 'climo_stdev.match_month' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_DAY_INTERVAL
     Specify the value for 'climo_stdev.day_interval' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   POINT_STAT_CLIMO_STDEV_HOUR_INTERVAL
     Specify the value for 'climo_stdev.hour_interval' in the MET configuration file for PointStat.

     | *Used by:* PointStat

   GRID_STAT_INTERP_FIELD
     Specify the value for 'interp.field' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_INTERP_VLD_THRESH
     Specify the value for 'interp.vld_thresh' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_INTERP_SHAPE
     Specify the value for 'interp.shape' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_INTERP_TYPE_METHOD
     Specify the value for 'interp.type.method' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_INTERP_TYPE_WIDTH
     Specify the value for 'interp.type.width' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_NC_PAIRS_VAR_NAME
     Specify the value for 'nc_pairs_var_name' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_FILE_NAME
     Specify the value for 'climo_mean.file_name' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_FIELD
     Specify the value for 'climo_mean.field' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_REGRID_METHOD
     Specify the value for 'climo_mean.regrid.method' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_REGRID_WIDTH
     Specify the value for 'climo_mean.regrid.width' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_REGRID_VLD_THRESH
     Specify the value for 'climo_mean.regrid.vld_thresh' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_REGRID_SHAPE
     Specify the value for 'climo_mean.regrid.shape' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_TIME_INTERP_METHOD
     Specify the value for 'climo_mean.time_interp_method' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_MATCH_MONTH
     Specify the value for 'climo_mean.match_month' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_DAY_INTERVAL
     Specify the value for 'climo_mean.day_interval' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_MEAN_HOUR_INTERVAL
     Specify the value for 'climo_mean.hour_interval' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_FILE_NAME
     Specify the value for 'climo_stdev.file_name' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_FIELD
     Specify the value for 'climo_stdev.field' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_REGRID_METHOD
     Specify the value for 'climo_stdev.regrid.method' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_REGRID_WIDTH
     Specify the value for 'climo_stdev.regrid.width' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_REGRID_VLD_THRESH
     Specify the value for 'climo_stdev.regrid.vld_thresh' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_REGRID_SHAPE
     Specify the value for 'climo_stdev.regrid.shape' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_TIME_INTERP_METHOD
     Specify the value for 'climo_stdev.time_interp_method' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_MATCH_MONTH
     Specify the value for 'climo_stdev.match_month' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_DAY_INTERVAL
     Specify the value for 'climo_stdev.day_interval' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   GRID_STAT_CLIMO_STDEV_HOUR_INTERVAL
     Specify the value for 'climo_stdev.hour_interval' in the MET configuration file for GridStat.

     | *Used by:* GridStat


   GRID_STAT_GRID_WEIGHT_FLAG
     Specify the value for 'grid_weight_flag' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   FCST_GRID_STAT_FILE_TYPE
     Specify the value for 'fcst.file_type' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   OBS_GRID_STAT_FILE_TYPE
     Specify the value for 'obs.file_type' in the MET configuration file for GridStat.

     | *Used by:* GridStat

   SERIES_ANALYSIS_CLIMO_MEAN_FILE_NAME
     Specify the value for 'climo_mean.file_name' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_FIELD
     Specify the value for 'climo_mean.field' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_REGRID_METHOD
     Specify the value for 'climo_mean.regrid.method' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_REGRID_WIDTH
     Specify the value for 'climo_mean.regrid.width' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_REGRID_VLD_THRESH
     Specify the value for 'climo_mean.regrid.vld_thresh' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_REGRID_SHAPE
     Specify the value for 'climo_mean.regrid.shape' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_TIME_INTERP_METHOD
     Specify the value for 'climo_mean.time_interp_method' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_MATCH_MONTH
     Specify the value for 'climo_mean.match_month' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_DAY_INTERVAL
     Specify the value for 'climo_mean.day_interval' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_MEAN_HOUR_INTERVAL
     Specify the value for 'climo_mean.hour_interval' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_FILE_NAME
     Specify the value for 'climo_stdev.file_name' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_FIELD
     Specify the value for 'climo_stdev.field' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_REGRID_METHOD
     Specify the value for 'climo_stdev.regrid.method' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_REGRID_WIDTH
     Specify the value for 'climo_stdev.regrid.width' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_REGRID_VLD_THRESH
     Specify the value for 'climo_stdev.regrid.vld_thresh' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_REGRID_SHAPE
     Specify the value for 'climo_stdev.regrid.shape' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_TIME_INTERP_METHOD
     Specify the value for 'climo_stdev.time_interp_method' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_MATCH_MONTH
     Specify the value for 'climo_stdev.match_month' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_DAY_INTERVAL
     Specify the value for 'climo_stdev.day_interval' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   SERIES_ANALYSIS_CLIMO_STDEV_HOUR_INTERVAL
     Specify the value for 'climo_stdev.hour_interval' in the MET configuration file for SeriesAnalysis.

     | *Used by:* SeriesAnalysis

   PB2NC_PB_REPORT_TYPE
     Specify the value for 'pb_report_type' in the MET configuration file for PB2NC.

     | *Used by:* PB2NC

   PB2NC_LEVEL_RANGE_BEG
     Specify the value for 'level_range.beg' in the MET configuration file for PB2NC.

     | *Used by:* PB2NC

   PB2NC_LEVEL_RANGE_END
     Specify the value for 'level_range.end' in the MET configuration file for PB2NC.

     | *Used by:* PB2NC

   PB2NC_LEVEL_CATEGORY
     Specify the value for 'level_category' in the MET configuration file for PB2NC.

     | *Used by:* PB2NC

   PB2NC_QUALITY_MARK_THRESH
     Specify the value for 'quality_mark_thresh' in the MET configuration file for PB2NC.

     | *Used by:* PB2NC
