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
        'METPLUS_LEAD_WINDOW_DICT',
        'METPLUS_MIN_DURATION',
        'METPLUS_FCST_GENESIS_DICT',
        'METPLUS_BEST_GENESIS_DICT',
        'METPLUS_OPER_GENESIS_DICT',
        'METPLUS_FILTER',
        'METPLUS_DESC',
        'METPLUS_MODEL',
        'METPLUS_STORM_ID',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_INIT_HOUR',
        'METPLUS_LEAD_LIST',
        'METPLUS_VX_MASK',
        'METPLUS_GENESIS_WINDOW_DICT',
        'METPLUS_GENESIS_RADIUS',
        'METPLUS_DLAND_FILE',
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
        self.set_met_config_int(self.env_var_dict,
                                f'{app_name_upper}_INIT_FREQUENCY',
                                'init_freq',
                                'METPLUS_INIT_FREQ')

        self.set_met_config_int(c_dict,
                                f'{app_name_upper}_LEAD_WINDOW_BEGIN',
                                'beg',
                                'LEAD_WINDOW_BEG')
        self.set_met_config_int(c_dict,
                                f'{app_name_upper}_LEAD_WINDOW_END',
                                'end',
                                'LEAD_WINDOW_END')

        self.set_met_config_int(self.env_var_dict,
                                f'{app_name_upper}_MIN_DURATION',
                                'min_duration',
                                'METPLUS_MIN_DURATION')

        conf_value = (
            self.config.getstr('config',
                               f'{app_name_upper}_FCST_GENESIS_VMAX_THRESH',
                               '')
        )
        if conf_value and conf_value != 'NA':
            if util.get_threshold_via_regex(conf_value) is None:
                self.log_error("Incorrectly formatted threshold: "
                               f"{app_name_upper}_FCST_GENESIS_VMAX_THRESH")

        # set values for dictionaries
        for dict_name in ['FCST_GENESIS', 'BEST_GENESIS', 'OPER_GENESIS']:
            # set threshold values
            for thresh_name in ['VMAX_THRESH', 'MSLP_THRESH']:
                self.set_met_config_thresh(
                    c_dict,
                    f'{app_name_upper}_{dict_name}_{thresh_name}',
                    thresh_name.lower(),
                    f'{dict_name}_{thresh_name}',
                )

            if dict_name == 'FCST_GENESIS':
                continue

            # get technique and category
            self.set_met_config_string(c_dict,
                                   f'{app_name_upper}_{dict_name}_TECHNIQUE',
                                   'technique',
                                   f'{dict_name}_TECHNIQUE')

            self.set_met_config_list(c_dict,
                                 f'{app_name_upper}_{dict_name}_CATEGORY',
                                 'category',
                                 f'{dict_name}_CATEGORY')

        # get filter values
        filters = self.get_filter_values()
        if filters:
            filter_string = 'filter = [{'
            filter_string += '}, {'.join(filters)
            filter_string += '}];'
            self.env_var_dict['METPLUS_FILTER'] = filter_string

        self.set_met_config_list(self.env_var_dict, 'MODEL', 'model',
                                 'METPLUS_MODEL')
        self.set_met_config_list(c_dict, 'MODEL', 'model')
        self.set_met_config_list(self.env_var_dict,
                                 f'{app_name_upper}_STORM_ID',
                                 'storm_id',
                                 'METPLUS_STORM_ID')
        self.set_met_config_list(self.env_var_dict,
                                 f'{app_name_upper}_STORM_NAME',
                                 'storm_name',
                                 'METPLUS_STORM_NAME')
        self.set_met_config_list(self.env_var_dict,
                                 f'{app_name_upper}_INIT_HOUR_LIST',
                                 'init_hour',
                                 'METPLUS_INIT_HOUR')

        # set INIT_BEG, INIT_END, VALID_BEG, and VALID_END
        for time_type in ['INIT', 'VALID']:
            for time_bound in ['BEG', "END"]:
                conf_value = self.config.getraw(
                    'config',
                    f'{self.app_name.upper()}_{time_type}_{time_bound}',
                    '',
                )
                time_value = util.remove_quotes(conf_value)

                if time_value:
                    time_key = f'{time_type}_{time_bound}'
                    time_value = f'{time_key.lower()} = "{time_value}";'
                    self.env_var_dict[f'METPLUS_{time_key}'] = time_value

        self.set_met_config_int(c_dict,
                                f'{app_name_upper}_GENESIS_WINDOW_BEGIN',
                                'beg',
                                'GENESIS_WINDOW_BEG')
        self.set_met_config_int(c_dict,
                                f'{app_name_upper}_GENESIS_WINDOW_END',
                                'end',
                                'GENESIS_WINDOW_END')

        self.set_met_config_int(self.env_var_dict,
                                f'{app_name_upper}_GENESIS_RADIUS',
                                'genesis_radius',
                                'METPLUS_GENESIS_RADIUS')

        self.set_met_config_string(self.env_var_dict,
                                   f'{app_name_upper}_VX_MASK',
                                   'vx_mask',
                                   'METPLUS_VX_MASK')

        self.set_met_config_string(self.env_var_dict,
                                   f'{app_name_upper}_DLAND_FILE',
                                   'dland_file',
                                   'METPLUS_DLAND_FILE')

        # set environment variables for dictionary items
        for dict_name, item_list in {'lead_window': ['BEG',
                                                     'END',
                                                    ],
                                    'fcst_genesis': ['VMAX_THRESH',
                                                     'MSLP_THRESH',
                                                    ],
                                     'best_genesis': ['TECHNIQUE',
                                                      'CATEGORY',
                                                      'VMAX_THRESH',
                                                      'MSLP_THRESH',
                                                     ],
                                     'oper_genesis': ['TECHNIQUE',
                                                      'CATEGORY',
                                                      'VMAX_THRESH',
                                                      'MSLP_THRESH',
                                                     ],
                                     'genesis_window': ['BEG',
                                                        'END',
                                                       ],
                                     }.items():
            dict_str = self.format_met_config_dict(c_dict,
                                                   dict_name,
                                                   item_list)
            self.env_var_dict[f'METPLUS_{dict_name.upper()}_DICT'] = dict_str

        # get INPUT_TIME_DICT values since wrapper only runs
        # once (doesn't look over time)
        self.set_time_dict_for_single_runtime(c_dict)

        # read desc from TC_GEN_DESC or DESC into c_dict['DESC']
        self.handle_description()

        return c_dict

    def get_filter_values(self):
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

        return filters

    def get_command(self):
        cmd = self.app_path

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

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
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

            self.env_var_dict['METPLUS_LEAD_LIST'] = (
                f"lead = [{', '.join(lead_list)}];"
            )

        return True

    def set_command_line_arguments(self, time_info):

        # add config file - passing through do_string_sub to get
        # custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f"-config {config_file}")
