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

from ..util import getlistint, skip_time, get_lead_sequence
from ..util import ti_calculate
from ..util import do_string_sub
from . import LoopTimesWrapper


class PB2NCWrapper(LoopTimesWrapper):
    """! Wrapper to the MET tool pb2nc which converts prepbufr files
         to NetCDF for MET's point_stat tool can recognize.
    """
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

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
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'PB2NC_MESSAGE_TYPE',
        'PB2NC_STATION_ID',
        'OBS_WINDOW_BEGIN',
        'OBS_WINDOW_END',
        'PB2NC_GRID',
        'PB2NC_POLY',
        'OBS_BUFR_VAR_LIST',
        'TIME_SUMMARY_FLAG',
        'TIME_SUMMARY_BEG',
        'TIME_SUMMARY_END',
        'TIME_SUMMARY_VAR_NAMES',
        'TIME_SUMMARY_TYPES',
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

        self.add_met_config(name='message_type', data_type='list')

        self.add_met_config(name='station_id', data_type='list')

        self.add_met_config_window('obs_window')

        self.handle_mask(single_value=True)

        self.add_met_config(name='obs_bufr_var',
                            data_type='list',
                            metplus_configs=['PB2NC_OBS_BUFR_VAR_LIST',
                                             'PB2NC_OBS_BUFR_VAR'],
                            extra_args={'allow_empty': True})

        self.handle_time_summary_dict()

        self.handle_file_window_variables(c_dict, data_types=['OBS'])

        c_dict['VALID_BEGIN_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_BEGIN', '')

        c_dict['VALID_END_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_END', '')

        c_dict['ALLOW_MULTIPLE_FILES'] = True

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

        return c_dict

    def find_input_files(self, input_dict):
        """!Find prepbufr data to convert.

            @param input_dict dictionary containing some time information
            @returns time info if files are found, None otherwise
        """
        infiles, time_info = self.find_obs_offset(input_dict,
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

    def run_at_time_once(self, input_dict):
        """!Find files needed to run pb2nc and run if found"""
        # look for input files to process
        self.run_count += 1
        time_info = self.find_input_files(input_dict)

        # if no files were found, don't run pb2nc
        if time_info is None:
            self.missing_input_count += 1
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

        # build and run command
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
