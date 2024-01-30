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
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

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

        c_dict['ASCII_FORMAT'] = self.config.getstr('config',
                                                    'ASCII2NC_INPUT_FORMAT',
                                                    '')
        c_dict['MASK_GRID'] = self.config.getstr('config',
                                                 'ASCII2NC_MASK_GRID',
                                                 '')
        c_dict['MASK_POLY'] = self.config.getstr('config',
                                                 'ASCII2NC_MASK_POLY',
                                                 '')
        c_dict['MASK_SID'] = self.config.getstr('config',
                                                'ASCII2NC_MASK_SID',
                                                '')
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('ASCII2NC_INPUT_DIR',
                                                     '')
        c_dict['OBS_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'ASCII2NC_INPUT_TEMPLATE')
        )
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("ASCII2NC_INPUT_TEMPLATE required to run")

        c_dict['OUTPUT_DIR'] = self.config.getdir('ASCII2NC_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'ASCII2NC_OUTPUT_TEMPLATE')
        )

        # MET config variables
        self.handle_time_summary_dict()

        # handle file window variables
        for edge in ['BEGIN', 'END']:
            file_window = (
                self.config.getseconds('config',
                                       f'ASCII2NC_FILE_WINDOW_{edge}',
                                       '')
            )
            if file_window == '':
                file_window = (
                    self.config.getseconds('config',
                                           f'OBS_FILE_WINDOW_{edge}',
                                           0)
                )

            c_dict[f'OBS_FILE_WINDOW_{edge}'] = file_window
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

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

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def find_input_files(self, time_info):
        # if using python embedding input, don't check if file exists,
        # just substitute time info and add to input file list
        if self.c_dict['ASCII_FORMAT'] == 'python':
            filename = do_string_sub(self.c_dict['OBS_INPUT_TEMPLATE'],
                                     **time_info)
            self.infiles.append(filename)
            return True

        # get list of files even if only one is found (return_list=True)
        obs_path = self.find_obs(time_info, return_list=True)
        if obs_path is None:
            return False

        self.infiles.extend(obs_path)
        return True

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
