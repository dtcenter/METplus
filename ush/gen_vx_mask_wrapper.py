#!/usr/bin/env python

"""
Program Name: gen_vx_mask_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs gen_vx_mask
History Log:  Initial version
Usage:
Parameters: None
Input Files: ascii files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import metplus_check_python_version

import os
import met_util as util
import time_util
from command_builder import CommandBuilder
from string_template_substitution import StringSub

'''!@namespace GenVxMaskWrapper
@brief Wraps the GenVxMask tool to reformat ascii format to NetCDF
@endcode
'''


class GenVxMaskWrapper(CommandBuilder):
    # valid values for the -type argument
    VALID_MASKING_TYPES = ["poly",
                           "box",
                           "circle",
                           "track",
                           "grid",
                           "data",
                           "solar_alt",
                           "solar_azi",
                           "lat",
                           "lon",
                           "shape",
                           ]

    def __init__(self, config, logger):
        self.app_name = "gen_vx_mask"
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)
        super().__init__(config, logger)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GEN_VX_MASK_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        # input and output files
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_DIR',
                                                     '')
        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                          'GEN_VX_MASK_INPUT_TEMPLATE')

        c_dict['MASK_INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_MASK_DIR',
                                                      '')
        c_dict['MASK_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                           'GEN_VX_MASK_INPUT_MASK_TEMPLATE')
        c_dict['OUTPUT_DIR'] = self.config.getdir('GEN_VX_MASK_OUTPUT_DIR',
                                                  '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'GEN_VX_MASK_OUTPUT_TEMPLATE')

        # handle window variables [GEN_VX_MASK_]FILE_WINDOW_[BEGIN/END]
        c_dict['OBS_FILE_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'GEN_VX_MASK_FILE_WINDOW_BEGIN',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_BEGIN', 0))
        c_dict['OBS_FILE_WINDOW_END'] = \
          self.config.getseconds('config', 'GEN_VX_MASK_FILE_WINDOW_END',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_END', 0))

        # use the same file windows for input and mask files
        c_dict['MASK_FILE_WINDOW_BEGIN'] = c_dict['OBS_FILE_WINDOW_BEGIN']
        c_dict['MASK_FILE_WINDOW_END'] = c_dict['OBS_FILE_WINDOW_END']

        # optional arguments
        c_dict['TYPE'] = self.config.getstr('config',
                                            'GEN_VX_MASK_TYPE',
                                            'poly')
        # if type is not set, set it to poly
        if not c_dict['TYPE']:
            c_dict['TYPE'] = 'poly'

        # check if value set for type is one of the valid options
        if c_dict['TYPE'] not in self.VALID_MASKING_TYPES:
            self.log_error(f"GEN_VX_MASK_TYPE value ({c_dict['TYPE']})is invalid. "
                           f"Valid options are {self.VALID_MASKING_TYPES}")
            self.isOK = False

        c_dict['INPUT_FIELD'] = self.config.getraw('config',
                                                   'GEN_VX_MASK_INPUT_FIELD',
                                                   '')
        c_dict['MASK_FIELD'] = self.config.getraw('config',
                                                  'GEN_VX_MASK_INPUT_MASK_FIELD',
                                                  '')
        c_dict['COMPLEMENT_FLAG'] = self.config.getbool('config',
                                                        'GEN_VX_MASK_COMPLEMENT_FLAG',
                                                        False)

        c_dict['UNION_FLAG'] = self.config.getbool('config',
                                                   'GEN_VX_MASK_UNION_FLAG',
                                                   False)

        c_dict['INTERSECTION_FLAG'] = self.config.getbool('config',
                                                          'GEN_VX_MASK_INTERSECTION_FLAG',
                                                          False)

        c_dict['SYMDIFF_FLAG'] = self.config.getbool('config',
                                                     'GEN_VX_MASK_SYMDIFF_FLAG',
                                                     False)

        # only one combination flag can be set. In sum, False becomes 0 and True becomes 1
        # so a sum greater than 1 means more than one value is True
        if sum([c_dict['UNION_FLAG'], c_dict['INTERSECTION_FLAG'], c_dict['SYMDIFF_FLAG']]) > 1:
            self.log_error("Only one combination flag (GEN_VX_MASK_[UNION/INTERSECTION/SYMDIFF]_FLAG)"
                           "can be set.")
            self.isOK = False


        c_dict['THRESH'] = self.config.getstr('config',
                                              'GEN_VX_MASK_THRESH',
                                              '')

        c_dict['HEIGHT'] = self.get_optional_number_from_config('config',
                                                                'GEN_VX_MASK_HEIGHT',
                                                                int)

        c_dict['WIDTH'] = self.get_optional_number_from_config('config',
                                                               'GEN_VX_MASK_WIDTH',
                                                               int)

        c_dict['SHAPENO'] = self.get_optional_number_from_config('config',
                                                                 'GEN_VX_MASK_SHAPE_NUMBER',
                                                                 int)

        c_dict['VALUE'] = self.get_optional_number_from_config('config',
                                                               'GEN_VX_MASK_VALUE',
                                                               float)

        c_dict['NAME'] = self.config.getstr('config',
                                            'GEN_VX_MASK_OUTPUT_NAME',
                                            '')

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read set when running this tool.
            This tool does not have a config file, but environment variables may still
            need to be set, such as MET_TMP_DIR and MET_PYTHON_EXE.
            Reformat as needed. Print list of variables that were set and their values.
            This function could be moved up to CommandBuilder so all wrappers have access to it.
            Wrappers could override it to set wrapper-specific values, then call the CommandBuilder
            version to handle user configs and printing
            Args:
              @param time_info dictionary containing timing info from current run"""
        # set user environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        self.print_all_envs()

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
        for infile in self.infiles:
            cmd += ' ' + infile

        # add output path
        out_path = self.get_output_path()
        cmd += ' ' + out_path

        parent_dir = os.path.dirname(out_path)
        if parent_dir == '':
            self.log_error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # add arguments
        cmd += ' ' + ' '.join(self.args)

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
        """! Process runtime and try to build command to run gen_vx_mask
             Args:
                @param time_info dictionary containing timing information
        """
        # get input files
        if self.find_input_files(time_info) is None:
            return

        # get output path
        if not self.find_and_check_output_file(time_info):
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

    def find_input_files(self, time_info):
        """!Find input file and mask file and add them to the list of input files.
            Args:
                @param time_info time dictionary for current run time
                @returns List of input files found or None if either file was not found
        """
        # get input file
        # calling find_obs because we set OBS_ variables in c_dict for the input data
        input_path = self.find_obs(time_info,
                                   var_info=None)
        if input_path is None:
            return None

        self.infiles.append(input_path)

        # get mask file
        mask_path = self.find_data(time_info,
                                   var_info=None,
                                   data_type='MASK')
        if mask_path is None:
            return None

        self.infiles.append(mask_path)

        return self.infiles

    def set_command_line_arguments(self, time_info):
        """!Set command line arguments from c_dict
            Args:
                @param time_info time dictionary to use for string substitution"""
        if self.c_dict['TYPE']:
            self.args.append(f"-type {self.c_dict['TYPE']}")

        if self.c_dict['INPUT_FIELD']:
            input_field = StringSub(self.logger,
                                    self.c_dict['INPUT_FIELD'],
                                    **time_info).do_string_sub()
            self.args.append(f"-input_field {input_field}")

        if self.c_dict['MASK_FIELD']:
            mask_field = StringSub(self.logger,
                                   self.c_dict['MASK_FIELD'],
                                   **time_info).do_string_sub()
            self.args.append(f"-mask_field {mask_field}")

        if self.c_dict['COMPLEMENT_FLAG']:
            self.args.append("-complement")

        if self.c_dict['UNION_FLAG']:
            self.args.append("-union")

        if self.c_dict['INTERSECTION_FLAG']:
            self.args.append("-intersection")

        if self.c_dict['SYMDIFF_FLAG']:
            self.args.append("-symdiff")

        if self. c_dict['THRESH']:
            self.args.append(f"-thresh {self.c_dict['THRESH']}")

        print(f"HEIGHT: {self.c_dict['HEIGHT']} and MISSING: {util.MISSING_DATA_VALUE_INT}")
        if self.c_dict['HEIGHT'] != util.MISSING_DATA_VALUE_INT:
            self.args.append(f"-height {self.c_dict['HEIGHT']}")

        if self.c_dict['WIDTH'] != util.MISSING_DATA_VALUE_INT:
            self.args.append(f"-width {self.c_dict['WIDTH']}")

        if self.c_dict['SHAPENO'] != util.MISSING_DATA_VALUE_INT:
            self.args.append(f"-shapeno {self.c_dict['SHAPENO']}")

        if self.c_dict['VALUE'] != util.MISSING_DATA_VALUE_INT:
            self.args.append(f"-value {self.c_dict['VALUE']}")

        if self.c_dict['NAME']:
            self.args.append(f"-name {self.c_dict['NAME']}")

if __name__ == "__main__":
    util.run_stand_alone(__file__, "GenVxMask")
