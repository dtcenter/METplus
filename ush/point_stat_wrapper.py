#!/usr/bin/env python

from __future__ import print_function
import os
import calendar
import time
import re
import sys
from collections import namedtuple
from collections import OrderedDict
import itertools
import copy
import pdb

import config_metplus
import met_util as util
import grid_to_obs_util as g2o_util
import produtil.setup
from command_builder import CommandBuilder
from string_template_substitution import StringSub

"""
Program Name: point_stat_wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET point_stat
History Log:  Initial version
Usage: point_stat_wrapper.py
Parameters: None
Input Files: netCDF data files
Output Files: ascii files
Condition codes: 0 for success, 1 for failure

"""


class PointStatWrapper(CommandBuilder):
    """! Wrapper to the MET tool, Point-Stat."""

    def __init__(self, p, logger):
        super(PointStatWrapper, self).__init__(p, logger)
        if logger is None:
            self.logger = util.get_logger(p)

        self.p = p
        self.ps_dict = self.create_point_stat_dict()

        # For building the argument string via
        # CommandBuilder:
        self.app_path = self.ps_dict['APP_PATH']
        self.app_name = self.ps_dict['APP_NAME']
        self.app_name = os.path.basename(self.app_path)
        self.outdir = ""
        self.outfile = ""
        self.args = []
        self.input_dir = ""
        self.param = ""
        # Conversion factor for hours to seconds
        self.HOURS_TO_SECONDS = 3600

    def create_point_stat_dict(self):
        """! Create a dictionary that holds all the values set in the
             METplus config file for the point-stat wrapper.

             Args:
                 None
             Returns:
                 ps_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Creating point-stat dictionary ...")
        ps_dict = dict()

        # directories
        ps_dict['APP_PATH'] = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                           'bin/point_stat')
        ps_dict['APP_NAME'] = os.path.basename(ps_dict['APP_PATH'])
        ps_dict['PROJ_DIR'] = self.p.getdir('PROJ_DIR')
        ps_dict['TMP_DIR'] = self.p.getdir('TMP_DIR')
        ps_dict['METPLUS_BASE'] = self.p.getdir('METPLUS_BASE')
        ps_dict['MET_BUILD_BASE'] = self.p.getdir('MET_BUILD_BASE')
        ps_dict['MET_INSTALL_DIR'] = self.p.getdir('MET_INSTALL_DIR')

        ps_dict['PARM_BASE'] = self.p.getdir('PARM_BASE')
        ps_dict['OUTPUT_BASE'] = self.p.getdir('OUTPUT_BASE')
        ps_dict['FCST_INPUT_DIR'] = self.p.getdir('FCST_INPUT_DIR')
        ps_dict['OBS_INPUT_DIR'] = self.p.getdir('OBS_INPUT_DIR')
        ps_dict['POINT_STAT_OUTPUT_DIR'] = \
            self.p.getdir('POINT_STAT_OUTPUT_DIR')

        # Configuration
        ps_dict['TIME_METHOD'] = self.p.getstr('config', 'TIME_METHOD')
        ps_dict['LOOP_METHOD'] = self.p.getstr('config', 'LOOP_METHOD')
        ps_dict['MODEL_NAME'] = self.p.getstr('config', 'MODEL_NAME')
        ps_dict['OBS_NAME'] = self.p.getstr('config', 'OBS_NAME')
        ps_dict['POINT_STAT_CONFIG_FILE'] = \
            self.p.getstr('config', 'POINT_STAT_CONFIG_FILE')
        ps_dict['REGRID_TO_GRID'] = self.p.getstr('config', 'REGRID_TO_GRID')
        ps_dict['POINT_STAT_GRID'] = self.p.getstr('config', 'POINT_STAT_GRID')

        ps_dict['POINT_STAT_POLY'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_POLY'))
        ps_dict['POINT_STAT_STATION_ID'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_STATION_ID'))
        ps_dict['POINT_STAT_MESSAGE_TYPE'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_MESSAGE_TYPE'))

        # Retrieve YYYYMMDD begin and end time
        ps_dict['BEG_TIME'] = self.p.getstr('config', 'BEG_TIME')[0:8]
        ps_dict['END_TIME'] = self.p.getstr('config', 'END_TIME')[0:8]
        ps_dict['START_HOUR'] = self.p.getstr('config', 'START_HOUR')
        ps_dict['END_HOUR'] = self.p.getstr('config', 'END_HOUR')
        ps_dict['START_DATE'] = self.p.getstr('config', 'START_DATE')
        ps_dict['END_DATE'] = self.p.getstr('config', 'END_DATE')
        ps_dict['FCST_HR_START'] = self.p.getstr('config', 'FCST_HR_START')
        ps_dict['FCST_HR_END'] = self.p.getstr('config', 'FCST_HR_END')
        ps_dict['FCST_HR_INTERVAL'] = self.p.getstr('config',
                                                    'FCST_HR_INTERVAL')

        ps_dict['OBS_WINDOW_BEGIN'] = self.p.getstr('config',
                                                    'OBS_WINDOW_BEGIN')
        ps_dict['OBS_WINDOW_END'] = self.p.getstr('config', 'OBS_WINDOW_END')

        # Filename templates and regex patterns for input dirs and filenames
        ps_dict['FCST_INPUT_DIR_REGEX'] = \
            util.getraw_interp(self.p, 'regex_pattern', 'FCST_INPUT_DIR_REGEX')
        ps_dict['OBS_INPUT_DIR_REGEX'] = \
            util.getraw_interp(self.p, 'regex_pattern', 'OBS_INPUT_DIR_REGEX')
        ps_dict['FCST_INPUT_FILE_TMPL'] = \
            util.getraw_interp(self.p, 'filename_templates',
                               'FCST_INPUT_FILE_TMPL')
        ps_dict['OBS_INPUT_FILE_TMPL'] = \
            util.getraw_interp(self.p, 'filename_templates',
                               'OBS_INPUT_FILE_TMPL')

        # non-MET executables
        ps_dict['WGRIB2'] = self.p.getexe('WGRIB2')
        ps_dict['RM_EXE'] = self.p.getexe('RM_EXE')
        ps_dict['CUT_EXE'] = self.p.getexe('CUT_EXE')
        ps_dict['TR_EXE'] = self.p.getexe('TR_EXE')
        ps_dict['NCAP2_EXE'] = self.p.getexe('NCAP2_EXE')
        ps_dict['CONVERT_EXE'] = self.p.getexe('CONVERT_EXE')
        ps_dict['NCDUMP_EXE'] = self.p.getexe('NCDUMP_EXE')
        ps_dict['EGREP_EXE'] = self.p.getexe('EGREP_EXE')

        return ps_dict

    def main(self):

        """! Entry point for the point-stat wrapper

             Args:

             Returns:
                 None - invokes other methods
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Starting PointStatWrapper...")

        loop_method = self.ps_dict['LOOP_METHOD']
        if loop_method == 'processes':
            self.run_all_times()
        else:
            self.logger.error(cur_function + '|' + cur_filename +
                              '| ' + " loop method defined in configuration "
                                     "file is unsupported.  Only 'processes' "
                                     "is "
                                     "currently supported for this wrapper.")
            sys.exit(1)

    def run_all_times(self):
        """! Runs MET Point_ for all times indicated in the configuration
             file"""

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Running point-stat for all initialization times...")

        # Get a list of all the files in the model/fcst and obs directories
        # Determine if we are performing point_stat based on init times or
        # valid times.
        pairs_by_time_method = self.select_fcst_obs_pairs()

        # Build up the commands to run MET point_stat
        self.set_environment_variables()

        # Call point_stat for each matched pair of fcst/model and obs file
        # within the specified time window (by init time or by valid time).
        for pairs in pairs_by_time_method:
            # fcst file
            self.add_arg(pairs[0])
            # obs file
            self.add_arg(pairs[1])

            # MET point_stat config file
            self.set_param_file(self.ps_dict['POINT_STAT_CONFIG_FILE'])

            # Output directory
            self.set_output_dir(self.ps_dict['POINT_STAT_OUTPUT_DIR'])
            util.mkdir_p(self.outdir)

            cmd = self.get_command()
            self.logger.debug(cur_function + "|" + cur_filename
                              + "| Command to run MET point_stat: " + cmd)
            self.build()
            self.clear()

    def set_environment_variables(self):
        """! Set all the environment variables in the MET config
             file to the corresponding values in the MET+ config file.

             Args:

             Returns: None - invokes parent class, CommandBuilder add_env_var
                             to add each environment variable to run the

        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Setting all environment variables specified in "
                         "the MET config file...")

        # Set the environment variables
        self.add_env_var(b'MODEL_NAME', str(self.ps_dict['MODEL_NAME']))

        regrid_to_grid = str(self.ps_dict['REGRID_TO_GRID'])
        self.add_env_var(b'REGRID_TO_GRID', regrid_to_grid)
        os.environ['REGRID_TO_GRID'] = regrid_to_grid

        # MET accepts a list of values for POINT_STAT_POLY, POINT_STAT_GRID,
        # POINT_STAT_STATION_ID, and POINT_STAT_MESSAGE_TYPE. If these
        # values are not set in the MET+ config file, assign them to "[]" so
        # MET recognizes that these are empty lists, resulting in the
        # expected behavior.
        poly_str = str(self.ps_dict['POINT_STAT_POLY'])
        if not poly_str:
            self.add_env_var(b'POINT_STAT_POLY', "[]")
        else:
            poly = poly_str.replace("\'", "\"")
            self.add_env_var(b'POINT_STAT_POLY', poly)

        grid_str = str(self.ps_dict['POINT_STAT_GRID'])
        if not grid_str:
            self.add_env_var(b'POINT_STAT_GRID', "[]")
        else:
            # grid = grid_str.replace("\'", "\"")
            grid = '"' + grid_str + '"'
            self.add_env_var(b'POINT_STAT_GRID', grid)

        sid_str = str(self.ps_dict['POINT_STAT_STATION_ID'])
        if not sid_str:
            self.add_env_var(b'POINT_STAT_STATION_ID', "[]")
        else:
            sid = sid_str.replace("\'", "\"")
            self.add_env_var(b'POINT_STAT_STATION_ID', sid)

        tmp_message_type = str(self.ps_dict['POINT_STAT_MESSAGE_TYPE'])
        # Check for "empty" POINT_STAT_MESSAGE_TYPE in MET+ config file and
        # set the POINT_STAT_MESSAGE_TYPE environment variable appropriately.
        if not tmp_message_type:
            self.add_env_var('POINT_STAT_MESSAGE_TYPE', "[]")
        else:
            # Not empty, set the POINT_STAT_MESSAGE_TYPE environment
            #  variable to the
            # message types specified in the MET+ config file.
            tmp_message_type = str(tmp_message_type).replace("\'", "\"")
            # Remove all whitespace
            tmp_message_type = ''.join(tmp_message_type.split())
            self.add_env_var(b'POINT_STAT_MESSAGE_TYPE', tmp_message_type)

        # Retrieve all the fcst and obs field values (name, level, options)
        # from the MET+ config file, passed into the MET config file via
        # the FCST_FIELD and OBS_FIELD environment variables.
        all_vars_list = util.parse_var_list(self.p)
        met_fields = util.reformat_fields_for_met(all_vars_list, self.logger)

        self.add_env_var(b'FCST_FIELD', met_fields.fcst_field)
        self.add_env_var(b'OBS_FIELD', met_fields.obs_field)

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var(b'OBS_WINDOW_BEGIN',
                         str(self.ps_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var(b'OBS_WINDOW_END', str(self.ps_dict['OBS_WINDOW_END']))

    def select_fcst_obs_pairs(self):
        """! Select file pairings of fcst and obs input files based on valid
             time:
              for NAM prepbufr files: (ymd + (cycle time - offset))
              for GDAS prepbufr files: ymdh
              for model file: ymd + fhr

             Args:

             Returns:
                 pairs_by_valid - a list of paired model/fcst and obs files
                                 (full filepath) that
                                 are selected based on valid time
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Selecting file pairings by valid time...")

        # Get fcst and obs files for all the requested forecast hours for
        # each initialization time within the start and end dates.
        fcst_files_info = self.create_input_file_info("fcst")
        obs_files_info = self.create_input_file_info("obs")

        # Use dictionary to store/organize obs and fcst files based on valid
        # times.  Key = valid time, Value = list of full_filepaths
        # associated with this valid time.
        obs_dict_by_valid = dict()
        fcst_dict_by_valid = dict()

        for fcst in fcst_files_info:
            if fcst.valid_time in fcst_dict_by_valid:
                fcst_dict_by_valid[fcst.valid_time].append(
                    fcst.full_filepath)
            else:
                # unique key, create a new list for this key and add the
                # first full filepath
                fcst_paths = list()
                fcst_paths.append(fcst.full_filepath)
                fcst_dict_by_valid[fcst.valid_time] = fcst_paths

        for obs in obs_files_info:
            if obs.valid_time in obs_dict_by_valid:
                # Valid time already encountered, enter this obs path
                # to the list of obs paths
                obs_dict_by_valid[obs.valid_time].append(obs.full_filepath)
            else:
                # New key/valid time
                obs_paths = list()
                obs_paths.append(obs.full_filepath)
                obs_dict_by_valid[obs.valid_time] = obs_paths

        # Now get paired fcst and obs files
        fcst_obs_pairs = []
        for valid_time, fcst_files in fcst_dict_by_valid.iteritems():
            if valid_time in obs_dict_by_valid:
                obs_files = obs_dict_by_valid[valid_time]
                paired_paths = list(itertools.product(fcst_files, obs_files))
                fcst_obs_pairs.extend(paired_paths)

        return fcst_obs_pairs

    def create_input_file_info(self, file_type):
        """! Consolidate all the relevant information on the input files
             such as full filepath, date (ymd or ymdh), and cycle and offset
             times (if applicable/available from filename), and the valid time.


             Args:
                 file_type   - either "fcst" (model) or "obs"
             Returns:
                consolidated_file_info - a list of named tuples containing
                                         information useful for determining
                                         the valid time of the file:
                                         full_filepath, date (ymd or ymdh),
                                         and offset/fhr if
                                         available/applicable.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Creating file information for model/fcst or obs...")

        # Determine which files are within the valid time window.
        # Whenever there is more than one fcst file with the same valid time,
        # keep it, because we want to perform verification for all fcst/model
        # forecast hours.
        time_method = self.ps_dict['TIME_METHOD']
        valid_start = self.ps_dict['START_DATE']
        valid_end = self.ps_dict['END_DATE']

        fhr_start = self.ps_dict['FCST_HR_START']
        fhr_end = self.ps_dict['FCST_HR_END']
        fhr_interval = self.ps_dict['FCST_HR_INTERVAL']

        fhr_start_secs = int(fhr_start) * self.HOURS_TO_SECONDS
        fhr_end_secs = int(fhr_end) * self.HOURS_TO_SECONDS
        last_fhr = fhr_end_secs + 1
        fhr_interval_secs = int(fhr_interval) * self.HOURS_TO_SECONDS
        date_start = self.convert_date_strings_to_unix_times(str(valid_start))
        date_end = self.convert_date_strings_to_unix_times(str(valid_end))
        all_valid_times = []
        all_dates = []
        all_fhrs = []
        for cur_fhr in range(fhr_start_secs, last_fhr, fhr_interval_secs):
            all_fhrs.append(cur_fhr)

        # create a list of tuples: date (yyyymmdd) and forecast hour (both
        # in seconds) to represent all the valid times of interest.
        if time_method == 'BY_VALID':
            # Note: xrange will NO LONGER be available in Python 3.x,
            # only range() will be available.
            for cur_date in range(date_start, date_end, fhr_interval_secs):
                for cur_fhr in range(fhr_start_secs, last_fhr,
                                     fhr_interval_secs):
                    cur_init_time = cur_date - cur_fhr
                    if cur_init_time not in all_dates:
                        all_dates.append(cur_init_time)
                all_valid_times.append(cur_date)

        elif time_method == 'BY_INIT':
            for cur_date in range(date_start, date_end, fhr_interval_secs):
                for cur_fhr in range(fhr_start_secs, last_fhr,
                                     fhr_interval_secs):
                    cur_valid_time = cur_date + cur_fhr
                    if cur_valid_time not in all_valid_times:
                        all_valid_times.append(cur_valid_time)
                all_dates.append(cur_date)

        if file_type == "fcst":
            # Get a list of all the model/fcst files
            dir_to_search = self.ps_dict['FCST_INPUT_DIR']
            fcst_file_tmpl = self.ps_dict['FCST_INPUT_FILE_TMPL']
            fcst_file_regex_tuple = self.create_filename_regex(fcst_file_tmpl)
            fcst_dir_regex = self.ps_dict['FCST_INPUT_DIR_REGEX']

            # Get a list of dates (YYYYMMDD or YYYYMMDDHH) from dated subdirs
            # (if data is not arranged
            # into dated subdirs, an empty list is returned).
            all_fcst_files = self.get_all_input_files(dir_to_search,
                                                      fcst_file_regex_tuple[0],
                                                      fcst_dir_regex)

            consolidated_file_info = self.get_input_within_time_window(
                file_type, all_dates, all_fhrs,
                all_fcst_files, fcst_file_regex_tuple)

        elif file_type == "obs":

            # Get a list of all the obs files
            dir_to_search = self.ps_dict['OBS_INPUT_DIR']
            obs_file_tmpl = self.ps_dict['OBS_INPUT_FILE_TMPL']
            obs_dir_regex = self.ps_dict['OBS_INPUT_DIR_REGEX']
            obs_file_regex_tuple = self.create_filename_regex(obs_file_tmpl)

            all_obs_files = self.get_all_input_files(dir_to_search,
                                                     obs_file_regex_tuple[0],
                                                     obs_dir_regex)
            consolidated_file_info = self.get_input_within_time_window(
                file_type, all_dates, all_fhrs,
                all_obs_files, obs_file_regex_tuple)
        else:
            self.logger.error(
                cur_filename + '|' + cur_function +
                '| Unsupported file type.  File type must be "fcst" or "obs"')
            sys.exit(1)

        return consolidated_file_info

    def get_input_within_time_window(self, input_file_type, all_dates_in_window,
                                     all_fhrs, all_input_files,
                                     input_regex_tuple):
        """! Filter the input files (fcst or obs) based on whether the
             date lies within the time window specified by the user
             (via start and end times, interval/step size, beginning forecast
             hour and ending forecast hour).  For files that fall within
             the time window, the full filepath and available time
             information (initialization time, cycle, lead, offset)
             are stored in a named tuple.

             Args:
                 @param input_file_type  - "fcst" or "obs"
                 @param all_dates_in_window - all the dates that comprise
                                              the user's time window
                 @param all_fhrs   - all the forecast hours in the time window
                 @param all_input_files - all the fcst or obs input files
                 @param input_regex_tuple     - the tuple containing the
                                                filename regex and the order
                                                of keywords for the date,cycle,
                                                offset and lead for the fcst/obs
                                                input file
             Returns:
                 consolidated_file_info  - a list of the named tuple,
                                           which contains the
                                           information for each file
                                           (i.e. the date and any combination of
                                           cycle, lead, and offset within
                                           the user's specified time window
                                           of interest).

        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Creating file information for model/fcst or obs...")

        consolidated_file_info = []

        InputFileInfo = namedtuple('InputFileInfo',
                                   'full_filepath, date, '
                                   'valid_time, cycle, lead')

        # Get the information for the fcst/model file
        # Create the regex for the full filepath, so we correctly
        # capture the date information from the dated subdirectories if
        # our data is organized by subdirectories with init dates.
        full_input_keywords = copy.deepcopy(input_regex_tuple[1])
        if input_file_type == 'fcst':
            fcst_dir_regex = self.ps_dict['FCST_INPUT_DIR_REGEX']
            if fcst_dir_regex:
                # If the data is organized by date subdirectories
                full_input_regex = '.*' + fcst_dir_regex + '/' + \
                                   input_regex_tuple[0]
                full_input_keywords.insert(0, 'init')
            else:
                full_input_regex = '.*' + str(input_regex_tuple[0])

        elif input_file_type == 'obs':
            obs_dir_regex = self.ps_dict['OBS_INPUT_DIR_REGEX']
            if obs_dir_regex:
                # If the data is organized by date subdirectories
                full_input_regex = '.*' + obs_dir_regex + '/' +\
                                   input_regex_tuple[0]
                full_input_keywords.insert(0, 'init')

            else:
                full_input_regex = '.*/' + input_regex_tuple[0]

        if all_input_files:
            regex_match = re.compile(full_input_regex)
            for input_file in all_input_files:
                match = re.match(regex_match, input_file)
                if input_file_type == 'fcst':
                    time_info_tuple = \
                        self.get_time_info_from_file(match,
                                                     full_input_regex,
                                                     full_input_keywords)
                elif input_file_type == 'obs':
                    time_info_tuple = \
                            self.get_time_info_from_file(match,
                                                         full_input_regex,
                                                         full_input_keywords)

                # Determine if this file's valid time is one of the
                # valid times of interest and corresponds to
                # the expected forecast hour (based on forecast hour start
                # and forecast hour interval).  If so, then consolidate
                # the time info into the InputFileInfo tuple.
                if time_info_tuple.date in all_dates_in_window:
                    input_file_info = InputFileInfo(input_file,
                                                    time_info_tuple.date,
                                                    time_info_tuple.valid,
                                                    time_info_tuple.
                                                    cycle,
                                                    time_info_tuple.lead)
                    consolidated_file_info.append(input_file_info)
        else:
            self.logger.error(cur_function + '|' + cur_filename + '| '
                              ' No input files for ' + input_file_type +
                              ' found in '
                              'the specified input directory. '
                              'Please verify that data '
                              'files are present and the '
                              'input directory path in '
                              'the config file is correct.')
            sys.exit(1)

        return consolidated_file_info

    def get_all_input_files(self, dir_to_search, input_file_regex,
                            input_dir_regex):
        """! Get all the input files (obs or fcst) based on the regular
             expression defined in the METplus configuration file.

             Args:
                 @param dir_to_search:     The directory where the input files
                                           reside.
                 @param input_file_regex:  The regular expression of the
                                           input fcst or obs file
                 @param input_dir_regex:   The regular expression for the
                                           input directory (if input data
                                           is organized into dated directories).
            Returns:
                 all_input_files:  a list of all the fcst or obs input files
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            cur_function + '|' + cur_filename + '| ' +
            "Retrieving all forecast or obs input files")
        all_input_files = []

        # Get a list of dates(YYYYMMDD or YYYYMMDDHH)
        # from dated subdirs (if data is not arranged
        # into dated subdirs, an empty list is returned).
        if input_dir_regex:
            fcst_date_dirs = g2o_util.get_date_from_path(dir_to_search,
                                                         input_dir_regex)
            if fcst_date_dirs:
                for fcst_entry in fcst_date_dirs:
                    dir_to_search = fcst_entry.subdir_filepath
                    input_files_in_subdirs = util.get_files(dir_to_search,
                                                            input_file_regex,
                                                            self.logger)
                    if input_files_in_subdirs:
                        all_input_files.extend(input_files_in_subdirs)
        else:
            # Files contain date information in the filename.
            all_input_files = util.get_files(dir_to_search, input_file_regex,
                                             self.logger)
        return all_input_files

    def get_time_info_from_file(self, match_from_regex, full_input_regex,
                                full_input_keywords):
        """! Determine the date and the valid time.

             Args:
               @param  match_from_regex - the match object returned from the
                                          regex match
               @param full_input_regex -       the file regex (full)
                                          containing the ordering
                                          of the date, cycle, offset, and
                                          lead for the fcst/obs input
                                          file.
               @param full_input_keywords - a list of all the keywords,
                                            including the init time from
                                            any date subdirectories
             Returns:
                   file_time_info - a named tuple containing the date (ymd
                   or ymdh), and cycle time for obs file,
                   or fhr if fcst file.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            cur_function + '|' + cur_filename + '| ' +
            "Retrieving time information for file")

        TimeInfo = namedtuple('TimeInfo', 'date, valid, cycle, lead')

        # We are only capturing the date, cycle, and lead time in the
        # this named tuple.  We don't need the offset for calculating
        # any other times elsewhere, so we will omit it.
        if not match_from_regex:
            # No match, filename format is unexpected.
            self.logger.error(cur_function + '|' + cur_filename +
                              ' filename does not match expected format, '
                              'please check your filename regex in the '
                              'configuration file. Exiting...')
            sys.exit(1)
        elif match_from_regex.lastindex == 4:
            # We have a date, cycle, lead, and offset
            # Get the index of the keywords from the regex tuple that
            # was passed in as an argument, so we preserve the order
            # of the cycle, offset, and lead in the filename.

            # We are assuming that since there are 4 matches, the
            # first one is the date derived from the subdirectory name.
            date_str = str(match_from_regex.group(1))

            # Enumerate the list of keywords embedded in the filename to
            # get the ordering so we can assign the correct value to the
            # cycle, offset, and lead.

            # Initialize the date, cycle, lead, and offset strings to None,
            # and xxx_secs to 0
            cycle_str = None
            offset_str = None
            lead_str = None
            cycle_index = None
            lead_index = None
            offset_index = None
            cycle_secs = 0
            offset_secs = 0
            lead_secs = 0

            for i, x in enumerate(full_input_keywords):
                if x == 'cycle':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    cycle_index = i + 1
                elif x == 'offset':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    offset_index = i + 1
                elif x == 'lead':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    lead_index = i + 1

            if cycle_index:
                cycle_str = match_from_regex.group(cycle_index)
                cycle_secs = int(cycle_str) * self.HOURS_TO_SECONDS

            if offset_index:
                offset_str = match_from_regex.group(3)
                offset_secs = self.HOURS_TO_SECONDS * int(offset_str)

            # For future case where a lead is used in conjunction with
            # date and either cycle or offset:
            if lead_index:
                lead_str = match_from_regex.group(lead_index)
                lead_secs = int(lead_str) * self.HOURS_TO_SECONDS

            cycle = match_from_regex.group(cycle_index)
            offset_str = match_from_regex.group(offset_index)
            lead_str = match_from_regex.group(lead_index)
            offset_secs = self.HOURS_TO_SECONDS * int(offset_str)
            unix_date = self.convert_date_strings_to_unix_times(
                date_str)
            cycle_secs = int(cycle) * self.HOURS_TO_SECONDS
            lead_secs = int(lead_str) * self.HOURS_TO_SECONDS
            valid_time_unix = unix_date + (cycle_secs - offset_secs + lead_secs)
            file_time_info = TimeInfo(unix_date, valid_time_unix, cycle_secs,
                                      lead_secs)
        elif match_from_regex.lastindex == 3:
            # We could have a combination of any three of the following:
            # date, cycle, lead, offset
            # Enumerate the list of keywords embedded in the filename to
            # get the ordering so we can assign the correct value to the
            # cycle, offset, and lead.

            # Initialize the date, cycle, lead, and offset strings to None
            # and xxx_secs to 0
            date_str = None
            cycle_str = None
            offset_str = None
            lead_str = None
            date_index = None
            cycle_index = None
            lead_index = None
            offset_index = None
            cycle_secs = 0
            offset_secs = 0
            lead_secs = 0

            for i, x in enumerate(full_input_keywords):
                if x == 'valid' or x == 'init':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    date_index = i + 1
                elif x == 'cycle':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    cycle_index = i + 1
                elif x == 'offset':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    offset_index = i + 1
                elif x == 'lead':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    lead_index = i + 1

            if date_index:
                date_str = match_from_regex.group(date_index)
                unix_date = self.convert_date_strings_to_unix_times(
                    date_str)
            else:
                self.logger.error(cur_filename + "|" + cur_function + "|" +
                                  "No date information available.  Exiting.")
                sys.exit(1)

            if cycle_index:
                cycle_str = match_from_regex.group(cycle_index)
                cycle_secs = int(cycle_str) * self.HOURS_TO_SECONDS

            if offset_index:
                offset_str = match_from_regex.group(3)
                offset_secs = self.HOURS_TO_SECONDS * int(offset_str)

            # For future case where a lead is used in conjunction with
            # date and either cycle or offset:
            if lead_index:
                lead_str = match_from_regex.group(lead_index)
                lead_secs = int(lead_str) * self.HOURS_TO_SECONDS

            valid_time_unix = unix_date + cycle_secs - offset_secs

            file_time_info = TimeInfo(unix_date, valid_time_unix, cycle_secs,
                                      lead_secs)

        elif match_from_regex.lastindex == 2:
            # We most likely have a fhr/cycle hour, and offset hr
            # or we could have a combination of any two of the following:
            # date, cycle, lead, offset

            #Initialize the date, cycle, lead, and offset strings to None
            # and xxx_secs to 0
            date_str = None
            cycle_str = None
            offset_str = None
            lead_str = None
            date_index = None
            cycle_index = None
            lead_index = None
            offset_index = None
            cycle_secs = 0
            offset_secs = 0
            lead_secs = 0

            for i, x in enumerate(full_input_keywords):
                if x == 'valid' or x == 'init':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    date_index = i + 1
                elif x == 'cycle':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    cycle_index = i + 1
                elif x == 'offset':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    offset_index = i + 1
                elif x == 'lead':
                    # Add one to the index, because
                    # the 0th regex group is the entire matched string.
                    lead_index = i + 1

            if date_index:
                date_str = match_from_regex.group(date_index)
                unix_date = self.convert_date_strings_to_unix_times(
                    date_str)

            if cycle_index:
                cycle_str = match_from_regex.group(cycle_index)
                cycle_secs = int(cycle_str) * self.HOURS_TO_SECONDS

            if offset_index:
                offset_str = match_from_regex.group(3)
                offset_secs = self.HOURS_TO_SECONDS * int(offset_str)

            # For future case where a lead is used in conjunction with
            # date and either cycle or offset:
            if lead_index:
                lead_str = match_from_regex.group(lead_index)
                lead_secs = int(lead_str) * self.HOURS_TO_SECONDS

            date_str = str(match_from_regex.group(2))
            fhr_cycle_hr = int(match_from_regex.group(1))
            fhr_cycle = self.HOURS_TO_SECONDS * fhr_cycle_hr
            unix_date = self.convert_date_strings_to_unix_times(date_str)
            valid_time_unix = unix_date + fhr_cycle
            file_time_info = TimeInfo(unix_date, valid_time_unix, fhr_cycle,
                                      None)

        elif match_from_regex.lastindex == 1:
            # We only have date in ymdh, which we use as a valid
            # time.
            date_str = str(match_from_regex.group(1))
            unix_date = self.convert_date_strings_to_unix_times(date_str)
            valid_time_unix = unix_date
            file_time_info = TimeInfo(unix_date, valid_time_unix, None, None)

        return file_time_info

    def convert_date_strings_to_unix_times(self, date_string):
        """! Convert any YYYYMMDD or YYYYMMDDHH date string to Unix time


             Args:
                 date_string - The date string in YYYYMMDD or YYYYMMDDHH format
             Returns:
                 unix_time - the Unix time corresponding to the YYYYMMDD
                             or YYYYMMDDHH string
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            cur_function + '|' + cur_filename + '| ' +
            "Converting date strings to unix times")

        if len(date_string) == 8:
            time_tuple = \
                time.strptime(date_string, "%Y%m%d")
            unix_time = calendar.timegm(time_tuple)
        elif len(date_string) == 10:
            time_tuple = \
                time.strptime(date_string, "%Y%m%d%H")
            unix_time = calendar.timegm(time_tuple)
        else:
            self.logger.error(cur_filename + '|' + cur_function +
                              '|: The date format does not match any '
                              'YMD or YMDh format. ')
            sys.exit(1)

        return unix_time

    def reformat_grid_id(self, grid_id):
        """!Reformat the grid id (POINT_STAT_GRID value in the configuration
            file.)

            Args:
                grid_id      - the grid_id of the grid to use in regridding

            Returns:
                reformatted_id - the grid id reformatted based on
                the numerical
                                value portion of the grid id defined
                                in the
                                configuration file (POINT_STAT_GRID)
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and
        # method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Do reformatting
        match = re.match(r'G([0-9]{1,3})', grid_id)
        if match:
            number = match.group(1)
            reformatted_id = 'G' + number.zfill(3)
        else:
            # Unexpected format
            self.logger.error(
                cur_function + '|' + cur_filename
                + '|' + 'Grid id in unexpected format of Gn or '
                        'Gnn, please check again. Exiting...')
            sys.exit(1)

        return reformatted_id

    def clear(self):
        super(PointStatWrapper, self).clear()
        self.args = []
        self.input_dir = ""
        self.outdir = ""
        self.outfile = ""
        self.param = ""

    def get_command(self):
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        cmd = " " + self.app_path + " "
        if self.args:
            # for a in self.args:
            cmd += self.args[0] + " " + self.args[1]

        if self.param != "":
            cmd += " " + self.param + " "

        if self.outdir != "":
            cmd += "-outdir " + self.outdir

        return cmd

    def create_filename_regex(self, tmpl):
        """! Creates the regex of the forecast or reference filename as defined
             in the filename_template section of the config file.

           Args:
               @param tmpl - The filename template describing the forecast or
                             reference input track file (full filepath)

           Returns:
               tuple of two values:
               input_file_regex - A regex string representing the filename.
                                  This will be useful when filtering based on
                                  date, region, or cyclone.
               keywords_ordered -  A list of keywords, in the order in which
                                   they were found in the template string.
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename +
            ":Generating the filename regex from the filename_templates "
            "section.")

        # To filter files on the criteria of date, region, or cyclone
        # (or any combination). Use dummy values for the region and cyclone,
        # to create a string template
        # substitution object. This string template substitution
        # object will be used to
        # replace the key-values in the filename template with its
        #  corresponding regex.
        offset = '00'
        cycle = '00'
        lead = '00'
        # support either init or valid time in the filename
        init = '20170704'
        valid = '2017070412'

        # The string template substitution object will be initialized
        # based on the combination of the keywords have been specified in the
        # filename_templates section: init/valid, cyclone, offset, lead
        init_match = re.match(r'.*\{init\?fmt=(.*?)\}.*', tmpl)
        valid_match = re.match(r'.*\{valid\?fmt=(.*?)\}.*', tmpl)

        # date (YYYYMMDD or YYYYMMDDHH) is either an initialization
        # time or valid time
        keyword_index = dict()
        kwargs = dict()
        if init_match:
            kwargs['init'] = init
        elif valid_match:
            kwargs['valid'] = valid
        else:
            # No init or valid time in name, this is possible as the
            # date information can be found in the subdirectory name.
            # Just in case, log a warning message and continue.
            self.logger.info(cur_filename + "|" +
                             cur_function + '|: No date information was found '
                                            'in the filename template section.'
                                            'Assuming date information was '
                                            'retrieved from a dated '
                                            'subdirectory.')
        offset_match = re.match(r'.*\{offset\?fmt=(.*?)\}', tmpl)
        cycle_match = re.match(r'.*\{cycle\?fmt=(.*?)\}', tmpl)
        lead_match = re.match(r'.*\{lead\?fmt=(.*?)\}', tmpl)

        # Rather than having multiple if-elif to account for every
        # possible combination of
        # keywords in a filename_template, store the keywords in
        # a dictionary and use
        # **kwargs to invoke StringSub with this dictionary of keyword
        #  argument. Determine
        # the order in which the keywords appear in the
        # filename_template and order
        # the keywords, to facilitate filtering.
        if init_match:
            [(m.start(), m.end()) for m in
             re.finditer(r".*\{init\?fmt=(.*?)\}", tmpl)]
            keyword_index['init'] = m.start(1)
        if valid_match:
            [(m.start(), m.end()) for m in
             re.finditer(r".*\{valid\?fmt=(.*?)\}", tmpl)]
            keyword_index['valid'] = m.start(1)
        if cycle_match:
            kwargs['cycle'] = cycle
            [(m.start(), m.end()) for m in
             re.finditer(r".*\{cycle\?fmt=(.*?)\}", tmpl)]
            keyword_index['cycle'] = m.start(1)
        if offset_match:
            kwargs['offset'] = offset
            [(m.start(), m.end()) for m in
             re.finditer(r".*\{offset\?fmt=(.*?)\}", tmpl)]
            keyword_index['offset'] = m.start(1)
        if lead_match:
            kwargs['lead'] = lead
            [(m.start(), m.end()) for m in
             re.finditer(r".*\{lead\?fmt=(.*?)\}", tmpl)]
            keyword_index['lead'] = m.start(1)
        string_sub = StringSub(self.logger, tmpl, **kwargs)

        input_file_regex = string_sub.create_grid2obs_regex()

        # Get a list of the keywords in the order in which they appeared in the
        # filename_template description
        ordered = OrderedDict(
            sorted(keyword_index.items(), key=lambda t: t[1]))
        keywords_ordered = ordered.keys()

        return input_file_regex, keywords_ordered


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='point_stat',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='point_stat')
        produtil.log.postmsg('PointStatWrapper  is starting')

        # Read in the configuration object conf
        conf = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = conf.getdir('MET_BASE')

        PSW = PointStatWrapper(conf, logger=None)
        PSW.main()
        produtil.log.postmsg('PointStatWrapper completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'point_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
