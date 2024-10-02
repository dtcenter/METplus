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

from ..util import getlistint
from ..util import do_string_sub
from . import ReformatPointWrapper


class PB2NCWrapper(ReformatPointWrapper):
    """!Wrapper to the MET tool pb2nc which converts prepbufr files
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

        @returns dictionary containing the settings from the configuration files
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getint('config',
                                                 'LOG_PB2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['OFFSETS'] = getlistint(self.config.getstr('config',
                                                          'PB2NC_OFFSETS',
                                                          '0'))

        c_dict['OBS_INPUT_DATATYPE'] = (
            self.config.getraw('config', 'PB2NC_INPUT_DATATYPE', '')
        )

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('PB2NCConfig_wrapped')

        self.add_met_config(name='message_type', data_type='list')

        self.add_met_config(name='station_id', data_type='list')

        self.add_met_config_window('obs_window')

        self.handle_mask(single_value=True)

        self.add_met_config(name='obs_bufr_var', data_type='list',
                            metplus_configs=['PB2NC_OBS_BUFR_VAR_LIST',
                                             'PB2NC_OBS_BUFR_VAR'],
                            extra_args={'allow_empty': True})

        self.handle_time_summary_dict()

        self.handle_file_window_variables(c_dict, data_types=['OBS'])

        c_dict['VALID_BEG'] = self.config.getraw('config', 'PB2NC_VALID_BEGIN')
        c_dict['VALID_END'] = self.config.getraw('config', 'PB2NC_VALID_END')

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        self.add_met_config(name='pb_report_type',
                            data_type='list',
                            metplus_configs=['PB2NC_PB_REPORT_TYPE'],
                            extra_args={'remove_quotes': True})

        # get level_range beg and end
        self.add_met_config_window('level_range')

        self.add_met_config(name='level_category', data_type='list',
                            metplus_configs=['PB2NC_LEVEL_CATEGORY'],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='quality_mark_thresh', data_type='int',
                            metplus_configs=['PB2NC_QUALITY_MARK_THRESH'])

        self.add_met_config(name='obs_bufr_map', data_type='list',
                            extra_args={'remove_quotes': True})

        return c_dict

    def set_command_line_arguments(self, time_info):
        # handle config file substitution
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(config_file)

        # if more than 2 input files are provided, add them with -pbfile
        if len(self.infiles) > 1:
            for infile in self.infiles[1:]:
                self.args.append(f"-pbfile {infile}")

            # reset infiles to only include first file
            self.infiles = [self.infiles[0]]

        for beg_end in ('VALID_BEG', 'VALID_END'):
            template = self.c_dict[beg_end]
            if not template:
                continue
            template = do_string_sub(template, **time_info)
            self.args.append(f"-{beg_end.lower()} {template}")
