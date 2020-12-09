"""
Program Name: time_freq_wrapper.py
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

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace TimeFreqWrapper
@brief Wraps the SeriesAnalysis tool to compare a series of gridded files
@endcode
'''

class TimeFreqWrapper(CommandBuilder):

    # valid options for run frequency
    FREQ_OPTIONS = ['RUN_ONCE',
                    'RUN_ONCE_PER_INIT_OR_VALID',
                    'RUN_ONCE_PER_LEAD',
                    'RUN_ONCE_FOR_EACH'
                    ]

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "time_freq"
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

        c_dict['TIME_FREQ'] = (
            self.config.getstr('config',
                               f'{app_name_upper}_TIME_FREQ',
                               '').upper()
        )
        if c_dict['TIME_FREQ'] not in self.FREQ_OPTIONS:
            self.log_error(f'Invalid value for {app_name_upper}_TIME_FREQ: ('
                           f"{c_dict['TIME_FREQ']}) Valid options include: "
                           f"{', '.join(self.FREQ_OPTIONS)}")

        c_dict['ALL_FILES'] = self.get_all_files()

        return c_dict

    def run_all_times(self):
        """! Run the wrapper based on the time frequency specified

             @returns True on success, False on failure
        """
        time_freq = self.c_dict['TIME_FREQ']
        if time_freq == 'RUN_ONCE':
            return self.run_once()
        elif time_freq == 'RUN_ONCE_PER_INIT_OR_VALID':
            return self.run_once_per_init_or_valid()
        elif time_freq == 'RUN_ONCE_PER_LEAD':
            return self.run_once_per_lead()
        elif time_freq == 'RUN_ONCE_FOR_EACH':
            return super().run_all_times()

    def run_once(self):
        input_dict = {}
        use_init = is_loop_by_init(config)
        if use_init is not None:
            start, _, _ = get_start_end_interval_times(self.config)
            if start:
                input_dict = util.set_input_dict(start,
                                                 self.config,
                                                 use_init)
        return self.run_at_time(input_dict)

    def run_once_per_init_or_valid(self):
        use_init = is_loop_by_init(config)
        if use_init is None:
            return False

        start, end, interval = get_start_end_interval_times(self.config)
        if not start:
            self.log_error("Could not get [INIT/VALID] time information"
                           "from configuration file")
            return False

        success = True
        loop_time = start
        while loop_time <= end:
            util.log_runtime_banner(loop_time, self.config, use_init)
            input_dict = util.set_input_dict(loop_time, self.config, use_init)
            if not self.run_at_time(input_dict):
                success = False

            loop_time += interval

        return success

    def run_once_per_lead(self):
        lead_seq = util.get_lead_sequence(self.config, input_dict=None)
        success = True
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
