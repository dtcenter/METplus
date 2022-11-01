# Constant variables used throughout the METplus wrappers source code

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
    'makeplots': 'MakePlots',
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
    'tcgen': 'TCGen',
    'tcpairs': 'TCPairs',
    'tcrmw': 'TCRMW',
    'tcstat': 'TCStat',
    'tcmprplotter': 'TCMPRPlotter',
    'usage': 'Usage',
    'userscript': 'UserScript',
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
