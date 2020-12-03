import logging
import os
import shutil
import sys
import datetime
import errno
import time
import calendar
import re
import gzip
import bz2
import zipfile
import struct
import getpass
from os import stat
from pwd import getpwuid
from csv import reader
from os.path import dirname, realpath
from dateutil.relativedelta import relativedelta
from pathlib import Path
from importlib import import_module

import produtil.setup
import produtil.log

from .string_template_substitution import do_string_sub
from .string_template_substitution import parse_template
from .string_template_substitution import get_tags
from . import time_util as time_util
from . import metplus_check

from .. import get_metplus_version

"""!@namespace met_util
 @brief Provides  Utility functions for METplus.
"""

# list of compression extensions that are handled by METplus
VALID_EXTENSIONS = ['.gz', '.bz2', '.zip']

PYTHON_EMBEDDING_TYPES = ['PYTHON_NUMPY', 'PYTHON_XARRAY', 'PYTHON_PANDAS']

LOWER_TO_WRAPPER_NAME = {'ascii2nc': 'ASCII2NC',
                         'cycloneplotter': 'CyclonePlotter',
                         'ensemblestat': 'EnsembleStat',
                         'example': 'Example',
                         'extracttiles': 'ExtractTiles',
                         'gempaktocf': 'GempakToCF',
                         'genvxmask': 'GenVxMask',
                         'griddiag': 'GridDiag',
                         'gridstat': 'GridStat',
                         'makeplots': 'MakePlots',
                         'mode': 'MODE',
                         'mtd': 'MTD',
                         'modetimedomain': 'MTD',
                         'pb2nc': 'PB2NC',
                         'pcpcombine': 'PCPCombine',
                         'plotdataplane': 'PlotDataPlane',
                         'point2grid': 'Point2Grid',
                         'pointtogrid': 'Point2Grid',
                         'Point_2_Grid': 'Point2Grid',
                         'pointstat': 'PointStat',
                         'pyembedingest': 'PyEmbedIngest',
                         'regriddataplane': 'RegridDataPlane',
                         'seriesanalysis': 'SeriesAnalysis',
                         'seriesbyinit': 'SeriesByInit',
                         'seriesbylead': 'SeriesByLead',
                         'statanalysis': 'StatAnalysis',
                         'tcgen': 'TCGen',
                         'tcpairs': 'TCPairs',
                         'tcrmw': 'TCRMW',
                         'tcstat': 'TCStat',
                         'tcmprplotter': 'TCMPRPlotter',
                         'usage': 'Usage',
                         }

valid_comparisons = {">=": "ge",
                     ">": "gt",
                     "==": "eq",
                     "!=": "ne",
                     "<=": "le",
                     "<": "lt",
                     }

# missing data value used to check if integer values are not set
# we often check for None if a variable is not set, but 0 and None
# have the same result in a test. 0 may be a valid integer value
MISSING_DATA_VALUE = -9999

def pre_run_setup(config_inputs):
    from . import config_metplus
    version_number = get_metplus_version()
    print(f'Starting METplus v{version_number}')

    # Read config inputs and return a config instance
    config = config_metplus.setup(config_inputs)

    logger = config.logger

    config.set('config', 'METPLUS_VERSION', version_number)
    logger.info('Running METplus v%s called with command: %s',
                version_number, ' '.join(sys.argv))

    logger.info(f"Log file: {config.getstr('config', 'LOG_METPLUS')}")

    # validate configuration variables
    isOK_A, isOK_B, isOK_C, isOK_D, all_sed_cmds = validate_configuration_variables(config)
    if not (isOK_A and isOK_B and isOK_C and isOK_D):
        # if any sed commands were generated, write them to the sed file
        if all_sed_cmds:
            sed_file = os.path.join(config.getdir('OUTPUT_BASE'), 'sed_commands.txt')
            # remove if sed file exists
            if os.path.exists(sed_file):
                os.remove(sed_file)

            write_list_to_file(sed_file, all_sed_cmds)
            config.logger.error(f"Find/Replace commands have been generated in {sed_file}")

        logger.error("Correct configuration variables and rerun. Exiting.")
        sys.exit(1)

    if not config.getdir('MET_INSTALL_DIR', must_exist=True):
        logger.error('MET_INSTALL_DIR must be set correctly to run METplus')
        sys.exit(1)

    # set staging dir to OUTPUT_BASE/stage if not set
    if not config.has_option('config', 'STAGING_DIR'):
        config.set('config', 'STAGING_DIR',
                   os.path.join(config.getdir('OUTPUT_BASE'), "stage"))

    # get USER_SHELL config variable so the default value doesn't get logged
    # at an inconvenient time (right after "COPYABLE ENVIRONMENT" but before actual
    # copyable environment variable list)
    config.getstr('config', 'USER_SHELL', 'bash')


    # get DO_NOT_RUN_EXE config variable so it shows up at the beginning of execution
    # only if the default value is used
    config.getbool('config', 'DO_NOT_RUN_EXE', False)

    # handle dir to write temporary files
    handle_tmp_dir(config)

    config.env = os.environ.copy()

    return config

def run_metplus(config, process_list):
    total_errors = 0

    try:
        processes = []
        for process, instance in process_list:
            try:
                logname = f"{process}.{instance}" if instance else process
                logger = config.log(logname)
                package_name = ('metplus.wrappers.'
                                f'{camel_to_underscore(process)}_wrapper')
                module = import_module(package_name)
                command_builder = (
                    getattr(module, f"{process}Wrapper")(config,
                                                         instance=instance)
                )

                # if Usage specified in PROCESS_LIST, print usage and exit
                if process == 'Usage':
                    command_builder.run_all_times()
                    return 0
            except AttributeError:
                raise NameError("There was a problem loading "
                                f"{process} wrapper.")

            processes.append(command_builder)

        # check if all processes initialized correctly
        allOK = True
        for process in processes:
            if not process.isOK:
                allOK = False
                class_name = process.__class__.__name__.replace('Wrapper', '')
                logger.error("{} was not initialized properly".format(class_name))

        # exit if any wrappers did not initialized properly
        if not allOK:
            logger.info("Refer to ERROR messages above to resolve issues.")
            return 1

        loop_order = config.getstr('config', 'LOOP_ORDER', '').lower()

        if loop_order == "processes":
            all_commands = []
            for process in processes:
                new_commands = process.run_all_times()
                if new_commands:
                    all_commands.extend(new_commands)

        elif loop_order == "times":
            all_commands = loop_over_times_and_call(config, processes)
        else:
            logger.error("Invalid LOOP_ORDER defined. " + \
                         "Options are processes, times")
            return 1

        # write out all commands and environment variables to file
        write_all_commands(all_commands, config)

       # compute total number of errors that occurred and output results
        for process in processes:
            if process.errors != 0:
                process_name = process.__class__.__name__.replace('Wrapper', '')
                error_msg = '{} had {} error'.format(process_name, process.errors)
                if process.errors > 1:
                    error_msg += 's'
                error_msg += '.'
                logger.error(error_msg)
                total_errors += process.errors

        return total_errors
    except:
        logger.exception("Fatal error occurred")
        logger.info(f"Check the log file for more information: {config.getstr('config', 'LOG_METPLUS')}")
        return 1

def post_run_cleanup(config, app_name, total_errors):
    logger = config.logger
    # scrub staging directory if requested
    if config.getbool('config', 'SCRUB_STAGING_DIR', False) and\
       os.path.exists(config.getdir('STAGING_DIR')):
        staging_dir = config.getdir('STAGING_DIR')
        logger.info("Scrubbing staging dir: %s", staging_dir)
        shutil.rmtree(staging_dir)

    # rewrite final conf so it contains all of the default values used
    write_final_conf(config, logger)

    # compute time it took to run
    start_clock_time = datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                  '%Y%m%d%H%M%S')
    end_clock_time = datetime.datetime.now()
    total_run_time = end_clock_time - start_clock_time
    logger.debug(f"{app_name} took {total_run_time} to run.")

    log_message = f"Check the log file for more information: {config.getstr('config', 'LOG_METPLUS')}"
    if total_errors == 0:
        logger.info(log_message)
        logger.info(f'{app_name} has successfully finished running.')
    else:
        error_msg = f"{app_name} has finished running but had {total_errors} error"
        if total_errors > 1:
            error_msg += 's'
        error_msg += '.'
        logger.error(error_msg)
        logger.info(log_message)
        sys.exit(1)

def write_all_commands(all_commands, config):
    log_timestamp = config.getstr('config', 'LOG_TIMESTAMP')
    filename = os.path.join(config.getdir('LOG_DIR'),
                            f'.all_commands.{log_timestamp}')
    config.logger.debug(f"Writing all commands and environment to {filename}")
    with open(filename, 'w') as file_handle:
        for command, envs in all_commands:
            for env in envs:
                file_handle.write(f"{env}\n")

            file_handle.write("COMMAND:\n")
            file_handle.write(f"{command}\n\n")

def check_for_deprecated_config(config):
    """!Checks user configuration files and reports errors or warnings if any deprecated variable
        is found. If an alternate variable name can be suggested, add it to the 'alt' section
        If the alternate cannot be literally substituted for the old name, set copy to False
       Args:
          @config : METplusConfig object to evaluate
       Returns:
          A tuple containing a boolean if the configuration is suitable to run or not and
          if it is not correct, the 2nd item is a list of sed commands that can be run to help
          fix the incorrect configuration variables
          """

    # key is the name of the depreacted variable that is no longer allowed in any config files
    # value is a dictionary containing information about what to do with the deprecated config
    # 'sec' is the section of the config file where the replacement resides, i.e. config, dir,
    #     filename_templates
    # 'alt' is the alternative name for the deprecated config. this can be a single variable name or
    #     text to describe multiple variables or how to handle it. Set to None to tell the user to
    #     just remove the variable
    # 'copy' is an optional item (defaults to True). set this to False if one cannot simply replace
    #     the deprecated config variable name with the value in 'alt'
    # 'req' is an optional item (defaults to True). this to False to report a warning for the
    #     deprecated config and allow execution to continue. this is generally no longer used
    #     because we are requiring users to update the config files. if used, the developer must
    #     modify the code to handle both variables accordingly
    deprecated_dict = {
        'LOOP_BY_INIT' : {'sec' : 'config', 'alt' : 'LOOP_BY', 'copy': False},
        'LOOP_METHOD' : {'sec' : 'config', 'alt' : 'LOOP_ORDER'},
        'PREPBUFR_DIR_REGEX' : {'sec' : 'regex_pattern', 'alt' : None},
        'PREPBUFR_FILE_REGEX' : {'sec' : 'regex_pattern', 'alt' : None},
        'OBS_INPUT_DIR_REGEX' : {'sec' : 'regex_pattern', 'alt' : 'OBS_POINT_STAT_INPUT_DIR', 'copy': False},
        'FCST_INPUT_DIR_REGEX' : {'sec' : 'regex_pattern', 'alt' : 'FCST_POINT_STAT_INPUT_DIR', 'copy': False},
        'FCST_INPUT_FILE_REGEX' :
        {'sec' : 'regex_pattern', 'alt' : 'FCST_POINT_STAT_INPUT_TEMPLATE', 'copy': False},
        'OBS_INPUT_FILE_REGEX' : {'sec' : 'regex_pattern', 'alt' : 'OBS_POINT_STAT_INPUT_TEMPLATE', 'copy': False},
        'PREPBUFR_DATA_DIR' : {'sec' : 'dir', 'alt' : 'PB2NC_INPUT_DIR'},
        'PREPBUFR_MODEL_DIR_NAME' : {'sec' : 'dir', 'alt' : 'PB2NC_INPUT_DIR', 'copy': False},
        'OBS_INPUT_FILE_TMPL' :
        {'sec' : 'filename_templates', 'alt' : 'OBS_POINT_STAT_INPUT_TEMPLATE'},
        'FCST_INPUT_FILE_TMPL' :
        {'sec' : 'filename_templates', 'alt' : 'FCST_POINT_STAT_INPUT_TEMPLATE'},
        'NC_FILE_TMPL' : {'sec' : 'filename_templates', 'alt' : 'PB2NC_OUTPUT_TEMPLATE'},
        'FCST_INPUT_DIR' : {'sec' : 'dir', 'alt' : 'FCST_POINT_STAT_INPUT_DIR'},
        'OBS_INPUT_DIR' : {'sec' : 'dir', 'alt' : 'OBS_POINT_STAT_INPUT_DIR'},
        'REGRID_TO_GRID' : {'sec' : 'config', 'alt' : 'POINT_STAT_REGRID_TO_GRID'},
        'FCST_HR_START' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'FCST_HR_END' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'FCST_HR_INTERVAL' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'START_DATE' : {'sec' : 'config', 'alt' : 'INIT_BEG or VALID_BEG', 'copy': False},
        'END_DATE' : {'sec' : 'config', 'alt' : 'INIT_END or VALID_END', 'copy': False},
        'INTERVAL_TIME' : {'sec' : 'config', 'alt' : 'INIT_INCREMENT or VALID_INCREMENT', 'copy': False},
        'BEG_TIME' : {'sec' : 'config', 'alt' : 'INIT_BEG or VALID_BEG', 'copy': False},
        'END_TIME' : {'sec' : 'config', 'alt' : 'INIT_END or VALID_END', 'copy': False},
        'START_HOUR' : {'sec' : 'config', 'alt' : 'INIT_BEG or VALID_BEG', 'copy': False},
        'END_HOUR' : {'sec' : 'config', 'alt' : 'INIT_END or VALID_END', 'copy': False},
        'OBS_BUFR_VAR_LIST' : {'sec' : 'config', 'alt' : 'PB2NC_OBS_BUFR_VAR_LIST'},
        'TIME_SUMMARY_FLAG' : {'sec' : 'config', 'alt' : 'PB2NC_TIME_SUMMARY_FLAG'},
        'TIME_SUMMARY_BEG' : {'sec' : 'config', 'alt' : 'PB2NC_TIME_SUMMARY_BEG'},
        'TIME_SUMMARY_END' : {'sec' : 'config', 'alt' : 'PB2NC_TIME_SUMMARY_END'},
        'TIME_SUMMARY_VAR_NAMES' : {'sec' : 'config', 'alt' : 'PB2NC_TIME_SUMMARY_VAR_NAMES'},
        'TIME_SUMMARY_TYPE' : {'sec' : 'config', 'alt' : 'PB2NC_TIME_SUMMARY_TYPE'},
        'OVERWRITE_NC_OUTPUT' : {'sec' : 'config', 'alt' : 'PB2NC_SKIP_IF_OUTPUT_EXISTS', 'copy': False},
        'VERTICAL_LOCATION' : {'sec' : 'config', 'alt' : 'PB2NC_VERTICAL_LOCATION'},
        'VERIFICATION_GRID' : {'sec' : 'config', 'alt' : 'REGRID_DATA_PLANE_VERIF_GRID'},
        'WINDOW_RANGE_BEG' : {'sec' : 'config', 'alt' : 'OBS_WINDOW_BEGIN'},
        'WINDOW_RANGE_END' : {'sec' : 'config', 'alt' : 'OBS_WINDOW_END'},
        'OBS_EXACT_VALID_TIME' :
        {'sec' : 'config', 'alt' : 'OBS_WINDOW_BEGIN and OBS_WINDOW_END', 'copy': False},
        'FCST_EXACT_VALID_TIME' :
        {'sec' : 'config', 'alt' : 'FCST_WINDOW_BEGIN and FCST_WINDOW_END', 'copy': False},
        'PCP_COMBINE_METHOD' :
        {'sec' : 'config', 'alt' : 'FCST_PCP_COMBINE_METHOD and/or OBS_PCP_COMBINE_METHOD', 'copy': False},
        'FHR_BEG' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'FHR_END' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'FHR_INC' : {'sec' : 'config', 'alt' : 'LEAD_SEQ', 'copy': False},
        'FHR_GROUP_BEG' : {'sec' : 'config', 'alt' : 'LEAD_SEQ_[N]', 'copy': False},
        'FHR_GROUP_END' : {'sec' : 'config', 'alt' : 'LEAD_SEQ_[N]', 'copy': False},
        'FHR_GROUP_LABELS' : {'sec' : 'config', 'alt' : 'LEAD_SEQ_[N]_LABEL', 'copy': False},
        'CYCLONE_OUT_DIR' : {'sec' : 'dir', 'alt' : 'CYCLONE_OUTPUT_DIR'},
        'ENSEMBLE_STAT_OUT_DIR' : {'sec' : 'dir', 'alt' : 'ENSEMBLE_STAT_OUTPUT_DIR'},
        'EXTRACT_OUT_DIR' : {'sec' : 'dir', 'alt' : 'EXTRACT_TILES_OUTPUT_DIR'},
        'GRID_STAT_OUT_DIR' : {'sec' : 'dir', 'alt' : 'GRID_STAT_OUTPUT_DIR'},
        'MODE_OUT_DIR' : {'sec' : 'dir', 'alt' : 'MODE_OUTPUT_DIR'},
        'MTD_OUT_DIR' : {'sec' : 'dir', 'alt' : 'MTD_OUTPUT_DIR'},
        'SERIES_INIT_OUT_DIR' : {'sec' : 'dir', 'alt' : 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_LEAD_OUT_DIR' : {'sec' : 'dir', 'alt' : 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_INIT_FILTERED_OUT_DIR' :
        {'sec' : 'dir', 'alt' : 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'SERIES_LEAD_FILTERED_OUT_DIR' :
        {'sec' : 'dir', 'alt' : 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'STAT_ANALYSIS_OUT_DIR' :
        {'sec' : 'dir', 'alt' : 'STAT_ANALYSIS_OUTPUT_DIR'},
        'TCMPR_PLOT_OUT_DIR' : {'sec' : 'dir', 'alt' : 'TCMPR_PLOT_OUTPUT_DIR'},
        'FCST_MIN_FORECAST' : {'sec' : 'config', 'alt' : 'LEAD_SEQ_MIN'},
        'FCST_MAX_FORECAST' : {'sec' : 'config', 'alt' : 'LEAD_SEQ_MAX'},
        'OBS_MIN_FORECAST' : {'sec' : 'config', 'alt' : 'OBS_PCP_COMBINE_MIN_LEAD'},
        'OBS_MAX_FORECAST' : {'sec' : 'config', 'alt' : 'OBS_PCP_COMBINE_MAX_LEAD'},
        'FCST_INIT_INTERVAL' : {'sec' : 'config', 'alt' : None},
        'OBS_INIT_INTERVAL' : {'sec' : 'config', 'alt' : None},
        'FCST_DATA_INTERVAL' : {'sec' : '', 'alt' : 'FCST_PCP_COMBINE_DATA_INTERVAL'},
        'OBS_DATA_INTERVAL' : {'sec' : '', 'alt' : 'OBS_PCP_COMBINE_DATA_INTERVAL'},
        'FCST_IS_DAILY_FILE' : {'sec' : '', 'alt' : 'FCST_PCP_COMBINE_IS_DAILY_FILE'},
        'OBS_IS_DAILY_FILE' : {'sec' : '', 'alt' : 'OBS_PCP_COMBINE_IS_DAILY_FILE'},
        'FCST_TIMES_PER_FILE' : {'sec' : '', 'alt' : 'FCST_PCP_COMBINE_TIMES_PER_FILE'},
        'OBS_TIMES_PER_FILE' : {'sec' : '', 'alt' : 'OBS_PCP_COMBINE_TIMES_PER_FILE'},
        'FCST_LEVEL' : {'sec' : '', 'alt' : 'FCST_PCP_COMBINE_INPUT_ACCUMS', 'copy': False},
        'OBS_LEVEL' : {'sec' : '', 'alt' : 'OBS_PCP_COMBINE_INPUT_ACCUMS', 'copy': False},
        'MODE_FCST_CONV_RADIUS' : {'sec' : 'config', 'alt' : 'FCST_MODE_CONV_RADIUS'},
        'MODE_FCST_CONV_THRESH' : {'sec' : 'config', 'alt' : 'FCST_MODE_CONV_THRESH'},
        'MODE_FCST_MERGE_FLAG' : {'sec' : 'config', 'alt' : 'FCST_MODE_MERGE_FLAG'},
        'MODE_FCST_MERGE_THRESH' : {'sec' : 'config', 'alt' : 'FCST_MODE_MERGE_THRESH'},
        'MODE_OBS_CONV_RADIUS' : {'sec' : 'config', 'alt' : 'OBS_MODE_CONV_RADIUS'},
        'MODE_OBS_CONV_THRESH' : {'sec' : 'config', 'alt' : 'OBS_MODE_CONV_THRESH'},
        'MODE_OBS_MERGE_FLAG' : {'sec' : 'config', 'alt' : 'OBS_MODE_MERGE_FLAG'},
        'MODE_OBS_MERGE_THRESH' : {'sec' : 'config', 'alt' : 'OBS_MODE_MERGE_THRESH'},
        'MTD_FCST_CONV_RADIUS' : {'sec' : 'config', 'alt' : 'FCST_MTD_CONV_RADIUS'},
        'MTD_FCST_CONV_THRESH' : {'sec' : 'config', 'alt' : 'FCST_MTD_CONV_THRESH'},
        'MTD_OBS_CONV_RADIUS' : {'sec' : 'config', 'alt' : 'OBS_MTD_CONV_RADIUS'},
        'MTD_OBS_CONV_THRESH' : {'sec' : 'config', 'alt' : 'OBS_MTD_CONV_THRESH'},
        'RM_EXE' : {'sec' : 'exe', 'alt' : 'RM'},
        'CUT_EXE' : {'sec' : 'exe', 'alt' : 'CUT'},
        'TR_EXE' : {'sec' : 'exe', 'alt' : 'TR'},
        'NCAP2_EXE' : {'sec' : 'exe', 'alt' : 'NCAP2'},
        'CONVERT_EXE' : {'sec' : 'exe', 'alt' : 'CONVERT'},
        'NCDUMP_EXE' : {'sec' : 'exe', 'alt' : 'NCDUMP'},
        'EGREP_EXE' : {'sec' : 'exe', 'alt' : 'EGREP'},
        'ADECK_TRACK_DATA_DIR' : {'sec' : 'dir', 'alt' : 'TC_PAIRS_ADECK_INPUT_DIR'},
        'BDECK_TRACK_DATA_DIR' : {'sec' : 'dir', 'alt' : 'TC_PAIRS_BDECK_INPUT_DIR'},
        'MISSING_VAL_TO_REPLACE' : {'sec' : 'config', 'alt' : 'TC_PAIRS_MISSING_VAL_TO_REPLACE'},
        'MISSING_VAL' : {'sec' : 'config', 'alt' : 'TC_PAIRS_MISSING_VAL'},
        'TRACK_DATA_SUBDIR_MOD' : {'sec' : 'dir', 'alt' : None},
        'ADECK_FILE_PREFIX' : {'sec' : 'config', 'alt' : 'TC_PAIRS_ADECK_TEMPLATE', 'copy': False},
        'BDECK_FILE_PREFIX' : {'sec' : 'config', 'alt' : 'TC_PAIRS_BDECK_TEMPLATE', 'copy': False},
        'TOP_LEVEL_DIRS' : {'sec' : 'config', 'alt' : 'TC_PAIRS_READ_ALL_FILES'},
        'TC_PAIRS_DIR' : {'sec' : 'dir', 'alt' : 'TC_PAIRS_OUTPUT_DIR'},
        'CYCLONE' : {'sec' : 'config', 'alt' : 'TC_PAIRS_CYCLONE'},
        'STORM_ID' : {'sec' : 'config', 'alt' : 'TC_PAIRS_STORM_ID'},
        'BASIN' : {'sec' : 'config', 'alt' : 'TC_PAIRS_BASIN'},
        'STORM_NAME' : {'sec' : 'config', 'alt' : 'TC_PAIRS_STORM_NAME'},
        'DLAND_FILE' : {'sec' : 'config', 'alt' : 'TC_PAIRS_DLAND_FILE'},
        'TRACK_TYPE' : {'sec' : 'config', 'alt' : 'TC_PAIRS_REFORMAT_DECK'},
        'FORECAST_TMPL' : {'sec' : 'filename_templates', 'alt' : 'TC_PAIRS_ADECK_TEMPLATE'},
        'REFERENCE_TMPL' : {'sec' : 'filename_templates', 'alt' : 'TC_PAIRS_BDECK_TEMPLATE'},
        'TRACK_DATA_MOD_FORCE_OVERWRITE' :
        {'sec' : 'config', 'alt' : 'TC_PAIRS_SKIP_IF_REFORMAT_EXISTS', 'copy': False},
        'TC_PAIRS_FORCE_OVERWRITE' : {'sec' : 'config', 'alt' : 'TC_PAIRS_SKIP_IF_OUTPUT_EXISTS', 'copy': False},
        'GRID_STAT_CONFIG' : {'sec' : 'config', 'alt' : 'GRID_STAT_CONFIG_FILE'},
        'MODE_CONFIG' : {'sec' : 'config', 'alt': 'MODE_CONFIG_FILE'},
        'FCST_PCP_COMBINE_INPUT_LEVEL': {'sec': 'config', 'alt' : 'FCST_PCP_COMBINE_INPUT_ACCUMS'},
        'OBS_PCP_COMBINE_INPUT_LEVEL': {'sec': 'config', 'alt' : 'OBS_PCP_COMBINE_INPUT_ACCUMS'},
        'TIME_METHOD': {'sec': 'config', 'alt': 'LOOP_BY', 'copy': False},
        'MODEL_DATA_DIR': {'sec': 'dir', 'alt': 'EXTRACT_TILES_GRID_INPUT_DIR'},
        'STAT_LIST': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_STAT_LIST'},
        'NLAT': {'sec': 'config', 'alt': 'EXTRACT_TILES_NLAT'},
        'NLON': {'sec': 'config', 'alt': 'EXTRACT_TILES_NLON'},
        'DLAT': {'sec': 'config', 'alt': 'EXTRACT_TILES_DLAT'},
        'DLON': {'sec': 'config', 'alt': 'EXTRACT_TILES_DLON'},
        'LON_ADJ': {'sec': 'config', 'alt': 'EXTRACT_TILES_LON_ADJ'},
        'LAT_ADJ': {'sec': 'config', 'alt': 'EXTRACT_TILES_LAT_ADJ'},
        'OVERWRITE_TRACK': {'sec': 'config', 'alt': 'EXTRACT_TILES_OVERWRITE_TRACK'},
        'BACKGROUND_MAP': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_BACKGROUND_MAP'},
        'GFS_FCST_FILE_TMPL': {'sec': 'filename_templates', 'alt': 'FCST_EXTRACT_TILES_INPUT_TEMPLATE'},
        'GFS_ANLY_FILE_TMPL': {'sec': 'filename_templates', 'alt': 'OBS_EXTRACT_TILES_INPUT_TEMPLATE'},
        'FCST_TILE_PREFIX': {'sec': 'regex_patterns', 'alt': 'FCST_EXTRACT_TILES_PREFIX'},
        'OBS_TILE_PREFIX': {'sec': 'regex_patterns', 'alt': 'OBS_EXTRACT_TILES_PREFIX'},
        'FCST_TILE_REGEX': {'sec': 'regex_patterns', 'alt': None},
        'OBS_TILE_REGEX': {'sec': 'regex_patterns', 'alt': None},
        'FCST_NC_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'FCST_SERIES_ANALYSIS_NC_TILE_REGEX'},
        'ANLY_NC_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'OBS_SERIES_ANALYSIS_NC_TILE_REGEX'},
        'FCST_ASCII_REGEX_LEAD': {'sec': 'regex_patterns', 'alt': 'FCST_SERIES_ANALYSIS_ASCII_REGEX_LEAD'},
        'ANLY_ASCII_REGEX_LEAD': {'sec': 'regex_patterns', 'alt': 'OBS_SERIES_ANALYSIS_ASCII_REGEX_LEAD'},
        'SERIES_BY_LEAD_FILTERED_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'SERIES_BY_INIT_FILTERED_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'SERIES_BY_LEAD_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_BY_INIT_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_BY_LEAD_GROUP_FCSTS': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_GROUP_FCSTS'},
        'SERIES_ANALYSIS_BY_LEAD_CONFIG_FILE': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_CONFIG_FILE'},
        'SERIES_ANALYSIS_BY_INIT_CONFIG_FILE': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_CONFIG_FILE'},
        'ENSEMBLE_STAT_MET_OBS_ERROR_TABLE': {'sec': 'config', 'alt': 'ENSEMBLE_STAT_MET_OBS_ERR_TABLE'},
        'VAR_LIST': {'sec': 'config', 'alt': 'BOTH_VAR<n>_NAME BOTH_VAR<n>_LEVELS or SERIES_ANALYSIS_VAR_LIST', 'copy': False},
        'SERIES_ANALYSIS_VAR_LIST': {'sec': 'config', 'alt': 'BOTH_VAR<n>_NAME BOTH_VAR<n>_LEVELS', 'copy': False},
        'EXTRACT_TILES_VAR_LIST': {'sec': 'config', 'alt': ''},
        'STAT_ANALYSIS_LOOKIN_DIR': {'sec': 'dir', 'alt': 'MODEL1_STAT_ANALYSIS_LOOKIN_DIR'},
        'VALID_HOUR_METHOD': {'sec': 'config', 'alt': None},
        'VALID_HOUR_BEG': {'sec': 'config', 'alt': None},
        'VALID_HOUR_END': {'sec': 'config', 'alt': None},
        'VALID_HOUR_INCREMENT': {'sec': 'config', 'alt': None},
        'INIT_HOUR_METHOD': {'sec': 'config', 'alt': None},
        'INIT_HOUR_BEG': {'sec': 'config', 'alt': None},
        'INIT_HOUR_END': {'sec': 'config', 'alt': None},
        'INIT_HOUR_INCREMENT': {'sec': 'config', 'alt': None},
        'STAT_ANALYSIS_CONFIG': {'sec': 'config', 'alt': 'STAT_ANALYSIS_CONFIG_FILE'},
        'JOB_NAME': {'sec': 'config', 'alt': 'STAT_ANALYSIS_JOB_NAME'},
        'JOB_ARGS': {'sec': 'config', 'alt': 'STAT_ANALYSIS_JOB_ARGS'},
        'DESC': {'sec': 'config', 'alt': 'DESC_LIST'},
        'FCST_LEAD': {'sec': 'config', 'alt': 'FCST_LEAD_LIST'},
        'FCST_VAR_NAME': {'sec': 'config', 'alt': 'FCST_VAR_LIST'},
        'FCST_VAR_LEVEL': {'sec': 'config', 'alt': 'FCST_VAR_LEVEL_LIST'},
        'OBS_VAR_NAME': {'sec': 'config', 'alt': 'OBS_VAR_LIST'},
        'OBS_VAR_LEVEL': {'sec': 'config', 'alt': 'OBS_VAR_LEVEL_LIST'},
        'REGION': {'sec': 'config', 'alt': 'VX_MASK_LIST'},
        'INTERP': {'sec': 'config', 'alt': 'INTERP_LIST'},
        'INTERP_PTS': {'sec': 'config', 'alt': 'INTERP_PTS_LIST'},
        'CONV_THRESH': {'sec': 'config', 'alt': 'CONV_THRESH_LIST'},
        'FCST_THRESH': {'sec': 'config', 'alt': 'FCST_THRESH_LIST'},
        'LINE_TYPE': {'sec': 'config', 'alt': 'LINE_TYPE_LIST'},
        'STAT_ANALYSIS_DUMP_ROW_TMPL': {'sec': 'filename_templates', 'alt': 'STAT_ANALYSIS_DUMP_ROW_TEMPLATE'},
        'STAT_ANALYSIS_OUT_STAT_TMPL': {'sec': 'filename_templates', 'alt': 'STAT_ANALYSIS_OUT_STAT_TEMPLATE'},
        'PLOTTING_SCRIPTS_DIR': {'sec': 'dir', 'alt': 'MAKE_PLOTS_SCRIPTS_DIR'},
        'STAT_FILES_INPUT_DIR': {'sec': 'dir', 'alt': 'MAKE_PLOTS_INPUT_DIR'},
        'PLOTTING_OUTPUT_DIR': {'sec': 'dir', 'alt': 'MAKE_PLOTS_OUTPUT_DIR'},
        'VERIF_CASE': {'sec': 'config', 'alt': 'MAKE_PLOTS_VERIF_CASE'},
        'VERIF_TYPE': {'sec': 'config', 'alt': 'MAKE_PLOTS_VERIF_TYPE'},
        'PLOT_TIME': {'sec': 'config', 'alt': 'DATE_TIME'},
        'MODEL<n>_NAME': {'sec': 'config', 'alt': 'MODEL<n>'},
        'MODEL<n>_OBS_NAME': {'sec': 'config', 'alt': 'MODEL<n>_OBTYPE'},
        'MODEL<n>_STAT_DIR': {'sec': 'dir', 'alt': 'MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR'},
        'MODEL<n>_NAME_ON_PLOT': {'sec': 'config', 'alt': 'MODEL<n>_REFERENCE_NAME'},
        'REGION_LIST': {'sec': 'config', 'alt': 'VX_MASK_LIST'},
        'PLOT_STATS_LIST': {'sec': 'config', 'alt': 'MAKE_PLOT_STATS_LIST'},
        'CI_METHOD': {'sec': 'config', 'alt': 'MAKE_PLOTS_CI_METHOD'},
        'VERIF_GRID': {'sec': 'config', 'alt': 'MAKE_PLOTS_VERIF_GRID'},
        'EVENT_EQUALIZATION': {'sec': 'config', 'alt': 'MAKE_PLOTS_EVENT_EQUALIZATION'},
        'MTD_CONFIG': {'sec': 'config', 'alt': 'MTD_CONFIG_FILE'},
        'CLIMO_GRID_STAT_INPUT_DIR': {'sec': 'dir', 'alt': 'GRID_STAT_CLIMO_MEAN_INPUT_DIR'},
        'CLIMO_GRID_STAT_INPUT_TEMPLATE': {'sec': 'filename_templates', 'alt': 'GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE'},
        'CLIMO_POINT_STAT_INPUT_DIR': {'sec': 'dir', 'alt': 'POINT_STAT_CLIMO_MEAN_INPUT_DIR'},
        'CLIMO_POINT_STAT_INPUT_TEMPLATE': {'sec': 'filename_templates', 'alt': 'POINT_STAT_CLIMO_MEAN_INPUT_TEMPLATE'},
        'GEMPAKTOCF_CLASSPATH': {'sec': 'exe', 'alt': 'GEMPAKTOCF_JAR', 'copy': False},
        'CUSTOM_INGEST_<n>_OUTPUT_DIR': {'sec': 'dir', 'alt': 'PY_EMBED_INGEST_<n>_OUTPUT_DIR'},
        'CUSTOM_INGEST_<n>_OUTPUT_TEMPLATE': {'sec': 'filename_templates', 'alt': 'PY_EMBED_INGEST_<n>_OUTPUT_TEMPLATE'},
        'CUSTOM_INGEST_<n>_OUTPUT_GRID': {'sec': 'config', 'alt': 'PY_EMBED_INGEST_<n>_OUTPUT_GRID'},
        'CUSTOM_INGEST_<n>_SCRIPT': {'sec': 'config', 'alt': 'PY_EMBED_INGEST_<n>_SCRIPT'},
        'CUSTOM_INGEST_<n>_TYPE': {'sec': 'config', 'alt': 'PY_EMBED_INGEST_<n>_TYPE'},
        'TC_STAT_RUN_VIA': {'sec': 'config', 'alt': 'TC_STAT_CONFIG_FILE',
                            'copy': False},
        'TC_STAT_CMD_LINE_JOB': {'sec': 'config', 'alt': 'TC_STAT_JOB_ARGS'},
        'TC_STAT_JOBS_LIST': {'sec': 'config', 'alt': 'TC_STAT_JOB_ARGS'},
        'EXTRACT_TILES_OVERWRITE_TRACK': {'sec': 'config',
                                          'alt': 'EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS',
                                          'copy': False},
        'INIT_INCLUDE': {'sec': 'config', 'alt': 'TC_PAIRS_INIT_INCLUDE'},
        'INIT_EXCLUDE': {'sec': 'config', 'alt': 'TC_PAIRS_INIT_EXCLUDE'},
        'EXTRACT_TILES_PAIRS_INPUT_DIR': {'sec': 'dir',
                                          'alt': 'EXTRACT_TILES_STAT_INPUT_DIR',
                                          'copy': False},
        'EXTRACT_TILES_FILTERED_OUTPUT_TEMPLATE': {'sec': 'filename_template',
                                                   'alt': 'EXTRACT_TILES_STAT_INPUT_TEMPLATE',},
        'EXTRACT_TILES_GRID_INPUT_DIR': {'sec': 'dir',
                                         'alt': 'FCST_EXTRACT_TILES_INPUT_DIR'
                                                'and '
                                                'OBS_EXTRACT_TILES_INPUT_DIR',
                                         'copy': False},
#        'SERIES_ANALYSIS_FILTER_OPTS': {'sec': 'config',
#                                        'alt': 'TC_STAT_JOB_ARGS',
#                                        'copy': False},
        'TC_STAT_INPUT_DIR': {'sec': 'dir',
                              'alt': 'TC_STAT_LOOKIN_DIR'},
        'SERIES_ANALYSIS_INPUT_DIR': {'sec': 'dir',
                              'alt': 'SERIES_ANALYSIS_TILE_INPUT_DIR'},
#        'FCST_SERIES_ANALYSIS_TILE_REGEX': {'sec': 'config',
#                                        'alt': 'FCST_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
#        'OBS_SERIES_ANALYSIS_TILE_REGEX': {'sec': 'config',
#                                        'alt': 'OBS_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
#        'FCST_SERIES_ANALYSIS_NC_TILE_REGEX': {'sec': 'config',
#                                        'alt': 'FCST_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
#        'OBS_SERIES_ANALYSIS_NC_TILE_REGEX': {'sec': 'config',
#                                        'alt': 'OBS_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
#        'FCST_SERIES_ANALYSIS_ASCII_REGEX_LEAD': {'sec': 'config',
#                                        'alt': 'FCST_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
#        'OBS_SERIES_ANALYSIS_ASCII_REGEX_LEAD': {'sec': 'config',
#                                        'alt': 'OBS_EXTRACT_TILES_PREFIX',
#                                        'copy': False},
    }

    # template       '' : {'sec' : '', 'alt' : '', 'copy': True},

    logger = config.logger

    # create list of errors and warnings to report for deprecated configs
    e_list = []
    w_list = []
    all_sed_cmds = []

    for old, depr_info in deprecated_dict.items():
        if isinstance(depr_info, dict):

            # check if <n> is found in the old item, use regex to find variables if found
            if '<n>' in old:
                old_regex = old.replace('<n>', r'(\d+)')
                indicies = find_indices_in_config_section(old_regex,
                                                          config,
                                                          'config',
                                                          noID=True).keys()
                for index in indicies:
                    old_with_index = old.replace('<n>', index)
                    if depr_info['alt']:
                        alt_with_index = depr_info['alt'].replace('<n>', index)
                    else:
                        alt_with_index = ''

                    handle_deprecated(old_with_index, alt_with_index, depr_info,
                                      config, all_sed_cmds, w_list, e_list)
            else:
                handle_deprecated(old, depr_info['alt'], depr_info,
                                  config, all_sed_cmds, w_list, e_list)


    # check all templates and error if any deprecated tags are used
    # value of dict is replacement tag, set to None if no replacement exists
    # deprecated tags: region (replace with basin)
    deprecated_tags = {'region' : 'basin'}
    template_vars = config.keys('config')
    template_vars = [tvar for tvar in template_vars if tvar.endswith('_TEMPLATE')]
    for temp_var in template_vars:
        template = config.getraw('filename_templates', temp_var)
        tags = get_tags(template)

        for depr_tag, replace_tag in deprecated_tags.items():
            if depr_tag in tags:
                e_msg = 'Deprecated tag {{{}}} found in {}.'.format(depr_tag,
                                                                    temp_var)
                if replace_tag is not None:
                    e_msg += ' Replace with {{{}}}'.format(replace_tag)

                e_list.append(e_msg)

    # if any warning exist, report them
    if w_list:
        for warning_msg in w_list:
            logger.warning(warning_msg)

    # if any errors exist, report them and exit
    if e_list:
        logger.error('DEPRECATED CONFIG ITEMS WERE FOUND. ' +\
                     'PLEASE REMOVE/REPLACE THEM FROM CONFIG FILES')
        for error_msg in e_list:
            logger.error(error_msg)
        return False, all_sed_cmds

    return True, []

def handle_deprecated(old, alt, depr_info, config, all_sed_cmds, w_list, e_list):
    sec = depr_info['sec']
    config_files = config.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
    # if deprecated config item is found
    if config.has_option(sec, old):
        # if it is not required to remove, add to warning list
        if 'req' in depr_info.keys() and depr_info['req'] is False:
            msg = '[{}] {} is deprecated and will be '.format(sec, old) + \
                  'removed in a future version of METplus'
            if alt:
                msg += ". Please replace with {}".format(alt)
            w_list.append(msg)
        # if it is required to remove, add to error list
        else:
            if not alt:
                e_list.append("[{}] {} should be removed".format(sec, old))
            else:
                e_list.append("[{}] {} should be replaced with {}".format(sec, old, alt))

                if 'copy' not in depr_info.keys() or depr_info['copy']:
                    for config_file in config_files:
                        all_sed_cmds.append(f"sed -i 's|^{old}|{alt}|g' {config_file}")
                        all_sed_cmds.append(f"sed -i 's|{{{old}}}|{{{alt}}}|g' {config_file}")

def check_for_deprecated_met_config(config):
    sed_cmds = []
    all_good = True

    # set CURRENT_* METplus variables in case they are referenced in a
    # METplus config variable and not already set
    current_vars = ['CURRENT_FCST_NAME',
                    'CURRENT_OBS_NAME',
                    'CURRENT_FCST_LEVEL',
                    'CURRENT_OBS_LEVEL',
                   ]
    for current_var in current_vars:
        if not config.has_option('config', current_var):
            config.set('config', current_var, '')

    # check if *_CONFIG_FILE if set in the METplus config file and check for
    # deprecated environment variables in those files
    met_config_keys = [key for key in config.keys('config') if key.endswith('CONFIG_FILE')]

    for met_config_key in met_config_keys:
        met_tool = met_config_key.replace('_CONFIG_FILE', '')

        # get custom loop list to check if multiple config files are used based on the custom string
        custom_list = get_custom_string_list(config, met_tool)

        for custom_string in custom_list:
            met_config = config.getraw('config', met_config_key)
            if not met_config:
                continue

            met_config_file = do_string_sub(met_config, custom=custom_string)

            if not check_for_deprecated_met_config_file(config, met_config_file, sed_cmds, met_tool):
                all_good = False

    return all_good, sed_cmds

def check_for_deprecated_met_config_file(config, met_config, sed_cmds, met_tool):

    all_good = True
    if not os.path.exists(met_config):
        config.logger.error(f"Config file does not exist: {met_config}")
        return False

    deprecated_met_list = ['MET_VALID_HHMM', 'GRID_VX', 'CONFIG_DIR']
    deprecated_output_prefix_list = ['FCST_VAR', 'OBS_VAR']
    config.logger.debug(f"Checking for deprecated environment variables in: {met_config}")

    with open(met_config, 'r') as f:
        for line in f:

            for deprecated_item in deprecated_met_list:
                if '${' + deprecated_item + '}' in line:
                    all_good = False
                    config.logger.error("Please remove deprecated environment variable "
                                        f"${{{deprecated_item}}} found in MET config file: "
                                        f"{met_config}")

                    if deprecated_item == 'MET_VALID_HHMM' and 'file_name' in line:
                        config.logger.error(f"Set {met_tool}_CLIMO_MEAN_INPUT_[DIR/TEMPLATE] in a "
                                            "METplus config file to set CLIMO_MEAN_FILE in a MET config")
                        new_line = "   file_name = [ ${CLIMO_MEAN_FILE} ];"

                        # escape [ and ] because they are special characters in sed commands
                        old_line = line.rstrip().replace('[', r'\[').replace(']', r'\]')

                        sed_cmds.append(f"sed -i 's|^{old_line}|{new_line}|g' {met_config}")
                        add_line = f"{met_tool}_CLIMO_MEAN_INPUT_TEMPLATE"
                        sed_cmds.append(f"#Add {add_line}")
                        break

                    if 'to_grid' in line:
                        config.logger.error("MET to_grid variable should reference "
                                            "${REGRID_TO_GRID} environment variable")
                        new_line = "   to_grid    = ${REGRID_TO_GRID};"

                        # escape [ and ] because they are special characters in sed commands
                        old_line = line.rstrip().replace('[', r'\[').replace(']', r'\]')

                        sed_cmds.append(f"sed -i 's|^{old_line}|{new_line}|g' {met_config}")
                        config.logger.info(f"Be sure to set {met_tool}_REGRID_TO_GRID to the correct value.")
                        add_line = f"{met_tool}_REGRID_TO_GRID"
                        sed_cmds.append(f"#Add {add_line}")
                        break


            for deprecated_item in deprecated_output_prefix_list:
                # if deprecated item found in output prefix or to_grid line, replace line to use
                # env var OUTPUT_PREFIX or REGRID_TO_GRID
                if '${' + deprecated_item + '}' in line and 'output_prefix' in line:
                    config.logger.error("output_prefix variable should reference "
                                        "${OUTPUT_PREFIX} environment variable")
                    new_line = "output_prefix    = \"${OUTPUT_PREFIX}\";"

                    # escape [ and ] because they are special characters in sed commands
                    old_line = line.rstrip().replace('[', r'\[').replace(']', r'\]')

                    sed_cmds.append(f"sed -i 's|^{old_line}|{new_line}|g' {met_config}")
                    config.logger.info(f"You will need to add {met_tool}_OUTPUT_PREFIX to the METplus config file"
                                       f" that sets {met_tool}_CONFIG_FILE. Set it to:")
                    output_prefix = replace_output_prefix(line)
                    add_line = f"{met_tool}_OUTPUT_PREFIX = {output_prefix}"
                    config.logger.info(add_line)
                    sed_cmds.append(f"#Add {add_line}")
                    all_good = False
                    break

    return all_good

def replace_output_prefix(line):
    op_replacements = {'${MODEL}': '{MODEL}',
                       '${FCST_VAR}': '{CURRENT_FCST_NAME}',
                       '${OBTYPE}': '{OBTYPE}',
                       '${OBS_VAR}': '{CURRENT_OBS_NAME}',
                       '${LEVEL}': '{CURRENT_FCST_LEVEL}',
                       '${FCST_TIME}': '{lead?fmt=%3H}',
                       }
    prefix = line.split('=')[1].strip().rstrip(';').strip('"')
    for key, value, in op_replacements.items():
        prefix = prefix.replace(key, value)

    return prefix

def get_custom_string_list(config, met_tool):
    custom_loop_list = config.getstr_nocheck('config',
                                             f'{met_tool.upper()}_CUSTOM_LOOP_LIST',
                                             config.getstr_nocheck('config',
                                                                   'CUSTOM_LOOP_LIST',
                                                                   ''))
    custom_loop_list = getlist(custom_loop_list)
    if not custom_loop_list:
        custom_loop_list.append('')

    return custom_loop_list

def handle_tmp_dir(config):
    """! if env var MET_TMP_DIR is set, override config TMP_DIR with value
     if it differs from what is set
     get config temp dir using getdir_nocheck to bypass check for /path/to
     this is done so the user can set env MET_TMP_DIR instead of config TMP_DIR
     and config TMP_DIR will be set automatically"""
    met_tmp_dir = os.environ.get('MET_TMP_DIR', '')
    conf_tmp_dir = config.getdir_nocheck('TMP_DIR', '')

    # if env MET_TMP_DIR is set
    if met_tmp_dir:
        # override config TMP_DIR to env MET_TMP_DIR value
        config.set('config', 'TMP_DIR', met_tmp_dir)

        # if config TMP_DIR differed from env MET_TMP_DIR, warn
        if conf_tmp_dir != met_tmp_dir:
            msg = 'TMP_DIR in config will be overridden by the ' +\
                'environment variable MET_TMP_DIR ({})'.format(met_tmp_dir)
            config.logger.warning(msg)

    # create temp dir if it doesn't exist already
    # this will fail if TMP_DIR is not set correctly and
    # env MET_TMP_DIR was not set
    tmp_dir = config.getdir('TMP_DIR')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

def get_skip_times(config, wrapper_name=None):
    """! Read SKIP_TIMES config variable and populate dictionary of times that should be skipped.
         SKIP_TIMES should be in the format: "%m:begin_end_incr(3,11,1)", "%d:30,31", "%Y%m%d:20201031"
         where each item inside quotes is a datetime format, colon, then a list of times in that format
         to skip.
         Args:
             @param config configuration object to pull SKIP_TIMES
             @param wrapper_name name of wrapper if supporting
               skipping times only for certain wrappers, i.e. grid_stat
             @returns dictionary containing times to skip
    """
    skip_times_dict = {}
    skip_times_string = None

    # if wrapper name is set, look for wrapper-specific _SKIP_TIMES variable
    if wrapper_name:
        skip_times_string = config.getstr('config',
                                          f'{wrapper_name.upper()}_SKIP_TIMES', '')

    # if skip times string has not been found, check for generic SKIP_TIMES
    if not skip_times_string:
        skip_times_string = config.getstr('config', 'SKIP_TIMES', '')

        # if no generic SKIP_TIMES, return empty dictionary
        if not skip_times_string:
            return {}

    # get list of skip items, but don't expand begin_end_incr yet
    skip_list = getlist(skip_times_string, expand_begin_end_incr=False)

    for skip_item in skip_list:
        try:
            time_format, skip_times = skip_item.split(':')

            # get list of skip times for the time format, expanding begin_end_incr
            skip_times_list = getlist(skip_times)

            # if time format is already in skip times dictionary, extend list
            if time_format in skip_times_dict:
                skip_times_dict[time_format].extend(skip_times_list)
            else:
                skip_times_dict[time_format] = skip_times_list

        except ValueError:
            config.logger.error(f"SKIP_TIMES item does not match format: {skip_item}")
            return None

    return skip_times_dict

def skip_time(time_info, skip_times):
    """!Used to check the valid time of the current run time against list of times to skip.
        Args:
            @param time_info dictionary with time information to check
            @param skip_times dictionary of times to skip, i.e. {'%d': [31]} means skip 31st day
            @returns True if run time should be skipped, False if not
    """
    for time_format, skip_time_list in skip_times.items():
        # extract time information from valid time based on skip time format
        run_time_value = time_info.get('valid')
        if not run_time_value:
            return False

        run_time_value = run_time_value.strftime(time_format)

        # loop over times to skip for this format and check if it matches
        for skip_time in skip_time_list:
            if int(run_time_value) == int(skip_time):
                return True

    # if skip time never matches, return False
    return False

def write_final_conf(config, logger):
    """!write final conf file including default values that were set during run"""
    confloc = config.getstr('config', 'METPLUS_CONF')
    logger.info('%s: write metplus.conf here' % (confloc,))
    with open(confloc, 'wt') as conf_file:
        config.write(conf_file)

    # write out os environment to file for debugging
    env_file = os.path.join(config.getdir('LOG_DIR'), '.metplus_user_env')
    with open(env_file, 'w') as env_file:
        for key, value in os.environ.items():
            env_file.write('{}={}\n'.format(key, value))

def is_loop_by_init(config):
    """!Check config variables to determine if looping by valid or init time"""
    if config.has_option('config', 'LOOP_BY'):
        loop_by = config.getstr('config', 'LOOP_BY').lower()
        if loop_by in ['init', 'retro']:
            return True
        elif loop_by in ['valid', 'realtime']:
            return False

    if config.has_option('config', 'LOOP_BY_INIT'):
        return config.getbool('config', 'LOOP_BY_INIT')

    msg = 'MUST SET LOOP_BY to VALID, INIT, RETRO, or REALTIME'
    if config.logger is None:
        print(msg)
    else:
        config.logger.error(msg)

    return None

def get_time_obj(time_from_conf, fmt, clock_time, logger=None):
    """!Substitute today or now into [INIT/VALID]_[BEG/END] if used
        Args:
            @param time_from_conf value from [INIT/VALID]_[BEG/END] that
                   may include now or today tags
            @param fmt format of time_from_conf, i.e. %Y%m%d
            @param clock_time datetime object for time when execution started
            @param logger log object to write error messages - None if not provided
            @returns datetime object if successful, None if not
    """
    time_str = do_string_sub(time_from_conf,
                             now=clock_time,
                             today=clock_time.strftime('%Y%m%d'))
    try:
        time_t = datetime.datetime.strptime(time_str, fmt)
    except ValueError:
        error_message = (f"[INIT/VALID]_TIME_FMT ({fmt}) does not match "
                         f"[INIT/VALID]_[BEG/END] ({time_str})")
        if logger:
            logger.error(error_message)
        else:
            print(f"ERROR: {error_message}")

        return None

    return time_t

def get_start_end_interval_times(config):
    clock_time_obj = datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                '%Y%m%d%H%M%S')
    use_init = is_loop_by_init(config)
    if use_init is None:
        return None

    if use_init:
        time_format = config.getstr('config', 'INIT_TIME_FMT')
        start_t = config.getraw('config', 'INIT_BEG')
        end_t = config.getraw('config', 'INIT_END')
        time_interval = time_util.get_relativedelta(config.getstr('config', 'INIT_INCREMENT'))
    else:
        time_format = config.getstr('config', 'VALID_TIME_FMT')
        start_t = config.getraw('config', 'VALID_BEG')
        end_t = config.getraw('config', 'VALID_END')
        time_interval = time_util.get_relativedelta(config.getstr('config', 'VALID_INCREMENT'))

    start_time = get_time_obj(start_t, time_format,
                             clock_time_obj, config.logger)
    if not start_time:
        config.logger.error("Could not format start time")
        return None

    end_time = get_time_obj(end_t, time_format,
                            clock_time_obj, config.logger)
    if not end_time:
        config.logger.error("Could not format end time")
        return None

    if start_time + time_interval < start_time + datetime.timedelta(seconds=60):
        config.logger.error("[INIT/VALID]_INCREMENT must be greater than or equal to 60 seconds")
        return None

    if start_time > end_time:
        config.logger.error("Start time must come before end time")
        return None

    return start_time, end_time, time_interval

def loop_over_times_and_call(config, processes):
    """! Loop over all run times and call wrappers listed in config

    @param config METplusConfig object
    @param processes list of CommandBuilder subclass objects (Wrappers) to call
    @returns list of tuples with all commands run and the environment variables
    that were set for each
    """
    clock_time_obj = datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                '%Y%m%d%H%M%S')
    use_init = is_loop_by_init(config)
    if use_init is None:
        return None

    # get start time, end time, and time interval from config
    loop_time, end_time, time_interval = get_start_end_interval_times(config) or (None, None, None)
    if not loop_time:
        config.logger.error("Could not get [INIT/VALID] time information from configuration file")
        return None

    # keep track of commands that were run
    all_commands = []
    while loop_time <= end_time:
        run_time = loop_time.strftime("%Y-%m-%d %H:%M")
        config.logger.info("****************************************")
        config.logger.info("* Running METplus")
        if use_init:
            config.logger.info("*  at init time: " + run_time)
        else:
            config.logger.info("*  at valid time: " + run_time)
        config.logger.info("****************************************")
        if not isinstance(processes, list):
            processes = [processes]
        for process in processes:
            input_dict = {}
            input_dict['now'] = clock_time_obj

            if use_init:
                input_dict['init'] = loop_time
            else:
                input_dict['valid'] = loop_time

            process.clear()
            process.run_at_time(input_dict)
            if process.all_commands:
                all_commands.extend(process.all_commands)
            process.all_commands.clear()

        loop_time += time_interval

    return all_commands

def get_lead_sequence(config, input_dict=None):
    """!Get forecast lead list from LEAD_SEQ or compute it from INIT_SEQ.
        Restrict list by LEAD_SEQ_[MIN/MAX] if set. Now returns list of relativedelta objects
        Args:
            @param config METplusConfig object to query config variable values
            @param input_dict time dictionary needed to handle using INIT_SEQ. Must contain
               valid key if processing INIT_SEQ
            @returns list of relativedelta objects or a list containing 0 if none are found
    """

    out_leads = []

    if config.has_option('config', 'LEAD_SEQ'):
        # return list of forecast leads
        lead_strings = getlist(config.getstr('config', 'LEAD_SEQ'))
        leads = []
        for lead in lead_strings:
            relative_delta = time_util.get_relativedelta(lead, 'H')
            if relative_delta is not None:
                leads.append(relative_delta)
            else:
                config.logger.error(f'Invalid item {lead} in LEAD_SEQ. Exiting.')
                exit(1)

        # remove any items that are outside of the range specified
        #  by LEAD_SEQ_MIN and LEAD_SEQ_MAX
        # convert min and max to relativedelta objects, then use current time
        # to compare them to each forecast lead
        # this is an approximation because relative time offsets depend on
        # each runtime
        lead_min_str = config.getstr('config', 'LEAD_SEQ_MIN', '0')
        lead_max_str = config.getstr('config', 'LEAD_SEQ_MAX', '4000Y')
        lead_min_relative = time_util.get_relativedelta(lead_min_str, 'H')
        lead_max_relative = time_util.get_relativedelta(lead_max_str, 'H')
        now_time = datetime.datetime.now()
        lead_min_approx = now_time + lead_min_relative
        lead_max_approx = now_time + lead_max_relative
        for lead in leads:
            lead_approx = now_time + lead
            if lead_approx >= lead_min_approx and lead_approx <= lead_max_approx:
                out_leads.append(lead)

    # use INIT_SEQ to build lead list based on the valid time
    elif config.has_option('config', 'INIT_SEQ'):
        # if input dictionary not passed in, cannot compute lead sequence
        #  from it, so exit
        if input_dict is None:
            log_msg = 'LEAD_SEQ must be specified to run'
            if config.logger:
                config.logger.error(log_msg)
            else:
                print(log_msg)
            exit(1)

        # if looping by init, fail and exit
        if 'valid' not in input_dict.keys():
            log_msg = 'INIT_SEQ specified while looping by init time.' + \
                      ' Use LEAD_SEQ or change to loop by valid time'
            if config.logger:
                config.logger.error(log_msg)
            else:
                print(log_msg)
            exit(1)

        valid_hr = int(input_dict['valid'].strftime('%H'))
        init_seq = getlistint(config.getstr('config', 'INIT_SEQ'))
        min_forecast = config.getint('config', 'LEAD_SEQ_MIN', 0)
        max_forecast = config.getint('config', 'LEAD_SEQ_MAX')
        lead_seq = []
        for i in init_seq:
            if valid_hr >= i:
                current_lead = valid_hr - i
            else:
                current_lead = valid_hr + (24 - i)

            while current_lead <= max_forecast:
                if current_lead >= min_forecast:
                    lead_seq.append(relativedelta(hours=current_lead))
                current_lead += 24

        out_leads = sorted(lead_seq, key=lambda rd: time_util.ti_get_seconds_from_relativedelta(rd, input_dict['valid']))

    if not out_leads:
        return [0]

    return out_leads

def round_0p5(val):
    """! Round to the nearest point five (ie 3.3 rounds to 3.5, 3.1
       rounds to 3.0) Take the input value, multiply by two, round to integer
       (no decimal places) then divide by two.  Expect any input value of n.0,
       n.1, or n.2 to round down to n.0, and any input value of n.5, n.6 or
       n.7 to round to n.5. Finally, any input value of n.8 or n.9 will
       round to (n+1).0
       Args:
          @param val :  The number to be rounded to the nearest .5
       Returns:
          pt_five:  The n.0, n.5, or (n+1).0 value as
                            a result of rounding the input value, val.
    """

    return round(val * 2) / 2

def round_to_int(val):
    """! Round to integer value
         Args:
             @param val:  The value to round up
         Returns:
            rval:  The rounded up value.
    """
    val += 0.5
    rval = int(val)
    return rval


def mkdir_p(path):
    """!
       From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).
       Args:
           @param path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist,
                 does nothing otherwise.
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def _rmtree_onerr(function, path, exc_info, logger=None):
    """!Internal function used to log errors.
    This is an internal implementation function called by
    shutil.rmtree when an underlying function call failed.  See
    the Python documentation of shutil.rmtree for details.
    @param function the funciton that failed
    @param path the path to the function that caused problems
    @param exc_info the exception information
    @protected"""
    if logger:
        logger.warning('%s: %s failed: %s' % (
            str(path), str(function), str(exc_info)))


def rmtree(tree, logger=None):
    """!Deletes the tree, if possible.
       @protected
       @param tree the directory tree to delete"
       @param logger the logger, optional
    """
    try:
        # If it is a file, special file or symlink we can just
        # delete it via unlink:
        os.unlink(tree)
        return
    except EnvironmentError:
        pass
    # We get here for directories.
    if logger:
        logger.info('%s: rmtree' % (tree,))
    shutil.rmtree(tree, ignore_errors=False)

def file_exists(filename):
    """! Determines if a file exists
        NOTE:  Simply using os.path.isfile() is not a Pythonic way
               to check if a file exists.  You can
               still encounter a TOCTTOU bug
               "time of check to time of use"
               Instead, use the raising of
               exceptions, which is a Pythonic
               approach:
               try:
                   with open(filename) as fileobj:
                      pass # or do something fruitful
               except IOError as e:
                   logger.error("your helpful error message goes here")
        Args:
            @param filename:  the full filename (full path)
        Returns:
            boolean : True if file exists, False otherwise
    """

    try:
        return os.path.isfile(filename)
    except IOError:
        pass


def is_dir_empty(directory):
    """! Determines if a directory exists and is not empty
        Args:
           @param directory:  The directory to check for existence
                                       and for contents.
        Returns:
           True:  If the directory is empty
           False:  If the directory exists and isn't empty
    """
    return not os.listdir(directory)

def grep(pattern, infile):
    """! Python version of grep, searches the file line-by-line
        to find a match to the pattern. Returns upon finding the
        first match.
        Args:
            @param pattern:  The pattern to be matched
            @param infile:     The filename with full filepath in which to
                             search for the pattern
        Returns:
            line (string):  The matching string
    """

    matching_lines = []
    with open(infile, 'r') as file_handle:
        for line in file_handle:
            match = re.search(pattern, line)
            if match:
                matching_lines.append(line)
                # if you got here, you didn't find anything
    return matching_lines


def get_filepaths_for_grbfiles(base_dir):
    """! Generates the grb2 file names in a directory tree
       by walking the tree either top-down or bottom-up.
       For each directory in the tree rooted at
       the directory top (including top itself), it
       produces a tuple: (dirpath, dirnames, filenames).
       This solution was found on Stack Overflow:
       http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-
           directory-in-python#3207973
       **scroll down to the section with "Getting Full File Paths From a
       Directory and All Its Subdirectories"
    Args:
        @param base_dir: The base directory from which we
                      begin the search for grib2 filenames.
    Returns:
        file_paths (list): A list of the full filepaths
                           of the data to be processed.
    """

    # Create an empty list which will eventually store
    # all the full filenames
    file_paths = []

    # pylint:disable=unused-variable
    # os.walk returns tuple, we don't need to utilize all the returned
    # values in the tuple.

    # Walk the tree
    for root, directories, files in os.walk(base_dir):
        for filename in files:
            # add it to the list only if it is a grib file
            match = re.match(r'.*(grib|grb|grib2|grb2)$', filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            else:
                continue
    return file_paths

def get_storms(filter_filename):
    """! Get each storm as identified by its STORM_ID in the filter file.
         Create dictionary storm ID as the key and a list of lines for that
         storm as the value.

         @param filter_filename name of tcst file to read and extract storm id
         @returns 2 item tuple - 1)dictionary where key is storm ID and value is list
          of relevant lines from tcst file, 2) header line from tcst file.
          Also, item with key 'header' contains the header of the tcst file
    """
    # Initialize a set because we want unique storm ids.
    storm_id_list = set()

    try:
        with open(filter_filename, "r") as file_handle:
            header, *lines = file_handle.readlines()

        storm_id_column = header.split().index('STORM_ID')
        for line in lines:
            storm_id_list.add(line.split()[storm_id_column])
    except (ValueError, FileNotFoundError):
        return {}

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)

    if not sorted_storms:
        return {}

    storm_dict = {'header': header}
    # for each storm, get all lines for that storm
    for storm in sorted_storms:
        storm_dict[storm] = [line for line in lines if storm in line]

    return storm_dict

def get_storm_ids(filter_filename, logger=None):
    """! Get each storm as identified by its STORM_ID in the filter file
        save these in a set so we only save the unique ids and sort them.
        Args:
            @param filter_filename:  The name of the filter file to read
                                       and extract the storm id
            @param logger:  The name of the logger for logging useful info
        Returns:
            sorted_storms (List):  a list of unique, sorted storm ids
    """
    # Initialize a set because we want unique storm ids.
    storm_id_list = set()

    try:
        with open(filter_filename, "r") as file_handle:
            header, *lines = file_handle.readlines()

        storm_id_column = header.split().index('STORM_ID')
        for line in lines:
            storm_id_list.add(line.split()[storm_id_column])
    except (ValueError, FileNotFoundError):
        return []

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    return sorted_storms

def get_files(filedir, filename_regex, logger=None):
    """! Get all the files (with a particular
        naming format) by walking
        through the directories.
        Args:
          @param filedir:  The topmost directory from which the
                           search begins.
          @param filename_regex:  The regular expression that
                                  defines the naming format
                                  of the files of interest.
       Returns:
          file_paths (string): a list of filenames (with full filepath)
    """
    file_paths = []

    # Walk the tree
    for root, _, files in os.walk(filedir):
        for filename in files:
            # add it to the list only if it is a match
            # to the specified format
            match = re.match(filename_regex, filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            else:
                continue
    return file_paths

def check_for_tiles(tile_dir, fcst_file_regex, anly_file_regex, logger):
    """! Checks for the presence of forecast and analysis
        tiles that were created by extract_tiles
        Args:
            @param tile_dir:  The directory where the expected
                              tiled files should reside.
            @param fcst_file_regex: The regexp describing the format of the
                                    forecast tile file.
            @param anly_file_regex: The regexp describing the format of the
                                    analysis tile file.
            @param logger:    The logger to which all log messages
                                should be directed.
        Returns:
            None  raises OSError if expected files are missing
    """
    anly_tiles = get_files(tile_dir, anly_file_regex, logger)
    fcst_tiles = get_files(tile_dir, fcst_file_regex, logger)

    num_anly_tiles = len(anly_tiles)
    num_fcst_tiles = len(fcst_tiles)

    # Check that there are analysis and forecast tiles
    # (which were, or should have been created earlier by extract_tiles).
    if not anly_tiles:
        # Cannot proceed, the necessary 30x30 degree analysis tiles are missing
        logger.error("No anly tile files were found  " + tile_dir)
        raise OSError("No 30x30 anlysis tiles were found")
    elif not fcst_tiles:
        # Cannot proceed, the necessary 30x30 degree fcst tiles are missing
        logger.error("No fcst tile files were found  " + tile_dir)
        raise OSError("No 30x30 fcst tiles were found")

    # Check for same number of fcst and analysis files
    if num_anly_tiles != num_fcst_tiles:
        # Something is wrong, we are missing
        # either an ANLY tile file or a FCST tile
        # file, this indicates a serious problem.
        logger.info("There are a different number of anly "
                    "and fcst tiles...")


def extract_year_month(init_time, logger):
    """! Retrieve the YYYYMM from the initialization time with format
         YYYYMMDD_hh
        Args:
            @param init_time:  The initialization time of expected format
            YYYYMMDD_hh
            @param logger:  Logger
        Returns:
            year_month (string):  The YYYYMM portion of the initialization time
    """
    # Match on anything that starts with 1 or 2 (for the century)
    #  followed by 5 digits for the remainder of the YYYMM
    year_month = re.match(r'^((1|2)[0-9]{5})', init_time)
    if year_month:
        year_month = year_month.group(0)
        return year_month
    else:
        logger.warning("Cannot extract YYYYMM from "
                       "initialization time, unexpected format")
        raise Warning("Cannot extract YYYYMM from initialization time,"
                      " unexpected format")

def create_grid_specification_string(lat, lon, logger, config):
    """! Create the grid specification string with the format:
         latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
         used by the MET tool, regrid_data_plane.
         Args:
            @param lat:   The latitude of the grid point
            @param lon:   The longitude of the grid point
            @param logger: The name of the logger
            @param config: config instance
         Returns:
            tile_grid_str (string): the tile grid string for the
                                    input lon and lat
    """

    # pylint: disable=protected-access
    # Need to access sys._getframe to capture current file and function for
    # logging information

    # Initialize the tile grid string
    # and get the other values from the parameter file
    nlat = config.getstr('config', 'EXTRACT_TILES_NLAT')
    nlon = config.getstr('config', 'EXTRACT_TILES_NLON')
    dlat = config.getstr('config', 'EXTRACT_TILES_DLAT')
    dlon = config.getstr('config', 'EXTRACT_TILES_DLON')
    lon_subtr = config.getfloat('config', 'EXTRACT_TILES_LON_ADJ')
    lat_subtr = config.getfloat('config', 'EXTRACT_TILES_LAT_ADJ')

    # Format for regrid_data_plane:
    # latlon Nx Ny lat_ll lon_ll delta_lat delta_lonadj_lon =
    # float(lon) - lon_subtr
    adj_lon = float(lon) - lon_subtr
    adj_lat = float(lat) - lat_subtr
    lon0 = str(round_0p5(adj_lon))
    lat0 = str(round_0p5(adj_lat))

    msg = ("lat:" + lat + " lon: " + lon +\
           " lat0:" + lat0 + " lon0: " + lon0)
    logger.debug(msg)

    # Create the specification string based on the requested tool.
    grid_list = ['"', 'latlon ', nlat, ' ', nlon, ' ', lat0, ' ',
                 lon0, ' ', dlat, ' ', dlon, '"']

    tile_grid_str = ''.join(grid_list)
    return tile_grid_str


def gen_date_list(begin_date, end_date):
    """! Generates a list of dates of the form yyyymmdd from a being date to
     end date
    Inputs:
      @param begin_date -- such as "20070101"
      @param end_date -- such as "20070103"
    Returns:
      date_list -- such as ["20070101","20070102","20070103"]
    """

    begin_tm = time.strptime(begin_date, "%Y%m%d")
    end_tm = time.strptime(end_date, "%Y%m%d")
    begin_tv = calendar.timegm(begin_tm)
    end_tv = calendar.timegm(end_tm)
    date_list = []
    for loop_tv in range(begin_tv, end_tv + 86400, 86400):
        date_list.append(time.strftime("%Y%m%d", time.gmtime(loop_tv)))
    return date_list


def gen_hour_list(hour_inc, hour_end):
    """! Generates a list of hours of the form hh or hhh
    Inputs:
      @param hour_inc -- increment in integer format such as 6
      @param hour_end -- hh or hhh string indicating the end hour for the
                       increment such as "18"
    Returns:
      hour_list -- such as ["00", "06", "12", "18"]
    """

    int_list = range(0, int(hour_end) + 1, hour_inc)

    zfill_val = 0
    if len(hour_end) == 2:
        zfill_val = 2
    elif len(hour_end) == 3:
        zfill_val = 3

    hour_list = []
    for my_int in int_list:
        hour_string = str(my_int).zfill(zfill_val)
        hour_list.append(hour_string)

    return hour_list


def gen_init_list(init_date_begin, init_date_end, init_hr_inc, init_hr_end):
    """!
    Generates a list of initialization date and times of the form yyyymmdd_hh
    or yyyymmdd_hhh
    Inputs:
      @param init_date_begin -- yyyymmdd string such as "20070101"
      @param init_date_end -- yyyymmdd string such as "20070102"
      @param init_hr_inc -- increment in integer format such as 6
      @param init_hr_end -- hh or hhh string indicating the end hour for the
                           increment such as "18"
    Returns:
      init_list -- such as ["20070101_00", "20070101_06", "20070101_12",
      "20070101_18", "20070102_00", "20070102_06", "20070102_12",
      "20070102_18"]
    """

    my_hour_list = gen_hour_list(init_hr_inc, init_hr_end)

    my_date_list = gen_date_list(init_date_begin, init_date_end)

    date_init_list = []

    # pylint:disable=unused-variable
    # using enumerate on my_date_list returns a tuple, and not all values
    # are needed.

    for index, my_date in enumerate(my_date_list):
        for my_hour in my_hour_list:
            init_string = my_date + "_" + my_hour
            date_init_list.append(init_string)

    return date_init_list


def prune_empty(output_dir, logger):
    """! Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they
        don't cause performance degradation or errors
        when performing subsequent tasks.
        Input:
            @param output_dir:  The directory from which searching
                                should begin.
            @param logger: The logger to which all logging is
                           directed.
    """

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        # Create a full file path by joining the path
        # and filename.
        for a_file in files:
            a_file = os.path.join(root, a_file)
            if os.stat(a_file).st_size == 0:
                logger.debug("Empty file: " + a_file +
                             "...removing")
                os.remove(a_file)

    # Now check for any empty directories, some
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for direc in dirs:
            full_dir = os.path.join(root, direc)
            if not os.listdir(full_dir):
                logger.debug("Empty directory: " + full_dir +
                             "...removing")
                os.rmdir(full_dir)


def cleanup_temporary_files(list_of_files):
    """! Remove the files indicated in the list_of_files list.  The full
       file path must be indicated.
        Args:
          @param list_of_files: A list of files (full filepath) to be
          removed.
        Returns:
            None:  Removes the requested files.
    """
    for single_file in list_of_files:
        try:
            os.remove(single_file)
        except OSError:
            # Raises exception if this doesn't exist (never created or
            # already removed).  Ignore.
            pass





def create_filter_tmp_files(filtered_files_list, filter_output_dir, logger=None):
    """! Creates the tmp_fcst and tmp_anly ASCII files that contain the full
        filepath of files that correspond to the filter criteria.  Useful for
        validating that filtering returns the expected results/troubleshooting.
        Args:
            @param filtered_files_list:  A list of the netCDF or grb2 files
                                          that result from applying filter
                                          options and running the MET tool
                                          tc_stat.
            @param filter_output_dir:  The directory where the filtered data is
                                       stored
            @param logger a logging.Logger for log messages
        Returns:
            None: Creates two ASCII files
    """
    # Create the filenames for the tmp_fcst and tmp_anly files.
    tmp_fcst_filename = os.path.join(filter_output_dir,
                                     "tmp_fcst_regridded.txt")
    tmp_anly_filename = os.path.join(filter_output_dir,
                                     "tmp_anly_regridded.txt")

    fcst_list = []
    anly_list = []

    for filter_file in filtered_files_list:
        fcst_match = re.match(r'(.*/FCST_TILE_F.*.[grb2|nc])', filter_file)
        if fcst_match:
            fcst_list.append(fcst_match.group(1))

        anly_match = re.match(r'(.*/ANLY_TILE_F.*.[grb2|nc])', filter_file)
        if anly_match:
            anly_list.append(anly_match.group(1))

    # Write to the appropriate tmp file
    # with open(tmp_fcst_filename, "a+") as fcst_tmpfile:
    with open(tmp_fcst_filename, "w+") as fcst_tmpfile:
        for fcst in fcst_list:
            fcst_tmpfile.write(fcst + "\n")

    with open(tmp_anly_filename, "w+") as anly_tmpfile:
        for anly in anly_list:
            anly_tmpfile.write(anly + "\n")


def get_updated_init_times(input_dir, config=None):
    """ Get a list of init times, derived by the .tcst files in the
        input_dir (and below).
        Args:
            @param input_dir:  The topmost directory from which our search for
                               filter.tcst files begins.
            @param config:  Reference to metplus.conf configuration instance.
        Returns:
            updated_init_times_list : A list of the init times represented by
                                      the forecast.tcst files found in the
                                      input_dir.
    """
    updated_init_times_list = []
    init_times_list = []
    filter_list = get_files(input_dir, ".*.tcst", config)
    if filter_list:
        for filter_file in filter_list:
            match = re.match(r'.*/filter_([0-9]{8}_[0-9]{2,3})', filter_file)
            if match:
                init_times_list.append(match.group(1))
        updated_init_times_list = sorted(init_times_list)

    return updated_init_times_list


def get_dirs(base_dir):
    """! Get a list of directories under a base directory.
        Args:
            @param base_dir:  The base directory from where search begins
       Returns:
           dir_list:  A list of directories under the base_dir
    """

    dir_list = []

    # pylint:disable=unused-variable
    # os.walk returns a tuple, not all returned values are needed.
    for dir_name, dirs, filenames in os.walk(base_dir):
        for direc in dirs:
            dir_list.append(os.path.join(dir_name, direc))

    return dir_list

def handle_begin_end_incr(list_str):
    """!Check for instances of begin_end_incr() in the input string and evaluate as needed
        Args:
            @param list_str string that contains a comma separated list
            @returns string that has list expanded"""

    matches = begin_end_incr_findall(list_str)

    for match in matches:
        item_list = begin_end_incr_evaluate(match)
        if item_list:
            list_str = list_str.replace(match, ','.join(item_list))

    return list_str

def begin_end_incr_findall(list_str):
    """!Find all instances of begin_end_incr in list string
        Args:
            @param list_str string that contains a comma separated list
            @returns list of strings that have begin_end_incr() characters"""
    # remove space around commas (again to make sure)
    # this makes the regex slightly easier because we don't have to include
    # as many \s* instances in the regex string
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # find begin_end_incr and any text before and after that are not a comma
    # [^,\s]* evaluates to any character that is not a comma or space
    return re.findall(r"([^,]*begin_end_incr\(\s*-?\d*,-?\d*,-*\d*,?\d*\s*\)[^,]*)",
                      list_str)

def begin_end_incr_evaluate(item):
    """!Expand begin_end_incr() items into a list of values
        Args:
            @param item string containing begin_end_incr() tag with
            possible text before and after
            @returns list of items expanded from begin_end_incr
    """
    match = re.match(r"^(.*)begin_end_incr\(\s*(-*\d*),(-*\d*),(-*\d*),?(\d*)\s*\)(.*)$",
                     item)
    if match:
        before = match.group(1).strip()
        after = match.group(6).strip()
        start = int(match.group(2))
        end = int(match.group(3))
        step = int(match.group(4))
        precision = match.group(5).strip()

        if start <= end:
            int_list = range(start, end+1, step)
        else:
            int_list = range(start, end-1, step)

        out_list = []
        for int_values in int_list:
            out_str = str(int_values)

            if precision:
                out_str = out_str.zfill(int(precision))

            out_list.append(f"{before}{out_str}{after}")

        return out_list

    return None

def fix_list(item_list):
    item_list = fix_list_helper(item_list, '(')
    item_list = fix_list_helper(item_list, '[')
    return item_list

def fix_list_helper(item_list, type):
    if type == '(':
        close_regex = r"[^(]+\).*"
        open_regex = r".*\([^)]*$"
    elif type == '[':
        close_regex = r"[^\[]+\].*"
        open_regex = r".*\[[^\]]*$"
    else:
        return item_list

    # combine items that had a comma between ()s or []s
    fixed_list = []
    incomplete_item = None
    found_close = False
    for index, item in enumerate(item_list):
        # if we have found an item that ends with ( but
        if incomplete_item:
            # check if item has ) before (
            match = re.match(close_regex, item)
            if match:
                # add rest of text, add it to output list, then reset incomplete_item
                incomplete_item += ',' + item
                found_close = True
            else:
                # if not ) before (, add text and continue
                incomplete_item += ',' + item

        match = re.match(open_regex, item)
        # if we find ( without ) after it
        if match:
            # if we are still putting together an item, append comma and new item
            if incomplete_item:
                if not found_close:
                    incomplete_item += ',' + item
            # if not, start new incomplete item to put together
            else:
                incomplete_item = item

            found_close = False
        # if we don't find ( without )
        else:
            # if we are putting together item, we can add to the output list and reset incomplete_item
            if incomplete_item:
                if found_close:
                    fixed_list.append(incomplete_item)
                    incomplete_item = None
            # if we are not within brackets and we found no brackets, add item to output list
            else:
                fixed_list.append(item)

    return fixed_list

def getlist(list_str, expand_begin_end_incr=True):
    """! Returns a list of string elements from a comma
         separated string of values.
         This function MUST also return an empty list [] if s is '' empty.
         This function is meant to handle these possible or similar inputs:
         AND return a clean list with no surrounding spaces or trailing
         commas in the elements.
         '4,4,2,4,2,4,2, ' or '4,4,2,4,2,4,2 ' or
         '4, 4, 4, 4, ' or '4, 4, 4, 4 '
         Note: getstr on an empty variable (EMPTY_VAR = ) in
         a conf file returns '' an empty string.

        @param list_str the string being converted to a list.
        @returns list of strings formatted properly and expanded as needed
    """
    # FIRST remove surrounding comma, and spaces, form the string.
    list_str = list_str.strip().strip(',').strip()

    # remove space around commas
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # option to not evaluate begin_end_incr
    if expand_begin_end_incr:
        list_str = handle_begin_end_incr(list_str)

    # use csv reader to divide comma list while preserving strings with comma
    # convert the csv reader to a list and get first item (which is the whole list)
    item_list = list(reader([list_str]))[0]

    item_list = fix_list(item_list)

    return item_list

def getlistfloat(list_str):
    """!Get list and convert all values to float
        Args:
            @param list_str the string being converted to a list.
            @returns list of floats
    """
    list_str = getlist(list_str)
    list_str = [float(i) for i in list_str]
    return list_str

def getlistint(list_str):
    """!Get list and convert all values to int
            Args:
            @param list_str the string being converted to a list.
            @returns list of ints
    """
    list_str = getlist(list_str)
    list_str = [int(i) for i in list_str]
    return list_str

def camel_to_underscore(camel):
    """! Change camel case notation to underscore notation, i.e. GridStatWrapper to grid_stat_wrapper
         Multiple capital letters are excluded, i.e. PCPCombineWrapper to pcp_combine_wrapper
         Numerals are also skipped, i.e. ASCII2NCWrapper to ascii2nc_wrapper
         Args:
             @param camel string to convert
             @returns string in underscore notation
    """
    s1 = re.sub(r'([^\d])([A-Z][a-z]+)', r'\1_\2', camel)
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', s1).lower()

def get_process_list(config):
    """!Read process list, Extract instance string if specified inside
     parenthesis. Remove dashes/underscores and change to lower case,
     then map the name to the correct wrapper name

     @param config METplusConfig object to read PROCESS_LIST value
     @returns list of tuple containing process name and instance identifier
     (None if no instance was set)
    """
    # get list of processes
    process_list = getlist(config.getstr('config', 'PROCESS_LIST'))

    out_process_list = []
    # for each item remove dashes, underscores, and cast to lower-case
    for process in process_list:
        # if instance is specified, extract the text inside parenthesis
        match = re.match(f'(.*)\((.*)\)', process)
        if match:
            instance = match.group(2)
            process_name = match.group(1)
        else:
            instance = None
            process_name = process

        wrapper_name = get_wrapper_name(process_name)
        if wrapper_name is None:
            config.logger.warning(f"PROCESS_LIST item {process_name} "
                                  "may be invalid.")
            wrapper_name = process_name

        # if MakePlots is in process list, remove it because
        # it will be called directly from StatAnalysis
        if wrapper_name == 'MakePlots':
            continue

        out_process_list.append((wrapper_name, instance))

    return out_process_list

def get_wrapper_name(process_name):
    """! Determine name of wrapper from string that may not contain the correct
         capitalization, i.e. Pcp-Combine translates to PCPCombine

         @param process_name string that was listed in the PROCESS_LIST
         @returns name of wrapper (without 'Wrapper' at the end) and None if
          name cannot be determined
    """
    lower_process = (process_name.replace('-', '')
                         .replace('_', '')
                         .replace(' ', '')
                         .lower())
    if lower_process in LOWER_TO_WRAPPER_NAME.keys():
        return LOWER_TO_WRAPPER_NAME[lower_process]

    return None

# minutes
def shift_time(time_str, shift):
    """ Adjust time by shift hours. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in hours
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            datetime.timedelta(hours=shift)).strftime("%Y%m%d%H%M%S")

def shift_time_minutes(time_str, shift):
    """ Adjust time by shift minutes. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in minutes
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            datetime.timedelta(minutes=shift)).strftime("%Y%m%d%H%M%S")

def shift_time_seconds(time_str, shift):
    """ Adjust time by shift seconds. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in seconds
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            datetime.timedelta(seconds=shift)).strftime("%Y%m%d%H%M%S")

def get_threshold_via_regex(thresh_string):
    """!Ensure thresh values start with >,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le and then a number
        Optionally can have multiple comparison/number pairs separated with && or ||.
        Args:
            @param thresh_string: String to examine, i.e. <=3.4
        Returns:
            None if string does not match any valid comparison operators or does
              not contain a number afterwards
            regex match object with comparison operator in group 1 and
            number in group 2 if valid
    """

    comparison_number_list = []
    # split thresh string by || or &&
    thresh_split = re.split(r'\|\||&&', thresh_string)
    # check each threshold for validity
    for thresh in thresh_split:
        found_match = False
        for comp in list(valid_comparisons.keys())+list(valid_comparisons.values()):
            # if valid, add to list of tuples
            # must be one of the valid comparison operators followed by
            # at least 1 digit or NA
            if thresh == 'NA':
                comparison_number_list.append((thresh, ''))
                found_match = True
                break

            match = re.match(r'^('+comp+r')(.*\d.*)$', thresh)
            if match:
                comparison = match.group(1)
                number = match.group(2)
                # try to convert to float if it can, but allow string
                try:
                    number = float(number)
                except ValueError:
                    pass

                comparison_number_list.append((comparison, number))
                found_match = True
                break

        # if no match was found for the item, return None
        if not found_match:
            return None

    if not comparison_number_list:
        return None

    return comparison_number_list

def comparison_to_letter_format(expression):
    """! Convert comparison operator to the letter version if it is not already
         @args expression string starting with comparison operator to
          convert, i.e. gt3 or <=5.4
         @returns letter comparison operator, i.e. gt3 or le5.4 or None if invalid
    """
    for symbol_comp, letter_comp in valid_comparisons.items():
        if letter_comp in expression or symbol_comp in expression:
            return expression.replace(symbol_comp, letter_comp)

    return None

def validate_thresholds(thresh_list):
    """ Checks list of thresholds to ensure all of them have the correct format
        Should be a comparison operator with number pair combined with || or &&
        i.e. gt4 or >3&&<5 or gt3||lt1
        Args:
            @param thresh_list list of strings to check
        Returns:
            True if all items in the list are valid format, False if not
    """
    valid = True
    for thresh in thresh_list:
        match = get_threshold_via_regex(thresh)
        if match is None:
            valid = False

    if valid is False:
        print("ERROR: Threshold values must use >,>=,==,!=,<,<=,gt,ge,eq,ne,lt, or le with a number, "
              "optionally combined with && or ||")
        return False
    return True

def write_list_to_file(filename, output_list):
    with open(filename, 'w+') as f:
        for line in output_list:
            f.write(f"{line}\n")

def validate_configuration_variables(config, force_check=False):

    all_sed_cmds = []
    # check for deprecated config items and warn user to remove/replace them
    deprecated_isOK, sed_cmds = check_for_deprecated_config(config)
    all_sed_cmds.extend(sed_cmds)

    # check for deprecated env vars in MET config files and warn user to remove/replace them
    deprecatedMET_isOK, sed_cmds = check_for_deprecated_met_config(config)
    all_sed_cmds.extend(sed_cmds)

    # validate configuration variables
    field_isOK, sed_cmds = validate_field_info_configs(config, force_check)
    all_sed_cmds.extend(sed_cmds)

    # check that OUTPUT_BASE is not set to the exact same value as INPUT_BASE
    inoutbase_isOK = True
    input_real_path = os.path.realpath(config.getdir_nocheck('INPUT_BASE', ''))
    output_real_path = os.path.realpath(config.getdir('OUTPUT_BASE'))
    if input_real_path == output_real_path:
      config.logger.error(f"INPUT_BASE AND OUTPUT_BASE are set to the exact same path: {input_real_path}")
      config.logger.error("Please change one of these paths to avoid risk of losing input data")
      inoutbase_isOK = False

    check_user_environment(config)

    return deprecated_isOK, field_isOK, inoutbase_isOK, deprecatedMET_isOK, all_sed_cmds

def skip_field_info_validation(config):
    """!Check config to see if having corresponding FCST/OBS variables is necessary. If process list only
        contains reformatter wrappers, don't validate field info. Also, if MTD is in the process list and
        it is configured to only process either FCST or OBS, validation is unnecessary."""

    reformatters = ['PCPCombine', 'RegridDataPlane']
    process_list = [item[0] for item in get_process_list(config)]

    # if running MTD in single mode, you don't need matching FCST/OBS
    if 'MTD' in process_list and config.getbool('config', 'MTD_SINGLE_RUN'):
        return True

    # if running any app other than the reformatters, you need matching FCST/OBS, so don't skip
    if [item for item in process_list if item not in reformatters]:
        return False

    return True

def find_indices_in_config_section(regex_expression, config, sec, noID=False):
    # regex expression must have 2 () items and the 2nd item must be the index
    all_conf = config.keys(sec)
    indices = {}
    regex = re.compile(regex_expression)
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
            if noID:
                index = result.group(1)
                identifier = None
            else:
                identifier = result.group(1)
                index = result.group(2)

            if index not in indices:
                indices[index] = [identifier]
            else:
                indices[index].append(identifier)

    return indices

def is_var_item_valid(item_list, index, ext, config):
    """!Given a list of data types (FCST, OBS, ENS, or BOTH) check if the
        combination is valid.
        If BOTH is found, FCST and OBS should not be found.
        If FCST or OBS is found, the other must also be found.
        @param item_list list of data types that were found for a given index
        @param index number following _VAR in the variable name
        @param ext extension to check, i.e. NAME, LEVELS, THRESH, or OPTIONS
        @param config METplusConfig instance
        @returns tuple containing boolean if var item is valid, list of error
         messages and list of sed commands to help the user update their old
         configuration files
    """

    full_ext = f"_VAR{index}_{ext}"
    msg = []
    sed_cmds = []
    if 'BOTH' in item_list and ('FCST' in item_list or 'OBS' in item_list):

        msg.append(f"Cannot set FCST{full_ext} or OBS{full_ext} if BOTH{full_ext} is set.")

    elif 'FCST' in item_list and 'OBS' not in item_list:
        # if FCST level has 1 item and OBS name is a python embedding script,
        # don't report error
        level_list = getlist(config.getraw('config',
                                           f'FCST_VAR{index}_LEVELS',
                                           ''))
        other_name = config.getraw('config', f'OBS_VAR{index}_NAME', '')
        skip_error_for_py_embed = ext == 'LEVELS' and is_python_script(other_name) and len(level_list) == 1
        # do not report error for OPTIONS since it isn't required to be the same length
        if ext not in ['OPTIONS'] and not skip_error_for_py_embed:
            msg.append(f"If FCST{full_ext} is set, you must either set OBS{full_ext} or "
                       f"change FCST{full_ext} to BOTH{full_ext}")

            config_files = config.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
            for config_file in config_files:
                sed_cmds.append(f"sed -i 's|^FCST{full_ext}|BOTH{full_ext}|g' {config_file}")
                sed_cmds.append(f"sed -i 's|{{FCST{full_ext}}}|{{BOTH{full_ext}}}|g' {config_file}")

    elif 'OBS' in item_list and 'FCST' not in item_list:
        # if OBS level has 1 item and FCST name is a python embedding script,
        # don't report error
        level_list = getlist(config.getraw('config',
                                           f'OBS_VAR{index}_LEVELS',
                                           ''))
        other_name = config.getraw('config', f'FCST_VAR{index}_NAME', '')
        skip_error_for_py_embed = ext == 'LEVELS' and is_python_script(other_name) and len(level_list) == 1

        if ext not in ['OPTIONS'] and not skip_error_for_py_embed:
            msg.append(f"If OBS{full_ext} is set, you must either set FCST{full_ext} or ."
                          f"change OBS{full_ext} to BOTH{full_ext}")

            config_files = config.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
            for config_file in config_files:
                sed_cmds.append(f"sed -i 's|^OBS{full_ext}|BOTH{full_ext}|g' {config_file}")
                sed_cmds.append(f"sed -i 's|{{OBS{full_ext}}}|{{BOTH{full_ext}}}|g' {config_file}")

    return not bool(msg), msg, sed_cmds

def validate_field_info_configs(config, force_check=False):
    """!Verify that config variables with _VAR<n>_ in them are valid. Returns True if all are valid.
       Returns False if any items are invalid"""

    variable_extensions = ['NAME', 'LEVELS', 'THRESH', 'OPTIONS']
    all_good = True, []

    if skip_field_info_validation(config) and not force_check:
        return True, []

    # keep track of all sed commands to replace config variable names
    all_sed_cmds = []

    for ext in variable_extensions:
        # find all _VAR<n>_<ext> keys in the conf files
        data_types_and_indices = find_indices_in_config_section(r"(\w+)_VAR(\d+)_"+ext,
                                                                config,
                                                                'config')

        # if BOTH_VAR<n>_ is used, set FCST and OBS to the same value
        # if FCST or OBS is used, the other must be present as well
        # if BOTH and either FCST or OBS are set, report an error
        # get other data type
        for index, data_type_list in data_types_and_indices.items():

            is_valid, err_msgs, sed_cmds = is_var_item_valid(data_type_list, index, ext, config)
            if not is_valid:
                for err_msg in err_msgs:
                    config.logger.error(err_msg)
                all_sed_cmds.extend(sed_cmds)
                all_good = False

            # make sure FCST and OBS have the same number of levels if coming from separate variables
            elif ext == 'LEVELS' and all(item in ['FCST', 'OBS'] for item in data_type_list):
                fcst_levels = getlist(config.getraw('config', f"FCST_VAR{index}_LEVELS", ''))

                # add empty string if no levels are found because python embedding items do not need
                # to include a level, but the other item may have a level and the numbers need to match
                if not fcst_levels:
                    fcst_levels.append('')

                obs_levels = getlist(config.getraw('config', f"OBS_VAR{index}_LEVELS", ''))
                if not obs_levels:
                    obs_levels.append('')

                if len(fcst_levels) != len(obs_levels):
                    config.logger.error(f"FCST_VAR{index}_LEVELS and OBS_VAR{index}_LEVELS do not have "
                                        "the same number of elements")
                    all_good = False

    return all_good, all_sed_cmds

def get_var_items(config, data_type, index, time_info, met_tool=None):
    """!Get configuration variables for given data type and index
        Args:
            @param config: METplusConfig object
            @param data_type: type of data to find, i.e. FCST, OBS, BOTH, or ENS
            @param index: index of variable, i.e. _VAR<index>_NAME
            @param met_tool: optional name of MET tool to look for wrapper specific items
            @returns tuple containing name, level, thresh, extra values if found. If not found
               4 empty strings are returned.
    """

    # build string to search for BOTH items, using MET tool name if provided
    # do the same for data_type, i.e. FCST
    # The result with either be BOTH_VAR and FCST_VAR or
    # BOTH_<MET-tool>_VAR and FCST_<MET-tool>_VAR
    both_var = "BOTH_"
    data_type_var = f"{data_type}_"
    if met_tool:
        both_var += f"{met_tool.upper()}_"
        data_type_var += f"{met_tool.upper()}_"
    both_var += "VAR"
    data_type_var += "VAR"

    # get field variable name from data type name
    # look for BOTH_VAR<n>_NAME if looking for FCST or OBS (not ENS)
    # return empty strings if name cannot be found from either
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"{both_var}{index}_NAME"):
        search_name = f"{both_var}{index}_NAME"
    elif config.has_option('config', f"{data_type_var}{index}_NAME"):
        search_name = f"{data_type_var}{index}_NAME"
    else:
        return '', '', '', ''

    name = do_string_sub(config.getraw('config', search_name),
                         **time_info)

    # get levels if available
    levels = []
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"{both_var}{index}_LEVELS"):
        search_levels = f"{both_var}{index}_LEVELS"
    else:
        search_levels = f"{data_type_var}{index}_LEVELS"

    levels = []
    for level in getlist(config.getraw('config', search_levels, '')):
        subbed_level = do_string_sub(level,
                                     **time_info)
        levels.append(subbed_level)

    # if no levels are found, add an empty string
    if not levels:
        levels.append('')

    # get thresholds if available
    thresh = []
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"{both_var}{index}_THRESH"):
        search_thresh = f"{both_var}{index}_THRESH"
    elif config.has_option('config', f"{data_type_var}{index}_THRESH"):
        search_thresh = f"{data_type_var}{index}_THRESH"
    else:
        search_thresh = None

    if search_thresh:
        thresh = getlist(config.getstr('config', search_thresh))
        if not validate_thresholds(thresh):
            config.logger.error(f"  Update {search_thresh} to match this format")
            return '', '', '', ''

    # get extra options if available
    extra = ""
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"{both_var}{index}_OPTIONS"):
        search_extra = f"{both_var}{index}_OPTIONS"
    elif config.has_option('config', f"{data_type_var}{index}_OPTIONS"):
        search_extra = f"{data_type_var}{index}_OPTIONS"
    else:
        search_extra = None

    if search_extra:
        extra = do_string_sub(config.getraw('config', search_extra),
                              **time_info)

        # split up each item by semicolon, then add a semicolon to the end of each item
        # to avoid errors where the user forgot to add a semicolon at the end
        # use list(filter(None to remove empty strings from list
        extra_list = list(filter(None, extra.split(';')))
        extra = f"{'; '.join(extra_list)};"

    return name, levels, thresh, extra

def find_var_name_indices(config, data_type, met_tool=None):

    regex_string = ''
    # if specific data type is requested, only get that type or BOTH
    if data_type:
        regex_string += f"({data_type}|BOTH)"
    # if no data type requested, get one or more characters that are not underscore
    else:
        regex_string += r"([^_]+)"

    # if MET tool is specified, get tool specific items
    if met_tool:
        regex_string += f"_{met_tool.upper()}"

    regex_string += r"_VAR(\d+)_NAME"

    # find all <data_type>_VAR<n>_NAME keys in the conf files
    return find_indices_in_config_section(regex_string,
                                          config,
                                          'config')

def parse_var_list(config, time_info=None, data_type=None, met_tool=None):
    """ read conf items and populate list of dictionaries containing
    information about each variable to be compared
        Args:
            @param config: METplusConfig object
            @param time_info: time object for string sub, optional
            @param data_type: data type to find. Can be FCST, OBS, or ENS. If not set, get FCST/OBS/BOTH
            @param met_tool: optional name of MET tool to look for wrapper specific var items
        Returns:
            list of dictionaries with variable information
    """

    # validate configs again in case wrapper is not running from master_metplus
    # this does not need to be done if parsing a specific data type, i.e. ENS or FCST
    if data_type is None:
        if not validate_field_info_configs(config)[0]:
            return []
    elif data_type == 'BOTH':
        config.logger.error("Cannot request BOTH explicitly in parse_var_list")
        return []

    # if time_info is not passed in, set 'now' to CLOCK_TIME
    # NOTE: any attempt to use string template substitution with an item other than
    #  'now' will fail if time_info is not passed into parse_var_list
    if time_info is None:
        time_info = { 'now' : datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                         '%Y%m%d%H%M%S') }

    # var_list is a list containing an list of dictionaries
    var_list = []

    # check if *_<MET-tool>_VAR<n>_NAME exists, if so, use that instead of generic
    data_types_and_indices = {}

    # if using wrapper specific field info, use_met_tool will be set to handle them
    use_met_tool = None
    if met_tool:
        data_types_and_indices = find_var_name_indices(config, data_type, met_tool)

    if not data_types_and_indices:
        data_types_and_indices = find_var_name_indices(config, data_type)
    # if found wrapper specific fields, pass the MET tool name to get_var_items
    else:
        use_met_tool = met_tool

    # loop over all possible variables and add them to list
    for index, data_type_list in data_types_and_indices.items():

        # if specific data type is requested, only get that type
        if data_type:
            data_type_lower = data_type.lower()
            name, levels, thresh, extra = get_var_items(config, data_type, index, time_info,
                                                        met_tool=use_met_tool)

            if not name:
                continue

            for level in levels:
                var_dict = {f"{data_type_lower}_name": name,
                            f"{data_type_lower}_level": level,
                            f"{data_type_lower}_thresh": thresh,
                            f"{data_type_lower}_extra": extra,
                            'index': index,
                            }
                var_list.append(var_dict)

        # if FCST and OBS or BOTH are used, get and set both of them
        else:
            f_name, f_levels, f_thresh, f_extra = get_var_items(config, 'FCST', index,
                                                                time_info,
                                                                met_tool=use_met_tool)
            o_name, o_levels, o_thresh, o_extra = get_var_items(config, 'OBS', index,
                                                                time_info,
                                                                met_tool=use_met_tool)

            # if number of levels are not equal, return an empty list
            if len(f_levels) != len(o_levels):
                return []

            if not o_name and not f_name:
                continue

            if not o_name or not f_name:
                return []

            for f_level, o_level in zip(f_levels, o_levels):
                var_dict = {"fcst_name": f_name,
                            "fcst_level": f_level,
                            "fcst_thresh": f_thresh,
                            "fcst_extra": f_extra,
                            "obs_name": o_name,
                            "obs_level": o_level,
                            "obs_thresh": o_thresh,
                            "obs_extra": o_extra,
                            'index': index,
                            }
                var_list.append(var_dict)


    # extra debugging information used for developer debugging only
    '''
    for v in var_list:
        config.logger.debug(f"VAR{v['index']}:")
        if 'fcst_name' in v.keys():
            config.logger.debug(" fcst_name:"+v['fcst_name'])
            config.logger.debug(" fcst_level:"+v['fcst_level'])
        if 'fcst_thresh' in v.keys():
            config.logger.debug(" fcst_thresh:"+str(v['fcst_thresh']))
        if 'fcst_extra' in v.keys():
            config.logger.debug(" fcst_extra:"+v['fcst_extra'])
        if 'obs_name' in v.keys():
            config.logger.debug(" obs_name:"+v['obs_name'])
            config.logger.debug(" obs_level:"+v['obs_level'])
        if 'obs_thresh' in v.keys():
            config.logger.debug(" obs_thresh:"+str(v['obs_thresh']))
        if 'obs_extra' in v.keys():
            config.logger.debug(" obs_extra:"+v['obs_extra'])
        if 'ens_name' in v.keys():
            config.logger.debug(" ens_name:"+v['ens_name'])
            config.logger.debug(" ens_level:"+v['ens_level'])
        if 'ens_thresh' in v.keys():
            config.logger.debug(" ens_thresh:"+str(v['ens_thresh']))
        if 'ens_extra' in v.keys():
            config.logger.debug(" ens_extra:"+v['ens_extra'])
    '''
    return sorted(var_list, key=lambda x: x['index'])

def split_level(level):
    level_type = ""
    if not level:
        return '', ''
    match = re.match(r'^(\w)(\d+)$', level)
    if match:
        level_type = match.group(1)
        level = match.group(2)
        return level_type, level

    return '', ''

def remove_quotes(input_string):
    """!Remove quotes from string"""
    if not input_string:
        return ''

    # strip off double and single quotes
    return input_string.strip('"').strip("'")

def get_filetype(filepath, logger=None):
    """!This function determines if the filepath is a NETCDF or GRIB file
       based on the first eight bytes of the file.
       It returns the string GRIB, NETCDF, or a None object.

       Note: If it is NOT determined to ba a NETCDF file,
       it returns GRIB, regardless.
       Unless there is an IOError exception, such as filepath refers
       to a non-existent file or filepath is only a directory, than
       None is returned, without a system exit.

       Args:
           @param filepath:  path/to/filename
           @param logger the logger, optional
       Returns:
           @returns The string GRIB, NETCDF or a None object
    """
    # Developer Note
    # Since we have the impending code-freeze, keeping the behavior the same,
    # just changing the implementation.
    # The previous logic did not test for GRIB it would just return 'GRIB'
    # if you couldn't run ncdump on the file.
    # Also note:
    # As John indicated ... there is the case when a grib file
    # may not start with GRIB ... and if you pass the MET command filtetype=GRIB
    # MET will handle it ok ...

    # Notes on file format and determining type.
    # https://www.wmo.int/pages/prog/www/WDM/Guides/Guide-binary-2.html
    # https://www.unidata.ucar.edu/software/netcdf/docs/faq.html
    # http: // www.hdfgroup.org / HDF5 / doc / H5.format.html

    # Interpreting single byte by byte - so ok to ignore endianess
    # od command:
    #   od -An -c -N8 foo.nc
    #   od -tx1 -N8 foo.nc
    # GRIB
    # Octet no.  IS Content
    # 1-4        'GRIB' (Coded CCITT-ITA No. 5) (ASCII);
    # 5-7        Total length, in octets, of GRIB message(including Sections 0 & 5);
    # 8          Edition number - currently 1
    # NETCDF .. ie. od -An -c -N4 foo.nc which will output
    # C   D   F 001
    # C   D   F 002
    # 211   H   D   F
    # HDF5
    # Magic numbers   Hex: 89 48 44 46 0d 0a 1a 0a
    # ASCII: \211 HDF \r \n \032 \n

    # Below is a reference that may be used in the future to
    # determine grib version.
    # import struct
    # with open ("foo.grb2","rb")as binary_file:
    #     binary_file.seek(7)
    #     one_byte = binary_file.read(1)
    #
    # This would return an integer with value 1 or 2,
    # B option is an unsigned char.
    #  struct.unpack('B',one_byte)[0]

    # if filepath is set to None, return None to avoid crash
    if filepath == None:
        return None

    try:
        # read will return up to 8 bytes, if file is 0 bytes in length,
        # than first_eight_bytes will be the empty string ''.
        # Don't test the file length, just adds more time overhead.
        with open(filepath, "rb") as binary_file:
            binary_file.seek(0)
            first_eight_bytes = binary_file.read(8)

        # From the first eight bytes of the file, unpack the bytes
        # of the known identifier byte locations, in to a string.
        # Example, if this was a netcdf file than ONLY name_cdf would
        # equal 'CDF' the other variables, name_hdf would be 'DF '
        # name_grid 'CDF '
        name_cdf, name_hdf, name_grib = [None] * 3
        if len(first_eight_bytes) == 8:
            name_cdf = struct.unpack('3s', first_eight_bytes[:3])[0]
            name_hdf = struct.unpack('3s', first_eight_bytes[1:4])[0]
            name_grib = struct.unpack('4s', first_eight_bytes[:4])[0]

        # Why not just use a else, instead of elif else if we are going to
        # return GRIB ? It allows for expansion, ie. Maybe we pass in a
        # logger and log the cases we can't determine the type.
        if name_cdf == 'CDF' or name_hdf == 'HDF':
            return "NETCDF"
        elif name_grib == 'GRIB':
            return "GRIB"
        else:
            # This mimicks previous behavoir, were we at least will always return GRIB.
            # It also handles the case where GRIB was not in the first 4 bytes
            # of a legitimate grib file, see John.
            # logger.info('Can't determine type, returning GRIB
            # as default %s'%filepath)
            return "GRIB"

    except IOError:
        # Skip the IOError, and keep processing data.
        # ie. filepath references a file that does not exist
        # or filepath is a directory.
        return None

    # Previous Logic
    # ncdump_exe = config.getexe('NCDUMP')
    #try:
    #    result = subprocess.check_output([ncdump_exe, filepath])

    #except subprocess.CalledProcessError:
    #    return "GRIB"

    #regex = re.search("netcdf", result)
    #if regex is not None:
    #    return "NETCDF"
    #else:
    #    return None



def get_time_from_file(filepath, template, logger=None):
    """! Extract time information from path using the filename template
         Args:
             @param filepath path to examine
             @param template filename template to use to extract time information
             @returns time_info dictionary with time information if successful, None if not
    """
    if os.path.isdir(filepath):
        return None

    out = parse_template(template, filepath, logger)
    if out is not None:
        return out

    # check to see if zip extension ends file path, try again without extension
    for ext in VALID_EXTENSIONS:
        if filepath.endswith(ext):
            out = parse_template(template, filepath[:-len(ext)], logger)
            if out is not None:
                return out

    return None

def preprocess_file(filename, data_type, config, allow_dir=False):
    """ Decompress gzip, bzip, or zip files or convert Gempak files to NetCDF
        Args:
            @param filename: Path to file without zip extensions
            @param config: Config object
        Returns:
            Path to staged unzipped file or original file if already unzipped
    """
    if not filename:
        return None

    if allow_dir and os.path.isdir(filename):
        return filename

    # if using python embedding for input, return the keyword
    if os.path.basename(filename) in PYTHON_EMBEDDING_TYPES:
        return os.path.basename(filename)

    if data_type is not None and 'PYTHON' in data_type:
        return filename

    stage_dir = config.getdir('STAGING_DIR')

    if os.path.isfile(filename):
        # if filename provided ends with a valid compression extension,
        # remove the extension and call function again so the
        # file will be uncompressed properly. This is done so that
        # the function will handle files passed to it with an
        # extension the same way as files passed
        # without an extension but the compressed equivalent exists
        for ext in VALID_EXTENSIONS:
            if filename.endswith(ext):
                return preprocess_file(filename[:-len(ext)], data_type, config)
        # if extension is grd (Gempak), then look in staging dir for nc file
        if filename.endswith('.grd') or data_type == "GEMPAK":
            if filename.endswith('.grd'):
                stagefile = stage_dir + filename[:-3]+"nc"
            else:
                stagefile = stage_dir + filename+".nc"
            if os.path.isfile(stagefile):
                return stagefile
            # if it does not exist, run GempakToCF and return staged nc file
            # Create staging area if it does not exist
            outdir = os.path.dirname(stagefile)
            if not os.path.exists(outdir):
                os.makedirs(outdir, mode=0o0775)

            # only import GempakToCF if needed
            from ..wrappers import GempakToCFWrapper

            run_g2c = GempakToCFWrapper(config)
            run_g2c.infiles.append(filename)
            run_g2c.set_output_path(stagefile)
            cmd = run_g2c.get_command()
            if cmd is None:
                config.logger.error("GempakToCF could not generate command")
                return None
            if config.logger:
                config.logger.debug("Converting Gempak file into {}".format(stagefile))
            run_g2c.build()
            return stagefile

        return filename

    # nc file requested and the Gempak equivalent exists
    if os.path.isfile(filename[:-2]+'grd'):
        return preprocess_file(filename[:-2]+'grd', data_type, config)

    # if file exists in the staging area, return that path
    outpath = stage_dir + filename
    if os.path.isfile(outpath):
        return outpath

    # Create staging area if it does not exist
    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
        os.makedirs(outdir, mode=0o0775)

    # uncompress gz, bz2, or zip file
    if os.path.isfile(filename+".gz"):
        if config.logger:
            config.logger.debug("Uncompressing gz file to {}".format(outpath))
        with gzip.open(filename+".gz", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(infile.read())
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".bz2"):
        if config.logger:
            config.logger.debug("Uncompressing bz2 file to {}".format(outpath))
        with open(filename+".bz2", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(bz2.decompress(infile.read()))
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".zip"):
        if config.logger:
            config.logger.debug("Uncompressing zip file to {}".format(outpath))
        with zipfile.ZipFile(filename+".zip") as z:
            with open(outpath, 'wb') as f:
                f.write(z.read(os.path.basename(filename)))
                return outpath

    return None

def template_to_regex(template, time_info, logger):
    in_template = re.sub(r'\.', '\\.', template)
    in_template = re.sub(r'{lead.*?}', '.*', in_template)
    return do_string_sub(in_template,
                         **time_info)

def is_python_script(name):
    if not name:
        return False

    all_items = name.split(' ')
    if any(item.endswith('.py') for item in all_items):
        return True

    return False

def check_user_environment(config):
    """!Check if any environment variables set in [user_env_vars] are already set in
    the user's environment. Warn them that it will be overwritten from the conf if it is"""
    if not config.has_section('user_env_vars'):
        return

    for env_var in config.keys('user_env_vars'):
        if env_var in os.environ:
            msg = '{} is already set in the environment. '.format(env_var) +\
                  'Overwriting from conf file'
            config.logger.warning(msg)


def remove_staged_files(staged_dir, filename_regex, logger):
    ''' Removes the staged files generated for series analysis filtering. This
        is important in the feature relative use case, when the series analysis
        wrappers can be run multiple times, each time the filter results are
        appended to any existing temp files, which is not desirable.
       Args:
        @param staged_dir:  The location of the directory where the
                            intermediate filter files are being saved.
        @param filename_regex: The regular expression that identifies the
                               filenaming format of the files to be removed.
        @param logger:  The logger instance


       Returns:
           0 on successful completion
    '''

    # Determine the current user's username so we only remove that individual's
    # staged files (important if the staged dir is a shared space).
    username = getpass.getuser()

    # Get a list of the files located in the tmp directory
    files_in_staged_dir = get_files(staged_dir, filename_regex, logger)

    for staged_file in files_in_staged_dir:
        cur_user = getpwuid(stat(staged_file).st_uid).pw_name
        if cur_user == username:
            # Remove this file, it is owned by the user
            full_filename = os.path.join(staged_dir, staged_file)
            os.remove(full_filename)

    # if we get here, all went well...
    return 0

def iterate_is_first(input_list):
    """!Use an iterator to loop over the list and keep track if the current item is the first in the loop
        Args:
            @param input_list list of items to iterate over
            @returns tuple containing the next item and a boolean that is only True for the first item"""
    iterate_check_position(input_list, check_first=True)

def iterate_is_last(input_list):
    """!Use an iterator to loop over the list and keep track if the current item is the last in the loop
        Args:
            @param input_list list of items to iterate over
            @returns tuple containing the next item and a boolean that is only True for the last item"""
    iterate_check_position(input_list, check_first=False)

def iterate_check_position(input_list, check_first):
    """!Use an iterator to loop over the list and keep track if the current item is the first or last in the loop
        Args:
            @param input_list list of items to iterate over
            @param check_first if True, return True if the current item is the first item, if False, return True
                if the current item is the last item
            @returns tuple containing the next item and a boolean that is only True for the first/last item"""
    it = iter(input_list)
    last = next(it)

    for item in it:
        yield last, check_first
        last = item

    yield last, not check_first

def expand_int_string_to_list(int_string):
    """! Expand string into a list of integer values. Items are separated by
    commas. Items that are formatted X-Y will be expanded into each number
    from X to Y inclusive. If the string ends with +, then add a str '+'
    to the end of the list.

    @param int_string String containing a comma-separated list of integers
    @returns List of integers and potentially '+' as the last item
    """
    subset_list = []

    # if string ends with +, remove it and add it back at the end
    if int_string.strip().endswith('+'):
        int_string = int_string.strip(' +')
        hasPlus = True
    else:
        hasPlus = False

    # separate into list by comma
    comma_list = int_string.split(',')
    for comma_item in comma_list:
        dash_list = comma_item.split('-')
        # if item contains X-Y, expand it
        if len(dash_list) == 2:
            for i in range(int(dash_list[0].strip()),
                           int(dash_list[1].strip())+1,
                           1):
                subset_list.append(i)
        else:
            subset_list.append(int(comma_item.strip()))

    if hasPlus:
        subset_list.append('+')
    print(f"{int_string} converted to {subset_list}")
    return subset_list

def subset_list(full_list, subset_definition):
    """! Extract subset of items from full_list based on subset_definition

    @param full_list List of all use cases that were requested
    @param subset_definition Defines how to subset the full list. If None,
    no subsetting occurs. If an integer value, select that index only.
    If a slice object, i.e. slice(2,4,1), pass slice object into list.
    If list, subset full list by integer index values in list. If
    last item in list is '+' then subset list up to 2nd last index, then
    get all items from 2nd last item and above
    """
    if subset_definition is not None:
        subset_list = []

        # if case slice is a list, use only the indices in the list
        if isinstance(subset_definition, list):
            # if last slice value is a plus sign, get rest of items
            # after 2nd last slice value
            if subset_definition[-1] == '+':
                plus_value = subset_definition[-2]
                # add all values before last index before plus
                subset_list.extend([full_list[i]
                                    for i in subset_definition[:-2]])
                # add last index listed + all items above
                subset_list.extend(full_list[plus_value:])
            else:
                # list of integers, so get items based on indices
                subset_list = [full_list[i] for i in subset_definition]
        else:
            subset_list = full_list[subset_definition]
    else:
        subset_list = full_list

    # if only 1 item is left, make it a list before returning
    if not isinstance(subset_list, list):
        subset_list = [subset_list]

    return subset_list

def is_met_netcdf(file_path):
    """! Check if a file is a MET-generated NetCDF file.
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    # disable functionality for testing
    return False
    try:
        from netCDF4 import Dataset
        nc_file = Dataset(file_path, 'r')
        getattr(nc_file, 'MET_version')
    except (AttributeError, OSError, ImportError):
        return False

    return True

def netcdf_has_var(file_path, name, level):
    """! Check if name is a variable in the NetCDF file. If not, check if
         {name}_{level} (with level prefix letter removed, i.e. 06 from A06)
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    try:
        from netCDF4 import Dataset

        nc_file = Dataset(file_path, 'r')
        variables = nc_file.variables.keys()

        # if name is a variable, return that name
        if name in variables:
            return name


        # if name_level is a variable, return that
        name_underscore_level = f"{name}_{split_level(level)[1]}"
        if name_underscore_level in variables:
            return name_underscore_level

        # requested variable name is not found in file
        return None

    except (AttributeError, OSError, ImportError):
        return False
