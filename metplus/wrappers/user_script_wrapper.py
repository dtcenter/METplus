"""
Program Name: user_script_wrapper.py
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
from . import RuntimeFreqWrapper
from ..util import do_string_sub

'''!@namespace UserScriptWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''


class UserScriptWrapper(RuntimeFreqWrapper):
    RUNTIME_FREQ_DEFAULT = None
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    def __init__(self, config, instance=None):
        self.app_name = "user_script"
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['COMMAND_TEMPLATE'] = (
            self.config.getraw('config',
                               'USER_SCRIPT_COMMAND')
        )
        if not c_dict['COMMAND_TEMPLATE']:
            self.log_error("Must supply a command to run with "
                           "USER_SCRIPT_COMMAND")

        c_dict['INPUT_DIR'] = self.config.getraw('config',
                                                 'USER_SCRIPT_INPUT_DIR',
                                                 '')
        self.get_input_templates(c_dict)

        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['IS_MET_CMD'] = False
        c_dict['LOG_THE_OUTPUT'] = True

        return c_dict

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        return self.c_dict['COMMAND']

    def run_at_time_once(self, time_info):
        """! Process runtime and build command to run

             @param time_info dictionary containing time information
             @returns True if command was run successfully, False otherwise
        """
        # if lead and either init or valid are set, compute other string sub
        if time_info.get('lead') != '*':
            if (time_info.get('init') != '*'
                    or time_info.get('valid') != '*'):
                time_info = time_util.ti_calculate(time_info)

        # create file list text files for the current run time criteria
        # set c_dict to the input file dict to set as environment vars
        self.c_dict['INPUT_LIST_DICT'] = (
            self.subset_input_files(time_info, force_list=True)
        )

        self.set_environment_variables(time_info)

        # substitute values from dictionary into command
        self.c_dict['COMMAND'] = (
            do_string_sub(self.c_dict['COMMAND_TEMPLATE'],
                          **time_info)
        )

        return self.build()

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime. The parent implementation of
             this function creates a dictionary and adds the time_info to it.
             This wrapper gets all files for the current runtime and adds it to
             the dictionary with keys 'fcst' and 'obs'

             @param time_info dictionary containing time information
             @returns dictionary containing time_info dict and any relevant
             files with a key representing a description of that file
        """
        file_dict = super().get_files_from_time(time_info)

        input_files = self.get_input_files(time_info, fill_missing=True)
        if input_files is None:
            return file_dict

        for key, value in input_files.items():
            file_dict[key] = value

        return file_dict

    def set_environment_variables(self, time_info):
        """! Set environment variables that will be read set when running this
         tool. Wrappers could override it to set wrapper-specific values,
         then call super version to handle user configs and printing

        @param time_info dictionary containing timing info from current run
        """

        for identifier, file_path in self.c_dict['INPUT_LIST_DICT'].items():
            self.add_env_var(f'METPLUS_FILELIST_{identifier.upper()}',
                             file_path)

        super().set_environment_variables(time_info)

    def get_all_files(self, custom=None):
        """! Call parent function to attempt to get files but always return
        True because this functionality is optional

        @returns True
        """
        all_files = super().get_all_files(custom)
        if not all_files:
            return True
        return all_files
