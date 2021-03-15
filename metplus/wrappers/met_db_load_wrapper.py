"""
Program Name: met_db_load_wrapper.py
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

'''!@namespace METdataDBWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''

class METdataDBWrapper(RuntimeFreqWrapper):
    def __init__(self, config, instance=None, config_overrides={}):
        met_data_db_dir = config.getdir('MET_DATA_DB_DIR')
        self.app_path = os.path.join(met_data_db_dir,
                                     'METdbLoad',
                                     'ush',
                                     'met_db_load.py')
        self.app_name = os.path.basename(self.app_path)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['XML_FILE'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_XML_FILE')
        )
        if not c_dict['XML_FILE']:
            self.log_error("Must supply an XML file with "
                           "MET_DB_LOAD_XML_FILE")

        c_dict['INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_INPUT_TEMPLATE')
        )
        if not c_dict['INPUT_TEMPLATE']:
            self.log_error("Must supply an input template with "
                           "MET_DB_LOAD_INPUT_TEMPLATE")

        c_dict['MV_HOST'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_HOST')
        )
        c_dict['MV_DATABASE'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_DATABASE')
        )
        c_dict['MV_USER'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_USER')
        )

        c_dict['IS_MET_CMD'] = False
        c_dict['LOG_THE_OUTPUT'] = True

        return c_dict

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        return f"python3 {self.app_path} {self.c_dict['XML_FILE']}"

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

            # substitute values from time dictionary
            input_path = (
                do_string_sub(self.c_dict['INPUT_TEMPLATE'],
                              **time_info)
            )
            # set up dictionary of text to substitute in XML file
            substitution_dict = {}
            substitution_dict['METPLUS_INPUT_PATH'] = input_path
            substitution_dict['METPLUS_USER'] = self.c_dict['MV_USER']
            substitution_dict['METPLUS_HOST'] = self.c_dict['MV_HOST']
            substitution_dict['METPLUS_DATABASE'] = self.c_dict['MV_DATABASE']

            # run command
            if not self.build():
                success = False

        return success

    def get_all_files(self, custom=None):
        """! Don't get list of all files for METdataDB wrapper

            @returns True to report that no failures occurred
        """
        return True
