#!/usr/bin/env python

"""
Program Name: series_analysis_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs SeriesAnalysis
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import metplus_check_python_version

import os
import met_util as util
import time_util
from command_builder import CommandBuilder
from string_template_substitution import StringSub

'''!@namespace SeriesAnalysisWrapper
@brief Wraps the SeriesAnalysis tool to compare a series of gridded files
@endcode
'''


class SeriesAnalysisWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = "series_analysis"
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_SERIES_ANALYSIS_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'SERIES_ANALYSIS_CONFIG_FILE', '')
        if not c_dict['CONFIG_FILE']:
            self.log_error("SERIES_ANALYSIS_CONFIG_FILE is required to run SeriesAnalysis wrapper")
            self.isOK = False

        c_dict['PAIRED'] = self.config.getstr('config', 'SERIES_ANALYSIS_IS_PAIRED', False)

        # get clock time from start of execution for input time dictionary
        clock_time_obj = datetime.datetime.strptime(self.config.getstr('config', 'CLOCK_TIME'),
                                                    '%Y%m%d%H%M%S')
        c_dict['INPUT_TIME_DICT'] = {'now': clock_time_obj}

        # get start run time from either INIT_BEG or VALID_BEG based on LOOP_BY and set INPUT_TIME_DICT
        start_time, _, _ = util.get_start_end_interval_times(self.config) or (None, None, None)
        if not start_time:
            self.config.logger.error("Could not get [INIT/VALID] time information from configuration file")
            self.isOK = False
        else:
            if util.is_loop_by_init(self.config):
                c_dict['INPUT_TIME_DICT']['init'] = start_time
            else:
                c_dict['INPUT_TIME_DICT']['valid'] = start_time

        for data_type in ('FCST', 'OBS', 'BOTH'):
            c_dict[f'{data_type}_INPUT_DIR'] = self.config.getdir(f'{data_type}_SERIES_ANALYSIS_INPUT_DIR', '')
            c_dict[f'{data_type}_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                              f'{data_type}_SERIES_ANALYSIS_INPUT_TEMPLATE',
                                                              '')

        c_dict['USING_BOTH'] = False
        # if BOTH is set, neither FCST or OBS can be set
        if c_dict['BOTH_INPUT_TEMPLATE']:
            if c_dict['FCST_INPUT_TEMPLATE'] or c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Cannot set FCST_SERIES_ANALYSIS_INPUT_TEMPLATE or OBS_SERIES_ANALYSIS_INPUT_TEMPLATE "
                               "if BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE is set.")
                self.isOK = False

            c_dict['USING_BOTH'] = True
        # if BOTH is not set, at least one of FCST or OBS must be set
        else:
            if not c_dict['FCST_INPUT_TEMPLATE'] and not c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Must set FCST_SERIES_ANALYSIS_INPUT_TEMPLATE, OBS_SERIES_ANALYSIS_INPUT_TEMPLATE "
                               "or BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE to run SeriesAnalysis wrapper.")
                self.isOK = False

        c_dict['OUTPUT_DIR'] = self.config.getdir('SERIES_ANALYSIS_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'SERIES_ANALYSIS_OUTPUT_TEMPLATE',
                                                       '')
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error("Must set SERIES_ANALYSIS_OUTPUT_TEMPLATE to run SeriesAnalysis wrapper")
            self.isOK = False


        # used to override the file type for fcst/obs if using python embedding for input
        c_dict['FCST_FILE_TYPE'] = ''
        c_dict['OBS_FILE_TYPE'] = ''

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        # set environment variables needed for MET application
        self.add_env_var("FCST_FILE_TYPE", self.c_dict['FCST_FILE_TYPE'])
        self.add_env_var("OBS_FILE_TYPE", self.c_dict['OBS_FILE_TYPE'])
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

    def run_all_times(self):
        """! Get start time, loop over forecast leads and run SeriesAnalysis
        """
        # get input time dictionary
        input_dict = c_dict['INPUT_TIME_DICT']

        # loop over forecast leads and process
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            # set current lead time config and environment variables
            time_info = time_util.ti_calculate(input_dict)

            self.logger.info("Processing forecast lead {}".format(time_info['lead_string']))

            if util.skip_time(time_info, self.config):
                self.logger.debug('Skipping run time')
                continue

            self.run_at_time(time_info)

    def run_at_time(self, time_info):
        """! Process runtime and try to build command to run SeriesAnalysis
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
            self.log_error("Could not generate command")
            return

        self.build()

    def find_input_files(self, time_info):
        if self.c_dict['USING_BOTH']:
            #
            both_file_ext = self.check_for_python_embedding('BOTH', var_info)

            # if check_for_python_embedding returns None, an error occurred
            if not both_file_ext:
                return
        else:
            if self.c_dict['FCST_INPUT_TEMPLATE']:
                fcst_file_ext = self.check_for_python_embedding('FCST', var_info)

            if self.c_dict['FCST_INPUT_TEMPLATE']:
                obs_file_ext = self.check_for_python_embedding('OBS', var_info)

            # if check_for_python_embedding returns None, an error occurred
            if not fcst_file_ext or not obs_file_ext:
                return

        # if using python embedding input, don't check if file exists,
        # just substitute time info and add to input file list
        if self.c_dict['ASCII_FORMAT'] == 'python':
            filename = StringSub(self.logger,
                                 self.c_dict['OBS_INPUT_TEMPLATE'],
                                 **time_info).do_string_sub()
            self.infiles.append(filename)
            return self.infiles

        obs_path = self.find_obs(time_info, None)
        if obs_path is None:
            return None

        if isinstance(obs_path, list):
            self.infiles.extend(obs_path)
        else:
            self.infiles.append(obs_path)
        return self.infiles

    def set_command_line_arguments(self):
        # add input data format if set
        if self.c_dict['PAIRED']:
            self.args.append(" -paired")

        # add config file if set
        if self.c_dict['CONFIG_FILE']:
            self.args.append(" -config {}".format(self.c_dict['CONFIG_FILE']))

        # add mask grid if set
        if self.c_dict['MASK_GRID']:
            self.args.append(" -mask_grid {}".format(self.c_dict['MASK_GRID']))

        # add mask poly if set
        if self.c_dict['MASK_POLY']:
            self.args.append(" -mask_poly {}".format(self.c_dict['MASK_POLY']))

        # add mask SID if set
        if self.c_dict['MASK_SID']:
            self.args.append(" -mask_sid {}".format(self.c_dict['MASK_SID']))


if __name__ == "__main__":
    util.run_stand_alone(__file__, "ASCII2NC")
