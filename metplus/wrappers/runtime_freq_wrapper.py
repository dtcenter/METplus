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

        # if looping over init/valid time,
        # check that the time config variables can be read correctly
        if c_dict['RUNTIME_FREQ'] == 'RUN_ONCE_PER_INIT_OR_VALID':
            start, end, interval = get_start_end_interval_times(self.config)
            c_dict['START_TIME'] = start
            c_dict['END_TIME'] = end
            c_dict['TIME_INTERVAL'] = interval

            if not c_dict['START_TIME']:
                self.log_error("Could not get [INIT/VALID] time information"
                               "from configuration file")

        c_dict['ALL_FILES'] = self.get_all_files()

        return c_dict

    def run_all_times(self):
        """! Run the wrapper based on the time frequency specified

             @returns True on success, False on failure
        """
        runtime_freq = self.c_dict['RUNTIME_FREQ']
        if runtime_freq == 'RUN_ONCE':
            self.run_once()
        elif runtime_freq == 'RUN_ONCE_PER_INIT_OR_VALID':
            self.run_once_per_init_or_valid()
        elif runtime_freq == 'RUN_ONCE_PER_LEAD':
            self.run_once_per_lead()
        elif runtime_freq == 'RUN_ONCE_FOR_EACH':
            return super().run_all_times()

        return self.all_commands

    def run_once(self):
        # create input dictionary and get 'now' item
        input_dict = set_input_dict(loop_time=None,
                                    config=self.config,
                                    use_init=None)

        # set other time items to wildcard to find all files
        input_dict['init'] = '*'
        input_dict['valid'] = '*'
        input_dict['lead'] = '*'

        return self.run_at_time_once(input_dict)

    def run_once_per_init_or_valid(self):
        use_init = is_loop_by_init(self.config)
        if use_init is None:
            return False

        success = True
        loop_time = self.c_dict['START_TIME']
        while loop_time <= self.c_dict['END_TIME']:
            log_runtime_banner(loop_time, self.config, use_init)
            input_dict = set_input_dict(loop_time, self.config, use_init)

            if 'init' in input_dict:
                input_dict['valid'] = '*'
            elif 'valid' in input_dict:
                input_dict['init'] = '*'

            input_dict['lead'] = '*'

            if not self.run_at_time_once(input_dict):
                success = False

            loop_time += self.c_dict['TIME_INTERVAL']

        return success

    def run_once_per_lead(self):
        success = True

        lead_seq = get_lead_sequence(self.config, input_dict=None)
        for lead in lead_seq:
            # create input dict and only set 'now' item
            # create a new dictionary each iteration in case the function
            # that it is passed into modifies it
            input_dict = set_input_dict(loop_time=None,
                                        config=self.config,
                                        use_init=None)
            # add forecast lead
            input_dict['lead'] = lead
            input_dict['init'] = '*'
            input_dict['valid'] = '*'

            if not self.run_at_time_once(input_dict):
                success = False

        return success

    def get_all_files(self):
        """! Get all files that can be processed with the app. Some wrappers
        like UserScript do not need to obtain a list of possible files. In this
        case, the function returns an empty dictionary.
        @returns A dictionary where the key is the type of data that was found,
        i.e. fcst or anly, and the value is a list of files that fit in that
        category
        """
        return {}
