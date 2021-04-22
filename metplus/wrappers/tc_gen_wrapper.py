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

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace TCGenWrapper
@brief Wraps the TC-Gen tool
@endcode
'''

class TCGenWrapper(CommandBuilder):

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

    OUTPUT_FLAGS = ['fho',
                    'ctc',
                    'cts',
                    'genmpr',
                    ]

    NC_PAIRS_FLAGS = ['latlon',
                      'fcst_genesis',
                      'fcst_tracks',
                      'fcst_fy_oy',
                      'fcst_fy_on',
                      'best_genesis',
                      'best_tracks',
                      'best_fy_oy',
                      'best_fn_oy',
                    ]


    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "tc_gen"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app_name_upper = self.app_name.upper()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               f'LOG_{app_name_upper}_VERBOSITY',
                               c_dict['VERBOSITY'])
        )
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = (
            self.config.getraw('config',
                               f'{app_name_upper}_CONFIG_FILE', '')
        )

        c_dict['GENESIS_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_GENESIS_INPUT_DIR', '')
        )
        c_dict['GENESIS_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               f'{app_name_upper}_GENESIS_INPUT_TEMPLATE')
        )
        if not c_dict['GENESIS_INPUT_TEMPLATE']:
            self.log_error(f'{app_name_upper}_GENESIS_INPUT_TEMPLATE must be '
                           'set to run TCGen')

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_OUTPUT_DIR', '')
        )
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               f'{app_name_upper}_OUTPUT_TEMPLATE')
        )

        c_dict['TRACK_INPUT_DIR'] = (
            self.config.getdir(f'{app_name_upper}_TRACK_INPUT_DIR', '')
        )
        c_dict['TRACK_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
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
        self.handle_fcst_hr_window()
        self.add_met_config(name='min_duration',
                            data_type='int',
                            metplus_configs=['TC_GEN_MIN_DURATION'])
        self.handle_fcst_genesis()
        self.handle_best_genesis()
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
        self.handle_dev_hit_window()
        self.handle_ops_hit_window()
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
        self.handle_genesis_match_window()

        # get INPUT_TIME_DICT values since wrapper only runs
        # once (doesn't look over time)
        self.set_time_dict_for_single_runtime(c_dict)

        return c_dict

    def handle_fcst_hr_window(self):
        dict_name = 'fcst_hr_window'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='beg',
                           data_type='int',
                           metplus_configs=['TC_GEN_FCST_HR_WINDOW_BEGIN',
                                            'TC_GEN_FCST_HR_WINDOW_BEG',
                                            'TC_GEN_LEAD_WINDOW_BEGIN',
                                            'TC_GEN_LEAD_WINDOW_BEG'])
        )
        dict_items.append(
            self.get_met_config(name='end',
                       data_type='int',
                       metplus_configs=['TC_GEN_FCST_HR_WINDOW_END',
                                        'TC_GEN_LEAD_WINDOW_END'])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_dev_hit_window(self):
        dict_name = 'dev_hit_window'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='beg',
                       data_type='int',
                       metplus_configs=['TC_GEN_DEV_HIT_WINDOW_BEGIN',
                                        'TC_GEN_DEV_HIT_WINDOW_BEG',
                                        'TC_GEN_GENESIS_WINDOW_BEGIN',
                                        'TC_GEN_GENESIS_WINDOW_BEG'])
        )
        dict_items.append(
            self.get_met_config(name='end',
                       data_type='int',
                       metplus_configs=['TC_GEN_DEV_HIT_WINDOW_END',
                                        'TC_GEN_GENESIS_WINDOW_END'])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_ops_hit_window(self):
        dict_name = 'ops_hit_window'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='beg',
                       data_type='int',
                       metplus_configs=['TC_GEN_OPS_HIT_WINDOW_BEGIN',
                                        'TC_GEN_OPS_HIT_WINDOW_BEG',])
        )
        dict_items.append(
            self.get_met_config(name='end',
                       data_type='int',
                       metplus_configs=['TC_GEN_OPS_HIT_WINDOW_END',])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_genesis_match_window(self):
        dict_name = 'genesis_match_window'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='beg',
                       data_type='int',
                       metplus_configs=['TC_GEN_GENESIS_MATCH_WINDOW_BEGIN',
                                        'TC_GEN_GENESIS_MATCH_WINDOW_BEG',])
        )
        dict_items.append(
            self.get_met_config(name='end',
                       data_type='int',
                       metplus_configs=['TC_GEN_GENESIS_MATCH_WINDOW_END',])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_fcst_genesis(self):
        dict_name = 'fcst_genesis'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='vmax_thresh',
                       data_type='thresh',
                       metplus_configs=['TC_GEN_FCST_GENESIS_VMAX_THRESH'])
        )
        dict_items.append(
            self.get_met_config(name='mslp_thresh',
                       data_type='thresh',
                       metplus_configs=['TC_GEN_FCST_GENESIS_MSLP_THRESH'])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_best_genesis(self):
        dict_name = 'best_genesis'
        dict_items = []
        dict_items.append(
            self.get_met_config(name='technique',
                       data_type='string',
                       metplus_configs=['TC_GEN_BEST_GENESIS_TECHNIQUE'])
        )
        dict_items.append(
            self.get_met_config(name='category',
                       data_type='list',
                       metplus_configs=['TC_GEN_BEST_GENESIS_CATEGORY'])
        )
        dict_items.append(
            self.get_met_config(name='vmax_thresh',
                       data_type='thresh',
                       metplus_configs=['TC_GEN_BEST_GENESIS_VMAX_THRESH'])
        )
        dict_items.append(
            self.get_met_config(name='mslp_thresh',
                       data_type='thresh',
                       metplus_configs=['TC_GEN_BEST_GENESIS_MSLP_THRESH'])
        )
        self.handle_met_config_dict(dict_name, dict_items)

    def handle_filter(self):
        """! find all TC_GEN_FILTER_<n> values in the config files
        """
        filters = []

        all_config = self.config.keys('config')
        indices = []
        regex = re.compile(r"TC_GEN_FILTER_(\d+)")
        for config in all_config:
            result = regex.match(config)
            if result is not None:
                indices.append(result.group(1))

        for index in indices:
            filter = self.config.getraw('config', f'TC_GEN_FILTER_{index}')
            filters.append(filter)

        if filters:
            filter_string = 'filter = [{'
            filter_string += '}, {'.join(filters)
            filter_string += '}];'
            self.env_var_dict['METPLUS_FILTER'] = filter_string

    def get_command(self):
        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        # add genesis
        cmd += ' -genesis ' + self.c_dict['GENESIS_FILE']

        # add track
        cmd += ' -track ' + self.c_dict['TRACK_FILE']

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add output path
        out_path = self.get_output_path()
        cmd += ' -out ' + out_path

        parent_dir = os.path.dirname(out_path)
        if not parent_dir:
            self.log_error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        return cmd

    def run_all_times(self):
        """! Runs the MET application for a given run time. This function
              loops over the list of forecast leads and runs the
               application for each.

             @param input_dict dictionary containing timing information
        """
        # run using input time dictionary
        self.run_at_time(self.c_dict['INPUT_TIME_DICT'])
        return self.all_commands

    def run_at_time(self, input_dict):
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param input_dict dictionary containing timing information
        """
        input_dict['instance'] = self.instance if self.instance else ''
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            time_info = time_util.ti_calculate(input_dict)

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
             Args:
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
        self.build()

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

        # get genesis file(s) or directory
        genesis_files = self.find_data(time_info,
                                       data_type='GENESIS',
                                       return_list=True,
                                       allow_dir=True)

        if not genesis_files:
            return False

        list_filename = time_info['init_fmt'] + '_tc_gen_genesis.txt'
        self.c_dict['GENESIS_FILE'] = self.write_list_file(list_filename,
                                                           genesis_files)

        # set METPLUS_LEAD_LIST to list of forecast leads used
        lead_seq = util.get_lead_sequence(self.config, time_info)
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
