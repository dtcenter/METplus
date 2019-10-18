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
import time_util
from command_builder import CommandBuilder

'''!@namespace ASCII2NCWrapper
@brief Wraps the ASCII2NC tool to reformat ascii format to NetCDF
@endcode
'''


class ASCII2NCWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super(ASCII2NCWrapper, self).__init__(config, logger)
        self.app_name = "ascii2nc"
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super(ASCII2NCWrapper, self).create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_ASCII2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'ASCII2NC_CONFIG_FILE', '')
        c_dict['ASCII_FORMAT'] = self.config.getstr('config', 'ASCII2NC_INPUT_FORMAT', '')
        c_dict['MASK_GRID'] = self.config.getstr('config', 'ASCII2NC_MASK_GRID', '')
        c_dict['MASK_POLY'] = self.config.getstr('config', 'ASCII2NC_MASK_POLY', '')
        c_dict['MASK_SID'] = self.config.getstr('config', 'ASCII2NC_MASK_SID', '')
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('ASCII2NC_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                          'ASCII2NC_INPUT_TEMPLATE')
        c_dict['OUTPUT_DIR'] = self.config.getdir('ASCII2NC_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'ASCII2NC_OUTPUT_TEMPLATE')
        c_dict['TIME_SUMMARY_FLAG'] = 'TRUE' if self.config.getbool('config',
                                                    'ASCII2NC_TIME_SUMMARY_FLAG', False) else 'FALSE'

        c_dict['TIME_SUMMARY_RAW_DATA'] = 'TRUE' if self.config.getbool('config',
                                                        'ASCII2NC_TIME_SUMMARY_RAW_DATA', False) else 'FALSE'
        c_dict['TIME_SUMMARY_BEG'] = self.config.getstr('config',
                                                        'ASCII2NC_TIME_SUMMARY_BEG')
        # add quotes if not already added
        if c_dict['TIME_SUMMARY_BEG'][0] != '"' and c_dict['TIME_SUMMARY_BEG'][-1] != '"':
            c_dict['TIME_SUMMARY_BEG'] = f"\"{c_dict['TIME_SUMMARY_BEG']}\""
        c_dict['TIME_SUMMARY_END'] = self.config.getstr('config',
                                                        'ASCII2NC_TIME_SUMMARY_END')
        if c_dict['TIME_SUMMARY_END'][0] != '"' and c_dict['TIME_SUMMARY_END'][-1] != '"':
            c_dict['TIME_SUMMARY_END'] = f"\"{c_dict['TIME_SUMMARY_END']}\""

        c_dict['TIME_SUMMARY_STEP'] = self.config.getstr('config',
                                                         'ASCII2NC_TIME_SUMMARY_STEP')
        c_dict['TIME_SUMMARY_WIDTH'] = self.config.getstr('config',
                                                          'ASCII2NC_TIME_SUMMARY_WIDTH')
        c_dict['TIME_SUMMARY_GRIB_CODES'] = ','.join(util.getlist(
            self.config.getstr('config', 'ASCII2NC_TIME_SUMMARY_GRIB_CODES')))

        c_dict['TIME_SUMMARY_VAR_NAMES'] = '"' + '","'.join(util.getlist(
            self.config.getstr('config', 'ASCII2NC_TIME_SUMMARY_VAR_NAMES'))) + '"'
        c_dict['TIME_SUMMARY_TYPES'] = '"' + '","'.join(util.getlist(
            self.config.getstr('config', 'ASCII2NC_TIME_SUMMARY_TYPES'))) + '"'
        c_dict['TIME_SUMMARY_VALID_FREQ'] = self.config.getstr('config',
                                                               'ASCII2NC_TIME_SUMMARY_VALID_FREQ')
        c_dict['TIME_SUMMARY_VALID_THRESH'] = self.config.getstr('config',
                                                                 'ASCII2NC_TIME_SUMMARY_VALID_THRESH')

        # handle window variables [ASCII2NC_][FILE_]_WINDOW_[BEGIN/END]
        c_dict['OBS_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'ASCII2NC_WINDOW_BEGIN',
                                 self.config.getseconds('config',
                                                        'OBS_WINDOW_BEGIN', 0))
        c_dict['OBS_WINDOW_END'] = \
          self.config.getseconds('config', 'ASCII_WINDOW_END',
                                 self.config.getseconds('config',
                                                        'OBS_WINDOW_END', 0))

        c_dict['OBS_FILE_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'ASCII2NC_FILE_WINDOW_BEGIN',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_BEGIN', 0))
        c_dict['OBS_FILE_WINDOW_END'] = \
          self.config.getseconds('config', 'ASCII2NC_FILE_WINDOW_END',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_END', 0))
        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        # list of fields to print to log
        print_list = ["TIME_SUMMARY_FLAG", "TIME_SUMMARY_RAW_DATA",
                      "TIME_SUMMARY_BEG", "TIME_SUMMARY_END",
                      "TIME_SUMMARY_STEP", "TIME_SUMMARY_WIDTH",
                      "TIME_SUMMARY_GRIB_CODES", "TIME_SUMMARY_VAR_NAMES",
                      "TIME_SUMMARY_TYPES", "TIME_SUMMARY_VALID_FREQ",
                      "TIME_SUMMARY_VALID_THRESH",
                      ]

        # set environment variables needed for MET application
        self.add_env_var('TIME_SUMMARY_FLAG',
                         self.c_dict['TIME_SUMMARY_FLAG'])
        self.add_env_var('TIME_SUMMARY_RAW_DATA',
                         self.c_dict['TIME_SUMMARY_RAW_DATA'])
        self.add_env_var('TIME_SUMMARY_BEG',
                         self.c_dict['TIME_SUMMARY_BEG'])
        self.add_env_var('TIME_SUMMARY_END',
                         self.c_dict['TIME_SUMMARY_END'])
        self.add_env_var('TIME_SUMMARY_STEP',
                         self.c_dict['TIME_SUMMARY_STEP'])
        self.add_env_var('TIME_SUMMARY_WIDTH',
                         self.c_dict['TIME_SUMMARY_WIDTH'])
        self.add_env_var('TIME_SUMMARY_GRIB_CODES',
                         self.c_dict['TIME_SUMMARY_GRIB_CODES'])
        self.add_env_var('TIME_SUMMARY_VAR_NAMES',
                         self.c_dict['TIME_SUMMARY_VAR_NAMES'])
        self.add_env_var('TIME_SUMMARY_TYPES',
                         self.c_dict['TIME_SUMMARY_TYPES'])
        self.add_env_var('TIME_SUMMARY_VALID_FREQ',
                         self.c_dict['TIME_SUMMARY_VALID_FREQ'])
        self.add_env_var('TIME_SUMMARY_VALID_THRESH',
                         self.c_dict['TIME_SUMMARY_VALID_THRESH'])

        # set user environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

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
        out_path = self.get_output_path()
        cmd += f' {out_path}'

        parent_dir = os.path.dirname(out_path)
        if parent_dir == '':
            self.logger.error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
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
        self.set_command_line_arguments()
        # set environment variables if using config file
        self.set_environment_variables(time_info)

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

        if isinstance(obs_path, list):
            self.infiles.extend(obs_path)
        else:
            self.infiles.append(obs_path)
        return self.infiles

    def set_command_line_arguments(self):
        # add input data format if set
        if self.c_dict['ASCII_FORMAT']:
            self.args.append(f" -format {self.c_dict['ASCII_FORMAT']}")

        # add config file if set
        if self.c_dict['CONFIG_FILE']:
            self.args.append(f" -config {self.c_dict['CONFIG_FILE']}")

        # add mask grid if set
        if self.c_dict['MASK_GRID']:
            self.args.append(f" -mask_grid {self.c_dict['MASK_GRID']}")

        # add mask poly if set
        if self.c_dict['MASK_POLY']:
            self.args.append(f" -mask_poly {self.c_dict['MASK_POLY']}")

        # add mask SID if set
        if self.c_dict['MASK_SID']:
            self.args.append(f" -mask_sid {self.c_dict['MASK_SID']}")
