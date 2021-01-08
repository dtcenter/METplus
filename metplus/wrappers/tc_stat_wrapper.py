"""!
Program Name: TCStatWrapper.py
Contact(s):  Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Stratify tropical cyclone data by any combination of time, column,
          statistics
History log: Initial version
Usage: TCStatWrapper.py
Parameters: None
Input Files: tc_pairs data
Output Files: subset of tc_pairs data
Condition codes: 0 for success, 1 for failure

"""

import os
import sys
from datetime import datetime

from produtil.run import ExitStatusException

from ..util import getlist, mkdir_p, do_string_sub, ti_calculate
from . import CommandBuilder

## @namespace TCStatWrapper
#  @brief Wrapper to the MET tool tc_stat, which is used for filtering tropical
#  cyclone pair data.

# pylint:disable=too-few-public-methods
# This class is just a wrapper to the MET tool tc_stat.  The attribute data
# is used to create the tc_stat commands and not necessarily operate on that
# attribute data.


class TCStatWrapper(CommandBuilder):
    """! Wrapper for the MET tool, tc_stat, which is used to filter tropical
         cyclone pair data.
    """

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'tc_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)

        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)
        self.logger.debug("Initialized TCStatWrapper")

    def create_c_dict(self):
        """!  Read in and store all the values from the config file.  This
              will make it easier to reassign values while unit testing and
              make it easier when retrieving these values, especially when
              they are needed multiple times by different methods.

              @returns a dictionary of the key-value representation of options
               set in the config file.
        """
        self.logger.debug('Creating tc-stat dictionary...')

        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['LOOKIN_DIR'] = self.config.getdir('TC_STAT_LOOKIN_DIR', '')
        if not c_dict['LOOKIN_DIR']:
            self.log_error("TC_STAT_LOOKIN_DIR must be set")

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_STAT_OUTPUT_DIR')

        c_dict['JOBS'] = getlist(self.config.getraw('config',
                                                    'TC_STAT_JOB_ARGS',
                                                    ''))
        if not c_dict.get('JOBS'):
            self.log_error('No job arguments defined. '
                           'Please set TC_STAT_JOB_ARGS')

        c_dict['CONFIG_FILE'] = self.config.getstr('config',
                                                   'TC_STAT_CONFIG_FILE',
                                                   '')
        if not c_dict['CONFIG_FILE']:
            default_config = os.path.join(self.config.getdir('PARM_BASE'),
                                          'met_config',
                                          'TCStatConfig_wrapped')
            self.logger.debug("TC_STAT_CONFIG_FILE not set. Using "
                              f"{default_config}")
            c_dict['CONFIG_FILE'] = default_config

        self.set_c_dict_for_environment_variables(c_dict)

        return c_dict

    def set_c_dict_for_environment_variables(self, c_dict):
        """! Set c_dict dictionary entries that will be set as environment
        variables to be read by the MET config file.
            @param c_dict dictionary to add key/value pairs
        """
        app_name_upper = self.app_name.upper()

        for config_list in ['AMODEL',
                            'BMODEL',
                            'DESC',
                            'STORM_ID',
                            'BASIN',
                            'CYCLONE',
                            'STORM_NAME',
                            'INIT_HOUR',
                            'LEAD_REQ',
                            'INIT_MASK',
                            'VALID_MASK',
                            'VALID_HOUR',
                            'LEAD',
                            'TRACK_WATCH_WARN',
                            'COLUMN_THRESH_NAME',
                            'COLUMN_THRESH_VAL',
                            'COLUMN_STR_NAME',
                            'COLUMN_STR_VAL',
                            'INIT_THRESH_NAME',
                            'INIT_THRESH_VAL',
                            'INIT_STR_NAME',
                            'INIT_STR_VAL',
                             ]:
            self.set_c_dict_list(c_dict,
                                 f'{app_name_upper}_{config_list}',
                                 config_list.lower())

            for iv_list in ['INIT', 'VALID',]:
                self.set_c_dict_list(c_dict,
                                     f'{app_name_upper}_{iv_list}_INCLUDE',
                                     f'{iv_list.lower()}_inc',
                                     )
                self.set_c_dict_list(c_dict,
                                     f'{app_name_upper}_{iv_list}_EXCLUDE',
                                     f'{iv_list.lower()}_exc',
                                     )

        for config_str in ['INIT_BEG',
                           'INIT_END',
                           'VALID_BEG',
                           'VALID_END',
                           'LANDFALL_BEG',
                           'LANDFALL_END',
                            ]:
            self.set_c_dict_string(c_dict,
                                   f'{app_name_upper}_{config_str}',
                                   config_str.lower())

        for config_bool in ['WATER_ONLY',
                            'LANDFALL',
                            'MATCH_POINTS',
                            ]:

            self.set_c_dict_bool(c_dict,
                                 f'{app_name_upper}_{config_bool}',
                                 config_bool.lower())

        # error check config values
        self.validate_config_values(c_dict)

    def run_at_time(self, input_dict=None):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from master_metplus
        """
        self.logger.info('Starting tc_stat_wrapper...')

        time_info = None
        if input_dict:
            time_info = ti_calculate(input_dict)

        if not self.set_environment_variables(time_info):
            return None

        return self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """

        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        cmd += f" -lookin {self.c_dict['LOOKIN_DIR']}"

        cmd += f" -config {self.c_dict.get('CONFIG_FILE')}"

        return cmd

    def set_environment_variables(self, time_info):
        """! Set the env variables based on settings in the METplus config
             files.

             @param time_info dictionary containing time information
             @returns True if command should be run, False if skipping
        """

        self.logger.info('Setting env variables from config file...')
        # Set all the environment variables that are needed by the
        # MET config file.

        for env_var in ['AMODEL',
                        'BMODEL',
                        'DESC',
                        'STORM_ID',
                        'BASIN',
                        'CYCLONE',
                        'STORM_NAME',
                        'INIT_BEG',
                        'INIT_END',
                        'INIT_INC',
                        'INIT_EXC',
                        'INIT_HOUR',
                        'VALID_BEG',
                        'VALID_END',
                        'VALID_INC',
                        'VALID_EXC',
                        'VALID_HOUR',
                        'LEAD_REQ',
                        'LEAD',
                        'INIT_MASK',
                        'VALID_MASK',
                        'TRACK_WATCH_WARN',
                        'COLUMN_THRESH_NAME',
                        'COLUMN_THRESH_VAL',
                        'COLUMN_STR_NAME',
                        'COLUMN_STR_VAL',
                        'INIT_THRESH_NAME',
                        'INIT_THRESH_VAL',
                        'INIT_STR_NAME',
                        'INIT_STR_VAL',
                        'LANDFALL_BEG',
                        'LANDFALL_END',
                        'WATER_ONLY',
                        'LANDFALL',
                        'MATCH_POINTS',
                        ]:
            # if time info is available, run value through string substitution
            value = self.c_dict.get(env_var, '')
            if time_info:
                value = do_string_sub(value, **time_info)

            self.add_env_var(env_var,
                             value)

        job_args_str = self.handle_jobs(time_info)
        if job_args_str is None:
            return False

        self.add_env_var('JOBS', job_args_str)

        super().set_environment_variables(time_info)
        return True

    def handle_jobs(self, time_info):
        """! Loop through job list found in c_dict key JOBS,
         create parent directory for -dump_row path if it is set,
         and format jobs string to pass to MET config file
         @param time_info time dictionary used to fill in filename
          template tags if used
         @returns formatted jobs string as jobs = ["job1", "job2"]; or None if
          command should be skipped
        """
        formatted_jobs = []
        for job in self.c_dict.get('JOBS'):
            # if time info is available, fill in filename template tags
            subbed_job = do_string_sub(job, **time_info) if time_info else job
            formatted_jobs.append(subbed_job.strip())

            # check if -dump_row is used
            # if it is, create parent directory of output file
            split_job = subbed_job.split(' ')
            if '-dump_row' in split_job:
                index = split_job.index('-dump_row') + 1
                filepath = split_job[index]
                self.c_dict['OUTPUT_TEMPLATE'] = split_job[index]
                if time_info is None:
                    time_info = {}

                if not self.find_and_check_output_file(time_info):
                    return None

        job_list_string = '","'.join(formatted_jobs)
        return f'jobs = ["{job_list_string}"];'

    def validate_config_values(self, c_dict):
        """! Verify that the length of the name and val lists
             in the MET tc-stat config file are of equal length, if
             not, log an error message and exit.  As soon as a length mismatch
             is encountered, return False.

             Args:

             Returns:
                 True: if all corresponding <>_NAME and <>_VAL lists
                       have the same length
                 False: if any name/val list length mismatch is encountered
        """

        self.logger.debug('Checking if name-val lists in config file have'
                          'the same length...')

        # Check COLUMN_THRESH_NAME and COLUMN_THRESH_VAL
        if len(c_dict.get('COLUMN_THRESH_NAME', '')) != \
                len(c_dict.get('COLUMN_THRESH_VAL', '')):
            self.log_error(
                'COLUMN_THRESH_NAME does not have the same ' +
                'number of items as COLUMN_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')

        # Check COLUMN_STR_NAME and COLUMN_STR_VAL
        if len(c_dict.get('COLUMN_STR_NAME', '')) != \
                len(c_dict.get('COLUMN_STR_VAL', '')):
            self.log_error(
                'COLUMN_STR_NAME does not have the same ' +
                'number of items as COLUMN_STR_VAL. Please' +
                ' check your MET tc_stat config file')

        # Check INIT_THRESH_NAME and INIT_THRESH_VAL
        if len(c_dict.get('INIT_THRESH_NAME', '')) != \
                len(c_dict.get('INIT_THRESH_VAL', '')):
            self.log_error(
                'INIT_THRESH_NAME does not have the same ' +
                'number of items as INIT_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')

        # Check INIT_STR_NAME and INIT_STR_VAL
        if len(c_dict.get('INIT_STR_NAME', '')) != \
                len(c_dict.get('INIT_STR_VAL', '')):
            self.log_error(
                'INIT_STR_NAME does not have the same ' +
                'number of items as INIT_STR_VAL. Please' +
                ' check your MET tc_stat config file')
