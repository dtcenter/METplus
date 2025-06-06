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

from ..util import do_string_sub, MISSING_DATA_VALUE
from . import ReformatPointWrapper

'''!@namespace MADIS2NCWrapper
@brief Wraps the madis2nc tool to reformat MADIS format to NetCDF
@endcode
'''


class MADIS2NCWrapper(ReformatPointWrapper):

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

        # config file settings
        c_dict['CONFIG_FILE'] = self.get_config_file('Madis2NcConfig_wrapped')
        self.handle_time_summary_dict()

        # command line settings
        c_dict['TYPE'] = self.config.getraw('config', 'MADIS2NC_TYPE')
        if not c_dict['TYPE']:
            self.log_error('Must set MADIS2NC_TYPE')

        c_dict['QC_DD'] = self.config.getraw('config', 'MADIS2NC_QC_DD')
        c_dict['LVL_DIM'] = self.config.getraw('config', 'MADIS2NC_LVL_DIM')
        c_dict['REC_BEG'] = self.config.getint('config', 'MADIS2NC_REC_BEG')
        if c_dict['REC_BEG'] == MISSING_DATA_VALUE:
            c_dict['REC_BEG'] = ''
        c_dict['REC_END'] = self.config.getint('config', 'MADIS2NC_REC_END')
        if c_dict['REC_END'] == MISSING_DATA_VALUE:
            c_dict['REC_END'] = ''
        c_dict['MASK_GRID'] = self.config.getraw('config', 'MADIS2NC_MASK_GRID')
        c_dict['MASK_POLY'] = self.config.getraw('config', 'MADIS2NC_MASK_POLY')
        c_dict['MASK_SID'] = self.config.getraw('config', 'MADIS2NC_MASK_SID')

        return c_dict

    def set_command_line_arguments(self, time_info):
        """!Read self.c_dict and set command line arguments in self.args.

        @param time_info dictionary containing time information
        """
        # set required command line arguments
        val = do_string_sub(self.c_dict['TYPE'], **time_info)
        self.args.append(f"-type {val}")

        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

        # set optional command line arguments if specified
        optional_args = ('qc_dd', 'lvl_dim', 'rec_beg', 'rec_end', 'mask_grid',
                         'mask_poly', 'mask_sid')
        for arg in optional_args:
            if self.c_dict[arg.upper()]:
                val = self.c_dict[arg.upper()]
                if isinstance(val, str):
                    val = do_string_sub(val, **time_info)
                self.args.append(f"-{arg} {val}")
