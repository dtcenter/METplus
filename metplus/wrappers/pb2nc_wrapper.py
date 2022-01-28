"""
Program Name: PB2NC_Wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET tool PB2NC
History Log:  Initial version
Usage: pb2nc_wrapper.py
Parameters: None
Input Files: prepBUFR data files
Output Files: netCDF files
Condition codes: 0 for success, 1 for failure
"""

import os
import re

from ..util import getlistint
from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CommandBuilder

class PB2NCWrapper(CommandBuilder):
    """! Wrapper to the MET tool pb2nc which converts prepbufr files
         to NetCDF for MET's point_stat tool can recognize.
    """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_STATION_ID',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_OBS_BUFR_VAR',
        'METPLUS_TIME_SUMMARY_DICT',
        'METPLUS_PB_REPORT_TYPE',
        'METPLUS_LEVEL_RANGE_DICT',
        'METPLUS_LEVEL_CATEGORY',
        'METPLUS_QUALITY_MARK_THRESH',
        'METPLUS_OBS_BUFR_MAP',
        'METPLUS_OBS_PREPBUFR_MAP',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'pb2nc'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """! Create a data structure (dictionary) that contains all the
        values set in the configuration files

             Args:

             Returns:
                c_dict  - a dictionary containing the settings in the
                configuration files
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getint('config',
                                                 'LOG_PB2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['OFFSETS'] = getlistint(self.config.getstr('config',
                                                          'PB2NC_OFFSETS',
                                                          '0'))

        # Directories
        # these are optional because users can specify full file path
        # in template instead
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('PB2NC_INPUT_DIR', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('PB2NC_OUTPUT_DIR', '')

        # filename templates, exit if not set
        c_dict['OBS_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'PB2NC_INPUT_TEMPLATE')
        )
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('Must set PB2NC_INPUT_TEMPLATE in config file')

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'PB2NC_OUTPUT_TEMPLATE')
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error('Must set PB2NC_OUTPUT_TEMPLATE in config file')

        c_dict['OBS_INPUT_DATATYPE'] = (
            self.config.getstr('config',
                               'PB2NC_INPUT_DATATYPE', '')
        )

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('PB2NCConfig_wrapped')

        self.add_met_config(name='message_type',
                            data_type='list')

        self.add_met_config(name='station_id',
                            data_type='list')

        self.add_met_config_window('obs_window')
        self.handle_obs_window_legacy(c_dict)

        self.handle_mask(single_value=True)

        self.add_met_config(name='obs_bufr_var',
                            data_type='list',
                            metplus_configs=['PB2NC_OBS_BUFR_VAR_LIST',
                                             'PB2NC_OBS_BUFR_VAR'],
                            extra_args={'allow_empty': True})

        #self.handle_time_summary_legacy(c_dict)
        self.handle_time_summary_dict()

        # handle legacy time summary variables
        self.add_met_config(name='',
                            data_type='bool',
                            env_var_name='TIME_SUMMARY_FLAG',
                            metplus_configs=['PB2NC_TIME_SUMMARY_FLAG'])

        self.add_met_config(name='',
                            data_type='string',
                            env_var_name='TIME_SUMMARY_BEG',
                            metplus_configs=['PB2NC_TIME_SUMMARY_BEG'])

        self.add_met_config(name='',
                            data_type='string',
                            env_var_name='TIME_SUMMARY_END',
                            metplus_configs=['PB2NC_TIME_SUMMARY_END'])

        self.add_met_config(name='',
                            data_type='list',
                            env_var_name='TIME_SUMMARY_VAR_NAMES',
                            metplus_configs=['PB2NC_TIME_SUMMARY_OBS_VAR',
                                             'PB2NC_TIME_SUMMARY_VAR_NAMES'],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='',
                            data_type='list',
                            env_var_name='TIME_SUMMARY_TYPES',
                            metplus_configs=['PB2NC_TIME_SUMMARY_TYPE',
                                             'PB2NC_TIME_SUMMARY_TYPES'],
                            extra_args={'allow_empty': True})

        self.handle_file_window_variables(c_dict, dtypes=['OBS'])

        c_dict['VALID_BEGIN_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_BEGIN', '')

        c_dict['VALID_END_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_END', '')

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # set c_dict values to handle old method of setting env vars
        message_type = self.get_env_var_value('METPLUS_MESSAGE_TYPE')
        if not message_type:
            message_type = '[]'
        c_dict['MESSAGE_TYPE'] = message_type

        station_id = self.get_env_var_value('METPLUS_STATION_ID')
        if not station_id:
            station_id = '[]'
        c_dict['STATION_ID'] = station_id

        c_dict['GRID'] = self.config.getstr('config', 'PB2NC_GRID', '')
        c_dict['POLY'] = self.config.getstr('config', 'PB2NC_POLY', '')

        c_dict['BUFR_VAR_LIST'] = (
            self.get_env_var_value('METPLUS_OBS_BUFR_VAR')
        )

        self.add_met_config(name='pb_report_type',
                            data_type='list',
                            metplus_configs=['PB2NC_PB_REPORT_TYPE'],
                            extra_args={'remove_quotes': True})

        # get level_range beg and end
        self.add_met_config_window('level_range')

        self.add_met_config(name='level_category',
                            data_type='list',
                            metplus_configs=['PB2NC_LEVEL_CATEGORY'],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='quality_mark_thresh',
                            data_type='int',
                            metplus_configs=['PB2NC_QUALITY_MARK_THRESH'])

        self.add_met_config(name='obs_bufr_map',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='obs_prepbufr_map',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
             Reformat as needed. Print list of variables that were set and
             their values.

            @param time_info dictionary containing timing info from current run
        """
        # set old method of setting env vars needed for MET config file
        self.add_env_var("PB2NC_MESSAGE_TYPE", self.c_dict.get('MESSAGE_TYPE', ''))
        self.add_env_var("PB2NC_STATION_ID", self.c_dict.get('STATION_ID', ''))
        self.add_env_var("OBS_WINDOW_BEGIN",
                         str(self.c_dict.get('OBS_WINDOW_BEGIN', '')))
        self.add_env_var("OBS_WINDOW_END",
                         str(self.c_dict.get('OBS_WINDOW_END', '')))
        self.add_env_var("PB2NC_GRID", self.c_dict.get('GRID', ''))
        self.add_env_var("PB2NC_POLY", self.c_dict.get('POLY', ''))

        self.add_env_var("OBS_BUFR_VAR_LIST", self.c_dict.get('BUFR_VAR_LIST',
                                                              ''))

        for item in ['FLAG', 'BEG', 'END', 'VAR_NAMES', 'TYPES']:
            ts_item = f'TIME_SUMMARY_{item}'
            self.add_env_var(f'{ts_item}',
                             self.env_var_dict.get(f'METPLUS_{ts_item}', ''))

        super().set_environment_variables(time_info)

    def find_input_files(self, input_dict):
        """!Find prepbufr data to convert.

            @param input_dict dictionary containing some time information
            @returns time info if files are found, None otherwise
        """

        infiles, time_info = self.find_obs_offset(input_dict,
                                                  None,
                                                  mandatory=True,
                                                  return_list=True)

        # if file is found, return timing info dict so
        # output template can use offset value
        if infiles is None:
            return None

        self.logger.debug(f"Adding input: {' and '.join(infiles)}")
        self.infiles.extend(infiles)
        return time_info

    def set_valid_window_variables(self, time_info):
        begin_template = self.c_dict['VALID_BEGIN_TEMPLATE']
        end_template = self.c_dict['VALID_END_TEMPLATE']

        if begin_template:
            self.c_dict['VALID_WINDOW_BEGIN'] = \
                do_string_sub(begin_template,
                              **time_info)

        if end_template:
            self.c_dict['VALID_WINDOW_END'] = \
                do_string_sub(end_template,
                              **time_info)


    def run_at_time(self, input_dict):
        """! Loop over each forecast lead and build pb2nc command """
         # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(
                        f"Processing custom string: {custom_string}"
                    )

                input_dict['custom'] = custom_string

                # Run for given init/valid time and forecast lead combination
                self.run_at_time_once(input_dict)


    def run_at_time_once(self, input_dict):
        """!Find files needed to run pb2nc and run if found"""
        # clear out information set from previous run
        self.clear()

        # look for input files to process
        time_info = self.find_input_files(input_dict)

        # if no files were found, don't run pb2nc
        if time_info is None:
            return

        if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
            self.logger.debug('Skipping run time')
            return

        # look for output file path and skip running pb2nc if necessary
        if not self.find_and_check_output_file(time_info):
            return

        # set environment variables to be passed to MET config file
        self.set_environment_variables(time_info)

        self.set_valid_window_variables(time_info)

        # handle config file substitution
        self.c_dict['CONFIG_FILE'] = do_string_sub(self.c_dict['CONFIG_FILE'],
                                                   **time_info)

        # build command and run if successful
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return
        self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        for arg in self.args:
            cmd += f' {arg}'

        # if multiple input files, add first now, then add rest with
        # -pbfile argument
        if not self.infiles:
            self.log_error("No input files found")
            return None

        cmd += f" {self.infiles[0]}"

        out_path = self.get_output_path()
        cmd += f" {out_path}"

        cmd += f" {self.c_dict['CONFIG_FILE']}"

        if len(self.infiles) > 1:
            for infile in self.infiles[1:]:
                cmd += f" -pbfile {infile}"

        if self.c_dict.get('VALID_WINDOW_BEGIN'):
            cmd += f" -valid_beg {self.c_dict['VALID_WINDOW_BEGIN']}"

        if self.c_dict.get('VALID_WINDOW_END'):
            cmd += f" -valid_end {self.c_dict['VALID_WINDOW_END']}"

        return cmd
