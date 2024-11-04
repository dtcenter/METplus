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

from ..util import getlist
from ..util import do_string_sub, remove_quotes
from . import LoopTimesWrapper

'''!@namespace GenVxMaskWrapper
@brief Wraps the GenVxMask tool to reformat ascii format to NetCDF
@endcode
'''


class GenVxMaskWrapper(LoopTimesWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = "gen_vx_mask"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GEN_VX_MASK_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        # input and output files
        c_dict['INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      'GEN_VX_MASK_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] = self.config.getdir('GEN_VX_MASK_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('config',
                                                       'GEN_VX_MASK_OUTPUT_TEMPLATE')

        c_dict['MASK_INPUT_DIR'] = self.config.getdir('GEN_VX_MASK_INPUT_MASK_DIR',
                                                      '')
        c_dict['MASK_INPUT_TEMPLATES'] = getlist(
            self.config.getraw('config', 'GEN_VX_MASK_INPUT_MASK_TEMPLATE')
        )

        if not c_dict['MASK_INPUT_TEMPLATES']:
            self.log_error("Must set GEN_VX_MASK_INPUT_MASK_TEMPLATE to run GenVxMask wrapper")
            self.isOK = False

        # optional arguments
        c_dict['COMMAND_OPTIONS'] = getlist(
            self.config.getraw('config', 'GEN_VX_MASK_OPTIONS')
        )

        # if no options were specified, set to a list with an empty string
        if not c_dict['COMMAND_OPTIONS']:
            c_dict['COMMAND_OPTIONS'] = ['']

        # error if -type is not set (previously optional)
        if not any([item for item in c_dict['COMMAND_OPTIONS'] if '-type' in item]):
            self.log_error("Must specify -type in GEN_VX_MASK_OPTIONS")

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
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
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

        # add arguments
        cmd += ' ' + self.args

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def run_at_time_once(self, time_info):
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
        self.run_count += 1
        temp_file = ''
        for index, (mask_template, cmd_args) in enumerate(zip(self.c_dict['MASK_INPUT_TEMPLATES'],
                                                              self.c_dict['COMMAND_OPTIONS'])):

            # set mask input template and command line arguments
            self.c_dict['MASK_INPUT_TEMPLATE'] = mask_template
            self.args = do_string_sub(cmd_args, **time_info)

            if not self.find_input_files(time_info, temp_file):
                self.missing_input_count += 1
                return

            # break out of loop if this is the last iteration to
            # run final command that writes to the output file
            if index+1 == len(self.c_dict['MASK_INPUT_TEMPLATES']):
                break

            # if not the last iteration, write to temporary file
            temp_file = os.path.join(self.config.getdir('STAGING_DIR'),
                                     'gen_vx_mask',
                                     f'temp_{index}.nc')
            self.find_and_check_output_file(time_info,
                                            output_path_template=temp_file)

            # run GenVxMask
            self.build()

        # use final output path for last (or only) run
        if not self.find_and_check_output_file(time_info):
            return

        # run GenVxMask
        self.build()

    def find_input_files(self, time_info, temp_file):
        """!Handle setting of input file list.

        @param time_info time dictionary for current runtime
        @param temp_file path to temporary file used for previous run or
         empty string on first iteration
        @returns True if successfully found all inputs, False if not
        """

        # clear out input file list
        self.infiles.clear()

        # if temp file is not set, this is the first iteration, so read input file
        if not temp_file:
            input_path = self.find_data(time_info)

            # return if file was not found
            if not input_path:
                return None

        # if temp file is set, use that as input
        else:
            input_path = temp_file

        # find mask file, using MASK_INPUT_TEMPLATE
        mask_file = self.find_data(time_info, data_type='MASK')
        if not mask_file:
            return None

        # add input and mask file to input file list
        self.infiles.append(f'"{remove_quotes(input_path)}"')
        self.infiles.append(mask_file)

        return time_info
