"""tc_gen
Program Name: tc_gen_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs tc_gen
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os
import datetime
import re

from ..util import time_util
from ..util import do_string_sub, skip_time, get_lead_sequence
from ..util import time_generator
from . import RuntimeFreqWrapper

'''!@namespace TCGenWrapper
@brief Wraps the TC-Gen tool
@endcode
'''


class TCGenWrapper(RuntimeFreqWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_INIT_FREQ',
        'METPLUS_VALID_FREQ',
        'METPLUS_FCST_HR_WINDOW_DICT',
        'METPLUS_MIN_DURATION',
        'METPLUS_FCST_GENESIS_DICT',
        'METPLUS_BEST_GENESIS_DICT',
        'METPLUS_OPER_TECHNIQUE',
        'METPLUS_FILTER',
        'METPLUS_DESC',
        'METPLUS_MODEL',
        'METPLUS_STORM_ID',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_INIT_INC',
        'METPLUS_INIT_EXC',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_INIT_HOUR',
        'METPLUS_LEAD',
        'METPLUS_VX_MASK',
        'METPLUS_BASIN_MASK',
        'METPLUS_DLAND_THRESH',
        'METPLUS_GENESIS_MATCH_RADIUS',
        'METPLUS_DEV_HIT_RADIUS',
        'METPLUS_DEV_HIT_WINDOW_DICT',
        'METPLUS_OPS_HIT_WINDOW_DICT',
        'METPLUS_DISCARD_INIT_POST_GENESIS_FLAG',
        'METPLUS_DEV_METHOD_FLAG',
        'METPLUS_OPS_METHOD_FLAG',
        'METPLUS_CI_ALPHA',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_NC_PAIRS_FLAG_DICT',
        'METPLUS_VALID_MINUS_GENESIS_DIFF_THRESH',
        'METPLUS_BEST_UNIQUE_FLAG',
        'METPLUS_DLAND_FILE',
        'METPLUS_BASIN_FILE',
        'METPLUS_NC_PAIRS_GRID',
        'METPLUS_GENESIS_MATCH_POINT_TO_TRACK',
        'METPLUS_GENESIS_MATCH_WINDOW_DICT',
    ]

    OUTPUT_FLAGS = [
        'fho',
        'ctc',
        'cts',
        'pct',
        'pstd',
        'pjc',
        'prc',
        'genmpr',
    ]

    NC_PAIRS_FLAGS = [
        'latlon',
        'fcst_genesis',
        'fcst_tracks',
        'fcst_fy_oy',
        'fcst_fy_on',
        'best_genesis',
        'best_tracks',
        'best_fy_oy',
        'best_fn_oy',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "tc_gen"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app_name_upper = self.app_name.upper()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               f'LOG_{app_name_upper}_VERBOSITY',
                               c_dict['VERBOSITY'])
        )
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('TCGenConfig_wrapped')

        c_dict['GENESIS_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_GENESIS_INPUT_DIR', '')
        )
        c_dict['GENESIS_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_GENESIS_INPUT_TEMPLATE')
        )

        c_dict['EDECK_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_EDECK_INPUT_DIR', '')
        )
        c_dict['EDECK_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_EDECK_INPUT_TEMPLATE')
        )

        c_dict['SHAPE_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_SHAPE_INPUT_DIR', '')
        )
        c_dict['SHAPE_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_SHAPE_INPUT_TEMPLATE')
        )

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_OUTPUT_DIR', '')
        )
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_OUTPUT_TEMPLATE')
        )

        c_dict['TRACK_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_TRACK_INPUT_DIR', '')
        )
        c_dict['TRACK_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_TRACK_INPUT_TEMPLATE')
        )
        if not c_dict['TRACK_INPUT_TEMPLATE']:
            self.log_error(f'{app_name_upper}_TRACK_INPUT_TEMPLATE must be '
                           'set to run TCGen')

        # values used in configuration file
        self.add_met_config(name='init_freq',
                            data_type='int',
                            metplus_configs=['TC_GEN_INIT_FREQUENCY',
                                             'TC_GEN_INIT_FREQ'])
        self.add_met_config(name='valid_freq',
                            data_type='int',
                            metplus_configs=['TC_GEN_VALID_FREQUENCY',
                                             'TC_GEN_VALID_FREQ'])
        self.add_met_config_window('fcst_hr_window')
        self.add_met_config(name='min_duration',
                            data_type='int',
                            metplus_configs=['TC_GEN_MIN_DURATION'])

        self.add_met_config_dict('fcst_genesis', {
            'vmax_thresh': 'thresh',
            'mslp_thresh': 'thresh',
        })
        self.add_met_config_dict('best_genesis', {
            'technique': 'string',
            'category': 'list',
            'vmax_thresh': 'thresh',
            'mslp_thresh': 'thresh',
        })

        self.add_met_config(name='oper_technique',
                            data_type='string',
                            metplus_configs=['TC_GEN_OPER_TECHNIQUE'])
        self.handle_filter()
        self.handle_description()
        self.add_met_config(name='model',
                            data_type='list',
                            metplus_configs=['MODEL'])
        self.add_met_config(name='storm_id',
                            data_type='list',
                            metplus_configs=['TC_GEN_STORM_ID'])
        self.add_met_config(name='storm_name',
                            data_type='list',
                            metplus_configs=['TC_GEN_STORM_NAME'])
        self.add_met_config(name='init_beg',
                            data_type='string',
                            metplus_configs=['TC_GEN_INIT_BEG',
                                             'TC_GEN_INIT_BEGIN'])
        self.add_met_config(name='init_end',
                            data_type='string',
                            metplus_configs=['TC_GEN_INIT_END'])
        self.add_met_config(name='init_inc',
                            data_type='list',
                            metplus_configs=['TC_GEN_INIT_INC',
                                             'TC_GEN_INIT_INCLUDE'])
        self.add_met_config(name='init_exc',
                            data_type='list',
                            metplus_configs=['TC_GEN_INIT_EXC',
                                             'TC_GEN_INIT_EXCLUDE'])
        self.add_met_config(name='valid_beg',
                            data_type='string',
                            metplus_configs=['TC_GEN_VALID_BEG',
                                             'TC_GEN_VALID_BEGIN'])
        self.add_met_config(name='valid_end',
                            data_type='string',
                            metplus_configs=['TC_GEN_VALID_END'])
        self.add_met_config(name='init_hour',
                            data_type='list',
                            metplus_configs=['TC_GEN_INIT_HOUR',
                                             'TC_GEN_INIT_HR',
                                             'TC_GEN_INIT_HOUR_LIST',])
        self.add_met_config(name='vx_mask',
                            data_type='string',
                            metplus_configs=['TC_GEN_VX_MASK'])
        self.add_met_config(name='basin_mask',
                            data_type='list',
                            metplus_configs=['TC_GEN_BASIN_MASK'])
        self.add_met_config(name='dland_thresh',
                            data_type='thresh',
                            metplus_configs=['TC_GEN_DLAND_THRESH'])
        self.add_met_config(name='genesis_match_radius',
                            data_type='int',
                            metplus_configs=['TC_GEN_GENESIS_MATCH_RADIUS'])
        self.add_met_config(name='dev_hit_radius',
                            data_type='int',
                            metplus_configs=['TC_GEN_DEV_HIT_RADIUS'])
        self.add_met_config_window('dev_hit_window')
        self.add_met_config_window('ops_hit_window')
        self.add_met_config(name='discard_init_post_genesis_flag',
                            data_type='bool',
                            metplus_configs=[
                                'TC_GEN_DISCARD_INIT_POST_GENESIS_FLAG'
                            ])
        self.add_met_config(name='dev_method_flag',
                            data_type='bool',
                            metplus_configs=['TC_GEN_DEV_METHOD_FLAG'])
        self.add_met_config(name='ops_method_flag',
                            data_type='bool',
                            metplus_configs=['TC_GEN_OPS_METHOD_FLAG'])
        self.add_met_config(name='ci_alpha',
                            data_type='float',
                            metplus_configs=['TC_GEN_CI_ALPHA'])
        self.handle_flags('output')
        self.handle_flags('nc_pairs')
        self.add_met_config(name='valid_minus_genesis_diff_thresh',
                            data_type='thresh',
                            metplus_configs=[
                                'TC_GEN_VALID_MINUS_GENESIS_DIFF_THRESH'
                            ])
        self.add_met_config(name='best_unique_flag',
                            data_type='bool',
                            metplus_configs=['TC_GEN_BEST_UNIQUE_FLAG'])
        self.add_met_config(name='dland_file',
                            data_type='string',
                            metplus_configs=['TC_GEN_DLAND_FILE'])
        self.add_met_config(name='basin_file',
                            data_type='string',
                            metplus_configs=['TC_GEN_BASIN_FILE'])
        self.add_met_config(name='nc_pairs_grid',
                            data_type='string',
                            metplus_configs=['TC_GEN_NC_PAIRS_GRID'])
        self.add_met_config(
            name='genesis_match_point_to_track',
            data_type='bool',
            metplus_configs=['TC_GEN_GENESIS_MATCH_POINT_TO_TRACK']
        )
        self.add_met_config_window('genesis_match_window')
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def handle_filter(self):
        """! find all TC_GEN_FILTER_<n> values in the config files
        """
        all_config = self.config.keys('config')
        indices = []
        regex = re.compile(r"TC_GEN_FILTER_(\d+)")
        for config in all_config:
            result = regex.match(config)
            if result is not None:
                indices.append(result.group(1))

        filters = [self.config.getraw('config', f'TC_GEN_FILTER_{index}')
                   for index in indices]
        if filters:
            filter_string = 'filter = [{'
            filter_string += '}, {'.join(filters)
            filter_string += '}];'
            self.env_var_dict['METPLUS_FILTER'] = filter_string

    def get_command(self):
        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        # add genesis, edeck, and/or shape if set
        for file_type in ('genesis', 'edeck', 'shape'):
            file_path = self.c_dict.get(f'{file_type.upper()}_FILE')
            if file_path:
                cmd += f' -{file_type} {file_path}'

        # add track
        cmd += ' -track ' + self.c_dict['TRACK_FILE']

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add output path
        out_path = self.get_output_path()
        cmd += ' -out ' + out_path

        return cmd

    def find_input_files(self, time_info):
        """!Get track and genesis files and set c_dict items. Also format
          forecast lead sequence to be read by the MET configuration file and
           set c_dict.

            @param time_info time dictionary to use for string substitution
            @returns True if all inputs were found, False if not.
        """
        # get track file(s) or directory
        track_files = self.find_data(time_info,
                                     data_type='TRACK',
                                     return_list=True,
                                     allow_dir=True)
        if not track_files:
            return False

        list_filename = time_info['init_fmt'] + '_tc_gen_track.txt'
        self.c_dict['TRACK_FILE'] = self.write_list_file(list_filename,
                                                         track_files)

        # get genesis, edeck, and/or shape file(s) or directory
        for file_type in ('genesis', 'edeck', 'shape'):

            # skip if template is not set for input type
            if not self.c_dict.get(f'{file_type.upper()}_INPUT_TEMPLATE'):
                continue

            file_list = self.find_data(time_info,
                                       data_type=file_type.upper(),
                                       return_list=True,
                                       allow_dir=True)

            # if template was provided but no files were found, skip run
            if not file_list:
                return False

            list_filename = f"{time_info['init_fmt']}_tc_gen_{file_type}.txt"
            self.c_dict[f'{file_type.upper()}_FILE'] = (
                self.write_list_file(list_filename, file_list)
            )

        # set METPLUS_LEAD_LIST to list of forecast leads used
        lead_seq = get_lead_sequence(self.config, time_info)
        if lead_seq != [0]:
            lead_list = []
            for lead in lead_seq:
                lead_hours = (
                    time_util.ti_get_seconds_from_relativedelta(
                        lead,
                        valid_time=time_info['valid']
                    )
                ) // 3600
                lead_list.append(f'"{str(lead_hours).zfill(2)}"')

            self.env_var_dict['METPLUS_LEAD'] = (
                f"lead = [{', '.join(lead_list)}];"
            )

        return True

    def set_command_line_arguments(self, time_info):

        # add config file - passing through do_string_sub to get
        # custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f"-config {config_file}")
