"""
Program Name: madis2nc_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs madis2nc
History Log:  Initial version
Usage:
Parameters: None
Input Files: MADIS files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub
from . import RuntimeFreqWrapper

'''!@namespace MADIS2NCWrapper
@brief Wraps the madis2nc tool to reformat MADIS format to NetCDF
@endcode
'''


class MADIS2NCWrapper(RuntimeFreqWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_TIME_SUMMARY_DICT',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "madis2nc"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_MADIS2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # file I/O
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        self.get_input_templates(c_dict, {
            'OBS': {'prefix': 'MADIS2NC', 'required': True},
        })

        c_dict['OUTPUT_DIR'] = self.config.getdir('MADIS2NC_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'MADIS2NC_OUTPUT_TEMPLATE')
        )
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error('MADIS2NC_OUTPUT_TEMPLATE must be set')

        # config file settings
        c_dict['CONFIG_FILE'] = self.get_config_file('Madis2NcConfig_wrapped')
        self.handle_time_summary_dict()

        # command line settings
        c_dict['TYPE'] = self.config.getraw('config', 'MADIS2NC_TYPE')
        if not c_dict['TYPE']:
            self.log_error('Must set MADIS2NC_TYPE')

        c_dict['QC_DD'] = self.config.getraw('config', 'MADIS2NC_QC_DD')
        c_dict['LVL_DIM'] = self.config.getraw('config', 'MADIS2NC_LVL_DIM')
        c_dict['REC_BEG'] = self.config.getint('config', 'MADIS2NC_REC_BEG', '')
        c_dict['REC_END'] = self.config.getint('config', 'MADIS2NC_REC_END', '')
        c_dict['MASK_GRID'] = self.config.getraw('config', 'MADIS2NC_MASK_GRID')
        c_dict['MASK_POLY'] = self.config.getraw('config', 'MADIS2NC_MASK_POLY')
        c_dict['MASK_SID'] = self.config.getraw('config', 'MADIS2NC_MASK_SID')

        return c_dict

    def get_command(self):
        """!Build command to run madis2nc

        @returns str: madis2nc command
        """
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" {' '.join(self.infiles)} {self.get_output_path()}"
                f" {' '.join(self.args)}")

    def find_input_files(self, time_info):
        """!Get list of input files to pass to command. Sets self.infiles.

        @param time_info dictionary containing time information
        @returns bool: True if files were found, False otherwise
        """
        if not self.c_dict.get('ALL_FILES'):
            return False

        input_files = self.c_dict['ALL_FILES'][0].get('OBS', [])
        if not input_files:
            return False

        self.logger.debug(f"Adding input: {' and '.join(input_files)}")
        self.infiles.extend(input_files)
        return True

    def set_command_line_arguments(self, time_info):
        """!Read self.c_dict and set command line arguments in self.args.

        @param time_info dictionary containing time information
        """
        # set required command line arguments
        self.args.append(f"-type {self.c_dict['TYPE']}")

        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

        # set optional command line arguments if specified
        optional_args = ('qc_dd', 'lvl_dim', 'rec_beg', 'rec_end', 'mask_grid',
                         'mask_poly', 'mask_sid')
        for arg in optional_args:
            if self.c_dict[arg.upper()]:
                self.args.append(f"-{arg} {self.c_dict[arg.upper()]}")
