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
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'plot_point_obs'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        app = self.app_name.upper()

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

        # get optional title command line argument
        c_dict['TITLE'] = self.config.getraw('config', f'{app}_TITLE')

        # read config file settings

        # handle grid_data dictionary
        items = {
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
        }
        self.add_met_config_dict('grid_data', items)

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

        c_dict['ALLOW_MULTIPLE_FILES'] = True
        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)

            @param input_dict dictionary with time information of current run
        """
        # fill in time info dictionary
        time_info = ti_calculate(input_dict)

        # check if looping by valid or init and log time for run
        loop_by = time_info['loop_by']
        current_time = time_info[loop_by + '_fmt']
        self.logger.info('Running PlotPointObsWrapper at '
                         f'{loop_by} time {current_time}')

        # read input directory and template from config dictionary
        input_dir = self.c_dict['INPUT_DIR']
        input_template = self.c_dict['INPUT_TEMPLATE']
        self.logger.info(f'Input directory is {input_dir}')
        self.logger.info(f'Input template is {input_template}')

        # get forecast leads to loop over
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            time_info['lead'] = lead

            # recalculate time info items
            time_info = ti_calculate(time_info)

            if skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(
                        f"Processing custom string: {custom_string}"
                    )

                time_info['custom'] = custom_string

                # log init/valid/forecast lead times for current loop iteration
                self.logger.info(
                    'Processing forecast lead '
                    f'{time_info["lead_string"]} initialized at '
                    f'{time_info["init"].strftime("%Y-%m-%d %HZ")} '
                    'and valid at '
                    f'{time_info["valid"].strftime("%Y-%m-%d %HZ")}'
                )

                # perform string substitution to find filename based on
                # template and current run time
                filename = do_string_sub(input_template,
                                         **time_info)
                self.logger.info('Looking in input directory '
                                 f'for file: {filename}')

        return True
