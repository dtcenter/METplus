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

from ..util import met_util as util
from ..util import time_util
from . import RuntimeFreqWrapper
from ..util import do_string_sub

'''!@namespace UserScriptWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''

class UserScriptWrapper(RuntimeFreqWrapper):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "user_script"
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['COMMAND_TEMPLATE'] = (
            self.config.getraw('config',
                               'USER_SCRIPT_COMMAND')
        )
        if not c_dict['COMMAND_TEMPLATE']:
            self.log_error("Must supply a command to run with "
                           "USER_SCRIPT_COMMAND")

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
        success = True

        # if custom is already set in time info, run for only that item
        # if not, loop over the CUSTOM_LOOP_LIST and process once for each
        if 'custom' in time_info:
            custom_loop_list = [time_info['custom']]
        else:
            custom_loop_list = self.c_dict['CUSTOM_LOOP_LIST']

        for custom_string in custom_loop_list:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            time_info['custom'] = custom_string
            # if lead and either init or valid are set, compute other string sub
            if time_info.get('lead') != '*':
                if (time_info.get('init') != '*'
                        or time_info.get('valid') != '*'):
                    time_info = time_util.ti_calculate(time_info)

            self.set_environment_variables(time_info)

            # substitute values from dictionary into command
            self.c_dict['COMMAND'] = (
                do_string_sub(self.c_dict['COMMAND_TEMPLATE'],
                              **time_info)
            )

            # if command contains wildcard character, run in shell
            if '*' in self.c_dict['COMMAND']:
                self.c_dict['RUN_IN_SHELL'] = True

            # run command
            if not self.build():
                success = False

        return success

    def get_all_files(self, custom=None):
        """! Don't get list of all files for UserScript wrapper

            @returns True to report that no failures occurred
        """
        return True
