"""tc_rmw
Program Name: tc_rmw_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs tc_rmw
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace TCRMWWrapper
@brief Wraps the TC-RMW tool
@endcode
'''


class TCRMWWrapper(CommandBuilder):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "tc_rmw"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_TC_RMW_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'TC_RMW_CONFIG_FILE', '')

        c_dict['INPUT_DIR'] = self.config.getdir('TC_RMW_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'TC_RMW_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_RMW_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'TC_RMW_OUTPUT_TEMPLATE')

        c_dict['DECK_INPUT_DIR'] = self.config.getdir('TC_RMW_DECK_INPUT_DIR', '')
        c_dict['DECK_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                            'TC_RMW_DECK_TEMPLATE')

        data_type = self.config.getstr('config', 'TC_RMW_INPUT_DATATYPE', '')
        if data_type:
            c_dict[f'DATA_FILE_TYPE'] = f"file_type = {data_type};"

        # values used in configuration file

        conf_value = self.config.getstr('config', 'MODEL', '')
        if conf_value:
            c_dict['MODEL'] = f'model = "{util.remove_quotes(conf_value)}";'

        conf_value = self.config.getstr('config', 'TC_RMW_REGRID_METHOD', '')
        if conf_value:
            c_dict['REGRID_METHOD'] = f"method = {conf_value};"

        conf_value = self.config.getint('config', 'TC_RMW_REGRID_WIDTH')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['REGRID_WIDTH'] = f"width = {str(conf_value)};"

        conf_value = self.config.getfloat('config', 'TC_RMW_REGRID_VLD_THRESH', )
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['REGRID_VLD_THRESH'] = f"vld_thresh = {str(conf_value)};"

        conf_value = self.config.getstr('config', 'TC_RMW_REGRID_SHAPE', '')
        if conf_value:
            c_dict['REGRID_SHAPE'] = f"shape = {conf_value};"

        conf_value = self.config.getint('config', 'TC_RMW_N_RANGE')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['N_RANGE'] = f"n_range = {str(conf_value)};"

        conf_value = self.config.getint('config', 'TC_RMW_N_AZIMUTH')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['N_AZIMUTH'] = f"n_azimuth = {str(conf_value)};"

        conf_value = self.config.getfloat('config', 'TC_RMW_MAX_RANGE_KM',)
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['MAX_RANGE_KM'] = f"max_range_km = {str(conf_value)};"

        conf_value = self.config.getfloat('config', 'TC_RMW_DELTA_RANGE_KM')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['DELTA_RANGE_KM'] = f"delta_range_km = {str(conf_value)};"

        conf_value = self.config.getfloat('config', 'TC_RMW_SCALE')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['RMW_SCALE'] = f"rmw_scale = {str(conf_value)};"

        conf_value = self.config.getstr('config', 'TC_RMW_STORM_ID', '')
        if conf_value:
            c_dict['STORM_ID'] = f'storm_id = "{conf_value}";'

        conf_value = self.config.getstr('config', 'TC_RMW_BASIN', '')
        if conf_value:
            c_dict['BASIN'] = f'basin = "{conf_value}";'

        conf_value = self.config.getstr('config', 'TC_RMW_CYCLONE', '')
        if conf_value:
            c_dict['CYCLONE'] = f'cyclone = "{conf_value}";'

        conf_value = self.config.getstr('config',
                                        'TC_RMW_INIT_INCLUDE',
                                        '')
        if conf_value:
            c_dict['INIT_INCLUDE'] = f'init_inc = "{conf_value}";'

        conf_value = self.config.getstr('config',
                                        'TC_RMW_VALID_BEG',
                                        self.config.getstr('config',
                                                           'VALID_BEG',
                                                           ''))
        if conf_value:
            c_dict['VALID_BEG'] = f'valid_beg = "{conf_value}";'

        conf_value = self.config.getstr('config',
                                        'TC_RMW_VALID_END',
                                        self.config.getstr('config',
                                                           'VALID_END',
                                                           ''))
        if conf_value:
            c_dict['VALID_END'] = f'valid_end = "{conf_value}";'

        conf_value = util.getlist(self.config.getstr('config',
                                                     'TC_RMW_VALID_INCLUDE_LIST',
                                                     ''))
        if conf_value:
            conf_list = str(conf_value).replace("'", '"')
            c_dict['VALID_INCLUDE_LIST'] = f"valid_inc = {conf_list};"

        conf_value = util.getlist(self.config.getstr('config',
                                                     'TC_RMW_VALID_EXCLUDE_LIST',
                                                     ''))
        if conf_value:
            conf_list = str(conf_value).replace("'", '"')
            c_dict['VALID_EXCLUDE_LIST'] = f"valid_exc = {conf_list};"

        conf_value = util.getlist(self.config.getstr('config',
                                                     'TC_RMW_VALID_HOUR_LIST',
                                                     ''))
        if conf_value:
            conf_list = str(conf_value).replace("'", '"')
            c_dict['VALID_HOUR_LIST'] = f"valid_hour = {conf_list};"

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""

        self.add_env_var('DATA_FILE_TYPE',
                         self.c_dict.get('DATA_FILE_TYPE', ''))

        self.add_env_var('DATA_FIELD',
                         self.c_dict.get('DATA_FIELD', ''))

        self.add_env_var('MODEL',
                         self.c_dict.get('MODEL', ''))

        regrid_dict_string = ''
        # if any regrid items are set, create the regrid dictionary and add them
        if (self.c_dict.get('REGRID_METHOD', '') or self.c_dict.get('REGRID_WIDTH', '') or
                self.c_dict.get('REGRID_VLD_THRESH', '') or self.c_dict.get('REGRID_SHAPE', '')):
            regrid_dict_string = 'regrid = {'
            regrid_dict_string += f"{self.c_dict.get('REGRID_METHOD', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_WIDTH', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_VLD_THRESH', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_SHAPE', '')}"
            regrid_dict_string += '}'

        self.add_env_var('REGRID_DICT',
                         regrid_dict_string)

        self.add_env_var('N_RANGE',
                         self.c_dict.get('N_RANGE', ''))

        self.add_env_var('N_AZIMUTH',
                         self.c_dict.get('N_AZIMUTH', ''))

        self.add_env_var('MAX_RANGE_KM',
                         self.c_dict.get('MAX_RANGE_KM', ''))

        self.add_env_var('DELTA_RANGE_KM',
                         self.c_dict.get('DELTA_RANGE_KM', ''))

        self.add_env_var('RMW_SCALE',
                         self.c_dict.get('RMW_SCALE', ''))

        self.add_env_var('STORM_ID',
                         self.c_dict.get('STORM_ID', ''))

        self.add_env_var('BASIN',
                         self.c_dict.get('BASIN', ''))

        self.add_env_var('CYCLONE',
                         self.c_dict.get('CYCLONE', ''))

        self.add_env_var('INIT_INCLUDE',
                         self.c_dict.get('INIT_INC', ''))

        self.add_env_var('VALID_BEG',
                         self.c_dict.get('VALID_BEG', ''))

        self.add_env_var('VALID_END',
                         self.c_dict.get('VALID_END', ''))

        self.add_env_var('VALID_INCLUDE_LIST',
                         self.c_dict.get('VALID_INCLUDE_LIST', ''))

        self.add_env_var('VALID_EXCLUDE_LIST',
                         self.c_dict.get('VALID_EXCLUDE_LIST', ''))

        self.add_env_var('VALID_HOUR_LIST',
                         self.c_dict.get('VALID_HOUR_LIST', ''))

        self.add_env_var('LEAD_LIST',
                         self.c_dict.get('LEAD_LIST', ''))

        super().set_environment_variables(time_info)

    def get_command(self):
        cmd = self.app_path

        # don't run if no input or output files were found
        if not self.infiles:
            self.log_error("No input files were found")
            return

        if not self.outfile:
            self.log_error("No output file specified")
            return

        # add deck
        cmd += ' -adeck ' + self.c_dict['DECK_FILE']

        # add input files
        cmd += ' -data'
        for infile in self.infiles:
            cmd += ' ' + infile

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add output path
        out_path = self.get_output_path()
        cmd += ' -out ' + out_path

        parent_dir = os.path.dirname(out_path)
        if not parent_dir:
            self.log_error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
        """
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string

            time_info = time_util.ti_calculate(input_dict)

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param time_info dictionary containing timing information
        """
        # get input files
        if self.find_input_files(time_info) is None:
            return

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get field information to set in MET config
        if not self.set_data_field(time_info):
            return

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return

        self.build()

    def set_data_field(self, time_info):
        """!Get list of fields from config to process. Build list of field info
            that are formatted to be read by the MET config file. Set DATA_FIELD
            item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """

        field_list = util.parse_var_list(self.config,
                                         time_info,
                                         data_type='FCST',
                                         met_tool=self.app_name)
        if not field_list:
            self.log_error("Could not get field information from config.")
            return False

        all_fields = []
        for field in field_list:
            field_list = self.get_field_info(d_type='FCST',
                                             v_name=field['fcst_name'],
                                             v_level=field['fcst_level'],
                                             )
            if field_list is None:
                return False

            all_fields.extend(field_list)

        self.c_dict['DATA_FIELD'] = ','.join(all_fields)

        return True

    def find_input_files(self, time_info):
        """!Get DECK file and list of input data files and set c_dict items.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns Input file list if all files were found, None if not.
        """

        # tc_rmw currently doesn't support an ascii file that contains a list of input files
        # setting this to False will list each file in the command, which can be difficult to read
        # when the tool supports reading a file list file, we should use the logic when
        # use_file_list = True
        use_file_list = False

        # get deck file
        deck_file = self.find_data(time_info, data_type='DECK')
        if not deck_file:
            return None

        self.c_dict['DECK_FILE'] = deck_file

        all_input_files = []

        lead_seq = util.get_lead_sequence(self.config, time_info)
        for lead in lead_seq:
            self.clear()
            time_info['lead'] = lead

            time_info = time_util.ti_calculate(time_info)

            # get a list of the input data files, write to an ascii file if there are more than one
            input_files = self.find_data(time_info, return_list=True)
            if not input_files:
                continue

            all_input_files.extend(input_files)

        if not all_input_files:
            return None

        if use_file_list:
            # create an ascii file with a list of the input files
            list_file = self.write_list_file(f"{os.path.basename(adeck_file)}_data_files.txt",
                                             all_input_files)
            self.infiles.append(list_file)
        else:
            self.infiles.extend(all_input_files)

        # set LEAD_LIST to list of forecast leads used
        if lead_seq != [0]:
            lead_list = []
            for lead in lead_seq:
                lead_hours = (
                    time_util.ti_get_seconds_from_relativedelta(lead,
                                                                valid_time=time_info['valid'])
                    ) // 3600
                lead_list.append(f'"{str(lead_hours).zfill(2)}"')

            self.c_dict['LEAD_LIST'] = f"lead = [{', '.join(lead_list)}];"

        return self.infiles

    def set_command_line_arguments(self, time_info):

        # add config file - passing through do_string_sub to get custom string if set
        if self.c_dict['CONFIG_FILE']:
            config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)
            self.args.append(f"-config {config_file}")
