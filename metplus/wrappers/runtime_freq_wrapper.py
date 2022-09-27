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
from ..util import do_string_sub
from ..util import log_runtime_banner, get_lead_sequence, is_loop_by_init
from ..util import skip_time, getlist
from ..util import time_generator, add_to_time_input

'''!@namespace RuntimeFreqWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''

class RuntimeFreqWrapper(CommandBuilder):

    # valid options for run frequency
    FREQ_OPTIONS = [
        'RUN_ONCE',
        'RUN_ONCE_PER_INIT_OR_VALID',
        'RUN_ONCE_PER_LEAD',
        'RUN_ONCE_FOR_EACH'
    ]

    def __init__(self, config, instance=None):
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app_name_upper = ''
        if hasattr(self, 'app_name'):
            app_name_upper = self.app_name.upper()

        c_dict['VERBOSITY'] = (
            self.config.getint('config',
                               f'LOG_{app_name_upper}_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        c_dict['RUNTIME_FREQ'] = (
            self.config.getstr_nocheck('config',
                                       f'{app_name_upper}_RUNTIME_FREQ',
                                       '').upper()
        )

        return c_dict

    def get_input_templates(self, c_dict):
        app_upper = self.app_name.upper()
        template_dict = {}

        input_templates = getlist(
            self.config.getraw('config',
                               f'{app_upper}_INPUT_TEMPLATE',
                               '')
        )
        input_template_labels = getlist(
            self.config.getraw('config',
                               f'{app_upper}_INPUT_TEMPLATE_LABELS',
                               '')
        )

        # cannot have more labels than templates specified
        if len(input_template_labels) > len(input_templates):
            self.log_error('Cannot supply more labels than templates. '
                           f'{app_upper}_INPUT_TEMPLATE_LABELS length must be '
                           f'less than {app_upper}_INPUT_TEMPLATES length.')
            return

        for idx, template in enumerate(input_templates):
            # if fewer labels than templates, fill in labels with input{idx}
            if len(input_template_labels) <= idx:
                label = f'input{idx}'
            else:
                label = input_template_labels[idx]

            template_dict[label] = template

        c_dict['TEMPLATE_DICT'] = template_dict

    def run_all_times(self):
        if self.c_dict['RUNTIME_FREQ'] not in self.FREQ_OPTIONS:
            self.log_error(f"Invalid value for "
                           f"{self.app_name.upper()}_RUNTIME_FREQ: "
                           f"({self.c_dict['RUNTIME_FREQ']}) "
                           f"Valid options include:"
                           f" {', '.join(self.FREQ_OPTIONS)}")
            return None

        # if not running once for each runtime and loop order is not set to
        # 'processes' report an error
        if self.c_dict['RUNTIME_FREQ'] != 'RUN_ONCE_FOR_EACH':
            loop_order = self.config.getstr('config', 'LOOP_ORDER', '').lower()
            if loop_order != 'processes':
                self.log_error(f"Cannot run using {self.c_dict['RUNTIME_FREQ']} "
                               "mode unless LOOP_ORDER = processes")
                return None

        wrapper_instance_name = self.get_wrapper_instance_name()
        self.logger.info(f'Running wrapper: {wrapper_instance_name}')

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
        runtime_freq = self.c_dict['RUNTIME_FREQ']
        if runtime_freq == 'RUN_ONCE':
            self.run_once(custom)
        elif runtime_freq == 'RUN_ONCE_PER_INIT_OR_VALID':
            self.run_once_per_init_or_valid(custom)
        elif runtime_freq == 'RUN_ONCE_PER_LEAD':
            self.run_once_per_lead(custom)
        elif runtime_freq == 'RUN_ONCE_FOR_EACH':
            self.all_commands = super().run_all_times(custom)

    def run_once(self, custom):
        self.logger.debug("Running once for all files")
        # create input dictionary and set clock time, instance, and custom
        time_input = {}
        add_to_time_input(time_input,
                          clock_time=self.config.getstr('config',
                                                        'CLOCK_TIME'),
                          instance=self.instance,
                          custom=custom)

        # set other time items to wildcard to find all files
        time_input['init'] = '*'
        time_input['valid'] = '*'
        time_input['lead'] = '*'

        if not self.get_all_files(custom):
            self.log_error("A problem occurred trying to obtain input files")
            return None

        return self.run_at_time_once(time_input)

    def run_once_per_init_or_valid(self, custom):
        self.logger.debug(f"Running once for each init/valid time")

        success = True
        for time_input in time_generator(self.config):
            if time_input is None:
                success = False
                continue

            log_runtime_banner(self.config, time_input, self)
            add_to_time_input(time_input,
                              instance=self.instance,
                              custom=custom)

            if 'init' in time_input:
                time_input['valid'] = '*'
            elif 'valid' in time_input:
                time_input['init'] = '*'

            time_input['lead'] = '*'

            self.c_dict['ALL_FILES'] = self.get_all_files_from_leads(time_input)

            self.clear()
            if not self.run_at_time_once(time_input):
                success = False

        return success

    def run_once_per_lead(self, custom):
        self.logger.debug("Running once for forecast lead time")
        success = True

        lead_seq = get_lead_sequence(self.config, input_dict=None)
        for lead in lead_seq:
            # create input dict and only set 'now' item
            # create a new dictionary each iteration in case the function
            # that it is passed into modifies it
            time_input = {}
            add_to_time_input(time_input,
                              clock_time=self.config.getstr('config',
                                                            'CLOCK_TIME'),
                              instance=self.instance,
                              custom=custom)

            # add forecast lead
            time_input['lead'] = lead
            time_input['init'] = '*'
            time_input['valid'] = '*'

            self.c_dict['ALL_FILES'] = self.get_all_files_for_lead(time_input)

            self.clear()
            if not self.run_at_time_once(time_input):
                success = False

        return success

    def run_at_time(self, input_dict):
        """! Runs the command for a given run time. This function loops
              over the list of forecast leads and list of custom loops
              and runs once for each combination

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

            # since run_all_times was not called (LOOP_BY=times) then
            # get files for current run time
            file_dict = self.get_files_from_time(time_info)
            all_files = []
            if file_dict:
                if isinstance(file_dict, list):
                    all_files = file_dict
                else:
                    all_files = [file_dict]

            self.c_dict['ALL_FILES'] = all_files

            # Run for given init/valid time and forecast lead combination
            self.clear()
            self.run_at_time_once(time_info)

    def get_all_files(self, custom=None):
        """! Get all files that can be processed with the app.
        @returns A dictionary where the key is the type of data that was found,
        i.e. fcst or obs, and the value is a list of files that fit in that
        category
        """
        self.logger.debug("Finding all input files")
        all_files = []

        # loop over all init/valid times
        for time_input in time_generator(self.config):
            if time_input is None:
                return False

            add_to_time_input(time_input,
                              instance=self.instance,
                              custom=custom)

            lead_files = self.get_all_files_from_leads(time_input)
            all_files.extend(lead_files)

        if not all_files:
            return False

        self.c_dict['ALL_FILES'] = all_files
        return True

    def get_all_files_from_leads(self, time_input):
        lead_files = []
        # loop over all forecast leads
        wildcard_if_empty = self.c_dict.get('WILDCARD_LEAD_IF_EMPTY',
                                            False)
        lead_seq = get_lead_sequence(self.config,
                                     time_input,
                                     wildcard_if_empty=wildcard_if_empty)
        for lead in lead_seq:
            current_time_input = time_input.copy()
            current_time_input['lead'] = lead

            # set current lead time config and environment variables
            time_info = time_util.ti_calculate(current_time_input)

            if skip_time(time_info, self.c_dict.get('SKIP_TIMES')):
                continue

            file_dict = self.get_files_from_time(time_info)
            if file_dict:
                if isinstance(file_dict, list):
                    lead_files.extend(file_dict)
                else:
                    lead_files.append(file_dict)

        return lead_files

    def get_all_files_for_lead(self, time_input):
        new_files = []
        for run_time in time_generator(self.config):
            if run_time is None:
                continue

            current_time_input = time_input.copy()
            if 'valid' in run_time:
                current_time_input['valid'] = run_time['valid']
                del current_time_input['init']
            elif 'init' in run_time:
                current_time_input['init'] = run_time['init']
                del current_time_input['valid']
            time_info = time_util.ti_calculate(current_time_input)
            if skip_time(time_info, self.c_dict.get('SKIP_TIMES')):
                continue
            file_dict = self.get_files_from_time(time_info)
            if file_dict:
                if isinstance(file_dict, list):
                    new_files.extend(file_dict)
                else:
                    new_files.append(file_dict)

        return new_files

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
        # False if init/valid is not wildcard and the file time doesn't match
        for time_val in ['init', 'valid']:
            if (runtime[time_val] != '*' and
                    filetime[time_val] != runtime[time_val]):
                return False

        if runtime.get('lead', '*') == '*':
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

    def find_input_files(self, time_info, fill_missing=False):
        """! Loop over list of input templates and find files for each

             @param time_info time dictionary to use for string substitution
             @param fill_missing if True, add a placeholder if a file is not
              found. Defaults to False.
             @returns Dictionary of key input number and value is list of
              input file list if all files were found, None if not.
        """
        all_input_files = {}
        if not self.c_dict.get('TEMPLATE_DICT'):
            return None

        for label, input_template in self.c_dict['TEMPLATE_DICT'].items():
            self.c_dict['INPUT_TEMPLATE'] = input_template
            # if fill missing is true, data is not mandatory to find
            mandatory = not fill_missing
            input_files = self.find_data(time_info,
                                         return_list=True,
                                         mandatory=mandatory)
            if not input_files:
                if not fill_missing:
                    continue

                # if no files are found and fill missing is set, add 'missing'
                input_files = ['missing']

            all_input_files[label] = input_files

        # return None if no matching input files were found
        if not all_input_files:
            return None

        return all_input_files

    def subset_input_files(self, time_info, output_dir=None):
        """! Obtain a subset of input files from the c_dict ALL_FILES based on
             the time information for the current run.

              @param time_info dictionary containing time information
              @returns dictionary with keys of the input identifier and the
               value is the path to a ascii file containing the list of files
               or None if could not find any files
        """
        all_input_files = {}
        if not self.c_dict.get('ALL_FILES'):
            return all_input_files

        for file_dict in self.c_dict['ALL_FILES']:
            # compare time information for each input file
            # add file to list of files to use if it matches
            if not self.compare_time_info(time_info, file_dict['time_info']):
                continue

            for input_key in file_dict:
                # skip time info key
                if input_key == 'time_info':
                    continue

                if input_key not in all_input_files:
                    all_input_files[input_key] = []

                all_input_files[input_key].extend(file_dict[input_key])

        # return None if no matching input files were found
        if not all_input_files:
            return all_input_files

        # loop over all inputs and write a file list file for each
        list_file_dict = {}
        for identifier, input_files in all_input_files.items():
            list_file_name = self.get_list_file_name(time_info, identifier)
            list_file_path = self.write_list_file(list_file_name,
                                                  input_files,
                                                  output_dir=output_dir)
            list_file_dict[identifier] = list_file_path

        return list_file_dict

    def get_list_file_name(self, time_info, identifier):
        """! Build name of ascii file that contains a list of files to process.
             If wildcard is set for init, valid, or lead then use the text ALL
             in the filename.

        @param time_info dictionary containing time information
        @param identifier string to identify which input is used
        @returns filename i.e.
        {app_name}_files_{identifier}_init_{init}_valid_{valid}_lead_{lead}.txt
        """
        if time_info['init'] == '*':
            init = 'ALL'
        else:
            init = time_info['init'].strftime('%Y%m%d%H%M%S')

        if time_info['valid'] == '*':
            valid = 'ALL'
        else:
            valid = time_info['valid'].strftime('%Y%m%d%H%M%S')

        if time_info.get('lead', '*') == '*':
            lead = 'ALL'
        else:
            lead = time_util.ti_get_seconds_from_lead(time_info['lead'],
                                                      time_info['valid'])

        return (f"{self.app_name}_files_{identifier}_"
                f"init_{init}_valid_{valid}_lead_{lead}.txt")
