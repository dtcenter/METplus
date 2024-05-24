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

from ..util import time_util
from . import LoopTimesWrapper
from ..util import do_string_sub, skip_time, get_lead_sequence

'''!@namespace ASCII2NCWrapper
@brief Wraps the ASCII2NC tool to reformat ascii format to NetCDF
@endcode
'''


class ASCII2NCWrapper(LoopTimesWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_TIME_SUMMARY_DICT',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'TIME_SUMMARY_FLAG',
        'TIME_SUMMARY_RAW_DATA',
        'TIME_SUMMARY_BEG',
        'TIME_SUMMARY_END',
        'TIME_SUMMARY_STEP',
        'TIME_SUMMARY_WIDTH',
        'TIME_SUMMARY_GRIB_CODES',
        'TIME_SUMMARY_VAR_NAMES',
        'TIME_SUMMARY_TYPES',
        'TIME_SUMMARY_VALID_FREQ',
        'TIME_SUMMARY_VALID_THRESH',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "ascii2nc"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_ASCII2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # ASCII2NC config file is optional, so
        # don't provide wrapped config file name as default value
        c_dict['CONFIG_FILE'] = self.get_config_file()

        c_dict['FORMAT'] = self.config.getraw('config', 'ASCII2NC_INPUT_FORMAT')
        if c_dict['FORMAT'] == 'python':
            c_dict['OBS_INPUT_DATATYPE'] = 'PYTHON'
        c_dict['MASK_GRID'] = self.config.getraw('config', 'ASCII2NC_MASK_GRID')
        c_dict['MASK_POLY'] = self.config.getraw('config', 'ASCII2NC_MASK_POLY')
        c_dict['MASK_SID'] = self.config.getraw('config', 'ASCII2NC_MASK_SID')
        c_dict['VALID_BEG'] = self.config.getraw('config', 'ASCII2NC_VALID_BEG')
        c_dict['VALID_END'] = self.config.getraw('config', 'ASCII2NC_VALID_END')

        self.get_input_templates(c_dict, {
            'OBS': {'prefix': 'ASCII2NC', 'required': True},
        })

        c_dict['OUTPUT_DIR'] = self.config.getdir('ASCII2NC_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'ASCII2NC_OUTPUT_TEMPLATE')
        )

        # MET config variables
        self.handle_time_summary_dict()
        # handle file window variables
        self.handle_file_window_variables(c_dict, data_types=['OBS'])

        return c_dict

    def get_command(self):
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" {' '.join(self.infiles)} {self.get_output_path()}"
                f" {' '.join(self.args)}".rstrip())

    def find_input_files(self, time_info):
        if not self.c_dict.get('ALL_FILES'):
            return False

        input_files = self.c_dict['ALL_FILES'][0].get('OBS', [])
        if not input_files:
            return False

        self.logger.debug(f"Adding input: {' and '.join(input_files)}")
        self.infiles.extend(input_files)

        return True

    def set_command_line_arguments(self, time_info):
        # add all arguments if set
        for arg in ('FORMAT', 'CONFIG_FILE', 'VALID_BEG', 'VALID_END',
                    'MASK_GRID', 'MASK_POLY', 'MASK_SID'):
            if self.c_dict[arg]:
                val = do_string_sub(self.c_dict[arg], **time_info)
                arg_name = 'config' if arg == 'CONFIG_FILE' else arg.lower()
                self.args.append(f"-{arg_name} {val}")
