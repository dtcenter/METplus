#!/usr/bin/env python

from __future__ import print_function
import os
import calendar
import time
import re
import sys
from collections import namedtuple

import itertools

import config_metplus
import met_util as util
import produtil.setup
from command_builder import CommandBuilder

"""
Program Name: Point_Stat_Wrapper.py
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
        ps_dict['PROJ_DIR'] = self.p.getdir('dir', 'PROJ_DIR')
        ps_dict['TMP_DIR'] = self.p.getdir('dir', 'TMP_DIR')
        ps_dict['METPLUS_BASE'] = self.p.getdir('dir', 'METPLUS_BASE')
        ps_dict['MET_BUILD_BASE'] = self.p.getdir('dir', 'MET_BUILD_BASE')
        ps_dict['MET_INSTALL_DIR'] = self.p.getdir('dir', 'MET_INSTALL_DIR')

        ps_dict['PARM_BASE'] = self.p.getdir('dir', 'PARM_BASE')
        ps_dict['OUTPUT_BASE'] = self.p.getstr('dir', 'OUTPUT_BASE')
        ps_dict['FCST_INPUT_DIR'] = self.p.getstr('dir', 'FCST_INPUT_DIR')
        ps_dict['OBS_INPUT_DIR'] = self.p.getstr('dir', 'OBS_INPUT_DIR')
        ps_dict['POINT_STAT_OUTPUT_DIR'] = \
            self.p.getstr('dir', 'POINT_STAT_OUTPUT_DIR')

        # Configuration
        ps_dict['LOOP_METHOD'] = self.p.getstr('config', 'LOOP_METHOD')
        ps_dict['MODEL_NAME'] = self.p.getstr('config', 'MODEL_NAME')
        ps_dict['OBS_NAME'] = self.p.getstr('config', 'OBS_NAME')
        ps_dict['POINT_STAT_CONFIG_FILE'] = \
            self.p.getstr('config', 'POINT_STAT_CONFIG_FILE')
        ps_dict['REGRID_TO_GRID'] = self.p.getstr('config', 'REGRID_TO_GRID')
        grid_id = self.p.getstr('config', 'GRID_MASK')
        if grid_id.startswith('G'):
            # Reformat grid ids that begin with 'G' ( G10, G1, etc.) to format
            # Gnnn
            ps_dict['GRID_MASK'] = self.reformat_grid_id(grid_id)
        else:
            ps_dict['GRID_MASK'] = grid_id

        ps_dict['MASK_POLY'] = util.getlist(self.p.getstr('config',
                                                          'MASK_POLY'))

        # Retrieve YYYYMMDD begin and end time
        ps_dict['BEG_TIME'] = self.p.getstr('config', 'BEG_TIME')[0:8]
        ps_dict['END_TIME'] = self.p.getstr('config', 'END_TIME')[0:8]
        ps_dict['START_HOUR'] = self.p.getstr('config', 'START_HOUR')
        ps_dict['END_HOUR'] = self.p.getstr('config', 'END_HOUR')
        ps_dict['START_DATE'] = self.p.getstr('config', 'START_DATE')
        ps_dict['END_DATE'] = self.p.getstr('config', 'END_DATE')
        ps_dict['POINT_STAT_OUTPUT_PREFIX'] = \
            self.p.getstr('config', 'POINT_STAT_OUTPUT_PREFIX')
        # Filename templates and regex patterns for input dirs and filenames
        ps_dict['FCST_INPUT_FILE_REGEX'] = \
            self.p.getraw('regex_pattern', 'FCST_INPUT_FILE_REGEX')
        ps_dict['OBS_INPUT_FILE_REGEX'] = \
            self.p.getraw('regex_pattern', 'OBS_INPUT_FILE_REGEX')

        # non-MET executables
        ps_dict['WGRIB2'] = self.p.getdir('exe', 'WGRIB2')
        ps_dict['RM_EXE'] = self.p.getdir('exe', 'RM_EXE')
        ps_dict['CUT_EXE'] = self.p.getdir('exe', 'CUT_EXE')
        ps_dict['TR_EXE'] = self.p.getdir('exe', 'TR_EXE')
        ps_dict['NCAP2_EXE'] = self.p.getdir('exe', 'NCAP2_EXE')
        ps_dict['CONVERT_EXE'] = self.p.getdir('exe', 'CONVERT_EXE')
        ps_dict['NCDUMP_EXE'] = self.p.getdir('exe', 'NCDUMP_EXE')
        ps_dict['EGREP_EXE'] = self.p.getdir('exe', 'EGREP_EXE')

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
            self.logger.error("ERROR|:" + cur_function + '|' + cur_filename +
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

        # prefix to the output file generated by MET point_stat
        output_prefix = self.ps_dict['POINT_STAT_OUTPUT_PREFIX']
        if output_prefix:
            self.add_env_var(b'output_prefix', output_prefix)

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
            self.logger.debug("DEBUG:|" + cur_function + "|" + cur_filename
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
        self.add_env_var(b'MODEL_FCST', str(self.ps_dict['MODEL_NAME']))
        os.environ['MODEL_FCST'] = str(self.ps_dict['MODEL_NAME'])

        regrid_to_grid = str(self.ps_dict['REGRID_TO_GRID'])
        self.add_env_var(b'REGRID_TO_GRID', regrid_to_grid)
        os.environ['REGRID_TO_GRID'] = regrid_to_grid

        mask_poly_str = str(self.ps_dict['MASK_POLY'])
        mask_poly = mask_poly_str.replace("\'", "\"")
        self.add_env_var(b'MASK_POLY', mask_poly)
        os.environ['MASK_POLY'] = mask_poly

        self.add_env_var(b'GRID_MASK', self.ps_dict['GRID_MASK'])
        os.environ['GRID_MASK'] = self.ps_dict['GRID_MASK']

        # Retrieve all the fcst and obs field values (name, level, options)
        # from the MET+ config file, passed into the MET config file via
        # the FCST_FIELD and OBS_FIELD environment variables.
        all_vars_list = util.parse_var_list(self.p)
        met_fields = util.reformat_fields_for_met(all_vars_list, self.logger)

        self.add_env_var(b'FCST_FIELD', met_fields.fcst_field)
        self.add_env_var(b'OBS_FIELD', met_fields.obs_field)

    def reformat_fields_for_met(self, all_vars_list):
        """! Reformat the fcst or obs field values defined in the
             MET+ config file to the MET field dictionary.

             Args:
                 all_vars_list - The list of all variables/fields retrieved
                                 from the MET+ configuration file

             Returns:
                 met_fields - a named tuple containing the


        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                         "Reformatting field dictionary ...")

        # Named tuple (so we don't have to remember the order of the fields)
        # containing the string corresponding to the fcst or obs field's
        # key-values for the MET config file.
        MetFields = namedtuple("MetFields", "fcst_field, obs_field")

        # Two types of fields in the MET fields dictionary, fcst and obs. Use
        # this to create the key-value pairs.
        field_list = ['fcst', 'obs']
        fcst_field = ''
        obs_field = ''
        for var in all_vars_list:
            # Create the key-value pairs in the fcst field and obs field
            # dictionaries defined in the MET configuration file:
            # fcst = {
            #    field = [
            #       {
            #         name = "TMP";
            #         level = ["P500"];
            #         cat_thresh = [ > 80.0];
            #         GRIB_lvl_typ = 202;
            #       },
            #       {
            #         name = "HGT";
            #         level = ["P500"];
            #         cat_thresh = [ > 0.0];
            #         GRIB_lvl_typ = 202;
            #       },
            #    ]
            # }
            # obs = fcst;
            #
            # The reformatting involves creating the field key-value pairs in
            # the fcst and obs dictionaries.
            # Determine if this is a fcst or obs field

            # Iterate for the field types fcst and obs
            for field in field_list:
                if field == 'fcst':
                    name = var.fcst_name
                    level = var.fcst_level.zfill(2)
                    extra = var.fcst_extra
                elif field == 'obs':
                    name = var.obs_name
                    level = var.obs_level
                    extra = var.obs_extra

                name_level_extra_list = ['{ name = "', name,
                                         '";  level = [ "', level, '"]; ']
                if extra:
                    extra_str = extra + '; }, '
                    name_level_extra_list.append(extra_str)
                else:
                    # End the text for this field.  If this is the last field,
                    # end the dictionary appropriately.
                    if var.fcst_name == all_vars_list[-1].fcst_name:
                        # This is the last field, terminate it appropriately.
                        name_level_extra_list.append(' }]; ')
                    else:
                        # More field(s) to go
                        name_level_extra_list.append(' }, ')
                # Create the long string that will comprise the dictionary in
                # the MET point_stat config file.
                if field == 'fcst':
                    fcst_field += ''.join(name_level_extra_list)
                elif field == 'obs':
                    obs_field += ''.join(name_level_extra_list)

        met_fields = MetFields(fcst_field, obs_field)

        return met_fields

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

        fcst_files_info = self.create_input_file_info("fcst")
        obs_files_info = self.create_input_file_info("obs")

        # Determine which files are within the valid time window.  Whenever
        # there is more than one fcst file with the same valid time,
        # keep it, because we want to perform verification for all fcst/model
        # forecast hours.
        valid_start = self.ps_dict['START_DATE']
        valid_end = self.ps_dict['END_DATE']
        unix_start = self.convert_date_strings_to_unix_times(str(valid_start))
        unix_end = self.convert_date_strings_to_unix_times(str(valid_end))

        # Use dictionary to store/organize obs and fcst files based on valid
        # times.  Key = valid time, Value = list of full_filepaths
        # associated with this valid time.
        obs_dict_by_valid = dict()
        fcst_dict_by_valid = dict()
        for fcst in fcst_files_info:
            if unix_start <= fcst.valid_time <= unix_end:
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
            if unix_start <= obs.valid_time <= unix_end:
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

        # Get a list of all the model/fcst files
        dir_to_search = self.ps_dict['FCST_INPUT_DIR']
        fcst_file_regex = self.ps_dict['FCST_INPUT_FILE_REGEX']
        all_fcst_files = util.get_files(dir_to_search, fcst_file_regex,
                                        self.logger)

        # Get a list of all the obs files
        dir_to_search = self.ps_dict['OBS_INPUT_DIR']
        obs_file_regex = self.ps_dict['OBS_INPUT_FILE_REGEX']
        all_obs_files = util.get_files(dir_to_search, obs_file_regex,
                                       self.logger)

        # Initialize the output list
        consolidated_file_info = []

        # Valid time tuple
        InputFileInfo = namedtuple('InputFileInfo',
                                   'full_filepath, date, '
                                   'valid_time')
        if file_type == "fcst":
            # Get the information for the fcst/model file
            if all_fcst_files:
                fcst_input_regex = self.ps_dict['FCST_INPUT_FILE_REGEX']
                regex_match = re.compile(fcst_input_regex)
                for fcst_file in all_fcst_files:
                    match = re.match(regex_match, fcst_file)
                    time_info_tuple = \
                        self.get_time_info_from_file(match)

                    # Incorporate the time information into the
                    # InputFileInfo tuple
                    input_file_info = InputFileInfo(fcst_file,
                                                    time_info_tuple.date,
                                                    time_info_tuple.valid)
                    consolidated_file_info.append(input_file_info)
            else:
                self.logger.error('ERROR:|' + cur_function + '|' +
                                  cur_filename + 'No fcst files found in '
                                                 'specified input directory. '
                                                 ' Please verify that data '
                                                 'files are present and the '
                                                 'input directory path in '
                                                 'the config file is correct.')
        else:
            # Get the relevant information for the obs file
            if all_obs_files:
                obs_input_regex = self.ps_dict['OBS_INPUT_FILE_REGEX']
                regex_match = re.compile(obs_input_regex)
                for obs_file in all_obs_files:
                    match = re.match(regex_match, obs_file)
                    time_info_tuple = self.get_time_info_from_file(match)
                    # Incorporate the time information into the
                    # InputFileInfo tuple
                    input_file_info = InputFileInfo(obs_file,
                                                    time_info_tuple.date,
                                                    time_info_tuple.valid)
                    consolidated_file_info.append(input_file_info)

            else:
                self.logger.error('ERROR:|' + cur_function + '|' +
                                  cur_filename + '| No obs files found in '
                                                 'specified input directory. '
                                                 ' Please verify that data '
                                                 'files are present and the '
                                                 'input directory path in '
                                                 'the config file is correct.')
        return consolidated_file_info

    def get_time_info_from_file(self, match_from_regex):
        """! Determine the date and the valid time.

             Args:
                match_from_regex - the match object returned from the
                                   regex match
             Returns:
                   file_time_info - a named tuple containing the date (ymd
                   or ymdh), and cycle and offset times for the file of
                   interest.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            "DEBUG|:" + cur_function + '|' + cur_filename + '| ' +
            "Retrieving time information for file")

        TimeInfo = namedtuple('TimeInfo', 'date, valid')

        if match_from_regex.lastindex == 3:
            # We have a date, cycle, and offset
            date_str = str(match_from_regex.group(1))
            cycle = match_from_regex.group(2)
            offset_str = match_from_regex.group(3)
            offset_secs = self.HOURS_TO_SECONDS * int(offset_str)
            unix_date = self.convert_date_strings_to_unix_times(
                date_str)
            cycle_secs = int(cycle) * self.HOURS_TO_SECONDS
            valid_time_unix = unix_date + (cycle_secs - offset_secs)
            file_time_info = TimeInfo(unix_date, valid_time_unix)
        elif match_from_regex.lastindex == 2:
            # We have a fhr cycle hour, and run date (CDATE -EMC terminology)
            date_str = str(match_from_regex.group(2))
            fhr_cycle_hr = int(match_from_regex.group(1))
            fhr_cycle = self.HOURS_TO_SECONDS * fhr_cycle_hr
            unix_date = self.convert_date_strings_to_unix_times(date_str)
            valid_time_unix = unix_date + fhr_cycle
            file_time_info = TimeInfo(unix_date, valid_time_unix)
        elif match_from_regex.lastindex == 1:
            # We only have date in ymdh, which we use as a valid
            # time.
            date_str = str(match_from_regex.group(1))
            unix_date = self.convert_date_strings_to_unix_times(date_str)
            valid_time_unix = unix_date
            file_time_info = TimeInfo(unix_date, valid_time_unix)
        else:
            # No match, filename format is unexpected.
            self.logger.error('ERROR|:' + cur_function + '|' + cur_filename +
                              ' filename does not match expected format, '
                              'please check your filename regex in the '
                              'configuration file. Exiting...')
            sys.exit(1)

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

    def reformat_grid_id(self, grid_id):
        """!Reformat the grid id (MASK_GRID value in the configuration
            file.)

            Args:
                grid_id      - the grid_id of the grid to use in regridding

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
                'ERROR |:' + cur_function + '|' + cur_filename
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
