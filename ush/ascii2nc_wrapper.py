#!/usr/bin/env python

"""
Program Name: ascii2nc_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs ascii2nc
History Log:  Initial version
Usage:
Parameters: None
Input Files: ascii files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os
import met_util as util
import string_template_substitution as sts
import time_util
from command_builder import CommandBuilder

'''!@namespace Ascii2NcWrapper
@brief Wraps the Ascii2Nc tool to reformat ascii format to NetCDF
@endcode
'''


class Ascii2NcWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super(Ascii2NcWrapper, self).__init__(config, logger)
        self.app_name = "ascii2nc"
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super(Ascii2NcWrapper, self).create_c_dict()
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'ASCII2NC_CONFIG_FILE', '')
        c_dict['ASCII_FORMAT'] = self.config.getstr('config', 'ASCII2NC_INPUT_FORMAT', '')
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('ASCII2NC_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'ASCII2NC_INPUT_TEMPLATE')

        return c_dict

    def get_command(self):
        cmd = self.app_path

        # don't run if no input or output files were found
        if not self.infiles:
            self.logger.error("No input files were found")
            return

        if self.outfile == "":
            self.logger.error("No output file specified")
            return

        # add input files
        for infile in self.infiles:
            cmd += f' {infile}'

        # add output path
        cmd += f' {self.get_output_path()}'

        # add input data format if set
        if self.c_dict['ASCII_FORMAT'] != '':
            cmd += ' -format ' + self.c_dict['ASCII_FORMAT']

        # add config file if set
        if self.c_dict['CONFIG_FILE'] != '':
            cmd += ' -config ' + self.c_dict['CONFIG_FILE']

        # add verbosity
        cmd += f'-v {self.verbose}'
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
            self.config.set('config', 'CURRENT_LEAD_TIME', lead)
            time_info = time_util.ti_calculate(input_dict)
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

        # get other configurations for command

        # set environment variables if using config file

        # build command and run
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        self.build()

    def find_input_files(self, time_info):
        obs_path = self.find_obs(time_info, None)
        if obs_path is None:
            return

        self.infiles.append(obs_path)
        return self.infiles
