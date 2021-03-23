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
from ..util import do_string_sub, getlist

'''!@namespace METDbLoadWrapper
@brief Parent class for wrappers that run over a grouping of times
@endcode
'''

class METDbLoadWrapper(RuntimeFreqWrapper):
    """! Config variable names - All names are prepended with MET_DB_LOAD_MV_
         and all c_dict values are prepended with MV_.
         The name is the key and string specifying the type is the value.
    """
    CONFIG_NAMES = {'HOST': 'string',
                    'DATABASE': 'string',
                    'USER': 'string',
                    'PASSWORD': 'string',
                    'VERBOSE': 'bool',
                    'INSERT_SIZE': 'int',
                    'MODE_HEADER_DB_CHECK': 'bool',
                    'DROP_INDEXES': 'bool',
                    'APPLY_INDEXES': 'bool',
                    'GROUP': 'string',
                    'LOAD_STAT': 'bool',
                    'LOAD_MODE': 'bool',
                    'LOAD_MTD': 'bool',
                    'LOAD_MPR': 'bool',
                    }

    def __init__(self, config, instance=None, config_overrides={}):
        met_data_db_dir = config.getdir('MET_DATA_DB_DIR')
        self.app_path = os.path.join(met_data_db_dir,
                                     'METdbLoad',
                                     'ush',
                                     'met_db_load')
        self.app_name = os.path.basename(self.app_path)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['XML_TEMPLATE'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_XML_FILE')
        )
        if not c_dict['XML_TEMPLATE']:
            self.log_error("Must supply an XML file with "
                           "MET_DB_LOAD_XML_FILE")

        c_dict['INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'MET_DB_LOAD_INPUT_TEMPLATE')
        )
        if not c_dict['INPUT_TEMPLATE']:
            self.log_error("Must supply an input template with "
                           "MET_DB_LOAD_INPUT_TEMPLATE")

        c_dict['REMOVE_TMP_XML'] = (
            self.config.getbool('config',
                                'MET_DB_LOAD_REMOVE_TMP_XML',
                                True)
        )

        # read config variables
        for name, type in self.CONFIG_NAMES.items():
            if type == 'int':
                get_fct = self.config.getint
            elif type == 'bool':
                get_fct = self.config.getbool
            else:
                get_fct = self.config.getraw
            value = get_fct('config',
                            f'MET_DB_LOAD_MV_{name}',
                            '')
            if value == '':
                self.log_error(f"Must set MET_DB_LOAD_MV_{name}")
            c_dict[f'MV_{name}'] = value

        c_dict['IS_MET_CMD'] = False
        c_dict['LOG_THE_OUTPUT'] = True

        return c_dict

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        return f"python3 {self.app_path}.py {self.c_dict.get('XML_TMP_FILE')}"

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

            if not self.replace_values_in_xml(time_info):
                return

            # run command
            if not self.build():
                success = False

            # remove tmp file
            if self.c_dict.get('REMOVE_TMP_XML', True):
                xml_file = self.c_dict.get('XML_TMP_FILE')
                if xml_file and os.path.exists(xml_file):
                    self.logger.debug(f"Removing tmp file: {xml_file}")
                    os.remove(xml_file)

        return success

    def get_all_files(self, custom=None):
        """! Don't get list of all files for METdataDB wrapper

            @returns True to report that no failures occurred
        """
        return True

    def get_stat_directories(self, input_paths):
        """! Traverse through files under input path and find all directories
        that contain .stat or .tcst files.

        @param input_path top level directory to search
        @returns list of unique directories that contain stat files
        """
        stat_dirs = set()
        for input_path in getlist(input_paths):
            self.logger.debug("Finding directories with stat files "
                              f"under {input_path}")
            for root, _, files in os.walk(input_path):
                for filename in files:
                    if (not filename.endswith('.stat') and
                            not filename.endswith('.tcst')):
                        continue
                    filepath = os.path.join(root, filename)
                    stat_dir = os.path.dirname(filepath)
                    stat_dirs.add(stat_dir)

        stat_dirs = list(stat_dirs)
        for stat_dir in stat_dirs:
            self.logger.info(f"Adding stat file directory: {stat_dir}")

        return stat_dirs

    def format_stat_dirs(self, stat_dirs):
        """! Format list of stat directories to substitute into XML file.
        <vaL></val> tags wil be added around each value.

        @param stat_dirs list of directories that contain stat files
        @returns string of formatted values
        """
        formatted_stat_dirs = []
        for stat_dir in stat_dirs:
            formatted_stat_dirs.append(f'<val>{stat_dir}</val>')

        output_string = '\n      '.join(formatted_stat_dirs)
        return output_string

    def populate_sub_dict(self, time_info):
        sub_dict = {}

        # substitute values from time dictionary
        input_paths = (
            do_string_sub(self.c_dict['INPUT_TEMPLATE'],
                          **time_info)
        )
        stat_dirs = self.get_stat_directories(input_paths)
        formatted_stat_dirs = self.format_stat_dirs(stat_dirs)
        sub_dict['METPLUS_INPUT_PATHS'] = formatted_stat_dirs

        for name, type in self.CONFIG_NAMES.items():
            value = str(self.c_dict.get(f'MV_{name}'))
            if type == 'bool':
                value = value.lower()

            value = do_string_sub(value,
                                  **time_info)

            sub_dict[f'METPLUS_MV_{name}'] = value

        return sub_dict

    def replace_values_in_xml(self, time_info):
        self.c_dict['XML_TMP_FILE'] = None

        xml_template = self.c_dict.get('XML_TEMPLATE')
        if not xml_template:
            return False

        # set up dictionary of text to substitute in XML file
        sub_dict = self.populate_sub_dict(time_info)

        # open XML template file and replace any values encountered
        with open(xml_template, 'r') as file_handle:
            input_lines = file_handle.read().splitlines()

        output_lines = []
        for input_line in input_lines:
            output_line = input_line
            for replace_string, value in sub_dict.items():
                output_line = output_line.replace(f"${{{replace_string}}}",
                                                  value)
            output_lines.append(output_line)

        # write tmp file with XML content with substituted values
        out_filename = util.generate_tmp_filename()
        out_path = os.path.join(self.config.getdir('TMP_DIR'),
                                out_filename)
        with open(out_path, 'w') as file_handle:
            for line in output_lines:
                file_handle.write(f'{line}\n')

        self.c_dict['XML_TMP_FILE'] = out_path
        return True
