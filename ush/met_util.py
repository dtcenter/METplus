#!/usr/bin/env python

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

from string_template_substitution import StringSub
from string_template_substitution import StringExtract
from string_template_substitution import get_tags
from gempak_to_cf_wrapper import GempakToCFWrapper
import time_util

# for run stand alone
import produtil.setup
import produtil.log
import config_metplus


"""!@namespace met_util
 @brief Provides  Utility functions for METplus.
"""
# list of compression extensions that are handled by METplus
VALID_EXTENSIONS = ['.gz', '.bz2', '.zip']

baseinputconfs = ['metplus_config/metplus_system.conf',
                  'metplus_config/metplus_data.conf',
                  'metplus_config/metplus_runtime.conf',
                  'metplus_config/metplus_logging.conf']

def pre_run_setup(filename, app_name):
    filebasename = os.path.basename(filename)
    logger = logging.getLogger(app_name)
    version_number = get_version_number()
    logger.info(f'Starting {app_name} v{version_number}')

    # Parse arguments, options and return a config instance.
    config = config_metplus.setup(baseinputconfs,
                                  filename=filebasename)

    logger = get_logger(config)

    config.set('config', 'METPLUS_VERSION', version_number)
    logger.info(f'Running {app_name} v%s called with command: %s',
                version_number, ' '.join(sys.argv))

    # validate configuration variables
    isOK_A, isOK_B, isOK_C, all_sed_cmds = validate_configuration_variables(config)
    if not (isOK_A and isOK_B and isOK_C):
        # if any sed commands were generated, write them to the sed file
        if all_sed_cmds:
            sed_file = os.path.join(config.getdir('OUTPUT_BASE'), 'sed_commands.txt')
            # remove if sed file exists
            if os.path.exists(sed_file):
                os.remove(sed_file)

            write_list_to_file(sed_file, all_sed_cmds)
            config.logger.error(f"Find/Replace commands have been generated in {sed_file}")

        logger.error("Correct configuration variables and rerun. Exiting.")
        exit(1)

    # set staging dir to OUTPUT_BASE/stage if not set
    if not config.has_option('dir', 'STAGING_DIR'):
        config.set('dir', 'STAGING_DIR',
                   os.path.join(config.getdir('OUTPUT_BASE'), "stage"))

    # handle dir to write temporary files
    handle_tmp_dir(config)

    config.env = os.environ.copy()

    return config

def run_metplus(config, process_list):

    processes = []
    for item in process_list:
        try:
            logger = config.log(item)
            command_builder = \
                getattr(sys.modules['__main__'],
                        item + "Wrapper")(config, logger)
            # if Usage specified in PROCESS_LIST, print usage and exit
            if item == 'Usage':
                command_builder.run_all_times()
                exit(1)
        except AttributeError:
            raise NameError("Process %s doesn't exist" % item)

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
        exit()

    loop_order = config.getstr('config', 'LOOP_ORDER', '')

    if loop_order == "processes":
        for process in processes:
            process.run_all_times()

    elif loop_order == "times":
        loop_over_times_and_call(config, processes)

    else:
        logger.error("Invalid LOOP_ORDER defined. " + \
              "Options are processes, times")
        exit()

   # compute total number of errors that occurred and output results
    total_errors = 0
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

    if total_errors == 0:
        logger.info(f'{app_name} has successfully finished running.')
    else:
        error_msg = f"{app_name} has finished running but had {total_errors} error"
        if total_errors > 1:
            error_msg += 's'
        error_msg += '.'
        logger.error(error_msg)


def check_for_deprecated_config(conf):
    """!Checks user configuration files and reports errors or warnings if any deprecated variable
        is found. If an alternate variable name can be suggested, add it to the 'alt' section
        If the alternate cannot be literally substituted for the old name, set copy to False
       Args:
          @conf : METplusConfig object to evaluate
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
        'VAR_LIST': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_VAR_LIST'},
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
        'FCST_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'FCST_SERIES_ANALYSIS_TILE_REGEX'},
        'OBS_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'OBS_SERIES_ANALYSIS_TILE_REGEX'},
        'FCST_NC_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'FCST_SERIES_ANALYSIS_NC_TILE_REGEX'},
        'ANLY_NC_TILE_REGEX': {'sec': 'regex_patterns', 'alt': 'OBS_SERIES_ANALYSIS_NC_TILE_REGEX'},
        'FCST_ASCII_REGEX_LEAD': {'sec': 'regex_patterns', 'alt': 'FCST_SERIES_ANALYSIS_LEAD_REGEX'},
        'ANLY_ASCII_REGEX_LEAD': {'sec': 'regex_patterns', 'alt': 'OBS_SERIES_ANALYSIS_LEAD_REGEX'},
        'SERIES_BY_LEAD_FILTERED_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'SERIES_BY_INIT_FILTERED_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_FILTERED_OUTPUT_DIR'},
        'SERIES_BY_LEAD_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_BY_INIT_OUTPUT_DIR': {'sec': 'dir', 'alt': 'SERIES_ANALYSIS_OUTPUT_DIR'},
        'SERIES_BY_LEAD_GROUP_FCSTS': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_GROUP_FCSTS'},
        'SERIES_ANALYSIS_BY_LEAD_CONFIG_FILE': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_CONFIG_FILE'},
        'SERIES_ANALYSIS_BY_INIT_CONFIG_FILE': {'sec': 'config', 'alt': 'SERIES_ANALYSIS_CONFIG_FILE'},
        'ENSEMBLE_STAT_MET_OBS_ERROR_TABLE': {'sec': 'config', 'alt': 'ENSEMBLE_STAT_MET_OBS_ERR_TABLE'},
        'VAR_LIST': {'sec': 'config', 'alt': 'BOTH_VAR<n>_NAME BOTH_VAR<n>_LEVELS', 'copy': False},
        'SERIES_ANALYSIS_VAR_LIST': {'sec': 'config', 'alt': 'BOTH_VAR<n>_NAME BOTH_VAR<n>_LEVELS', 'copy': False},
        'EXTRACT_TILES_VAR_LIST': {'sec': 'config', 'alt': ''},

    }

    # template       '' : {'sec' : '', 'alt' : '', 'copy': True},

    logger = conf.logger

    # create list of errors and warnings to report for deprecated configs
    e_list = []
    w_list = []
    all_sed_cmds = []
    config_files = conf.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
    for old, depr_info in deprecated_dict.items():
        if isinstance(depr_info, dict):
            sec = depr_info['sec']
            alt = depr_info['alt']
            # if deprecated config item is found
            if conf.has_option(sec, old):
                # if it is not required to remove, add to warning list
                if 'req' in depr_info.keys() and depr_info['req'] is False:
                    msg = '[{}] {} is deprecated and will be '.format(sec, old) +\
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

    # check all templates and error if any deprecated tags are used
    # value of dict is replacement tag, set to None if no replacement exists
    # deprecated tags: region (replace with basin)
    deprecated_tags = {'region' : 'basin'}
    template_vars = conf.keys('filename_templates')
    for temp_var in template_vars:
        template = conf.getraw('filename_templates', temp_var)
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
        config.set('dir', 'TMP_DIR', met_tmp_dir)

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

def skip_time(time_info, config):
    """!Used to check current run time against list of times to skip."""
    # never skip until this is implemented correctly
    return False

    # get list of times to skip

    # check skip times against current time_info object and skip if it matches

def write_final_conf(conf, logger):
    """!write final conf file including default values that were set during run"""
    confloc = conf.getloc('METPLUS_CONF')
    logger.info('%s: write metplus.conf here' % (confloc,))
    with open(confloc, 'wt') as conf_file:
        conf.write(conf_file)

    # remove current time env vars if they are set
    if 'METPLUS_CURRENT_INIT_TIME' in os.environ.keys():
        del os.environ['METPLUS_CURRENT_INIT_TIME']

    if 'METPLUS_CURRENT_VALID_TIME' in os.environ.keys():
        del os.environ['METPLUS_CURRENT_VALID_TIME']

    if 'METPLUS_CURRENT_LEAD_TIME' in os.environ.keys():
        del os.environ['METPLUS_CURRENT_LEAD_TIME']

    # write out os environment to file for debugging
    env_file = os.path.join(conf.getdir('LOG_DIR'), '.metplus_user_env')
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

    exit(1)


def get_time_obj(time_from_conf, fmt, clock_time, logger=None):
    """!Substitute today or now into [INIT/VALID]_[BEG/END] if used"""
    sts = StringSub(logger, time_from_conf,
                    now=clock_time,
                    today=clock_time.strftime('%Y%m%d'))
    time_str = sts.do_string_sub()
    return datetime.datetime.strptime(time_str, fmt)

def loop_over_times_and_call(config, processes):
    """!Loop over all run times and call wrappers listed in config"""
    clock_time_obj = datetime.datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                                '%Y%m%d%H%M%S')
    use_init = is_loop_by_init(config)
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

    # verify that *_TIME_FMT matches *_BEG and *_END
    time_format_len = len(datetime.datetime.now().strftime(time_format))
    if len(start_t) != time_format_len:
        config.logger.error(f"[INIT/VALID]_TIME_FMT {time_format} does not match [INIT/VALID]_BEG {start_t}.")
        exit(1)

    if len(end_t) != time_format_len:
        config.logger.error(f"[INIT/VALID]_TIME_FMT ({time_format}) does not match [INIT/VALID]_END ({end_t}).")
        exit(1)

    loop_time = get_time_obj(start_t, time_format,
                             clock_time_obj, config.logger)
    end_time = get_time_obj(end_t, time_format,
                            clock_time_obj, config.logger)

    if loop_time + time_interval < loop_time + datetime.timedelta(seconds=60):
        config.logger.error("time_interval parameter must be "
                            "greater than or equal to 60 seconds")
        exit(1)

    while loop_time <= end_time:
        run_time = loop_time.strftime("%Y%m%d%H%M")
        config.logger.info("****************************************")
        config.logger.info("* Running METplus")
        if use_init:
            config.logger.info("*  at init time: " + run_time)
            config.set('config', 'CURRENT_INIT_TIME', run_time)
            os.environ['METPLUS_CURRENT_INIT_TIME'] = run_time
        else:
            config.logger.info("*  at valid time: " + run_time)
            config.set('config', 'CURRENT_VALID_TIME', run_time)
            os.environ['METPLUS_CURRENT_VALID_TIME'] = run_time
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

        loop_time += time_interval

def get_lead_sequence(config, input_dict=None):
    """!Get forecast lead list from LEAD_SEQ or compute it from INIT_SEQ.
        Restrict list by LEAD_SEQ_[MIN/MAX] if set. Now returns list of relativedelta objects"""
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
        out_leads = []
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

        return out_leads

    # use INIT_SEQ to build lead list based on the valid time
    if config.has_option('config', 'INIT_SEQ'):
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

        return sorted(lead_seq, key=lambda rd: time_util.ti_get_seconds_from_relativedelta(rd, input_dict['valid']))
    else:
        return [0]


def get_version_number():
    # read version file and return value
    version_file_path = os.path.join(dirname(dirname(realpath(__file__))),
                                     'doc', 'version')
    with open(version_file_path, 'r') as version_file:
        return version_file.read()


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

    val2 = val * 2
    rval = round_to_int(val2)
    pt_five = round(rval, 0) / 2
    return pt_five


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

    try:
        # ***Note***:
        # For Python 3.2 and beyond, os.makedirs has a third optional argument,
        # exist_ok, that when set to True will enable the mkdir -p
        # functionality.
        # The mkdir -p functionality holds unless the mode is provided and the
        # existing directory has different permissions from the intended ones.
        # In this situation the OSError exception is raised.

        # default mode is octal 0777
        os.makedirs(path, mode=0o0775)
    except OSError as exc:
        # Ignore the error that gets created if the path already exists
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


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


def set_logvars(config, logger=None):
    """!Sets and adds the LOG_METPLUS and LOG_TIMESTAMP
       to the config object. If LOG_METPLUS was already defined by the
       user in their conf file. It expands and rewrites it in the conf
       object and the final file.
       conf file.
       Args:
           @param config:   the config instance
           @param logger: the logger, optional
    """

    if logger is None:
        logger = config.log()

    # LOG_TIMESTAMP_TEMPLATE is not required in the conf file,
    # so lets first test for that.
    log_timestamp_template = config.getstr('config', 'LOG_TIMESTAMP_TEMPLATE', '')
    if log_timestamp_template:
        # Note: strftime appears to handle if log_timestamp_template
        # is a string ie. 'blah' and not a valid set of % directives %Y%m%d,
        # it does return the string 'blah', instead of crashing.
        # However, I'm still going to test for a valid % directive and
        # set a default. It probably is ok to remove the if not block pattern
        # test, and not set a default, especially if causing some unintended
        # consequences or the pattern is not capturing a valid directive.
        # The reality is, the user is expected to have entered a correct
        # directive in the conf file.
        # This pattern is meant to test for a repeating set of
        # case insensitive %(AnyAlphabeticCharacter), ie. %Y%m ...
        # The basic pattern is (%+[a-z])+ , %+ allows for 1 or more
        # % characters, ie. %%Y, %% is a valid directive.
        # (?i) case insensitive, \A begin string \Z end of string
        if not re.match(r'(?i)\A(?:(%+[a-z])+)\Z', log_timestamp_template):
            logger.warning('Your LOG_TIMESTAMP_TEMPLATE is not '
                           'a valid strftime directive: %s' % repr(log_timestamp_template))
            logger.info('Using the following default: %Y%m%d%H')
            log_timestamp_template = '%Y%m%d%H'
        date_t = datetime.datetime.now()
        if config.getbool('config', 'LOG_TIMESTAMP_USE_DATATIME', False):
            if is_loop_by_init(config):
                date_t = datetime.datetime.strptime(config.getstr('config',
                                                                  'INIT_BEG'),
                                                    config.getstr('config',
                                                                  'INIT_TIME_FMT'))
            else:
                date_t = datetime.datetime.strptime(config.getstr('config',
                                                                  'VALID_BEG'),
                                                    config.getstr('config',
                                                                  'VALID_TIME_FMT'))
        log_filenametimestamp = date_t.strftime(log_timestamp_template)
    else:
        log_filenametimestamp = ''

    log_dir = config.getdir('LOG_DIR')

    # NOTE: LOG_METPLUS or metpluslog is meant to include the absolute path
    #       and the metpluslog_filename,
    # so metpluslog = /path/to/metpluslog_filename

    # if LOG_METPLUS =  unset in the conf file, means NO logging.
    # Also, assUmes the user has included the intended path in LOG_METPLUS.
    user_defined_log_file = None
    if config.has_option('config', 'LOG_METPLUS'):
        user_defined_log_file = True
        # strinterp will set metpluslog to '' if LOG_METPLUS =  is unset.
        metpluslog = config.strinterp('config', '{LOG_METPLUS}',
                                      LOG_TIMESTAMP_TEMPLATE=log_filenametimestamp)

        # test if there is any path information, if there is, assUme it is as intended,
        # if there is not, than add log_dir.
        if metpluslog:
            if os.path.basename(metpluslog) == metpluslog:
                metpluslog = os.path.join(log_dir, metpluslog)
    else:
        # No LOG_METPLUS in conf file, so let the code try to set it,
        # if the user defined the variable LOG_FILENAME_TEMPLATE.
        # LOG_FILENAME_TEMPLATE is an 'unpublished' variable - no one knows
        # about it unless you are reading this. Why does this exist ?
        # It was from my first cycle implementation. I did not want to pull
        # it out, in case the group wanted a stand alone metplus log filename
        # template variable.

        # If metpluslog_filename includes a path, python joins it intelligently.
        # Set the metplus log filename.
        # strinterp will set metpluslog_filename to '' if LOG_FILENAME_TEMPLATE =
        if config.has_option('config', 'LOG_FILENAME_TEMPLATE'):
            metpluslog_filename = config.strinterp('config', '{LOG_FILENAME_TEMPLATE}',
                                                   LOG_TIMESTAMP_TEMPLATE=log_filenametimestamp)
        else:
            metpluslog_filename = ''
        if metpluslog_filename:
            metpluslog = os.path.join(log_dir, metpluslog_filename)
        else:
            metpluslog = ''



    # Adding LOG_TIMESTAMP to the final configuration file.
    logger.info('Adding: config.LOG_TIMESTAMP=%s' % repr(log_filenametimestamp))
    config.set('config', 'LOG_TIMESTAMP', log_filenametimestamp)

    # Setting LOG_METPLUS in the configuration object
    # At this point LOG_METPLUS will have a value or '' the empty string.
    if user_defined_log_file:
        logger.info('Replace [config] LOG_METPLUS with %s' % repr(metpluslog))
    else:
        logger.info('Adding: config.LOG_METPLUS=%s' % repr(metpluslog))
    # expand LOG_METPLUS to ensure it is available
    config.set('config', 'LOG_METPLUS', metpluslog)


def get_logger(config, sublog=None):
    """!This function will return a logger with a formatted file handler
    for writing to the LOG_METPLUS and it sets the LOG_LEVEL. If LOG_METPLUS is
    not defined, a logger is still returned without adding a file handler,
    but still setting the LOG_LEVEL.
       Args:
           @param config:   the config instance
           @param sublog the logging subdomain, or None
       Returns:
           logger: the logger
    """

    # Retrieve all logging related parameters from the param file
    log_dir = config.getdir('LOG_DIR')
    log_level = config.getstr('config', 'LOG_LEVEL')

    # TODO review, use builtin produtil.fileop vs. mkdir_p ?
    # import produtil.fileop
    # produtil.fileop.makedirs(log_dir,logger=None)

    # Check if the directory path for the log file exists, if
    # not create it.
    if not os.path.exists(log_dir):
        mkdir_p(log_dir)

    if sublog is not None:
        logger = config.log(sublog)
    else:
        logger = config.log()

    # Setting of the logger level from the config instance.
    # Check for log_level by Integer or LevelName.
    # Try to convert the string log_level to an integer and use that, if
    # it can't convert then we assume it is a valid LevelName, which
    # is what is should be anyway,  ie. DEBUG.
    # Note:
    # Earlier versions of python2 require setLevel(<int>), argument
    # to be an int. Passing in the LevelName, 'DEBUG' will disable
    # logging output. Later versions of python2 will accept 'DEBUG',
    # not sure which version that changed with, but the logic below
    # should work for all version. I know python 2.6.6 must be an int,
    # and python 2.7.5 accepts the LevelName.
    try:
        int_log_level = int(log_level)
        logger.setLevel(int_log_level)
    except ValueError:
        logger.setLevel(logging.getLevelName(log_level))

    # Make sure the LOG_METPLUS is defined. In this function,
    # LOG_METPLUS should already be defined in the config object,
    # even if it is empty, LOG_METPLUS =.
    if not config.has_option('config', 'LOG_METPLUS'):
        set_logvars(config)
    metpluslog = config.getstr('config', 'LOG_METPLUS', '')

    if metpluslog:
        # It is possible that more path, other than just LOG_DIR, was added
        # to the metpluslog, by either a user defining more path in
        # LOG_METPLUS or LOG_FILENAME_TEMPLATE definitions in their conf file.
        # So lets check and make more directory if needed.
        dir_name = os.path.dirname(metpluslog)
        if not os.path.exists(dir_name):
            mkdir_p(dir_name)

        # set up the filehandler and the formatter, etc.
        # The default matches the oformat log.py formatter of produtil
        # So terminal output will now match log files.
        formatter = config_metplus.METplusLogFormatter(config)
        file_handler = logging.FileHandler(metpluslog, mode='a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # set add the logger to the config
    config.logger = logger
    return logger

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


def get_storm_ids(filter_filename, logger):
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
    empty_list = []

    # Check if the filter_filename is empty, if it
    # is, then return an empty list.
    if not os.path.isfile(filter_filename):
        return empty_list
    if os.stat(filter_filename).st_size == 0:
        return empty_list
    with open(filter_filename, "r") as fileobj:
        header = fileobj.readline().split()
        header_colnum = header.index('STORM_ID')
        for line in fileobj:
            storm_id_list.add(str(line.split()[header_colnum]))

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    return sorted_storms


def get_files(filedir, filename_regex, logger):
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

    # pylint:disable=unused-variable
    # os.walk returns a tuple. Not all returned values are needed.

    # Walk the tree
    for root, directories, files in os.walk(filedir):
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

    msg = ("nlat:" + nlat + " nlon: " + nlon +\
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

    # Useful for logging
    # cur_filename = sys._getframe().f_code.co_filename
    # cur_function = sys._getframe().f_code.co_name

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


def getlist(list_str, logger=None):
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
    """
    # FIRST remove surrounding comma, and spaces, form the string.
    list_str = list_str.strip().strip(',').strip()

    # remove space around commas
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # support beg, end, step to generate a int list
    # begin_end_incr(0, 10, 2) will create a list of 0, 2, 4, 6, 8, 10 (inclusive)
    match = re.match(r'^begin_end_incr\(\s*(-*\d*),(-*\d*),(-*\d*)\s*\)$', list_str)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        step = int(match.group(3))
        if start <= end:
            int_list = range(start, end+1, step)
        else:
            int_list = range(start, end-1, step)

        return list(map(lambda int_list: str(int_list), int_list))

    # use csv reader to divide comma list while preserving strings with comma
    list_str = reader([list_str])
    # convert the csv reader to a list and get first item (which is the whole list)
    list_str = list(list_str)[0]
    return list_str

def getlistfloat(list_str):
    """!Get list and convert all values to float"""
    list_str = getlist(list_str)
    list_str = [float(i) for i in list_str]
    return list_str

def getlistint(list_str):
    """!Get list and convert all values to int"""
    list_str = getlist(list_str)
    list_str = [int(i) for i in list_str]
    return list_str

def get_process_list(config):
    """!Read process list, remove dashes/underscores and change to lower case. Then
        map the name to the correct wrapper name"""
    lower_to_wrapper_name = {'ascii2nc': 'ASCII2NC',
                             'customingest': 'CustomIngest',
                             'cycloneplotter': 'CyclonePlotter',
                             'ensemblestat': 'EnsembleStat',
                             'example': 'Example',
                             'extracttiles': 'ExtractTiles',
                             'gempaktocf': 'GempakToCF',
                             'gridstat': 'GridStat',
                             'makeplots': 'MakePlots',
                             'mode': 'MODE',
                             'mtd': 'MTD',
                             'modetimedomain': 'MTD',
                             'pb2nc': 'PB2NC',
                             'pcpcombine': 'PCPCombine',
                             'pointstat': 'PointStat',
                             'regriddataplane': 'RegridDataPlane',
                             'seriesbyinit': 'SeriesByInit',
                             'seriesbylead': 'SeriesByLead',
                             'statanalysis': 'StatAnalysis',
                             'tcpairs': 'TCPairs',
                             'tcstat': 'TCStat',
                             'tcmprplotter': 'TCMPRPlotter',
                             'usage': 'Usage',
                            }

    # get list of processes
    process_list = getlist(config.getstr('config', 'PROCESS_LIST'))

    out_process_list = []
    # for each item remove dashes, underscores, and cast to lower-case
    for process in process_list:
        lower_process = process.replace('-', '').replace('_', '').lower()
        if lower_process in lower_to_wrapper_name.keys():
            out_process_list.append(lower_to_wrapper_name[lower_process])
        else:
            config.logger.warning(f"PROCESS_LIST item {process} may be invalid.")
            out_process_list.append(process)

    return out_process_list

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
    valid_comparisons = {">", ">=", "==", "!=", "<", "<=", "gt", "ge", "eq", "ne", "lt", "le"}
    comparison_number_list = []
    # split thresh string by || or &&
    thresh_split = re.split(r'\|\||&&', thresh_string)
    # check each threshold for validity
    for thresh in thresh_split:
        found_match = False
        for comp in valid_comparisons:
            # if valid, add to list of tuples
            match = re.match(r'^('+comp+r')([+-]?\d*\.?\d*)$', thresh)
            if match:
                comparison_number_list.append((match.group(1), float(match.group(2))))
                found_match = True
                break

        # if no match was found for the item, return None
        if not found_match:
            return None

    if not comparison_number_list:
        return None

    return comparison_number_list

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

    # validate configuration variables
    field_isOK, sed_cmds = validate_field_info_configs(config, force_check)
    all_sed_cmds.extend(sed_cmds)

    # check that OUTPUT_BASE is not set to the exact same value as INPUT_BASE
    inoutbase_isOK = True
    input_real_path = os.path.realpath(config.getdir('INPUT_BASE'))
    output_real_path = os.path.realpath(config.getdir('OUTPUT_BASE'))
    if input_real_path == output_real_path:
      config.logger.error(f"INPUT_BASE AND OUTPUT_BASE are set to the exact same path: {input_real_path}")
      config.logger.error("Please change one of these paths to avoid risk of losing input data")
      inoutbase_isOK = False

    check_user_environment(config)
    print(f"{deprecated_isOK}, {field_isOK}, {inoutbase_isOK}, {all_sed_cmds}")

    return deprecated_isOK, field_isOK, inoutbase_isOK, all_sed_cmds

def skip_field_info_validation(config):
    """!Check config to see if having corresponding FCST/OBS variables is necessary. If process list only
        contains reformatter wrappers, don't validate field info. Also, if MTD is in the process list and
        it is configured to only process either FCST or OBS, validation is unnecessary."""

    reformatters = ['PCPCombine', 'RegridDataPlane']
    process_list = get_process_list(config)

    # if running MTD in single mode, you don't need matching FCST/OBS
    if 'MTD' in process_list and config.getbool('config', 'MTD_SINGLE_RUN'):
        return True

    # if only running PCPCombine and/or RegridDataPlane, you don't need matching FCST/OBS
    if [item for item in process_list if item not in reformatters]:
        return True

    return False

def find_indices_in_config_section(regex_expression, config, sec):
    # regex expression must have 2 () items and the 2nd item must be the index
    all_conf = config.keys(sec)
    indices = {}
    regex = re.compile(regex_expression)
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
            identifier = result.group(1)
            index = result.group(2)
            if index not in indices:
                indices[index] = [identifier]
            else:
                indices[index].append(identifier)

    return indices

def is_var_item_valid(item_list, index, ext, config):
    """!Given a list of data types (FCST, OBS, ENS, or BOTH) check if the combination is valid.
        If BOTH is found, FCST and OBS should not be found.
        If FCST or OBS is found, ther other must also be found."""

    full_ext = f"_VAR{index}_{ext}"
    msg = []
    sed_cmds = []
    if 'BOTH' in item_list and ('FCST' in item_list or 'OBS' in item_list):

        msg.append(f"Cannot set FCST{full_ext} or OBS{full_ext} if BOTH{full_ext} is set.")

    elif ext not in ['OPTIONS'] and 'FCST' in item_list and 'OBS' not in item_list:

        msg.append(f"If FCST{full_ext} is set, you must either set OBS{full_ext} or "
                   f"change FCST{full_ext} to BOTH{full_ext}")

        config_files = config.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
        for config_file in config_files:
            sed_cmds.append(f"sed -i 's|^FCST{full_ext}|BOTH{full_ext}|g' {config_file}")
            sed_cmds.append(f"sed -i 's|{{FCST{full_ext}}}|{{BOTH{full_ext}}}|g' {config_file}")

    elif ext not in ['OPTIONS'] and 'OBS' in item_list and 'FCST' not in item_list:

        msg.append(f"If OBS{full_ext} is set, you must either set FCST{full_ext} or ."
                      f"change OBS{full_ext} to BOTH{full_ext}")

        config_files = config.getstr('config', 'METPLUS_CONFIG_FILES', '').split(',')
        for config_file in config_files:
            sed_cmds.append(f"sed -i 's|^OBS{full_ext}|BOTH{full_ext}|g' {config_file}")
            sed_cmds.append(f"sed -i 's|{{OBS{full_ext}}}|{{BOTH{full_ext}}}|g' {config_file}")

    else:
        return True, msg, sed_cmds

    return False, msg, sed_cmds

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
                    config.logger.error(f"FCST_VAR{index}_LEVELS and OBS_VAR{inx}_LEVELS do not have "
                                        "the same number of elements")
                    all_good = False

    return all_good, all_sed_cmds

def get_var_items(config, data_type, index, time_info):
    """!Get configuration variables for given data type and index
        Args:
            @param config: METplusConfig object
            @param data_type: type of data to find, i.e. FCST, OBS, BOTH, or ENS
            @param index: index of variable, i.e. _VAR<index>_NAME"""

    # get field variable name from data type name
    # look for BOTH_VAR<n>_NAME if looking for FCST or OBS (not ENS)
    # return empty strings if name cannot be found from either
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"BOTH_VAR{index}_NAME"):
        search_name = f"BOTH_VAR{index}_NAME"
    elif config.has_option('config', f"{data_type}_VAR{index}_NAME"):
        search_name = f"{data_type}_VAR{index}_NAME"
    else:
        return '', '', '', ''

    name = StringSub(config.logger,
                     config.getraw('config', search_name),
                     **time_info).do_string_sub()

    # get levels if available
    levels = []
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"BOTH_VAR{index}_LEVELS"):
        search_levels = f"BOTH_VAR{index}_LEVELS"
    else:
        search_levels = f"{data_type}_VAR{index}_LEVELS"

    levels = []
    for level in getlist(config.getraw('config', search_levels, '')):
        subbed_level = StringSub(config.logger, level, **time_info).do_string_sub()
        levels.append(subbed_level)

    # if no levels are found, add an empty string
    if not levels:
        levels.append('')

    # get thresholds if available
    thresh = []
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"BOTH_VAR{index}_THRESH"):
        search_thresh = f"BOTH_VAR{index}_THRESH"
    elif config.has_option('config', f"{data_type}_VAR{index}_THRESH"):
        search_thresh = f"{data_type}_VAR{index}_THRESH"
    else:
        search_thresh = None

    if search_thresh:
        thresh = getlist(config.getstr('config', search_thresh))
        if not validate_thresholds(thresh):
            config.logger.error(f"  Update {search_thresh} to match this format")
            return '', '', '', ''

    # get extra options if available
    extra = ""
    if data_type in ['FCST', 'OBS'] and config.has_option('config', f"BOTH_VAR{index}_OPTIONS"):
        search_extra = f"BOTH_VAR{index}_OPTIONS"
    elif config.has_option('config', f"{data_type}_VAR{index}_OPTIONS"):
        search_extra = f"{data_type}_VAR{index}_OPTIONS"
    else:
        search_extra = None

    if search_extra:
        extra = StringSub(config.logger,
                          config.getraw('config', search_extra),
                          **time_info).do_string_sub()

        # split up each item by semicolon, then add a semicolon to the end of each item
        # to avoid errors where the user forgot to add a semicolon at the end
        # use list(filter(None to remove empty strings from list
        extra_list = list(filter(None, extra.split(';')))
        extra = f"{'; '.join(extra_list)};"

    return name, levels, thresh, extra


def parse_var_list(config, time_info=None, data_type=None):
    """ read conf items and populate list of dictionaries containing
    information about each variable to be compared
        Args:
            @param config: METplusConfig object
            @param time_info: time object for string sub, optional
            @param data_type: data type to find. Can be FCST, OBS, or ENS. If not set, get FCST/OBS/BOTH
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

    # if specific data type is requested, only get those items
    if data_type:
        regex_string = f"({data_type})"+r"_VAR(\d+)_NAME"
    else:
        regex_string = r"(\w+)_VAR(\d+)_NAME"

    # find all <data_type>_VAR<n>_NAME keys in the conf files
    data_types_and_indices = find_indices_in_config_section(r"(\w+)_VAR(\d+)_NAME",
                                                            config,
                                                            'config')

    # loop over all possible variables and add them to list
    for index, data_type_list in data_types_and_indices.items():

        # if specific data type is requested, only get that type
        if data_type:
            data_type_lower = data_type.lower()
            name, levels, thresh, extra = get_var_items(config, data_type, index, time_info)

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
            f_name, f_levels, f_thresh, f_extra = get_var_items(config, 'FCST', index, time_info)
            o_name, o_levels, o_thresh, o_extra = get_var_items(config, 'OBS', index, time_info)

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
    if input_string[0] == '"' and input_string[-1] == '"':
        return input_string[1:-1]

    return input_string

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



def get_time_from_file(logger, filepath, template):
    if os.path.isdir(filepath):
        return None

    se = StringExtract(logger, template, filepath)

    out = se.parse_template()
    if se:
        return out
    else:
        # check to see if zip extension ends file path, try again without extension
        for ext in VALID_EXTENSIONS:
            if filepath.endswith(ext):
                se = StringExtract(logger, template, filepath[:-len(ext)])
                out = se.parse_template()
                if se:
                    return out
        return None


def preprocess_file(filename, data_type, config):
    """ Decompress gzip, bzip, or zip files or convert Gempak files to NetCDF
        Args:
            @param filename: Path to file without zip extensions
            @param config: Config object
        Returns:
            Path to staged unzipped file or original file if already unzipped
    """
    if filename is None or filename == "":
        return None

    # if using python embedding for input, return the keyword
    if os.path.basename(filename) in ['PYTHON_NUMPY', 'PYTHON_XARRAY', 'PYTHON_PANDAS']:
            return os.path.basename(filename)

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
            run_g2c = GempakToCFWrapper(config, config.logger)
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

def run_stand_alone(filename, app_name):
    """ Used to allow MET tool wrappers to be run without using
    master_metplus.py
        Args:
            @param filename: Path to wrapper file with underscores, i.e.
            /path/to/pcp_combine_wrapper.py
            @param app_name: Name of wrapper with camel case, i.e.
            PcpCombine
        Returns:
            None
    """
    module_name = os.path.splitext(os.path.basename(filename))[0]
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus')

        config = pre_run_setup(filename, app_name)

        module = __import__(module_name)
        wrapper_class = getattr(module, app_name + "Wrapper")
        wrapper = wrapper_class(config, config.logger)

        process_list = [app_name]
        total_errors = run_metplus(config, process_list)

        post_run_cleanup(config, app_name, total_errors)

    except Exception as e:
        produtil.log.jlogger.critical(
            app_name + '  failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)

def template_to_regex(template, time_info, logger):
    in_template = re.sub(r'\.', '\\.', template)
    in_template = re.sub(r'{lead.*?}', '.*', in_template)
    sts = StringSub(logger,
                    in_template,
                    **time_info)
    return sts.do_string_sub()

def is_python_script(name):
    all_items = name.split(' ')
    if any(item.endswith('.py') for item in all_items):
        return True
    # python returns None when no explicit return statement is hit

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


if __name__ == "__main__":
    gen_init_list("20141201", "20150331", 6, "18")
