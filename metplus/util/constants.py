# Constant variables used throughout the METplus wrappers source code

UPGRADE_INSTRUCTIONS_URL = (
    'https://metplus.readthedocs.io/en/develop/Users_Guide/'
    'release-notes.html#metplus-wrappers-upgrade-instructions'
)

# dictionary used by get_wrapper_name function to easily convert wrapper
# name in many formats to the correct name of the wrapper class
LOWER_TO_WRAPPER_NAME = {
    'ascii2nc': 'ASCII2NC',
    'cycloneplotter': 'CyclonePlotter',
    'ensemblestat': 'EnsembleStat',
    'example': 'Example',
    'extracttiles': 'ExtractTiles',
    'gempaktocf': 'GempakToCF',
    'genvxmask': 'GenVxMask',
    'genensprod': 'GenEnsProd',
    'gfdltracker': 'GFDLTracker',
    'griddiag': 'GridDiag',
    'gridstat': 'GridStat',
    'ioda2nc': 'IODA2NC',
    'madis2nc': 'MADIS2NC',
    'metdbload': 'METDbLoad',
    'mode': 'MODE',
    'mtd': 'MTD',
    'modetimedomain': 'MTD',
    'pb2nc': 'PB2NC',
    'pcpcombine': 'PCPCombine',
    'plotdataplane': 'PlotDataPlane',
    'plotpointobs': 'PlotPointObs',
    'point2grid': 'Point2Grid',
    'pointtogrid': 'Point2Grid',
    'pointstat': 'PointStat',
    'pyembedingest': 'PyEmbedIngest',
    'regriddataplane': 'RegridDataPlane',
    'seriesanalysis': 'SeriesAnalysis',
    'statanalysis': 'StatAnalysis',
    'tcdiag': 'TCDiag',
    'tcgen': 'TCGen',
    'tcpairs': 'TCPairs',
    'tcrmw': 'TCRMW',
    'tcstat': 'TCStat',
    'usage': 'Usage',
    'userscript': 'UserScript',
    'waveletstat': 'WaveletStat',
}

# supported file extensions that will automatically be uncompressed
COMPRESSION_EXTENSIONS = [
    '.gz',
    '.bz2',
    '.zip',
]

# Keywords of valid types of Python Embedding in MET tools
PYTHON_EMBEDDING_TYPES = [
    'PYTHON_NUMPY',
    'PYTHON_XARRAY',
    'PYTHON_PANDAS',
]

# types of climatology values that should be checked and set
CLIMO_TYPES = [
    'MEAN',
    'STDEV',
]

# comparison operators that the MET tools support
# key is an operator and value is the alphabetic equivalent
VALID_COMPARISONS = {
    '>=': 'ge',
    '>': 'gt',
    '==': 'eq',
    '!=': 'ne',
    '<=': 'le',
    '<': 'lt',
}

# wrappers that do not run shell commands
# used to check that at least one command was generated if it should
NO_COMMAND_WRAPPERS = (
    'Example',
    'CyclonePlotter',
)

# wrappers that takes multiple inputs via Python Embedding
# used to check if file_type is set properly to note Python Embedding is used
MULTIPLE_INPUT_WRAPPERS = (
    'EnsembleStat',
    'MTD',
    'SeriesAnalysis',
    'GenEnsProd',
)

# wrappers that support the time_offset_warning global MET config variable
TIME_OFFSET_WARNING_WRAPPERS = (
    'GridStat',
    'MODE',
    'SeriesAnalysis',
    'WaveletStat',
)

# configuration variables that are specific to a given run
# these are copied from [config] to [runtime] at the
# end of the run so they will not be read if the final
# config file is passed back into METplus but they will
# still be available to review
RUNTIME_CONFS = [
    'RUN_ID',
    'CLOCK_TIME',
    'METPLUS_VERSION',
    'MET_INSTALL_DIR',
    'CONFIG_INPUT',
    'METPLUS_CONF',
    'TMP_DIR',
    'STAGING_DIR',
    'FILE_LISTS_DIR',
    'CONVERT',
    'GEMPAKTOCF_JAR',
    'GFDL_TRACKER_EXEC',
    'INPUT_MUST_EXIST',
    'USER_SHELL',
    'DO_NOT_RUN_EXE',
    'SCRUB_STAGING_DIR',
    'MET_BIN_DIR',
]

# datetime year month day (YYYYMMDD) notation
YMD = '%Y%m%d'

# datetime year month day hour minute second (YYYYMMDD_HHMMSS) notation
YMD_HMS = '%Y%m%d_%H%M%S'

# missing data value used to check if integer values are not set
# we often check for None if a variable is not set, but 0 and None
# have the same result in a test. 0 may be a valid integer value
MISSING_DATA_VALUE = -9999

# Dictionary used to alert users that they are using deprecated config
# variables and need to update the configs to run METplus
# key is the name of the depreacted variable that is no longer allowed in any
#   config files
# value is a dictionary containing information about what to do with the
#   deprecated config
# 'alt' is the alternative name for the deprecated config. this can be a
#   single variable name or text to describe multiple variables or how to
#   handle it. Set to None to tell the user to just remove the variable.
# 'copy' is an optional item (defaults to True). set this to False if one
#   cannot simply replace the deprecated variable name with the value in 'alt'
# 'upgrade' is an optional item where the value is a keyword that will output
#   additional instructions for the user.
#   Valid Values: 'ensemble'
DEPRECATED_DICT = {
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_MEAN': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_STDEV': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_MINUS': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_PLUS': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_MIN': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_MAX': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_RANGE': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_VLD_COUNT': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_FREQUENCY': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_NEP': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_ENSEMBLE_FLAG_NMEP': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NBRHD_PROB_WIDTH': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NBRHD_PROB_SHAPE': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NBRHD_PROB_VLD_THRESH': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_VLD_THRESH': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_SHAPE': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_METHOD': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_WIDTH': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_DX': {'upgrade': 'ensemble'},
    'ENSEMBLE_STAT_NMEP_SMOOTH_GAUSSIAN_RADIUS': {'upgrade': 'ensemble'},
}

# List of variables in wrapped MET config files that are no longer set
# All explicitly set wrapped MET config files found in a METplus config,
# e.g. GRID_STAT_CONFIG_FILE, will be checked for these variables
# If any of these items are found, then an error will be reported
DEPRECATED_MET_LIST = [
]
