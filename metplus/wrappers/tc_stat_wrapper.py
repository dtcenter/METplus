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

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_AMODEL',
        'METPLUS_BMODEL',
        'METPLUS_DESC',
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_INIT_INCLUDE',
        'METPLUS_INIT_EXCLUDE',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_VALID_INCLUDE',
        'METPLUS_VALID_EXCLUDE',
        'METPLUS_INIT_HOUR',
        'METPLUS_VALID_HOUR',
        'METPLUS_LEAD',
        'METPLUS_LEAD_REQ',
        'METPLUS_INIT_MASK',
        'METPLUS_VALID_MASK',
        'METPLUS_TRACK_WATCH_WARN',
        'METPLUS_COLUMN_THRESH_NAME',
        'METPLUS_COLUMN_THRESH_VAL',
        'METPLUS_COLUMN_STR_NAME',
        'METPLUS_COLUMN_STR_VAL',
        'METPLUS_INIT_THRESH_NAME',
        'METPLUS_INIT_THRESH_VAL',
        'METPLUS_INIT_STR_NAME',
        'METPLUS_INIT_STR_VAL',
        'METPLUS_WATER_ONLY',
        'METPLUS_LANDFALL',
        'METPLUS_LANDFALL_BEG',
        'METPLUS_LANDFALL_END',
        'METPLUS_MATCH_POINTS',
        'METPLUS_JOBS',
    ]

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

        # support LOOKIN_DIR and INPUT_DIR
        if not c_dict['LOOKIN_DIR']:
            c_dict['LOOKIN_DIR'] = self.config.getdir('TC_STAT_INPUT_DIR', '')

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

        self.handle_description()

        self.set_met_config_for_environment_variables()

        return c_dict

    def set_met_config_for_environment_variables(self):
        """! Set c_dict dictionary entries that will be set as environment
        variables to be read by the MET config file.
            @param c_dict dictionary to add key/value pairs
        """
        app_name_upper = self.app_name.upper()

        for config_list in ['AMODEL',
                            'BMODEL',
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
            self.set_met_config_list(self.env_var_dict,
                                     f'{app_name_upper}_{config_list}',
                                     config_list.lower(),
                                     f'METPLUS_{config_list}')

        for iv_list in ['INIT', 'VALID',]:
            self.set_met_config_list(self.env_var_dict,
                                     f'{app_name_upper}_{iv_list}_INCLUDE',
                                     f'{iv_list.lower()}_inc',
                                     f'METPLUS_{iv_list}_INC'
                                     )
            self.set_met_config_list(self.env_var_dict,
                                     f'{app_name_upper}_{iv_list}_EXCLUDE',
                                     f'{iv_list.lower()}_exc',
                                     f'METPLUS_{iv_list}_EXC'
                                     )

        for config_str in ['INIT_BEG',
                           'INIT_END',
                           'VALID_BEG',
                           'VALID_END',
                           'LANDFALL_BEG',
                           'LANDFALL_END',
                            ]:
            self.set_met_config_string(self.env_var_dict,
                                       [f'{app_name_upper}_{config_str}',
                                        f'{config_str}'],
                                       config_str.lower(),
                                       f'METPLUS_{config_str}')

        for config_bool in ['WATER_ONLY',
                            'LANDFALL',
                            'MATCH_POINTS',
                            ]:

            self.set_met_config_bool(self.env_var_dict,
                                     f'{app_name_upper}_{config_bool}',
                                     config_bool.lower(),
                                     f'METPLUS_{config_bool}')

    def run_at_time(self, input_dict=None):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from run_metplus
        """
        self.logger.info('Starting tc_stat_wrapper...')

        time_info = None
        if input_dict:
            time_info = ti_calculate(input_dict)

        job_args_str = self.handle_jobs(time_info)
        if job_args_str is None:
            return None

        self.env_var_dict['METPLUS_JOBS'] = job_args_str

        self.set_environment_variables(time_info)

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
        """
        # handle old method of setting env vars in MET config files

        # variables that are lists in the MET config
        # need to set them to an empty list if they are unset
        var_lists = ['AMODEL',
                     'BMODEL',
                     'DESC',
                     'STORM_ID',
                     'BASIN',
                     'CYCLONE',
                     'STORM_NAME',
                     'INIT_INCLUDE',
                     'INIT_EXCLUDE',
                     'VALID_INCLUDE',
                     'VALID_EXCLUDE',
                     'INIT_HOUR',
                     'VALID_HOUR',
                     'LEAD',
                     'LEAD_REQ',
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
                     'JOBS',
                     ]
        for name in var_lists:
            value = self.get_env_var_value(f'METPLUS_{name}')
            if not value:
                value = '[]'
            self.add_env_var(name, value)

        # variables that previously had quotes around them in the MET config
        # need to remove quotes before setting env var
        var_quotes = ['INIT_BEG',
                      'INIT_END',
                      'VALID_BEG',
                      'VALID_END',
                      'LANDFALL_BEG',
                      'LANDFALL_END']
        for name in var_quotes:
            value = self.get_env_var_value(f'METPLUS_{name}').strip('"')
            self.add_env_var(name, value)

        # variables that can be set directly once the value is extracted
        var_items = ['WATER_ONLY',
                     'LANDFALL',
                     'MATCH_POINTS']
        for name in var_items:
            value = self.get_env_var_value(f'METPLUS_{name}')
            self.add_env_var(name, value)

        super().set_environment_variables(time_info)

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
                self.c_dict['OUTPUT_TEMPLATE'] = filepath
                if time_info is None:
                    time_info = {}

                if not self.find_and_check_output_file(time_info):
                    return None

        job_list_string = '","'.join(formatted_jobs)
        return f'jobs = ["{job_list_string}"];'
