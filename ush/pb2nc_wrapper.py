#!/usr/bin/env python

from __future__ import print_function, unicode_literals
import sys
import os
import re
import time
import calendar
from collections import namedtuple
from command_builder import CommandBuilder
import config_metplus
import met_util as util
import produtil.setup
from string_template_substitution import StringSub

"""
Program Name: PB2NC_Wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET tool PB2NC
History Log:  Initial version
Usage: pb2nc_wrapper.py
Parameters: None
Input Files: prepBUFR data files
Output Files: netCDF files
Condition codes: 0 for success, 1 for failure
"""


class PB2NCWrapper(CommandBuilder):
    """! Wrapper to the MET tool pb2nc which converts prepbufr files
         to NetCDF for MET's point_stat tool can recognize.
    """
    def __init__(self, p, logger):
        super(PB2NCWrapper, self).__init__(p, logger)
        self.p = p
        if logger is None:
            self.logger = util.get_logger(p)
        self.pb_dict = self.create_pb_dict()

        self.app_path = self.pb_dict['APP_PATH']
        self.app_name = self.pb_dict['APP_NAME']
        self.args = []

        # Conversion of hours to seconds
        # pylint:disable=invalid-name
        # Need to set constant value, most Pythonic way according to
        # Stack-Overflow is to set attribute.
        self.HOURS_TO_SECONDS = 3600

    def create_pb_dict(self):
        """! Create a data structure (dictionary) that contains all the
        values set in the configuration files

             Args:

             Returns:
                pb_dict  - a dictionary containing the settings in the
                configuration files (that aren't in the
                           metplus_data, metplus_system, and metplus_runtime
                           config files.
        """
        pb_dict = dict()

        # Directories
        pb_dict['APP_PATH'] = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                           'bin/pb2nc')
        pb_dict['APP_NAME'] = os.path.basename(pb_dict['APP_PATH'])
        pb_dict['PROJ_DIR'] = self.p.getdir('dir', 'PROJ_DIR')
        pb_dict['TMP_DIR'] = self.p.getdir('dir', 'TMP_DIR')
        pb_dict['METPLUS_BASE'] = self.p.getdir('dir', 'METPLUS_BASE')
        pb_dict['MET_BUILD_BASE'] = self.p.getdir('dir', 'MET_BUILD_BASE')
        pb_dict['MET_INSTALL_DIR'] = self.p.getdir('dir', 'MET_INSTALL_DIR')
        pb_dict['PREPBUFR_DATA_DIR'] = self.p.getstr('dir','PREPBUFR_DATA_DIR')
        pb_dict['PREPBUFR_MODEL_DIR_NAME'] = \
            self.p.getstr('dir', 'PREPBUFR_MODEL_DIR_NAME')
        pb_dict['PB2NC_OUTPUT_DIR'] = self.p.getstr('dir', 'PB2NC_OUTPUT_DIR')

        pb_dict['PARM_BASE'] = self.p.getdir('dir', 'PARM_BASE')
        pb_dict['OUTPUT_BASE'] = self.p.getstr('dir', 'OUTPUT_BASE')

        # Configuration
        pb_dict['TIME_METHOD'] = self.p.getstr('config', 'TIME_METHOD')
        pb_dict['PB2NC_CONFIG_FILE'] = self.p.getstr('config', 'PB2NC_CONFIG_FILE')
        pb_dict['PB2NC_MESSAGE_TYPE'] = util.getlist(self.p.getstr('config', 'PB2NC_MESSAGE_TYPE'))
        pb_dict['VERTICAL_LOCATION'] = self.p.getstr('config', 'VERTICAL_LOCATION')

        grid_id = self.p.getstr('config', 'PB2NC_GRID')
        if grid_id.startswith('G'):
            # Reformat grid ids that begin with 'G' ( G10, G1, etc.) to format
            # Gnnn
            pb_dict['PB2NC_GRID'] = self.reformat_grid_id(grid_id)
        else:
            pb_dict['PB2NC_GRID'] = grid_id

        pb_dict['PB2NC_POLY'] = self.p.getstr('config', 'PB2NC_POLY')
        pb_dict['PB2NC_STATION_ID'] = util.getlist(self.p.getstr('config', 'PB2NC_STATION_ID'))

        # Retrieve YYYYMMDD begin and end time
        pb_dict['BEG_TIME'] = self.p.getstr('config', 'BEG_TIME')[0:8]
        pb_dict['END_TIME'] = self.p.getstr('config', 'END_TIME')[0:8]
        pb_dict['INTERVAL_TIME'] = \
            self.p.getstr('config', 'INTERVAL_TIME')[0:2]
        pb_dict['OBS_BUFR_VAR_LIST'] = util.getlist(
            self.p.getstr('config', 'OBS_BUFR_VAR_LIST'))

        pb_dict['START_HOUR'] = self.p.getstr('config', 'START_HOUR')
        pb_dict['END_HOUR'] = self.p.getstr('config', 'END_HOUR')
        pb_dict['START_DATE'] = self.p.getstr('config', 'START_DATE')
        pb_dict['END_DATE'] = self.p.getstr('config', 'END_DATE')
        pb_dict['TIME_SUMMARY_FLAG'] = self.p.getbool('config',
                                                      'TIME_SUMMARY_FLAG')
        pb_dict['TIME_SUMMARY_BEG'] = self.p.getstr('config',
                                                    'TIME_SUMMARY_BEG')
        pb_dict['TIME_SUMMARY_END'] = self.p.getstr('config',
                                                    'TIME_SUMMARY_END')
        pb_dict['TIME_SUMMARY_VAR_NAMES'] = util.getlist(
            self.p.getstr('conf', 'TIME_SUMMARY_VAR_NAMES'))
        pb_dict['TIME_SUMMARY_TYPES'] = util.getlist(
            self.p.getstr('config', 'TIME_SUMMARY_TYPES'))
        pb_dict['OVERWRITE_NC_OUTPUT'] = \
            self.p.getstr('config', 'OVERWRITE_NC_OUTPUT').lower()

        # Filename templates and regex patterns for input dirs and filenames
        pb_dict['NC_FILE_TMPL'] = self.p.getraw('filename_templates',
                                                'NC_FILE_TMPL')
        pb_dict['PREPBUFR_FILE_REGEX'] = self.p.getraw('regex_pattern',
                                                       'PREPBUFR_FILE_REGEX')
        pb_dict['PREPBUFR_DIR_REGEX'] = self.p.getraw('regex_pattern',
                                                      'PREPBUFR_DIR_REGEX')

        # non-MET executables
        pb_dict['WGRIB2'] = self.p.getdir('exe', 'WGRIB2')
        pb_dict['RM_EXE'] = self.p.getdir('exe', 'RM_EXE')
        pb_dict['CUT_EXE'] = self.p.getdir('exe', 'CUT_EXE')
        pb_dict['TR_EXE'] = self.p.getdir('exe', 'TR_EXE')
        pb_dict['NCAP2_EXE'] = self.p.getdir('exe', 'NCAP2_EXE')
        pb_dict['CONVERT_EXE'] = self.p.getdir('exe', 'CONVERT_EXE')
        pb_dict['NCDUMP_EXE'] = self.p.getdir('exe', 'NCDUMP_EXE')
        pb_dict['EGREP_EXE'] = self.p.getdir('exe', 'EGREP_EXE')

        return pb_dict

    def main(self):
        """! Main entry point to the pb2nc wrapper if running stand-alone"""

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        loop_method = self.p.getstr('config', 'LOOP_METHOD')
        if loop_method == 'processes':
            self.run_all_times()
        else:
            # For now, we only support running all times (loop method via
            # processes).
            self.logger.error('ERROR:|:' + cur_function + '|' + cur_filename +
                              '|' + 'Only the loop method of "processes" is ' +
                              'currently supported, please change the ' +
                              'LOOP_METHOD value in your config file.')
            sys.exit(1)

    def reformat_grid_id(self, grid_id):
        """!Reformat the grid id (MASK_GRID value in the configuration
            file.)

            Args:
                @param grid_id      - the grid_id of the grid to use in
                                      regridding

            Returns:
                reformatted_id - the grid id reformatted based on
                the numerical
                                value portion of the grid id defined
                                in the
                                configuration file (MASK_GRID)
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
                'ERROR |:' + cur_function + '|' + cur_filename +
                '|' + 'Grid id in unexpected format of Gn or ' +
                'Gnn, please check again. Exiting...')
            sys.exit(1)

        return reformatted_id

    def run_at_time(self):
        """! Stub, not yet implemented """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Run for one single initialization time...")

        self.logger.error("ERROR|:" + cur_function + '|' + cur_filename +
                          '|' + 'Not yet supported, only run_all_times() is ' +
                          'currently supported. Set LOOP_METHOD = ' +
                          '"processes" in your configuration file')
        sys.exit(1)

    def run_all_times(self):
        """! Run MET pb2nc for all times specified in the configuration file.
             Build up the arguments necessary for invoking pb2nc using the
             methods provided by CommandBuilder, or use overridden methods.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Convert prepbufr files to netCDF for all times...")

        # Environment variables
        # Set ENVs that are needed by the MET pb2nc config file
        self.set_input_dir(self.pb_dict['PREPBUFR_DATA_DIR'])
        grid_mask = str(self.pb_dict['PB2NC_GRID'])
        self.add_env_var(b'PB2NC_GRID', grid_mask)
        poly = str(self.pb_dict['PB2NC_POLY'])
        self.add_env_var(b'PB2NC_POLY', poly)
        station_id = str(self.pb_dict['PB2NC_STATION_ID'])
        self.add_env_var(b'PB2NC_STATION_ID', station_id)

        # Convert any lists into strings, so that when we run via
        # subprocess, the environment variables are handled as strings.
        # Need to do some pre-processing so that Python will use " and not '
        # because currently MET doesn't support single-quotes

        # PB2NC_MESSAGE_TYPE, PB2NC_STATION_ID, OBS_BUFR_VAR_LIST are different from other
        # variables.  For instance, if set to nothing:
        #          PB2NC_MESSAGE_TYPE =
        # then don't allow it to be converted to "", or else MET will
        # search for message type "" in the prepbufr file.
        tmp_message_type = self.pb_dict['PB2NC_MESSAGE_TYPE']
        # Check for "empty" PB2NC_MESSAGE_TYPE in MET+ config file and
        # set the PB2NC_MESSAGE_TYPE environment variable appropriately.
        if not tmp_message_type:
            self.add_env_var('PB2NC_MESSAGE_TYPE', "[]")
        else:
            # Not empty, set the PB2NC_MESSAGE_TYPE environment variable to the
            # message types specified in the MET+ config file.
            tmp_message_type = str(tmp_message_type).replace("\'", "\"")
            # Remove all whitespace
            tmp_message_type = ''.join(tmp_message_type.split())
            self.add_env_var(b'PB2NC_MESSAGE_TYPE', tmp_message_type)

        tmp_station_id = self.pb_dict['PB2NC_STATION_ID']
        if not tmp_station_id:
            self.add_env_var('PB2NC_STATION_ID', "[]")
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file.
            station_id_string = str(tmp_station_id).replace("\'", "\"")
            # Remove all whitespace
            station_id_string = ''.join(station_id_string.split())
            self.add_env_var(b'PB2NC_STATION_ID', station_id_string)

        tmp_obs_bufr = self.pb_dict['OBS_BUFR_VAR_LIST']
        if not tmp_obs_bufr:
            self.add_env_var(b'OBS_BUFR_VAR_LIST', "[]")
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file.
            tmp_obs_bufr_str = str(tmp_obs_bufr).replace("\'", "\"")
            tmp_obs_bufr_str = ''.join(tmp_obs_bufr_str.split())
            self.add_env_var(b'OBS_BUFR_VAR_LIST', tmp_obs_bufr_str)

        # Support for time summary was introduced with MET-6.1 release
        #
        if self.pb_dict['TIME_SUMMARY_FLAG']:
            flag = "True"
        else:
            flag = "False"

        self.add_env_var('TIME_SUMMARY_FLAG', flag)
        self.add_env_var('TIME_SUMMARY_BEG',
                         self.pb_dict['TIME_SUMMARY_BEG'])
        self.add_env_var(b'TIME_SUMMARY_END', self.pb_dict[
            'TIME_SUMMARY_END'])
        time_summary_var_names_str = str(
            self.pb_dict['TIME_SUMMARY_VAR_NAMES'])
        self.add_env_var(b'TIME_SUMMARY_VAR_NAMES', time_summary_var_names_str)
        time_summary_types_str = str(self.pb_dict['TIME_SUMMARY_TYPES'])
        self.add_env_var(b'TIME_SUMMARY_TYPES', time_summary_types_str)

        # Determine the files to convert based on init or valid start and
        # end times and a time interval.
        relevant_pb_files = self.get_pb_files_by_time()

        # Build the command to call MET pb2nc
        self.build_pb2nc_command(relevant_pb_files)

    def get_pb_files_by_time(self):
        """! Identify the prepbufr files that are within the specified time
             window and the specified time intervals between initialization
             times.

             Args:

             Returns:
                 files_of_interest : A list of the full filepaths
                                     corresponding to the files of interest
                                     (i.e. those files that are within the
                                     specified start and end times, and the
                                     appropriate interval times)

        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Filtering prepbufr files based on time (init or "
                         "valid).")

        # Create a list of times that are expected, based on
        # the begin, end, and interval date/times.
        dates_needed = []
        initial_start_date = \
            self.convert_date_strings_to_unix_times(self.pb_dict['START_DATE'])
        current_start_date = initial_start_date
        interval_time_str = self.pb_dict['INTERVAL_TIME']
        interval_time = int(interval_time_str) * self.HOURS_TO_SECONDS
        start_date_unix = self.convert_date_strings_to_unix_times(
            self.pb_dict['START_DATE'])
        end_date_unix = self.convert_date_strings_to_unix_times(
            self.pb_dict['END_DATE'])
        while start_date_unix <= current_start_date <= end_date_unix:
            dates_needed.append(current_start_date)
            current_start_date = current_start_date + interval_time

        # Iterate through the input prepbufr directories to determine the
        # init or valid times.
        # Get a list of all the sub-directories and files under the
        # PREPBUFR_DATA_DIR/PREPBUFR_MODEL_DIR_NAME
        dir_to_search = os.path.join(self.pb_dict['PREPBUFR_DATA_DIR'],
                                     self.pb_dict['PREPBUFR_MODEL_DIR_NAME'])
        pb_subdirs_list = util.get_dirs(dir_to_search)

        # Determine whether times are to be retrieved based on init times:
        # ymd + cycle hour or valid times: ymd + (cycle hour - offset)
        # initialize the time flag
        if self.pb_dict['TIME_METHOD'].lower() == 'by_init':
            time_flag = 'init'
        elif self.pb_dict['TIME_METHOD'].lower() == 'by_valid':
            time_flag = 'valid'
        else:
            # unsupported time method
            self.logger.error('ERROR|:' + cur_function + '|' + cur_filename +
                              ' Unrecognized time method, only BY_INIT or ' +
                              'BY_VALID are supported. Check the ' +
                              'TIME_METHOD setting in your configuration ' +
                              'file.')
            sys.exit(1)

        # Some prepbufr files are organized into YMD subdirectories with
        # the cycle and offset (fhr) times incorporated into their filenames.
        #
        # There are also prepbufr files that are not separated by YMD and
        # instead have the YMDh incorporated into their filenames.  Provide
        # support for both cases.
        files_within_time_criteria = []
        if pb_subdirs_list:
            for pb_subdir in pb_subdirs_list:
                # Retrieve the YMD from the subdirectory name
                dir_regex = self.pb_dict['PREPBUFR_DIR_REGEX']
                regex_search = re.compile(dir_regex)
                match = re.match(regex_search, pb_subdir)
                if match:
                    ymd = match.group(1)
                    regex_file = self.pb_dict['PREPBUFR_FILE_REGEX']
                    pb_files_list = util.get_files(pb_subdir, regex_file,
                                                   self.logger)
                    if pb_files_list:
                        # Calculate the init or valid time for each file, then
                        # determine if this is found in the list of times of
                        # interest, dates_needed[].
                        for pb_file in pb_files_list:
                            # Create the time information for this file, based
                            # on init time or valid time, as indicated by the
                            # time_flag.
                            pb_file_time_info = \
                                self.retrieve_pb_time_info(pb_file,
                                                           time_flag,
                                                           ymd)
                            if pb_file_time_info.pb_unix_time in dates_needed:
                                files_within_time_criteria.append(
                                    pb_file_time_info.full_filepath)

                    else:
                        # No files in subdirectory, continue to next
                        # subdirectory
                        self.logger.info('INFO:|' + cur_function + '|' +
                                         cur_filename + ' No files found in '
                                                        'current '
                                                        'subdirectory: ' +
                                         pb_subdir + ' continue checking '
                                                     'next available '
                                                     'subdirectory for files.')
                        continue

        else:
            # No subdirectories, only files, get the list of files to process
            # These files will have YMD incorporated in the filename.
            files_within_time_criteria = []
            pb_files_list = util.get_files(dir_to_search,
                                           self.pb_dict['PREPBUFR_FILE_REGEX'],
                                           self.logger)
            if not pb_files_list:
                self.logger.error('ERROR:|' + cur_function + '|' +
                                  cur_filename + ' No files were found.  '
                                                 'Check the path to '
                                                 'the prepbufr '
                                                 'data directory in your '
                                                 'configuration file.')
                sys.exit(1)
            else:
                for pb_file in pb_files_list:
                    pb_file_time_info = \
                        self.retrieve_pb_time_info(pb_file,
                                                   time_flag)
                    if pb_file_time_info.pb_unix_time in dates_needed:
                        files_within_time_criteria.append(
                            pb_file_time_info.full_filepath)

        return files_within_time_criteria

    def retrieve_pb_time_info(self, pb_file, time_method, date=None):
        """! Retrieve the time information (either init or valid time) from
             the prepbufr filename or the prepbufr filename and directory.

             Args:
                 @param pb_file -      The prepbufr file (full filepath) under
                                                         consideration
                 @param time_method - 'by_init' or 'by_valid'
                 @param date     - If applicable, the YMD derived from the
                                   subdir name
             Returns:
                 pb_file_time_info : A named tuple containing the full
                                    filepath and derived and calculated init
                                    or valid time (in seconds, Unix time)
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Retrieving the time info for the prepBufr file of "
                         "interest, based on init time (YMD + cycle) or valid"
                         "time (YMDH or [YMD + (cycle - offset)].")

        # pylint:disable=invalid-name
        # This is a named tuple, and follows the "standard" practice of
        # capitalizing the name of a named tuple, like a class name.
        PbFileTimeInfo = namedtuple('PbFileTimeInfo',
                                    'full_filepath, pb_unix_time')

        # Check if the filename has an offset
        match = re.match(r'.*tm([0-9]{2}).*', pb_file)
        if match:
            offset = match.group(1)
            offset_in_secs = int(offset) * self.HOURS_TO_SECONDS

            # Retrieve the cycle time
            cycle_match = re.match(r'.*t([0-9]{2})z.*', pb_file)
            if cycle_match:
                # Files contain information to derive init and valid times
                cycle = cycle_match.group(1)
                cycle_in_secs = int(cycle) * self.HOURS_TO_SECONDS

                # Convert init time and valid time to Unix time
                if len(date) == 8:
                    # ymd, cycle and offset
                    unix_cur_date = \
                        self.convert_date_strings_to_unix_times(date)
                    if time_method == 'init':
                        cur_init_unix = unix_cur_date + cycle_in_secs
                        pb_file_time_info = PbFileTimeInfo(pb_file,
                                                           cur_init_unix)
                    else:
                        cur_valid_unix = unix_cur_date + \
                                         (cycle_in_secs - offset_in_secs)
                        pb_file_time_info = PbFileTimeInfo(pb_file,
                                                           cur_valid_unix)

                else:
                    # ymdh, which is the valid time, use this as the init
                    # time for this prepbufr file, so no need to treat
                    # by_init and by_valid separately.
                    unix_pb_file_date = \
                        self.convert_date_strings_to_unix_times(date)
                    pb_file_time_info = PbFileTimeInfo(pb_file,
                                                       unix_pb_file_date)

            else:
                # Something is wrong, there should be a cycle time if
                # there is an offset time.
                self.logger.error('ERROR |' + cur_function + '|' +
                                  cur_filename + 'Expected cycle time not'
                                                 'found. This '
                                                 'data does not have '
                                                 'the expected prepbufr '
                                                 'filename, exiting...')
                sys.exit(1)
        else:
            # No offset, check for cycle time (these files correspond to
            # init times, use these for valid times as well)
            cycle_match = re.match(r'.*t([0-9]{2})z.*', pb_file)
            if cycle_match:
                cycle = cycle_match.group(1)
                cycle_in_secs = int(cycle) * self.HOURS_TO_SECONDS
                unix_date = self.convert_date_strings_to_unix_times(date)
                unix_pb_file_date = unix_date + cycle_in_secs
                pb_file_time_info = PbFileTimeInfo(pb_file, unix_pb_file_date)
            else:
                # no cycle or offset, the file contains YMDh information
                # in its filename corresponding to valid times.
                ymdh_match = re.match(r'.*(2[0-9]{9}).*', pb_file)
                if ymdh_match:
                    date = ymdh_match.group(1)
                    unix_date = self.convert_date_strings_to_unix_times(date)
                    pb_file_time_info = PbFileTimeInfo(pb_file,
                                                       unix_date)

        return pb_file_time_info

    def build_pb2nc_command(self, relevant_pb_files):
        """! Build the command to MET pb2nc

             Args:
                 @param relevant_pb_files - a list containing the relevant
                                            prepbufr files after applying a
                                            filtering by valid time or by
                                            init time.  Each item is a
                                            named tuple with the full filepath,
                                            date, and cycle hour of the file.
             Returns:
                 None - builds the command and invokes MET pb2nc
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Building MET pb2nc command...")

        # Create the call to MET pb2nc with the following format:
        # pb2nc \
        # /path/to/input/prepbufr_file (first file in
        # prepbufr_files_to_evaluate \
        # /path/to/output/netCDF_file \
        # /path/to/MET_pb2nc_config_file
        # -pbFile <list of remaining prepbufr files in the
        # prepbufr_files_to_evaluate
        # pylint:disable=simplifiable-if-statement
        # Expecting 'yes' or 'no' from user in config file.
        if self.pb_dict['OVERWRITE_NC_OUTPUT'] == 'yes':
            overwrite_flag = True
        else:
            overwrite_flag = False

        for relevant_pb_file in relevant_pb_files:
            pb_file = relevant_pb_file

            # Start building the pieces of the argument to invoke MET pb2nc if
            # the input file is within the start and end init times specified.
            # Input file with full path.
            # input_file = os.path.join(self.pb_dict['PREPBUFR_DATA_DIR'],
            #                         pb_file)
            input_file = pb_file
            self.add_arg(input_file)

            # Generate the output filename (with full path) based on the
            # file template specified in the config file
            pb_output_file_to_name = self.extract_prepbufr_file_info(
                relevant_pb_file)

            output_full_filename = self.generate_output_nc_filename(
                pb_output_file_to_name)

            # Run if overwrite_flag is True, or if the output
            # file doesn't already exist.
            if overwrite_flag or \
                    not util.file_exists(output_full_filename):
                self.pb_dict['OUTPUT_DIR_STRUCTURE'] = output_full_filename
                self.add_arg(output_full_filename)

                # Config file location
                self.set_param_file(self.pb_dict['PB2NC_CONFIG_FILE'])

                # For developer debugging
                # self.add_arg(' -index -v 4 -log /tmp/pb2nc.log')

                # Invoke MET pb2nc
                cmd = self.get_command()
                self.logger.debug('DEBUG|:' + cur_function + '|' +
                                  cur_filename + 'pb2nc called with: ' + cmd)
                self.build()
                self.logger.debug(
                    'DEBUG|:' + cur_function + '|' + cur_filename +
                    ' Finished running pb2nc...')
                self.clear()

                # pb2nc_cmd = \
                #     batchexe('sh')['-c', cmd].err2out()
                # run(pb2nc_cmd)

            else:
                self.logger.debug("DEBUG|:" + cur_function + '|' +
                                  cur_filename + ' Not overwriting existing '
                                                 'files, continue')

    def create_full_filepath(self, filename, subdir=None):
        """! Create the full filepath corresponding to this file.

            Args:
                @param filename   - filename of the file of interest
                @param subdir     - if this file is located in a dated subdir,
                then
                             include this, default is None.
            Returns:
                full_filepath - the full filepath for this file.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Creating full filepath for file" + filename)

        data_dir = self.pb_dict['PREPBUFR_DATA_DIR']
        if subdir:
            full_filepath = os.path.join(data_dir, subdir, filename)
        else:
            full_filepath = os.path.join(data_dir, filename)

        return full_filepath

    # pylint:disable=invalid-name
    # this method name adheres to "snake_case", is descriptive of what
    # it does, and conveys an action.
    def convert_date_strings_to_unix_times(self, date_string):
        """! Convert any YYYYMMDD or YYYYMMDDHH date string to Unix time
             Args:
                 @param date_string - The date string in YYYYMMDD or
                                      YYYYMMDDHH format
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
            "DEBUG|:" + cur_function + '|' + cur_filename + '| ' +
            "Converting date strings to unix times")
        if len(date_string) == 8:
            time_tuple = \
                time.strptime(date_string, "%Y%m%d")
            unix_time = calendar.timegm(time_tuple)
        elif len(date_string) == 10:
            time_tuple = \
                time.strptime(date_string, "%Y%m%d%H")
            unix_time = calendar.timegm(time_tuple)
        return unix_time

    def extract_prepbufr_file_info(self, pb_file):
        """! Extract date information on all prepbufr files in the specified
             input directory.  This information will facilitate the naming
             of output files.

        Args:
            @param pb_file - The prepbufr file(full filepath) undergoing
                              conversion to NetCDF
        Returns:
            prepbufr_file_info - information in the form
                                 of named tuples: full_filepath, ymd,
                                 cycle, offset for files that are in
                                 dated subdirectories (e.g.
                                 nam/nam.20170601/nam.t00z.prepbufr.tm03);
                                 full_filepath,
                                 ymdh
                                 for those which have the ymd
                                 information as part of their filename (
                                 e.g. prepbufr.gdas.2018010100)


        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Creating prepbufr file information")

        # For files like GDAS, there are no cycle and offset values in the
        # filename.  These will be set to None.
        PrepbufrFile = namedtuple('PrepbufrFile',
                                  'full_filepath, date, cycle, offset')

        # Check if this prepbufr data has the date in the subdirectory name
        # in the form of a dated subdirectory,
        # This is indicated by setting the directory regex, PREPBUFR_DIR_REGEX
        subdir_regex = self.pb_dict['PREPBUFR_DIR_REGEX']
        if subdir_regex:
            regex_compile = re.compile(subdir_regex)
            match = re.match(regex_compile, pb_file)
            if match:
                date = match.group(1)
            else:
                date = None

        # Check if the filename has an offset
        match = re.match(r'.*tm([0-9]{2}).*', pb_file)
        if match:
            offset = match.group(1)

            # Retrieve the cycle time
            cycle_match = re.match(r'.*t([0-9]{2})z.*', pb_file)
            if cycle_match:
                # Files contain information to derive init and valid times
                cycle = cycle_match.group(1)
                pb_file_info = PrepbufrFile(pb_file, date, cycle, offset)
            else:
                # Something is wrong, there should be a cycle time if
                # there is an offset time.
                self.logger.error('ERROR |' + cur_function + '|' +
                                  cur_filename + 'Expected cycle time not'
                                                 'found. This '
                                                 'data does not have '
                                                 'the expected prepbufr '
                                                 'filename, exiting...')
                sys.exit(1)
        else:
            # No offset, check for cycle time (these files correspond to
            # init times)
            cycle_match = re.match(r'.*t([0-9]{2})z.*', pb_file)
            if cycle_match:
                cycle = cycle_match.group(1)
                pb_file_info = PrepbufrFile(pb_file, date, cycle, None)
            else:
                # no cycle or offset, the file contains YMDh information
                # in its filename corresponding to valid times.
                ymdh_match = re.match(r'.*(2[0-9]{9}).*', pb_file)
                if ymdh_match:
                    date = ymdh_match.group(1)
                    pb_file_info = PrepbufrFile(pb_file, date, None, None)

        return pb_file_info

    def generate_output_nc_filename(self, prepbufr_file_info):
        """! Create the output netCDF filename as specified in the use
        case/custom configuration file.
             Args:
                 @param prepbufr_file_info - a list of the full filepaths of
                                             prepbufr data of interest.
             Returns:
                 a tuple:
                 nc_output_filepath - the full filepath
                 nc_output_filename - the filename follows the format
                                      specified in the configuration file
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug('DEBUG:|' + cur_function + '|' + cur_filename +
                          ' Generating output NetCDF file name...')

        # Get the output directory
        pb2nc_output_dir = self.pb_dict['PB2NC_OUTPUT_DIR']

        # Get the cycle hour and offset hour from the prepbufr file info named
        # tuple
        if prepbufr_file_info.cycle:
            # Get the cycle hour, offset hour and add the appropriate
            # prefix, validation ymd and .nc extension
            cycle = prepbufr_file_info.cycle
            offset = prepbufr_file_info.offset
            date = prepbufr_file_info.date

            string_sub = StringSub(self.logger, self.pb_dict['NC_FILE_TMPL'],
                                   init=str(date), cycle=cycle, offset=offset)
            nc_output_filename = string_sub.doStringSub()
            nc_output_filepath = os.path.join(pb2nc_output_dir,
                                              nc_output_filename)

        else:
            # Typically for files that aren't separated into dated
            # subdirectories, the date is incorporated in the filename.
            # Append the input file name with .nc extension
            # extract the filename portion of the full_filepath
            filename = os.path.basename(prepbufr_file_info.full_filepath)
            nc_output_filename = filename + ".nc"
            nc_output_filepath = os.path.join(pb2nc_output_dir,
                                              nc_output_filename)
        return nc_output_filepath

    def get_command(self):
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        cmd = " " + self.app_path + " "
        if self.args:
            for arg in self.args:
                cmd += arg + " "

        if self.param != "":
            cmd += " " + self.param + " "

        return cmd


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='pb2nc',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='pb2nc')
        produtil.log.postmsg('pb2nc is starting')

        # Read in the configuration object CONFIG_INST
        CONFIG_INST = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        PB2NC = PB2NCWrapper(CONFIG_INST, logger=None)
        PB2NC.main()
        produtil.log.postmsg('pb2nc completed')
    except Exception as exception:
        produtil.log.jlogger.critical(
            'pb2nc failed: %s' % (str(exception),), exc_info=True)

        sys.exit(2)
