"""
Program Name: plot_point_obs_wrapper.py
Contact(s): George McCabe
Abstract: Wrapper for plot_point_obs MET tool
History Log:  Initial version
Usage: Not meant to be run
Parameters: None
Input Files: None
Output Files: None
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from ..util import skip_time
from . import RuntimeFreqWrapper


class PlotPointObsWrapper(RuntimeFreqWrapper):
    """! Wrapper used to build commands to call plot_point_obs """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_GRID_DATA_DICT',
        'METPLUS_MSG_TYP',
        'METPLUS_SID_INC',
        'METPLUS_SID_EXC',
        'METPLUS_OBS_VAR',
        'METPLUS_OBS_GC',
        'METPLUS_OBS_QUALITY',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_LAT_THRESH',
        'METPLUS_LON_THRESH',
        'METPLUS_ELV_THRESH',
        'METPLUS_HGT_THRESH',
        'METPLUS_PRS_THRESH',
        'METPLUS_OBS_THRESH',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_DOTSIZE',
        'METPLUS_LINE_COLOR',
        'METPLUS_LINE_WIDTH',
        'METPLUS_FILL_COLOR',
        'METPLUS_FILL_PLOT_INFO_DICT',
        'METPLUS_POINT_DATA',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'plot_point_obs'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        app = self.app_name.upper()

        # set default runtime frequency if unset explicitly
        if not c_dict['RUNTIME_FREQ']:
            c_dict['RUNTIME_FREQ'] = 'RUN_ONCE_FOR_EACH'

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # get point obs input files
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      f'{app}_INPUT_TEMPLATE')
        c_dict['INPUT_DIR'] = self.config.getdir(f'{app}_INPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.logger.warning(f'{app}_INPUT_TEMPLATE is required '
                                'to run PlotPointObs wrapper.')

        # get optional grid input files
        c_dict['GRID_INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            f'{app}_GRID_INPUT_TEMPLATE'
        )
        c_dict['GRID_INPUT_DIR'] = self.config.getdir(f'{app}_GRID_INPUT_DIR',
                                                      '')

        # get output path
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw(
            'config',
            f'{app}_OUTPUT_TEMPLATE'
        )
        c_dict['OUTPUT_DIR'] = self.config.getdir(f'{app}_OUTPUT_DIR', '')

        # get optional title command line argument
        c_dict['TITLE'] = self.config.getraw('config', f'{app}_TITLE')

        # read config file settings

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = (
            self.get_config_file('PlotPointObsConfig_wrapped')
        )

        # handle grid_data dictionary
        self.add_met_config_dict('grid_data', {
            'field': ('list', 'remove_quotes'),
            'regrid': ('dict', '', {
                'to_grid': ('string', 'uppercase,to_grid'),
                'method': ('string', 'uppercase,remove_quotes'),
                'width': 'int',
                'vld_thresh': 'float',
                'shape': ('string', 'uppercase,remove_quotes'),
            }),
            'grid_plot_info': ('dict', '', {
                'color_table': 'string',
                'plot_min': 'float',
                'plot_max': 'float',
                'colorbar_flag': 'bool',
            }),
        })

        config_lists = [
            'msg_typ',
            'sid_inc',
            'sid_exc',
            'obs_var',
            'obs_gc',
            'obs_quality',
            'censor_thresh',
            'censor_val',
            'line_color',
            'fill_color',
        ]
        for config_list in config_lists:
            self.add_met_config(name=config_list, data_type='list')

        config_strings = [
            'valid_beg',
            'valid_end',
        ]
        for config_string in config_strings:
            self.add_met_config(name=config_string, data_type='string')

        config_threshs = [
            'lat_thresh',
            'lon_thresh',
            'elv_thresh',
            'hgt_thresh',
            'prs_thresh',
            'obs_thresh',
        ]
        for config_thresh in config_threshs:
            self.add_met_config(name=config_thresh, data_type='string',
                                extra_args={'remove_quotes': True})

        self.add_met_config(name='dotsize(x)', data_type='string',
                            extra_args={'remove_quotes': True},
                            metplus_configs=[f'{app}_DOTSIZE'])
        self.add_met_config(name='line_width', data_type='int')

        self.add_met_config_dict('fill_plot_info', {
            'flag': 'bool',
            'color_table': 'string',
            'plot_min': 'float',
            'plot_max': 'float',
            'colorbar_flag': 'bool',
        })

        self.add_met_config(name='point_data',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        c_dict['ALLOW_MULTIPLE_FILES'] = True
        return c_dict

    def get_command(self):
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" {self.infiles[0]} {self.get_output_path()}"
                f" {' '.join(self.args)}")

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run plot_point_obs.

        @param time_info dictionary containing timing information
        @returns True if command was built/run successfully or
         False if something went wrong
        """
        # get input files
        if not self.find_input_files(time_info):
            return False

        # get output path
        if not self.find_and_check_output_file(time_info):
            return False

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        return self.build()

    def find_input_files(self, time_info):
        """! Get all input files for plot_point_obs. Sets self.infiles list.

        @param time_info dictionary containing timing information
        @returns List of files that were found or None if no files were found
        """
        input_files = self.find_data(time_info,
                                     return_list=True,
                                     mandatory=True)
        if input_files is None:
            return None

        self.infiles.extend(input_files)

        # get optional grid file path
        if self.c_dict['GRID_INPUT_TEMPLATE']:
            grid_file = self.find_data(time_info,
                                       data_type='GRID',
                                       return_list=True)
            if not grid_file:
                return None

            if len(grid_file) > 1:
                self.log_error('More than one file found from '
                               'PLOT_POINT_OBS_GRID_INPUT_TEMPLATE: '
                               f'{grid_file.split(",")}')
                return None

            self.c_dict['GRID_INPUT_PATH'] = grid_file[0]

        return self.infiles

    def set_command_line_arguments(self, time_info):
        """! Set all arguments for plot_point_obs command.

        @param time_info dictionary containing timing information
        """
        # if more than 1 input file was found, add them with -point_obs
        for infile in self.infiles[1:]:
            self.args.append(f'-point_obs {infile}')

        if self.c_dict.get('GRID_INPUT_PATH'):
            grid_file = do_string_sub(self.c_dict['GRID_INPUT_PATH'],
                                      **time_info)
            self.args.append(f'-plot_grid {grid_file}')

        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f'-config {config_file}')

        if self.c_dict.get('TITLE'):
            title = do_string_sub(self.c_dict['TITLE'], **time_info)
            self.args.append(f'-title "{title}"')
