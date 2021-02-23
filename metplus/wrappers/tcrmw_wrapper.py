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

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_INIT_INCLUDE',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_VALID_INCLUDE_LIST',
        'METPLUS_VALID_EXCLUDE_LIST',
        'METPLUS_VALID_HOUR_LIST',
        'METPLUS_LEAD_LIST',
        'METPLUS_DATA_FILE_TYPE',
        'METPLUS_DATA_FIELD',
        'METPLUS_REGRID_DICT',
        'METPLUS_N_RANGE',
        'METPLUS_N_AZIMUTH',
        'METPLUS_MAX_RANGE_KM',
        'METPLUS_DELTA_RANGE_KM',
        'METPLUS_RMW_SCALE',
    ]
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "tc_rmw"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_RMW_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'TC_RMW_CONFIG_FILE', '')

        c_dict['INPUT_DIR'] = self.config.getdir('TC_RMW_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'TC_RMW_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_RMW_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_RMW_OUTPUT_TEMPLATE')
        )

        c_dict['DECK_INPUT_DIR'] = self.config.getdir('TC_RMW_DECK_INPUT_DIR',
                                                      '')
        c_dict['DECK_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_RMW_DECK_TEMPLATE')
        )

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_INPUT_DATATYPE',
                                   'file_type',
                                   'METPLUS_DATA_FILE_TYPE')

        # values used in configuration file
        self.set_met_config_string(self.env_var_dict,
                                   'MODEL',
                                   'model',
                                   'METPLUS_MODEL')

        self.handle_regrid(c_dict, set_to_grid=False)

        self.set_met_config_int(self.env_var_dict,
                                'TC_RMW_N_RANGE',
                                'n_range',
                                'METPLUS_N_RANGE')

        self.set_met_config_int(self.env_var_dict,
                                'TC_RMW_N_AZIMUTH',
                                'n_azimuth',
                                'METPLUS_N_AZIMUTH')

        self.set_met_config_float(self.env_var_dict,
                                  'TC_RMW_MAX_RANGE_KM',
                                  'max_range_km',
                                  'METPLUS_MAX_RANGE_KM')

        self.set_met_config_float(self.env_var_dict,
                                  'TC_RMW_DELTA_RANGE_KM',
                                  'delta_range_km',
                                  'METPLUS_DELTA_RANGE_KM')

        self.set_met_config_float(self.env_var_dict,
                                  'TC_RMW_SCALE',
                                  'rmw_scale',
                                  'METPLUS_RMW_SCALE')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_STORM_ID',
                                   'storm_id',
                                   'METPLUS_STORM_ID')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_BASIN',
                                   'basin',
                                   'METPLUS_BASIN')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_CYCLONE',
                                   'cyclone',
                                   'METPLUS_CYCLONE')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_INIT_INCLUDE',
                                   'init_inc',
                                   'METPLUS_INIT_INCLUDE')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_VALID_BEG',
                                   'valid_beg',
                                   'METPLUS_VALID_BEG')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_RMW_VALID_END',
                                   'valid_end',
                                   'METPLUS_VALID_END')

        self.set_met_config_list(self.env_var_dict,
                                 'TC_RMW_VALID_INCLUDE_LIST',
                                 'valid_inc',
                                 'METPLUS_VALID_INCLUDE_LIST')

        self.set_met_config_list(self.env_var_dict,
                                 'TC_RMW_VALID_EXCLUDE_LIST',
                                 'valid_exc',
                                 'METPLUS_VALID_EXCLUDE_LIST')

        self.set_met_config_list(self.env_var_dict,
                                 'TC_RMW_VALID_HOUR_LIST',
                                 'valid_hour',
                                 'METPLUS_VALID_HOUR_LIST')

        return c_dict

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
              loops over the list of forecast leads and runs the
               application for each.
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

        data_field = ','.join(all_fields)
        self.env_var_dict['METPLUS_DATA_FIELD'] = f'field = [{data_field}];'

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
                    time_util.ti_get_hours_from_relativedelta(lead,
                                                              valid_time=time_info['valid'])
                    )
                lead_list.append(f'"{str(lead_hours).zfill(2)}"')

            self.c_dict['LEAD_LIST'] = f"lead = [{', '.join(lead_list)}];"

        return self.infiles

    def set_command_line_arguments(self, time_info):

        # add config file - passing through do_string_sub to get custom string if set
        if self.c_dict['CONFIG_FILE']:
            config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)
            self.args.append(f"-config {config_file}")
