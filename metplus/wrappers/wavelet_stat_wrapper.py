'''
Program Name: wavelet_stat_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

import os

from . import CompareGriddedWrapper

# pylint:disable=pointless-string-statement
"""!@namespace WaveletStatWrapper
@brief Wraps the MET tool wavelet_stat to compare gridded datasets
@endcode
"""


class WaveletStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool wavelet_stat to compare gridded datasets"""

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_FIELD',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_MASK_MISSING_FLAG',
        'METPLUS_GRID_DECOMP_FLAG',
        'METPLUS_TITLE_DICT',
        'METPLUS_WAVELET_DICT',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_NC_PAIRS_FLAG_DICT',
        'METPLUS_PS_PLOT_FLAG',
        'METPLUS_FCST_RAW_PLOT_DICT',
        'METPLUS_OBS_RAW_PLOT_DICT',
        'METPLUS_WVLT_PLOT_DICT',
        'METPLUS_OUTPUT_PREFIX',
    ]

    OUTPUT_FLAGS = [
        'isc',
    ]

    NC_PAIRS_FLAGS = [
        'raw',
        'diff',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'wavelet_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        app = self.app_name.upper()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('WaveletStatConfig_wrapped')

        c_dict['OBS_INPUT_DIR'] = self.config.getdir(f'OBS_{app}_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = (
            self.config.getraw('config', f'OBS_{app}_INPUT_TEMPLATE')
        )
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error(f"OBS_{app}_INPUT_TEMPLATE required to run")

        c_dict['OBS_INPUT_DATATYPE'] = (
            self.config.getstr('config', f'OBS_{app}_INPUT_DATATYPE', '')
        )

        c_dict['FCST_INPUT_DIR'] = self.config.getdir(f'FCST_{app}_INPUT_DIR', '')
        c_dict['FCST_INPUT_TEMPLATE'] = (
            self.config.getraw('config', f'FCST_{app}_INPUT_TEMPLATE')
        )
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error(f"FCST_{app}_INPUT_TEMPLATE required to run")

        c_dict['FCST_INPUT_DATATYPE'] = (
            self.config.getstr('config', f'FCST_{app}_INPUT_DATATYPE', '')
        )

        c_dict['OUTPUT_DIR'] = self.config.getdir(f'{app}_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error(f"Must set {app}_OUTPUT_DIR")

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', f'{app}_OUTPUT_TEMPLATE')
        )
        c_dict['ONCE_PER_FIELD'] = (
            self.config.getbool('config',
                                f'{app}_ONCE_PER_FIELD',
                                False)
        )

        c_dict['FCST_PROB_THRESH'] = (
            self.config.getstr('config',
                               f'FCST_{app}_PROB_THRESH', '==0.1')
        )
        c_dict['OBS_PROB_THRESH'] = (
            self.config.getstr('config',
                               f'OBS_{app}_PROB_THRESH', '==0.1')
        )

        c_dict['ALLOW_MULTIPLE_FILES'] = False

        # MET config variables
        self.add_met_config(name='censor_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_val', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mask_missing_flag', data_type='string',
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='grid_decomp_flag', data_type='string',
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.handle_flags('output')
        self.handle_flags('nc_pairs')

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=['{app}_FCST_FILE_TYPE',
                                             'FCST_{app}_FILE_TYPE',
                                             '{app}_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=['{app}_OBS_FILE_TYPE',
                                             'OBS_{app}_FILE_TYPE',
                                             '{app}_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config_dict('title', {
            'width': 'int',
            'location': ('dictlist', '', {'x_ll': 'int', 'y_ll': 'int'})
        })

        self.add_met_config_dict('wavelet', {
            'type': ('string', 'remove_quotes,uppercase'),
            'member': 'int'
        })

        self.add_met_config(name='ps_plot_flag', data_type='bool')

        for config_name in ('fcst_raw_plot', 'obs_raw_plot', 'wvlt_plot'):
            self.add_met_config_dict(config_name, {
                'color_table': 'string',
                'plot_min': 'float',
                'plot_max': 'float',
            })

        self.add_met_config(name='output_prefix', data_type='string')

        return c_dict
