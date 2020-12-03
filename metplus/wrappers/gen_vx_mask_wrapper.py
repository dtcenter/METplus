"""
Program Name: gen_vx_mask_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs gen_vx_mask
History Log:  Initial version
Usage:
Parameters: None
Input Files: Valid MET input files
Output Files: NetCDF files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace GenVxMaskWrapper
@brief Wraps the GenVxMask tool to reformat ascii format to NetCDF
@endcode
'''


class GenVxMaskWrapper(CommandBuilder):

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "gen_vx_mask"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GEN_VX_MASK_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        # input and output files
        c_dict['INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_DIR',
                                                 '')
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'GEN_VX_MASK_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] = self.config.getdir('GEN_VX_MASK_OUTPUT_DIR',
                                                  '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'GEN_VX_MASK_OUTPUT_TEMPLATE')

        c_dict['MASK_INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_MASK_DIR',
                                                      '')
        c_dict['MASK_INPUT_TEMPLATES'] = util.getlist(self.config.getraw('filename_templates',
                                                           'GEN_VX_MASK_INPUT_MASK_TEMPLATE'))

        if not c_dict['MASK_INPUT_TEMPLATES']:
            self.log_error("Must set GEN_VX_MASK_INPUT_MASK_TEMPLATE to run GenVxMask wrapper")
            self.isOK = False

        # optional arguments
        c_dict['COMMAND_OPTIONS'] = util.getlist(self.config.getraw('config',
                                                                    'GEN_VX_MASK_OPTIONS'))

        # if no options were specified, set to a list with an empty string
        if not c_dict['COMMAND_OPTIONS']:
            c_dict['COMMAND_OPTIONS'] = ['']

        # make sure the list of mask templates is the same size as the list of
        # command line options that correspond to each mask
        if len(c_dict['MASK_INPUT_TEMPLATES']) != len(c_dict['COMMAND_OPTIONS']):
            self.log_error("Number of items in GEN_VX_MASK_INPUT_MASK_TEMPLATE must "
                           "be equal to the number of items in GEN_VX_MASK_OPTIONS")

            self.isOK = False

        # handle window variables [GEN_VX_MASK_]FILE_WINDOW_[BEGIN/END]
        c_dict['FILE_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'GEN_VX_MASK_FILE_WINDOW_BEGIN',
                                 self.config.getseconds('config',
                                                        'FILE_WINDOW_BEGIN', 0))
        c_dict['FILE_WINDOW_END'] = \
          self.config.getseconds('config', 'GEN_VX_MASK_FILE_WINDOW_END',
                                 self.config.getseconds('config',
                                                        'FILE_WINDOW_END', 0))

        # use the same file windows for input and mask files
        c_dict['MASK_FILE_WINDOW_BEGIN'] = c_dict['FILE_WINDOW_BEGIN']
        c_dict['MASK_FILE_WINDOW_END'] = c_dict['FILE_WINDOW_END']

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

        # add input files
        for infile in self.infiles:
            cmd += ' ' + infile

        # add output path
        out_path = self.get_output_path()
        cmd += ' ' + out_path

        parent_dir = os.path.dirname(out_path)
        if not parent_dir:
            self.log_error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # add arguments
        cmd += ' ' + self.args

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
                @returns None
        """
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            self.clear()
            input_dict['lead'] = lead

            time_info = time_util.ti_calculate(input_dict)

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string

                self.run_at_time_all(time_info)

    def run_at_time_all(self, time_info):
        """!Loop over list of mask templates and call GenVxMask for each, adding the
            corresponding command line arguments for each call
            Args:
                @param time_info time dictionary for current runtime
                @returns None
        """
        # set environment variables
        # there is no config file, so using CommandBuilder implementation
        self.set_environment_variables(time_info)

        # loop over mask templates and command line args,
        temp_file = ''
        for index, (mask_template, cmd_args) in enumerate(zip(self.c_dict['MASK_INPUT_TEMPLATES'],
                                                              self.c_dict['COMMAND_OPTIONS'])):

            # set mask input template and command line arguments
            self.c_dict['MASK_INPUT_TEMPLATE'] = mask_template
            self.args = do_string_sub(cmd_args,
                                      **time_info)

            if not self.find_input_files(time_info, temp_file):
                return

            # break out of loop if this is the last iteration to
            # run final command that writes to the output file
            if index+1 == len(self.c_dict['MASK_INPUT_TEMPLATES']):
                break

            # if not the last iteration, write to temporary file
            temp_file = os.path.join(self.config.getdir('STAGING_DIR'),
                                     'gen_vx_mask',
                                     f'temp_{index}.nc')
            self.set_output_path(temp_file)

            # run GenVxMask
            self.build_and_run_command()

        # use final output path for last (or only) run
        if not self.find_and_check_output_file(time_info):
            return

        # run GenVxMask
        self.build_and_run_command()

    def find_input_files(self, time_info, temp_file):
        """!Handle setting of input file list.
            Args:
                @param time_info time dictionary for current runtime
                @param temp_file path to temporary file used for previous run or empty string on first iteration
                @returns True if successfully found all inputs, False if not
        """

        # clear out input file list
        self.infiles.clear()

        # if temp file is not set, this is the first iteration, so read input file
        if not temp_file:
            input_path = self.find_data(time_info)

            # return if file was not found
            if not input_path:
                return False

        # if temp file is set, use that as input
        else:
            input_path = temp_file

        # find mask file, using MASK_INPUT_TEMPLATE
        mask_file = self.find_data(time_info,
                                   data_type='MASK')
        if not mask_file:
            return False

        # add input and mask file to input file list
        self.infiles.append(input_path)
        self.infiles.append(mask_file)

        return True
