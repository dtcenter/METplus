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

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace ASCII2NCWrapper
@brief Wraps the ASCII2NC tool to reformat ascii format to NetCDF
@endcode
'''


class ASCII2NCWrapper(CommandBuilder):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "ascii2nc"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_ASCII2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'ASCII2NC_CONFIG_FILE', '')
        c_dict['ASCII_FORMAT'] = self.config.getstr('config', 'ASCII2NC_INPUT_FORMAT', '')
        c_dict['MASK_GRID'] = self.config.getstr('config', 'ASCII2NC_MASK_GRID', '')
        c_dict['MASK_POLY'] = self.config.getstr('config', 'ASCII2NC_MASK_POLY', '')
        c_dict['MASK_SID'] = self.config.getstr('config', 'ASCII2NC_MASK_SID', '')
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('ASCII2NC_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                          'ASCII2NC_INPUT_TEMPLATE')
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("ASCII2NC_INPUT_TEMPLATE required to run")
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
            c_dict['TIME_SUMMARY_BEG'] = "\"{}\"".format(c_dict['TIME_SUMMARY_BEG'])
        c_dict['TIME_SUMMARY_END'] = self.config.getstr('config',
                                                        'ASCII2NC_TIME_SUMMARY_END')
        if c_dict['TIME_SUMMARY_END'][0] != '"' and c_dict['TIME_SUMMARY_END'][-1] != '"':
            c_dict['TIME_SUMMARY_END'] = "\"{}\"".format(c_dict['TIME_SUMMARY_END'])

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
        super().set_environment_variables(time_info)

    def get_command(self):
        cmd = self.app_path

        # don't run if no input or output files were found
        if not self.infiles:
            self.log_error("No input files were found")
            return

        if self.outfile == "":
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
        cmd += ''.join(self.args)

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

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

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
        # if using python embedding input, don't check if file exists,
        # just substitute time info and add to input file list
        if self.c_dict['ASCII_FORMAT'] == 'python':
            filename = do_string_sub(self.c_dict['OBS_INPUT_TEMPLATE'],
                                     **time_info)
            self.infiles.append(filename)
            return self.infiles

        # get list of files even if only one is found (return_list=True)
        obs_path = self.find_obs(time_info, var_info=None, return_list=True)
        if obs_path is None:
            return None

        self.infiles.extend(obs_path)
        return self.infiles

    def set_command_line_arguments(self, time_info):
        # add input data format if set
        if self.c_dict['ASCII_FORMAT']:
            self.args.append(" -format {}".format(self.c_dict['ASCII_FORMAT']))

        # add config file - passing through do_string_sub to get custom string if set
        if self.c_dict['CONFIG_FILE']:
            config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)
            self.args.append(f" -config {config_file}")

        # add mask grid if set
        if self.c_dict['MASK_GRID']:
            self.args.append(" -mask_grid {}".format(self.c_dict['MASK_GRID']))

        # add mask poly if set
        if self.c_dict['MASK_POLY']:
            self.args.append(" -mask_poly {}".format(self.c_dict['MASK_POLY']))

        # add mask SID if set
        if self.c_dict['MASK_SID']:
            self.args.append(" -mask_sid {}".format(self.c_dict['MASK_SID']))
