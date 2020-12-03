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

import os
from datetime import datetime

from ..util import met_util as util
from ..util import time_util
from . import CompareGriddedWrapper
from ..util import do_string_sub

'''!@namespace SeriesAnalysisWrapper
@brief Wraps the SeriesAnalysis tool to compare a series of gridded files
@endcode
'''

class SeriesAnalysisWrapper(CompareGriddedWrapper):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "series_analysis"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_SERIES_ANALYSIS_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'SERIES_ANALYSIS_CONFIG_FILE', '')
        if not c_dict['CONFIG_FILE']:
            self.log_error("SERIES_ANALYSIS_CONFIG_FILE is required to run SeriesAnalysis wrapper")

        stat_list = util.getlist(self.config.getstr('config', 'SERIES_ANALYSIS_STAT_LIST', ''))
        # replace single quotes with double quotes
        c_dict['STAT_LIST'] = str(stat_list).replace("'", '"')

        c_dict['PAIRED'] = self.config.getbool('config', 'SERIES_ANALYSIS_IS_PAIRED', False)

        # get clock time from start of execution for input time dictionary
        clock_time_obj = datetime.strptime(self.config.getstr('config', 'CLOCK_TIME'),
                                                    '%Y%m%d%H%M%S')

        # get start run time and set INPUT_TIME_DICT
        c_dict['INPUT_TIME_DICT'] = {'now': clock_time_obj}
        start_time, _, _ = util.get_start_end_interval_times(self.config) or (None, None, None)
        if start_time:
            # set init or valid based on LOOP_BY
            use_init = util.is_loop_by_init(self.config)
            if use_init is None:
                self.isOK = False
            elif use_init:
                c_dict['INPUT_TIME_DICT']['init'] = start_time
            else:
                c_dict['INPUT_TIME_DICT']['valid'] = start_time
        else:
            self.log_error("Could not get [INIT/VALID] time information from configuration file")

        # get input dir, template, and datatype for FCST, OBS, and BOTH
        for data_type in ('FCST', 'OBS', 'BOTH'):
            c_dict[f'{data_type}_INPUT_DIR'] = \
              self.config.getdir(f'{data_type}_SERIES_ANALYSIS_INPUT_DIR', '')
            c_dict[f'{data_type}_INPUT_TEMPLATE'] = \
              self.config.getraw('filename_templates',
                                 f'{data_type}_SERIES_ANALYSIS_INPUT_TEMPLATE',
                                 '')

            c_dict[f'{data_type}_INPUT_DATATYPE'] = \
              self.config.getstr('config', f'{data_type}_SERIES_ANALYSIS_INPUT_DATATYPE', '')

            # initialize list path to None for each type
            c_dict[f'{data_type}_LIST_PATH'] = None

        # if BOTH is set, neither FCST or OBS can be set
        c_dict['USING_BOTH'] = False
        if c_dict['BOTH_INPUT_TEMPLATE']:
            if c_dict['FCST_INPUT_TEMPLATE'] or c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Cannot set FCST_SERIES_ANALYSIS_INPUT_TEMPLATE or "
                               "OBS_SERIES_ANALYSIS_INPUT_TEMPLATE "
                               "if BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE is set.")

            c_dict['USING_BOTH'] = True

            # set *_WINDOW_* variables for BOTH (used in CommandBuilder.find_data function)
            self.handle_window_variables(c_dict, 'series_analysis', dtypes=['BOTH'])

        # if BOTH is not set, both FCST or OBS must be set
        else:
            if not c_dict['FCST_INPUT_TEMPLATE'] or not c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Must either set BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE or both "
                               "FCST_SERIES_ANALYSIS_INPUT_TEMPLATE and "
                               "OBS_SERIES_ANALYSIS_INPUT_TEMPLATE to run "
                               "SeriesAnalysis wrapper.")

            # set *_WINDOW_* variables for FCST and OBS
            self.handle_window_variables(c_dict, 'series_analysis', dtypes=['FCST', 'OBS'])

        c_dict['OUTPUT_DIR'] = self.config.getdir('SERIES_ANALYSIS_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'SERIES_ANALYSIS_OUTPUT_TEMPLATE',
                                                       '')
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error("Must set SERIES_ANALYSIS_OUTPUT_TEMPLATE to run SeriesAnalysis wrapper")

        # get climatology config variables
        self.read_climo_wrapper_specific('SERIES_ANALYSIS', c_dict)

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'SERIES_ANALYSIS_REGRID_TO_GRID', '')

        # used to override the file type for fcst/obs if using python embedding for input
        c_dict['FCST_FILE_TYPE'] = ''
        c_dict['OBS_FILE_TYPE'] = ''

        return c_dict

    def clear(self):
        super().clear()
        for data_type in ('FCST', 'OBS', 'BOTH'):
            self.c_dict[f'{data_type}_LIST_PATH'] = None

    def set_environment_variables(self, fcst_field, obs_field, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        # set environment variables needed for MET application
        self.add_env_var("FCST_FILE_TYPE", self.c_dict['FCST_FILE_TYPE'])
        self.add_env_var("OBS_FILE_TYPE", self.c_dict['OBS_FILE_TYPE'])

        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        self.add_env_var("STAT_LIST", self.c_dict['STAT_LIST'])
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)

        # set climatology environment variables
        self.set_climo_env_vars()

        super().set_environment_variables(time_info)

    def get_command(self):
        cmd = self.app_path

        if self.c_dict['USING_BOTH']:
            cmd += f" -both {self.c_dict['BOTH_LIST_PATH']}"
        else:
            cmd += f" -fcst {self.c_dict['FCST_LIST_PATH']}"
            cmd += f" -obs {self.c_dict['OBS_LIST_PATH']}"

        # add output path
        cmd += f' -out {self.get_output_path()}'

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def run_all_times(self):
        """! Get start time, loop over forecast leads and run SeriesAnalysis
        """
        # get input time dictionary
        input_dict = self.c_dict['INPUT_TIME_DICT']

        # loop over forecast leads and process
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            # set current lead time config and environment variables
            time_info = time_util.ti_calculate(input_dict)

            self.logger.info("Processing forecast lead {}".format(time_info['lead_string']))

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            self.run_at_time(time_info)

    def run_at_time(self, time_info):
        """! Process runtime and try to build command to run SeriesAnalysis
             Args:
                @param time_info dictionary containing timing information
        """

        # parse var list for FCST and/or OBS fields
        var_list = util.parse_var_list(self.config,
                                       time_info,
                                       met_tool=self.app_name)

        # loop of var list and process for each
        for var_info in var_list:
            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string
                self.process_field_at_time(time_info, var_info)

    def process_field_at_time(self, time_info, var_info):

        # clear variables for next run
        self.clear()

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get input files
        if not self.find_input_files(time_info, var_info):
            return

        self.handle_climo(time_info)

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # get formatted field dictionary to pass into the MET config file
        fcst_field, obs_field = self.get_formatted_fields(var_info)

        # set environment variables if using config file
        self.set_environment_variables(fcst_field, obs_field, time_info)

        self.build()

    def find_input_files(self, time_info, var_info):
        if self.c_dict['USING_BOTH']:
            return self.get_files_and_create_list(time_info, var_info, 'BOTH')

        if not self.get_files_and_create_list(time_info, var_info, 'FCST'):
            return False

        if not self.get_files_and_create_list(time_info, var_info, 'OBS'):
            return False

        return True

    def get_files_and_create_list(self, time_info, var_info, data_type):
        found_files = self.find_data(time_info,
                                     var_info=var_info,
                                     data_type=data_type,
                                     mandatory=True,
                                     return_list=True,
                                     )

        if not found_files:
            return False

        file_ext = self.check_for_python_embedding(data_type, var_info)

        # if check_for_python_embedding returns None, an error occurred
        if not file_ext:
            return False

        list_file = time_info['valid_fmt'] + f'_SA_{data_type.lower()}_' + file_ext + '.txt'
        list_path = self.write_list_file(list_file, found_files)
        self.c_dict[f'{data_type}_LIST_PATH'] = list_path
        return True

    def set_command_line_arguments(self, time_info):
        # add input data format if set
        if self.c_dict['PAIRED']:
            self.args.append(" -paired")

        # add config file - passing through do_string_sub to get custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f" -config {config_file}")

    def get_formatted_fields(self, var_info):
        # get field info field a single field to pass to the MET config file
        fcst_field_list = self.get_field_info(v_level=var_info['fcst_level'],
                                              v_thresh=var_info['fcst_thresh'],
                                              v_name=var_info['fcst_name'],
                                              v_extra=var_info['fcst_extra'],
                                              d_type='FCST')

        obs_field_list = self.get_field_info(v_level=var_info['obs_level'],
                                             v_thresh=var_info['obs_thresh'],
                                             v_name=var_info['obs_name'],
                                             v_extra=var_info['obs_extra'],
                                             d_type='OBS')

        if fcst_field_list is None or obs_field_list is None:
            return

        fcst_fields = ','.join(fcst_field_list)
        obs_fields = ','.join(obs_field_list)

        return fcst_fields, obs_fields
