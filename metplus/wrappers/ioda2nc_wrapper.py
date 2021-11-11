"""
Program Name: ioda2nc_wrapper.py
Contact(s): George McCabe
Abstract: Builds commands to run ioda2nc
"""

import os

from ..util import do_string_sub
from . import LoopTimesWrapper

'''!@namespace IODA2NCWrapper
@brief Wraps the IODA2NC tool to reformat IODA NetCDF data to MET NetCDF
@endcode
'''


class IODA2NCWrapper(LoopTimesWrapper):

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_MESSAGE_TYPE_GROUP_MAP',
        'METPLUS_MESSAGE_TYPE_MAP',
        'METPLUS_STATION_ID',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_ELEVATION_RANGE_DICT',
        'METPLUS_LEVEL_RANGE_DICT',
        'METPLUS_OBS_VAR',
        'METPLUS_OBS_NAME_MAP',
        'METPLUS_METADATA_MAP',
        'METPLUS_MISSING_THRESH',
        'METPLUS_QUALITY_MARK_THRESH',
        'METPLUS_TIME_SUMMARY_DICT',
    ]

    def __init__(self, config, instance=None, config_overrides=None):
        self.app_name = "ioda2nc"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # file I/O
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('IODA2NC_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = (
            self.config.getraw('config', 'IODA2NC_INPUT_TEMPLATE')
        )
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("IODA2NC_INPUT_TEMPLATE required to run")

        # handle input file window variables
        self.handle_file_window_variables(c_dict, dtypes=['OBS'])

        c_dict['OUTPUT_DIR'] = self.config.getdir('IODA2NC_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'IODA2NC_OUTPUT_TEMPLATE')
        )

        # optional command line arguments
        c_dict['VALID_BEG'] = self.config.getraw('config', 'IODA2NC_VALID_BEG')
        c_dict['VALID_END'] = self.config.getraw('config', 'IODA2NC_VALID_END')
        c_dict['NMSG'] = self.config.getint('config', 'IODA2NC_NMSG')

        # MET config variables
        c_dict['CONFIG_FILE'] = self.get_config_file('IODA2NCConfig_wrapped')

        self.add_met_config(name='message_type', data_type='list')
        self.add_met_config(name='message_type_map', data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='message_type_group_map', data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='station_id', data_type='list')
        self.handle_met_config_window('obs_window')
        self.handle_mask(single_value=True)
        self.handle_met_config_window('elevation_range')
        self.handle_met_config_window('level_range')
        self.add_met_config(name='obs_var', data_type='list')
        self.add_met_config(name='obs_name_map', data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='metadata_map', data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='missing_thresh', data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='quality_mark_thresh', data_type='float')
        self.handle_time_summary_dict()

        return c_dict

    def get_command(self):
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" {self.infiles[0]} {self.get_output_path()}"
                f" {' '.join(self.args)}")

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ioda2nc

        @param time_info dictionary containing timing information
        """
        # get input files
        if not self.find_input_files(time_info):
            return

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        return self.build()

    def find_input_files(self, time_info):
        """! Get all input files for ioda2nc

        @param time_info dictionary containing timing information
        """
        # get list of files even if only one is found (return_list=True)
        obs_path = self.find_obs(time_info, var_info=None, return_list=True)
        if obs_path is None:
            return None

        self.infiles.extend(obs_path)
        return self.infiles

    def set_command_line_arguments(self, time_info):
        """! Set all arguments for ioda2nc command.
        Note: -obs_var will be set in wrapped MET config file, not command line

        @param time_info dictionary containing timing information
        """
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

        # if more than 1 input file was found, add them with -iodafile
        for infile in self.infiles[1:]:
            self.args.append(f"-iodafile {infile}")

        if self.c_dict['VALID_BEG']:
            valid_beg = do_string_sub(self.c_dict['VALID_BEG'], **time_info)
            self.args.append(f"-valid_beg {valid_beg}")

        if self.c_dict['VALID_END']:
            valid_end = do_string_sub(self.c_dict['VALID_END'], **time_info)
            self.args.append(f"-valid_end {valid_end}")

        if self.c_dict['NMSG']:
            self.args.append(f"-nmsg {self.c_dict['NMSG']}")
