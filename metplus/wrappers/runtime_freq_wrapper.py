"""
Program Name: runtime_freq_wrapper.py
Contact(s): George McCabe
Abstract: Parent class for wrappers that process groups of times
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
from datetime import datetime

from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub, get_start_end_interval_times, set_input_dict
from ..util import log_runtime_banner, get_lead_sequence, is_loop_by_init
from ..util import skip_time

'''!@namespace RuntimeFreqWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''

class RuntimeFreqWrapper(CommandBuilder):

    # valid options for run frequency
    FREQ_OPTIONS = ['RUN_ONCE',
                    'RUN_ONCE_PER_INIT_OR_VALID',
                    'RUN_ONCE_PER_LEAD',
                    'RUN_ONCE_FOR_EACH'
                    ]

    def __init__(self, config, instance=None, config_overrides={}):
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app_name_upper = ''
        if hasattr(self, 'app_name'):
            app_name_upper = self.app_name.upper()

        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               f'LOG_{app_name_upper}_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        c_dict['RUNTIME_FREQ'] = (
            self.config.getstr('config',
                               f'{app_name_upper}_RUNTIME_FREQ',
                               '').upper()
        )
        if c_dict['RUNTIME_FREQ'] not in self.FREQ_OPTIONS:
            self.log_error(f'Invalid value for {app_name_upper}_RUNTIME_FREQ: '
                           f"({c_dict['RUNTIME_FREQ']}) Valid options include:"
                           f" {', '.join(self.FREQ_OPTIONS)}")

        # get runtime information to obtain all input files
        start, end, interval = get_start_end_interval_times(self.config,
                                                            warn=True)
        c_dict['START_TIME'] = start
        c_dict['END_TIME'] = end
        c_dict['TIME_INTERVAL'] = interval

        # if looping over init/valid time,
        # check that the time config variables can be read correctly
        if c_dict['RUNTIME_FREQ'] == 'RUN_ONCE_PER_INIT_OR_VALID':

            if not c_dict['START_TIME']:
                self.log_error("Could not get [INIT/VALID] time information"
                               "from configuration file")

        # if not running once for each runtime and loop order is not set to
        # 'processes' report an error
        if c_dict['RUNTIME_FREQ'] != 'RUN_ONCE_FOR_EACH':
            loop_order = self.config.getstr('config', 'LOOP_ORDER', '').lower()
            if loop_order != 'processes':
                self.log_error(f"Cannot run using {c_dict['RUNTIME_FREQ']} "
                               "mode unless LOOP_ORDER = processes")

        return c_dict

    def run_all_times(self):
        # loop over all custom strings
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(
                    f"Processing custom string: {custom_string}"
                )

            self.run_all_times_custom(custom_string)

        return self.all_commands

    def run_all_times_custom(self, custom):
        """! Run the wrapper based on the time frequency specified

             @returns True on success, False on failure
        """
        # get a list of all input files that are available
        if not self.get_all_files(custom):
            self.log_error("A problem occurred trying to obtain input files")
            return None

        runtime_freq = self.c_dict['RUNTIME_FREQ']
        if runtime_freq == 'RUN_ONCE':
            self.run_once(custom)
        elif runtime_freq == 'RUN_ONCE_PER_INIT_OR_VALID':
            self.run_once_per_init_or_valid(custom)
        elif runtime_freq == 'RUN_ONCE_PER_LEAD':
            self.run_once_per_lead(custom)
        elif runtime_freq == 'RUN_ONCE_FOR_EACH':
            self.all_commands = super().run_all_times()

    def run_once(self, custom):
        self.logger.debug("Running once for all files")
        # create input dictionary and get 'now' item
        input_dict = set_input_dict(loop_time=None,
                                    config=self.config,
                                    use_init=None,
                                    instance=self.instance,
                                    custom=custom)

        # set other time items to wildcard to find all files
        input_dict['init'] = '*'
        input_dict['valid'] = '*'
        input_dict['lead'] = '*'

        return self.run_at_time_once(input_dict)

    def run_once_per_init_or_valid(self, custom):
        use_init = is_loop_by_init(self.config)
        if use_init is None:
            return False

        # log which time type to loop over
        if use_init:
            init_or_valid = 'init'
        else:
            init_or_valid = 'valid'
        self.logger.debug(f"Running once for each {init_or_valid} time")

        success = True
        loop_time = self.c_dict['START_TIME']
        while loop_time <= self.c_dict['END_TIME']:
            log_runtime_banner(loop_time, self.config, use_init)
            input_dict = set_input_dict(loop_time,
                                        self.config,
                                        use_init,
                                        instance=self.instance,
                                        custom=custom)

            if 'init' in input_dict:
                input_dict['valid'] = '*'
            elif 'valid' in input_dict:
                input_dict['init'] = '*'

            input_dict['lead'] = '*'

            if not self.run_at_time_once(input_dict):
                success = False

            loop_time += self.c_dict['TIME_INTERVAL']

        return success

    def run_once_per_lead(self, custom):
        self.logger.debug("Running once for forecast lead time")
        success = True

        lead_seq = get_lead_sequence(self.config, input_dict=None)
        for lead in lead_seq:
            # create input dict and only set 'now' item
            # create a new dictionary each iteration in case the function
            # that it is passed into modifies it
            input_dict = set_input_dict(loop_time=None,
                                        config=self.config,
                                        use_init=None,
                                        instance=self.instance,
                                        custom=custom)
            # add forecast lead
            input_dict['lead'] = lead
            input_dict['init'] = '*'
            input_dict['valid'] = '*'

            if not self.run_at_time_once(input_dict):
                success = False

        return success

    def run_at_time(self, input_dict):
        """! Runs the command for a given run time. This function loops
              over the list of forecast leads and list of custom loops
              and runs once for each combination
              Args:
                @param input_dict dictionary containing time information
        """

        # loop of forecast leads and process each
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            # set current lead time config and environment variables
            time_info = time_util.ti_calculate(input_dict)

            self.logger.info(
                f"Processing forecast lead {time_info['lead_string']}"
            )

            if skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(time_info)

    def get_all_files(self, custom=None):
        """! Get all files that can be processed with the app. Some wrappers
        like UserScript do not need to obtain a list of possible files. In this
        case, the function returns an empty dictionary.
        @returns A dictionary where the key is the type of data that was found,
        i.e. fcst or obs, and the value is a list of files that fit in that
        category
        """
        use_init = is_loop_by_init(self.config)
        if use_init is None:
            return False

        self.logger.debug("Finding all input files")
        all_files = []

        # loop over all init/valid times
        loop_time = self.c_dict['START_TIME']
        while loop_time <= self.c_dict['END_TIME']:
            input_dict = set_input_dict(loop_time,
                                        self.config,
                                        use_init,
                                        instance=self.instance,
                                        custom=custom)

            # loop over all forecast leads
            wildcard_if_empty = self.c_dict.get('WILDCARD_LEAD_IF_EMPTY',
                                                False)
            lead_seq = get_lead_sequence(self.config,
                                         input_dict,
                                         wildcard_if_empty=wildcard_if_empty)
            for lead in lead_seq:
                input_dict['lead'] = lead

                # set current lead time config and environment variables
                time_info = time_util.ti_calculate(input_dict)

                file_dict = self.get_files_from_time(time_info)
                if file_dict:
                    if isinstance(file_dict, list):
                        all_files.extend(file_dict)
                    else:
                        all_files.append(file_dict)

            loop_time += self.c_dict['TIME_INTERVAL']

        if not all_files:
            return False

        self.c_dict['ALL_FILES'] = all_files
        return True

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime.
             @param time_info dictionary containing time information
             @returns dictionary containing time_info dict and any relevant
             files with a key representing a description of that file
        """
        file_dict = {}
        file_dict['time_info'] = time_info.copy()
        return file_dict

    def compare_time_info(self, runtime, filetime):
        """! Compare current runtime dictionary to current file time dictionary
             If runtime value for init, valid, or lead is not a wildcard and
             it doesn't match the file's time value, return False. Otherwise
             return True.

             @param runtime dictionary containing time info for current runtime
             @param filetime dictionary containing time info for current file
             @returns True if file's info matches the requirements for current
             runtime or False if not.
        """
        for time_val in ['init', 'valid']:
            if (runtime[time_val] != '*' and
                    filetime[time_val] != runtime[time_val]):
                return False

        if runtime['lead'] == '*':
            return True

        # convert each value to seconds to compare
        runtime_lead = time_util.ti_get_seconds_from_lead(runtime['lead'],
                                                          runtime['valid'])
        filetime_lead = time_util.ti_get_seconds_from_lead(filetime['lead'],
                                                           filetime['valid'])
        # if cannot compute seconds, possibly using months or years, so compare
        # forecast leads directly
        if runtime_lead is None or filetime_lead is None:
            return runtime['lead'] == filetime['lead']

        return runtime_lead == filetime_lead
