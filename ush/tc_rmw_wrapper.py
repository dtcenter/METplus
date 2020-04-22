#!/usr/bin/env python

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

import metplus_check_python_version

import os
import met_util as util
import time_util
from command_builder import CommandBuilder
from string_template_substitution import StringSub

'''!@namespace TCRMWWrapper
@brief Wraps the TC-RMW tool
@endcode
'''


class TCRMWWrapper(CommandBuilder):
    def __init__(self, config, logger):
        self.app_name = "tc_rmw"
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)
        super().__init__(config, logger)

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

        c_dict['ADECK_INPUT_DIR'] = self.config.getdir('TC_RMW_ADECK_INPUT_DIR', '')
        c_dict['ADECK_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                            'TC_RMW_ADECK_TEMPLATE')

        # values used in configuration file
        c_dict['MODEL'] = self.config.getstr('config', 'MODEL', 'GFS')
        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'TC_RMW_REGRID_TO_GRID', '')

        c_dict['N_RANGE'] = ''
        conf_value = self.config.getint('config', 'TC_RMW_N_RANGE')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE_INT:
            c_dict['N_RANGE'] = f"n_range = {str(conf_value)};"

        c_dict['N_AZIMUTH'] = ''
        conf_value = self.config.getint('config', 'TC_RMW_N_AZIMUTH')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE_INT:
            c_dict['N_AZIMUTH'] = f"n_azimuth = {str(conf_value)};"

        c_dict['MAX_RANGE_KM'] = ''
        conf_value = self.config.getfloat('config', 'TC_RMW_MAX_RANGE_KM',)
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE_FLOAT:
            c_dict['MAX_RANGE_KM'] = f"max_range_km = {str(conf_value)};"

        c_dict['DELTA_RANGE_KM'] = ''
        conf_value = self.config.getfloat('config', 'TC_RMW_DELTA_RANGE_KM')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE_FLOAT:
            c_dict['DELTA_RANGE_KM'] = f"delta_range_km = {str(conf_value)};"

        c_dict['RMW_SCALE'] = ''
        conf_value = self.config.getfloat('config', 'TC_RMW_SCALE')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE_FLOAT:
            c_dict['RMW_SCALE'] = f"rmw_scale = {str(conf_value)};"

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""

        self.add_env_var('DATA_FIELD',
                         self.c_dict.get('DATA_FIELD', ''))

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

        model = self.c_dict.get('MODEL', '')
        if model:
            model = f"model = {model};"
        self.add_env_var('MODEL', model)

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

        # add input files
        cmd += ' -data'
        for infile in self.infiles:
            cmd += ' ' + infile

        # add adeck
        cmd += ' -adeck ' + self.c_dict['ADECK_FILE']

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
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            self.clear()
            input_dict['lead'] = lead

            time_info = time_util.ti_calculate(input_dict)
            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string

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
        self.c_dict['DATA_FIELD'] = ''
        field_list = util.parse_var_list(self.config,
                                         time_info,
                                         met_tool=self.app_name)
        if not field_list:
            self.log_error("Could not get field information from config.")
            return False

        for field in field_list:
            field_list = self.get_field_info(d_type='FCST',
                                             v_name=field['fcst_name'],
                                             v_level=field['fcst_level'],
                                             )
            if field_list is None:
                return False

            formatted_fields = ','.join(field_list)
            self.c_dict['DATA_FIELD'] = formatted_fields
            return True

    def find_input_files(self, time_info):
        # get a list of the input data files, write to an ascii file if there are more than one
        input_files = self.find_data(time_info, return_list=True)
        if not input_files:
            return None

        if len(input_files) > 1:

        else:
            input_file = input_files[0]

        self.infiles.append(input_file)

        # get adeck file
        adeck_file = self.find_data(time_info, data_type='ADECK')
        if not adeck_file:
            return None

        # get list of files even if only one is found (return_list=True)
#        obs_path = self.find_obs(time_info, var_info=None, return_list=True)
#        if obs_path is None:
#            return None

#        self.infiles.extend(obs_path)
        return self.infiles

    def set_command_line_arguments(self, time_info):

        # add config file - passing through StringSub to get custom string if set
        if self.c_dict['CONFIG_FILE']:
            config_file = StringSub(self.logger,
                                    self.c_dict['CONFIG_FILE'],
                                    **time_info).do_string_sub()
            self.args.append(f"-config {config_file}")

if __name__ == "__main__":
    util.run_stand_alone(__file__, "TCRMW")
