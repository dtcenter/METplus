METplus Configuration Glossary
===========================================================

.. glossary::
   :sorted:

   AAAAAA_THIS_IS_A_TEMPLATE
     Text goes here
    
     | *Used by:*
     | *Family:*
     | *Default:*

   ANLY_ASCII_REGEX_LEAD
     The regular expression describing the analysis (obs) file name (in ASCII format) of the intermediate file generated when running a series_by_lead process.
    
     | *Used by:* SeriesByLead
     | *Family:* [regex_pattern]
     | *Default:*

   ANLY_NC_TILE_REGEX
     The regular expression used to search the input files that are in netCDF format and used in the series_by_analysis process.
    
     | *Used by:* SeriesByLead, SeriesByInit
     | *Family:* [regex_pattern]
     | *Default:*
   
   ANLY_TILE_PREFIX
     The prefix to the filename for the analysis file that is created as part of a series_analysis process.
    
     | *Used by:* ExtractTiles, SeriesByLead
     | *Family:* [regex_pattern]
     | *Default:*
   
   ANLY_TILE_REGEX
     The regular expression for the analysis input file. The file is in GRIBv2 format.
    
     | *Used by:* SeriesByLead, SeriesByInit
     | *Family:* [regex_pattern]
     | *Default:*

   TESTING_SORTING_THIS_IS_FIRST_BUT_SHOULD_BE_LAST
     Testing
     
     | *Used by:*

   CYCLONE_INPUT_DIR
     Input directory for the cyclone plotter. This should be the output directory for the MET TC-Pairs utility

     | *Used by:* CyclonePlotter
     | *Family:* [dir]
     | *Default:* Varies

   OBS_REGRID_DATA_PLANE_RUN
     The value

   VALID_TIME_FMT
     The format of the valid time string

   ANOTHER_ONE
     Value

   ANOTHER_ONE
     Value

   TESTING2
     Value
     
   FCST_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME
     Specify the forecast output field name that is created by RegridDataPlane. The name corresponds to FCST_VAR<n>_NAME. This is used when using Python Embedding as input to the MET tool, because the FCST_VAR<n>_NAME defines the python script to call.
    
     | *Used by:* RegridDataPlane
     | *Family:* [config]
     | *Default:* None


   OBS_REGRID_DATA_PLANE_VAR<n>_OUTPUT_FIELD_NAME
     Specify the observation output field name that is created by RegridDataPlane. The name corresponds to OBS_VAR<n>_NAME. This is used when using Python Embedding as input to the MET tool, because the OBS_VAR<n>_NAME defines the python script to call.
    
     | *Used by:* RegridDataPlane
     | *Family:* [config]
     | *Default:* None

   LOG_ASCII2NC_VERBOSITY
     Overrides the log verbosity for Ascii2Nc only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None
     
   LOG_ENSEMBLE_STAT_VERBOSITY
     Overrides the log verbosity for EnsembleStat only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* EnsembleStat
     | *Family:* [config]
     | *Default:* None
     
   LOG_GRID_STAT_VERBOSITY
     Overrides the log verbosity for GridStat only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* GridStat
     | *Family:* [config]
     | *Default:* None
     
   LOG_MODE_VERBOSITY
     Overrides the log verbosity for Mode only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* Mode
     | *Family:* [config]
     | *Default:* None
     
   LOG_MTD_VERBOSITY
     Overrides the log verbosity for MTD only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* MTD
     | *Family:* [config]
     | *Default:* None
     
   LOG_PB2NC_VERBOSITY
     Overrides the log verbosity for PB2NC only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* PB2NC
     | *Family:* [config]
     | *Default:* None
     
   LOG_PCP_COMBINE_VERBOSITY
     Overrides the log verbosity for PcpCombine only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* PcpCombine
     | *Family:* [config]
     | *Default:* None
     
   LOG_POINT_STAT_VERBOSITY
     Overrides the log verbosity for PointStat only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* PointStat
     | *Family:* [config]
     | *Default:* None
     
   LOG_REGRID_DATA_PLANE_VERBOSITY
     Overrides the log verbosity for RegridDataPlane only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* RegridDataPlane
     | *Family:* [config]
     | *Default:* None
     
   LOG_TC_PAIRS_VERBOSITY
     Overrides the log verbosity for TcPairs only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* TcPairs
     | *Family:* [config]
     | *Default:* None
     
   LOG_TC_STAT_VERBOSITY
     Overrides the log verbosity for TcStat only. If not set, the verbosity level is controlled by LOG_MET_VERBOSITY.

     | *Used by:* TcStat
     | *Family:* [config]
     | *Default:* None

   LOG_LINE_FORMAT
     Defines the formatting of each METplus log output line. For more information on acceptable values, see the Python documentation for LogRecord: https://docs.python.org/3/library/logging.html#logging.LogRecord

     | *Used by:* All
     | *Family:* [config]
     | *Default:* %(asctime)s.%(msecs)03d %(name)s (%(filename)s:%(lineno)d) %(levelname)s: %(message)s

   LOG_LINE_DATE_FORMAT
     Defines the formatting of the date in the METplus log output. See LOG_LINE_FORMAT.

     | *Used by:* All
     | *Family:* [config]
     | *Default:* %m/%d %H:%M:%S


   FCST_PCP_COMBINE_COMMAND
     Used only when FCST_PCP_COMBINE_METHOD = CUSTOM. Custom command to run PcpCombine with a complex call that doesn't fit common use cases. Value can include filename template syntax, i.e. {valid?fmt=%Y%m%d}, that will be substituted based on the current runtime. The name of the application and verbosity flag does not need to be included. For example, if set to '-derive min,max /some/file' the command run will be pcp_combine -v 2 -derive min,max /some/file. A corresponding variable exists for observation data called OBS_PCP_COMBINE_COMMAND.

     | *Used by:* PcpCombine
     | *Family:* [config]
     | *Default:* None
     
   OBS_PCP_COMBINE_COMMAND
     Used only when OBS_PCP_COMBINE_METHOD = CUSTOM. Custom command to run PcpCombine with a complex call that doesn't fit common use cases. Value can include filename template syntax, i.e. {valid?fmt=%Y%m%d}, that will be substituted based on the current runtime. The name of the application and verbosity flag does not need to be included. For example, if set to '-derive min,max /some/file' the command run will be pcp_combine -v 2 -derive min,max /some/file. A corresponding variable exists for forecast data called FCST_PCP_COMBINE_COMMAND.

     | *Used by:* PcpCombine
     | *Family:* [config]
     | *Default:* None
     
   CUSTOM_INGEST_<n>_SCRIPT
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the python script with arguments to run through RegridDataPlane to generate a file that can be read by the MET tools. This variable supports filename template syntax, so you can specify filenames with time information, i.e. {valid?fmt=%Y%m%d}. See also CUSTOM_INGEST<n>_TYPE, CUSTOM_INGEST<n>_OUTPUT_GRID, CUSTOM_INGEST<n>_OUTPUT_TEMPLATE, and CUSTOM_INGEST<n>_OUTPUT_DIR.

     | *Used by:* CustomIngest
     | *Family:* [config]
     | *Default:* None

   CUSTOM_INGEST_<n>_TYPE
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the type of output generated by the Python script. Valid options are NUMPY, XARRAY, and PANDAS. See also CUSTOM_INGEST<n>_SCRIPT, CUSTOM_INGEST<n>_OUTPUT_GRID, CUSTOM_INGEST<n>_OUTPUT_TEMPLATE, and CUSTOM_INGEST<n>_OUTPUT_DIR.

     | *Used by:* CustomIngest
     | *Family:* [config]
     | *Default:* None

   CUSTOM_INGEST_<n>_OUTPUT_GRID
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the grid information that RegridDataPlane will use to generate a file that can be read by the MET tools. This can be a file path or a grid definition. See the MET User's Guide section regarding Regrid-Data-Plane for more information. See also CUSTOM_INGEST<n>_TYPE, CUSTOM_INGEST<n>_SCRIPT, CUSTOM_INGEST<n>_OUTPUT_TEMPLATE, and CUSTOM_INGEST<n>_OUTPUT_DIR.

     | *Used by:* CustomIngest
     | *Family:* [config]
     | *Default:* None

   CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the output filename using filename template syntax. The value will be substituted with time information and appended to CUSTOM_INGEST_<n>_OUTPUT_DIR if it is set. See also CUSTOM_INGEST<n>_TYPE, CUSTOM_INGEST<n>_SCRIPT, and CUSTOM_INGEST<n>_OUTPUT_GRID.

     | *Used by:* CustomIngest
     | *Family:* [filename_templates]
     | *Default:* None

   CUSTOM_INGEST_<n>_OUTPUT_DIR
     Used to use Python embedding to process multiple files. <n> is an integer greater than or equal to 1. Specifies the output diirectory to write data. See also CUSTOM_INGEST<n>_TYPE, CUSTOM_INGEST<n>_SCRIPT, and CUSTOM_INGEST<n>_OUTPUT_GRID, and CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE.

     | *Used by:* CustomIngest
     | *Family:* [dir]
     | *Default:* None

   ASCII2NC_CONFIG_FILE
     Path to optional configuration file read by Ascii2Nc.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_INPUT_FORMAT
     Optional string to specify the format of the input data. Valid options are "met_point", "little_r", "surfrad", "wwsis", "aeronet", "aeronetv2", or "aeronetv3."

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_MASK_GRID
     Named grid or a data file defining the grid for filtering the point observations spatially (optional).

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_MASK_POLY
     A polyline file, the output of gen_vx_mask, or a gridded data file with field information for filtering the point observations spatially (optional).

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_MASK_SID
     A station ID masking file or a comma-separated list of station ID's for filtering the point observations spatially (optional).

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_INPUT_DIR
     Directory containing input data to Ascii2Nc. This variable is optional because you can specify the full path to the input files using ASCII2NC_INPUT_TEMPLATE.

     | *Used by:* Ascii2Nc
     | *Family:* [dir]
     | *Default:* None

   ASCII2NC_INPUT_TEMPLATE
     Filename template of the input file used by Ascii2Nc. See also ASCII2NC_INPUT_DIR.

     | *Used by:* Ascii2Nc
     | *Family:* [filename_templates]
     | *Default:* None

   ASCII2NC_OUTPUT_DIR
     Directory to write output data generated by Ascii2Nc. This variable is optional because you can specify the full path to the output files using ASCII2NC_OUTPUT_TEMPLATE.

     | *Used by:* Ascii2Nc
     | *Family:* [dir]
     | *Default:* None

   ASCII2NC_OUTPUT_TEMPLATE
     Filename template of the output file generated by Ascii2Nc. See also ASCII2NC_OUTPUT_DIR.

     | *Used by:* Ascii2Nc
     | *Family:* [filename_templates]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_FLAG
     Boolean value to turn on/off time summarization. Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* False

   ASCII2NC_TIME_SUMMARY_RAW_DATA
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_BEG
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_END
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_STEP
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_WIDTH
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_GRIB_CODES
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_VAR_NAMES
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_TYPES
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_VALID_FREQ
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_TIME_SUMMARY_VALID_THRESH
     Read by the Ascii2Nc configuration file if specified by ASCII2NC_CONFIG_FILE. See the MET User's Guide section regarding Ascii2Nc configuration files for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   ASCII2NC_FILE_WINDOW_BEGIN
     Used to control the lower bound of the window around the valid time to determine if an Ascii2Nc input file should be used for processing. Overrides OBS_FILE_WINDOW_BEGIN. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* 0

   ASCII2NC_FILE_WINDOW_END
     Used to control the upper bound of the window around the valid time to determine if an Ascii2Nc input file should be used for processing. Overrides OBS_FILE_WINDOW_BEGIN. See 'Use Windows to Find Valid Files' section for more information.

     | *Used by:* Ascii2Nc
     | *Family:* [config]
     | *Default:* None

   CLIMO_GRID_STAT_INPUT_DIR
     Directory containing the climatology file used by GridStat. This variable is optional because you can specify the full path to a climatology file using CLIMO_GRID_STAT_INPUT_TEMPLATE.

     | *Used by:* GridStat
     | *Family:* [dir]
     | *Default:* None

   CLIMO_GRID_STAT_INPUT_TEMPLATE
     Filename template of the climatology file used by GridStat. See also CLIMO_GRID_STAT_INPUT_DIR.

     | *Used by:* GridStat
     | *Family:* [filename_templates]
     | *Default:* None

   CLIMO_POINT_STAT_INPUT_DIR
     Directory containing the climatology file used by PointStat. This variable is optional because you can specify the full path to a climatology file using CLIMO_POINT_STAT_INPUT_TEMPLATE.

     | *Used by:* PointStat
     | *Family:* [dir]
     | *Default:* None

   CLIMO_POINT_STAT_INPUT_TEMPLATE
     Filename template of the climatology file used by PointStat. See also CLIMO_POINT_STAT_INPUT_DIR.

     | *Used by:* PointStat
     | *Family:* [filename_templates]
     | *Default:* None

