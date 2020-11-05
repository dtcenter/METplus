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

from produtil.run import ExitStatusException

from ..util import getlist, mkdir_p
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

    def __init__(self, config, config_overrides={}):
        self.app_name = 'tc_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)

        super().__init__(config, config_overrides)
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

        c_dict['INPUT_DIR'] = self.config.getdir('TC_STAT_INPUT_DIR', '')
        if not c_dict['INPUT_DIR']:
            self.log_error("TC_STAT_INPUT_DIR must be set")

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_STAT_OUTPUT_DIR')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("TC_STAT_OUTPUT_DIR must be set")

        c_dict['JOBS'] = self.config.getstr('config',
                                            'TC_STAT_JOB_ARGS',
                                            '')
        if not c_dict.get('JOBS'):
            self.log_error('No job arguments defined. '
                           'Please set TC_STAT_JOB_ARGS')

        c_dict['MATCH_POINTS'] = (
            self.config.getbool('config', 'TC_STAT_MATCH_POINTS')
        )
        if c_dict['MATCH_POINTS'] is None:
            self.log_error('Invalid boolean value set for '
                           'TC_STAT_MATCH_POINTS')

        c_dict['CONFIG_FILE'] = self.config.getstr('config',
                                                   'TC_STAT_CONFIG_FILE',
                                                   '')
        if not c_dict['CONFIG_FILE']:
            self.log_error("TC_STAT_CONFIG_FILE must be set to run "
                           "TCStat wrapper")

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
                            'INIT_INCLUDE',
                            'INIT_EXCLUDE',
                            'INIT_HOUR',
                            'VALID_INCLUDE',
                            'VALID_EXCLUDE',
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
                            ]:

            self.set_c_dict_bool(c_dict,
                                 f'{app_name_upper}_{config_bool}',
                                 config_bool.lower())

        # error check config values
        self.validate_config_values(c_dict)

    def run_all_times(self):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from master_metplus
        """
        self.logger.info('Starting tc_stat_wrapper...')

        self.set_environment_variables()

        # Don't forget to create the output directory, as MET tc_stat will
        # not do this.
        mkdir_p(self.c_dict['OUTPUT_DIR'])

        self.build_and_run_command()
        return

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """

        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        cmd += f" -lookin {self.c_dict['INPUT_DIR']}"

        cmd += f" -config {self.c_dict.get('CONFIG_FILE')}"

        match_points = str(self.c_dict['MATCH_POINTS']).lower()
        cmd += f" -match_points {match_points}"

        return cmd

    def set_environment_variables(self, time_info=None):
        """! Set the env variables based on settings in the METplus config
             files.
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
                        'INIT_INCLUDE',
                        'INIT_EXCLUDE',
                        'INIT_HOUR',
                        'VALID_BEG',
                        'VALID_END',
                        'VALID_INCLUDE',
                        'VALID_EXCLUDE',
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
                        ]:
            self.add_env_var(env_var,
                             self.c_dict.get(env_var, ''))

        job_args_str = f"jobs = [\"{self.c_dict.get('JOBS')}\"];"
        self.add_env_var('JOBS', job_args_str)

        super().set_environment_variables(time_info)

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
        self.logger.debug(c_dict.keys())
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

    def build_tc_stat(self, tc_stat_output_dir, cur_init, tc_input_list,
                      filter_opts):
        """!This is called from extract_tiles_wrapper and from any other
            wrapper to provide additional filtering WITHOUT the need for
            a tc_stat MET config file.

            Creates the call to MET tool TC-STAT to subset tc-pairs output
            based on the criteria specified in the feature relative
            use case parameter/config file.

            Args:
            @param tc_stat_output_dir:  The output directory where filtered
                                       results are saved.
            @param cur_init:  The initialization time
            @param tc_input_list:  The "list" of input data (the files containing
                                   the tc pair data to be filtered) in a
                                   string
            @param filter_opts:  The list of filter options to apply

            Returns:
                None: if no error, then invoke MET tool TC-STAT and
                    subsets tc-pairs data, creating a filter.tcst file.

                Raises CalledProcessError
        """

        mkdir_p(tc_stat_output_dir)

        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(tc_stat_output_dir, cur_init,
                                   filter_filename)
        filter_path = os.path.join(tc_stat_output_dir, cur_init)
        mkdir_p(filter_path)

        # This is for extract_tiles to call without a config file
        tc_cmd_list = [self.app_path, " -job filter ",
                       " -lookin ", tc_input_list,
                       " -match_points true ",
                       " -init_inc ", cur_init,
                       " -dump_row ", filter_name,
                       " ", filter_opts]

        tc_cmd_str = ''.join(tc_cmd_list)

        # Since this wrapper is not using the CommandBuilder to build the cmd,
        # we need to add the met verbosity level to the MET cmd created before
        # we run the command.
        tc_cmd_str = self.cmdrunner.insert_metverbosity_opt(tc_cmd_str)

        # Run tc_stat
        try:
            # tc_cmd = batchexe('sh')['-c', tc_cmd_str].err2out()
            # checkrun(tc_cmd)
            (ret, cmd) = \
                self.cmdrunner.run_cmd(tc_cmd_str, self.env, app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(cmd),), ret)
        except ExitStatusException as ese:
            self.log_error(ese)
